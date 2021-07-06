%global py_ver %(python3 -c 'import sys; print(sys.version[:3])')

%define py_libdir %{_libdir}/python%{py_ver}
%define py_sitedir %{py_libdir}/site-packages

Summary: The RPM package management system python3 support
Name: rpm-python
Version: 4.16.1.3
Release: 1
Source0: %{name}-%{version}.tar.bz2
Source1: libsymlink.attr
Source2: rpmdb-rebuild.service
Patch1:  0001-openSUSE-finddebuginfo-patch.patch
Patch2:  0002-OpenSUSE-finddebuginfo-absolute-links.patch
Patch3:  0003-OpenSUSE-debugsubpkg.patch
Patch4:  0004-OpenSUSE-fileattrs.patch
Patch5:  0005-OpenSUSE-elfdeps.patch
Patch8:  0008-rpmbuild-Add-nobuildstage-to-not-execute-build-stage.patch
Patch9:  0009-Compatibility-with-older-dd.patch
Patch10: 0010-Omit-debug-info-from-main-package-and-enable-debugso.patch
Patch11: 0011-Disable-systemdinhibit-plugin-to-minimize-dependenci.patch
Patch13: 0013-Use-POSIX-compatible-arguments-for-find.patch
Patch17: 0017-rpmsign-Close-file-before-replacing.patch
Patch18: 0018-include-plugin-header.patch
# Fix for error: liblzma: Memory allocation failed
# Next version of rpm should have better handling of parallel processes
# so then it could probably be removed.
Patch19: 0019-Limit-to-4-threads-for-lzma-compression-to-make-sure.patch
Patch20: 0020-Do-not-fail-on-magic-errors.patch
Url: http://www.rpm.org/

# Partially GPL/LGPL dual-licensed and some bits with BSD
# SourceLicense: (GPLv2+ and LGPLv2+ with exceptions) and BSD 
License: GPLv2+

Requires: rpm = %{version}
Requires: python3-base

BuildRequires: python3-devel
BuildRequires: db4-devel
BuildRequires: meego-rpm-config
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: libarchive-devel
BuildRequires: gawk
BuildRequires: elfutils-devel >= 0.112
BuildRequires: elfutils-libelf-devel
BuildRequires: readline-devel zlib-devel
BuildRequires: openssl-devel
# The popt version here just documents an older known-good version
BuildRequires: popt-devel >= 1.10.2
BuildRequires: file-devel
BuildRequires: gettext-devel
BuildRequires: ncurses-devel
BuildRequires: bzip2-devel >= 0.9.0c-2
BuildRequires: lua-devel >= 5.1
BuildRequires: libcap-devel
BuildRequires: xz-devel >= 4.999.8

%description
The RPM Package Manager (RPM) is a powerful command line driven
package management system capable of installing, uninstalling,
verifying, querying, and updating software packages. Each software
package consists of an archive of files along with information about
the package like its version, a description, etc.

This package contains python3 support

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

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
    --with-lua \
    --with-cap \
    --enable-python

%make_build

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR="$RPM_BUILD_ROOT" install
find "%{buildroot}" -not -type d -and -not -path %{buildroot}%{_libdir}/python%{py_ver}/site-packages/rpm/\* -print0 | xargs -0 rm
pushd $RPM_BUILD_ROOT/%py_sitedir/rpm
rm -f _rpmmodule.a _rpmmodule.la
python3 %py_libdir/py_compile.py *.py
python3 -O %py_libdir/py_compile.py *.py
popd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_libdir}/python*

