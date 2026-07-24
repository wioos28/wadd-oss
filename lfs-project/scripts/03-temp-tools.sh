#!/bin/bash
# LFS Build Script - Chapter 6: Cross Compiling Temporary Tools
# This script builds temporary tools using the cross-toolchain

set -e

echo "=== LFS Build - Temporary Tools ==="
echo "Starting at: $(date)"

# Set environment
export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources
export LFS_TGT=$(uname -m)-lfs-linux-gnu
export PATH=$LFS/tools/bin:$PATH
export LC_ALL=POSIX

cd $LFS_SOURCES

# Function to build a package
build_package() {
    local package=$1
    local extract_dir=$2
    local configure_args=$3
    
    echo ""
    echo "=== Building $package ==="
    
    # Extract
    echo "[EXTRACT] Extracting $package..."
    tar xf $package
    cd $extract_dir
    
    # Configure
    echo "[CONFIGURE] Configuring..."
    if [ -n "$configure_args" ]; then
        ./configure $configure_args
    fi
    
    # Build
    echo "[BUILD] Compiling..."
    make
    
    # Install
    echo "[INSTALL] Installing..."
    make install
    
    # Clean up
    cd $LFS_SOURCES
    rm -rf $extract_dir
    
    echo "[OK] $package installed"
}

# Common configure args for cross-compilation
CROSS_CONFIG="--prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls --disable-werror"

# 6.1 M4
echo ""
echo "=========================================="
echo "6.1 M4-1.4.19"
echo "=========================================="
cd $LFS_SOURCES
tar xf m4-1.4.19.tar.xz
cd m4-1.4.19
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls --disable-werror
make
make install
cd $LFS_SOURCES
rm -rf m4-1.4.19

# 6.2 Ncurses
echo ""
echo "=========================================="
echo "6.2 Ncurses-6.4"
echo "=========================================="
cd $LFS_SOURCES
tar xf ncurses-6.4.tar.xz
cd ncurses-6.4
./configure --prefix=/tools \
            --host=$LFS_TGT \
            --build=$(../scripts/config.guess) \
            --with-shared \
            --with-normal \
            --without-debug \
            --without-cxx-binding \
            --with-fpkgconfig-libdir=/tools/lib/pkgconfig
make
make install
cd $LFS_SOURCES
rm -rf ncurses-6.4

# 6.3 Bash
echo ""
echo "=========================================="
echo "6.3 Bash-5.2.15"
echo "=========================================="
cd $LFS_SOURCES
tar xf bash-5.2.15.tar.gz
cd bash-5.2.15
./configure --prefix=/tools \
            --host=$LFS_TGT \
            --build=$(../scripts/config.guess) \
            --without-bash-malloc \
            --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf bash-5.2.15

# 6.4 Coreutils
echo ""
echo "=========================================="
echo "6.4 Coreutils-9.3"
echo "=========================================="
cd $LFS_SOURCES
tar xf coreutils-9.3.tar.xz
cd coreutils-9.3
./configure --prefix=/tools \
            --host=$LFS_TGT \
            --build=$(../scripts/config.guess) \
            --enable-install-program=hostname \
            --enable-no-install-program=kill,uptime \
            --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf coreutils-9.3

# 6.5 Diffutils
echo ""
echo "=========================================="
echo "6.5 Diffutils-3.10"
echo "=========================================="
cd $LFS_SOURCES
tar xf diffutils-3.10.tar.xz
cd diffutils-3.10
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf diffutils-3.10

# 6.6 File
echo ""
echo "=========================================="
echo "6.6 File-5.45"
echo "=========================================="
cd $LFS_SOURCES
tar xf file-5.45.tar.gz
cd file-5.45
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf file-5.45

# 6.7 Findutils
echo ""
echo "=========================================="
echo "6.7 Findutils-4.9.0"
echo "=========================================="
cd $LFS_SOURCES
tar xf findutils-4.9.0.tar.xz
cd findutils-4.9.0
./configure --prefix=/tools \
            --host=$LFS_TGT \
            --build=$(../scripts/config.guess) \
            --disable-nls \
            --disable-man \
            --without-inject-locate-regex
