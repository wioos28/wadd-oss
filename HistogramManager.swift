//
//  HistogramManager.swift
//  ProCameraApp
//
//  Live Histogram - Phân tích luminance real-time từ CMSampleBuffer
//  Trích xuất dữ liệu độ sáng và vẽ biểu đồ trên SwiftUI
//

import AVFoundation
import CoreImage
import CoreVideo
import SwiftUI

// MARK: - HistogramManager
/// ViewModel quản lý việc phân tích histogram real-time
@MainActor
class HistogramManager: ObservableObject {
    // MARK: - Published Properties

    /// Dữ liệu histogram luminance (256 bins, giá trị 0-1)
    @Published var luminanceData: [Float] = Array(repeating: 0, count: 256)

    /// Dữ liệu histogram RGB riêng biệt
    @Published var redData: [Float] = Array(repeating: 0, count: 256)
    @Published var greenData: [Float] = Array(repeating: 0, count: 256)
    @Published var blueData: [Float] = Array(repeating: 0, count: 256)

    /// Trạng thái hoạt động
    @Published var isAnalyzing: Bool = false

    /// Peak luminance value (0-255)
    @Published var peakLuminance: Int = 0

    /// Average luminance (0-255)
    @Published var averageLuminance: Float = 0.0

    // MARK: - Private Properties

    /// CIContext để tối ưu performance
    private var ciContext: CIContext?

    /// Number of histogram bins
    private let binCount = 256

    /// Frame counter để skip frames (performance)
    private var frameCounter: Int = 0
    private let frameSkipInterval: Int = 3 // Process every 3rd frame

    // MARK: - Initialization

    init() {
        setupCIContext()
    }

    /// Setup CIContext với GPU acceleration
    private func setupCIContext() {
        let options: [CIContextOption: Any] = [
            .useSoftwareRenderer: false,
            .workingColorSpace: CGColorSpaceCreateDeviceRGB()
        ]
        ciContext = CIContext(options: options)
    }

    // MARK: - Public Methods

    /// Bắt đầu phân tích histogram
    func startAnalysis() {
        isAnalyzing = true
    }

    /// Dừng phân tích
    func stopAnalysis() {
        isAnalyzing = false
        resetData()
    }

    /// Xử lý frame từ camera và cập nhật histogram
    /// Gọi từ captureOutput trong CameraManager
    /// - Parameter sampleBuffer: CMSampleBuffer từ AVCaptureVideoDataOutput
    func processSampleBuffer(_ sampleBuffer: CMSampleBuffer) {
        guard isAnalyzing else { return }

        // Skip frames for performance
        frameCounter += 1
        guard frameCounter % frameSkipInterval == 0 else { return }

        // Extract pixel buffer
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {
            return
        }

        // Process histogram
        Task {
            await computeHistogram(from: pixelBuffer)
        }
    }

    /// Process pixel buffer directly (alternative entry point)
    func processPixelBuffer(_ pixelBuffer: CVPixelBuffer) {
        guard isAnalyzing else { return }

        frameCounter += 1
        guard frameCounter % frameSkipInterval == 0 else { return }

        Task {
            await computeHistogram(from: pixelBuffer)
        }
    }

    // MARK: - Histogram Computation

    /// Tính toán histogram từ pixel buffer
    private func computeHistogram(from pixelBuffer: CVPixelBuffer) async {
        let startTime = CFAbsoluteTimeGetCurrent()

        // Create CIImage from pixel buffer
        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)

        // Compute luminance histogram using Core Image
        guard let luminance = computeLuminanceHistogram(from: ciImage) else {
            return
        }

        // Compute RGB histograms
        let (r, g, b) = computeRGBHistograms(from: ciImage)

        // Update published properties
        luminanceData = luminance
        redData = r
        greenData = g
        blueData = b

        // Calculate statistics
        calculateStatistics(from: luminance)

