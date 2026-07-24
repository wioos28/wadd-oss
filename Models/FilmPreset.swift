//
//  FilmPreset.swift
//  ProCameraApp
//
//  Mô phỏng màu phim (Film Simulation) sử dụng Core Image
//  Hỗ trợ: Kodak Portra 400, Fuji Velvia, Ilford B&W, CineStill 800T, Original
//

import CoreImage
import SwiftUI

// MARK: - Film Preset Type
/// Các loại phim được mô phỏng
enum FilmPresetType: String, CaseIterable, Identifiable {
    case original = "Original"
    case kodakPortra400 = "Kodak Portra 400"
    case fujiVelvia = "Fuji Velvia"
    case ilfordBW = "Ilford B&W"
    case cineStill800T = "CineStill 800T"

    var id: String { rawValue }

    /// Mô tả ngắn gọn
    var description: String {
        switch self {
        case .original:
            return "Không có bộ lọc"
        case .kodakPortra400:
            return "Tông màu ấm, da thịt tự nhiên"
        case .fujiVelvia:
            return "Màu sắc rực rỡ, độ bão hòa cao"
        case .ilfordBW:
            return "Đen trắng cổ điển, grain mềm"
        case .cineStill800T:
            return "Tông màu điện ảnh, halation đỏ"
        }
    }

    /// Màu accent cho UI
    var accentColor: Color {
        switch self {
        case .original:
            return .white
        case .kodakPortra400:
            return Color(red: 0.96, green: 0.87, blue: 0.70) // Warm gold
        case .fujiVelvia:
            return Color(red: 0.20, green: 0.60, blue: 0.86) // Vibrant blue
        case .ilfordBW:
            return .gray
        case .cineStill800T:
            return Color(red: 0.90, green: 0.30, blue: 0.24) // Film red
        }
    }

    /// Icon name
    var iconName: String {
        switch self {
        case .original:
            return "camera.viewfinder"
        case .kodakPortra400:
            return "sun.max.fill"
        case .fujiVelvia:
            return "leaf.fill"
        case .ilfordBW:
            return "circle.lefthalf.filled"
        case .cineStill800T:
            return "film.fill"
        }
    }
}

// MARK: - Film Simulation Parameters
/// Tham số mô phỏng phim
struct FilmSimulationParams {
    /// Saturation (Độ bão hòa)
    var saturation: Float

    /// Contrast (Độ tương phản)
    var contrast: Float

    /// Brightness (Độ sáng)
    var brightness: Float

    /// Temperature (Nhiệt độ màu - Kelvin)
    var temperature: Float

    /// Tint (Màu tím/xanh lá)
    var tint: Float

    /// Highlights (Điểm ảnh sáng)
    var highlights: Float

    /// Shadows (Bóng tối)
    var shadows: Float

    /// Grain (Hạt phim)
    var grain: Float

    /// Vignette (Viền tối)
    var vignette: Float

    /// Fade (Mờ nhạt - làm柔和 màu sắc)
    var fade: Float

    /// Cyan-Red shift (Dịch chuyển cyan-red)
    var cyanRedShift: Float

    /// Magenta-Green shift (Dịch chuyển magenta-green)
    var magentaGreenShift: Float

    /// Yellow-Blue shift (Dịch chuyển yellow-blue)
    var yellowBlueShift: Float
}

// MARK: - Film Preset
/// Thông tin mô phỏng phim
struct FilmSimulation {
    let type: FilmPresetType
    let params: FilmSimulationParams
    let description: String