make
make install
cd $LFS_SOURCES
rm -rf findutils-4.9.0

# 6.8 Gawk
echo ""
echo "=========================================="
echo "6.8 Gawk-5.2.2"
echo "=========================================="
cd $LFS_SOURCES
tar xf gawk-5.2.2.tar.xz
cd gawk-5.2.2
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf gawk-5.2.2

# 6.9 Grep
echo ""
echo "=========================================="
echo "6.9 Grep-3.11"
echo "=========================================="
cd $LFS_SOURCES
tar xf grep-3.11.tar.xz
cd grep-3.11
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf grep-3.11

# 6.10 Gzip
echo ""
echo "=========================================="
echo "6.10 Gzip-1.12"
echo "=========================================="
cd $LFS_SOURCES
tar xf gzip-1.12.tar.xz
cd gzip-1.12
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf gzip-1.12

# 6.11 Make
echo ""
echo "=========================================="
echo "6.11 Make-4.4.1"
echo "=========================================="
cd $LFS_SOURCES
tar xf make-4.4.1.tar.gz
cd make-4.4.1
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf make-4.4.1

# 6.12 Patch
echo ""
echo "=========================================="
echo "6.12 Patch-2.7.6"
echo "=========================================="
cd $LFS_SOURCES
tar xf patch-2.7.6.tar.xz
cd patch-2.7.6
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf patch-2.7.6

# 6.13 Sed
echo ""
echo "=========================================="
echo "6.13 Sed-4.9"
echo "=========================================="
cd $LFS_SOURCES
tar xf sed-4.9.tar.xz
cd sed-4.9
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf sed-4.9

# 6.14 Tar
echo ""
echo "=========================================="
echo "6.14 Tar-1.35"
echo "=========================================="
cd $LFS_SOURCES
tar xf tar-1.35.tar.xz
cd tar-1.35
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf tar-1.35

# 6.15 Xz
echo ""
echo "=========================================="
echo "6.15 Xz-5.4.4"
echo "=========================================="
cd $LFS_SOURCES
tar xf xz-5.4.4.tar.xz
cd xz-5.4.4
./configure --prefix=/tools --host=$LFS_TGT --build=$(../scripts/config.guess) --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf xz-5.4.4

# 6.16 Binutils - Pass 2
echo ""
echo "=========================================="
echo "6.16 Binutils-2.41 - Pass 2"
echo "=========================================="
cd $LFS_SOURCES
tar xf binutils-2.41.tar.xz
cd binutils-2.41
mkdir -v build
cd build
../configure --prefix=/tools \
             --build=$(../scripts/config.guess) \
             --host=$LFS_TGT \
             --disable-nls \
             --enable-gprofng=no \
             --disable-werror \
             --enable-default-hash-style=gnu
make
make install
cd $LFS_SOURCES
rm -rf binutils-2.41

# 6.17 GCC - Pass 2
echo ""
echo "=========================================="
echo "6.17 GCC-13.2.0 - Pass 2"
echo "=========================================="
cd $LFS_SOURCES
tar xf gcc-13.2.0.tar.xz
cd gcc-13.2.0
mkdir -v build
cd build
cat > ../gcc/limitx.h << "EOF"
#include "limits.h"
#include <syslimits.h>
EOF

../configure --target=$LFS_TGT \
             --prefix=/tools \
             --build=$(../scripts/config.guess) \
             --with-glibc-version=2.38 \
             --with-sysroot=$LFS \
             --with-newlib \
             --without-headers \
             --enable-default-pie \
             --enable-default-ssp \
             --disable-nls \
             --disable-shared \
             --disable-threads \
             --disable-multilib \
             --disable-objc \
             --disable-libatomic \
             --disable-libgomp \
             --disable-libquadmath \
             --disable-libssp \
             --disable-libvtv \
             --enable-languages=c,c++
make
make install
cd $LFS_SOURCES
rm -rf gcc-13.2.0

echo ""
echo "=== Temporary Tools Complete ==="
echo "Next step: Run scripts/04-chroot-tools.sh"
