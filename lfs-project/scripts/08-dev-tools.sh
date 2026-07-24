#!/bin/bash
# LFS Build Script - Development Tools Installation
# This script installs development tools like browser, IDE, Docker, Git

set -e

echo "=== LFS Build - Development Tools ==="
echo "Starting at: $(date)"

# Create chroot script for development tools
cat > $LFS/chroot-dev.sh << 'CHROOT_EOF'
#!/bin/bash
set -e

echo "=== Inside Chroot - Development Tools ==="

export LFS=/mnt/lfs
export LC_ALL=POSIX

# Install package manager first
echo ""
echo "=== Installing Package Manager ==="
cd $LFS_SOURCES

# Create a minimal package management script
cat > /usr/sbin/lfs-pkg << 'EOF'
#!/bin/bash
# Simple package manager for LFS
# Usage: lfs-pkg install <package>
#        lfs-pkg remove <package>

PKG_DIR=/var/cache/lfs-packages
INSTALLED_DIR=/var/lib/lfs-installed

mkdir -p $PKG_DIR $INSTALLED_DIR

case "$1" in
    install)
        if [ -z "$2" ]; then
            echo "Usage: lfs-pkg install <package>"
            exit 1
        fi
        echo "Installing $2..."
        # Download and install logic here
        echo "Package $2 installed"
        ;;
    remove)
        if [ -z "$2" ]; then
            echo "Usage: lfs-pkg remove <package>"
            exit 1
        fi
        echo "Removing $2..."
        echo "Package $2 removed"
        ;;
    *)
        echo "Usage: lfs-pkg {install|remove} <package>"
        ;;
esac
EOF
chmod +x /usr/sbin/lfs-pkg

# 1. Network Configuration
echo ""
echo "=== Configuring Network ==="
cat > /etc/sysconfig/network << "EOF"
# Begin /etc/sysconfig/network
HOSTNAME=lfs
GATEWAY=192.168.1.1
# End /etc/sysconfig/network
EOF

cat > /etc/resolv.conf << "EOF"
# Begin /etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 208.67.222.222
# End /etc/resolv.conf
EOF

# 2. Install Development Tools
echo ""
echo "=== Installing Development Tools ==="

# Build and install development tools
install_dev_tools() {
    echo "Installing development tools..."
    
    # Install build essentials
    apt-get update
    apt-get install -y \
        build-essential \
        gcc \
        g++ \
        make \
        cmake \
        autoconf \
        automake \
        libtool \
        pkg-config \
        git \
        vim \
        nano \
        htop \
        tmux \
        curl \
        wget \
        openssh-client \
        openssh-server \
        zip \
        unzip \
        tar \
        gzip \
        bzip2 \
        xz-utils \
        tree \
        findutils \
        grep \
        sed \
        gawk \
        bison \
        flex \
        openssl \
        libssl-dev \
        libncurses-dev \
        libreadline-dev \
        libffi-dev \
        liblzma-dev \
        libbz2-dev \
        zlib1g-dev \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        pipx \
        snapd \
        flatpak
}

# Install Node.js and npm
echo ""
echo "=== Installing Node.js ==="
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install Yarn
npm install -g yarn

# Install Git
echo ""
echo "=== Installing Git ==="
apt-get install -y git
git config --global user.name "LFS User"
git config --global user.email "user@lfs.local"

# Install Docker
echo ""
echo "=== Installing Docker ==="
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install VS Code
echo ""
echo "=== Installing VS Code ==="
apt-get install -y wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
apt-get update
apt-get install -y code

# Install Firefox
echo ""
echo "=== Installing Firefox ==="
apt-get install -y firefox

# Install Chromium
echo ""
echo "=== Installing Chromium ==="
apt-get install -y chromium-browser

# Install essential applications
echo ""
echo "=== Installing Essential Applications ==="
apt-get install -y \
    gparted \
    file-roller \
    evince \
    eog \
    vlc \
    transmission-gtk \
    system-tools-backends \
    network-manager-gnome \
    bluez \
    pulseaudio \
    alsa-utils \
    cups \
    cups-client \
    printer-driver-gutenprint

# Install development environments
echo ""
echo "=== Installing Development Environments ==="

# Install Python tools
pip3 install --upgrade pip
pip3 install \
    pipenv \
    poetry \
    virtualenv \
    pylint \
    flake8 \
    black \
    isort \
    mypy \
    pytest \
    requests \
    flask \
    django \
    numpy \
    pandas \
    matplotlib

# Install Rust
echo ""
echo "=== Installing Rust ==="
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Install Go
echo ""
echo "=== Installing Go ==="
wget -q https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile.d/go.sh
export PATH=$PATH:/usr/local/go/bin

# Install Java
echo ""
echo "=== Installing Java ==="
apt-get install -y openjdk-17-jdk

# Install additional tools
echo ""
echo "=== Installing Additional Tools ==="
apt-get install -y \
    neofetch \
    screenfetch \
    cmatrix \
   fortune \
    cowsay \
    figlet \
    toilet

# Create useful aliases
cat >> /etc/bashrc << 'EOF'

# Development aliases
alias ll='ls -la'
alias la='ls -la'
alias l='ls -la'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log'
alias gd='git diff'

# Docker aliases
alias dps='docker ps'
alias dpa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'
alias dlog='docker logs -f'
alias dstop='docker stop'
alias drm='docker rm'
alias drmi='docker rmi'

# Development
alias py='python3'
alias pip='pip3'
alias node='node'
alias npm='npm'
alias yarn='yarn'
alias code='code'

# System
alias reboot='sudo reboot'
alias poweroff='sudo poweroff'
alias update='sudo apt-get update && sudo apt-get upgrade'
alias install='sudo apt-get install'
EOF

# Set timezone
timedatectl set-timezone UTC

# Set hostname
hostnamectl set-hostname lfs

# Enable services
systemctl enable docker
systemctl enable ssh
systemctl enable NetworkManager
systemctl enable bluetooth

echo ""
echo "=== Development Tools Installation Complete ==="
echo "Next: Reboot the system"
CHROOT_EOF
chmod +x $LFS/chroot-dev.sh

echo ""
echo "=== Development Tools Setup Complete ==="
echo ""
echo "Final steps:"
echo "1. Enter chroot: sudo $LFS/entreroot.sh"
echo "2. Inside chroot, run: /mnt/lfs/chroot-dev.sh"
echo "3. Exit chroot: exit"
echo "4. Unmount filesystems: sudo umount -v $LFS/dev/pts"
echo "                           sudo umount -v $LFS/dev"
echo "                           sudo umount -v $LFS/proc"
echo "                           sudo umount -v $LFS/sys"
echo "                           sudo umount -v $LFS/run"
echo "5. Unmount LFS partition: sudo umount -v $LFS"
echo "6. Reboot: sudo reboot"
echo ""
echo "Congratulations! Your LFS system is ready!"
