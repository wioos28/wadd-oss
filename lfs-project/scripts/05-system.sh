#!/bin/bash
# LFS Build Script - Chapter 8: Installing Basic System Software
# This script builds the final system packages

set -e

echo "=== LFS Build - System Packages ==="
echo "Starting at: $(date)"

# Set environment
export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources
export LC_ALL=POSIX

# Create chroot script for Chapter 8
cat > $LFS/chroot-ch8.sh << 'CHROOT_EOF'
#!/bin/bash
set -e

echo "=== Inside Chroot - Chapter 8 ==="

export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources
export LC_ALL=POSIX
export PATH=/usr/bin:/usr/sbin:/bin:/sbin

cd $LFS_SOURCES

# 8.1 Man-pages-6.05.01
echo ""
echo "=== Installing Man-pages ==="
tar xf man-pages-6.05.01.tar.xz
cd man-pages-6.05.01
make install
cd $LFS_SOURCES
rm -rf man-pages-6.05.01

# 8.2 Iana-Etc-20230810
echo ""
echo "=== Installing Iana-Etc ==="
tar xf iana-etc-20230810.tar.gz
cd iana-etc-20230810
cp services protocols /etc
cd $LFS_SOURCES
rm -rf iana-etc-20230810

# 8.3 Glibc-2.38
echo ""
echo "=== Building Glibc-2.38 ==="
tar xf glibc-2.38.tar.xz
cd glibc-2.38
case $(uname -m) in
    i?86)   ln -sfv ld-linux.so.2 /lib/ld-linux.so.2
            ;;
    x86_64) ln -sfv ../lib/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2
            ;;
esac
patch -Np1 -i ../glibc-2.38-fhs-1.patch
mkdir -v build
cd build
echo "scripts_python=\"/usr/bin/python3\"" > ../parms
echo "install_bootstrap_args=\"--prefix=/tools\"" >> ../parms
echo "glibc_cv_cc_cleanup=yes" >> ../parms
../configure --prefix=/usr \
             --libdir=/usr/lib \
             --libexecdir=/usr/lib \
             --enable-kernel=4.14 \
             --enable-stack-protector=strong \
             --enable-multi-arch \
             --enable-bind-now \
             --disable-nls \
             --disable-werror
make
make install
cd $LFS_SOURCES
rm -rf glibc-2.38

# 8.4 Zlib-1.2.13
echo ""
echo "=== Building Zlib-1.2.13 ==="
tar xf zlib-1.2.13.tar.xz
cd zlib-1.2.13
./configure --prefix=/usr --shared
make
make install
cd $LFS_SOURCES
rm -rf zlib-1.2.13

# 8.5 Bzip2-1.0.8
echo ""
echo "=== Building Bzip2-1.0.8 ==="
tar xf bzip2-1.0.8.tar.gz
cd bzip2-1.0.8
patch -Np1 -i ../bzip2-1.0.8-install_docs-1.patch
make -f Makefile-libbz2_so
make clean
make
make PREFIX=/usr install
cd $LFS_SOURCES
rm -rf bzip2-1.0.8

# 8.6 Xz-5.4.4
echo ""
echo "=== Building Xz-5.4.4 ==="
tar xf xz-5.4.4.tar.xz
cd xz-5.4.4
./configure --prefix=/usr \
            --libdir=/usr/lib \
            --disable-static \
            --docdir=/usr/share/doc/xz-5.4.4
make
make install
cd $LFS_SOURCES
rm -rf xz-5.4.4

# 8.7 Zstd-1.5.5
echo ""
echo "=== Building Zstd-1.5.5 ==="
tar xf zstd-1.5.5.tar.gz
cd zstd-1.5.5
make prefix=/usr
make prefix=/usr install
cd $LFS_SOURCES
rm -rf zstd-1.5.5

# 8.8 File-5.45
echo ""
echo "=== Building File-5.45 ==="
tar xf file-5.45.tar.gz
cd file-5.45
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf file-5.45

# 8.9 Readline-8.2
echo ""
echo "=== Building Readline-8.2 ==="
tar xf readline-8.2.tar.gz
cd readline-8.2
patch -Np1 -i ../readline-8.2-upstream_fix-1.patch
./configure --prefix=/usr \
            --libdir=/usr/lib \
            --disable-static \
            --with-curses
make
make install
cd $LFS_SOURCES
rm -rf readline-8.2

