#!/bin/bash
# Create Bootable Disk Image for UTM SE
# Tạo file disk image có thể boot trên UTM SE

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Tạo Disk Image Bootable cho UTM SE                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
IMAGE_NAME="lfs-utm-se.img"
IMAGE_SIZE="20G"  # 20GB
MOUNT_POINT="/mnt/lfs-img"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Script này cần chạy với sudo!"
    echo "Usage: sudo ./create-disk-image.sh"
    exit 1
fi

# Check if LFS build exists
if [ ! -d "/mnt/lfs" ]; then
    echo "ERROR: Không tìm thấy /mnt/lfs"
    echo "Hãy build LFS trước khi tạo disk image!"
    echo "Chạy: sudo ./build.sh"
    exit 1
fi

echo "[1/6] Tạo disk image ${IMAGE_SIZE}..."
dd if=/dev/zero of=${IMAGE_NAME} bs=1M count=20480 status=progress

echo ""
echo "[2/6] Format disk image..."
mkfs.ext4 -L "LFS-Root" ${IMAGE_NAME}

echo ""
echo "[3/6] Mount disk image..."
mkdir -p ${MOUNT_POINT}
mount -o loop ${IMAGE_NAME} ${MOUNT_POINT}

echo ""
echo "[4/6] Copy hệ thống LFS..."
# Copy hệ thống đã build
cp -a /mnt/lfs/* ${MOUNT_POINT}/

# Tạo thư mục boot
mkdir -p ${MOUNT_POINT}/boot/grub
mkdir -p ${MOUNT_POINT}/boot/initramfs

echo ""
echo "[5/6] Cấu hình bootloader..."

# Tạo GRUB config
cat > ${MOUNT_POINT}/boot/grub/grub.cfg << 'GRUB'
# GRUB Config for LFS on UTM SE

set default=0
set timeout=5

insmod all_video
insmod gfxterm
insmod ext2

set gfxmode=auto
set gfxpayload=keep

menuentry "LFS Linux" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz root=/dev/sda1 ro quiet splash
    initrd /boot/initramfs.img
}

menuentry "LFS Linux (Recovery)" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz root=/dev/sda1 ro single
    initrd /boot/initramfs.img
}
GRUB

# Tạo fstab
cat > ${MOUNT_POINT}/etc/fstab << 'FSTAB'
# /etc/fstab: static file system information.
/dev/sda1    /            ext4    defaults,noatime    1 1
proc         /proc        proc    defaults            0 0
sysfs        /sys         sysfs   defaults            0 0
devpts       /dev/pts     devpts  gid=5,mode=620      0 0
tmpfs        /run         tmpfs   defaults            0 0
devtmpfs     /dev         devtmpfs mode=0755,nosuid   0 0
FSTAB

# Tạo GRUB install script
cat > ${MOUNT_POINT}/tmp/install-grub.sh << 'GRUBINSTALL'
#!/bin/bash
# Install GRUB
grub-install --target=i386-pc /dev/sda
update-grub
GRUBINSTALL
chmod +x ${MOUNT_POINT}/tmp/install-grub.sh

echo ""
echo "[6/6] Tạo initramfs..."

# Tạo initramfs đơn giản
mkdir -p ${MOUNT_POINT}/boot/initramfs/{bin,sbin,etc,proc,sys,dev,lib/modules}

cat > ${MOUNT_POINT}/boot/initramfs/init << 'INIT'
#!/bin/sh
# Minimal init script for LFS

export PATH=/bin:/sbin:/usr/bin:/usr/sbin

echo "LFS Linux Booting..."

# Mount essential filesystems
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
mount -t tmpfs none /tmp

# Wait for root device
echo "Waiting for root device..."
for i in $(seq 1 30); do
    if [ -e /dev/sda1 ]; then
        echo "Root device found!"
        break
    fi
    sleep 1
done

# Mount root
mkdir -p /mnt/root
mount -t ext4 /dev/sda1 /mnt/root

# Switch root
echo "Switching to root filesystem..."
exec switch_root /mnt/root /sbin/init
INIT
chmod +x ${MOUNT_POINT}/boot/initramfs/init

# Copy modules
find /lib/modules -name "*.ko*" -exec cp {} ${MOUNT_POINT}/boot/initramfs/lib/modules/ \; 2>/dev/null || true

# Tạo initramfs image
cd ${MOUNT_POINT}/boot/initramfs
find . -print0 | cpio --null -ov --format=newc | gzip -9 > ${MOUNT_POINT}/boot/initramfs.img

# Cleanup
cd /
umount ${MOUNT_POINT}

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Disk Image đã tạo thành công!                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "File: ${IMAGE_NAME}"
echo "Size: ${IMAGE_SIZE}"
echo ""
echo "Hướng dẫn sử dụng trên UTM SE:"
echo ""
echo "1. Mở UTM SE trên iPhone"
echo "2. Nhấn + để tạo VM mới"
echo "3. Chọn 'Virtualize' → 'Linux'"
echo "4. Import file: ${IMAGE_NAME}"
echo "5. Cấu hình:"
echo "   - CPU: 2 cores"
echo "   - RAM: 1024 MB (hoặc 2048 MB)"
echo "   - Storage: ${IMAGE_NAME}"
echo "   - Network: Default (NAT)"
echo "6. Boot VM"
echo ""
echo "Login:"
echo "   Username: root"
echo "   Password: (đã set khi build)"
echo ""
echo "Enjoy your LFS system! 🐧"
