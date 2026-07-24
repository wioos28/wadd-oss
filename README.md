# ProCameraApp

Ứng dụng chụp ảnh chuyên nghiệp (Pro Camera App) được phát triển bằng SwiftUI cho iOS 16+.

## Tính năng chính

### Manual Controls
- **ISO**: Điều chỉnh độ nhạy sáng (25-2500)
- **Shutter Speed**: Điều chỉnh tốc độ màn hình (1/1000s - 2s)
- **Aperture**: Hiển thị khẩu độ (f/1.6, f/1.8, etc.)
- **Exposure Compensation**: Bù trừ EV (-3.0 đến +3.0)
- **Torch/Flash**: Đèn flash liên tục với cường độ điều chỉnh

### Format Selection
- **ProRAW**: Apple ProRAW 12-bit DNG (iPhone 12 Pro+)
- **RAW**: RAW DNG 10-bit
- **JPEG**: JPEG chất lượng cao
- **PNG**: PNG lossless

### Real-time Color Grading
- **White Balance**: Nhiệt độ màu (2000K-10000K) và Tint
- **Saturation**: Độ bão hòa (0.0-2.0)
- **Contrast**: Độ tương phản (0.0-2.0)
- **Brightness**: Độ sáng (-1.0-1.0)
- **Highlights/Shadows**: Bảo vệ chi tiết sáng/tối
- **Vignette**: Hiệu ứng viền
- **Grain**: Hiệu ứng hạt film

### Built-in Filters
- Vivid
- Warm
- Cool
- B&W (Black & White)
- Film
- Portrait

## Cấu trúc dự án

```
wadd-oss/
├── Info.plist                        # Cấu hình quyền Camera & Photo Library
├── ProCameraAppApp.swift             # App entry point
├── ContentView.swift                 # Giao diện chính
├── CameraManager.swift               # Quản lý AVCaptureSession
├── ColorFilterManager.swift          # Xử lý màu real-time
├── Models/
│   └── CameraSettings.swift          # Models và data structures
├── Views/
│   └── CameraPreviewView.swift       # Live camera preview
├── ProCameraApp.xcodeproj/           # Xcode project
├── codemagic.yaml                    # CI/CD configuration
├── ExportOptions.plist               # Export options cho IPA
├── README.md
└── HOW-TO-USE.md
```

## Yêu cầu

- iOS 16.0+
- Xcode 14.0+
- Swift 5.7+

## Cài đặt

1. Clone hoặc tải dự án
2. Mở `ProCameraApp.xcodeproj` trong Xcode
3. Chọn **iPhone** làm target (không dùng simulator vì cần camera thật)
4. Build và chạy (Cmd + R)
5. Cấp quyền Camera khi được yêu cầu

## Info.plist Configuration

File Info.plist đã được cấu hình sẵn với các quyền sau:

- `NSCameraUsageDescription`: Quyền truy cập camera
- `NSPhotoLibraryAddUsageDescription`: Quyền lưu ảnh
- `NSPhotoLibraryUsageDescription`: Quyền truy cập thư viện ảnh

## Architecture

### CameraManager (ViewModel)
Quản lý toàn bộ hoạt động camera:
- AVCaptureSession lifecycle
- Manual controls (ISO, Shutter, EV, White Balance)
- Photo capture và saving
- Camera switching

### ColorFilterManager
Xử lý bộ lọc màu real-time:
- Core Image filters
- CIColorCube cho 3D LUT
- Performance optimization

### SwiftUI Views
Giao diện người dùng:
- Live camera preview
- Control sliders
- Filter selection
- Settings panel

## CI/CD với Codemagic

Dự án đã được cấu hình sẵn với `codemagic.yaml`:

### Workflows
- **ios-release**: Build Release IPA cho App Store
- **ios-debug**: Build Debug cho testing
- **ios-test**: Chạy unit tests

### Trigger
- Push/PR đến `main`, `develop`, `feature/*`
- Tag pattern `v*`

### Cấu hình
1. Đăng nhập Codemagic
2. Kết nối repository
3. Cấu hình `teamID` trong `ExportOptions.plist`
4. Trigger build

## License

MIT License