# 8.10 M4-1.4.19
echo ""
echo "=== Building M4-1.4.19 ==="
tar xf m4-1.4.19.tar.xz
cd m4-1.4.19
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf m4-1.4.19

# 8.11 Bc-6.6.0
echo ""
echo "=== Building Bc-6.6.0 ==="
tar xf bc-6.6.0.tar.xz
cd bc-6.6.0
./configure --prefix=/usr \
            --with-readline \
            --mandir=/usr/share/man \
            --infodir=/usr/share/info \
            --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf bc-6.6.0

# 8.12 Flex-2.6.4
echo ""
echo "=== Building Flex-2.6.4 ==="
tar xf flex-2.6.4.tar.gz
cd flex-2.6.4
./configure --prefix=/usr \
            --docdir=/usr/share/doc/flex-2.6.4 \
            --disable-static
make
make install
cd $LFS_SOURCES
rm -rf flex-2.6.4

# 8.13 Tcl-8.6.13
echo ""
echo "=== Building Tcl-8.6.13 ==="
tar xf tcl8.6.13-src.tar.gz
cd tcl8.6.13
./configure --prefix=/usr \
            --mandir=/usr/share/man \
            --disable-static
make
make install
cd $LFS_SOURCES
rm -rf tcl8.6.13

# 8.14 Expect-5.45.4
echo ""
echo "=== Building Expect-5.45.4 ==="
tar xf expect5.45.4.tar.gz
cd expect5.45.4
./configure --prefix=/usr \
            --with-tcl=/usr/lib \
            --enable-shared \
            --mandir=/usr/share/man \
            --with-tclinclude=/usr/include
make
make install
cd $LFS_SOURCES
rm -rf expect5.45.4

# 8.15 DejaGNU-1.6.3
echo ""
echo "=== Building DejaGNU-1.6.3 ==="
tar xf dejagnu-1.6.3.tar.gz
cd dejagnu-1.6.3
mkdir build && cd build
../configure --prefix=/usr
makeinfo --html -o doc/dejagnu.html ../doc/dejagnu.texi
makeinfo --plaintext -o doc/dejagnu.txt ../doc/dejagnu.texi
make install
install -v -dm755 /usr/share/doc/dejagnu-1.6.3
install -v -m644 doc/dejagnu.{html,txt} /usr/share/doc/dejagnu-1.6.3
cd $LFS_SOURCES
rm -rf dejagnu-1.6.3

# 8.16 Binutils-2.41
echo ""
echo "=== Building Binutils-2.41 ==="
tar xf binutils-2.41.tar.xz
cd binutils-2.41
mkdir -v build
cd build
../configure --prefix=/usr \
             --libdir=/usr/lib \
             --enable-gprofng=no \
             --disable-werror \
             --enable-64-bit-bfd \
             --enable-default-hash-style=gnu
make tooldir=/usr
make tooldir=/usr install
cd $LFS_SOURCES
rm -rf binutils-2.41

# 8.17 GMP-6.3.0
echo ""
echo "=== Building GMP-6.3.0 ==="
tar xf gmp-6.3.0.tar.xz
cd gmp-6.3.0
./configure --prefix=/usr \
            --docdir=/usr/share/doc/gmp-6.3.0 \
            --disable-static \
            --disable-cxx
make
make install
cd $LFS_SOURCES
rm -rf gmp-6.3.0

# 8.18 MPFR-4.2.0
echo ""
echo "=== Building MPFR-4.2.0 ==="
tar xf mpfr-4.2.0.tar.xz
cd mpfr-4.2.0
./configure --prefix=/usr \
            --docdir=/usr/share/doc/mpfr-4.2.0 \
            --disable-static \
            --with-gmp
make
make install
cd $LFS_SOURCES
rm -rf mpfr-4.2.0

# 8.19 MPC-1.3.1
echo ""
echo "=== Building MPC-1.3.1 ==="
tar xf mpc-1.3.1.tar.gz
cd mpc-1.3.1
./configure --prefix=/usr \
            --docdir=/usr/share/doc/mpc-1.3.1 \
            --disable-static \
            --with-gmp \
            --with-mpfr
make
make install
cd $LFS_SOURCES
rm -rf mpc-1.3.1

# 8.20 Attr-2.5.1
echo ""
echo "=== Building Attr-2.5.1 ==="
tar xf attr-2.5.1.tar.gz
cd attr-2.5.1
./configure --prefix=/usr \
            --disable-static \
            --docdir=/usr/share/doc/attr-2.5.1
