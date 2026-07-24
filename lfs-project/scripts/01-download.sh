#!/bin/bash
# LFS Build Script - Chapter 1: Download Packages
# This script downloads all required packages

set -e

echo "=== LFS Build - Download Packages ==="
echo "Starting at: $(date)"

# Set LFS directory
export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources

# Create sources directory
mkdir -p $LFS_SOURCES
cd $LFS_SOURCES

# Package list - LFS 12.0
PACKAGES=(
    # Chapter 5 - Cross Toolchain
    "https://ftp.gnu.org/gnu/binutils/binutils-2.41.tar.xz"
    "https://ftp.gnu.org/gnu/gcc/gcc-13.2.0/gcc-13.2.0.tar.xz"
    "https://www.kernel.org/pub/linux/kernel/v6.x/linux-6.4.12.tar.xz"
    "https://ftp.gnu.org/gnu/glibc/glibc-2.38.tar.xz"
    
    # Chapter 6 - Temporary Tools
    "https://ftp.gnu.org/gnu/m4/m4-1.4.19.tar.xz"
    "https://ftp.gnu.org/gnu/ncurses/ncurses-6.4.tar.xz"
    "https://ftp.gnu.org/gnu/bash/bash-5.2.15.tar.gz"
    "https://ftp.gnu.org/gnu/coreutils/coreutils-9.3.tar.xz"
    "https://ftp.gnu.org/gnu/diffutils/diffutils-3.10.tar.xz"
    "https://astron.com/pub/file/file-5.45.tar.gz"
    "https://ftp.gnu.org/gnu/findutils/findutils-4.9.0.tar.xz"
    "https://ftp.gnu.org/gnu/gawk/gawk-5.2.2.tar.xz"
    "https://ftp.gnu.org/gnu/grep/grep-3.11.tar.xz"
    "https://ftp.gnu.org/gnu/gzip/gzip-1.12.tar.xz"
    "https://ftp.gnu.org/gnu/make/make-4.4.1.tar.gz"
    "https://ftp.gnu.org/gnu/patch/patch-2.7.6.tar.xz"
    "https://ftp.gnu.org/gnu/sed/sed-4.9.tar.xz"
    "https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz"
    "https://tukaani.org/xz/xz-5.4.4.tar.xz"
    
    # Chapter 7 - Additional Temporary Tools
    "https://ftp.gnu.org/gnu/gettext/gettext-0.22.tar.xz"
    "https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.xz"
    "https://www.cpan.org/src/5.0/perl-5.38.0.tar.xz"
    "https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tar.xz"
    "https://ftp.gnu.org/gnu/texinfo/texinfo-7.0.3.tar.xz"
    "https://www.kernel.org/pub/linux/utils/util-linux/v2.39/util-linux-2.39.1.tar.xz"
    
    # Chapter 8 - Basic System Software
    "https://www.linuxfromscratch.org/lfs/view/12.0/man-pages-6.05.01.tar.xz"
    "https://www.linuxfromscratch.org/lfs/view/12.0/iana-etc-20230810.tar.gz"
    "https://zlib.net/zlib-1.2.13.tar.xz"
    "https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz"
    "https://tukaani.org/xz/xz-5.4.4.tar.xz"
    "https://github.com/facebook/zstd/releases/download/v1.5.5/zstd-1.5.5.tar.gz"
    "https://ftp.gnu.org/gnu/readline/readline-8.2.tar.gz"
    "https://ftp.gnu.org/gnu/bc/bc-6.6.0.tar.xz"
    "https://github.com/westes/flex/releases/download/v2.6.4/flex-2.6.4.tar.gz"
    "https://prdownloads.sourceforge.net/tcl/tcl8.6.13-src.tar.gz"
    "https://sourceforge.net/projects/expect/files/Expect/5.45.4/expect5.45.4.tar.gz"
    "https://ftp.gnu.org/gnu/dejagnu/dejagnu-1.6.3.tar.gz"
    "https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz"
    "https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.0.tar.xz"
    "https://ftp.gnu.org/gnu/mpc/mpc-1.3.1.tar.gz"
    "https://download.savannah.gnu.org/releases/attr/attr-2.5.1.tar.gz"
    "https://download.savannah.gnu.org/releases/acl/acl-2.3.1.tar.xz"
    "https://www.kernel.org/pub/linux/libs/security/linux-privs/libcap2/libcap-2.69.tar.gz"
    "https://github.com/besser82/libxcrypt/releases/download/v4.4.36/libxcrypt-4.4.3.tar.xz"
    "https://github.com/shadow-maint/shadow/releases/download/4.13/shadow-4.13.tar.xz"
    "https://ftp.gnu.org/gnu/pkgconf/pkgconf-2.0.1.tar.xz"
    "https://ftp.gnu.org/gnu/psmisc/psmisc-23.6.tar.xz"
    "https://github.com/libtool/libtool/releases/download/2.4.7/libtool-2.4.7.tar.xz"
    "https://ftp.gnu.org/gnu/gdbm/gdbm-1.23.tar.xz"
    "https://ftp.gnu.org/gnu/gperf/gperf-3.1.tar.gz"
    "https://github.com/libexpat/libexpat/releases/download/R_2.5.0/expat-2.5.0.tar.xz"
    "https://ftp.gnu.org/gnu/inetutils/inetutils-2.4.tar.xz"
    "https://ftp.gnu.org/gnu/less/less-643.tar.gz"
    "https://www.cpan.org/src/5.0/perl-5.38.0.tar.xz"
    "https://cpan.metacpan.org/authors/id/P/PM/PMQS/XML-Parser-2.46.tar.gz"
    "https://ftp.gnu.org/gnu/intltool/intltool-0.51.0.tar.gz"
    "https://ftp.gnu.org/gnu/autoconf/autoconf-2.71.tar.xz"
    "https://ftp.gnu.org/gnu/automake/automake-1.16.5.tar.xz"
    "https://github.com/openssl/openssl/releases/download/openssl-3.1.2/openssl-3.1.2.tar.gz"
    "https://github.com/kmod-project/kmod/archive/refs/tags/v30.tar.gz"
    "https://sourceware.org/elfutils/ftp/0.189/elfutils-0.189.tar.bz2"
    "https://github.com/libffi/libffi/releases/download/3.4.4/libffi-3.4.4.tar.gz"
    "https://github.com/mesonbuild/meson/releases/download/1.2.1/meson-1.2.1.tar.gz"
    "https://github.com/ninja-build/ninja/archive/refs/tags/v1.11.1.tar.gz"
    "https://github.com/pallets/markupsafe/releases/download/2.1.3/markupsafe-2.1.3.tar.gz"
    "https://github.com/pallets/jinja/releases/download/3.1.2/Jinja2-3.1.2.tar.gz"
    "https://github.com/util-linux/util-linux/archive/refs/tags/v2.39.1.tar.gz"
    "https://github.com/Pro/ecryptfs/releases/download/v111/ecryptfs-utils-111.tar.gz"
    "https://github.com/tytso/e2fsprogs/releases/download/v1.47.0/e2fsprogs-1.47.0.tar.gz"
    "https://www.kernel.org/pub/linux/utils/net/sysklogd/sysklogd-1.5.1.tar.gz"
    "https://github.com/slicer69/sysvinit/archive/refs/tags/3.07.tar.gz"
    
    # GRUB
    "https://ftp.gnu.org/gnu/grub/grub-2.06.tar.xz"
    
    # Linux Kernel for final system
    "https://www.kernel.org/pub/linux/kernel/v6.x/linux-6.4.12.tar.xz"
)

# Download function with retry
download_package() {
    local url=$1
    local filename=$(basename $url)
    
    if [ -f "$filename" ]; then
        echo "  [SKIP] $filename already exists"
        return 0
    fi
    
    echo "  [DOWNLOAD] $filename"
    wget -q --tries=3 --timeout=30 "$url" -O "$filename"
    
    if [ $? -eq 0 ]; then
        echo "  [OK] $filename downloaded"
        return 0
    else
        echo "  [ERROR] Failed to download $filename"
        return 1
    fi
}

# Download all packages
echo "Downloading packages to $LFS_SOURCES..."
TOTAL=${#PACKAGES[@]}
COUNT=0
FAILED=0

for url in "${PACKAGES[@]}"; do
    COUNT=$((COUNT + 1))
    echo ""
    echo "[$COUNT/$TOTAL] Processing..."
    
    if ! download_package "$url"; then
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "=== Download Complete ==="
echo "Total: $TOTAL packages"
echo "Failed: $FAILED packages"
echo ""
echo "Next step: Run scripts/02-cross-toolchain.sh"
