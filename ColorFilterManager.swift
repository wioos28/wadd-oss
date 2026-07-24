//
//  ColorFilterManager.swift
//  ProCameraApp
//
//  Xử lý bộ lọc màu thời gian thực (Real-time Color Grading)
//  Sử dụng Core Image / CIColorCube / 3D LUT
//

import AVFoundation
import CoreImage
import Combine
import SwiftUI

// MARK: - ColorFilterManager
/// ViewModel quản lý việc áp dụng bộ lọc màu real-time
@MainActor
class ColorFilterManager: ObservableObject {
    // MARK: - Published Properties

    /// CIContext để tối ưu performance
    private var ciContext: CIContext?

    /// LUT hiện tại đang áp dụng
    @Published var currentLUT: FilterPreset?

    /// Intensity of current filter (0.0 - 1.0)
    @Published var filterIntensity: Float = 1.0

    /// Active color adjustments
    @Published var colorAdjustments = ColorAdjustments()

    /// Filter preview image
    @Published var processedPreview: CGImage?

    // MARK: - Private Properties

    /// CIFilter cho color adjustments
    private var colorControlsFilter: CIFilter?
    private var temperatureFilter: CIFilter?
    private var exposureFilter: CIFilter?
    private var highlightsFilter: CIFilter?
    private var shadowsFilter: CIFilter?
    private var vignetteFilter: CIFilter?
    private var grainFilter: CIFilter?

    /// CIImage cache
    private var lastProcessedFrame: CIImage?

    /// Performance tracking
    private var lastProcessTime: CFAbsoluteTime = 0

    // MARK: - Initialization

    init() {
        setupFilters()
        setupCIContext()
    }

    /// Setup Core Image context
    private func setupCIContext() {
        // Use GPU acceleration
        let options: [CIContextOption: Any] = [
            .useSoftwareRenderer: false,
            .workingColorSpace: CGColorSpaceCreateDeviceRGB(),
            .outputPremultiplied: true
        ]

        ciContext = CIContext(options: options)
    }

    /// Initialize all CIFilters
    private func setupFilters() {
        colorControlsFilter = CIFilter(name: "CIColorControls")
        temperatureFilter = CIFilter(name: "CITemperatureAndTint")
        exposureFilter = CIFilter(name: "CIExposureAdjust")
        highlightsFilter = CIFilter(name: "CIHighlightShadowAdjust")
        shadowsFilter = CIFilter(name: "CIHighlightShadowAdjust")
        vignetteFilter = CIFilter(name: "CIVignette")
        grainFilter = CIFilter(name: "CINoiseReduction")
    }

    // MARK: - Frame Processing

    /// Xử lý frame từ camera và áp dụng filters
    /// - Parameter pixelBuffer: Pixel buffer từ AVCaptureVideoDataOutput
    func processFrame(_ pixelBuffer: CVPixelBuffer) {
        let startTime = CFAbsoluteTimeGetCurrent()

        // Convert pixel buffer to CIImage
        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)

        // Apply all filters
        guard let processedImage = applyFilters(to: ciImage) else {
            return
        }

        // Render to CGImage for display
        if let cgImage = ciContext?.createCGImage(
            processedImage,
            from: processedImage.extent
        ) {
            processedPreview = cgImage
        }

        // Track performance
        let processTime = CFAbsoluteTimeGetCurrent() - startTime
        lastProcessTime = processTime

