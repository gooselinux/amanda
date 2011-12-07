%define	_libexecdir %{_libdir}
%{!?defconfig:%define defconfig DailySet1}
%{!?indexserver:%define indexserver amandahost}
%{!?tapeserver:%define tapeserver %{indexserver}}
%{!?amanda_user:%define amanda_user amandabackup}
%{!?amanda_group:%define amanda_group disk}

Summary: A network-capable tape backup solution
Name: amanda
Version: 2.6.1p2
Release: 7%{?dist}
Source: http://downloads.sourceforge.net/amanda/amanda-%{version}.tar.gz
#Source: http://www.zmanda.com/downloads/community/community-builds/amanda-%{version}.tar.gz
Source1: amanda.crontab
Source4: disklist
Source5: amanda-xinetd
Source8: amandahosts
Source9: README-rpm
Patch1: amanda-2.6.1p2-example.patch
Patch2: amanda-2.6.1p2-xattrs.patch
Patch3: amanda-2.6.0p2-tcpport.patch
Patch4: amanda-2.6.0b3-lib.patch
Patch5: amanda-2.6.1p2-pie.patch
Patch6: amanda-2.6.1p2-ftbfs.patch
Patch7: amanda-2.6.1p2-optionk.patch
Patch8: amanda-2.6.1p2-amold.patch
License: BSD and LGPLv2 and GPLv3+ and GPLv2
Group: Applications/System
URL: http://www.amanda.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: automake autoconf libtool
BuildRequires: dump gnuplot cups samba-client tar grep fileutils
BuildRequires: gcc-c++ readline-devel
BuildRequires: krb5-devel rsh openssh-clients ncompress mtx mt-st
BuildRequires: perl-devel perl(ExtUtils::Embed)
BuildRequires: glib2-devel openssl-devel swig bison flex
BuildRequires: libcurl-devel
Requires(pre): shadow-utils
Requires(post): grep sed
Requires: fileutils grep initscripts tar /bin/mail xinetd
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description 
AMANDA, the Advanced Maryland Automatic Network Disk Archiver, is a
backup system that allows the administrator of a LAN to set up a
single master backup server to back up multiple hosts to one or more
tape drives or disk files.  AMANDA uses native dump and/or GNU tar
facilities and can back up a large number of workstations running
multiple versions of Unix.  Newer versions of AMANDA (including this
version) can use SAMBA to back up Microsoft(TM) Windows95/NT hosts.
The amanda package contains the core AMANDA programs and will need to
be installed on both AMANDA clients and AMANDA servers.  Note that you
will have to install the amanda-client and/or amanda-server packages as
well.

%package client
Summary: The client component of the AMANDA tape backup system
Group: Applications/System
Requires: fileutils grep /sbin/service
Requires(pre): amanda = %{version}-%{release}
Requires(post): grep sed

%description client
The Amanda-client package should be installed on any machine that will
be backed up by AMANDA (including the server if it also needs to be
backed up).  You will also need to install the amanda package on each
AMANDA client machine.

%package server
Summary: The server side of the AMANDA tape backup system
Group: Applications/System
Requires: fileutils grep /sbin/service
Requires(pre): amanda = %{version}-%{release}
Requires(post): grep sed findutils

%description server
The amanda-server package should be installed on the AMANDA server,
the machine attached to the device(s) (such as a tape drive) where backups
will be written. You will also need to install the amanda package on
the AMANDA server machine.  And, if the server is also to be backed up, the
server also needs to have the amanda-client package installed.

%package devel
Summary: Libraries and documentation of the AMANDA tape backup system
Group: Development/Libraries
Requires(pre): amanda = %{version}-%{release}

%description devel
The amanda-devel package should be installed on any machine that will
be used to develop amanda applications.

#%%define _default_patch_fuzz 3

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1 -b .example
%patch2 -p1 -b .xattrs
%patch3 -p1 -b .tcpport
%patch4 -p1 -b .lib
%patch5 -p1 -b .pie
%patch6 -p1 -b .ftbfs
%patch7 -p1 -b .optionk
%patch8 -p1 -b .amold
./autogen

%build
export MAILER=/bin/mail

%configure --enable-shared \
	--disable-rpath \
	--disable-static \
	--disable-dependency-tracking \
	--disable-installperms \
	--with-amlibdir=%{_libdir} \
	--with-amperldir=%{perl_vendorarch} \
	--with-index-server=%{indexserver} \
	--with-tape-server=%{tapeserver} \
	--with-config=%{defconfig} \
	--with-gnutar-listdir=%{_localstatedir}/lib/amanda/gnutar-lists \
	--with-smbclient=%{_bindir}/smbclient \
	--with-amandates=%{_localstatedir}/lib/amanda/amandates \
	--with-amandahosts \
	--with-user=%amanda_user \
	--with-group=%amanda_group \
	--with-tmpdir=/var/log/amanda \
	--with-gnutar=/bin/tar \
	--with-ssh-security \
	--with-rsh-security \
	--with-bsdtcp-security \
	--with-bsdudp-security \
	--with-krb5-security
	