        // Track performance
        let processTime = CFAbsoluteTimeGetCurrent() - startTime
        if processTime > 0.033 {
            print("⚠️ Histogram processing slow: \(String(format: "%.2f", processTime * 1000))ms")
        }
    }

    /// Tính histogram luminance sử dụng CIColorMatrix + CIDetector
    private func computeLuminanceHistogram(from image: CIImage) -> [Float]? {
        guard let context = ciContext else { return nil }

        // Get image dimensions
        let extent = image.extent
        let width = Int(extent.width)
        let height = Int(extent.height)

        // Guard against zero dimensions
        guard width > 0, height > 0 else { return nil }

        // Downsample for performance (process at lower resolution)
        let sampleWidth = min(width, 320)
        let sampleHeight = min(height, 240)
        let scaleX = Float(sampleWidth) / Float(width)
        let scaleY = Float(sampleHeight) / Float(height)

        // Scale down
        let scaledImage = image.transformed(by: CGAffineTransform(scaleX: CGFloat(scaleX), y: CGFloat(scaleY)))

        // Render to bitmap
        var bitmap = [UInt8](repeating: 0, count: sampleWidth * sampleHeight * 4)
        context.render(
            scaledImage,
            toBitmap: &bitmap,
            rowBytes: sampleWidth * 4,
            bounds: CGRect(x: 0, y: 0, width: sampleWidth, height: sampleHeight),
            format: .BGRA8,
            colorSpace: CGColorSpaceCreateDeviceRGB()
        )

        // Calculate luminance for each pixel
        // Using standard luminance formula: Y = 0.299R + 0.587G + 0.114B
        var histogram = [Float](repeating: 0, count: binCount)

        for y in 0..<sampleHeight {
            for x in 0..<sampleWidth {
                let offset = (y * sampleWidth + x) * 4

                // BGRA format
                let b = Float(bitmap[offset]) / 255.0
                let g = Float(bitmap[offset + 1]) / 255.0
                let r = Float(bitmap[offset + 2]) / 255.0

                // Calculate luminance
                let luminance = 0.299 * r + 0.587 * g + 0.114 * b

                // Map to bin
                let bin = min(255, max(0, Int(luminance * 255.0)))
                histogram[bin] += 1.0
            }
        }

        // Normalize histogram
        let maxValue = max(histogram.max() ?? 0, 1.0) // Avoid division by zero

        // Normalize to 0-1 range
        return histogram.map { $0 / maxValue }
    }

    /// Tính RGB histograms riêng biệt
    private func computeRGBHistograms(from image: CIImage) -> ([Float], [Float], [Float]) {
        guard let context = ciContext else {
            return (
                Array(repeating: 0, count: binCount),
                Array(repeating: 0, count: binCount),
                Array(repeating: 0, count: binCount)
            )
        }

        let extent = image.extent
        let width = Int(extent.width)
        let height = Int(extent.height)

        // Guard against zero dimensions
        guard width > 0, height > 0 else {
            return (
                Array(repeating: 0, count: binCount),
                Array(repeating: 0, count: binCount),
                Array(repeating: 0, count: binCount)
            )
        }

        let sampleWidth = min(width, 320)
        let sampleHeight = min(height, 240)
        let scaleX = Float(sampleWidth) / Float(width)
        let scaleY = Float(sampleHeight) / Float(height)

        let scaledImage = image.transformed(by: CGAffineTransform(scaleX: CGFloat(scaleX), y: CGFloat(scaleY)))

        var bitmap = [UInt8](repeating: 0, count: sampleWidth * sampleHeight * 4)
        context.render(
            scaledImage,
            toBitmap: &bitmap,
            rowBytes: sampleWidth * 4,
            bounds: CGRect(x: 0, y: 0, width: sampleWidth, height: sampleHeight),
            format: .BGRA8,
            colorSpace: CGColorSpaceCreateDeviceRGB()
        )

        var redHistogram = [Float](repeating: 0, count: binCount)
        var greenHistogram = [Float](repeating: 0, count: binCount)
        var blueHistogram = [Float](repeating: 0, count: binCount)

        for y in 0..<sampleHeight {
            for x in 0..<sampleWidth {
                let offset = (y * sampleWidth + x) * 4

                let b = Int(bitmap[offset])
                let g = Int(bitmap[offset + 1])
                let r = Int(bitmap[offset + 2])

                redHistogram[min(255, max(0, r))] += 1.0
                greenHistogram[min(255, max(0, g))] += 1.0
                blueHistogram[min(255, max(0, b))] += 1.0
            }
        }

        // Normalize (avoid division by zero)
        let maxValue = max(redHistogram.max() ?? 0, greenHistogram.max() ?? 0, blueHistogram.max() ?? 0, 1.0)

        return (
            redHistogram.map { $0 / maxValue },
            greenHistogram.map { $0 / maxValue },
            blueHistogram.map { $0 / maxValue }
        )
    }

    /// Tính toán thống kê
    private func calculateStatistics(from histogram: [Float]) {
        var totalLuminance: Float = 0
        var totalWeight: Float = 0
        var peakBin: Int = 0
        var peakValue: Float = 0

        for (bin, value) in histogram.enumerated() {
            totalLuminance += Float(bin) * value
            totalWeight += value

            if value > peakValue {
                peakValue = value
                peakBin = bin
            }
        }

        peakLuminance = peakBin
        averageLuminance = totalWeight > 0 ? totalLuminance / totalWeight : 0
    }

    /// Reset dữ liệu
    private func resetData() {
        luminanceData = Array(repeating: 0, count: binCount)
        redData = Array(repeating: 0, count: binCount)
        greenData = Array(repeating: 0, count: binCount)
        blueData = Array(repeating: 0, count: binCount)
        peakLuminance = 0
        averageLuminance = 0
    }
}