make
make install
cd $LFS_SOURCES
rm -rf attr-2.5.1

# 8.21 Acl-2.3.1
echo ""
echo "=== Building Acl-2.3.1 ==="
tar xf acl-2.3.1.tar.xz
cd acl-2.3.1
./configure --prefix=/usr \
            --disable-static \
            --docdir=/usr/share/doc/acl-2.3.1
make
make install
cd $LFS_SOURCES
rm -rf acl-2.3.1

# 8.22 Libcap-2.69
echo ""
echo "=== Building Libcap-2.69 ==="
tar xf libcap-2.69.tar.gz
cd libcap-2.69
sed -i 's/-lequal//g' libcap/Makefile
make prefix=/usr lib=lib
make prefix=/usr lib=lib install
cd $LFS_SOURCES
rm -rf libcap-2.69

# 8.23 Libxcrypt-4.4.36
echo ""
echo "=== Building Libxcrypt-4.4.36 ==="
tar xf libxcrypt-4.4.3.tar.xz
cd libxcrypt-4.4.3
./configure --prefix=/usr \
            --enable-hashes=strong,s겢 \
            --disable-static \
            --disable-werror \
            --libdir=/usr/lib \
            --enable-valia \
            --docdir=/usr/share/doc/libxcrypt-4.4.3
make
make install
cd $LFS_SOURCES
rm -rf libxcrypt-4.4.3

# 8.24 Shadow-4.13
echo ""
echo "=== Building Shadow-4.13 ==="
tar xf shadow-4.13.tar.xz
cd shadow-4.13
sed -i 's/1000/999/' etc/login.defs
./configure --prefix=/usr \
            --bindir=/bin \
            --with-no-chown \
            --with-libpam \
            --disable-static \
            --libdir=/usr/lib
make
make install
cd $LFS_SOURCES
rm -rf shadow-4.13

# 8.25 GCC-13.2.0
echo ""
echo "=== Building GCC-13.2.0 ==="
tar xf gcc-13.2.0.tar.xz
cd gcc-13.2.0
mkdir -v build
cd build
../configure --prefix=/usr \
             --libdir=/usr/lib \
             --enable-languages=c,c++ \
             --disable-multilib \
             --disable-bootstrap \
             --with-system-zlib \
             --enable-initfini-array \
             --enable-threads=posix \
             --enable-__cxa_atexit \
             --enable-libstdcxx-threads \
             --enable-libstdcxx-time \
             --enable-shared \
             --enable-default-pie \
             --enable-default-ssp \
             --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf gcc-13.2.0

# 8.26 Pkgconf-2.0.1
echo ""
echo "=== Building Pkgconf-2.0.1 ==="
tar xf pkgconf-2.0.1.tar.xz
cd pkgconf-2.0.1
./configure --prefix=/usr \
            --disable-static \
            --docdir=/usr/share/doc/pkgconf-2.0.1
make
make install
cd $LFS_SOURCES
rm -rf pkgconf-2.0.1

# 8.27 Ncurses-6.4
echo ""
echo "=== Building Ncurses-6.4 ==="
tar xf ncurses-6.4.tar.xz
cd ncurses-6.4
./configure --prefix=/usr \
            --with-shared \
            --with-normal \
            --with-cxx-binding \
            --with-pkg-config-libdir=/usr/lib/pkgconfig
make
make install
cd $LFS_SOURCES
rm -rf ncurses-6.4

# 8.28 Sed-4.9
echo ""
echo "=== Building Sed-4.9 ==="
tar xf sed-4.9.tar.xz
cd sed-4.9
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf sed-4.9

# 8.29 Psmisc-23.6
echo ""
echo "=== Building Psmisc-23.6 ==="
tar xf psmisc-23.6.tar.xz
cd psmisc-23.6
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf psmisc-23.6

# 8.30 Gettext-0.22
echo ""
echo "=== Building Gettext-0.22 ==="
tar xf gettext-0.22.tar.xz
cd gettext-0.22
./configure --prefix=/usr \
            --disable-static \
            --docdir=/usr/share/doc/gettext-0.22
make
make install
cd $LFS_SOURCES
rm -rf gettext-0.22

# 8.31 Bison-3.8.2
echo ""
echo "=== Building Bison-3.8.2 ==="
tar xf bison-3.8.2.tar.xz
cd bison-3.8.2
./configure --prefix=/usr \
            --docdir=/usr/share/doc/bison-3.8.2
