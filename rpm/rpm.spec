Summary: The RPM package management system
Name: rpm
Version: 4.19.1.1
Release: 1
%include rpm/shared.inc

Requires: curl
Requires: coreutils
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
Requires: debugedit

%description build
The rpm-build package contains the scripts and executable programs
that are used to build packages using the RPM Package Manager.

%prep
%autosetup -p1 -n rpm-%{version}/upstream

%build
CFLAGS="$RPM_OPT_FLAGS"
export CPPFLAGS CFLAGS LDFLAGS

%cmake \
    -DRPM_CONFIGDIR=%{_rpmconfigdir} \
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
    -DENABLE_NDB=ON \
    -DENABLE_CUTF8=OFF \
    .
%cmake_build

%install
%cmake_install

#sed "s/i386/arm/g" platform > platform.arm
#sed "s/i386/mipsel/g" platform > platform.mipsel

#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.arm arm %%{_vendor} linux -gnueabi
#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.mipsel mipsel %%{_vendor} linux -gnu

find %{buildroot} -regex ".*\\.la$" | xargs rm -f --

# Database backend is auto-detected during build
if ! grep -E '^%%_db_backend[[:space:]]+ndb$' ${RPM_BUILD_ROOT}%{_rpmconfigdir}/macros; then
    echo "Default database is not ndb"
    exit 1
fi

# We cannot use _unitdir macro as we don't want to depend on systemd
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/usr/lib/systemd/system

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
mkdir -p $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d
mkdir -p $RPM_BUILD_ROOT/bin
mkdir -p $RPM_BUILD_ROOT%{_rpmconfigdir}/rpm/fileattrs

install -m 644 %{SOURCE1} ${RPM_BUILD_ROOT}%{_rpmconfigdir}/fileattrs/libsymlink.attr
rm -f ${RPM_BUILD_ROOT}%{_rpmconfigdir}/rpm/fileattrs/ksyms.attr
mkdir -p $RPM_BUILD_ROOT/var/lib/rpm
ln -s %{_bindir}/rpm $RPM_BUILD_ROOT/bin/

%find_lang %{name}

find $RPM_BUILD_ROOT -name "*.la"|xargs rm -f

# Remove php macro as we don't use php
rm -f $RPM_BUILD_ROOT/%{_rpmconfigdir}/macros.php

# Move doc files to their directory
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/ CREDITS README
echo "This is an empty package" > $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README.rpm-libs
chmod 0644 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README.rpm-libs

rm $RPM_BUILD_ROOT%{_docdir}/%{name}/*.md

# Provide symlinks for legacy location bins and scripts. JB#62519
ln -sf %{_bindir}/debugedit      $RPM_BUILD_ROOT%{_rpmconfigdir}/debugedit
ln -sf %{_bindir}/find-debuginfo $RPM_BUILD_ROOT%{_rpmconfigdir}/find-debuginfo.sh
ln -sf %{_bindir}/sepdebugcrcfix $RPM_BUILD_ROOT%{_rpmconfigdir}/sepdebugcrcfix

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
# When installing for the first time, make sure the database exists.
# bdb: Packages
# ndb: Packages.db
if [ "$1" -eq "1" ] && [ ! -f /var/lib/rpm/Packages ] && [ ! -f /var/lib/rpm/Packages.db ]; then
    rpmdb --initdb
fi

%postun -p /sbin/ldconfig

%posttrans
# Trigger database migration from obsolete bdb to nbd, if bdb is detected.
if [ -f /var/lib/rpm/Packages ]; then
    touch /var/lib/rpm/.rebuilddb
fi
# Make sure the service is enabled.
if [ -x /usr/bin/systemctl ]; then
    systemctl --no-reload preset rpmdb-rebuild ||:
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%license COPYING

/usr/lib/systemd/system/rpmdb-rebuild.service

%dir %{_sysconfdir}/rpm

%attr(0755, root, root) %dir /var/lib/rpm
%attr(0755, root, root) %dir %{_rpmconfigdir}

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

%{_rpmconfigdir}/macros
%{_rpmconfigdir}/macros.d
%{_rpmconfigdir}/rpmpopt*
%{_rpmconfigdir}/rpmrc
%{_rpmconfigdir}/rpmdb_*
%{_rpmconfigdir}/rpmuncompress
%{_rpmconfigdir}/rpm.daily
%{_rpmconfigdir}/rpm.log
%{_rpmconfigdir}/rpm.supp
%{_rpmconfigdir}/rpm2cpio.sh
%{_rpmconfigdir}/sysusers.sh
%{_rpmconfigdir}/tgpg
%{_rpmconfigdir}/platform

%dir %{_rpmconfigdir}/fileattrs

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

%{_rpmconfigdir}/brp-*
%{_rpmconfigdir}/check-*

# Remove these when updating rpm. JB#62519
%{_rpmconfigdir}/debugedit
%{_rpmconfigdir}/sepdebugcrcfix
%{_rpmconfigdir}/find-debuginfo.sh

%{_rpmconfigdir}/find-lang.sh
%{_rpmconfigdir}/*provides*
%{_rpmconfigdir}/*requires*
%{_rpmconfigdir}/*deps*
%{_rpmconfigdir}/*.prov
%{_rpmconfigdir}/*.req
%{_rpmconfigdir}/fileattrs/*

%files devel
%defattr(-,root,root)
%{_includedir}/rpm
%{_libdir}/librp*[a-z].so
%{_bindir}/rpmgraph
%{_libdir}/pkgconfig/rpm.pc
%{_libdir}/cmake/rpm/

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
