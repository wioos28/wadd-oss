//
//  WatermarkEngine.swift
//  ProCameraApp
//
//  Engine xử lý Privacy Watermark & Fake Location
//  Xóa GPS EXIF và in watermark lên ảnh
//

import CoreImage
import Foundation
import UIKit

// MARK: - WatermarkEngine
/// Engine xử lý watermark và privacy
@MainActor
class WatermarkEngine: ObservableObject {
    // MARK: - Published Properties

    /// Trạng thái Privacy Mode
    @Published var isPrivacyModeEnabled: Bool = false

    /// Vị trí giả do người dùng nhập
    @Published var fakeLocation: String = "Somewhere on Earth"

    /// Ngày giờ chụp (auto-set khi chụp)
    private var captureDate: Date = Date()

    // MARK: - Private Properties

    /// DateFormatter cho watermark
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        return formatter
    }()

    // MARK: - Public Methods

    /// Cập nhật ngày giờ chụp
    func updateCaptureDate(_ date: Date = Date()) {
        captureDate = date
    }

    /// Xóa GPS metadata từ image data
    /// - Parameter imageData: Data ảnh gốc
    /// - Returns: Data ảnh đã xóa GPS
    func stripGPSMetadata(from imageData: Data) -> Data {
        guard let source = CGImageSourceCreateWithData(imageData as CFData, nil) else {
            return imageData
        }

        // Lấy metadata hiện tại
        guard let metadata = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any] else {
            return imageData
        }

        // Tạo mutable copy
        var mutableMetadata = metadata

        // Xóa GPS dictionary
        mutableMetadata.removeValue(forKey: kCGImagePropertyGPSDictionary as String)

        // Tạo output data
        guard let destinationData = NSMutableData() as CFMutableData? else {
            return imageData
        }

        guard let destination = CGImageDestinationCreateWithData(
            destinationData,
            CGImageSourceGetType(source) ?? kUTTypeJPEG,
            1,
            nil
        ) else {
            return imageData
        }

        // Copy image source
        CGImageSourceAddImageAndMetadata(source, destination, 0, mutableMetadata as CFDictionary)

        // Lấy output data
        if let outputData = destinationData as Data? {
            return outputData
        }

        return imageData
    }

    /// Xóa GPS metadata từ CIImage
    /// - Parameter image: CIImage gốc
    /// - Returns: Data ảnh đã xóa GPS
    func stripGPSMetadata(from image: CIImage) -> Data? {
        // Convert CIImage to UIImage
        let context = CIContext(options: [.useSoftwareRenderer: false])

        guard let cgImage = context.createCGImage(image, from: image.extent) else {
            return nil
        }

        let uiImage = UIImage(cgImage: cgImage)

        // Convert to JPEG data
        guard let imageData = uiImage.jpegData(compressionQuality: 0.95) else {
            return nil
        }

        // Strip GPS metadata
        return stripGPSMetadata(from: imageData)
    }

    /// Vẽ watermark lên ảnh
    /// - Parameters:
    ///   - image: Ảnh gốc (CIImage)
    ///   - date: Ngày giờ chụp
    ///   - location: Vị trí hiển thị
    /// - Returns: CIImage đã có watermark
    func applyWatermark(
        to image: CIImage,
        date: Date = Date(),
        location: String? = nil
    ) -> CIImage {
        let displayDate = dateFormatter.string(from: date)
        let displayLocation = location ?? fakeLocation

        // Tạo watermark image
        guard let watermarkImage = createWatermarkImage(
            date: displayDate,
            location: displayLocation
        ) else {
            return image
        }

        // Convert UIImage to CIImage
        guard let watermarkCIImage = CIImage(image: watermarkImage) else {
            return image
        }

        // Tính toán vị trí watermark (góc dưới bên phải)
        let imageSize = image.extent.size
        let watermarkSize = watermarkCIImage.extent.size

        // Margin từ cạnh
        let margin: CGFloat = 20.0

        // Vị trí watermark
        let watermarkX = imageSize.width - watermarkSize.width - margin
        let watermarkY = margin

        // Di chuyển watermark đến vị trí mong muốn
        let positionedWatermark = watermarkCIImage.transformed(
            by: CGAffineTransform(translationX: watermarkX, y: watermarkY)
        )

        // Compose ảnh gốc với watermark
        guard let compositeFilter = CIFilter(name: "CISourceOverCompositing") else {
            return image
        }

        compositeFilter.setValue(image, forKey: kCIInputImageKey)
        compositeFilter.setValue(positionedWatermark, forKey: kCIInputBackgroundImageKey)

        return compositeFilter.outputImage ?? image
    }

    /// Vẽ watermark lên UIImage
    /// - Parameters:
    ///   - image: UIImage gốc
    ///   - date: Ngày giờ chụp
    ///   - location: Vị trí hiển thị
    /// - Returns: UIImage đã có watermark
    func applyWatermark(
        to image: UIImage,
        date: Date = Date(),
        location: String? = nil
    ) -> UIImage {
        let displayDate = dateFormatter.string(from: date)
        let displayLocation = location ?? fakeLocation

        let renderer = UIGraphicsImageRenderer(size: image.size)
        return renderer.ctx { ctx in
            // Draw original image
            image.draw(at: .zero)

            // Draw watermark
            drawWatermark(
                in: ctx,
                date: displayDate,
                location: displayLocation,
                imageSize: image.size
            )
        }
    }

    /// Xóa GPS và áp dụng watermark lên ảnh
    /// - Parameters:
    ///   - imageData: Data ảnh gốc
    ///   - date: Ngày giờ chụp
    ///   - location: Vị trí hiển thị
    ///   - applyWatermarkFlag: Có áp dụng watermark không
    /// - Returns: Data ảnh đã xử lý
    func processImage(
        imageData: Data,
        date: Date = Date(),
        location: String? = nil,
        applyWatermarkFlag: Bool = true
    ) -> Data {
        // Bước 1: Xóa GPS metadata
        let cleanData = stripGPSMetadata(from: imageData)

        // Nếu không cần watermark, trả về data đã xóa GPS
        guard applyWatermarkFlag else {
            return cleanData
        }

        // Bước 2: Convert sang UIImage để vẽ watermark
        guard let uiImage = UIImage(data: cleanData) else {
            return cleanData
        }

        // Bước 3: Vẽ watermark
        let watermarkedImage = applyWatermark(
            to: uiImage,
            date: date,
            location: location
        )

        // Bước 4: Convert lại sang Data
        return watermarkedImage.jpegData(compressionQuality: 0.95) ?? cleanData
    }

    /// Xóa GPS và áp dụng watermark lên CIImage
    /// - Parameters:
    ///   - image: CIImage gốc
    ///   - date: Ngày giờ chụp
    ///   - location: Vị trí hiển thị
    ///   - applyWatermarkFlag: Có áp dụng watermark không
    /// - Returns: CIImage đã xử lý
    func processImage(
        _ image: CIImage,
        date: Date = Date(),
        location: String? = nil,
        applyWatermarkFlag: Bool = true
    ) -> CIImage {
        guard applyWatermarkFlag else {
            return image
        }

        // Áp dụng watermark
        return applyWatermark(
            to: image,
            date: date,
            location: location
        )
    }

    // MARK: - Private Methods

    /// Tạo watermark image với text
    private func createWatermarkImage(date: String, location: String) -> UIImage? {
        // Tạo text attributes
        let paragraphStyle = NSMutableParagraphStyle()
        paragraphStyle.alignment = .left

        let dateAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.monospacedSystemFont(ofSize: 24, weight: .bold),
            .foregroundColor: UIColor.cyan,
            .paragraphStyle: paragraphStyle
        ]

        let locationAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.monospacedSystemFont(ofSize: 20, weight: .medium),
            .foregroundColor: UIColor.yellow,
            .paragraphStyle: paragraphStyle
        ]

        // Tính toán kích thước text
        let dateSize = (date as NSString).size(withAttributes: dateAttributes)
        let locationSize = (location as NSString).size(withAttributes: locationAttributes)

        let maxWidth = max(dateSize.width, locationSize.width)
        let totalHeight = dateSize.height + locationSize.height + 8 // 8pt spacing

        let padding: CGFloat = 16
        let watermarkSize = CGSize(
            width: maxWidth + padding * 2,
            height: totalHeight + padding * 2
        )

        // Tạo image renderer
        let renderer = UIGraphicsImageRenderer(size: watermarkSize)

        return renderer.image { ctx in
            // Draw background (semi-transparent black)
            let bgRect = CGRect(origin: .zero, size: watermarkSize)
            ctx.cgContext.setFillColor(UIColor.black.withAlphaComponent(0.7).cgColor)
            ctx.cgContext.fillEllipse(in: bgRect.insetBy(dx: -8, dy: -4))

            // Draw border
            ctx.cgContext.setStrokeColor(UIColor.white.withAlphaComponent(0.3).cgColor)
            ctx.cgContext.setLineWidth(1)
            ctx.cgContext.strokeEllipse(in: bgRect.insetBy(dx: -4, dy: -2))

            // Draw date text
            let dateRect = CGRect(
                x: padding,
                y: padding,
                width: dateSize.width,
                height: dateSize.height
            )
            (date as NSString).draw(in: dateRect, withAttributes: dateAttributes)

            // Draw location text
            let locationRect = CGRect(
                x: padding,
                y: padding + dateSize.height + 8,
                width: locationSize.width,
                height: locationSize.height
            )
            (location as NSString).draw(in: locationRect, withAttributes: locationAttributes)
        }
    }

    /// Vẽ watermark trực tiếp lên CGContext
    private func drawWatermark(
        in ctx: CGContext,
        date: String,
        location: String,
        imageSize: CGSize
    ) {
        ctx.saveGState()

        // Tính toán vị trí (góc dưới bên phải)
        let margin: CGFloat = 20
        let lineHeight: CGFloat = 28
        let lineHeight2: CGFloat = 24
        let spacing: CGFloat = 8

        // Tạo text attributes
        let dateAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.monospacedSystemFont(ofSize: 22, weight: .bold),
            .foregroundColor: UIColor.cyan
        ]

        let locationAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.monospacedSystemFont(ofSize: 18, weight: .medium),
            .foregroundColor: UIColor.yellow
        ]

        // Tính toán kích thước text
        let dateSize = (date as NSString).size(withAttributes: dateAttributes)
        let locationSize = (location as NSString).size(withAttributes: locationAttributes)

        let textWidth = max(dateSize.width, locationSize.width)
        let totalHeight = lineHeight + lineHeight2 + spacing

        // Vị trí bắt đầu (góc dưới bên phải)
        let startX = imageSize.width - textWidth - margin
        let startY = imageSize.height - totalHeight - margin

        // Draw background
        let bgRect = CGRect(
            x: startX - 12,
            y: startY - 8,
            width: textWidth + 24,
            height: totalHeight + 16
        )
        ctx.setFillColor(UIColor.black.withAlphaComponent(0.7).cgColor)
        ctx.fillEllipse(in: bgRect)

        // Draw border
        ctx.setStrokeColor(UIColor.white.withAlphaComponent(0.3).cgColor)
        ctx.setLineWidth(1)
        ctx.strokeEllipse(in: bgRect.insetBy(dx: -2, dy: -2))

        // Draw date
        let dateRect = CGRect(x: startX, y: startY, width: dateSize.width, height: lineHeight)
        (date as NSString).draw(in: dateRect, withAttributes: dateAttributes)

        // Draw location
        let locationRect = CGRect(
            x: startX,
            y: startY + lineHeight + spacing,
            width: locationSize.width,
            height: lineHeight2
        )
        (location as NSString).draw(in: locationRect, withAttributes: locationAttributes)

        ctx.restoreGState()
    }
}

