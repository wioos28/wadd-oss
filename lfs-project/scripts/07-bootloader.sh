#!/bin/bash
# LFS Build Script - Chapter 10: Making the LFS System Bootable
# This script sets up the bootloader

set -e

echo "=== LFS Build - Bootloader ==="
echo "Starting at: $(date)"

# Create chroot script for Chapter 10
cat > $LFS/chroot-ch10.sh << 'CHROOT_EOF'
#!/bin/bash
set -e

echo "=== Inside Chroot - Chapter 10 ==="

export LFS=/mnt/lfs
export LC_ALL=POSIX

# 10.1 Creating /etc/fstab
echo ""
echo "=== Creating /etc/fstab ==="
cat > /etc/fstab << "EOF"
# Begin /etc/fstab
# file_system  mount_point  type  options  dump  fsck
/dev/sda1      /            ext4  defaults 1     1
proc           /proc        proc  defaults 0     0
sysfs          /sys         sysfs defaults 0     0
devpts         /dev/pts     devpts gid=5,mode=620 0 0
tmpfs          /run         tmpfs defaults 0     0
devtmpfs       /dev         devtmpfs mode=0755,nosuid 0 0
# End /etc/fstab
EOF

# 10.2 Linux Kernel
echo ""
echo "=== Installing Linux Kernel ==="
cd $LFS_SOURCES

# Extract kernel
tar xf linux-6.4.12.tar.xz
cd linux-6.4.12

# Configure kernel
make mrproper

# Create minimal config
cat > .config << "EOF"
# Minimal kernel configuration for LFS
CONFIG_MODULES=y
CONFIG_MODULE_UNLOAD=y
CONFIG_NET=y
CONFIG_INET=y
CONFIG_IPV6=y
CONFIG_EXT4_FS=y
CONFIG_VFAT_FS=y
CONFIG_NTFS_FS=y
CONFIG_TMPFS=y
CONFIG_PROC_FS=y
CONFIG_SYSFS=y
CONFIG_DEVPTS_FS=y
CONFIG_TMPFS_POSIX_ACL=y
CONFIG_BLK_DEV_SD=y
CONFIG_BLK_DEV_ATA=y
CONFIG_BLK_DEV_PIIX=y
CONFIG_BLK_DEV_VIRTIO_BLK=m
CONFIG_BLK_DEV_VIRTIO_SCSI=m
CONFIG_VIRTIO_PCI=m
CONFIG_VIRTIO_BLK=m
CONFIG_VIRTIO_NET=m
CONFIG_VIRTIO_CONSOLE=m
CONFIG_VIRTIO=m
CONFIG_SCSI=m
CONFIG_SCSI_VIRTIO=m
CONFIG_INPUT_EVDEV=m
CONFIG_SERIO_I8042=m
CONFIG_SERIO=m
CONFIG_TTY=y
CONFIG_VT=y
CONFIG_VT_CONSOLE=y
CONFIG_FRAMEBUFFER_CONSOLE=y
CONFIG_LOGO=y
CONFIG_LOGO_LINUX_MONO=y
CONFIG_LOGO_LINUX_VGA16=y
CONFIG_LOGO_LINUX_CLUT224=y
CONFIG_SOUND=m
CONFIG_SND=m
CONFIG_SND_HDA_INTEL=m
CONFIG_SND_HDA_CODEC_HDMI=m
CONFIG_USB=y
CONFIG_USB_XHCI_HCD=m
CONFIG_USB_EHCI_HCD=m
CONFIG_USB_OHCI_HCD=m
CONFIG_USB_STORAGE=m
CONFIG_USB_HID=m
CONFIG_HID_GENERIC=m
CONFIG_HID_APPLE=m
CONFIG_HID_GENERIC=m
CONFIG_FONT_SUPPORT=y
CONFIG_CONSOLE_TRANSLATIONS=y
CONFIG_VT_CONSOLE_SLEEP=y
CONFIG_HW_CONSOLE=y
CONFIG_UNIX98_PTYS=y
CONFIG_DEVPTS_MULTIPLE_INSTANCES=y
CONFIG_SYSFS_DEPRECATED=y
CONFIG_RELAY=y
CONFIG_IKCONFIG=m
CONFIG_IKCONFIG_PROC=m
CONFIG_PROC_SYSCTL=y
CONFIG_PRINTK=y
CONFIG_BUG=y
CONFIG_FUTEX=y
CONFIG_EPOLL=y
CONFIG_SIGNALFD=y
CONFIG_TIMERFD=y
CONFIG_EVENTFD=y
CONFIG_SHMEM=y
CONFIG_AIO=y
CONFIG_DEFAULT_HOSTNAME="(none)"
CONFIG_SYSCTL=y
CONFIG_MULTIUSER=y
CONFIG_SYSCTL_EXCEPTION_TRACE=y
CONFIG_EXPERT=y
CONFIG_SYSCTL_SYSCALL=y
CONFIG_KALLSYMS=y
CONFIG_KALLSYMS_ALL=y
CONFIG_PRINTK=y
CONFIG_BUG=y
CONFIG_FUTEX=y
CONFIG_EPOLL=y
CONFIG_SIGNALFD=y
CONFIG_TIMERFD=y
CONFIG_EVENTFD=y
CONFIG_SHMEM=y
CONFIG_AIO=y
CONFIG_DEFAULT_HOSTNAME="(none)"
CONFIG_SYSCTL=y
CONFIG_MULTIUSER=y
CONFIG_SYSCTL_EXCEPTION_TRACE=y
CONFIG_EXPERT=y
CONFIG_SYSCTL_SYSCALL=y
CONFIG_KALLSYMS=y
CONFIG_KALLSYMS_ALL=y
EOF

