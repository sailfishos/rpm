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
    --enable-python

%make_build

pushd python
%py3_build
popd

%install
pushd python
%py3_install
popd

%files
%defattr(-,root,root)
%{_libdir}/python*