    /// Áp dụng mô phỏng lên CIImage
    func apply(to image: CIImage, context: CIContext) -> CIImage {
        var processedImage = image

        // 1. Color Temperature & Tint
        processedImage = applyTemperatureTint(to: processedImage)

        // 2. Color Controls (Saturation, Contrast, Brightness)
        processedImage = applyColorControls(to: processedImage)

        // 3. Highlight/Shadow adjustments
        processedImage = applyHighlightShadow(to: processedImage)

        // 4. Color Balance shifts
        processedImage = applyColorBalance(to: processedImage)

        // 5. Fade effect (lift blacks)
        if params.fade > 0 {
            processedImage = applyFade(to: processedImage)
        }

        // 6. Vignette
        if params.vignette > 0 {
            processedImage = applyVignette(to: processedImage)
        }

        // 7. Grain
        if params.grain > 0 {
            processedImage = applyGrain(to: processedImage, context: context)
        }

        return processedImage
    }

    // MARK: - Filter Application Methods

    private func applyTemperatureTint(to image: CIImage) -> CIImage {
        guard let filter = CIFilter(name: "CITemperatureAndTint") else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(
            CIVector(x: CGFloat(params.temperature), y: CGFloat(params.tint * 100)),
            forKey: "inputNeutral"
        )
        filter.setValue(
            CIVector(x: 6500, y: 0),
            forKey: "inputTargetNeutral"
        )

        return filter.outputImage ?? image
    }

    private func applyColorControls(to image: CIImage) -> CIImage {
        guard let filter = CIFilter(name: "CIColorControls") else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(params.saturation, forKey: kCIInputSaturationKey)
        filter.setValue(params.contrast, forKey: kCIInputContrastKey)
        filter.setValue(params.brightness, forKey: kCIInputBrightnessKey)

        return filter.outputImage ?? image
    }

    private func applyHighlightShadow(to image: CIImage) -> CIImage {
        guard let filter = CIFilter(name: "CIHighlightShadowAdjust") else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)

        // Map -1...1 to 0...1 range
        let highlightAmount = (params.highlights + 1.0) / 2.0
        let shadowAmount = (params.shadows + 1.0) / 2.0

        filter.setValue(highlightAmount, forKey: "inputHighlightAmount")
        filter.setValue(shadowAmount, forKey: "inputShadowAmount")

        return filter.outputImage ?? image
    }

    private func applyColorBalance(to image: CIImage) -> CIImage {
        guard params.cyanRedShift != 0 || params.magentaGreenShift != 0 || params.yellowBlueShift != 0 else {
            return image
        }

        guard let filter = CIFilter(name: "CIColorBalance") else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)

        // Convert shifts to CMYK vector
        let vector = CIVector(
            x: CGFloat(params.cyanRedShift),
            y: CGFloat(params.magentaGreenShift),
            z: CGFloat(params.yellowBlueShift),
            w: 0
        )
        filter.setValue(vector, forKey: "inputColorBalance")

        return filter.outputImage ?? image
    }

    private func applyFade(to image: CIImage) -> CIImage {
        // Lift blacks by adjusting contrast and brightness
        guard let filter = CIFilter(name: "CIColorControls") else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)

        // Reduce contrast and lift brightness to create fade effect
        let fadedContrast = 1.0 - (params.fade * 0.3)
        let fadedBrightness = params.fade * 0.1

        filter.setValue(fadedContrast, forKey: kCIInputContrastKey)
        filter.setValue(fadedBrightness, forKey: kCIInputBrightnessKey)

        return filter.outputImage ?? image
    }

    private func applyVignette(to image: CIImage) -> CIImage {
        guard let filter = CIFilter(name: "CIVignette") else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(params.vignette * 2.0, forKey: kCIInputIntensityKey)
        filter.setValue(params.vignette * 2.0, forKey: "inputRadius")

        return filter.outputImage ?? image
    }

    private func applyGrain(to image: CIImage, context: CIContext) -> CIImage {
        // Create noise image
        guard let noiseFilter = CIFilter(name: "CIRandomGenerator") else { return image }

        let noiseImage = noiseFilter.outputImage ?? image

        // Adjust noise appearance
        guard let noiseAdjustFilter = CIFilter(name: "CIColorControls") else { return image }
        noiseAdjustFilter.setValue(noiseImage, forKey: kCIInputImageKey)
        noiseAdjustFilter.setValue(params.grain * 0.5, forKey: kCIInputSaturationKey)
        noiseAdjustFilter.setValue(0.8, forKey: kCIInputContrastKey)

        guard let adjustedNoise = noiseAdjustFilter.outputImage else { return image }

        // Blend noise with original image
        guard let blendFilter = CIFilter(name: "CIOverlayBlendMode") else { return image }

        blendFilter.setValue(image, forKey: kCIInputImageKey)
        blendFilter.setValue(adjustedNoise, forKey: kCIInputBackgroundImageKey)

        return blendFilter.outputImage ?? image
    }
}

