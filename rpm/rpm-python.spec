# build against xz?
%bcond_without xz
# build against python
%bcond_without python
# sqlite backend is pretty useless
%bcond_with sqlite
# just for giggles, option to build with internal Berkeley DB
%bcond_with int_bdb

%define rpmhome /usr/lib/rpm

%define rpmver 4.13.0.rc1

%global py_ver %(python2 -c 'import sys; print sys.version[:3]')

%define py_libdir %{_libdir}/python%{py_ver}

%define py_sitedir %{py_libdir}/site-packages

Summary: The RPM package management system
Name: rpm-python
Version: 4.13.0.rc1
Release: 1
BuildRequires: python-devel
# Up to END_OF_INCLUDE_IN_PYTHON_SPEC lines are from the main spec file
Source0: http://rpm.org/releases/%{name}-%{version}.tar.bz2
Source1: libsymlink.attr
Patch12:	0012-openSUSE-finddebuginfo-patch.patch
Patch13:	0013-Add-debugsource-package-to-rpm-straight-don-t-strip.patch
Patch14:	0014-OpenSUSE-finddebuginfo-absolute-links.patch
Patch17:	0017-OpenSUSE-debugsubpkg.patch
Patch18:	0018-OpenSUSE-fileattrs.patch
Patch19:	0019-OpenSUSE-elfdeps.patch
Group: System/Base
Url: http://www.rpm.org/
# See also https://github.com/mer-packages/rpm/



# Partially GPL/LGPL dual-licensed and some bits with BSD
# SourceLicense: (GPLv2+ and LGPLv2+ with exceptions) and BSD 
License: GPLv2+
##END_OF_INCLUDE_IN_PYTHON_SPEC##
Requires: coreutils
Requires: db4-utils
Requires: popt >= 1.10.2.1
Requires: curl
Requires: rpm = %{version}
BuildRequires: db4-devel


# XXX generally assumed to be installed but make it explicit as rpm
# is a bit special...
BuildRequires: meego-rpm-config
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: libarchive-devel
BuildRequires: gawk
BuildRequires: elfutils-devel >= 0.112
BuildRequires: elfutils-libelf-devel
BuildRequires: readline-devel zlib-devel
BuildRequires: nss-devel
# The popt version here just documents an older known-good version
BuildRequires: popt-devel >= 1.10.2
BuildRequires: file-devel
BuildRequires: gettext-devel
BuildRequires: ncurses-devel
BuildRequires: bzip2-devel >= 0.9.0c-2
BuildRequires: lua-devel >= 5.1
BuildRequires: libcap-devel
BuildRequires: xz-devel >= 4.999.8
BuildRequires: cvs
BuildRequires: dbus-devel

%description
The RPM Package Manager (RPM) is a powerful command line driven
package management system capable of installing, uninstalling,
verifying, querying, and updating software packages. Each software
package consists of an archive of files along with information about
the package like its version, a description, etc.

%prep
# prep and build sections are from the main spec file
%setup -q  -n %{name}-%{version}/upstream
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1

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

make %{?jobs:-j%jobs}

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR="$RPM_BUILD_ROOT" install
find "%{buildroot}" -not -type d -and -not -path %{buildroot}%{_libdir}/python%{py_ver}/site-packages/rpm/\* -print0 | xargs -0 rm
pushd $RPM_BUILD_ROOT/%py_sitedir/rpm
rm -f _rpmmodule.a _rpmmodule.la
python %py_libdir/py_compile.py *.py
python -O %py_libdir/py_compile.py *.py
popd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_libdir}/python*
