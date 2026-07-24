# Hướng dẫn sử dụng LFS Project

## QUAN TRỌNG

Dự án này là **BUILD SYSTEM** (hệ thống build), không phải file chạy trực tiếp.

Bạn cần **BUILD** trước, sau đó tạo disk image để chạy trên UTM SE.

---

## Cách 1: Build từ đầu (Khuyên nghị)

### Yêu cầu
- Linux host (Ubuntu/Debian)
- 10GB+ disk space
- 2-4GB RAM
- Internet connection

### Các bước

```bash
# 1. Clone project
git clone https://github.com/wioos28/wadd-oss.git
cd wadd-oss/lfs-project

# 2. Chuẩn bị host
sudo ./scripts/00-host-prep.sh

# 3. Switch user
su - lfs

# 4. Download packages
./scripts/01-download.sh

# 5. Build cross-toolchain
./scripts/02-cross-toolchain.sh

# 6. Build temporary tools
./scripts/03-temp-tools.sh

# 7. Vào chroot và build
sudo mount -v --bind /dev /mnt/lfs/dev
sudo mount -v --bind /dev/pts /mnt/lfs/dev/pts
sudo mount -vt proc proc /mnt/lfs/proc
sudo mount -vt sysfs sysfs /mnt/lfs/sys
sudo mount -vt tmpfs tmpfs /mnt/lfs/run

sudo chroot /mnt/lfs /tools/bin/env -i \
    HOME=/root \
    TERM="$TERM" \
    PATH=/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin \
    /tools/bin/bash --login +h

# Trong chroot:
/mnt/lfs/chroot-build.sh
/mnt/lfs/chroot-ch8.sh
/mnt/lfs/chroot-optimize.sh
/mnt/lfs/chroot-desktop.sh
/mnt/lfs/chroot-dev.sh

# Thoát
exit

# 8. Tạo disk image
sudo ./create-disk-image.sh

# 9. Copy image vào iPhone và chạy trên UTM SE
```

---

## Cách 2: Tạo Minimal Boot Image (Nhanh)

Nếu bạn muốn test nhanh trên UTM SE:

```bash
# Clone project
git clone https://github.com/wioos28/wadd-oss.git
cd wadd-oss/lfs-project

# Tạo minimal boot image
sudo ./scripts/create-minimal-boot.sh

# Copy file lfs-minimal-boot.img vào iPhone
# Tạo VM trên UTM SE và boot
```

---

## Cách 3: Dùng Disk Image có sẵn

Nếu có người share disk image:

1. Tải file `.img` về
2. Import vào UTM SE
3. Boot

---

## Cấu hình UTM SE trên iPhone 11

### Tạo VM mới

1. Mở **UTM SE**
2. Nhấn **+** (Create New)
3. Chọn **Virtualize**
4. Chọn **Linux**
5. Import Drive: chọn file `.img`

### Cấu hình khuyến nghị

| Setting | Giá trị |
|---------|---------|
| Name | LFS Linux |
| CPU | 2 cores |
| RAM | 1024 MB |
| Storage | Import existing |
| Network | Default (NAT) |
| Display | Default |

### Nếu bị lag

- Giảm RAM xuống **512 MB**
- Giảm CPU xuống **1 core**
- Tắt animation

---

## Troubleshooting

### "Boot failed: not a bootable disk"

**Nguyên nhân**: File .img không phải bootable disk

**Giải pháp**:
1. Dùng script `create-disk-image.sh` để tạo bootable disk
2. Hoặc dùng `create-minimal-boot.sh` cho minimal image

### "No bootable device"

**Nguyên nhân**: GRUB chưa được cài

**Giải pháp**:
```bash
# Trong chroot
grub-install /dev/sda
update-grub
```

### "Kernel panic"

**Nguyên nhân**: Kernel không tìm thấy root device

**Giải pháp**:
1. Kiểm tra fstab
2. Kiểm tra UUID: `lsblk -f`
3. Sửa grub config: `root=/dev/sda1`

### "Cannot mount root filesystem"

**Nguyên nhân**: Driver không được load

**Giải pháp**:
1. Boot từ live USB
2. Mount root partition
3. Chroot và load modules

---

## Cài đặt từ Ubuntu/Debian

Nếu bạn có Ubuntu/Debian host:

```bash
# Cài dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    bison \
    gawk \
    texinfo \
    python3 \
    wget \
    curl \
    git

# Clone và build
git clone https://github.com/wioos28/wadd-oss.git
cd wadd-oss/lfs-project
sudo ./build.sh
```

---

## Liên hệ

- GitHub: https://github.com/wioos28/wadd-oss
- Issues: https://github.com/wioos28/wadd-oss/issues

---

## Tips

1. **Đọc kỹ** README.md trước khi bắt đầu
2. **Backup** dữ liệu quan trọng
3. **Kiểm tra** disk space trước khi build
4. **Đợi** các script hoàn thành (có thể mất 3-8 giờ)
5. **Hỏi help** nếu gặp vấn đề

---

Chúc bạn build thành công! 🐧