# Build kernel
make
make modules_install
cp arch/x86/boot/bzImage /boot/vmlinuz-6.4.12-lfs
cp System.map /boot/System.map-6.4.12
cp .config /boot/config-6.4.12

# Create initramfs
mkdir -p /boot/initramfs
cd /boot/initramfs
mkdir -p {bin,sbin,etc,proc,sys,dev,usr/bin,usr/sbin,lib/modules}

cat > init << "INIT"
#!/bin/sh
# Minimal initramfs init script

export PATH=/bin:/sbin:/usr/bin:/usr/sbin

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
mount -t tmpfs none /tmp

echo "LFS Linux - Loading..."

# Wait for root device
echo "Waiting for root device..."
for i in $(seq 1 30); do
    if [ -e /dev/sda1 ]; then
        echo "Root device found: /dev/sda1"
        break
    fi
    sleep 1
done

# Mount root filesystem
mkdir -p /mnt/root
mount -t ext4 /dev/sda1 /mnt/root

# Switch root
echo "Switching to root filesystem..."
umount /proc
umount /sys
umount /dev

exec switch_root /mnt/root /sbin/init
INIT
chmod +x init

# Copy required modules
for mod in ext4 mbcache jbd2; do
    find /lib/modules -name ${mod}.ko* -exec cp {} /boot/initramfs/lib/modules/ \;
done

# Create initramfs image
find . -print0 | cpio --null -ov --format=newc | gzip -9 > /boot/initramfs-6.4.12.img

cd $LFS_SOURCES
rm -rf linux-6.4.12

# 10.3 Using GRUB to Set Up the Boot Process
echo ""
echo "=== Installing GRUB ==="
grub-install --target=i386-pc /dev/sda

cat > /boot/grub/grub.cfg << "GRUB"
# Begin /boot/grub/grub.cfg

set default=0
set timeout=5

insmod ext2
insmod gzio

menuentry "LFS Linux 6.4.12" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz-6.4.12 root=/dev/sda1 ro
    initrd /boot/initramfs-6.4.12.img
}

menuentry "LFS Linux 6.4.12 (recovery)" {
    set root=(hd0,msdos1)
    linux /boot/vmlinuz-6.4.12 root=/dev/sda1 ro single
    initrd /boot/initramfs-6.4.12.img
}

# End /boot/grub/grub.cfg
GRUB

# Update GRUB
update-grub

echo ""
echo "=== Bootloader Installation Complete ==="
echo "Next step: Run scripts/08-dev-tools.sh"
CHROOT_EOF
chmod +x $LFS/chroot-ch10.sh

echo ""
echo "=== Chapter 10 Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Enter chroot: sudo $LFS/entreroot.sh"
echo "2. Inside chroot, run: /mnt/lfs/chroot-ch10.sh"
echo "3. Exit chroot: exit"
echo "4. Continue with: scripts/08-dev-tools.sh"
