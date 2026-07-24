# Linux From Scratch (LFS) for UTM SE

Dự án xây dựng hệ điều hành Linux từ source代码, tối ưu cho UTM SE với đầy đủ công cụ phát triển.

## Mục tiêu

- Hệ điều hành nhẹ nhưng đầy đủ tính năng
- Chạy mượt trên UTM SE (QEMU)
- Bao gồm: Trình duyệt, Terminal, IDE, Docker, Git

## Cấu trúc dự án

```
lfs-project/
├── README.md              # Tài liệu dự án
├── build.sh               # Script build chính
├── scripts/               # Script cho từng giai đoạn
│   ├── 00-host-prep.sh    # Chuẩn bị host system
│   ├── 01-download.sh     # Download packages
│   ├── 02-cross-toolchain.sh  # Build cross-toolchain
│   ├── 03-temp-tools.sh   # Temporary tools
│   ├── 04-chroot-tools.sh # Tools trong chroot
│   ├── 05-system.sh       # System packages
│   ├── 06-config.sh       # System configuration
│   ├── 07-bootloader.sh   # Bootloader setup
│   └── 08-dev-tools.sh    # Development tools
├── packages/              # Danh sách packages
│   ├── base.txt           # Packages cơ bản LFS
│   └── dev.txt            # Development tools
├── config/                # Configuration files
│   ├── fstab              # Filesystem table
│   ├── network.sh         # Network config
│   └── grub.cfg           # GRUB config
└── docs/                  # Tài liệu tham khảo
```

## Yêu cầu hệ thống

- Host: Linux (Ubuntu/Debian recommended)
- Disk: 10GB+ free space
- RAM: 2GB+ recommended
- Thời gian build: 3-8 giờ tùy phần cứng

## Cách sử dụng

```bash
# 1. Chuẩn bị host
sudo ./scripts/00-host-prep.sh

# 2. Download packages
./scripts/01-download.sh

# 3. Build theo thứ tự
./scripts/02-cross-toolchain.sh
./scripts/03-temp-tools.sh
./scripts/04-chroot-tools.sh
./scripts/05-system.sh
./scripts/06-config.sh
./scripts/07-bootloader.sh

# 4. Cài development tools
./scripts/08-dev-tools.sh
```

## Ghi chú

- Mỗi script có thể chạy riêng lẻ
- Log files lưu trong /var/log/lfs-build/
- Nếu build bị gián đoạn, có thể tiếp tục từ bước cuối

## Tài liệu tham khảo

- [LFS Book 12.0](https://www.linuxfromscratch.org/lfs/view/12.0/)
- [Beyond Linux From Scratch](https://www.linuxfromscratch.org/blfs/)
- [UTM SE Documentation](https://mac.getutm.app/support/)