// MARK: - WatermarkEngine Extension
extension WatermarkEngine {
    /// Tọa độ GPS ngẫu nhiên (dùng khi fake location)
    static func randomCoordinates() -> (latitude: Double, longitude: Double) {
        // Tọa độ ngẫu nhiên ở một số địa điểm nổi tiếng
        let locations: [(name: String, lat: Double, lon: Double)] = [
            ("Paris, France", 48.8566, 2.3522),
            ("Tokyo, Japan", 35.6762, 139.6503),
            ("New York, USA", 40.7128, -74.0060),
            ("London, UK", 51.5074, -0.1278),
            ("Sydney, Australia", -33.8688, 151.2093),
            ("Dubai, UAE", 25.2048, 55.2708),
            ("Singapore", 1.3521, 103.8198),
            ("Seoul, Korea", 37.5665, 126.9780),
            ("Bangkok, Thailand", 13.7563, 100.5018),
            ("Istanbul, Turkey", 41.0082, 28.9784)
        ]

        let randomIndex = Int.random(in: 0..<locations.count)
        let location = locations[randomIndex]

        return (location.lat, location.lon)
    }
}

// MARK: - UIImage Extension
extension UIImage {
    /// Vẽ image vào UIGraphicsImageRenderer context
    func draw(in ctx: CGContext) {
        ctx.saveGState()
        ctx.translateBy(x: 0, y: size.height)
        ctx.scaleBy(x: 1, y: -1)
        ctx.draw(self.cgImage!, in: CGRect(origin: .zero, size: size))
        ctx.restoreGState()
    }
}

// MARK: - UIGraphicsImageRenderer Extension
extension UIGraphicsImageRenderer {
    /// Tạo image với closure
    func image(_ draw: (CGContext) -> Void) -> UIImage {
        let image = image(actions: { ctx in
            draw(ctx.cgContext)
        })
        return image
    }
}
