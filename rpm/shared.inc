Source0: %{name}-%{version}.tar.bz2
Source1: libsymlink.attr
Source2: rpmdb-rebuild.service
Source100: shared.inc
Patch4:  0004-OpenSUSE-fileattrs.patch
Patch5:  0005-OpenSUSE-elfdeps.patch
Patch8:  0008-rpmbuild-Add-nobuildstage-to-not-execute-build-stage.patch
Patch10: 0010-Omit-debug-info-from-main-package-and-enable-debugso.patch
Patch13: 0013-Use-POSIX-compatible-arguments-for-find.patch
Patch18: 0018-include-plugin-header.patch
# Fix for error: liblzma: Memory allocation failed
# Next version of rpm should have better handling of parallel processes
# so then it could probably be removed.
Patch19: 0019-Limit-to-4-threads-for-lzma-compression-to-make-sure.patch
Patch21: 0021-Revert-Don-t-set-target-in-configure-RhBug-458648.patch
Patch24: 0024-Also-delete-symbol-links-that-could-point-to-la-file.patch
Patch25: 0025-Exclude-usr-share-info-dir-from-check-files.patch

# Partially GPL/LGPL dual-licensed and some bits with BSD
# SourceLicense: (GPLv2+ and LGPLv2+ with exceptions) and BSD 
License: GPLv2+

Url: https://github.com/sailfishos/rpm
