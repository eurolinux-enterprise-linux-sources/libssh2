Name:           libssh2
Version:        1.4.2
Release:        3%{?dist}.1
Summary:        A library implementing the SSH2 protocol

Group:          System Environment/Libraries
License:        BSD
URL:            http://www.libssh2.org/
Source0:        http://libssh2.org/download/libssh2-%{version}.tar.gz
Patch0:         libssh2-1.4.2-tests-mansyntax.patch
Patch1:         libssh2-1.4.2-fips.patch
Patch2:         libssh2-1.4.2-CVE-2016-0787.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  openssh-server
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel

# fix integer overflow in transport read resulting in out of bounds write (CVE-2019-3855)
Patch201:   0001-libssh2-1.8.0-CVE-2019-3855.patch

# fix integer overflow in keyboard interactive handling resulting in out of bounds write (CVE-2019-3856)
Patch202:   0002-libssh2-1.8.0-CVE-2019-3856.patch

# fix integer overflow in SSH packet processing channel resulting in out of bounds write (CVE-2019-3857)
Patch203:   0003-libssh2-1.8.0-CVE-2019-3857.patch

# fix integer overflow in keyboard interactive handling that allows out-of-bounds writes (CVE-2019-3863)
Patch209:   0009-libssh2-1.8.0-CVE-2019-3863.patch


%description
libssh2 is a library implementing the SSH2 protocol as defined by
Internet Drafts: SECSH-TRANS(22), SECSH-USERAUTH(25),
SECSH-CONNECTION(23), SECSH-ARCH(20), SECSH-FILEXFER(06)*,
SECSH-DHGEX(04), and SECSH-NUMBERS(10).


%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        docs
Summary:        Documentation for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    docs
The %{name}-docs package contains man pages and examples for
developing applications that use %{name}.


%prep
%setup -q
%patch0 -p1

# Make sure libssh2 works in FIPS mode...
%patch1 -p1

# use secrects of the appropriate length in Diffie-Hellman (CVE-2016-0787)
%patch2 -p1

# rhel-6.10.z patches
%patch201 -p1
%patch202 -p1
%patch203 -p1
%patch209 -p1

# make sure things are UTF-8...
for i in ChangeLog NEWS ; do
    iconv --from=ISO-8859-1 --to=UTF-8 $i > new
    mv new $i
done

# make it possible to launch OpenSSH server for testing purposes
chcon -t initrc_exec_t tests/ssh2.sh || :
chcon -Rt etc_t tests/etc || :
chcon -t sshd_key_t tests/etc/{host,user} || :


%build
%configure --disable-static --enable-shared --with-openssl

make %{?_smp_mflags}

%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot} INSTALL="install -p"
find %{buildroot} -name '*.la' -exec rm -f {} +

# clean things up a bit for packaging
make -C example clean
rm -rf example/.deps
find example/ -type f '(' -name '*.am' -o -name '*.in' ')' -exec rm -v {} +

# avoid multilib conflict on libssh2-devel
mv -v example example.%{_arch}

%check
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
make check -C tests

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README NEWS
%{_libdir}/libssh2.so.1
%{_libdir}/libssh2.so.1.*

%files docs
%defattr(-,root,root,-)
%doc COPYING HACKING example.%{_arch}/
%{_mandir}/man3/libssh2_*.3*

%files devel
%defattr(-,root,root,-)
%doc COPYING
%{_includedir}/libssh2.h
%{_includedir}/libssh2_publickey.h
%{_includedir}/libssh2_sftp.h
%{_libdir}/libssh2.so
%{_libdir}/pkgconfig/libssh2.pc

%changelog
* Tue Mar 19 2019 Kamil Dudka <kdudka@redhat.com> - 1.4.2-3.el6_10.1
- fix integer overflow in keyboard interactive handling that allows out-of-bounds writes (CVE-2019-3863)
- fix integer overflow in SSH packet processing channel resulting in out of bounds write (CVE-2019-3857)
- fix integer overflow in keyboard interactive handling resulting in out of bounds write (CVE-2019-3856)
- fix integer overflow in transport read resulting in out of bounds write (CVE-2019-3855)

* Fri Feb 19 2016 Kamil Dudka <kdudka@redhat.com> - 1.4.2-3
- use secrects of the appropriate length in Diffie-Hellman (CVE-2016-0787)

