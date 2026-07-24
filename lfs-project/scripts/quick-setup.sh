#!/bin/bash
# Quick Setup - Tạo disk image hoàn chỉnh cho UTM SE
# Chạy script này để tạo file .img có thể boot ngay

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     QUICK SETUP - Tạo Disk Image cho UTM SE                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "Cần chạy với sudo!"
    echo "Usage: sudo ./quick-setup.sh"
    exit 1
fi

# Configuration
IMAGE_NAME="lfs-utm-se.img"
MOUNT_POINT="/mnt/lfs-img"

echo "Hướng dẫn:"
echo ""
echo "1. TẠO DISK IMAGE:"
echo "   sudo ./quick-setup.sh create"
echo ""
echo "2. CHẠY TRÊN UTM SE:"
echo "   - Import file lfs-utm-se.img vào UTM"
echo "   - Tạo VM Linux mới"
echo "   - Boot từ disk image"
echo ""

case "$1" in
    create)
        echo "[1/5] Tạo disk image 20GB..."
        dd if=/dev/zero of=${IMAGE_NAME} bs=1M count=20480 status=progress

        echo ""
        echo "[2/5] Format ext4..."
        mkfs.ext4 -L "LFS-Root" ${IMAGE_NAME}

        echo ""
        echo "[3/5] Mount và copy hệ thống..."
        mkdir -p ${MOUNT_POINT}
        mount -o loop ${IMAGE_NAME} ${MOUNT_POINT}

        # Copy LFS system
        if [ -d "/mnt/lfs" ]; then
            cp -a /mnt/lfs/* ${MOUNT_POINT}/
        else
            echo "WARN: /mnt/lfs not found, creating minimal system"
            mkdir -p ${MOUNT_POINT}/{bin,sbin,etc,usr,var,lib,tmp,root,home,boot,dev,proc,sys}
        fi

        echo ""
        echo "[4/5] Cài GRUB bootloader..."

        # Install GRUB
        grub-install --target=i386-pc --boot-directory=${MOUNT_POINT}/boot ${IMAGE_NAME} || true

        # Create GRUB config
        mkdir -p ${MOUNT_POINT}/boot/grub
        cat > ${MOUNT_POINT}/boot/grub/grub.cfg << 'GRUB'
set default=0
set timeout=5
insmod all_video

menuentry "LFS Linux" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz root=/dev/sda1 ro quiet
    initrd /boot/initramfs.img
}
GRUB

        echo ""
        echo "[5/5] Tạo initramfs..."

        # Create initramfs
        mkdir -p ${MOUNT_POINT}/boot/initramfs/{bin,sbin,etc,proc,sys,dev}
        cat > ${MOUNT_POINT}/boot/initramfs/init << 'INIT'
#!/bin/sh
export PATH=/bin:/sbin
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
for i in $(seq 1 30); do
    [ -e /dev/sda1 ] && break
    sleep 1
done
mkdir -p /mnt/root
mount -t ext4 /dev/sda1 /mnt/root
exec switch_root /mnt/root /sbin/init
INIT
        chmod +x ${MOUNT_POINT}/boot/initramfs/init

        cd ${MOUNT_POINT}/boot/initramfs
        find . -print0 | cpio --null -ov --format=newc | gzip -9 > ../initramfs.img

        umount ${MOUNT_POINT}

        echo ""
        echo "╔═══════════════════════════════════════════════════════════════╗"
        echo "║     HOÀN TẤT! Disk image đã sẵn sàng                       ║"
        echo "╚═══════════════════════════════════════════════════════════════╝"
        echo ""
        echo "File: $(pwd)/${IMAGE_NAME}"
        echo "Size: $(ls -lh ${IMAGE_NAME} | awk '{print $5}')"
        echo ""
        echo "Các bước tiếp theo:"
        echo ""
        echo "1. Copy file ${IMAGE_NAME} vào iPhone"
        echo "   - Dùng AirDrop, iCloud, hoặc iTunes"
        echo ""
        echo "2. Mở UTM SE trên iPhone"
        echo ""
        echo "3. Tạo VM mới:"
        echo "   - Nhấn + (tạo mới)"
        echo "   - Chọn 'Virtualize'"
        echo "   - Chọn 'Linux'"
        echo "   - Import file: ${IMAGE_NAME}"
        echo ""
        echo "4. Cấu hình VM:"
        echo "   - Name: LFS Linux"
        echo "   - CPU: 2 cores"
        echo "   - RAM: 1024 MB"
        echo "   - Storage: Import existing drive"
        echo "   - Network: Default (NAT)"
        echo ""
        echo "5. Boot và sử dụng!"
        echo ""
        echo "Troubleshooting:"
        echo "- Nếu boot không được, thử tạo VM mới và import lại"
        echo "- Nếu lag, giảm RAM xuống 512MB"
        echo "- Nếu không có mạng, kiểm tra network setting"
        ;;

    *)
        echo "Usage: sudo ./quick-setup.sh create"
        echo ""
        echo "Ví dụ:"
        echo "  sudo ./quick-setup.sh create"
        ;;
esac
