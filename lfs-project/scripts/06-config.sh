#!/bin/bash
# LFS Build Script - Chapter 9: System Configuration
# This script configures the system

set -e

echo "=== LFS Build - System Configuration ==="
echo "Starting at: $(date)"

# Create chroot script for Chapter 9
cat > $LFS/chroot-ch9.sh << 'CHROOT_EOF'
#!/bin/bash
set -e

echo "=== Inside Chroot - Chapter 9 ==="

export LFS=/mnt/lfs
export LC_ALL=POSIX

# 9.1 LFS-Bootscripts
echo ""
echo "=== Installing LFS-Bootscripts ==="
cd $LFS_SOURCES
tar xf lfs-bootscripts-20230728.tar.xz
cd lfs-bootscripts-20230728
make install
cd $LFS_SOURCES
rm -rf lfs-bootscripts-20230728

# 9.2 Udev Configuration
echo ""
echo "=== Configuring Udev ==="
cat > /etc/udev/rules.d/99-lfs.rules << "EOF"
# /etc/udev/rules.d/99-lfs.rules: Rule for udev
#
# These rules ensure correct device default naming and accessibility for LFS
#
SUBSYSTEM=="block", ENV{ID_SERIAL}!="", SYMLINK+="disk/by-id/[env{ID_BUS}]-[env{ID_SERIAL}]"
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="?*", ENV{MATCHIFTYPE}="1", KERNEL=="eth*", NAME="eth0"
EOF

# 9.3 Network Configuration
echo ""
echo "=== Configuring Network ==="
cd /etc/sysconfig/
cat > ifconfig.eth0 << "EOF"
ONBOOT=yes
IFACE=eth0
SERVICE=ipv4-static
IP=192.168.1.100
GATEWAY=192.168.1.1
PREFIX=24
BROADCAST=192.168.1.255
EOF

cat > network << "EOF"
# Begin /etc/sysconfig/network
HOSTNAME=lfs.example.com
GATEWAY=192.168.1.1
# End /etc/sysconfig/network
EOF

echo "192.168.1.100 lfs.example.com lfs" >> /etc/hosts

# 9.4 System V Bootscripts
echo ""
echo "=== Configuring System V Bootscripts ==="
cat > /etc/sysconfig/console << "EOF"
# Begin /etc/sysconfig/console
CHARMAP="UTF-8"
FONT="lat2-16 -m 8859-15"
# End /etc/sysconfig/console
EOF

cat > /etc/sysconfig/clock << "EOF"
# Begin /etc/sysconfig/clock
ZONE=UTC
UTC=1
ARC=0
# End /etc/sysconfig/clock
EOF

# 9.5 Bash Shell Startup Files
echo ""
echo "=== Configuring Bash Shell ==="
cat > /etc/profile << "EOF"
# Begin /etc/profile
export LANG=en_US.UTF-8
export PATH=/bin:/usr/bin
# End /etc/profile
EOF

cat > /etc/bashrc << "EOF"
# Begin /etc/bashrc
alias ll='ls -la'
alias l='ls -la'
export PS1='\[\e[32m\]\u@\h:\w\$ \[\e[0m\]'
# End /etc/bashrc
EOF

# 9.6 Inputrc
echo ""
echo "=== Configuring Inputrc ==="
cat > /etc/inputrc << "EOF"
# Begin /etc/inputrc
set input-meta on
set output-meta on
set convert-meta off
set horizontal-scroll-mode off
set bell-style none
set keymap vi
# End /etc/inputrc
EOF

# 9.7 Shells
echo ""
echo "=== Configuring Shells ==="
cat > /etc/shells << "EOF"
# Begin /etc/shells
/bin/sh
/bin/bash
# End /etc/shells
EOF

# Create essential directories
mkdir -p /dev/pts
mkdir -p /dev/shm

# Create /etc/fstab
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

echo ""
echo "=== System Configuration Complete ==="
echo "Next step: Run scripts/07-bootloader.sh"
CHROOT_EOF
chmod +x $LFS/chroot-ch9.sh

echo ""
echo "=== Chapter 9 Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Enter chroot: sudo $LFS/entreroot.sh"
echo "2. Inside chroot, run: /mnt/lfs/chroot-ch9.sh"
echo "3. Exit chroot: exit"
echo "4. Continue with: scripts/07-bootloader.sh"
