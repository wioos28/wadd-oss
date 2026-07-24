# Hướng dẫn sử dụng ProCameraApp

## Cài đặt và Chạy

### Bước 1: Mở Project trong Xcode

```bash
# Mở file .xcodeproj
open ProCameraApp.xcodeproj
```

Hoặc mở Xcode → File → Open → Chọn thư mục `ProCameraApp`

### Bước 2: Chọn Device

- Chọn **iPhone** làm target device (không dùng simulator vì cần camera thực)
- Hoặc chọn **Generic iOS Device** nếu muốn build cho thiết bị thật

### Bước 3: Build và Chạy

Nhấn `Cmd + R` hoặc chọn Product → Run

### Bước 4: Cấp quyền Camera

Khi chạy lần đầu, ứng dụng sẽ yêu cầu quyền truy cập Camera và Photo Library. Nhấn **Allow**.

---

## Tính năng chi tiết

### 1. Manual Controls

#### ISO (Độ nhạy sáng)
- **Vùng slider**: 25 - 2500
- **Mặc định**: 100
- **Công dụng**: Tăng ISO giúp chụp trong điều kiện thiếu sáng nhưng sẽ tạo noise

#### Shutter Speed (Tốc độ màn hình)
- **Vùng slider**: 1/1000s - 2s
- **Mặc định**: 1/125s
- **Công dụng**:
  - Nhanh (1/1000s): Đóng băng chuyển động
  - Chậm (1/30s): Tạo hiệu ứng mờ chuyển động (motion blur)

#### Exposure Compensation (EV)
- **Vùng slider**: -3.0 - +3.0
- **Mặc định**: 0
- **Công dụng**: Bù trừ độ sáng tự động

### 2. Format Selection

Nhấn vào nút format ở góc trên để chọn:

- **ProRAW**: Chất lượng cao nhất, chỉnh sửa linh hoạt (iPhone 12 Pro+)
- **RAW**: DNG 10-bit, phù hợp cho post-processing
- **JPEG**: File nhỏ, chia sẻ dễ dàng
- **PNG**: Lossless, phù hợp cho graphic design

### 3. Color Grading

#### Temperature (Nhiệt độ màu)
- **2000K - 4000K**: Ấm (vàng cam)
- **5000K - 6500K**: Trung tính
- **7000K - 10000K**: Mát (xanh dương)

#### Tint
- **-1.0 - 0**: Hướng xanh lá
- **0 - +1.0**: Hướng tím/magenta

#### Saturation
- **0**: Đen trắng
- **1.0**: Bình thường
- **2.0**: Saturated mạnh

#### Contrast
- **0**: Flat
- **1.0**: Bình thường
- **2.0**: Cao contrast

### 4. Built-in Filters

| Filter | Mô tả |
|--------|-------|
| Vivid | Tăng saturation, contrast |
| Warm | Nhiệt độ màu cao, ấm áp |
| Cool | Nhiệt độ màu thấp, mát mẻ |
| B&W | Đen trắng |
| Film | Hiệu ứng film cổ điển |
| Portrait | Tối ưu cho chụp chân dung |

### 5. Camera Switch

Nhấn nút mũi tên xoay ở góc phải để chuyển camera:
- **Back**: Camera chính (Wide)
- **Front**: Camera trước

### 6. Tap to Focus

Nhấn vào bất kỳ đâu trên preview để lấy nét tại điểm đó.

---

## Troubleshooting

### "Không tìm thấy camera"
- Đảm bảo chạy trên thiết bị thực (không phải simulator)
- Kiểm tra quyền camera trong Settings → Privacy → Camera

### "Lưu ảnh thất bại"
- Kiểm tra quyền Photo Library trong Settings → Privacy → Photos
- Đảm bảo còn dung lượng trống

### "Preview bị đen"
- Thử restart app
- Kiểm tra camera không bị ứng dụng khác chiếm

### Performance issues (FPS thấp)
- Giảm độ phức tạp của color filters
- Tắt Vignette/Grain nếu không cần
- Sử dụng chế độ Auto thay vì Manual

---

## Technical Notes

### Supported Devices
- iPhone 12 Pro trở lên: Hỗ trợ ProRAW
- iPhone 11 trở lên: Hỗ trợ大部分 features
- iPhone X trở lên: Hỗ trợ基本 manual controls

### Known Limitations
- Simulator không hỗ trợ camera
- Một số manual controls có thể bị giới hạn tùy model iPhone
- ProRAW chỉ khả dụng trên iPhone 12 Pro trở lên

---

## Development

### Architecture
- **MVVM Pattern**: CameraManager (ViewModel) + SwiftUI Views
- **Combine**: Publisher/Subscriber cho reactive updates
- **Core Image**: Real-time color processing
- **AVFoundation**: Camera hardware control

### Adding New Filters
1. Thêm preset trong `FilterPreset` struct
2. Hoặc import file `.cube` (3D LUT)

### Custom LUT Files
Đặt file `.cube` trong thư mục Resources và load:
```swift
let customLUT = colorFilterManager.loadLUT(named: "my-lut")
colorFilterManager.applyFilter(customLUT)
```

---

## License

MIT License - Sử dụng miễn phí
