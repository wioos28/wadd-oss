#!/bin/bash
# LFS Build Script - Chapter 0: Host System Preparation
# This script prepares the host system for building LFS

set -e

echo "=== LFS Build - Host System Preparation ==="
echo "Starting at: $(date)"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root!"
    echo "Run as normal user with sudo privileges."
    exit 1
fi

# Create LFS directory
echo "[1/6] Creating LFS directory..."
export LFS=/mnt/lfs
sudo mkdir -p $LFS

# Check available disk space
echo "[2/6] Checking disk space..."
DF_OUTPUT=$(df -h $LFS | tail -1 | awk '{print $4}')
echo "Available space: $DF_OUTPUT"

# Install required packages
echo "[3/6] Installing required packages..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    bison \
    gawk \
    texinfo \
    python3 \
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
    network-manager

# Configure locale
echo "[4/6] Configuring locale..."
sudo locale-gen en_US.UTF-8
sudo update-locale LANG=en_US.UTF-8

# Create LFS user (optional, for security)
echo "[5/6] Creating lfs user..."
if ! id "lfs" &>/dev/null; then
    sudo useradd -m -s /bin/bash lfs
    sudo passwd lfs
    echo "User 'lfs' created. Set password when prompted."
fi

# Set ownership
echo "[6/6] Setting ownership..."
sudo chown -v lfs $LFS

echo ""
echo "=== Host preparation complete ==="
echo "Next step: Run scripts/01-download.sh as user 'lfs'"
echo ""
echo "To switch to lfs user:"
echo "  su - lfs"
echo ""
