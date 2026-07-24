#!/bin/bash
# LFS Optimization Script - Minimal RAM Usage + Beautiful UI
# Tối ưu hệ thống cho iPhone 11 / UTM SE

set -e

echo "=== LFS Optimization Script ==="
echo "Tối ưu: ít RAM + đẹp + đầy đủ tính năng"
echo "Starting at: $(date)"

# Create chroot optimization script
cat > $LFS/chroot-optimize.sh << 'CHROOT_EOF'
#!/bin/bash
set -e

echo "=== Inside Chroot - Optimization ==="

export LFS=/mnt/lfs
export LC_ALL=POSIX

# ============================================
# 1. KERNEL OPTIMIZATION - Minimal RAM
# ============================================
echo ""
echo "=== [1/8] Kernel Optimization ==="
cd /usr/src/linux

# Backup original config
cp .config .config.backup

# Create optimized minimal config
cat > .config << 'KERNEL_CONFIG'
# ============================================
# MINIMAL KERNEL FOR UTM SE - iPhone 11
# Tối ưu cho RAM thấp
# ============================================

# General setup
CONFIG_SYSVIPC=y
CONFIG_POSIX_MQUEUE=y
CONFIG_AUDIT=y
CONFIG_AUDITSYSCALL=y
CONFIG_NO_HZ_FULL=y
CONFIG_HIGH_RES_TIMERS=y
CONFIG_PREEMPT=y
CONFIG_HZ_1000=y

# Processor
CONFIG_X86_64=y
CONFIG_SMP=y
CONFIG_NR_CPUS=2
CONFIG_HOTPLUG_CPU=y

# Power management
CONFIG_PM=y
CONFIG_PM_SLEEP=y
CONFIG_PM_ADVANCED_DEBUG=y
CONFIG_CPU_FREQ_DEFAULT_GOV_POWERSAVE=y
CONFIG_CPU_FREQ_DEFAULT_GOV_SCHEDUTIL=y

# Modules
CONFIG_MODULES=y
CONFIG_MODULE_UNLOAD=y
CONFIG_MODULE_FORCE_UNLOAD=y

# Block devices
CONFIG_BLK_DEV_LOOP=y
CONFIG_BLK_DEV_RAM=y
CONFIG_BLK_DEV_RAM_SIZE=65536

# Networking
CONFIG_NET=y
CONFIG_INET=y
CONFIG_IPV6=y
CONFIG_NETFILTER=y
CONFIG_BRIDGE=y
CONFIG_VLAN_8021Q=y

# File systems
CONFIG_EXT2_FS=y
CONFIG_EXT3_FS=y
CONFIG_EXT4_FS=y
CONFIG_BTRFS_FS=m
CONFIG_XFS_FS=m
CONFIG_F2FS_FS=m
CONFIG_VFAT_FS=y
CONFIG_NTFS_FS=y
CONFIG_TMPFS=y
CONFIG_TMPFS_POSIX_ACL=y
CONFIG_TMPFS_XATTR=y
CONFIG_SQUASHFS=m
CONFIG_ISO9660_FS=y
CONFIG_UDF_FS=m

# CD-ROM/DVD
CONFIG_BLK_DEV_SR=y
CONFIG_BLK_DEV_SD=y

# Input
CONFIG_INPUT_EVDEV=m
CONFIG_INPUT_UINPUT=m
CONFIG_SERIO_I8042=m
CONFIG_SERIO=m
CONFIG_VT=y
CONFIG_VT_CONSOLE=y
CONFIG_VT_HW_CONSOLE_BINDING=y
CONFIG_UNIX98_PTYS=y
CONFIG_DEVPTS_MULTIPLE_INSTANCES=y