make %{?_smp_mflags}


%install
rm -rf ${RPM_BUILD_ROOT}
#export SED=sed

make install BINARY_OWNER=%(id -un) SETUID_GROUP=%(id -gn) DESTDIR=$RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/etc/xinetd.d
perl -p -e "s,\@LIBEXECDIR\@,%{_libexecdir},g" < %SOURCE5 > $RPM_BUILD_ROOT/etc/xinetd.d/amanda
chmod 644 $RPM_BUILD_ROOT/etc/xinetd.d/amanda
mkdir -p $RPM_BUILD_ROOT/var/log/amanda
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/amanda
install -m 600 %SOURCE8 $RPM_BUILD_ROOT%{_localstatedir}/lib/amanda/.amandahosts

ln -s %{_libexecdir}/amanda/amandad $RPM_BUILD_ROOT%{_sbindir}/amandad

cp %SOURCE9 .

#pushd tape-src/.libs
#install -m 755 amtapetype $RPM_BUILD_ROOT/%{_sbindir}
#popd

ln -s amrecover.8.gz $RPM_BUILD_ROOT%{_mandir}/man8/amoldrecover.8

pushd ${RPM_BUILD_ROOT}
  mv .%{_sysconfdir}/amanda/example .%{_sysconfdir}/amanda/%defconfig
  cp ${RPM_SOURCE_DIR}/amanda.crontab .%{_sysconfdir}/amanda/crontab.sample
  cp ${RPM_SOURCE_DIR}/disklist .%{_sysconfdir}/amanda/%defconfig
  cp ${RPM_SOURCE_DIR}/disklist .%{_sysconfdir}/amanda/%defconfig

  mkdir -p .%{_localstatedir}/lib/amanda/gnutar-lists
  mkdir -p .%{_localstatedir}/lib/amanda/%defconfig/index
  touch .%{_localstatedir}/lib/amanda/amandates
popd
rm -rf $RPM_BUILD_ROOT/usr/share/amanda
find $RPM_BUILD_ROOT -name \*.la | xargs rm

%check
make check

%clean 
rm -rf ${RPM_BUILD_ROOT}

%pre
# look for user 'amanda' with uid 33, if exists, rename to new %amanda_user
getent passwd 'amanda' | grep ':33:' >/dev/null &&
usermod -l %amanda_user amanda >/dev/null 2>&1 &&
mv /var/spool/cron/amanda /var/spool/cron/%amanda_user &>/dev/null

/usr/sbin/useradd -M -N -g %amanda_group -o -r -d %{_localstatedir}/lib/amanda -s /bin/bash \
	-c "Amanda user" -u 33 %amanda_user >/dev/null 2>&1 || :
/usr/bin/gpasswd -a %amanda_user tape >/dev/null 2>&1 || :

%post
/sbin/ldconfig
# when upgrading and /etc/xinet.d/amanda contains obsolete user name, update it
[ $1 -eq 2 ] &&
	grep -E '^[[:blank:]]*user[[:blank:]]*=[[:blank:]]*amanda[[:blank:]]*$' /etc/xinetd.d/amanda &>/dev/null &&
	sed -i.rpmsave -r -e 's/^([[:blank:]]*user[[:blank:]]*=[[:blank:]]*)amanda([[:blank:]]*)$/\1%amanda_user\2/' /etc/xinetd.d/amanda || :

[ -f /var/lock/subsys/xinetd ] && /sbin/service xinetd reload > /dev/null 2>&1 || :
# when upgrading and .amandahosts contains obsolete user name, update it
#[ $1 -eq 2 ] &&
#grep -E '^[^[:blank:]]+[[:blank:]]+amanda([[:blank:]].*)?$' /var/lib/amanda/.amandahosts &>/dev/null &&
#	sed -i.usernameupdate -r -e 's/^([^[:blank:]]+[[:blank:]]+)amanda([[:blank:]].*)?$/\1%amanda_user\2/' /var/lib/amanda/.amandahosts || :

%postun
/sbin/ldconfig
[ -f /var/lock/subsys/xinetd ] && /sbin/service xinetd reload > /dev/null 2>&1 || :