make
make install
cd $LFS_SOURCES
rm -rf bison-3.8.2

# 8.32 Grep-3.11
echo ""
echo "=== Building Grep-3.11 ==="
tar xf grep-3.11.tar.xz
cd grep-3.11
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf grep-3.11

# 8.33 Bash-5.2.15
echo ""
echo "=== Building Bash-5.2.15 ==="
tar xf bash-5.2.15.tar.gz
cd bash-5.2.15
./configure --prefix=/usr \
            --docdir=/usr/share/doc/bash-5.2.15 \
            --without-bash-malloc \
            --with-curses
make
make install
cd $LFS_SOURCES
rm -rf bash-5.2.15

# 8.34 Libtool-2.4.7
echo ""
echo "=== Building Libtool-2.4.7 ==="
tar xf libtool-2.4.7.tar.xz
cd libtool-2.4.7
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf libtool-2.4.7

# 8.35 GDBM-1.23
echo ""
echo "=== Building GDBM-1.23 ==="
tar xf gdbm-1.23.tar.xz
cd gdbm-1.23
./configure --prefix=/usr \
            --disable-static \
            --enable-libgdbm-compat
make
make install
cd $LFS_SOURCES
rm -rf gdbm-1.23

# 8.36 GPerf-3.1
echo ""
echo "=== Building GPerf-3.1 ==="
tar xf gperf-3.1.tar.gz
cd gperf-3.1
./configure --prefix=/usr \
            --docdir=/usr/share/doc/gperf-3.1
make
make install
cd $LFS_SOURCES
rm -rf gperf-3.1

# 8.37 Expat-2.5.0
echo ""
echo "=== Building Expat-2.5.0 ==="
tar xf expat-2.5.0.tar.xz
cd expat-2.5.0
./configure --prefix=/usr \
            --disable-static \
            --docdir=/usr/share/doc/expat-2.5.0
make
make install
cd $LFS_SOURCES
rm -rf expat-2.5.0

# 8.38 Inetutils-2.4
echo ""
echo "=== Building Inetutils-2.4 ==="
tar xf inetutils-2.4.tar.xz
cd inetutils-2.4
./configure --prefix=/usr \
            --localstatedir=/var \
            --disable-logger \
            --disable-syslogd \
            --disable-whois \
            --disable-sbin
make
make install
cd $LFS_SOURCES
rm -rf inetutils-2.4

# 8.39 Less-643
echo ""
echo "=== Building Less-643 ==="
tar xf less-643.tar.gz
cd less-643
./configure --prefix=/usr --sysconfdir=/etc
make
make install
cd $LFS_SOURCES
rm -rf less-643

# 8.40 Perl-5.38.0
echo ""
echo "=== Building Perl-5.38.0 ==="
tar xf perl-5.38.0.tar.xz
cd perl-5.38.0
sh Configure -des \
             -Dprefix=/usr \
             -Dvendorprefix=/usr \
             -Dman1dir=/usr/share/man/man1 \
             -Dman3dir=/usr/share/man/man3 \
             -Dpager="/usr/bin/less -isR" \
             -Duseshrplib \
             -Duseithreads
make
make install
cd $LFS_SOURCES
rm -rf perl-5.38.0

# 8.41 XML::Parser-2.46
echo ""
echo "=== Building XML::Parser-2.46 ==="
tar xf XML-Parser-2.46.tar.gz
cd XML-Parser-2.46
perl Makefile.PL
make
make test
make install
cd $LFS_SOURCES
rm -rf XML-Parser-2.46

# 8.42 Intltool-0.51.0
echo ""
echo "=== Building Intltool-0.51.0 ==="
tar xf intltool-0.51.0.tar.gz
cd intltool-0.51.0
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf intltool-0.51.0

# 8.43 Autoconf-2.71
echo ""
echo "=== Building Autoconf-2.71 ==="
tar xf autoconf-2.71.tar.xz
cd autoconf-2.71
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf autoconf-2.71

# 8.44 Automake-1.16.5
echo ""
echo "=== Building Automake-1.16.5 ==="
tar xf automake-1.16.5.tar.xz
cd automake-1.16.5
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf automake-1.16.5

# 8.45 OpenSSL-3.1.2
echo ""
echo "=== Building OpenSSL-3.1.2 ==="
tar xf openssl-3.1.2.tar.gz
cd openssl-3.1.2
./config --prefix=/usr \
         --openssldir=/etc/ssl \
         --libdir=lib \
         shared \
         zlib-dynamic
