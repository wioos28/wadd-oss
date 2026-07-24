#!/bin/bash
# LFS Build Script - Chapter 7: Entering Chroot and Building Additional Temporary Tools
# This script builds tools inside the chroot environment

set -e

echo "=== LFS Build - Chroot Tools ==="
echo "Starting at: $(date)"

# Set environment
export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources
export LC_ALL=POSIX

# 7.1 Changing Ownership
echo ""
echo "=========================================="
echo "7.1 Changing Ownership"
echo "=========================================="
sudo chown -v root:root $LFS/{usr,var,etc,bin,sbin,lib}
sudo case $(uname -m) in
    x86_64) sudo chown -v root:root $LFS/tools ;;
esac

# 7.2 Creating Directories
echo ""
echo "=========================================="
echo "7.2 Creating Directories"
echo "=========================================="
sudo mkdir -pv $LFS/{dev,proc,sys,run}

# 7.3 Mounting Virtual Kernel File Systems
echo ""
echo "=========================================="
echo "7.3 Mounting Virtual Kernel File Systems"
echo "=========================================="
sudo mount -v --bind /dev $LFS/dev
sudo mount -v --bind /dev/pts $LFS/dev/pts
sudo mount -vt proc proc $LFS/proc
sudo mount -vt sysfs sysfs $LFS/sys
sudo mount -vt tmpfs tmpfs $LFS/run

# 7.4 Entering the Chroot Environment
echo ""
echo "=========================================="
echo "7.4 Entering Chroot Environment"
echo "=========================================="

# Create mount script
cat > $LFS/entreroot.sh << 'EOF'
#!/bin/bash
chroot "$LFS" /tools/bin/env -i \
    HOME=/root \
    TERM="$TERM" \
    PATH=/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin \
    LOGNAME=root \
    /tools/bin/bash --login +h
EOF
chmod +x $LFS/entreroot.sh

echo ""
echo "To enter chroot, run: sudo $LFS/entreroot.sh"
echo ""

# Create chroot build script
cat > $LFS/chroot-build.sh << 'CHROOT_EOF'
#!/bin/bash
# Chroot build script - runs inside chroot environment
set -e

echo "=== Inside Chroot ==="

export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources
export LC_ALL=POSIX

cd $LFS_SOURCES

# 7.5 Creating Directories
echo "[1/3] Creating directories..."
mkdir -pv /{bin,boot,etc/{opt,sysconfig},home,lib/firmware,mnt,opt}
mkdir -pv /{media/{floppy,cdrom},sbin,srv,var}
install -dv -m 0750 /root
install -dv -m 1777 /tmp /var/tmp
mkdir -pv /usr/{,local/}{bin,include,lib,sbin,src}
mkdir -pv /usr/{,local/}share/{doc,info,locale,man}
mkdir -v /usr/libexec
mkdir -pv /usr/share/{color,dict,doc,info,locale,man}
ln -sv /tools/bin/{bash,install,ld,ldd} /bin
ln -sv /tools/etc/ssl /etc
ln -sv /tools/lib/libgcc_s.so{,.1} /usr/lib
ln -sv /tools/lib/libstdc++.la /usr/lib
install -v -dm755 /usr/lib/gconv
chmod -v 1777 /usr/lib/gconv
mkdir -pv /usr/share/i18n/charmaps
mkdir -pv /usr/share/i18n/locales
mkdir -pv /usr/lib/nss
install -v -dm755 /usr/share/man/man{1..8}
for locale in en_US en_US.UTF-8; do
    localedef -i $(echo $locale | sed 's/\..*//') -f $(echo $locale | sed 's/.*\.//') $locale
done
localedef -i POSIX -f UTF-8 C.UTF-8 2>/dev/null || true
localedef -i en_HK -f ISO-8859-15 en_HK
localedef -i en_PH -f ISO-8859-15 en_PH

# 7.6 Creating Essential Files and Symlinks
echo "[2/3] Creating essential files..."
cat > /etc/hosts << "EOF"
127.0.0.1 localhost
::1       localhost
EOF

cat > /etc/passwd << "EOF"
root:x:0:0:root:/root:/bin/bash
lfs:x:1000:1000:lfs:/home/lfs:/bin/bash
EOF

cat > /etc/shadow << "EOF"
root:$6$xyz$...:19000:0:99999:7:::
lfs:$6$xyz$...:19000:0:99999:7:::
EOF

cat > /etc/group << "EOF"
root:x:0:
bin:x:1:
sys:x:2:
kmem:x:3:
tty:x:4:
sys:x:5:
audio:x:6:
cdrom:x:7:
disk:x:8:
floppy:x:9:
video:x:10:
dialout:x:11:
tape:x:12:
audio:x:13:
lfs:x:1000:
EOF

touch /var/log/{btmp,lastlog,wtmp}
chmod -v 664 /var/log/{btmp,lastlog,wtmp}
chgrp -v utmp /var/log/lastlog

# 7.7 Gettext-0.22
echo "[3/3] Building additional tools..."
echo ""
echo "=== Building Gettext-0.22 ==="
cd $LFS_SOURCES
tar xf gettext-0.22.tar.xz
cd gettext-0.22
./configure --disable-shared
make
cp -v gettext-tools/src/{msgfmt,msgmerge,xgettext} /usr/bin
cd $LFS_SOURCES
rm -rf gettext-0.22

# 7.8 Bison-3.8.2
echo ""
echo "=== Building Bison-3.8.2 ==="
cd $LFS_SOURCES
tar xf bison-3.8.2.tar.xz
cd bison-3.8.2
./configure --prefix=/usr \
            --docdir=/usr/share/doc/bison-3.8.2
make
make install
cd $LFS_SOURCES
rm -rf bison-3.8.2

# 7.9 Perl-5.38.0
echo ""
echo "=== Building Perl-5.38.0 ==="
cd $LFS_SOURCES
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

# 7.10 Python-3.11.4
echo ""
echo "=== Building Python-3.11.4 ==="
cd $LFS_SOURCES
tar xf Python-3.11.4.tar.xz
cd Python-3.11.4
./configure --prefix=/usr \
            --enable-shared \
            --with-system-expat \
            --with-ensurepip=install
make
make install
cd $LFS_SOURCES
rm -rf Python-3.11.4

# 7.11 Texinfo-7.0.3
echo ""
echo "=== Building Texinfo-7.0.3 ==="
cd $LFS_SOURCES
tar xf texinfo-7.0.3.tar.xz
cd texinfo-7.0.3
./configure --prefix=/usr
make
make install
cd $LFS_SOURCES
rm -rf texinfo-7.0.3

# 7.12 Util-linux-2.39.1
echo ""
echo "=== Building Util-linux-2.39.1 ==="
cd $LFS_SOURCES
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

# 7.13 Cleaning up
echo ""
echo "=== Cleaning up ==="
rm -rf /usr/share/{info,man,doc}/*
find /usr/{lib,libexec} -name \*.la -delete
rm -rf /tools

echo ""
echo "=== Chroot Tools Complete ==="
echo "Next: Exit chroot and run scripts/05-system.sh"
CHROOT_EOF
chmod +x $LFS/chroot-build.sh

echo ""
echo "=== Chroot Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Enter chroot: sudo $LFS/entreroot.sh"
echo "2. Inside chroot, run: /mnt/lfs/chroot-build.sh"
echo "3. Exit chroot: exit"
echo "4. Continue with: scripts/05-system.sh"
