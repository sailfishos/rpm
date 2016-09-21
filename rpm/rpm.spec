# run internal testsuite?
%bcond_without check

Summary: The RPM package management system
Name: rpm
Version: 4.14.1
Release: 1
Source0: http://rpm.org/releases/%{name}-%{version}.tar.bz2
Source1: libsymlink.attr
Patch1:  0001-openSUSE-finddebuginfo-patch.patch
Patch2:  0002-OpenSUSE-finddebuginfo-absolute-links.patch
Patch3:  0003-OpenSUSE-debugsubpkg.patch
Patch4:  0004-OpenSUSE-fileattrs.patch
Patch5:  0005-OpenSUSE-elfdeps.patch
Patch6:  0006-add-python3-macro.patch
Patch7:  0007-rpmbuild-Add-nobuildstage-to-not-execute-build-stage.patch
Patch8:  0008-Compatibility-with-older-dd.patch
Patch9:  0009-Omit-debug-info-from-main-package-and-enable-debugso.patch
Patch10: 0010-Disable-systemdinhibit-plugin-to-minimize-dependenci.patch
Group: System/Base
Url: http://www.rpm.org/
# See also https://github.com/mer-packages/rpm/



# Partially GPL/LGPL dual-licensed and some bits with BSD
# SourceLicense: (GPLv2+ and LGPLv2+ with exceptions) and BSD 
License: GPLv2+
##END_OF_INCLUDE_IN_PYTHON_SPEC##

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
BuildRequires: readline-devel zlib-devel
BuildRequires: nss-devel
# The popt version here just documents an older known-good version
BuildRequires: popt-devel >= 1.10.2
BuildRequires: file-devel
BuildRequires: gettext-devel
BuildRequires: cvs
BuildRequires: ncurses-devel
BuildRequires: bzip2-devel >= 0.9.0c-2
BuildRequires: lua-devel >= 5.1
BuildRequires: libcap-devel
BuildRequires: xz-devel >= 4.999.8
BuildRequires: libarchive-devel
BuildRequires: python

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The RPM Package Manager (RPM) is a powerful command line driven
package management system capable of installing, uninstalling,
verifying, querying, and updating software packages. Each software
package consists of an archive of files along with information about
the package like its version, a description, etc.

%package libs
Summary:  Libraries for manipulating RPM packages
Group: Development/Libraries
License: GPLv2+ and LGPLv2+ with exceptions
Requires: rpm = %{version}-%{release}

%description libs
This package contains the RPM shared libraries.

%package devel
Summary:  Development files for manipulating RPM packages
Group: Development/Libraries
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
Group: Development/Tools
Requires: rpm = %{version}-%{release}
Requires: elfutils >= 0.128 binutils
Requires: findutils sed grep gawk diffutils file patch >= 2.5
Requires: unzip gzip bzip2 cpio lzma xz
Requires: pkgconfig

%description build
The rpm-build package contains the scripts and executable programs
that are used to build packages using the RPM Package Manager.
#

%prep
%setup -q  -n rpm-%{version}/upstream
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1

%build
CPPFLAGS="$CPPFLAGS `pkg-config --cflags nss`"
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
%if %{with python}
    --enable-python \
%endif
    --with-lua \
    --with-cap  

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

%make_install

# HACK: include older .so so we can get everything rebuild properly
cp -a /%{_libdir}/librpm.so.2.0.2 $RPM_BUILD_ROOT/%{_libdir}/
cp -a /%{_libdir}/librpm.so.2 $RPM_BUILD_ROOT/%{_libdir}/
cp -a /%{_libdir}/librpmbuild.so.2.0.1 $RPM_BUILD_ROOT/%{_libdir}/
cp -a /%{_libdir}/librpmbuild.so.2 $RPM_BUILD_ROOT/%{_libdir}/
cp -a /%{_libdir}/librpmio.so.2.0.1 $RPM_BUILD_ROOT/%{_libdir}/
cp -a /%{_libdir}/librpmio.so.2 $RPM_BUILD_ROOT/%{_libdir}/
cp -a /%{_libdir}/librpmsign.so.0.0.1 $RPM_BUILD_ROOT/%{_libdir}/
cp -a /%{_libdir}/librpmsign.so.0 $RPM_BUILD_ROOT/%{_libdir}/

#sed "s/i386/arm/g" platform > platform.arm
#sed "s/i386/mipsel/g" platform > platform.mipsel

#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.arm arm %{_vendor} linux -gnueabi
#DESTDIR=$RPM_BUILD_ROOT ./installplatform rpmrc macros platform.mipsel mipsel %{_vendor} linux -gnu


find %{buildroot} -regex ".*\\.la$" | xargs rm -f -- 

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
mkdir -p $RPM_BUILD_ROOT%{_libdir}/rpm
mkdir -p $RPM_BUILD_ROOT/bin
install -m 644 %{SOURCE1} ${RPM_BUILD_ROOT}%{_libdir}/rpm/fileattrs/libsymlink.attr
rm -f ${RPM_BUILD_ROOT}%{_libdir}/rpm/fileattrs/ksyms.attr
mkdir -p $RPM_BUILD_ROOT/var/lib/rpm
ln -s %{_bindir}/rpm $RPM_BUILD_ROOT/bin/

for dbi in \
    Basenames Conflictname Dirnames Group Installtid Name Packages \
    Providename Provideversion Requirename Requireversion Triggername \
    Filedigests Pubkeys Sha1header Sigmd5 Obsoletename \
    __db.001 __db.002 __db.003 __db.004 __db.005 __db.006 __db.007 \
    __db.008 __db.009