// MARK: - Film Simulation Presets
extension FilmSimulation {
    /// Original - Không có bộ lọc
    static let original = FilmSimulation(
        type: .original,
        params: FilmSimulationParams(
            saturation: 1.0,
            contrast: 1.0,
            brightness: 0.0,
            temperature: 5500,
            tint: 0.0,
            highlights: 0.0,
            shadows: 0.0,
            grain: 0.0,
            vignette: 0.0,
            fade: 0.0,
            cyanRedShift: 0.0,
            magentaGreenShift: 0.0,
            yellowBlueShift: 0.0
        ),
        description: "Không có bộ lọc"
    )

    /// Kodak Portra 400 - Tông màu ấm, da thịt tự nhiên
    static let kodakPortra400 = FilmSimulation(
        type: .kodakPortra400,
        params: FilmSimulationParams(
            saturation: 0.85,
            contrast: 0.95,
            brightness: 0.05,
            temperature: 6200,
            tint: 0.1,
            highlights: -0.15,
            shadows: 0.2,
            grain: 0.12,
            vignette: 0.15,
            fade: 0.1,
            cyanRedShift: 0.15,
            magentaGreenShift: -0.05,
            yellowBlueShift: 0.1
        ),
        description: "Tông màu warm, da thịt tự nhiên, hoàn hảo cho portrait"
    )

    /// Fuji Velvia - Màu sắc rực rỡ, độ bão hòa cao
    static let fujiVelvia = FilmSimulation(
        type: .fujiVelvia,
        params: FilmSimulationParams(
            saturation: 1.4,
            contrast: 1.2,
            brightness: 0.0,
            temperature: 5800,
            tint: 0.0,
            highlights: -0.2,
            shadows: -0.1,
            grain: 0.05,
            vignette: 0.2,
            fade: 0.0,
            cyanRedShift: -0.1,
            magentaGreenShift: 0.1,
            yellowBlueShift: -0.05
        ),
        description: "Màu sắc sống động, phù hợp phong cảnh thiên nhiên"
    )

    /// Ilford B&W - Đen trắng cổ điển
    static let ilfordBW = FilmSimulation(
        type: .ilfordBW,
        params: FilmSimulationParams(
            saturation: 0.0,
            contrast: 1.3,
            brightness: 0.0,
            temperature: 5500,
            tint: 0.0,
            highlights: -0.1,
            shadows: -0.2,
            grain: 0.2,
            vignette: 0.25,
            fade: 0.05,
            cyanRedShift: 0.0,
            magentaGreenShift: 0.0,
            yellowBlueShift: 0.0
        ),
        description: "Đen trắng cổ điển, grain mềm, phù hợp street photography"
    )

    /// CineStill 800T - Tông màu điện ảnh, halation đỏ
    static let cineStill800T = FilmSimulation(
        type: .cineStill800T,
        params: FilmSimulationParams(
            saturation: 0.9,
            contrast: 1.1,
            brightness: 0.02,
            temperature: 3800,
            tint: -0.15,
            highlights: 0.1,
            shadows: 0.15,
            grain: 0.18,
            vignette: 0.3,
            fade: 0.15,
            cyanRedShift: -0.2,
            magentaGreenShift: -0.1,
            yellowBlueShift: 0.2
        ),
        description: "Tông màu điện ảnh, halation đỏ, hoàn hảo cho night photography"
    )

