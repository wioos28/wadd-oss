#!/bin/bash
# CodeMagic Build Script - Quick LFS Build
# Simplified build for CodeMagic CI/CD

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     CodeMagic LFS Build Script                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Starting at: $(date)"
echo ""

# Configuration
LFS_VERSION="12.0"
KERNEL_VERSION="6.4.12"
WORK_DIR="/tmp/lfs-build"
IMAGE_SIZE="20480"  # 20GB in MB

# Create work directory
mkdir -p ${WORK_DIR}
cd ${WORK_DIR}

echo "[1/10] Installing dependencies..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    bison \
    gawk \
    texinfo \
    python3 \
    python3-pip \
    unzip \
    wget \
    curl \
    git \
    libncurses-dev \
    libssl-dev \
    libelf-dev \
    bc \
    flex \
    man-db \
    locales \
    sudo \
    vim \
    nano \
    openssh-server \
    network-manager \
    qemu-utils \
    grub-pc-bin \
    grub-common

echo "[2/10] Configuring locale..."
sudo locale-gen en_US.UTF-8
sudo update-locale LANG=en_US.UTF-8

echo "[3/10] Creating LFS user..."
sudo useradd -m -s /bin/bash lfs || true
echo "lfs:password" | sudo chpasswd
sudo mkdir -p /mnt/lfs
sudo chown -v lfs /mnt/lfs

echo "[4/10] Setting environment variables..."
export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources
export LFS_TGT=$(uname -m)-lfs-linux-gnu
export PATH=$LFS/tools/bin:$PATH
export LC_ALL=POSIX

echo "[5/10] Creating directories..."
sudo -u lfs mkdir -p $LFS_SOURCES

echo "[6/10] Downloading packages..."
cd ${WORK_DIR}
git clone https://github.com/wioos28/wadd-oss.git || true
cd wadd-oss/lfs-project
sudo -u lfs bash -c "export LFS=/mnt/lfs && ./scripts/01-download.sh" || true

echo "[7/10] Building cross-toolchain..."
sudo -u lfs bash -c "export LFS=/mnt/lfs && ./scripts/02-cross-toolchain.sh" || true

echo "[8/10] Building temporary tools..."
sudo -u lfs bash -c "export LFS=/mnt/lfs && ./scripts/03-temp-tools.sh" || true

echo "[9/10] Building system in chroot..."
# Mount filesystems
sudo mount -v --bind /dev /mnt/lfs/dev
sudo mount -v --bind /dev/pts /mnt/lfs/dev/pts
sudo mount -vt proc proc /mnt/lfs/proc
sudo mount -vt sysfs sysfs /mnt/lfs/sys
sudo mount -vt tmpfs tmpfs /mnt/lfs/run

# Enter chroot and build
sudo chroot /mnt/lfs /tools/bin/env -i \
    HOME=/root \
    TERM="$TERM" \
    PATH=/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin \
    /tools/bin/bash --login +h -c '
        /mnt/lfs/chroot-build.sh
        /mnt/lfs/chroot-ch8.sh
        /mnt/lfs/chroot-optimize.sh
        /mnt/lfs/chroot-desktop.sh
        /mnt/lfs/chroot-dev.sh
    '

# Umount
sudo umount -v /mnt/lfs/dev/pts
sudo umount -v /mnt/lfs/dev
sudo umount -v /mnt/lfs/proc
sudo umount -v /mnt/lfs/sys
sudo umount -v /mnt/lfs/run

echo "[10/10] Creating bootable disk image..."
cd ${WORK_DIR}/wadd-oss/lfs-project
sudo ./scripts/create-disk-image.sh

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     BUILD COMPLETE!                                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Build time: $(date)"
echo ""

# Show results
if [ -f "lfs-utm-se.img" ]; then
    echo "✅ Full disk image created: lfs-utm-se.img"
    ls -lh lfs-utm-se.img
fi

if [ -f "lfs-minimal-boot.img" ]; then
    echo "✅ Minimal boot image created: lfs-minimal-boot.img"
    ls -lh lfs-minimal-boot.img
fi

echo ""
echo "Next steps:"
echo "1. Download the .img file"
echo "2. Import into UTM SE on iPhone"
echo "3. Boot the VM"
echo ""
echo "Enjoy your LFS system! 🐧"
