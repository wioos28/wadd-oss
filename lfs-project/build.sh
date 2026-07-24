#!/bin/bash
# LFS Build - Main Build Script
# This script orchestrates the entire LFS build process

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           Linux From Scratch (LFS) Build System             ║"
echo "║                    for UTM SE                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Starting at: $(date)"
echo ""

# Set environment
export LFS=/mnt/lfs
export LFS_SOURCES=$LFS/sources

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root!"
    echo "Usage: sudo ./build.sh"
    exit 1
fi

# Function to display menu
show_menu() {
    clear
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           Linux From Scratch (LFS) Build Menu               ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    echo "║  1. Prepare Host System                                      ║"
    echo "║  2. Download Packages                                        ║"
    echo "║  3. Build Cross-Toolchain                                    ║"
    echo "║  4. Build Temporary Tools                                    ║"
    echo "║  5. Build Chroot Tools                                       ║"
    echo "║  6. Build System Packages                                    ║"
    echo "║  7. Configure System                                         ║"
    echo "║  8. Install Bootloader                                       ║"
    echo "║  9. Install Development Tools                                ║"
    echo "║  10. Full Build (Run all steps)                              ║"
    echo "║  0. Exit                                                     ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Function to run a step
run_step() {
    local step=$1
    local script=$2
    
    echo ""
    echo "=== Running Step $step ==="
    echo ""
    
    if [ -f "./scripts/$script" ]; then
        bash "./scripts/$script"
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ Step $step completed successfully"
        else
            echo ""
            echo "✗ Step $step failed"
            return 1
        fi
    else
        echo "✗ Script not found: ./scripts/$script"
        return 1
    fi
}

# Main loop
while true; do
    show_menu
    read -p "Select an option: " choice
    
    case $choice in
        1)
            run_step "1" "00-host-prep.sh"
            ;;
        2)
            run_step "2" "01-download.sh"
            ;;
        3)
            run_step "3" "02-cross-toolchain.sh"
            ;;
        4)
            run_step "4" "03-temp-tools.sh"
            ;;
        5)
            run_step "5" "04-chroot-tools.sh"
            ;;
        6)
            run_step "6" "05-system.sh"
            ;;
        7)
            run_step "7" "06-config.sh"
            ;;
        8)
            run_step "8" "07-bootloader.sh"
            ;;
        9)
            run_step "9" "08-dev-tools.sh"
            ;;
        10)
            echo ""
            echo "Starting full build..."
            echo ""
            
            for i in 1 2 3 4 5 6 7 8 9; do
                run_step "$i" "$(ls scripts/*.sh | head -1 | xargs basename)"
                if [ $? -ne 0 ]; then
                    echo ""
                    echo "Build failed at step $i"
                    echo "You can resume from this step later"
                    exit 1
                fi
            done
            
            echo ""
            echo "╔═══════════════════════════════════════════════════════════════╗"
            echo "║           Build Complete!                                    ║"
            echo "╚═══════════════════════════════════════════════════════════════╝"
            echo ""
            echo "Your LFS system is ready!"
            echo ""
            echo "Next steps:"
            echo "1. Reboot your system"
            echo "2. Select LFS from GRUB menu"
            echo "3. Login with root"
            echo ""
            echo "Enjoy your new Linux system!"
            ;;
        0)
            echo ""
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo ""
            echo "Invalid option. Please try again."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
