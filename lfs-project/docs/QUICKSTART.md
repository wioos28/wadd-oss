# Quick Start Guide

## Overview

This guide will help you build a custom Linux system from source using Linux From Scratch (LFS). The system is optimized for running on UTM SE (QEMU) and includes development tools.

## Prerequisites

- Linux host system (Ubuntu/Debian recommended)
- At least 10GB free disk space
- 2GB+ RAM recommended
- Internet connection
- Basic knowledge of Linux commands

## Step-by-Step Instructions

### 1. Clone/Download the Project

```bash
cd /path/to/your/workspace
git clone <repository-url> lfs-project
cd lfs-project
chmod +x scripts/*.sh
chmod +x build.sh
```

### 2. Prepare the Host System

This script installs required packages and creates the LFS user:

```bash
sudo ./scripts/00-host-prep.sh
```

### 3. Switch to LFS User

```bash
su - lfs
```

### 4. Download Packages

Download all required source packages:

```bash
./scripts/01-download.sh
```

### 5. Build Cross-Toolchain

Build the cross-compilation toolchain:

```bash
./scripts/02-cross-toolchain.sh
```

### 6. Build Temporary Tools

Build temporary tools using the cross-toolchain:

```bash
./scripts/03-temp-tools.sh
```

### 7. Build Chroot Tools

Enter chroot environment and build additional tools:

```bash
sudo ./scripts/04-chroot-tools.sh
sudo $LFS/entreroot.sh
/mnt/lfs/chroot-build.sh
exit
```

### 8. Build System Packages

Build the final system packages:

```bash
sudo ./scripts/05-system.sh
sudo $LFS/entreroot.sh
/mnt/lfs/chroot-ch8.sh
exit
```

### 9. Configure System

Configure the system (network, boot scripts, etc.):

```bash
sudo ./scripts/06-config.sh
sudo $LFS/entreroot.sh
/mnt/lfs/chroot-ch9.sh
exit
```

### 10. Install Bootloader

Install and configure GRUB bootloader:

```bash
sudo ./scripts/07-bootloader.sh
sudo $LFS/entreroot.sh
/mnt/lfs/chroot-ch10.sh
exit
```

### 11. Install Development Tools

Install development tools (browser, IDE, Docker, etc.):

```bash
sudo ./scripts/08-dev-tools.sh
sudo $LFS/entreroot.sh
/mnt/lfs/chroot-dev.sh
exit
```

### 12. Final Steps

```bash
# Unmount filesystems
sudo umount -v $LFS/dev/pts
sudo umount -v $LFS/dev
sudo umount -v $LFS/proc
sudo umount -v $LFS/sys
sudo umount -v $LFS/run
sudo umount -v $LFS

# Reboot
sudo reboot
```

## Using the Build Menu

You can also use the interactive build menu:

```bash
sudo ./build.sh
```

This will display a menu where you can select individual steps or run the full build.

## Running on UTM SE

1. Export the LFS partition as a raw disk image
2. Create a new VM in UTM SE
3. Use the raw disk image as the primary disk
4. Boot from the VM

## Troubleshooting

### Build Fails at a Step

If a build step fails, you can resume from that step:

1. Check the error message
2. Fix any issues
3. Re-run the failed step

### Missing Dependencies

If you get "command not found" errors:

```bash
sudo apt-get update
sudo apt-get install -y <package-name>
```

### Disk Space Issues

Check available space:

```bash
df -h /mnt/lfs
```

If you need more space, consider:
- Removing unnecessary files
- Expanding the partition
- Using a different location with more space

## Post-Installation

After booting into your new LFS system:

1. Login as root
2. Set up network connection
3. Install additional packages as needed
4. Customize your environment

## Resources

- [LFS Book 12.0](https://www.linuxfromscratch.org/lfs/view/12.0/)
- [Beyond Linux From Scratch](https://www.linuxfromscratch.org/blfs/)
- [UTM SE Documentation](https://mac.getutm.app/support/)
- [LFS Wiki](https://wiki.linuxfromscratch.org/)
