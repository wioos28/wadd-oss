#!/bin/bash
# LFS Desktop Setup - Beautiful UI with Minimal Resources
# Cài đặt desktop đẹp, nhẹ, đầy đủ tính năng

set -e

echo "=== LFS Desktop Setup ==="
echo "Beautiful UI + Minimal RAM"

# Create chroot desktop script
cat > $LFS/chroot-desktop.sh << 'CHROOT_EOF'
#!/bin/bash
set -e

echo "=== Inside Chroot - Desktop Setup ==="

export LFS=/mnt/lfs
export LC_ALL=POSIX

# ============================================
# 1. INSTALL DESKTOP ENVIRONMENT
# ============================================
echo ""
echo "=== [1/6] Installing LXDE Desktop ==="

apt-get update
apt-get install -y \
    xorg \
    lxde-core \
    lxde \
    lightdm \
    lightdm-gtk-greeter \
    lightdm-gtk-greeter-settings \
    openbox \
    pcmanfm \
    lxtask \
    lxappearance \
    lxinput \
    lxrandr \
    lxterminal \
    leafpad \
    xinit \
    x11-xserver-utils \
    xfonts-base \
    xfonts-100dpi \
    xfonts-75dpi \
    xfonts-cyrillic

echo "[OK] LXDE installed"

# ============================================
# 2. INSTALL BEAUTIFUL THEMES
# ============================================
echo ""
echo "=== [2/6] Installing Beautiful Themes ==="

apt-get install -y \
    arc-theme \
    numix-gtk-theme \
    numix-icon-theme \
    papirus-icon-theme \
    breeze-cursor-theme \
    gnome-themes-standard \
    gtk2-engines-murrine \
    gtk2-engines-pixbuf \
    adwaita-icon-theme

# Create custom LFS theme
mkdir -p /usr/share/themes/LFS-Dark/gtk-2.0
mkdir -p /usr/share/themes/LFS-Dark/gtk-3.0

cat > /usr/share/themes/LFS-Dark/gtk-2.0/gtkrc << 'GTK2'
gtk-theme-name="Arc-Dark"
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
GTK2

echo "[OK] Themes installed"

# ============================================
# 3. INSTALL FONTS
# ============================================
echo ""
echo "=== [3/6] Installing Beautiful Fonts ==="

apt-get install -y \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto \
    fonts-ubuntu \
    fonts-freefont-ttf \
    fonts-freefont-otf \
    fonts-noto-color-emoji \
    fonts-font-awesome \
    fonts-powerline