    /// Danh sách tất cả presets
    static let allPresets: [FilmSimulation] = [
        .original,
        .kodakPortra400,
        .fujiVelvia,
        .ilfordBW,
        .cineStill800T
    ]
}

// MARK: - Film Simulation Manager
/// ViewModel quản lý mô phỏng phim
@MainActor
class FilmSimulationManager: ObservableObject {
    // MARK: - Published Properties

    /// Phim hiện tại đang chọn
    @Published var currentFilm: FilmPresetType = .original

    /// Intensity của film simulation (0.0 - 1.0)
    @Published var intensity: Float = 1.0

    /// Processed preview image
    @Published var processedPreview: CGImage?

    // MARK: - Private Properties

    /// CIContext để xử lý ảnh
    private var ciContext: CIContext?

    /// Film simulation hiện tại
    private var currentSimulation: FilmSimulation?

    // MARK: - Initialization

    init() {
        setupCIContext()
    }

    private func setupCIContext() {
        let options: [CIContextOption: Any] = [
            .useSoftwareRenderer: false,
            .workingColorSpace: CGColorSpaceCreateDeviceRGB(),
            .outputPremultiplied: true
        ]
        ciContext = CIContext(options: options)
    }

    // MARK: - Film Selection

    /// Chọn phim mô phỏng
    func selectFilm(_ type: FilmPresetType) {
        currentFilm = type

        switch type {
        case .original:
            currentSimulation = nil
        case .kodakPortra400:
            currentSimulation = .kodakPortra400
        case .fujiVelvia:
            currentSimulation = .fujiVelvia
        case .ilfordBW:
            currentSimulation = .ilfordBW
        case .cineStill800T:
            currentSimulation = .cineStill800T
        }
    }

    /// Set intensity
    func setIntensity(_ value: Float) {
        intensity = max(0, min(1, value))
    }

    // MARK: - Frame Processing

    /// Xử lý frame từ camera
    func processFrame(_ pixelBuffer: CVPixelBuffer) {
        guard let simulation = currentSimulation,
              let context = ciContext else {
            processedPreview = nil
            return
        }

        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
        let processedImage = simulation.apply(to: ciImage, context: context)

        // Blend with original based on intensity
        let finalImage: CIImage
        if intensity < 1.0 {
            let originalImage = ciImage
            guard let dissolveFilter = CIFilter(name: "CIDissolveTransition") else {
                finalImage = processedImage
                return
            }
            dissolveFilter.setValue(originalImage, forKey: kCIInputImageKey)
            dissolveFilter.setValue(processedImage, forKey: kCIInputTargetImageKey)
            dissolveFilter.setValue(intensity, forKey: kCIInputTimeKey)
            finalImage = dissolveFilter.outputImage ?? processedImage
        } else {
            finalImage = processedImage
        }

        // Render to CGImage
        if let cgImage = context.createCGImage(finalImage, from: finalImage.extent) {
            processedPreview = cgImage
        }
    }

    /// Xử lý ảnh tĩnh (cho việc chụp)
    func processStaticImage(_ image: CIImage) -> CIImage? {
        guard let simulation = currentSimulation,
              let context = ciContext else {
            return nil
        }

        let processedImage = simulation.apply(to: image, context: context)

        // Blend with original based on intensity
        if intensity < 1.0 {
            guard let dissolveFilter = CIFilter(name: "CIDissolveTransition") else {
                return processedImage
            }
            dissolveFilter.setValue(image, forKey: kCIInputImageKey)
            dissolveFilter.setValue(processedImage, forKey: kCIInputTargetImageKey)
            dissolveFilter.setValue(intensity, forKey: kCIInputTimeKey)
            return dissolveFilter.outputImage ?? processedImage
        }

        return processedImage
    }

    /// Reset về mặc định
    func reset() {
        currentFilm = .original
        currentSimulation = nil
        intensity = 1.0
        processedPreview = nil
    }
}