// MARK: - HistogramView
/// SwiftUI View hiển thị Live Histogram
struct HistogramView: View {
    @ObservedObject var histogramManager: HistogramManager

    /// Loại histogram cần hiển thị
    enum HistogramType {
        case luminance
        case rgb
    }

    let type: HistogramType

    var body: some View {
        GeometryReader { geometry in
            switch type {
            case .luminance:
                luminanceHistogram(in: geometry)
            case .rgb:
                rgbHistogram(in: geometry)
            }
        }
        .background(Color.black.opacity(0.6))
        .cornerRadius(8)
    }

    /// Vẽ luminance histogram
    @ViewBuilder
    private func luminanceHistogram(in geometry: GeometryProxy) -> some View {
        Canvas { context, size in
            let width = size.width
            let height = size.height
            let barWidth = width / CGFloat(histogramManager.luminanceData.count)

            // Draw histogram bars
            for (index, value) in histogramManager.luminanceData.enumerated() {
                let barHeight = CGFloat(value) * height
                let x = CGFloat(index) * barWidth
                let y = height - barHeight

                let rect = CGRect(x: x, y: y, width: barWidth + 0.5, height: barHeight)

                // Gradient from black to white
                let grayValue = CGFloat(index) / 255.0
                let color = Color(white: grayValue)

                context.fill(Path(rect), with: .color(color))
            }

            // Draw peak marker
            let peakX = CGFloat(histogramManager.peakLuminance) * barWidth
            context.stroke(
                Path { path in
                    path.move(to: CGPoint(x: peakX, y: 0))
                    path.addLine(to: CGPoint(x: peakX, y: height))
                },
                with: .color(.white),
                lineWidth: 1
            )
        }
    }

    /// Vẽ RGB histogram
    @ViewBuilder
    private func rgbHistogram(in geometry: GeometryProxy) -> some View {
        Canvas { context, size in
            let width = size.width
            let height = size.height
            let barWidth = width / CGFloat(histogramManager.redData.count)

            // Draw each channel with opacity
            drawChannel(
                data: histogramManager.redData,
                color: .red,
                context: context,
                size: size,
                barWidth: barWidth
            )

            drawChannel(
                data: histogramManager.greenData,
                color: .green,
                context: context,
                size: size,
                barWidth: barWidth
            )

            drawChannel(
                data: histogramManager.blueData,
                color: .blue,
                context: context,
                size: size,
                barWidth: barWidth
            )
        }
    }

    /// Helper để vẽ một kênh màu
    private func drawChannel(
        data: [Float],
        color: Color,
        context: GraphicsContext,
        size: CGSize,
        barWidth: CGFloat
    ) {
        let height = size.height

        for (index, value) in data.enumerated() {
            let barHeight = CGFloat(value) * height * 0.8 // Slightly smaller for blending
            let x = CGFloat(index) * barWidth
            let y = height - barHeight

            let rect = CGRect(x: x, y: y, width: barWidth + 0.5, height: barHeight)

            context.fill(Path(rect), with: .color(color.opacity(0.4)))
        }
    }
}

// MARK: - Compact Histogram
/// Histogram nhỏ gọn cho góc màn hình
struct CompactHistogramView: View {
    @ObservedObject var histogramManager: HistogramManager

    var body: some View {
        VStack(alignment: .trailing, spacing: 4) {
            // Mini histogram
            HistogramView(histogramManager: histogramManager, type: .luminance)
                .frame(width: 120, height: 60)

            // Stats
            HStack(spacing: 8) {
                Text("P: \(histogramManager.peakLuminance)")
                    .font(.system(size: 8, weight: .medium, design: .monospaced))
                    .foregroundColor(.white)

                Text("A: \(Int(histogramManager.averageLuminance))")
                    .font(.system(size: 8, weight: .medium, design: .monospaced))
                    .foregroundColor(.white)
            }
        }
        .padding(6)
        .background(Color.black.opacity(0.7))
        .cornerRadius(8)
    }
}