        // Log if processing takes too long (> 33ms = 30fps)
        if processTime > 0.033 {
            print("⚠️ Color processing slow: \(String(format: "%.2f", processTime * 1000))ms")
        }
    }

    /// Áp dụng tất cả filters lên CIImage
    private func applyFilters(to inputImage: CIImage) -> CIImage? {
        var processedImage = inputImage

        // 1. Apply Exposure
        processedImage = applyExposure(to: processedImage)

        // 2. Apply Color Controls (Saturation, Contrast, Brightness)
        processedImage = applyColorControls(to: processedImage)

        // 3. Apply Temperature
        processedImage = applyTemperature(to: processedImage)

        // 4. Apply Highlights/Shadows
        processedImage = applyHighlightsShadows(to: processedImage)

        // 5. Apply Vignette
        processedImage = applyVignette(to: processedImage)

        // 6. Apply Grain
        processedImage = applyGrain(to: processedImage)

        // 7. Apply LUT if active
        if let lut = currentLUT, filterIntensity > 0 {
            processedImage = applyLUT(to: processedImage, lut: lut)
        }

        return processedImage
    }

    // MARK: - Filter Application Methods

    /// Apply Exposure adjustment
    private func applyExposure(to image: CIImage) -> CIImage {
        guard let filter = exposureFilter else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(colorAdjustments.exposure, forKey: kCIInputEVKey)

        return filter.outputImage ?? image
    }

    /// Apply Color Controls (Saturation, Contrast, Brightness)
    private func applyColorControls(to image: CIImage) -> CIImage {
        guard let filter = colorControlsFilter else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(colorAdjustments.saturation, forKey: kCIInputSaturationKey)
        filter.setValue(colorAdjustments.contrast, forKey: kCIInputContrastKey)
        filter.setValue(colorAdjustments.brightness, forKey: kCIInputBrightnessKey)

        return filter.outputImage ?? image
    }

    /// Apply Color Temperature
    private func applyTemperature(to image: CIImage) -> CIImage {
        guard let filter = temperatureFilter else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)

        // CITemperatureAndTint expects temperature in Kelvin (2000-10000)
        // and tint in range (-100 to 100)
        let temperature = CGFloat(colorAdjustments.temperature)
        let tint = CGFloat(colorAdjustments.tint * 100.0) // Scale tint to -100...100

        filter.setValue(CIVector(x: temperature, y: tint), forKey: "inputNeutral")
        filter.setValue(CIVector(x: 6500, y: 0), forKey: "inputTargetNeutral")

        return filter.outputImage ?? image
    }

    /// Apply Highlights and Shadows adjustments
    private func applyHighlightsShadows(to image: CIImage) -> CIImage {
        guard let filter = highlightsFilter else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)

        // Map -1...1 to 0...1 range
        let highlightAmount = (colorAdjustments.highlights + 1.0) / 2.0
        let shadowAmount = (colorAdjustments.shadows + 1.0) / 2.0

        filter.setValue(highlightAmount, forKey: "inputHighlightAmount")
        filter.setValue(shadowAmount, forKey: "inputShadowAmount")

        return filter.outputImage ?? image
    }

    /// Apply Vignette effect
    private func applyVignette(to image: CIImage) -> CIImage {
        guard let filter = vignetteFilter, colorAdjustments.vignette > 0 else {
            return image
        }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(colorAdjustments.vignette * 2.0, forKey: kCIInputIntensityKey)
        filter.setValue(colorAdjustments.vignette * 2.0, forKey: "inputRadius")

        return filter.outputImage ?? image
    }

    /// Apply Grain effect (simulated noise)
    private func applyGrain(to image: CIImage) -> CIImage {
        guard let filter = grainFilter, colorAdjustments.grain > 0 else {
            return image
        }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(colorAdjustments.grain * 0.5, forKey: kCIInputNoiseLevelKey)
        filter.setValue(0.8, forKey: kCIInputSharpnessKey)

        return filter.outputImage ?? image
    }

    /// Apply 3D LUT using CIColorCube
    private func applyLUT(to image: CIImage, lut: FilterPreset) -> CIImage {
        guard let cubeData = lut.cubeData else { return image }

        let size = lut.cubeSize
        let data = Data(bytes: cubeData, count: size * size * size * 4 * MemoryLayout<Float>.size)

        guard let filter = CIFilter(name: "CIColorCube") else { return image }

        filter.setValue(image, forKey: kCIInputImageKey)
        filter.setValue(size, forKey: "inputCubeDimension")
        filter.setValue(data, forKey: "inputCubeData")

        // Apply with intensity
        if let outputImage = filter.outputImage {
            return blendWithOriginal(original: image, filtered: outputImage, intensity: filterIntensity)
        }

        return image
    }

    /// Blend filtered image with original based on intensity
    private func blendWithOriginal(original: CIImage, filtered: CIImage, intensity: Float) -> CIImage {
        guard let blendFilter = CIFilter(name: "CILinearDodgeBlendMode") else {
            return filtered
        }

        // Use dissolvBlendMode for intensity blending
        guard let dissolveFilter = CIFilter(name: "CIDissolveTransition") else {
            return filtered
        }

        dissolveFilter.setValue(original, forKey: kCIInputImageKey)
        dissolveFilter.setValue(filtered, forKey: kCIInputTargetImageKey)
        dissolveFilter.setValue(intensity, forKey: kCIInputTimeKey)

        return dissolveFilter.outputImage ?? filtered
    }

    // MARK: - Color Adjustment Methods

    /// Set saturation value
    func setSaturation(_ value: Float) {
        colorAdjustments.saturation = value
    }

    /// Set contrast value
    func setContrast(_ value: Float) {
        colorAdjustments.contrast = value
    }

    /// Set brightness value
    func setBrightness(_ value: Float) {
        colorAdjustments.brightness = value
    }

    /// Set temperature value (Kelvin)
    func setTemperature(_ kelvin: Float) {
        colorAdjustments.temperature = kelvin
    }

    /// Set tint value (-1.0 to 1.0)
    func setTint(_ value: Float) {
        colorAdjustments.tint = value
    }

    /// Set exposure EV
    func setExposure(_ ev: Float) {
        colorAdjustments.exposure = ev
    }

    /// Set highlights
    func setHighlights(_ value: Float) {
        colorAdjustments.highlights = value
    }

    /// Set shadows
    func setShadows(_ value: Float) {
        colorAdjustments.shadows = value
    }

    /// Set vignette
    func setVignette(_ value: Float) {
        colorAdjustments.vignette = value
    }

    /// Set grain
    func setGrain(_ value: Float) {
        colorAdjustments.grain = value
    }

    // MARK: - LUT Management

    /// Load LUT from file
    func loadLUT(named name: String, from bundle: Bundle = .main) -> FilterPreset? {
        guard let url = bundle.url(forResource: name, withExtension: "cube") else {
            print("LUT file not found: \(name).cube")
            return nil
        }

        return loadLUT(from: url)
    }

    /// Load LUT from URL
    func loadLUT(from url: URL) -> FilterPreset? {
        do {
            let lutData = try Data(contentsOf: url)
            let preset = try FilterPreset(lutData: lutData, name: url.lastPathComponent)
            return preset
        } catch {
            print("Error loading LUT: \(error)")
            return nil
        }
    }

    /// Apply a filter preset
    func applyFilter(_ preset: FilterPreset?) {
        currentLUT = preset

        // Apply preset adjustments if available
        if let preset = preset, preset.cubeData.isEmpty {
            colorAdjustments = preset.storedAdjustments
        }
    }

    /// Remove current filter
    func removeFilter() {
        currentLUT = nil
        filterIntensity = 1.0
        processedPreview = nil // Clear stale overlay
    }

    /// Reset all adjustments
    func resetAll() {
        colorAdjustments = ColorAdjustments()
        currentLUT = nil
        filterIntensity = 1.0
        processedPreview = nil // Clear stale overlay
    }

    // MARK: - Performance

    /// Get current processing time
    func getProcessingTime() -> CFAbsoluteTime {
        return lastProcessTime
    }

    /// Check if real-time processing is feasible
    func isRealTimeCapable() -> Bool {
        return lastProcessTime < 0.033 // 30fps target
    }
}