# Graphics
CONFIG_DRM=y
CONFIG_DRM_VBOXVIDEO=m
CONFIG_DRM_BOCHS=m
CONFIG_DRM_CIRRUS_QEMU=m
CONFIG_FB=y
CONFIG_FB_VESA=y
CONFIG_FB_EFI=y
CONFIG_FRAMEBUFFER_CONSOLE=y
CONFIG_FRAMEBUFFER_CONSOLE_DEFERRED_TAKEOVER=y
CONFIG_LOGO=y
CONFIG_LOGO_LINUX_MONO=y
CONFIG_LOGO_LINUX_VGA16=y
CONFIG_LOGO_LINUX_CLUT224=y
CONFIG_FONT_SUPPORT=y
CONFIG_CONSOLE_TRANSLATIONS=y
CONFIG_VT_CONSOLE_SLEEP=y
CONFIG_HW_CONSOLE=y

# Sound
CONFIG_SOUND=y
CONFIG_SND=y
CONFIG_SND_HDA_INTEL=m
CONFIG_SND_HDA_CODEC_HDMI=m
CONFIG_SND_HDA_CODEC_REALTEK=m
CONFIG_SND_HDA_GENERIC=m

# USB
CONFIG_USB=y
CONFIG_USB_XHCI_HCD=m
CONFIG_USB_EHCI_HCD=m
CONFIG_USB_OHCI_HCD=m
CONFIG_USB_STORAGE=m
CONFIG_USB_HID=m
CONFIG_HID_GENERIC=m
CONFIG_HID_APPLE=m

# Network devices
CONFIG_ETHERNET=y
CONFIG_NET_VENDOR_INTEL=y
CONFIG_E1000=y
CONFIG_E1000E=y
CONFIG_VIRTIO_NET=m
CONFIG_VIRTIO_PCI=m
CONFIG_VIRTIO_BLK=m
CONFIG_VIRTIO_CONSOLE=m
CONFIG_VIRTIO=m
CONFIG_VIRTIO_MMIO=m

# SCSI
CONFIG_SCSI=y
CONFIG_BLK_DEV_SD=y
CONFIG_CHR_DEV_SG=y
CONFIG_SCSI_VIRTIO=m

# Sound
CONFIG_SOUND=y
CONFIG_SND=y
CONFIG_SND_HDA_INTEL=m
CONFIG_SND_HDA_CODEC_HDMI=m

# Virtualization support
CONFIG_KVM=m
CONFIG_KVM_INTEL=m
CONFIG_KVM_AMD=m
CONFIG_VHOST_NET=m

# Security
CONFIG_SECURITY=y
CONFIG_SECURITY_APPARMOR=m

# Crypto
CONFIG_CRYPTO=y
CONFIG_CRYPTO_AES=y
CONFIG_CRYPTO_SHA256=y

# Power management
CONFIG_PM=y
CONFIG_PM_SLEEP=y
CONFIG_SUSPEND=y
CONFIG_HIBERNATION=n
CONFIG_CPU_FREQ=y
CONFIG_CPU_FREQ_DEFAULT_GOV_SCHEDUTIL=y

# Memory optimization
CONFIG_ZSWAP=y
CONFIG_ZSWAP_COMPRESSOR_DEFAULT_LZO=y
CONFIG_ZSWAP_ZPOOL_DEFAULT_Z3FOLD=y
CONFIG_ZRAM=y
CONFIG_ZRAM_DEF_COMPRESSOR_LZ4=y
CONFIG_LZO_COMPRESS=y
CONFIG_LZ4_COMPRESS=y
CONFIG_ZSTD_COMPRESS=y

# Cgroup
CONFIG_CGROUPS=y
CONFIG_CGROUP_FREEZER=y
CONFIG_CGROUP_DEVICE=y
CONFIG_CPUSETS=y
CONFIG_CGROUP_CPUACCT=y
CONFIG_MEMCG=y

# Namespaces
CONFIG_NAMESPACES=y
CONFIG_UTS_NS=y
CONFIG_IPC_NS=y
CONFIG_USER_NS=y
CONFIG_PID_NS=y
CONFIG_NET_NS=y