%pre client
# when upgrading, move /etc/amandates to /var/lib/amanda/amandates
[ -f /etc/amandates ] &&
	mv /etc/amandates /var/lib/amanda/amandates || :

%post client -p /sbin/ldconfig

%post server
/sbin/ldconfig
# when upgrading, check amanda.conf in all configurations
# if it contains obsolete user name, update it
[ $1 -eq 2 ] &&
grep -l -E '^dumpuser[[:blank:]]*"amanda"' /etc/amanda/*/amanda.conf |
	xargs sed -i.usernameupdate -r -e 's/^(dumpuser[[:blank:]]*)"amanda"/\1"%amanda_user"/' &>/dev/null || :

%postun client -p /sbin/ldconfig

%postun server -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc COPYRIGHT* NEWS README
					%config(noreplace) /etc/xinetd.d/amanda
%attr(-,%amanda_user,%amanda_group)	%{_libdir}/libamanda-*.so
					%{_libdir}/libamdevice-*.so
					%{_libdir}/libamglue.so
#					%{_libdir}/libamtape-*.so
					%{_libdir}/libamserver-*.so
					%{_libdir}/librestore-*.so
					%{_libdir}/libamclient-*.so
					%{_libdir}/libamandad-*.so
					%{_libdir}/libamar-*.so
					%{_libdir}/libamxfer-*.so
%attr(-,%amanda_user,%amanda_group)	%dir %{_libexecdir}/amanda
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amanda-sh-lib.sh
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-glue
%attr(-,%amanda_user,%amanda_group)	%{perl_vendorarch}/auto/Amanda/
%attr(-,%amanda_user,%amanda_group)	%{perl_vendorarch}/Amanda/
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amrestore
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amarchiver
					%{_mandir}/man8/amrestore.8*
					%{_mandir}/man8/amarchiver.8*
					%{_mandir}/man8/script-email.8*
					%{_mandir}/man5/amanda-archive-format.5*
					%{_mandir}/man7/amanda-auth.7*
					%{_mandir}/man7/amanda-scripts.7*					
%attr(600,%amanda_user,%amanda_group)	%config(noreplace) %{_localstatedir}/lib/amanda/.amandahosts

%attr(02700,%amanda_user,%amanda_group) %dir /var/log/amanda
%attr(-,%amanda_user,%amanda_group)	%dir %{_localstatedir}/lib/amanda/
%attr(-,%amanda_user,%amanda_group)	%dir %{_sysconfdir}/amanda/
%attr(-,%amanda_user,%amanda_group)	%dir %{_sysconfdir}/amanda/%defconfig
%doc README-rpm

%{_mandir}/man5/amanda.conf*

%files server
%defattr(-,root,root)
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amidxtaped
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amindexd
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amlogroll
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amtrmidx
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amtrmlog
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/driver
%attr(4750,root,%amanda_group)	%{_libexecdir}/amanda/dumper
%attr(4750,root,%amanda_group)	%{_libexecdir}/amanda/planner
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/taper
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chunker
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amcleanupdisk
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-chio
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-chs
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-juke
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-manual
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-mcutil
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-mtx
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-multi
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-null
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-rait
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-rth
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-scsi
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-zd-mtx
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-disk
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-iomega
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/chg-lib.sh
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amcat.awk
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amplot.awk
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amplot.g
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amplot.gp

%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amaespipe
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amaddclient
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amadmin
%attr(4750,root,%amanda_group)		%{_sbindir}/amcheck
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amcheckdump
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amcrypt
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amcryptsimple
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amcrypt-ossl
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amcrypt-ossl-asym
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amdevcheck
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amflush
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amgetconf
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amgpgcrypt
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amlabel
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amtape
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amreport
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amcheckdb
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amcleanup
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amdump
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amoverview
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amrmtape
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amtoc
#%%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amverify
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amserverconfig
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amstatus
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amplot
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amtapetype
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amservice
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amvault
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/activate-devpay
#%%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amdd
#%%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/ammt
#%%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amverifyrun

%attr(-,%amanda_user,%amanda_group)	%dir %{_localstatedir}/lib/amanda/%defconfig/
%attr(-,%amanda_user,%amanda_group)	%dir %{_localstatedir}/lib/amanda/%defconfig/index
%attr(-,%amanda_user,%amanda_group)	%dir %{_sysconfdir}/amanda
%attr(-,%amanda_user,%amanda_group)	%config(noreplace) %{_sysconfdir}/amanda/crontab.sample
%attr(-,%amanda_user,%amanda_group)	%config(noreplace) %{_sysconfdir}/amanda/%defconfig/*
%exclude %{_sysconfdir}/amanda/%defconfig/amanda-client.conf
%attr(-,%amanda_user,%amanda_group)	%dir %{_localstatedir}/lib/amanda/template.d
%attr(-,%amanda_user,%amanda_group)	%config(noreplace) %{_localstatedir}/lib/amanda/template.d/*

%{_mandir}/man8/amadmin.8*
%{_mandir}/man8/amaespipe.8*
%{_mandir}/man8/amaddclient.8*
%{_mandir}/man8/amanda.8*
%{_mandir}/man8/amcheck.8*
%{_mandir}/man8/amcheckdb.8*
%{_mandir}/man8/amcheckdump.8*
%{_mandir}/man8/amcleanup.8*
%{_mandir}/man8/amcrypt.8*
%{_mandir}/man8/amcryptsimple.8*
#%%{_mandir}/man8/amdd.8*
%{_mandir}/man8/amdevcheck.8*
%{_mandir}/man8/amdump.8*
%{_mandir}/man8/amflush.8*
%{_mandir}/man8/amgetconf.8*
%{_mandir}/man8/amgpgcrypt.8*
%{_mandir}/man8/amlabel.8*
%{_mandir}/man8/amservice.8*
%{_mandir}/man8/amvault.8*
#%%{_mandir}/man8/ammt.8*
%{_mandir}/man8/amoverview.8*
%{_mandir}/man8/amplot.8*
%{_mandir}/man8/amreport.8*
%{_mandir}/man8/amrmtape.8*
%{_mandir}/man8/amserverconfig.8*
%{_mandir}/man8/amstatus.8*
%{_mandir}/man8/amtape.8*
%{_mandir}/man8/amtapetype.8*
%{_mandir}/man8/amtoc.8*
#%%{_mandir}/man8/amverify.8*
#%%{_mandir}/man8/amverifyrun.8*
%{_mandir}/man8/amcrypt-ossl.8*
%{_mandir}/man8/amcrypt-ossl-asym.8*
%{_mandir}/man7/amanda-changers.7*
%{_mandir}/man7/amanda-devices.7*
%{_mandir}/man5/disklist.5*
%{_mandir}/man5/tapelist.5*

%files client
					%defattr(-,root,root)
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/amandad
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/application/
%attr(4750,root,%amanda_group)		%{_libexecdir}/amanda/calcsize
%attr(4750,root,%amanda_group)		%{_libexecdir}/amanda/killpgrp
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/noop
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/patch-system
%attr(4750,root,%amanda_group)		%{_libexecdir}/amanda/rundump
%attr(4750,root,%amanda_group)		%{_libexecdir}/amanda/runtar
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/selfcheck
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/sendbackup
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/sendsize
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/versionsuffix
%attr(-,%amanda_user,%amanda_group)	%{_libexecdir}/amanda/teecount
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amfetchdump
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amandad
					%{_mandir}/man8/amfetchdump.8*
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amrecover
%attr(-,%amanda_user,%amanda_group)	%{_sbindir}/amoldrecover
					%{_mandir}/man8/amrecover.8*
					%{_mandir}/man8/amoldrecover.8*
					%{_mandir}/man8/amgtar.8*
					%{_mandir}/man8/amsamba.8*
					%{_mandir}/man8/amstar.8*
					%{_mandir}/man8/amzfs-sendrecv.8*
					%{_mandir}/man8/amzfs-snapshot.8*
					%{_mandir}/man5/amanda-client.conf.5*
					%{_mandir}/man7/amanda-applications.7*
%attr(-,%amanda_user,%amanda_group)	%config(noreplace) %{_localstatedir}/lib/amanda/amandates
%attr(-,%amanda_user,%amanda_group)	%{_localstatedir}/lib/amanda/gnutar-lists/
%attr(-,%amanda_user,%amanda_group)	%config(noreplace) %{_sysconfdir}/amanda/%defconfig/amanda-client.conf

%files devel
%defattr(-,root,root)
%{_includedir}/amanda/
%{_libdir}/libamanda.so
%{_libdir}/libamdevice.so
#%%{_libdir}/libamtape.so
%{_libdir}/libamclient.so
%{_libdir}/libamserver.so
%{_libdir}/librestore.so
%{_libdir}/libamandad.so
%{_libdir}/libamar.so
%{_libdir}/libamxfer.so

%changelog
* Wed Jun 23 2010 Jan Görig <jgorig@redhat.com> 2.6.1p2-7
- added amoldrecover description to amrecover man page
- Resolves: #593775

* Fri May 28 2010 Jan Görig <jgorig@redhat.com> 2.6.1p2-6
- removed non existing -k option from amfetchdump help
- Resolves: #596050

* Wed May 26 2010 Jan Görig <jgorig@redhat.com> 2.6.1p2-5
- fix xinetd file multilib issue
- Resolves: #593775

* Tue Apr 27 2010 Jan Görig <jgorig@redhat.com> 2.6.1p2-4
- move files from libexecdir to libdir to avoid multilib config (#586203)
- fix licence flag

* Thu Apr 22 2010 Jan Görig <jgorig@redhat.com> 2.6.1p2-3
- spec fixes
- update and reinclude pie patch
- documentation moved to main package

* Tue Feb 16 2010 Daniel Novotny <dnovotny@redhat.com> 2.6.1p2-2
- fix #564935 -  FTBFS amanda-2.6.1p2-1.fc13

* Thu Jan 21 2010 Daniel Novotny <dnovotny@redhat.com> 2.6.1p2-1
- upgrade to 2.6.1p2, drop upstreamed patches, rebase remaining patches

* Fri Dec  4 2009 Stepan Kasal <skasal@redhat.com> - 2.6.0p2-15
- rebuild against perl 5.10.1

* Thu Oct 15 2009 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-14
- add amanda user to group "tape" (#529159)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.6.0p2-13
- rebuilt with new openssl

* Tue Aug 04 2009 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-12
-fix #512534 -  amstatus outputs "Insecure dependency in printf ..." 

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.0p2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-10
- fix #510961 -  FTBFS: amanda-2.6.0p2-9

* Fri Apr 24 2009 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-9
- fix #497488 -  amanda subpackages require only a specific version of amanda,
      not also release

* Tue Apr 14 2009 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-8
- fix #495724 (spec file fix, use "useradd -N" instead of "useradd -n") 

* Wed Apr 08 2009 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-7
- the tcpport patch was lost after rebase, adding again
  (#448071, #462681)

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.0p2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> 2.6.0p2-5
- rebuild with new openssl

* Thu Nov 20 2008 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-4
  .usernameupdate extension changed to .rpmsave (#472349)

* Thu Oct 23 2008 Daniel Novotny <dnovotny@redhat.com> 2.6.0p2-3
- added trailing || : in the %%pre client script

* Fri Oct 10 2008 Orion Poplawski <orion@cora.nwra.com> 2.6.0p2-2
- Drop duplicated libamglue.so from -devel
- Update -pie patch
- Fix Source typo
- Move xinetd to main package - used by both client and server
- Move %%{_libexecdir}/amanda/amanda-sh-lib.sh to main package
- LIBEXECDIR is used in xinetd template
- Make calcsize setuid root

* Wed Oct 01 2008 Daniel Novotny 2.6.0p2-1
- Update to 2.6.0p2
- perl-ExtUtils-Embed added to BuildRequires
- perl patch dropped (upstreamed)
- library name change from libamglue.so.* to libamglue.so

* Thu Mar 27 2008 Orion Poplawski <orion@cora.nwra.com> 2.6.0-0.b3_20080314.1
- Update to 2.6.0b3_20080314
- New -lib patch that patches the autotool source files

* Tue Mar 11 2008 Orion Poplawski <orion@cora.nwra.com> 2.6.0-0.b3_20080310.1
- Update to 2.6.0b3_20080310
- Re-add updated pie patch, re-add autogen
- Update example patch to modify Makefile.am, leave template.d in
 /var/lib/amanda for now

* Wed Feb 20 2008 Orion Poplawski <orion@cora.nwra.com> 2.6.0-0.b2_20080220.1
- Update to 2.6.0b2-20080220
- Drop libdir patch, use --with-libdir instead
- Move perl modules to %%{perl_vendorarch} and add perl Requires

* Wed Feb 20 2008 Orion Poplawski <orion@cora.nwra.com> 2.6.0-0.b2
- Update to 2.6.0b2, drop upstreamed patches
- Update xattrs patch
- Add patches to fix install locations
- Add -fPIE/-pie to CFLAGS/LDFLAGS, drop pie patch
- Drop autotools BR
- Drop /usr/bin/Mail BR and specify mailer as /bin/mail
- Add %%check section
- Move /etc/amanda/amandates to /var/lib/amanda/amandates
- Remove ending . from summaries

* Mon Feb 18 2008 Radek Brich <rbrich@redhat.com> 2.5.2.p1-10
- do not require gnuplot by -server subpackage (bz#433101)

* Thu Nov 22 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-9
- Change default amanda user name to 'amandabackup' (#124510).
  This should not break upgrades as config files are checked for
  old user name and updated.
- Add some explaining comments to .amandahosts (#153749)

* Tue Aug 28 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-8
- rebuild

* Fri Aug 17 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-7
- BuildRequires mtx and mt-st (#251690).

* Fri Aug 10 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-6
- Included upstream patch for chg-multi.sh (#251316).

* Wed Aug 08 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-5
- Added ssh and ncompress to BuildRequires (#250730).
- Removed some obsolete makes from build section.

* Thu Jul 12 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-4
- Enable backing up ACL/SElinux xattrs with tar (#201916).
- Removed obsolete patches and sources.

* Mon Jun 25 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-3
- Update -undefSymbols patch. All undefined symbols reported by
  'ldd -r' should now be fixed (#198178).

* Fri Jun 22 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-2
- Fix undefined symbols in libamserver.so.
- Fix ./autogen so it automatically installs ylwrap (bug 224143).
- Run ./autogen in prep section (otherwise the -pie patch had no effect).
- Update -pie patch.

* Thu Jun 21 2007 Radek Brich <rbrich@redhat.com> 2.5.2.p1-1
- New upstream version.
- Client rpm now installs amanda-client.conf.
- Removed obsolete patches -bug18322 and -rsh.
- Clean up spec file (non-utf8 error and some warnings from rpmlint).

* Mon Feb 19 2007 Jay Fenlason <fenlason@redhat.com> 2.5.1p3-1%{?dist}
- Upgrade to new upstream release, now that 2.5.1 is somewhat stable.
- Note that this requires changing the xinetd configuration and amanda.conf
  because of the new authentication mechanism.
- -server subpackage does not require xinetd.
- -server scriptlets do not need to reload xinetd.

* Mon Sep 25 2006 Jay Fenlason <fenlason@redhat.com> 2.5.0p2-4
- Include my -dump_size patch to close
  bz#206129: Dump output size determined incorrectly
- Clean up the spec file, following some suggestions in
  bz#185659: amanda 2.5.0
- Use a tarball without the problematic contrib/sst directory.
- Include my new_gnutar (based on a patch by Orion Poplawski
  <orion@cora.nwra.com>) to work around changed incremental file format
  in newer (>1.15.1) versions of gnutar.
- include my -wildcards patch to turn on wildcards with new versions of tar.

* Tue Sep 5 2006 Jay Fenlason <fenlason@redhat.com> 2.5.0p2-3
- move libamclient-*.so to the base rpm, so that multilib support works.
  This fixes
  bz#205202 File conflicts

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.5.0p2-2.1
- rebuild

* Thu Jun 8 2006 Jay Fenlason <fenlason@redhat.com> 2.5.0p2-2
- New upstream version
- Make the BuildRequires on /usr/bin/Mail rather than mailx, because we
  don't really care where the Mail command comes from.
- include the amcheck_badtape patch by Paul Bijnens
  <paul.bijnens@xplanation.com> to fix a problem where amcheck doesn't
  realize the wrong tape is in the drive.
- include the error_msg patch from Jean-Louis Martineau <martineau@zmanda.com>
  to fix a double-free problem
- include the restore patch from Jean-Louis Martineau <martineau@zmanda.com>
  to fix an error in amrestore
- include a slightly modified form of the big_holding_disk patch from
  Andrej Filipcic <andrej.filipcic@ijs.si> to fix a problem with holding
  disks bigger than 4tb

* Mon May 22 2006 Jesse Keating <jkeating@redhat.com> 2.5.0-3
- Fix BuildReqs

* Fri Apr 7 2006 Jay Fenlason <fenlason@redhat.com> 2.5.0-2
- New upstream release: 2.5.0, with new features
- Do not include our own amanda.conf anymore, use the one from the
  tarball.
- Remove the static libraries.
- Update the -pie patch
- Turn on the new -with-ssh-security option.
- Change the mode of ~amanda/.amandahosts to 600, since 2.5.0 requires
  it.
- actually use the defconfig macro it this spec file.
- Change the name of the index server to "amandahost" from localhost.
  Users should ensure that "amandahost.their-domain" points to their
  Amanda server.
- Change amandahosts likewise.
- Add dependency on /usr/bin/Mail
- Ensure unversioned .so files are only in the -devel rpm.
- Remove DUMPER_DIR and the files in it, as nothing seems to actually
  use them.
- Include the -overflow patch from Jean-Louis Martineau
  <martineau@zmanda.com>

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.4.5p1-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.4.5p1-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Jan 18 2006 Jay Fenlason <fenlason@redhat.com> 2.4.5p1-3
- Fix spec file to use %%{_localstatedir} instead of hardcoding /var/lib
- Add amanda_user and amanda_group defines, to make changing the username
  easier.
- Add a BuildRequires on /usr/bin/Mail

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 4 2005 Jay Fenlason <fenlason@redhat.com>
- New upstream release.

* Sun Jul 31 2005 Florian La Roche <laroche@redhat.com>
- make sure amanda builds with newest rpm

* Wed Apr 20 2005 Jay Fenlason <fenlason@redhat.com> 2.4.5-2
- New upstream release.  This obsoletes the -bug144052 patch.
- Reorg this spec file slightly to allow someone to specify
  index server, tape server and default configuration when
  rebuilding the rpms via something like
  'rpmbuild -ba --define "indexserver foo.fqdn.com" amanda.spec'
  This change suggested by Matt Hyclak <hyclak@math.ohiou.edu>.
  
* Tue Apr 5 2005 Jay Fenlason <fenlason@redhat.com> 2.4.4p4-4
- Add -bug144052 patch to close
  bz#144052 amverifyrun sometimes verifies the wrong tapes

* Tue Mar 8 2005 Jay Fenlason <fenlason@redhat.com> 2.4.4p4-3
- rebuild with gcc4

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> 2.4.4p4-2
- Rebuilt for new readline.

* Mon Oct 25 2004 Jay Fenlason <fenlason@redhat.com> 2.4.4p4-1
- New upstream version
- Turn on --disable-dependency-tracking to work around an automake bug.

* Fri Jun 28 2004 Jay Fenlason <fenlason@redhat.com> 2.4.4p3-1
- New upstream version

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Mar 19 2004 Jay Fenlason <fenlason@redhat.com> 2.4.4p2-3
- make a few more programs PIE by updating the amanda-2.4.4p2-pie.path

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jan 13 2004 Jay Fenlason <fenlason@redhat.com> 2.4.4p2-1
- New upstream version, includes the -sigchld and -client-utils
  patches.  Also includes a new chg-disk changer script and a new
  amqde "quick-and-dirty estimate" program (called from sendsize--not
  a user command.

* Wed Jul 23 2003 Jay Fenlason <fenlason@redhat.com> 2.4.4p1-1
- Merge from 2.4.4p1-0.3E

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 26 2003 Jay Fenlason <fenlason@redhat.com> 2.4.4-0
- New upstream version.

* Thu Feb 13 2003 Jay Fenlason <fenlason@redhat.com> 2.4.3-3
- Removed call to signal(SIGCHLD, SIG_IGN) which prevents wait...()
  from working on newer Red Hat systems.  This fixes bug #84092.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Dec 11 2002 Jay Fenlason <fenlason@redhat.com> 2.4.3-2
- Add spec file entry for /usr/lib/amanda so owner/group set
  correctly  Fixes bugs 74025 and 73379.

* Wed Nov 20 2002 Elliot Lee <sopwith@redhat.com> 2.4.3-1
- Update to version 2.4.3, rebuild
- Update patch for bug18322 to match

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Apr  2 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.4.2p2-7
- Don't strip explicitly
- Require samba-client instead of /usr/bin/smbclient

* Thu Feb 21 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.4.2p2-6
- Rebuild

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Jul 13 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Build and install the "tapetype"  utility program, for
  tape size identification (#48745)  

* Tue Jun 19 2001 Trond Eivind Glomsrød <teg@redhat.com>
- don't use %%configure, to make it build

* Mon Apr  9 2001 Bill Nottingham <notting@redhat.com>
- include ia64 again

* Wed Apr  4 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.4.2p2 - fixes problems with amrecover (#26567)
- made config files noreplace
- don't build on IA64 right now, amanda doesn't like
  the dump there: It segfaults.

* Fri Mar 16 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add /usr/bin/smbclient to buildprereq (#31996), to
  avoid samba being built without such support

* Thu Feb 22 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Use %%{version} in source URL, and thus actually use 
  2.4.2p1 instead of 2.4.2 (doh! # 28759)
- add patch to handle bogus /dev/root entries (#28759)

* Fri Feb 16 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.4.2p1 bugfix release
- move amandaixd and amidxtape to the server package (#28037)

* Wed Jan 31 2001 Trond Eivind Glomsrød <teg@redhat.com>
- move /etc/xinetd.d/amanda to the client subpackage (#25430)

* Tue Jan 30 2001 Trond Eivind Glomsrød <teg@redhat.com>
- don't have "chunksize -1" as the default, as it's no longer
  supported
- make it uid amanda, with home /var/lib/amada
  so programs can actually access it (#20510)
- make .amandahosts a config file (#18322)

* Tue Jan 23 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.4.2
- make the UDP service "wait" (#23047)

* Tue Oct 10 2000 Jeff Johnson <jbj@redhat.com>
- build with shared libraries.
- add amanda-devel package to contain static libraries.
- update to 2.4.2-19991216-beta1 (#16818).
- sort out client-server file confusions (#17232).
- amandaidx-xinetd should have "wait = no" (#17551).
- /var/lib/amanda needs operator.disk ownership (17913).
- /etc/xinetd.d/amanda added to the amanda-server package (#18112).
- ignore socket error message (#18322).

* Sun Sep  3 2000 Florian La Roche <Florian.LaRoche@redhat.de>
- do not include /etc/xinetd.d/amandaidx in the server rpm

* Mon Aug 21 2000 Trond Eivind Glomsrød <teg@redhat.com>
- only do reload of xinetd if xinetd is running (#16653)
- don't show output of reload command to STDOUT (#16653)
- don't use /usr/sbin/tcpd in amidx, xinetd is linked
  with tcp_wrappers
- prereq initscripts (fixes #14572 and duplicates)

* Tue Aug  1 2000 Bill Nottingham <notting@redhat.com>
- turn off amandaidx by default (#14937)
- fix some binary permissions (#14938)

* Tue Aug  1 2000 Matt Wilson <msw@redhat.com>
- added Prereq: /sbin/service xinetd to client and server subpackages

* Tue Jul 18 2000 Trond Eivind Glomsrød <teg@redhat.com>
- xinetd support

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Sun Jun 18 2000 Jeff Johnson <jbj@redhat.com>
- add prereqs for scriptlets, requires for common package.

* Sat Jun 10 2000 Jeff Johnson <jbj@redhat.com>
- FHS packaging.
- move to 7.0 distro.

* Tue May 23 2000 Tim Powers <timp@redhat.com>
- built for 7.0
- man pages in /usr/share/man

* Thu Apr 27 2000 Tim Powers <timp@redhat.com>
- added usr/lib/amanda/chg-zd-mtx to the client RPM to fix bug #8282

* Wed Mar 8 2000 Tim Powers <timp@redhat.com>
- fixed files/dirs ending up in the wrong packages.
- last time it wasn't built with dump (doh!), this time it is. Now has a
	BuildRequires for dump.

* Thu Feb 10 2000 Tim Powers <timp@redhat.com>
- strip binaries

* Fri Jan 21 2000 TIm Powers <timp@redhat.com>
- added chown lines to post section

* Tue Jan 11 2000 Tim Powers <timp@redhat.com>
- make sure the man pages are gzipped in each subpackage, overriding the build
	system spec_install_post macro.
- using mega spec file changes from Marc Merlin <merlin_bts@valinux.com> since
	the package we were shipping in the past had some major issues (not in
	Marc's words ;)
- using Marc's added README and modified config files.
- adapted patches written by Alexandre Oliva <oliva@dcc.unicamp.br> from Marc
	Merlin's package so that the patch matches the source version (the patches
	are the glibc2.1 and glibc2.2 patches)

* Mon Jan 3 2000 Tim Powers <timp@redhat.com>
- fix so configure doesn't crap out (libtoolize --force)
- gzip man pages, strip binaries
- rebuilt for 6.2

* Thu Aug 5 1999 Tim Powers <timp@redhat.com>
- applied patch so that it reports the available holding disk space correctly

* Thu Jul 8 1999 Tim Powers <timp@redhat.com>
- added %%defattr lines
- rebuilt for 6.1

* Wed May 05 1999 Bill Nottingham <notting@redhat.com>
- update to 2.4.1p1

* Tue Oct 27 1998 Cristian Gafton <gafton@redhat.com>
- version 2.4.1

* Tue May 19 1998 Cristian Gafton <gafton@redhat.com>
- upgraded to full 2.4.0 release

* Thu Feb 19 1998 Otto Hammersmith <otto@redhat.com>
- fixed group for -client and -server packages (Network->Networking)

* Wed Feb 11 1998 Otto Hammersmith <otto@redhat.com>
- updated to 2.4.0b6, fixes security hole among other things
  (as well as finally got the glibc patch in the main source.)
 
* Tue Jan 27 1998 Otto Hammersmith <otto@redhat.com>
- moved versionsuffix to client package to remove dependency of amanda on amanda-client

* Mon Jan 26 1998 Otto Hammersmith <otto@redhat.com>
- fixed libexec garbage.

* Wed Jan 21 1998 Otto Hammersmith <otto@redhat.com>
- split into three packages amanda, amanda-client, and amanda-server

* Fri Jan  9 1998 Otto Hammersmith <otto@redhat.com>
- updated to latest beta... builds much cleaner now.

* Thu Jan  8 1998 Otto Hammersmith <otto@redhat.com>
- created the package