* Fri May 31 2013 Kamil Dudka <kdudka@redhat.com> - 1.4.2-2
- fix basic functionality of libssh2 in FIPS mode (#968575)

* Fri Jul 20 2012 Kamil Dudka <kdudka@redhat.com> - 1.4.2-1
- rebase to libssh2-1.4.2 (#745420, #749873, #804150, #806862)

* Wed Jun 20 2012 Kamil Dudka <kdudka@redhat.com> - 1.2.2-11
- do not return LIBSSH2_ERROR_EAGAIN in blocking mode (#826511)

* Mon Mar 19 2012 Kamil Dudka <kdudka@redhat.com> - 1.2.2-10
- transport_send: finish in-progress key exchange before sending data (#804145)

* Wed Mar 14 2012 Kamil Dudka <kdudka@redhat.com> - 1.2.2-9
- avoid a crash of curl when downloading large files using SFTP (#801428)

* Tue Oct 04 2011 Kamil Dudka <kdudka@redhat.com> - 1.2.2-8
- fix memory safety errors and memory leakage (#741919)

* Wed Jul 21 2010 Ondrej Vasik <ovasik@redhat.com> - 1.2.2-7
- two other SELinux issues still caused build failure in mock
  in the enforcing mode(#558911)

* Mon Jun 21 2010 Kamil Dudka <kdudka@redhat.com> - 1.2.2-6
- avoid multilib conflict on libssh2-docs (#605082)

* Tue Jan 26 2010 Kamil Dudka <kdudka@redhat.com> - 1.2.2-5
- avoid build failure in mock with SELinux in the enforcing mode (#558911)

* Sun Dec 06 2009 Kamil Dudka <kdudka@redhat.com> - 1.2.2-4
- fix padding in ssh-dss signature blob encoding (#539444)
- fix gcc warnings

* Wed Dec 02 2009 Kamil Dudka <kdudka@redhat.com> - 1.2.2-3
- boost test suite coverage by having a ssh server available

* Wed Dec 02 2009 Kamil Dudka <kdudka@redhat.com> - 1.2.2-2
- reenable test suite

* Tue Dec 01 2009 Kamil Dudka <kdudka@redhat.com> - 1.2.2-1
- new upstream release

* Mon Nov 23 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.2-2.1
- Rebuilt for RHEL 6

* Mon Sep 21 2009 Chris Weyl <cweyl@alumni.drew.edu> 1.2-2
- patch based on 683aa0f6b52fb1014873c961709102b5006372fc
- disable tests (*sigh*)

* Tue Aug 25 2009 Chris Weyl <cweyl@alumni.drew.edu> 1.2-1
- update to 1.2

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.0-4
- rebuilt with new openssl

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Chris Weyl <cweyl@alumni.drew.edu> 1.0-1
- update to 1.0

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 0.18-8
- rebuild with new openssl

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.18-7
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Chris Weyl <cweyl@alumni.drew.edu> 0.18-6
- rebuild for new openssl...

* Tue Nov 27 2007 Chris Weyl <cweyl@alumni.drew.edu> 0.18-5
- bump

* Tue Nov 27 2007 Chris Weyl <cweyl@alumni.drew.edu> 0.18-4
- add INSTALL arg to make install vs env. var

* Mon Nov 26 2007 Chris Weyl <cweyl@alumni.drew.edu> 0.18-3
- run tests; don't package test

* Sun Nov 18 2007 Chris Weyl <cweyl@alumni.drew.edu> 0.18-2
- split docs into -docs (they seemed... large.)

* Tue Nov 13 2007 Chris Weyl <cweyl@alumni.drew.edu> 0.18-1
- update to 0.18

* Sun Oct 14 2007 Chris Weyl <cweyl@alumni.drew.edu> 0.17-1
- update to 0.17
- many spec file changes

* Wed May 23 2007 Sindre Pedersen Bjørdal <foolish[AT]guezz.net> - 0.15-0.2.20070506
- Fix release tag
- Move manpages to -devel package
- Add Examples dir to -devel package

* Sun May 06 2007 Sindre Pedersen Bjørdal <foolish[AT]guezz.net> - 0.15-0.20070506.1
- Initial build
