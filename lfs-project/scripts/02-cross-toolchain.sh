#!/bin/bash
# LFS Build Script - Chapter 5: Compiling a Cross-Toolchain
# This script builds the cross-compilation toolchain

set -e

echo "=== LFS Build - Cross-Toolchain ==="
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

# 5.1 Binutils - Pass 1
echo ""
echo "=========================================="
echo "5.1 Binutils-2.41 - Pass 1"
echo "=========================================="
cd $LFS_SOURCES
tar xf binutils-2.41.tar.xz
cd binutils-2.41
mkdir -v build
cd build
../configure --prefix=$LFS/tools \
             --with-sysroot=$LFS \
             --target=$LFS_TGT \
             --disable-nls \
             --enable-gprofng=no \
             --disable-werror \
             --enable-default-hash-style=gnu
make
make install
cd $LFS_SOURCES
rm -rf binutils-2.41

# 5.2 GCC - Pass 1
echo ""
echo "=========================================="
echo "5.2 GCC-13.2.0 - Pass 1"
echo "=========================================="
cd $LFS_SOURCES
tar xf gcc-13.2.0.tar.xz
cd gcc-13.2.0

# Download prerequisites
./contrib/download_prerequisites

mkdir -v build
cd build
../configure --target=$LFS_TGT \
             --prefix=$LFS/tools \
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
             --with-system-zlib \
             --enable-languages=c,c++
make
make install
cd $LFS_SOURCES
rm -rf gcc-13.2.0

# 5.3 Linux API Headers
echo ""
echo "=========================================="
echo "5.3 Linux-6.4.12 API Headers"
echo "=========================================="
cd $LFS_SOURCES
tar xf linux-6.4.12.tar.xz
cd linux-6.4.12
make headers
find -type f -name "*.h" -exec install -v {} $LFS/tools/include \;
cd $LFS_SOURCES
rm -rf linux-6.4.12

# 5.4 Glibc
echo ""
echo "=========================================="
echo "5.4 Glibc-2.38"
echo "=========================================="
cd $LFS_SOURCES
tar xf glibc-2.38.tar.xz
cd glibc-2.38

# Create symlink for ld-linux.so
case $(uname -m) in
    i?86)   ln -sfv ld-linux.so.2 $LFS/tools/lib/ld-linux.so.2
            ;;
    x86_64) ln -sfv ../lib/ld-linux-x86-64.so.2 $LFS/tools/lib64/ld-linux-x86-64.so.2
            ;;
esac

patch -Np1 -i ../glibc-2.38-fhs-1.patch

mkdir -v build
cd build
echo "scripts_python=\"/usr/bin/python3\"" > ../ parms
echo "install_bootstrap_args=\"--prefix=/tools\"" >> ../ parms
echo "glibc_cv_cc_cleanup=yes" >> ../ parms

../configure --prefix=/tools \
             --host=$LFS_TGT \
             --build=$(../scripts/config.guess) \
             --enable-kernel=4.14 \
             --with-headers=$LFS/tools/include \
             --disable-nls \
             --disable-werror \
             --without-selinux \
             --without-gd \
             --enable-stack-protector=strong \
             libc_cv_slibdir=/tools/lib

make
make install
cd $LFS_SOURCES
rm -rf glibc-2.38

# 5.5 Libstdc++ from GCC
echo ""
echo "=========================================="
echo "5.5 Libstdc++ from GCC-13.2.0"
echo "=========================================="
cd $LFS_SOURCES
tar xf gcc-13.2.0.tar.xz
cd gcc-13.2.0
mkdir -v build
cd build
../libstdc++-v3/configure \
    --host=$LFS_TGT \
    --prefix=/tools \
    --disable-multilib \
    --disable-shared \
    --disable-nls \
    --disable-libstdc++-v3 \
    --disable-libssp \
    --enable-libstdcxx-static
make
make install
cd $LFS_SOURCES
rm -rf gcc-13.2.0

echo ""
echo "=== Cross-Toolchain Complete ==="
echo "Next step: Run scripts/03-temp-tools.sh"
