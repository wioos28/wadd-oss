//
//  FocusPeakingManager.swift
//  ProCameraApp
//
//  Focus Peaking - Làm nổi bật viền vật thể đang được lấy nét
//  Sử dụng Core Image (CIEdges) hoặc custom shader để detect edges
//

import AVFoundation
import CoreImage
import CoreVideo
import SwiftUI

// MARK: - FocusPeakingManager
/// ViewModel quản lý Focus Peaking visualization
@MainActor
class FocusPeakingManager: ObservableObject {
    // MARK: - Published Properties

    /// Trạng thái bật/tắt Focus Peaking
    @Published var isEnabled: Bool = false

    /// Màu sắc highlight edges
    @Published var highlightColor: FocusPeakingColor = .green

    /// Cường độ của edge detection (0.0 - 2.0)
    @Published var intensity: Float = 1.0

    /// Ngưỡng threshold cho edge detection
    @Published var threshold: Float = 0.1

    /// Kết quả edge detection image (overlay trên preview)
    @Published var edgeImage: CGImage?

    /// Performance metrics
    @Published var processingTime: CFAbsoluteTime = 0

    // MARK: - Private Properties

    /// CIContext để xử lý image
    private var ciContext: CIContext?

    /// CIFilter cho edge detection
    private var edgesFilter: CIFilter?
    private var colorControlsFilter: CIFilter?
    private var falseColorFilter: CIFilter?

    /// Frame counter để skip frames
    private var frameCounter: Int = 0
    private let frameSkipInterval: Int = 2 // Process every 2nd frame

    /// Previous edge image để blend
    private var previousEdgeImage: CIImage?

    // MARK: - Focus Peaking Color Options
    enum FocusPeakingColor: String, CaseIterable, Identifiable {
        case green = "Green"
        case red = "Red"
        case blue = "Blue"
        case white = "White"
        case yellow = "Yellow"

        var id: String { rawValue }

        /// SwiftUI Color
        var color: Color {
            switch self {
            case .green: return .green
            case .red: return .red
            case .blue: return .blue
            case .white: return .white
            case .yellow: return .yellow
            }
        }

        /// CIImage false color vector
        var falseColorVector: CIVector {
            switch self {
            case .green: return CIVector(x: 0, y: 1, z: 0, w: 1)
            case .red: return CIVector(x: 1, y: 0, z: 0, w: 1)
            case .blue: return CIVector(x: 0, y: 0, z: 1, w: 1)
            case .white: return CIVector(x: 1, y: 1, z: 1, w: 1)
            case .yellow: return CIVector(x: 1, y: 1, z: 0, w: 1)
            }
        }
    }

    // MARK: - Initialization

    init() {
        setupCIContext()
        setupFilters()
    }

    /// Setup CIContext
    private func setupCIContext() {
        let options: [CIContextOption: Any] = [
            .useSoftwareRenderer: false,
            .workingColorSpace: CGColorSpaceCreateDeviceRGB(),
            .outputPremultiplied: true
        ]
        ciContext = CIContext(options: options)
    }

    /// Initialize CIFilters
    private func setupFilters() {
        // CIEdges: Detects edges using Canny edge detection algorithm
        edgesFilter = CIFilter(name: "CIEdges")

        // CIColorControls: For adjusting intensity
        colorControlsFilter = CIFilter(name: "CIColorControls")

        // CIFalseColor: Apply custom color to edges
        falseColorFilter = CIFilter(name: "CIFalseColor")
    }

    // MARK: - Control Methods

    /// Bật/tắt Focus Peaking
    func toggle() {
        isEnabled.toggle()
        if !isEnabled {
            edgeImage = nil
        }
    }

    /// Bật Focus Peaking
    func enable() {
        isEnabled = true
    }

    /// Tắt Focus Peaking
    func disable() {
        isEnabled = false
        edgeImage = nil
    }

    /// Đặt màu highlight
    func setHighlightColor(_ color: FocusPeakingColor) {
        highlightColor = color
    }

    /// Đặt cường độ edge detection
    func setIntensity(_ value: Float) {
        intensity = max(0, min(2.0, value))
    }

    /// Đặt ngưỡng threshold
    func setThreshold(_ value: Float) {
        threshold = max(0, min(1.0, value))
    }

    // MARK: - Frame Processing

    /// Xử lý frame từ camera và tạo edge overlay
    /// Gọi từ captureOutput trong CameraManager
    /// - Parameter sampleBuffer: CMSampleBuffer từ AVCaptureVideoDataOutput
    func processSampleBuffer(_ sampleBuffer: CMSampleBuffer) {
        guard isEnabled else { return }

        // Skip frames for performance
        frameCounter += 1
        guard frameCounter % frameSkipInterval == 0 else { return }

        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {
            return
        }

        Task {
            await processPixelBuffer(pixelBuffer)
        }
    }

    /// Process pixel buffer directly
    func processPixelBuffer(_ pixelBuffer: CVPixelBuffer) async {
        guard isEnabled else { return }

        let startTime = CFAbsoluteTimeGetCurrent()

        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)

        guard let processedEdge = applyFocusPeaking(to: ciImage) else {
            return
        }

        // Render to CGImage for overlay
        if let cgImage = ciContext?.createCGImage(
            processedEdge,
            from: processedEdge.extent
        ) {
            edgeImage = cgImage
        }

