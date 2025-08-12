%define __cmake_builddir python

Summary: The RPM package management system python3 support
Name: rpm-python
Version: 4.19.1.1
Release: 1
# Normally we could just read rpm.spec
# for our sources but tar_git doesn't include rpm.spec
# into this package
%include rpm/shared.inc



Requires: rpm = %{version}
Requires: python3-base

BuildRequires: python3-devel
BuildRequires: db4-devel
BuildRequires: meego-rpm-config
BuildRequires: gcc
BuildRequires: make
BuildRequires: cmake >= 3.18
BuildRequires: libarchive-devel
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
BuildRequires: libzstd-devel

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

%cmake \
    -DCMAKE_INSTALL_PREFIX=%{_usr} \
    -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} \
    -DCMAKE_INSTALL_LOCALSTATEDIR=%{_var} \
    -DCMAKE_INSTALL_SHAREDSTATEDIR=%{_var}/lib \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DRPM_VENDOR=meego \
    -DWITH_OPENSSL=ON \
    -DWITH_CAP=ON \
    -DWITH_ACL=OFF \
    -DWITH_DBUS=OFF \
    -DWITH_READLINE=OFF \
    -DENABLE_SQLITE=OFF \
    -DENABLE_PYTHON=ON \
    -DWITH_INTERNAL_OPENPGP=ON \
    -DENABLE_TESTSUITE=OFF \
    -DWITH_AUDIT=OFF \
    -DWITH_SELINUX=OFF \
    -DWITH_FAPOLICYD=OFF \
    -DWITH_IMAEVM=OFF \
    -DENABLE_NDB=ON \
    .
%cmake_build

%install
%cmake_install

# Remove examples
rm -Rf %{buildroot}%{_docdir}

%files
%{_libdir}/python*
