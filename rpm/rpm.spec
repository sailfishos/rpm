%define rpmhome /usr/lib/rpm

Summary: The RPM package management system
Name: rpm
Version: 4.19.1.1
Release: 1
%include rpm/shared.inc

Requires: curl
Requires: coreutils
Requires: db4-utils
BuildRequires: db4-devel
BuildRequires: meego-rpm-config
BuildRequires: gcc
BuildRequires: make
BuildRequires: cmake >= 3.18
BuildRequires: gawk
BuildRequires: elfutils-devel >= 0.112
BuildRequires: elfutils-libelf-devel
BuildRequires: zlib-devel
BuildRequires: openssl-devel
BuildRequires: popt-devel >= 1.16
BuildRequires: file-devel
BuildRequires: gettext-devel >= 0.19.8
BuildRequires: ncurses-devel
BuildRequires: bzip2-devel >= 0.9.0c-2
BuildRequires: lua-devel >= 5.1
BuildRequires: libcap-devel
BuildRequires: xz-devel >= 4.999.8
BuildRequires: libarchive-devel
BuildRequires: libzstd-devel
BuildRequires: libacl-devel

# Need rpm-sign for the work around to include old version of so files
# can be removed after transition
BuildRequires: rpm-sign

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Provides:      rpm-libs = %{version}-%{release}
Obsoletes:     rpm-libs < %{version}-%{release}

%description
The RPM Package Manager (RPM) is a powerful command line driven
package management system capable of installing, uninstalling,
verifying, querying, and updating software packages. Each software
package consists of an archive of files along with information about
the package like its version, a description, etc.
This package also contains the RPM shared libraries.

%package libs
Summary:  Libraries for manipulating RPM packages
License: GPLv2+ and LGPLv2+ with exceptions
Requires: rpm = %{version}-%{release}

%description libs
This is an empty transitional package.

%package devel
Summary:  Development files for manipulating RPM packages
License: GPLv2+ and LGPLv2+ with exceptions
Requires: rpm = %{version}-%{release}
Requires: file-devel
Requires: popt-devel

%description devel
This package contains the RPM C library and header files. These
development files will simplify the process of writing programs that
manipulate RPM packages and databases. These files are intended to
simplify the process of creating graphical package managers or any
other tools that need an intimate knowledge of RPM packages in order
to function.

This package should be installed if you want to develop programs that
will manipulate RPM packages and databases.

%package build
Summary: Scripts and executable programs used to build packages
Requires: rpm = %{version}-%{release}
Requires: elfutils >= 0.128 binutils
Requires: findutils sed grep gawk diffutils file patch >= 2.5
Requires: tar unzip gzip bzip2 cpio lzma xz
Requires: zstd
Requires: pkgconfig

%description build
The rpm-build package contains the scripts and executable programs
that are used to build packages using the RPM Package Manager.

%package doc
Summary:  Documentation for %{name}
Requires: rpm = %{version}-%{release}

%description doc
Man pages for %{name}, %{name}-build and %{name}-devel.

%prep
%autosetup  -n rpm-%{version}/upstream -p1

%build
CFLAGS="$RPM_OPT_FLAGS"
export CPPFLAGS CFLAGS LDFLAGS

%cmake \
    -DRPM_CONFIGDIR=%{rpmhome} \
    -DCMAKE_INSTALL_PREFIX=%{_usr} \
    -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} \
    -DCMAKE_INSTALL_LOCALSTATEDIR=%{_var} \
    -DCMAKE_INSTALL_SHAREDSTATEDIR=%{_var}/lib \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DRPM_VENDOR=meego \
    -DWITH_OPENSSL=ON \
    -DWITH_CAP=ON \
    -DWITH_DBUS=OFF \
    -DWITH_READLINE=OFF \
    -DENABLE_SQLITE=OFF \
    -DENABLE_PYTHON=OFF \
    -DWITH_INTERNAL_OPENPGP=ON \
    -DENABLE_TESTSUITE=OFF \
    -DWITH_AUDIT=OFF \
    -DWITH_SELINUX=OFF \
    -DWITH_FAPOLICYD=OFF \
    -DWITH_IMAEVM=OFF \
    .
%cmake_build

%install
%cmake_install

#sed "s/i386/arm/g" platform > platform.arm
#sed "s/i386/mipsel/g" platform > platform.mipsel

#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.arm arm %%{_vendor} linux -gnueabi
#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.mipsel mipsel %%{_vendor} linux -gnu

find %{buildroot} -regex ".*\\.la$" | xargs rm -f -- 