// MARK: - Color Adjustments
/// Cài đặt điều chỉnh màu
struct ColorAdjustments {
    /// Exposure (EV): -3.0 to +3.0
    var exposure: Float = 0.0

    /// Saturation: 0.0 to 2.0
    var saturation: Float = 1.0

    /// Contrast: 0.0 to 2.0
    var contrast: Float = 1.0

    /// Brightness: -1.0 to 1.0
    var brightness: Float = 0.0

    /// Temperature (Kelvin): 2000 to 10000
    var temperature: Float = 5500.0

    /// Tint: -1.0 to 1.0
    var tint: Float = 0.0

    /// Highlights: -1.0 to 1.0
    var highlights: Float = 0.0

    /// Shadows: -1.0 to 1.0
    var shadows: Float = 0.0

    /// Vignette: 0.0 to 1.0
    var vignette: Float = 0.0

    /// Grain (Noise): 0.0 to 1.0
    var grain: Float = 0.0
}

// MARK: - Filter Preset
/// Preset bộ lọc màu
class FilterPreset: Identifiable {
    let id = UUID()
    let name: String
    let cubeData: [Float]
    let cubeSize: Int
    let storedAdjustments: ColorAdjustments

    init(lutData: Data, name: String) throws {
        self.name = name

        // Parse .cube file
        var size = 0
        var data: [Float] = []

        let content = String(data: lutData, encoding: .utf8) ?? ""
        var isDataSection = false

        for line in content.components(separatedBy: .newlines) {
            let trimmed = line.trimmingCharacters(in: .whitespaces)

            if trimmed.isEmpty || trimmed.hasPrefix("#") {
                continue
            }

            if trimmed.lowercased().hasPrefix("title") {
                continue
            }

            if trimmed.lowercased().hasPrefix("lut_3d_size") {
                let parts = trimmed.components(separatedBy: .whitespaces)
                if let sizeStr = parts.last, let parsedSize = Int(sizeStr) {
                    size = parsedSize
                }
                continue
            }

            if trimmed.lowercased() == "data_min" || trimmed.lowercased() == "data_max" {
                continue
            }

            // Parse data line (R G B values)
            let components = trimmed.components(separatedBy: .whitespaces)
            if components.count == 3, let r = Float(components[0]),
               let g = Float(components[1]), let b = Float(components[2]) {
                data.append(r)
                data.append(g)
                data.append(b)
                data.append(1.0) // Alpha
            }
        }

        guard size > 0 else {
            throw FilterError.invalidCubeSize
        }

        guard data.count == size * size * size * 4 else {
            throw FilterError.invalidDataCount
        }

        self.cubeSize = size
        self.cubeData = data
        self.storedAdjustments = ColorAdjustments()
    }