# Disable unused features
CONFIG_IP6_NF_IPTABLES=m
CONFIG_IP6_NF_FILTER=m
CONFIG_IP6_NF_MANGLE=m
CONFIG_IP6_NF_NAT=m
CONFIG_NF_NAT_IPV4=m
CONFIG_IP_NF_IPTABLES=m
CONFIG_IP_NF_FILTER=m
CONFIG_IP_NF_NAT=m
CONFIG_IP_NF_MANGLE=m

# Wireless
CONFIG_WLAN=y
CONFIG_WLAN_VENDOR_INTEL=y

# Misc
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
KERNEL_CONFIG

# Build optimized kernel
make olddefconfig
make -j$(nproc)
make modules_install
cp arch/x86/boot/bzImage /boot/vmlinuz-6.4.12-lfs-optimized
cp System.map /boot/System.map-6.4.12-optimized
cp .config /boot/config-6.4.12-optimized

echo "[OK] Kernel optimized for minimal RAM"

# ============================================
# 2. SWAP & ZRAM - Extended Memory
# ============================================
echo ""
echo "=== [2/8] Swap & ZRAM Setup ==="

# Create swap file
dd if=/dev/zero of=/swapfile bs=1M count=512
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Configure zram
cat > /etc/systemd/system/zram.service << 'EOF'
[Unit]
Description=ZRAM Compression
After=local-fs.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'echo 512M > /sys/block/zram0/disksize'
ExecStart=/sbin/mkswap /dev/zram0
ExecStart=/sbin/swapon -p 100 /dev/zram0

[Install]
WantedBy=multi-user.target
EOF

echo "[OK] Swap & ZRAM configured"

# ============================================
# 3. LIGHTWEIGHT DESKTOP - LXDE + Theming
# ============================================
echo ""
echo "=== [3/8] Lightweight Desktop (LXDE) ==="

# Install LXDE (lightweight desktop)
apt-get update
apt-get install -y \
    lxde-core \
    lxde \
    openbox \
    pcmanfm \
    lxtask \
    lxappearance \
    lxinput \
    lxrandr \
    lxterminal \
    leafpad \
    xorg \
    xserver-xorg \
    xinit \
    x11-xserver-utils \
    xfonts-base \
    xfonts-100dpi \
    xfonts-75dpi \
    xfonts-cyrillic \
    fontconfig \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto \
    fonts-ubuntu \
    fonts-freefont-ttf \
    gtk2-engines-murrine \
    gtk2-engines-pixbuf \
    arc-theme \
    numix-gtk-theme \
    numix-icon-theme \
    papirus-icon-theme \
    breeze-cursor-theme \
    lightdm \
    lightdm-gtk-greeter \
    lightdm-gtk-greeter-settings

echo "[OK] LXDE desktop installed"

# ============================================
# 4. BEAUTIFUL THEMING
# ============================================
echo ""
echo "=== [4/8] Beautiful Theming ==="

# Create beautiful theme
mkdir -p /usr/share/themes/LFS-Theme/gtk-2.0
mkdir -p /usr/share/themes/LFS-Theme/gtk-3.0
mkdir -p /usr/share/icons/LFS-Theme

# GTK2 Theme
cat > /usr/share/themes/LFS-Theme/gtk-2.0/gtkrc << 'GTK2'
# LFS Theme - Dark & Beautiful
gtk-theme-name="LFS-Theme"
gtk-icon-theme-name="Papirus-Dark"
gtk-cursor-theme-name="Breeze"
gtk-cursor-theme-size=24
gtk-toolbar-style=GTK_TOOLBAR_BOTH_HORIZ
gtk-toolbar-icon-size=GTK_ICON_SIZE_LARGE_TOOLBAR
gtk-button-images=1
gtk-menu-images=1
gtk-enable-event-sounds=1
gtk-enable-input-feedback-sounds=1
gtk-xft-antialias=1
gtk-xft-hinting=1
gtk-xft-hintstyle="hintfull"
gtk-xft-rgba="rgb"
GTK2_EOF

# Create dark theme
cat > /usr/share/themes/LFS-Theme/gtk-3.0/gtk.css << 'CSS'
/* LFS Dark Theme */
@import url("resource:///org/gtk/libgtk/theme/Adwaita-dark/index.css");