# Install JetBrains Mono
mkdir -p /usr/share/fonts/truetype/jetbrains
cd /tmp
wget -q https://github.com/JetBrains/JetBrainsMono/releases/download/v2.242/JetBrainsMono-2.242.zip
unzip -q JetBrainsMono-2.242.zip -d jetbrains
cp jetbrains/fonts/ttf/*.ttf /usr/share/fonts/truetype/jetbrains/
fc-cache -fv

echo "[OK] Fonts installed"

# ============================================
# 4. INSTALL MODERN TERMINAL
# ============================================
echo ""
echo "=== [4/6] Installing Modern Terminals ==="

apt-get install -y \
    alacritty \
    kitty \
    tilix \
    guake \
    terminator

# Configure Alacritty
mkdir -p /home/lfs/.config/alacritty
cat > /home/lfs/.config/alacritty/alacritty.toml << 'ALACRITTY'
# Alacritty - Beautiful & Fast Terminal

[window]
padding = { x = 12, y = 12 }
dynamic_padding = true
decorations = "Full"
opacity = 0.92
blur = true

[scrolling]
history = 50000

[font]
size = 13.0

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

[colors.selection]
text = "#1e1e2e"
background = "#585b70"

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
ALACRITTY

echo "[OK] Terminals installed"

# ============================================
# 5. INSTALL WALLPAPERS
# ============================================
echo ""
echo "=== [5/6] Setting up Wallpapers ==="

apt-get install -y imagemagick

mkdir -p /usr/share/backgrounds

# Create beautiful gradient wallpapers
convert -size 1920x1080 \
    gradient:'#0f0c29'-'#302b63' \
    -fill '#24243e' -draw "rectangle 0,800 1920,1080" \
    /usr/share/backgrounds/lfs-dark.png

convert -size 1920x1080 \
    gradient:'#141e30'-'#243b55' \
    /usr/share/backgrounds/lfs-blue.png

convert -size 1920x1080 \
    gradient:'#232526'-'#414345' \
    /usr/share/backgrounds/lfs-gray.png

convert -size 1920x1080 \
    gradient:'#0f2027'-'#2c5364' \
    /usr/share/backgrounds/lfs-teal.png

# Create wallpaper selector
cat > /usr/local/bin/lfs-wallpaper << 'WALLPAPER'
#!/bin/bash
echo "Select wallpaper:"
echo "1. Dark (default)"
echo "2. Blue"
echo "3. Gray"
echo "4. Teal"
read -p "Choice: " choice

case $choice in
    1) wp="/usr/share/backgrounds/lfs-dark.png" ;;
    2) wp="/usr/share/backgrounds/lfs-blue.png" ;;
    3) wp="/usr/share/backgrounds/lfs-gray.png" ;;
    4) wp="/usr/share/backgrounds/lfs-teal.png" ;;
    *) wp="/usr/share/backgrounds/lfs-dark.png" ;;
esac

pcmanfm --set-wallpaper=$wp --wallpaper-mode=fit
WALLPAPER
chmod +x /usr/local/bin/lfs-wallpaper

echo "[OK] Wallpapers configured"

# ============================================
# 6. CONFIGURE LIGHTDM
# ============================================
echo ""
echo "=== [6/6] Configuring LightDM ==="

# Configure LightDM
cat > /etc/lightdm/lightdm.conf << 'LIGHTDM'
[Seat:*]
autologin-user=lfs
autologin-user-timeout=0
user-session=lxde
greeter-session=lightdm-gtk-greeter

[Greeter]
theme-name=Arc-Dark
icon-theme-name=Papirus-Dark
font-name=Noto Sans 11
cursor-theme-name=Breeze
cursor-theme-size=24
LIGHTDM

# Configure LightDM greeter
cat > /etc/lightdm/lightdm-gtk-greeter.conf << 'GREETER'
[greeter]
theme-name=Arc-Dark
icon-theme-name=Papirus-Dark
font-name=Noto Sans 11
cursor-theme-name=Breeze
cursor-theme-size=24
background=/usr/share/backgrounds/lfs-dark.png
user-background=/usr/share/backgrounds/lfs-dark.png
position=50%,center
default-user-image=/usr/share/icons/default-user.png
GREETER

echo "[OK] LightDM configured"

# ============================================
# 7. CREATE DESKTOP SHORTCUTS
# ============================================
echo ""
echo "=== [7/7] Creating Desktop Shortcuts ==="

mkdir -p /home/lfs/Desktop

# Create app launcher
cat > /home/lfs/Desktop/App-Store.desktop << 'DESKTOP'
[Desktop Entry]
Name=App Store
Comment=Install applications
Exec=lfs-app-install
Icon=system-software-install
Terminal=true
Type=Application
Categories=System;
DESKTOP

# Create terminal shortcut
cat > /home/lfs/Desktop/Terminal.desktop << 'DESKTOP'
[Desktop Entry]
Name=Terminal
Comment=Open Terminal
Exec=alacritty
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=System;TerminalEmulator;
DESKTOP

# Create file manager
cat > /home/lfs/Desktop/Files.desktop << 'DESKTOP'
[Desktop Entry]
Name=Files
Comment=File Manager
Exec=pcmanfm
Icon=system-file-manager
Terminal=false
Type=Application
Categories=System;FileManager;
DESKTOP

# Create browser
cat > /home/lfs/Desktop/Firefox.desktop << 'DESKTOP'
[Desktop Entry]
Name=Firefox
Comment=Web Browser
Exec=firefox
Icon=firefox
Terminal=false
Type=Application
Categories=Network;WebBrowser;
DESKTOP

chmod +x /home/lfs/Desktop/*.desktop

echo "[OK] Desktop shortcuts created"

echo ""
echo "=== Desktop Setup Complete ==="
echo ""
echo "Features:"
echo "  - LXDE Desktop (lightweight)"
echo "  - Arc-Dark Theme (beautiful)"
echo "  - Papirus Icons"
echo "  - JetBrains Mono Font"
echo "  - Alacritty Terminal (fast)"
echo "  - Beautiful Wallpapers"
echo "  - App Store (like Ubuntu)"
echo ""
CHROOT_EOF
chmod +x $LFS/chroot-desktop.sh

echo ""
echo "=== Desktop Setup Script Ready ==="
echo ""
echo "Next steps:"
echo "1. Enter chroot: sudo $LFS/entreroot.sh"
echo "2. Run desktop setup: /mnt/lfs/chroot-desktop.sh"
echo "3. Exit chroot: exit"
echo ""