    /// Pre-made filter: Vivid
    static let vivid = FilterPreset(
        name: "Vivid",
        adjustments: ColorAdjustments(
            saturation: 1.3,
            contrast: 1.1,
            brightness: 0.05
        )
    )

    /// Pre-made filter: Warm
    static let warm = FilterPreset(
        name: "Warm",
        adjustments: ColorAdjustments(
            temperature: 7000,
            saturation: 1.1,
            brightness: 0.05
        )
    )

    /// Pre-made filter: Cool
    static let cool = FilterPreset(
        name: "Cool",
        adjustments: ColorAdjustments(
            temperature: 4000,
            saturation: 0.9,
            contrast: 1.05
        )
    )

    /// Pre-made filter: B&W
    static let blackAndWhite = FilterPreset(
        name: "B&W",
        adjustments: ColorAdjustments(
            saturation: 0.0,
            contrast: 1.2,
            brightness: 0.0
        )
    )

    /// Pre-made filter: Film
    static let film = FilterPreset(
        name: "Film",
        adjustments: ColorAdjustments(
            saturation: 0.9,
            contrast: 1.15,
            brightness: 0.05,
            grain: 0.15,
            vignette: 0.3
        )
    )

    /// Pre-made filter: Portrait
    static let portrait = FilterPreset(
        name: "Portrait",
        adjustments: ColorAdjustments(
            saturation: 1.1,
            contrast: 1.05,
            brightness: 0.1,
            temperature: 6000,
            highlights: -0.2,
            shadows: 0.2
        )
    )

    /// Initialize with adjustments (for presets without LUT data)
    init(name: String, adjustments: ColorAdjustments) {
        self.name = name
        self.cubeData = []
        self.cubeSize = 0
        self.storedAdjustments = adjustments
    }
}

// MARK: - Filter Errors
enum FilterError: Error, LocalizedError {
    case invalidCubeSize
    case invalidDataCount
    case failedToCreateFilter

    var errorDescription: String? {
        switch self {
        case .invalidCubeSize:
            return "LUT cube size không hợp lệ"
        case .invalidDataCount:
            return "LUT data count không khớp với cube size"
        case .failedToCreateFilter:
            return "Không thể tạo CIFilter"
        }
    }
}

// MARK: - Built-in Filter Presets
extension FilterPreset {
    /// Danh sách các filter presets có sẵn
    static let builtInPresets: [FilterPreset] = [
        .vivid,
        .warm,
        .cool,
        .blackAndWhite,
        .film,
        .portrait
    ]
}