headerbar,
headerbar.titlebar {
    background-color: #2d2d2d;
    color: #ffffff;
}

button {
    background-color: #4a4a4a;
    color: #ffffff;
    border-radius: 4px;
}

button:hover {
    background-color: #5a5a5a;
}

button:active {
    background-color: #3a3a3a;
}

entry {
    background-color: #3a3a3a;
    color: #ffffff;
    border-radius: 4px;
}

textview text {
    background-color: #1e1e1e;
    color: #d4d4d4;
}

scrollbar {
    background-color: #2d2d2d;
}

scrollbar slider {
    background-color: #5a5a5a;
    border-radius: 4px;
}

notebook tab {
    background-color: #3a3a3a;
    color: #ffffff;
}

notebook tab:checked {
    background-color: #4a4a4a;
}

sidebar {
    background-color: #2d2d2d;
}

.sidebar row:selected {
    background-color: #4a90d9;
}

CSS

echo "[OK] Theme configured"

# ============================================
# 5. WALLPAPERS & ICONS
# ============================================
echo ""
echo "=== [5/8] Wallpapers & Icons ==="

# Create beautiful wallpaper
mkdir -p /usr/share/backgrounds

# Create gradient wallpaper with ImageMagick
apt-get install -y imagemagick

convert -size 1920x1080 \
    gradient:'#1a1a2e'-'#16213e' \
    -fill '#0f3460' -draw "rectangle 0,900 1920,1080" \
    -fill '#e94560' -draw "circle 960,540 960,560" \
    /usr/share/backgrounds/lfs-wallpaper.png

# Set wallpaper
mkdir -p /home/lfs/.config/pcmanfm/LXDE
cat > /home/lfs/.config/pcmanfm/LXDE/pcmanfm.conf << 'WALLPAPER'
[desktop]
wallpaper_mode=stretch
wallpaper_common=1
wallpaper=/usr/share/backgrounds/lfs-wallpaper.png
desktop_bg=#1a1a2e
desktop_fg=#ffffff
desktop_shadow=#000000
show_wm_menu=0
sort=mtime
ascending=0
show_documents=0
show_trash=1
show_mounts=1
WALLPAPER

echo "[OK] Wallpaper configured"

# ============================================
# 6. POWERFUL TERMINAL
# ============================================
echo ""
echo "=== [6/8] Terminal Setup ==="

# Install modern terminal
apt-get install -y \
    alacritty \
    kitty \
    tilix

# Configure Alacritty
mkdir -p /home/lfs/.config/alacritty
cat > /home/lfs/.config/alacritty/alacritty.toml << 'ALACRITTY'
# Alacritty Configuration - Beautiful & Fast

[window]
padding = { x = 10, y = 10 }
dynamic_padding = true
decorations = "Full"
opacity = 0.95
blur = true

[scrolling]
history = 10000

[font]
size = 12.0

[font.normal]
family = "JetBrains Mono"
style = "Regular"

[font.bold]
family = "JetBrains Mono"
style = "Bold"

[font.italic]
family = "JetBrains Mono"
style = "Italic"

[colors.primary]
background = "#1e1e2e"
foreground = "#cdd6f4"

[colors.cursor]
text = "#1e1e2e"
cursor = "#f5e0dc"

[colors.vi_mode_cursor]
text = "#1e1e2e"
cursor = "#b4befe"

[colors.selection]
text = "#1e1e2e"
background = "#f5e0dc"

[colors.normal]
black = "#45475a"
red = "#f38ba8"
green = "#a6e3a1"
yellow = "#f9e2af"
blue = "#89b4fa"
magenta = "#f5c2e7"
cyan = "#94e2d5"
white = "#bac2de"

[colors.bright]
black = "#585b70"
red = "#f38ba8"
green = "#a6e3a1"
yellow = "#f9e2af"
blue = "#89b4fa"
magenta = "#f5c2e7"
cyan = "#94e2d5"
white = "#a6adc8"

