#!/bin/bash
# Create Minimal Bootable Image for UTM SE
# Tạo image nhỏ, chạy được ngay trên UTM SE

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     TẠO MINIMAL BOOT IMAGE CHO UTM SE                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "Cần chạy với sudo!"
    echo "Usage: sudo ./create-minimal-boot.sh"
    exit 1
fi

IMAGE_NAME="lfs-minimal-boot.img"
MOUNT_POINT="/mnt/lfs-boot"

echo "[1/4] Tạo image 2GB (nhẹ, nhanh)..."
dd if=/dev/zero of=${IMAGE_NAME} bs=1M count=2048 status=progress

echo ""
echo "[2/4] Format..."
mkfs.ext4 -L "LFS-Boot" ${IMAGE_NAME}

echo ""
echo "[3/4] Mount và cài đặt..."
mkdir -p ${MOUNT_POINT}
mount -o loop ${IMAGE_NAME} ${MOUNT_POINT}

# Tạo cấu trúc thư mục cơ bản
mkdir -p ${MOUNT_POINT}/{bin,sbin,etc/ssh,usr/bin,usr/sbin,usr/lib,var/log,var/run,tmp,root,home/guest,boot/grub,dev,proc,sys,lib/modules,lib/firmware}

# Copy busybox (nếu có) hoặc tạo minimal binaries
if command -v busybox &> /dev/null; then
    cp $(which busybox) ${MOUNT_POINT}/bin/
    cd ${MOUNT_POINT}/bin
    for cmd in sh bash ls cat cp mv rm mkdir mount umount ps kill sleep echo date hostname; do
        ln -sf busybox ${cmd}
    done
    cd -
else
    # Tạo minimal shell script
    cat > ${MOUNT_POINT}/bin/sh << 'SHELL'
#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
echo "LFS Linux Minimal System"
echo "Type 'help' for commands"
while true; do
    echo -n "$ "
    read cmd
    case $cmd in
        help) echo "Available: help, ls, cat, echo, date, reboot, poweroff, exit" ;;
        ls) echo "/bin /sbin /etc /usr /var /tmp /root /home /boot /dev /proc /sys" ;;
        cat) echo "Usage: cat <file>" ;;
        echo) echo "LFS Linux" ;;
        date) date ;;
        reboot) reboot ;;
        poweroff) poweroff ;;
        exit) exit 0 ;;
        *) echo "Command not found: $cmd" ;;
    esac
done
SHELL
    chmod +x ${MOUNT_POINT}/bin/sh
    ln -sf sh ${MOUNT_POINT}/bin/bash
fi

# Tạo inittab
cat > ${MOUNT_POINT}/etc/inittab << 'INITTAB'
::sysinit:/etc/init.d/rcS
tty1::respawn:/bin/sh
tty2::respawn:/bin/sh
::ctrlaltdel:/sbin/reboot
::shutdown:/bin/umount -a -r
INITTAB

# Tạo init.d
mkdir -p ${MOUNT_POINT}/etc/init.d
cat > ${MOUNT_POINT}/etc/init.d/rcS << 'RCS'
#!/bin/sh
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
echo "LFS Linux started!"
RCS
chmod +x ${MOUNT_POINT}/etc/init.d/rcS

# Tạo hostname
echo "lfs" > ${MOUNT_POINT}/etc/hostname
echo "127.0.0.1 localhost lfs" > ${MOUNT_POINT}/etc/hosts

# Tạo fstab
cat > ${MOUNT_POINT}/etc/fstab << 'FSTAB'
/dev/sda1    /    ext4    defaults    1 1
proc         /proc proc   defaults    0 0
sysfs        /sys  sysfs  defaults    0 0
FSTAB

# Tạo GRUB config
mkdir -p ${MOUNT_POINT}/boot/grub
cat > ${MOUNT_POINT}/boot/grub/grub.cfg << 'GRUB'
set default=0
set timeout=5

menuentry "LFS Linux Minimal" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz root=/dev/sda1 ro console=ttyS0,115200n8 console=tty1
    initrd /boot/initramfs.img
}
GRUB

# Tạo initramfs
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
find . -print0 | cpio --null -ov --format=newc | gzip -9 > ../initramfs.img

echo ""
echo "[4/4] Cleanup..."
umount ${MOUNT_POINT}

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     HOÀN TẤT! Minimal Boot Image ready                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "File: $(pwd)/${IMAGE_NAME}"
echo "Size: $(ls -lh ${IMAGE_NAME} | awk '{print $5}')"
echo ""
echo "HƯỚNG DẪN SỬ DỤNG:"
echo ""
echo "1. Copy file vào iPhone:"
echo "   - AirDrop: Gửi file ${IMAGE_NAME} từ Mac/PC"
echo "   - iCloud: Upload và download trên iPhone"
echo "   - iTunes: Sync file qua iTunes"
echo ""
echo "2. Mở UTM SE trên iPhone"
echo ""
echo "3. Tạo VM mới:"
echo "   - Nhấn + (Create New)"
echo "   - Chọn 'Virtualize'"
echo "   - Chọn 'Linux'"
echo "   - Import Drive: chọn file ${IMAGE_NAME}"
echo ""
echo "4. Cấu hình VM:"
echo "   - Name: LFS Minimal"
echo "   - CPU: 1-2 cores"
echo "   - RAM: 256-512 MB"
echo "   - Storage: ${IMAGE_NAME}"
echo "   - Network: Default (NAT)"
echo ""
echo "5. Boot VM!"
echo ""
echo "Sau khi boot thành công, bạn có thể:"
echo "- Cài thêm packages với apt-get"
echo "- Cài desktop environment"
echo "- Cài development tools"
echo ""
echo "Chúc may mắn! 🐧"