        processingTime = CFAbsoluteTimeGetCurrent() - startTime
    }

    // MARK: - Edge Detection Pipeline

    /// Áp dụng Focus Peaking effect lên image
    private func applyFocusPeaking(to inputImage: CIImage) -> CIImage? {
        guard let edgesFilter = edgesFilter else { return nil }

        // Step 1: Edge Detection
        // CIEdges uses Sobel edge detection
        edgesFilter.setValue(inputImage, forKey: kCIInputImageKey)
        edgesFilter.setValue(intensity * 5.0, forKey: kCIInputIntensityKey)

        guard let edgeImage = edgesFilter.outputImage else {
            return nil
        }

        // Step 2: Enhance edges (optional - makes them more visible)
        guard let enhancedEdges = enhanceEdges(edgeImage) else {
            return edgeImage
        }

        // Step 3: Apply false color
        guard let coloredEdges = applyFalseColor(to: enhancedEdges) else {
            return enhancedEdges
        }

        // Step 4: Threshold to reduce noise
        guard let thresholded = applyThreshold(to: coloredEdges) else {
            return coloredEdges
        }

        return thresholded
    }

    /// Enhance edges để visible hơn
    private func enhanceEdges(_ image: CIImage) -> CIImage? {
        guard let colorControls = colorControlsFilter else { return nil }

        colorControls.setValue(image, forKey: kCIInputImageKey)
        colorControls.setValue(intensity * 2.0, forKey: kCIInputContrastKey)
        colorControls.setValue(0.5, forKey: kCIInputBrightnessKey)

        return colorControls.outputImage
    }

    /// Áp dụng false color (màu tùy chỉnh) cho edges
    private func applyFalseColor(to image: CIImage) -> CIImage? {
        guard let falseColor = CIFilter(name: "CIFalseColor") else { return nil }

        falseColor.setValue(image, forKey: kCIInputImageKey)
        falseColor.setValue(highlightColor.falseColorVector, forKey: "inputColor0")
        falseColor.setValue(CIVector(x: 0, y: 0, z: 0, w: 0), forKey: "inputColor1")

        return falseColor.outputImage
    }

    /// Threshold để loại bỏ noise
    private func applyThreshold(to image: CIImage) -> CIImage? {
        guard let colorControls = CIFilter(name: "CIColorControls") else { return nil }

        colorControls.setValue(image, forKey: kCIInputImageKey)
        colorControls.setValue(threshold * 5.0, forKey: kCIInputBrightnessKey)
        colorControls.setValue(3.0, forKey: kCIInputContrastKey)

        return colorControls.outputImage
    }
}

// MARK: - FocusPeakingOverlay
/// SwiftUI View overlay cho Focus Peaking
struct FocusPeakingOverlay: View {
    @ObservedObject var focusPeakingManager: FocusPeakingManager

    var body: some View {
        if focusPeakingManager.isEnabled, let edgeImage = focusPeakingManager.edgeImage {
            Image(decorative: edgeImage, scale: 1)
                .resizable()
                .ignoresSafeArea()
                .blendMode(.screen) // Screen blend for overlay effect
                .allowsHitTesting(false)
                .opacity(0.8)
        }
    }
}

// MARK: - FocusPeakingControls
/// Controls panel cho Focus Peaking settings
struct FocusPeakingControls: View {
    @ObservedObject var focusPeakingManager: FocusPeakingManager

    var body: some View {
        VStack(spacing: 12) {
            // Toggle
            Toggle(isOn: $focusPeakingManager.isEnabled) {
                HStack {
                    Image(systemName: "scope")
                    Text("Focus Peaking")
                }
                .font(.caption)
                .foregroundColor(.white)
            }
            .tint(.green)

            if focusPeakingManager.isEnabled {
                // Color selector
                HStack {
                    Text("Color")
                        .font(.caption)
                        .foregroundColor(.gray)
                        .frame(width: 50, alignment: .leading)

                    ForEach(FocusPeakingManager.FocusPeakingColor.allCases) { color in
                        Button(action: {
                            focusPeakingManager.setHighlightColor(color)
                        }) {
                            Circle()
                                .fill(color.color)
                                .frame(width: 20, height: 20)
                                .overlay(
                                    Circle()
                                        .stroke(
                                            focusPeakingManager.highlightColor == color
                                                ? Color.white
                                                : Color.clear,
                                            lineWidth: 2
                                        )
                                )
                        }
                    }
                }

                // Intensity slider
                HStack {
                    Text("Intensity")
                        .font(.caption)
                        .foregroundColor(.gray)
                        .frame(width: 60, alignment: .leading)

                    Slider(value: $focusPeakingManager.intensity, in: 0...2.0)
                        .tint(.green)

                    Text(String(format: "%.1f", focusPeakingManager.intensity))
                        .font(.caption)
                        .foregroundColor(.white)
                        .frame(width: 30, alignment: .trailing)
                }

                // Threshold slider
                HStack {
                    Text("Threshold")
                        .font(.caption)
                        .foregroundColor(.gray)
                        .frame(width: 60, alignment: .leading)

                    Slider(value: $focusPeakingManager.threshold, in: 0...1.0)
                        .tint(.green)

                    Text(String(format: "%.2f", focusPeakingManager.threshold))
                        .font(.caption)
                        .foregroundColor(.white)
                        .frame(width: 30, alignment: .trailing)
                }
            }
        }
        .padding(.horizontal, 12)
    }
}