[cursor]
style = { shape = "Block", blinking = "On" }

[mouse]
hide_when_typing = true
ALACRITTY

echo "[OK] Terminal configured"

# ============================================
# 7. APP STORE - Like Ubuntu Software Center
# ============================================
echo ""
echo "=== [7/8] App Store (Like Ubuntu) ==="

# Install package management
apt-get install -y \
    synaptic \
    software-properties-common \
    apt-transport-https \
    gpg \
    curl \
    wget

# Create LFS App Store (like Ubuntu Software Center)
mkdir -p /usr/share/applications
mkdir -p /opt/lfs-appstore

# Create App Store launcher
cat > /usr/share/applications/lfs-appstore.desktop << 'DESKTOP'
[Desktop Entry]
Name=LFS App Store
Comment=Install applications like Ubuntu
Exec=sudo synaptic
Icon=system-software-install
Terminal=false
Type=Application
Categories=System;PackageManager;
StartupNotify=true
DESKTOP

# Create app categories
mkdir -p /usr/share/applications/{accessories,education,games,graphics,internet,multimedia,office,programming,system,utilities}

# Create app installer script
cat > /usr/local/bin/lfs-app-install << 'INSTALLER'
#!/bin/bash
# LFS App Installer - Like Ubuntu Software Center

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           LFS App Store - Like Ubuntu                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Available apps:"
echo ""
echo "=== Browsers ==="
echo "  1. firefox          - Mozilla Firefox"
echo "  2. chromium         - Chromium Browser"
echo "  3. brave            - Brave Browser"
echo ""
echo "=== Development ==="
echo "  4. code             - Visual Studio Code"
echo "  5. vim              - Vim Editor"
echo "  6. neovim           - Neovim Editor"
echo "  7. git              - Git Version Control"
echo "  8. nodejs           - Node.js Runtime"
echo "  9. python3          - Python 3"
echo "  10. rust            - Rust Language"
echo "  11. go              - Go Language"
echo "  12. java            - Java JDK"
echo ""
echo "=== Graphics ==="
echo "  13. gimp            - GIMP Image Editor"
echo "  14. inkscape        - Inkscape Vector Graphics"
echo "  15. blender         - Blender 3D"
echo "  16. imagemagick     - ImageMagick"
echo ""
echo "=== Multimedia ==="
echo "  17. vlc             - VLC Media Player"
echo "  18. mpv             - MPV Media Player"
echo "  19. obs-studio      - OBS Studio"
echo "  20. audacity        - Audacity Audio Editor"
echo ""
echo "=== Office ==="
echo "  21. libreoffice     - LibreOffice Suite"
echo "  22. thunderbird     - Thunderbird Email"
echo "  23. evince          - Evince PDF Viewer"
echo ""
echo "=== System ==="
echo "  24. htop            - System Monitor"
echo "  25. gparted         - Partition Editor"
echo "  26. file-roller     - Archive Manager"
echo "  27. neofetch        - System Info"
echo ""
echo "=== Games ==="
echo "  28. steam           - Steam Gaming"
echo "  29. lutris          - Lutris Game Manager"
echo "  30. retroarch       - RetroArch Emulator"
echo ""
echo "=== Communication ==="
echo "  31. discord         - Discord"
echo "  32. telegram        - Telegram Desktop"
echo "  33. slack           - Slack"
echo ""
echo "=========================================="
echo ""
read -p "Enter app number (or name): " choice

