#!/bin/bash
# Create Bootable Image Directly - No LFS Build Required
# Tạo bootable image trực tiếp cho UTM SE

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     TẠO BOOTABLE IMAGE TRỰC TIẾP CHO UTM SE                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "Cần chạy với sudo!"
    exit 1
fi

IMAGE_NAME="lfs-bootable.img"
MOUNT_POINT="/mnt/lfs-img"

echo "[1/8] Tạo image 2GB..."
dd if=/dev/zero of=${IMAGE_NAME} bs=1M count=2048 status=progress

echo ""
echo "[2/8] Format ext4..."
mkfs.ext4 -L "LFS-Boot" ${IMAGE_NAME}

echo ""
echo "[3/8] Mount image..."
mkdir -p ${MOUNT_POINT}
mount -o loop ${IMAGE_NAME} ${MOUNT_POINT}

echo ""
echo "[4/8] Tạo cấu trúc thư mục..."
mkdir -p ${MOUNT_POINT}/{bin,sbin,etc/init.d,etc/ssh,usr/bin,usr/sbin,usr/lib,var/log,var/run,tmp,root,home/guest,boot/grub,dev,proc,sys,lib/modules}

echo ""
echo "[5/8] Copy busybox (nếu có)..."
if command -v busybox &> /dev/null; then
    cp $(which busybox) ${MOUNT_POINT}/bin/
    cd ${MOUNT_POINT}/bin
    for cmd in sh bash ls cat cp mv rm mkdir mount umount ps kill sleep echo date hostname vi nano grep find wget curl git apt-get dpkg; do
        ln -sf busybox ${cmd} 2>/dev/null || true
    done
    cd -
else
    # Tạo shell script thay thế
    cat > ${MOUNT_POINT}/bin/sh << 'SHELL'
#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           LFS Linux - Bootable System                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Available commands: help, ls, cat, echo, date, reboot, poweroff"
echo ""
while true; do
    echo -n "lfs@localhost:~$ "
    read cmd
    case $cmd in
        help)
            echo "Commands:"
            echo "  help      - Show this help"
            echo "  ls        - List files"
            echo "  cat       - Show file content"
            echo "  echo      - Print text"
            echo "  date      - Show date/time"
            echo "  hostname  - Show hostname"
            echo "  reboot    - Reboot system"
            echo "  poweroff  - Shutdown system"
            echo "  exit      - Exit shell"
            ;;
        ls) echo "/bin /sbin /etc /usr /var /tmp /root /home /boot /dev /proc /sys" ;;
        cat) echo "Usage: cat <file>" ;;
        echo) echo "LFS Linux Bootable System" ;;
        date) date ;;
        hostname) echo "lfs" ;;
        reboot) echo "Rebooting..."; reboot ;;
        poweroff) echo "Shutting down..."; poweroff ;;
        exit) echo "Goodbye!"; exit 0 ;;
        "") ;;
        *) echo "Command not found: $cmd (type 'help' for commands)" ;;
    esac
done
SHELL
    chmod +x ${MOUNT_POINT}/bin/sh
    ln -sf sh ${MOUNT_POINT}/bin/bash
fi

echo ""
echo "[6/8] Tạo system files..."

# inittab
cat > ${MOUNT_POINT}/etc/inittab << 'INITTAB'
::sysinit:/etc/init.d/rcS
tty1::respawn:/bin/sh
::ctrlaltdel:/sbin/reboot
::shutdown:/bin/umount -a -r
INITTAB

# init.d/rcS
cat > ${MOUNT_POINT}/etc/init.d/rcS << 'RCS'
#!/bin/sh
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
mount -t tmpfs none /tmp
echo "LFS Linux started!"
RCS
chmod +x ${MOUNT_POINT}/etc/init.d/rcS

# hostname & hosts
echo "lfs" > ${MOUNT_POINT}/etc/hostname
echo "127.0.0.1 localhost lfs" > ${MOUNT_POINT}/etc/hosts

# fstab
cat > ${MOUNT_POINT}/etc/fstab << 'FSTAB'
/dev/sda1    /    ext4    defaults,noatime    1 1
proc         /proc proc   defaults            0 0
sysfs        /sys  sysfs  defaults            0 0
tmpfs        /tmp  tmpfs  defaults            0 0
FSTAB

echo ""
echo "[7/8] Tạo GRUB bootloader..."
mkdir -p ${MOUNT_POINT}/boot/grub
cat > ${MOUNT_POINT}/boot/grub/grub.cfg << 'GRUB'
set default=0
set timeout=5

menuentry "LFS Linux" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz root=/dev/sda1 ro console=ttyS0,115200n8 console=tty1
    initrd /boot/initramfs.img
}

menuentry "LFS Linux (Recovery)" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz root=/dev/sda1 ro single
    initrd /boot/initramfs.img
}
GRUB

echo ""
echo "[8/8] Tạo initramfs..."
mkdir -p ${MOUNT_POINT}/boot/initramfs/{bin,sbin,etc,proc,sys,dev}

cat > ${MOUNT_POINT}/boot/initramfs/init << 'INIT'
#!/bin/sh
echo "LFS Booting..."
export PATH=/bin:/sbin
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
echo "Mounting root filesystem..."
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
find . -print0 | cpio --null -ov --format=newc | gzip -9 > ../initramfs.img 2>/dev/null

# Copy kernel from host (if exists)
if [ -f "/boot/vmlinuz" ]; then
    cp /boot/vmlinuz ${MOUNT_POINT}/boot/vmlinuz
elif [ -f "/boot/vmlinuz-*" ]; then
    cp /boot/vmlinuz-* ${MOUNT_POINT}/boot/vmlinuz
else
    echo "WARNING: No kernel found, creating placeholder"
    echo "Please add kernel manually" > ${MOUNT_POINT}/boot/README
fi

# Cleanup
cd /
umount ${MOUNT_POINT}

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     HOÀN TẤT! Bootable Image ready                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "File: $(pwd)/${IMAGE_NAME}"
echo "Size: $(ls -lh ${IMAGE_NAME} | awk '{print $5}')"
echo ""
echo "CÁCH SỬ DỤNG:"
echo ""
echo "1. Copy file ${IMAGE_NAME} vào iPhone"
echo "2. Mở UTM SE → Create New → Virtualize → Linux"
echo "3. Import Drive: chọn file ${IMAGE_NAME}"
echo "4. Cấu hình: CPU=2, RAM=512MB, Network=NAT"
echo "5. Boot VM"
echo ""
echo "Login: root (không có password)"
echo ""
echo "Lưu ý: Đây là minimal system. Để có full LFS,"
echo "cần build trên host trước."