make
make test
make install
cd $LFS_SOURCES
rm -rf openssl-3.1.2

# 8.46 Kmod-30
echo ""
echo "=== Building Kmod-30 ==="
tar xf kmod-30.tar.gz
cd kmod-30
./configure --prefix=/usr \
            --bindir=/bin \
            --libdir=/usr/lib \
            --sysconfdir=/etc \
            --disable-man \
            --disable-python \
            --disable-static
make
make install
cd $LFS_SOURCES
rm -rf kmod-30

# 8.47 Libelf from Elfutils-0.189
echo ""
echo "=== Building Libelf-0.189 ==="
tar xf elfutils-0.189.tar.bz2
cd elfutils-0.189
./configure --prefix=/usr \
            --disable-debuginfod \
            --enable-libdebuginfod=dummy
make
make -C libelf install
cd $LFS_SOURCES
rm -rf elfutils-0.189

# 8.48 Libffi-3.4.4
echo ""
echo "=== Building Libffi-3.4.4 ==="
tar xf libffi-3.4.4.tar.gz
cd libffi-3.4.4
./configure --prefix=/usr \
            --disable-static \
            --with-gcc-arch=native
make
make install
cd $LFS_SOURCES
rm -rf libffi-3.4.4

# 8.49 Python-3.11.4
echo ""
echo "=== Building Python-3.11.4 ==="
tar xf Python-3.11.4.tar.xz
cd Python-3.11.4
./configure --prefix=/usr \
            --enable-shared \
            --with-system-expat \
            --with-ensurepip=install \
            --with-system-ffi
make
make install
cd $LFS_SOURCES
rm -rf Python-3.11.4

# 8.50 Flit-Core-3.9.0
echo ""
echo "=== Building Flit-Core-3.9.0 ==="
tar xf flit-core-3.9.0.tar.gz
cd flit-core-3.9.0
pip3 install --no-build-isolation -e .
cd $LFS_SOURCES
rm -rf flit-core-3.9.0

# 8.51 Wheel-0.41.1
echo ""
echo "=== Building Wheel-0.41.1 ==="
tar xf wheel-0.41.1.tar.gz
cd wheel-0.41.1
pip3 install --no-build-isolation -e .
cd $LFS_SOURCES
rm -rf wheel-0.41.1

# 8.52 Ninja-1.11.1
echo ""
echo "=== Building Ninja-1.11.1 ==="
tar xf ninja-1.11.1.tar.gz
cd ninja-1.11.1
./configure.py --bootstrap
./ninja ninja_test
./ninja_test --gtest_filter='*concurrent*'
install -vm755 ninja /usr/bin
cd $LFS_SOURCES
rm -rf ninja-1.11.1

# 8.53 Meson-1.2.1
echo ""
echo "=== Building Meson-1.2.1 ==="
tar xf meson-1.2.1.tar.gz
cd meson-1.2.1
pip3 install --no-build-isolation -e .
cd $LFS_SOURCES
rm -rf meson-1.2.1

# 8.54 Coreutils-9.3
echo ""
echo "=== Building Coreutils-9.3 ==="
tar xf coreutils-9.3.tar.xz
cd coreutils-9.3
./configure --prefix=/usr \
            --enable-install-program=hostname \
            --enable-no-install-program=kill,uptime \
            --disable-nls
make
make install
cd $LFS_SOURCES
rm -rf coreutils-9.3

# 8.55 Check-0.15.2
echo ""
echo "=== Building Check-0.15.2 ==="
tar xf check-0.15.2.tar.gz
cd check-0.15.2
./configure --prefix=/usr --disable-static
make
make install
cd $LFS_SOURCES
rm -rf check-0.15.2

# 8.56 Diffutils-3.10
echo ""
echo "=== Building Diffutils-3.10 ==="
tar xf diffutils-3.10.tar.xz
cd diffutils-3.10
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf diffutils-3.10

# 8.57 Gawk-5.2.2
echo ""
echo "=== Building Gawk-5.2.2 ==="
tar xf gawk-5.2.2.tar.xz
cd gawk-5.2.2
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf gawk-5.2.2

# 8.58 Findutils-4.9.0
echo ""
echo "=== Building Findutils-4.9.0 ==="
tar xf findutils-4.9.0.tar.xz
cd findutils-4.9.0
./configure --prefix=/usr \
            --localstatedir=/var \
            --disable-makeinstall-chown