case $choice in
    1|firefox) sudo apt-get install -y firefox ;;
    2|chromium) sudo apt-get install -y chromium-browser ;;
    3|brave) 
        sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
        echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list
        sudo apt-get update
        sudo apt-get install -y brave-browser
        ;;
    4|code) 
        wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
        sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/
        echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
        sudo apt-get update
        sudo apt-get install -y code
        ;;
    5|vim) sudo apt-get install -y vim ;;
    6|neovim) sudo apt-get install -y neovim ;;
    7|git) sudo apt-get install -y git ;;
    8|nodejs) 
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        ;;
    9|python3) sudo apt-get install -y python3 python3-pip ;;
    10|rust) curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y ;;
    11|go) 
        wget -q https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
        sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
        echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile.d/go.sh
        ;;
    12|java) sudo apt-get install -y openjdk-17-jdk ;;
    13|gimp) sudo apt-get install -y gimp ;;
    14|inkscape) sudo apt-get install -y inkscape ;;
    15|blender) sudo apt-get install -y blender ;;
    16|imagemagick) sudo apt-get install -y imagemagick ;;
    17|vlc) sudo apt-get install -y vlc ;;
    18|mpv) sudo apt-get install -y mpv ;;
    19|obs-studio) sudo apt-get install -y obs-studio ;;
    20|audacity) sudo apt-get install -y audacity ;;
    21|libreoffice) sudo apt-get install -y libreoffice ;;
    22|thunderbird) sudo apt-get install -y thunderbird ;;
    23|evince) sudo apt-get install -y evince ;;
    24|htop) sudo apt-get install -y htop ;;
    25|gparted) sudo apt-get install -y gparted ;;
    26|file-roller) sudo apt-get install -y file-roller ;;
    27|neofetch) sudo apt-get install -y neofetch ;;
    28|steam) 
        sudo dpkg --add-architecture i386
        sudo apt-get update
        sudo apt-get install -y steam
        ;;
    29|lutris) sudo apt-get install -y lutris ;;
    30|retroarch) sudo apt-get install -y retroarch ;;
    31|discord) sudo apt-get install -y discord ;;
    32|telegram) sudo apt-get install -y telegram-desktop ;;
    33|slack) sudo apt-get install -y slack-desktop ;;
    *) 
        echo "Installing: $choice"
        sudo apt-get install -y $choice
        ;;
esac

echo ""
echo "Installation complete!"
INSTALLER
chmod +x /usr/local/bin/lfs-app-install

echo "[OK] App Store created"

# ============================================
# 8. PERFORMANCE TWEAKS
# ============================================
echo ""
echo "=== [8/8] Performance Tweaks ==="

# Optimize sysctl
cat > /etc/sysctl.d/99-lfs-optimized.conf << 'SYSCTL'
# LFS Optimized Settings for Minimal RAM

# Virtual memory
vm.swappiness=10
vm.dirty_ratio=15
vm.dirty_background_ratio=5
vm.vfs_cache_pressure=50
vm.min_free_kbytes=64
vm.overcommit_memory=1
vm.overcommit_ratio=50

# Network
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr
net.core.default_qdisc=fq

# File system
fs.file-max=2097152
fs.inotify.max_user_watches=524288

# Kernel
kernel.pid_max=4194304
SYSCTL

sysctl -p /etc/sysctl.d/99-lfs-optimized.conf

# Create systemd service for auto-start desktop
cat > /etc/systemd/system/autologin@.service << 'AUTOLOGIN'
[Unit]
Description=Automatic Login
After=systemd-user-sessions.service

[Service]
ExecStart=-/sbin/agetty --autologin %I -o '-p -f lfs' %I tty7 linux
Type=idle

[Install]
WantedBy=multi-user.target
AUTOLOGIN

# Optimize services
systemctl set-default graphical.target
systemctl mask tmp.mount
systemctl mask systemd-modules-load.service

echo "[OK] Performance optimized"

echo ""
echo "=== Optimization Complete ==="
echo "System optimized for:"
echo "  - Minimal RAM usage"
echo "  - Beautiful LXDE desktop"
echo "  - App Store (like Ubuntu)"
echo "  - Full development tools"
echo ""
CHROOT_EOF
chmod +x $LFS/chroot-optimize.sh

echo ""
echo "=== Optimization Script Ready ==="
echo ""
echo "Next steps:"
echo "1. Enter chroot: sudo $LFS/entreroot.sh"
echo "2. Run optimization: /mnt/lfs/chroot-optimize.sh"
echo "3. Exit chroot: exit"
echo ""