do
    touch $RPM_BUILD_ROOT/var/lib/rpm/$dbi
done


%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%posttrans
# XXX this is klunky and ugly, rpm itself should handle this
dbstat=/usr/lib/rpm/rpmdb_stat
if [ -x "$dbstat" ]; then
    if "$dbstat" -e -h /var/lib/rpm 2>&1 | grep -q "doesn't match environment version \| Invalid argument"; then
        rm -f /var/lib/rpm/__db.* 
    fi
fi
exit 0

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc COPYING CREDITS README

%dir %{_sysconfdir}/rpm

%attr(0755, root, root)   %dir /var/lib/rpm
%attr(0644, root, root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/lib/rpm/*
%attr(0755, root, root) %dir %{_libdir}/rpm

/bin/rpm
%{_bindir}/rpm
%{_bindir}/rpmkeys
%{_bindir}/rpmspec
%{_bindir}/rpm2cpio
%{_bindir}/rpmdb
%{_bindir}/rpmsign
%{_bindir}/rpmquery
%{_bindir}/rpmverify
%{_bindir}/rpm2archive
%{_libdir}/rpm-plugins/syslog.so
%{_libdir}/rpm-plugins/ima.so
%{_libdir}/rpm-plugins/prioreset.so

%doc %{_mandir}/man8/rpm.8*
%doc %{_mandir}/man8/rpm2cpio.8*
%doc %{_mandir}/man8/rpmdb.8.gz
%doc %{_mandir}/man8/rpmkeys.8.gz
%doc %{_mandir}/man8/rpmsign.8.gz
%doc %{_mandir}/man8/rpmspec.8.gz
%doc %{_mandir}/man8/rpm-misc.8.gz
%doc %{_mandir}/man8/rpm-plugin-systemd-inhibit.8.gz

# XXX this places translated manuals to wrong package wrt eg rpmbuild
%lang(fr) %{_mandir}/fr/man[18]/*.[18]*
%lang(ko) %{_mandir}/ko/man[18]/*.[18]*
%lang(ja) %{_mandir}/ja/man[18]/*.[18]*
%lang(pl) %{_mandir}/pl/man[18]/*.[18]*
%lang(ru) %{_mandir}/ru/man[18]/*.[18]*
%lang(sk) %{_mandir}/sk/man[18]/*.[18]*

%{_libdir}/rpm/macros
%{_libdir}/rpm/rpmpopt*
%{_libdir}/rpm/rpmrc

%{_libdir}/rpm/rpmdb_*
%{_libdir}/rpm/rpm.daily
%{_libdir}/rpm/rpm.log
%{_libdir}/rpm/rpm2cpio.sh
%{_libdir}/rpm/tgpg

%{_libdir}/rpm/platform

%files libs
%defattr(-,root,root)
%{_libdir}/librpm*.so.*

%files build
%defattr(-,root,root)
%{_bindir}/rpmbuild
%{_bindir}/gendiff
%{_mandir}/man1/gendiff.1*

%{_libdir}/rpm/fileattrs/*.attr
%{_libdir}/rpm/script.req
%{_libdir}/rpm/elfdeps
%{_libdir}/rpm/brp-*
%{_libdir}/rpm/check-buildroot
%{_libdir}/rpm/check-files
%{_libdir}/rpm/check-prereqs
%{_libdir}/rpm/check-rpaths*
%{_libdir}/rpm/debugedit
%{_libdir}/rpm/find-debuginfo.sh
%{_libdir}/rpm/find-lang.sh
%{_libdir}/rpm/find-provides
%{_libdir}/rpm/find-requires
%{_libdir}/rpm/mono-find-provides
%{_libdir}/rpm/mono-find-requires
%{_libdir}/rpm/ocaml-find-provides.sh
%{_libdir}/rpm/ocaml-find-requires.sh
%{_libdir}/rpm/libtooldeps.sh
%{_libdir}/rpm/pkgconfigdeps.sh
%{_libdir}/rpm/perl.prov
%{_libdir}/rpm/perl.req
%{_libdir}/rpm/pythondeps.sh
%{_libdir}/rpm/rpmdeps
%{_libdir}/rpm/config.guess
%{_libdir}/rpm/config.sub
%{_libdir}/rpm/mkinstalldirs
%{_libdir}/rpm/desktop-file.prov
%{_libdir}/rpm/fontconfig.prov
%{_libdir}/rpm/macros.perl
%{_libdir}/rpm/macros.python
%{_libdir}/rpm/macros.php
%{_libdir}/rpm/rpm.supp
%{_libdir}/rpm/debuginfo.prov
%{_libdir}/rpm/metainfo.prov
%{_libdir}/rpm/python-macro-helper
%{_libdir}/rpm/pythondistdeps.py
%{_libdir}/rpm/pythondistdeps.pyc
%{_libdir}/rpm/pythondistdeps.pyo
%{_libdir}/rpm/sepdebugcrcfix

%{_mandir}/man8/rpmbuild.8*
%{_mandir}/man8/rpmdeps.8*


%files devel
%defattr(-,root,root)
%{_includedir}/rpm
%{_libdir}/librp*[a-z].so
%{_mandir}/man8/rpmgraph.8*
%{_bindir}/rpmgraph
%{_libdir}/pkgconfig/rpm.pc
