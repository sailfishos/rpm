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
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: gawk
BuildRequires: elfutils-devel >= 0.112
BuildRequires: elfutils-libelf-devel
BuildRequires: zlib-devel
BuildRequires: openssl-devel
# The popt version here just documents an older known-good version
BuildRequires: popt-devel >= 1.10.2
BuildRequires: file-devel
BuildRequires: gettext-devel
BuildRequires: ncurses-devel
BuildRequires: bzip2-devel >= 0.9.0c-2
BuildRequires: lua-devel
BuildRequires: libcap-devel
BuildRequires: xz-devel >= 4.999.8
BuildRequires: libarchive-devel
BuildRequires: libzstd-devel
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

%package doc
Summary:  Documentation for %{name}
Requires: rpm = %{version}-%{release}

%description doc
Man pages for %{name}, %{name}-build and %{name}-devel.

%prep
%autosetup -p1 -n rpm-%{version}/upstream

%build
CFLAGS="$RPM_OPT_FLAGS"
export CPPFLAGS CFLAGS LDFLAGS

./autogen.sh \
    --prefix=%{_usr} \
    --sysconfdir=%{_sysconfdir} \
    --localstatedir=%{_var} \
    --sharedstatedir=%{_var}/lib \
    --libdir=%{_libdir} \
    --with-vendor=meego \
    --with-external-db \
    --with-crypto=openssl \
    --enable-zstd \
    --with-lua \
    --with-cap \
    --disable-inhibit-plugin \
    --enable-ndb

%make_build

%install
rm -rf $RPM_BUILD_ROOT

%make_install

#sed "s/i386/arm/g" platform > platform.arm
#sed "s/i386/mipsel/g" platform > platform.mipsel

#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.arm arm %%{_vendor} linux -gnueabi
#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.mipsel mipsel %%{_vendor} linux -gnu

find %{buildroot} -regex ".*\\.la$" | xargs rm -f --

# We cannot use _unitdir macro as we don't want to depend on systemd
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/usr/lib/systemd/system

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
mkdir -p $RPM_BUILD_ROOT%{rpmhome}/macros.d
mkdir -p $RPM_BUILD_ROOT/bin
mkdir -p $RPM_BUILD_ROOT%{rpmhome}/rpm/fileattrs

install -m 644 %{SOURCE1} ${RPM_BUILD_ROOT}%{rpmhome}/fileattrs/libsymlink.attr
rm -f ${RPM_BUILD_ROOT}%{rpmhome}/rpm/fileattrs/ksyms.attr
mkdir -p $RPM_BUILD_ROOT/var/lib/rpm
ln -s %{_bindir}/rpm $RPM_BUILD_ROOT/bin/

%find_lang %{name}

find $RPM_BUILD_ROOT -name "*.la"|xargs rm -f

# Remove php macro as we don't use php
rm -f $RPM_BUILD_ROOT/%{rpmhome}/macros.php

# These live in python-rpm-generators now
# https://bugzilla.redhat.com/show_bug.cgi?id=1410631
rm -f $RPM_BUILD_ROOT/%{rpmhome}/pythond*
rm -f $RPM_BUILD_ROOT/%{_fileattrsdir}/python*

# Move doc files to their directory
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/ CREDITS README
echo "This is an empty package" > $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README.rpm-libs
chmod 0644 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/README.rpm-libs

# Provide symlinks for legacy location bins and scripts. JB#62519
ln -sf %{_bindir}/debugedit      $RPM_BUILD_ROOT%{rpmhome}/debugedit
ln -sf %{_bindir}/find-debuginfo $RPM_BUILD_ROOT%{rpmhome}/find-debuginfo.sh
ln -sf %{_bindir}/sepdebugcrcfix $RPM_BUILD_ROOT%{rpmhome}/sepdebugcrcfix

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
%attr(0755, root, root) %dir %{rpmhome}

/bin/rpm
%{_bindir}/rpm
%{_bindir}/rpmkeys
%{_bindir}/rpm2cpio
%{_bindir}/rpmdb
%{_bindir}/rpmquery
%{_bindir}/rpmverify
%{_bindir}/rpm2archive
%{_libdir}/rpm-plugins/syslog.so
%{_libdir}/rpm-plugins/ima.so
%{_libdir}/rpm-plugins/prioreset.so

%{rpmhome}/macros
%{rpmhome}/macros.d
%{rpmhome}/rpmpopt*
%{rpmhome}/rpmrc
%{rpmhome}/rpmdb_*
%{rpmhome}/rpm.daily
%{rpmhome}/rpm.log
%{rpmhome}/rpm.supp
%{rpmhome}/rpm2cpio.sh
%{rpmhome}/tgpg
%{rpmhome}/platform

%dir %{rpmhome}/fileattrs

%{_libdir}/librpmio.so.*
%{_libdir}/librpm.so.*

%files build
%{_bindir}/rpmbuild
%{_bindir}/gendiff
%{_bindir}/rpmspec

%{_libdir}/librpmbuild.so.*

%{rpmhome}/brp-*
%{rpmhome}/check-*

# Remove these when updating rpm. JB#62519
%{rpmhome}/debugedit
%{rpmhome}/sepdebugcrcfix
%{rpmhome}/find-debuginfo.sh

%{rpmhome}/find-lang.sh
%{rpmhome}/*provides*
%{rpmhome}/*requires*
%{rpmhome}/*deps*
%{rpmhome}/*.prov
%{rpmhome}/*.req
%{rpmhome}/mkinstalldirs
%{rpmhome}/fileattrs/*

%files devel
%defattr(-,root,root)
%{_includedir}/rpm
%{_libdir}/librp*[a-z].so
%{_bindir}/rpmgraph
%{_libdir}/pkgconfig/rpm.pc


%files doc
%defattr(-, root, root)
%doc %{_docdir}/%{name}-%{version}

%{_mandir}/man8/rpm.8*
%{_mandir}/man8/rpm2cpio.8*
%{_mandir}/man8/rpmdb.8.gz
%{_mandir}/man8/rpmkeys.8.gz
%{_mandir}/man8/rpmspec.8.gz
%{_mandir}/man8/rpm-misc.8.gz
%{_mandir}/man8/rpm-plugin-ima.8.gz
%{_mandir}/man8/rpm-plugin-prioreset.8.gz
%{_mandir}/man8/rpm-plugin-syslog.8.gz
%{_mandir}/man8/rpm-plugins.8.gz
%{_mandir}/man8/rpm2archive.8.gz

# XXX this places translated manuals to wrong package wrt eg rpmbuild
%lang(fr) %{_mandir}/fr/man[18]/*.[18]*
%lang(ko) %{_mandir}/ko/man[18]/*.[18]*
%lang(ja) %{_mandir}/ja/man[18]/*.[18]*
%lang(pl) %{_mandir}/pl/man[18]/*.[18]*
%lang(ru) %{_mandir}/ru/man[18]/*.[18]*
%lang(sk) %{_mandir}/sk/man[18]/*.[18]*

%{_mandir}/man1/gendiff.1*
%{_mandir}/man8/rpmbuild.8*
%{_mandir}/man8/rpmdeps.8*

%{_mandir}/man8/rpmgraph.8*

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
%{_mandir}/man8/rpmsign.8*
%{_libdir}/librpmsign.so.*

%post sign -p /sbin/ldconfig
%postun sign -p /sbin/ldconfig
