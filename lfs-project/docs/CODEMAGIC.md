# CodeMagic Setup Guide

## Build LFS on CodeMagic Cloud

Hướng dẫn build Linux From Scratch trên CodeMagic CI/CD.

---

## Tại sao dùng CodeMagic?

- **Free tier**: 500 credits/tháng
- **Linux environment**: Ubuntu 24.04
- **Cloud build**: Không cần máy tính cục bộ
- **Artifact storage**: Lưu disk image
- **GitHub integration**: Auto release

---

## Cấu hình CodeMagic

### Bước 1: Đăng ký CodeMagic

1. Truy cập https://codemagic.io/start
2. Đăng ký tài khoản miễn phí
3. Kết nối GitHub repository

### Bước 2: Thêm repository

1. Dashboard → Add application
2. Chọn GitHub
3. Chọn repository: `wioos28/wadd-oss`
4. Chọn branch: `main`

### Bước 3: Upload codemagic.yaml

File `codemagic.yaml` đã được tạo trong project. CodeMagic sẽ tự động detect.

### Bước 4: Chạy build

1. Vào workflow "LFS Build"
2. Nhấn "Start new build"
3. Đợi build hoàn thành (3-8 giờ)

---

## Cấu hình Environment Variables

Vào CodeMagic → Environment Groups → Tạo group `lfs_credentials`:

```
LFS_VERSION=12.0
```

---

## Build Process

### Timeline

| Step | Time | Description |
|------|------|-------------|
| Setup | 5 min | Install dependencies |
| Download | 10 min | Download packages |
| Cross-toolchain | 30 min | Build GCC, Binutils |
| Temporary tools | 30 min | Build shell, coreutils |
| Chroot build | 2-4 hours | Build full system |
| Optimize | 10 min | Kernel, desktop |
| Create image | 5 min | Create .img file |
| **Total** | **3-6 hours** | |

### Artifacts

Sau khi build xong, CodeMagic sẽ tạo:

- `lfs-utm-se.img` (20GB) - Full disk image
- `lfs-minimal-boot.img` (2GB) - Minimal boot image
- `BUILD_REPORT.md` - Build report

---

## Tải disk image

### Cách 1: CodeMagic Dashboard

1. Vào build result
2. Download artifact
3. File .img sẽ được download

### Cách 2: GitHub Release

CodeMagic sẽ tự động tạo GitHub release với disk image.

---

## Cài đặt trên UTM SE

### Bước 1: Transfer file vào iPhone

- **AirDrop**: Gửi file từ Mac/PC
- **iCloud**: Upload → Download trên iPhone
- **iTunes**: Sync qua iTunes

### Bước 2: Tạo VM trên UTM SE

1. Mở UTM SE
2. Nhấn **+**
3. Chọn **Virtualize** → **Linux**
4. Import Drive: chọn file `.img`

### Bước 3: Cấu hình VM

| Setting | Giá trị |
|---------|---------|
| Name | LFS Linux |
| CPU | 2 cores |
| RAM | 1024 MB |
| Storage | Import existing |
| Network | Default (NAT) |

### Bước 4: Boot

1. Nhấn Play button
2. Chờ boot
3. Login: `root` / `password`

---

## Troubleshooting

### Build timeout

LFS build mất 3-6 giờ. Nếu timeout:

```yaml
# Trong codemagic.yaml
max_build_duration: 720  # 12 hours
```

### Out of disk space

CodeMagic có 14GB free space. Nếu不够:

1. Tối ưu build script
2. Xóa files không cần thiết
3. Dùng minimal build

### Network error

Nếu download fail:

1. Kiểm tra network
2. Retry build
3. Mirror packages

---

## Tùy chỉnh build

### Thêm packages

Edit `scripts/08-dev-tools.sh` để thêm packages.

### Thay đổi kernel

Edit `scripts/09-optimize.sh` để customize kernel.

### Thay đổi theme

Edit `scripts/10-desktop-setup.sh` để thay đổi theme.

---

## Chi phí

### CodeMagic Free Tier

- **500 credits/tháng**
- **1 build ≈ 100-200 credits**
- **5-10 builds/tháng miễn phí**

### CodeMagic Pro

- **$149/tháng**
- **Unlimited builds**
- **Priority machines**

---

## Liên hệ

- CodeMagic Docs: https://docs.codemagic.io
- CodeMagic Support: https://codemagic.io/support
- GitHub Issues: https://github.com/wioos28/wadd-oss/issues

---

Chúc bạn build thành công! 🐧
