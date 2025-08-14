Source0: %{name}-%{version}.tar.bz2
Source1: libsymlink.attr
Source2: rpmdb-rebuild.service
Source100: shared.inc

Patch1:  0001-OpenSUSE-fileattrs.patch
Patch2:  0002-OpenSUSE-elfdeps.patch
Patch3:  0003-rpmbuild-Add-nobuildstage-to-not-execute-build-stage.patch
Patch4:  0004-Omit-debug-info-from-main-package-and-enable-debugso.patch
Patch5:  0005-Use-POSIX-compatible-arguments-for-find.patch
Patch6:  0006-Make-the-plugin-API-public.patch
# Fix for error: liblzma: Memory allocation failed
# Next version of rpm should have better handling of parallel processes
# so then it could probably be removed.
Patch7:  0007-Limit-to-4-threads-for-lzma-compression-to-make-sure.patch
Patch8:  0008-Revert-Don-t-set-target-in-configure-RhBug-458648.patch
Patch9:  0009-Also-delete-symbol-links-that-could-point-to-la-file.patch
Patch10: 0010-Exclude-usr-share-info-dir-from-check-files.patch

# Partially GPL/LGPL dual-licensed and some bits with BSD
# SourceLicense: (GPLv2+ and LGPLv2+ with exceptions) and BSD
License: GPLv2+

Url: https://github.com/sailfishos/rpm