# We cannot use _unitdir macro as we don't want to depend on systemd
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/usr/lib/systemd/system

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
mkdir -p $RPM_BUILD_ROOT%{rpmhome}/macros.d
mkdir -p $RPM_BUILD_ROOT/bin
mkdir -p $RPM_BUILD_ROOT%{rpmhome}/rpm/fileattrs

rm -f ${RPM_BUILD_ROOT}%{rpmhome}/rpm/fileattrs/ksyms.attr
mkdir -p $RPM_BUILD_ROOT/var/lib/rpm
ln -s %{_bindir}/rpm $RPM_BUILD_ROOT/bin/

%find_lang %{name}

find $RPM_BUILD_ROOT -name "*.la"|xargs rm -f

# Remove php macro as we don't use php
rm -f $RPM_BUILD_ROOT/%{rpmhome}/macros.php

# Move doc files to their directory
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/ CREDITS README
echo "This is an empty package" > $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README.rpm-libs
chmod 0644 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README.rpm-libs

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
test -f var/lib/rpm/Packages || rpmdb --initdb

%postun -p /sbin/ldconfig

# Handle rpmdb rebuild service on erasure of old to avoid ordering issues
# https://pagure.io/fesco/issue/2382
%triggerun -- rpm < 4.16.1.3+git2
if [ -x /usr/bin/systemctl ]; then
    systemctl --no-reload preset rpmdb-rebuild ||:
fi

%posttrans
if [ -f /var/lib/rpm/Packages ]; then
    touch /var/lib/rpm/.rebuilddb
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%license COPYING

/usr/lib/systemd/system/rpmdb-rebuild.service

%dir %{_sysconfdir}/rpm

%attr(0755, root, root) %dir /var/lib/rpm
%attr(0755, root, root) %dir %{rpmhome}

/bin/rpm
%{_bindir}/rpm
%{_bindir}/rpmkeys
%{_bindir}/rpm2cpio
%{_bindir}/rpmdb
%{_bindir}/rpmquery
%{_bindir}/rpmsort
%{_bindir}/rpmverify
%{_bindir}/rpm2archive
%{_libdir}/rpm-plugins/syslog.so
%{_libdir}/rpm-plugins/prioreset.so

%{rpmhome}/macros
%{rpmhome}/macros.d
%{rpmhome}/rpmpopt*
%{rpmhome}/rpmrc
%{rpmhome}/rpmdb_*
%{rpmhome}/rpmuncompress
%{rpmhome}/rpm.daily
%{rpmhome}/rpm.log
%{rpmhome}/rpm.supp
%{rpmhome}/rpm2cpio.sh
%{rpmhome}/sysusers.sh
%{rpmhome}/tgpg
%{rpmhome}/platform

%dir %{rpmhome}/fileattrs

%{_libdir}/librpmio.so.*
%{_libdir}/librpm.so.*

%files build
%{_bindir}/rpmbuild
%{_bindir}/rpmlua
%{_bindir}/gendiff
%{_bindir}/rpmspec
%doc %{_defaultdocdir}/rpm/CREDITS
%doc %{_defaultdocdir}/rpm/COPYING
%doc %{_defaultdocdir}/rpm/INSTALL
%doc %{_defaultdocdir}/rpm/README

%{_libdir}/librpmbuild.so.*

%{rpmhome}/brp-*
%{rpmhome}/check-*
%{rpmhome}/find-lang.sh
%{rpmhome}/*provides*
%{rpmhome}/*requires*
%{rpmhome}/*deps*
%{rpmhome}/*.prov
%{rpmhome}/*.req
%{rpmhome}/fileattrs/*

%files devel
%defattr(-,root,root)
%{_includedir}/rpm
%{_libdir}/librp*[a-z].so
%{_bindir}/rpmgraph
%{_libdir}/pkgconfig/rpm.pc
%{_libdir}/cmake/rpm/


%files doc
%defattr(-, root, root)
%doc %{_docdir}/%{name}-%{version}

# Upstream has documentation in Markdown, which would need pandoc
# to generate manpages. We don't have it, so package the md files instead.
%{_docdir}/%{name}/*.md

%files libs
%defattr(-,root,root)
%doc %{_docdir}/%{name}-%{version}/README.rpm-libs

%package sign
Summary:   Package signing support
License:   GPLv2+ and LGPLv2+ with exceptions
Requires:  rpm  = %{version}-%{release}
Requires:  %{_bindir}/gpg2

%description sign
This package contains support for digitally signing RPM packages.

%files sign
%{_bindir}/rpmsign
%{_libdir}/librpmsign.so.*

%post sign -p /sbin/ldconfig
%postun sign -p /sbin/ldconfig
