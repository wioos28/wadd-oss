//
//  CameraSettings.swift
//  ProCameraApp
//
//  Mô hình dữ liệu cho các cài đặt camera thủ công
//

import AVFoundation
import CoreImage
import Foundation

// MARK: - Camera Capture Format
/// Định dạng ảnh chụp được hỗ trợ
enum CaptureFormat: String, CaseIterable, Identifiable {
    case ProRAW = "ProRAW"
    case RAW = "RAW (DNG)"
    case JPEG = "JPEG"
    case PNG = "PNG"

    var id: String { rawValue }

    /// Mô tả ngắn gọn
    var description: String {
        switch self {
        case .ProRAW: return "Apple ProRAW (12-bit DNG)"
        case .RAW: return "RAW DNG (10-bit)"
        case .JPEG: return "JPEG (Lossy)"
        case .PNG: return "PNG (Lossless)"
        }
    }

    /// Chất lượng nén (0-1)
    var compressionQuality: CGFloat {
        switch self {
        case .ProRAW, .RAW: return 1.0
        case .JPEG: return 0.95
        case .PNG: return 1.0
        }
    }

    /// File extension
    var fileExtension: String {
        switch self {
        case .ProRAW, .RAW: return "dng"
        case .JPEG: return "jpg"
        case .PNG: return "png"
        }
    }
}

// MARK: - White Balance Preset
/// Preset cân bằng trắng
enum WhiteBalancePreset: String, CaseIterable, Identifiable {
    case auto = "Auto"
    case daylight = "Daylight"
    case cloudy = "Cloudy"
    case tungsten = "Tungsten"
    case fluorescent = "Fluorescent"
    case shade = "Shade"
    case custom = "Custom"

    var id: String { rawValue }

    /// Nhiệt độ màu (Kelvin) tương ứng
    var temperature: Float {
        switch self {
        case .auto: return 5500
        case .daylight: return 5500
        case .cloudy: return 6500
        case .tungsten: return 3200
        case .fluorescent: return 4000
        case .shade: return 7500
        case .custom: return 5500
        }
    }
}

// MARK: - Camera Settings
/// Cài đặt camera hiện tại
struct CameraSettings {
    /// Khẩu độ (Aperture) - f-stop value
    /// Trên iPhone, thường là fixed aperture (f/1.6, f/1.8, f/2.2, f/2.8)
    var aperture: Float = 1.6

    /// Tốc độ màn hình (Shutter Speed) - đơn vị: giây
    /// Ví dụ: 1/1000s = 0.001, 1/60s ≈ 0.0167, 1s = 1.0
    var shutterSpeed: Double = 1.0 / 125.0

    /// ISO - Độ nhạy sáng
    /// iPhone thường hỗ trợ: 25-2500 (tùy model)
    var iso: Float = 100.0

    /// Exposure Compensation (EV)
    /// Điều chỉnh độ sáng bù trừ: -3.0 đến +3.0
    var exposureCompensation: Float = 0.0

    /// Định dạng ảnh chụp
    var captureFormat: CaptureFormat = .JPEG

    /// Cân bằng trắng
    var whiteBalancePreset: WhiteBalancePreset = .daylight

    /// Nhiệt độ màu tùy chỉnh (Kelvin)
    var customTemperature: Float = 5500

    /// Tint value (-1.0 đến 1.0)
    var tint: Float = 0.0

    /// Saturation (Độ bão hòa) - 0.0 đến 2.0
    var saturation: Float = 1.0

    /// Contrast (Độ tương phản) - 0.0 đến 2.0
    var contrast: Float = 1.0

    /// Brightness (Độ sáng) - -1.0 đến 1.0
    var brightness: Float = 0.0

    /// Highlight Protection (-1.0 đến 1.0)
    var highlights: Float = 0.0

    /// Shadow Protection (-1.0 đến 1.0)
    var shadows: Float = 0.0

    /// Sharpness (Độ sắc nét) - 0.0 đến 2.0
    var sharpness: Float = 1.0

    /// Vignette effect - 0.0 đến 1.0
    var vignette: Float = 0.0

    /// Grain effect (Noise) - 0.0 đến 1.0
    var grain: Float = 0.0

    // MARK: - Helper Methods

    /// Tính thời gian phơi sáng hiển thị
    var shutterSpeedDisplay: String {
        if shutterSpeed <= 0 {
            return "1/∞s"
        } else if shutterSpeed >= 1.0 {
            return String(format: "%.1fs", shutterSpeed)
        } else {
            let denominator = Int(1.0 / shutterSpeed)
            return "1/\(denominator)s"
        }
    }

    /// ISO hiển thị
    var isoDisplay: String {
        return "ISO \(Int(iso))"
    }

    /// Khẩu độ hiển thị
    var apertureDisplay: String {
        return String(format: "f/%.1f", aperture)
    }

    /// EV hiển thị
    var evDisplay: String {
        if exposureCompensation == 0 {
            return "EV 0"
        } else if exposureCompensation > 0 {
            return String(format: "EV +%.1f", exposureCompensation)
        } else {
            return String(format: "EV %.1f", exposureCompensation)
        }
    }
}

// MARK: - Camera State
/// Trạng thái hiện tại của camera
enum CameraState: Equatable {
    case idle
    case configuring
    case running
    case capturing
    case error(String)

    static func == (lhs: CameraState, rhs: CameraState) -> Bool {
        switch (lhs, rhs) {
        case (.idle, .idle), (.configuring, .configuring),
             (.running, .running), (.capturing, .capturing):
            return true
        case (.error(let a), .error(let b)):
            return a == b
        default:
            return false
        }
    }
}

// MARK: - Camera Position
/// Vị trí camera
enum CameraPosition: String, CaseIterable, Identifiable {
    case back = "Back"
    case front = "Front"
    case ultrawide = "Ultrawide"
    case telephoto = "Telephoto"

    var id: String { rawValue }

    /// AVCaptureDevice.Position tương ứng
    var avPosition: AVCaptureDevice.Position {
        switch self {
        case .back: return .back
        case .front: return .front
        case .ultrawide: return .back // Same device, different lens
        case .telephoto: return .back // Same device, different lens
        }
    }
}

// MARK: - Focus Mode
/// Chế độ lấy nét
enum FocusModeOption: String, CaseIterable, Identifiable {
    case auto = "Auto"
    case manual = "Manual"
    case continuous = "Continuous"

    var id: String { rawValue }

    var avFocusMode: AVCaptureDevice.FocusMode {
        switch self {
        case .auto: return .autoFocus
        case .manual: return .locked
        case .continuous: return .continuousAutoFocus
        }
    }
}

// MARK: - Exposure Mode
/// Chế độ phơi sáng
enum ExposureModeOption: String, CaseIterable, Identifiable {
    case auto = "Auto"
    case manual = "Manual"
    case continuous = "Continuous"

    var id: String { rawValue }

    var avExposureMode: AVCaptureDevice.ExposureMode {
        switch self {
        case .auto: return .autoExpose
        case .manual: return .locked
        case .continuous: return .continuousAutoExposure
        }
    }
}

// MARK: - Torch Mode
/// Chế độ đèn flash (Torch)
enum TorchMode: String, CaseIterable, Identifiable {
    case off = "Off"
    case on = "On"
    case auto = "Auto"

    var id: String { rawValue }
}