make
make install
cd $LFS_SOURCES
rm -rf findutils-4.9.0

# 8.59 Groff-1.23.0
echo ""
echo "=== Building Groff-1.23.0 ==="
tar xf groff-1.23.0.tar.xz
cd groff-1.23.0
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf groff-1.23.0

# 8.60 GRUB-2.06
echo ""
echo "=== Building GRUB-2.06 ==="
tar xf grub-2.06.tar.xz
cd grub-2.06
./configure --prefix=/usr \
            --sysconfdir=/etc \
            --disable-werror
make
make install
make install
cd $LFS_SOURCES
rm -rf grub-2.06

# 8.61 Gzip-1.12
echo ""
echo "=== Building Gzip-1.12 ==="
tar xf gzip-1.12.tar.xz
cd gzip-1.12
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf gzip-1.12

# 8.62 IPRoute2-6.4.0
echo ""
echo "=== Building IPRoute2-6.4.0 ==="
tar xf iproute2-6.4.0.tar.xz
cd iproute2-6.4.0
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf iproute2-6.4.0

# 8.63 Kbd-2.6.1
echo ""
echo "=== Building Kbd-2.6.1 ==="
tar xf kbd-2.6.1.tar.xz
cd kbd-2.6.1
./configure --prefix=/usr \
            --disable-vlock
make
make install
cd $LFS_SOURCES
rm -rf kbd-2.6.1

# 8.64 Libpipeline-1.5.7
echo ""
echo "=== Building Libpipeline-1.5.7 ==="
tar xf libpipeline-1.5.7.tar.gz
cd libpipeline-1.5.7
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf libpipeline-1.5.7

# 8.65 Make-4.4.1
echo ""
echo "=== Building Make-4.4.1 ==="
tar xf make-4.4.1.tar.gz
cd make-4.4.1
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf make-4.4.1

# 8.66 Patch-2.7.6
echo ""
echo "=== Building Patch-2.7.6 ==="
tar xf patch-2.7.6.tar.xz
cd patch-2.7.6
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf patch-2.7.6

# 8.67 Tar-1.35
echo ""
echo "=== Building Tar-1.35 ==="
tar xf tar-1.35.tar.xz
cd tar-1.35
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf tar-1.35

# 8.68 Texinfo-7.0.3
echo ""
echo "=== Building Texinfo-7.0.3 ==="
tar xf texinfo-7.0.3.tar.xz
cd texinfo-7.0.3
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf texinfo-7.0.3

# 8.69 Vim-9.0.1677
echo ""
echo "=== Building Vim-9.0.1677 ==="
tar xf vim-9.0.1677.tar.gz
cd vim-9.0.1677
echo '#define SYS_VIMRC_FILE "/etc/vimrc"' >> src/feature.h
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf vim-9.0.1677

# 8.70 MarkupSafe-2.1.3
echo ""
echo "=== Building MarkupSafe-2.1.3 ==="
tar xf markupsafe-2.1.3.tar.gz
cd markupsafe-2.1.3
pip3 install --no-build-isolation -e .
cd $LFS_SOURCES
rm -rf markupsafe-2.1.3

# 8.71 Jinja2-3.1.2
echo ""
echo "=== Building Jinja2-3.1.2 ==="
tar xf Jinja2-3.1.2.tar.gz
cd Jinja2-3.1.2
pip3 install --no-build-isolation -e .
cd $LFS_SOURCES
rm -rf Jinja2-3.1.2

# 8.72 Udev from Systemd-254
echo ""
echo "=== Building Udev-254 ==="
tar xf systemd-254.tar.xz
cd systemd-254
ln -sf /bin/true /usr/bin/chfn
ln -sf /bin/true /usr/bin/chsh
ln -sf /bin/true /usr/bin/groupadd
ln -sf /bin/true /usr/bin/groupdel
ln -sf /bin/true /usr/bin/groupmod
ln -sf /bin/true /usr/bin/useradd
ln -sf /bin/true /usr/bin/userdel
ln -sf /bin/true /usr/bin/usermod
./configure --prefix=/usr \
            --sysconfdir=/etc \
            --localstatedir=/var \
            -Dblkid=true \
            -Dmount=true \
            -Dudev=true \
            -Dudev-dir=/lib/udev \
            -Dmode=developer
ninja
ninja install
cd $LFS_SOURCES
rm -rf systemd-254

# 8.73 Man-DB-2.11.2
echo ""
echo "=== Building Man-DB-2.11.2 ==="
tar xf man-db-2.11.2.tar.xz
cd man-db-2.11.2
./configure --prefix=/usr \
            --docdir=/usr/share/doc/man-db-2.11.2 \
            --sysconfdir=/etc \
            --disable-setuid
make
make install
cd $LFS_SOURCES
rm -rf man-db-2.11.2

# 8.74 Procps-ng-4.0.3
echo ""
echo "=== Building Procps-ng-4.0.3 ==="
tar xf procps-ng-4.0.3.tar.xz
cd procps-ng-4.0.3
./configure --prefix=/usr \
            --disable-static \
            --disable-kill \
            --with-systemd
make
make install
cd $LFS_SOURCES
rm -rf procps-ng-4.0.3

# 8.75 Util-linux-2.39.1
echo ""
echo "=== Building Util-linux-2.39.1 ==="
tar xf util-linux-2.39.1.tar.xz
cd util-linux-2.39.1
mkdir -p /var/lib/hwclock
./configure ADJTIME_PATH=/var/lib/hwclock/adjtime \
            --docdir=/usr/share/doc/util-linux-2.39.1 \
            --disable-chfn-chsh \
            --disable-login \
            --disable-nologin \
            --disable-su \
            --disable-setpriv \
            --disable-runuser \
            --disable-pylibmount \
            --disable-static \
            --without-python
make
make install
cd $LFS_SOURCES
rm -rf util-linux-2.39.1

# 8.76 E2fsprogs-1.47.0
echo ""
echo "=== Building E2fsprogs-1.47.0 ==="
tar xf e2fsprogs-1.47.0.tar.gz
cd e2fsprogs-1.47.0
mkdir -v build
cd build
../configure --prefix=/usr \
             --bindir=/bin \
             --with-root-prefix="" \
             --enable-libblkid \
             --enable-libuuid \
             --enable-libsmartcols \
             --enable-libttyutils \
             --disable-libprofile \
             --disable-static \
             --disable-fsck
make
make install
cd $LFS_SOURCES
rm -rf e2fsprogs-1.47.0

# 8.77 Sysklogd-1.5.1
echo ""
echo "=== Building Sysklogd-1.5.1 ==="
tar xf sysklogd-1.5.1.tar.gz
cd sysklogd-1.5.1
make
make install
cd $LFS_SOURCES
rm -rf sysklogd-1.5.1

# 8.78 Sysvinit-3.07
echo ""
echo "=== Building Sysvinit-3.07 ==="
tar xf sysvinit-3.07.tar.gz
cd sysvinit-3.07
make
make install
cd $LFS_SOURCES
rm -rf sysvinit-3.07

# 8.79 Linux Kernel
echo ""
echo "=== Building Linux Kernel ==="
tar xf linux-6.4.12.tar.xz
cd linux-6.4.12
make mrproper
make menuconfig
make
make modules_install
cp arch/x86/boot/bzImage /boot/vmlinuz-6.4.12-lfs
cp System.map /boot/System.map-6.4.12
cp .config /boot/config-6.4.12
cd $LFS_SOURCES
rm -rf linux-6.4.12

# 8.80 Stripping
echo ""
echo "=== Stripping ==="
save_lib="ld-2.38.so libc-2.38.so libpthread-2.38.so libthread_db-2.38.so libncursesw.so.6.4 libgcc_s.so.1 libstdc++.so.6.11.4"
for LIB in $save_lib; do
    cp -v /lib/$LIB /lib/$LIB.orig
done
strip --strip-unneeded /lib/*
strip --strip-unneeded /usr/lib/*
strip --strip-unneeded /usr/libexec/*

# Cleanup
rm -rf /usr/share/{info,man,doc}/*
find /usr/{lib,libexec} -name \*.la -delete

echo ""
echo "=== System Packages Complete ==="
echo "Next step: Run scripts/06-config.sh"
CHROOT_EOF
chmod +x $LFS/chroot-ch8.sh

echo ""
echo "=== Chapter 8 Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Enter chroot: sudo $LFS/entreroot.sh"
echo "2. Inside chroot, run: /mnt/lfs/chroot-ch8.sh"
echo "3. Exit chroot: exit"
echo "4. Continue with: scripts/06-config.sh"
