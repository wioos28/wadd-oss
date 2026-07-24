//
//  CameraManager.swift
//  ProCameraApp
//
//  ViewModel quản lý AVCaptureSession, điều khiển thủ công camera
//  Hỗ trợ: ISO, Shutter Speed, Format (ProRAW/JPEG/PNG), Manual Controls
//

import AVFoundation
import Combine
import CoreImage
import Photos
import SwiftUI

// MARK: - CameraManager
/// ViewModel chính quản lý toàn bộ hoạt động camera
/// Tuân thủ ObservableObject để tương tác với SwiftUI
@MainActor
class CameraManager: NSObject, ObservableObject {
    // MARK: - Published Properties (UI Binding)

    /// Trạng thái hiện tại của camera
    @Published var state: CameraState = .idle

    /// Cài đặt camera hiện tại
    @Published var settings = CameraSettings()

    /// Vị trí camera hiện tại
    @Published var currentPosition: CameraPosition = .back

    /// Chế độ lấy nét
    @Published var focusMode: FocusModeOption = .auto

    /// Chế độ phơi sáng
    @Published var exposureMode: ExposureModeOption = .auto

    /// Torch mode
    @Published var torchMode: TorchMode = .off

    /// torch level (0.0 - 1.0)
    @Published var torchLevel: Float = 1.0

    /// Có thể capture không
    @Published var canCapture: Bool = true

    /// Flash mode cho capture
    @Published var flashMode: AVCaptureDevice.FlashMode = .off

    /// Zoom level
    @Published var zoomLevel: CGFloat = 1.0

    /// Frame cuối cùng từ live preview (dùng cho color grading)
    @Published var currentFrame: CVPixelBuffer?

    /// Lỗi hiện tại
    @Published var errorMessage: String?

    /// Whether photo was saved successfully
    @Published var photoSaved: Bool = false

    // MARK: - Private Properties

    /// AVCaptureSession chính
    var captureSession: AVCaptureSession?

    /// Current capture device (camera lens)
    private var currentDevice: AVCaptureDevice?

    /// Photo output cho việc capture
    private var photoOutput: AVCapturePhotoOutput?

    /// Movie output (nếu cần quay video)
    private var movieFileOutput: AVCaptureMovieFileOutput?

    /// Video data output để lấy pixel buffer cho live preview
    private var videoDataOutput: AVCaptureVideoDataOutput?

    /// Dispatch queue cho video processing
    private let sessionQueue = DispatchQueue(label: "com.procamera.sessionqueue")

    /// Dispatch queue cho video data output
    private let videoOutputQueue = DispatchQueue(label: "com.procamera.videooutput")

    /// Combine cancellables
    private var cancellables = Set<AnyCancellable>()

    /// Reference to color filter manager
    var colorFilterManager: ColorFilterManager?

    /// Reference to histogram manager
    var histogramManager: HistogramManager?

    /// Reference to focus peaking manager
    var focusPeakingManager: FocusPeakingManager?

    /// Reference to film simulation manager
    var filmSimulationManager: FilmSimulationManager?

    /// Reference to watermark engine
    var watermarkEngine: WatermarkEngine?

    // MARK: - Initialization

    override init() {
        super.init()
        setupBindings()
    }

    deinit {
        // Nonisolated access to captureSession for cleanup in deinit
        let session = captureSession
        Task.detached {
            session?.stopRunning()
        }
    }

    // MARK: - Setup

    /// Setup Combine bindings
    private func setupBindings() {
        // When settings change, update device
        $settings
            .debounce(for: .milliseconds(50), scheduler: RunLoop.main)
            .sink { [weak self] _ in
                self?.applySettingsToDevice()
            }
            .store(in: &cancellables)
    }

    // MARK: - Session Management

    /// Khởi tạo và cấu hình AVCaptureSession
    func setupSession() async {
        state = .configuring

        let session = AVCaptureSession()

        // Cấu hình session quality
        // .high = 1920x1080 hoặc cao hơn tùy device
        if session.canSetSessionPreset(.high) {
            session.sessionPreset = .high
        } else if session.canSetSessionPreset(.hd1920x1080) {
            session.sessionPreset = .hd1920x1080
        }

        self.captureSession = session

        // Setup camera input
        do {
            try await setupCameraInput(for: currentPosition)
        } catch {
            state = .error("Không thể khởi tạo camera: \(error.localizedDescription)")
            return
        }

        // Setup photo output
        setupPhotoOutput()

        // Setup video data output (cho live preview & color grading)
        setupVideoDataOutput()

        state = .running
    }

    /// Bắt đầu chạy session
    func startSession() {
        sessionQueue.async { [weak self] in
            self?.captureSession?.startRunning()
        }
    }

    /// Dừng session
    func stopSession() {
        sessionQueue.async { [weak self] in
            self?.captureSession?.stopRunning()
        }
    }

    // MARK: - Camera Input Setup

    /// Setup camera input cho vị trí camera cụ thể
    private func setupCameraInput(for position: CameraPosition) async throws {
        guard let session = captureSession else {
            throw CameraError.sessionNotConfigured
        }

        // Xóa input cũ nếu có
        for input in session.inputs {
            session.removeInput(input)
        }

        // Tìm device phù hợp
        let device: AVCaptureDevice?
        let discoverySession = AVCaptureDevice.DiscoverySession(
            deviceTypes: [.builtInWideAngleCamera],
            mediaType: .video,
            position: position.avPosition
        )

        // Lấy device từ discovery session
        device = discoverySession.devices.first

        guard let selectedDevice = device else {
            throw CameraError.deviceNotFound
        }

        // Tạo device input
        let deviceInput = try AVCaptureDeviceInput(device: selectedDevice)

        if session.canAddInput(deviceInput) {
            session.addInput(deviceInput)
            self.currentDevice = selectedDevice

            // Lock device để cấu hình
            try selectedDevice.lockForConfiguration()

            // Cấu hình ban đầu
            configureDeviceDefaults(selectedDevice)

            selectedDevice.unlockForConfiguration()
        } else {
            throw CameraError.inputFailed
        }
    }

    /// Cấu hình mặc định cho device
    private func configureDeviceDefaults(_ device: AVCaptureDevice) {
        // Auto focus
        if device.isFocusModeSupported(.continuousAutoFocus) {
            device.focusMode = .continuousAutoFocus
        }

        // Auto exposure
        if device.isExposureModeSupported(.continuousAutoExposure) {
            device.exposureMode = .continuousAutoExposure
        }

        // Auto white balance
        if device.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
            device.whiteBalanceMode = .continuousAutoWhiteBalance
        }

        // Enable low light boost if available
        if device.isLowLightBoostSupported {
            device.automaticallyEnablesLowLightBoostWhenAvailable = true
        }
    }

    // MARK: - Photo Output Setup

    /// Setup AVCapturePhotoOutput cho việc capture
    private func setupPhotoOutput() {
        let photoOutput = AVCapturePhotoOutput()

        if let session = captureSession, session.canAddOutput(photoOutput) {
            session.addOutput(photoOutput)
            self.photoOutput = photoOutput

            // iOS 16+ use maxPhotoDimensions instead of deprecated isHighResolutionCaptureEnabled
            if #available(iOS 16.0, *) {
                photoOutput.maxPhotoDimensions = CMVideoDimensions(width: 4032, height: 3024)
            } else {
                photoOutput.isHighResolutionCaptureEnabled = true
            }

            // Configure supported photo codecs
            configurePhotoCodecs(photoOutput: photoOutput)
        }
    }

    /// Cấu hình các codec ảnh được hỗ trợ
    private func configurePhotoCodecs(photoOutput: AVCapturePhotoOutput) {
        // Kiểm tra ProRAW support (iPhone 12 Pro trở lên)
        if photoOutput.availablePhotoCodecTypes.contains(.hevc) {
            print("HEVC codec supported")
        }

        if photoOutput.availablePhotoCodecTypes.contains(.jpeg) {
            print("JPEG codec supported")
        }

        // ProRAW/DNG support
        if photoOutput.availableRawPhotoPixelFormatTypes.count > 0 {
            print("DNG (RAW) codec supported")
        }
    }

    // MARK: - Video Data Output (Live Preview)

    /// Setup video data output để lấy pixel buffer cho live preview
    private func setupVideoDataOutput() {
        let videoOutput = AVCaptureVideoDataOutput()

        // Yêu cầu pixel buffer format: 32BGRA (cho Core Image processing)
        videoOutput.videoSettings = [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA
        ]

        // Discard late frames
        videoOutput.alwaysDiscardsLateVideoFrames = true

        // Set delegate
        videoOutput.setSampleBufferDelegate(self, queue: videoOutputQueue)

        if let session = captureSession, session.canAddOutput(videoOutput) {
            session.addOutput(videoOutput)
            self.videoDataOutput = videoOutput

            // Set connection video orientation
            if let connection = videoOutput.connection(with: .video) {
                if #available(iOS 17.0, *) {
                    if connection.isVideoRotationAngleSupported(90) {
                        connection.videoRotationAngle = 90 // Portrait
                    }
                } else {
                    if connection.isVideoOrientationSupported {
                        connection.videoOrientation = .portrait
                    }
                }
                if connection.isVideoMirroringSupported {
                    connection.isVideoMirrored = false
                }
            }
        }
    }

    // MARK: - Camera Controls (Manual Adjustments)

    /// Điều khiển ISO thủ công
    /// - Parameter iso: Giá trị ISO (thường 25-2500 tùy iPhone model)
    func setISO(_ iso: Float) {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            // Clamp ISO trong khoảng hỗ trợ
            let clampedISO = max(device.activeFormat.minISO,
                                 min(iso, device.activeFormat.maxISO))

            // Set ISO
            device.setExposureModeCustom(
                duration: device.exposureDuration,
                iso: clampedISO,
                completionHandler: nil
            )

            settings.iso = clampedISO
            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi thiết lập ISO: \(error.localizedDescription)"
        }
    }

    /// Điều khiển Shutter Speed (Exposure Duration) thủ công
    /// - Parameter duration: Thời gian phơi sáng (đơn vị: giây)
    ///   Ví dụ: 1/1000s = 0.001, 1/60s ≈ 0.0167, 1s = 1.0
    func setShutterSpeed(_ duration: Double) {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            // Clamp duration trong khoảng hỗ trợ
            let minDuration = device.activeFormat.minExposureDuration.seconds
            let maxDuration = device.activeFormat.maxExposureDuration.seconds
            let clampedDuration = max(minDuration, min(duration, maxDuration))

            // Set shutter speed
            device.setExposureModeCustom(
                duration: CMTime(seconds: clampedDuration, preferredTimescale: 1000000),
                iso: device.iso,
                completionHandler: nil
            )

            settings.shutterSpeed = clampedDuration
            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi thiết lập Shutter Speed: \(error.localizedDescription)"
        }
    }

    /// Điều chỉnh Exposure Compensation (EV)
    /// - Parameter ev: Giá trị EV (-3.0 đến +3.0)
    func setExposureCompensation(_ ev: Float) {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            let clampedEV = max(device.minExposureTargetBias,
                                min(ev, device.maxExposureTargetBias))

            device.setExposureTargetBias(clampedEV, completionHandler: nil)

            settings.exposureCompensation = clampedEV
            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi thiết lập EV: \(error.localizedDescription)"
        }
    }

    /// Điều chỉnh White Balance (Nhiệt độ màu)
    /// - Parameter temperature: Nhiệt độ màu (Kelvin, 2000-10000K)
    func setWhiteBalanceTemperature(_ temperature: Float) {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            if device.isWhiteBalanceModeSupported(.locked) {
                device.whiteBalanceMode = .locked

                // Convert temperature to device RGB gain
                let temperatureAndTint = AVCaptureDevice.WhiteBalanceTemperatureAndTintValues(
                    temperature: temperature,
                    tint: 0
                )
                let gain = device.deviceWhiteBalanceGains(for: temperatureAndTint)

                // Clamp gains
                let maxGain = device.maxWhiteBalanceGain
                let rGain = min(max(gain.redGain, 1.0), maxGain)
                let gGain = min(max(gain.greenGain, 1.0), maxGain)
                let bGain = min(max(gain.blueGain, 1.0), maxGain)

                device.setWhiteBalanceModeLocked(
                    with: AVCaptureDevice.WhiteBalanceGains(
                        redGain: rGain,
                        greenGain: gGain,
                        blueGain: bGain
                    ),
                    completionHandler: nil
                )
            }

            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi thiết lập White Balance: \(error.localizedDescription)"
        }
    }

    /// Set White Balance theo preset
    func setWhiteBalancePreset(_ preset: WhiteBalancePreset) {
        settings.whiteBalancePreset = preset

        if preset != .custom {
            setWhiteBalanceTemperature(preset.temperature)
        }
    }

    /// Set Tint value
    func setTint(_ tint: Float) {
        settings.tint = tint
        if settings.whiteBalancePreset == .custom {
            setWhiteBalanceTemperature(settings.customTemperature)
        }
    }

    /// Điều chỉnh Torch (đèn flash liên tục)
    /// - Parameters:
    ///   - mode: Chế độ torch (on/off/auto)
    ///   - level: Cường độ (0.0 - 1.0)
    func setTorch(mode: TorchMode, level: Float = 1.0) {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            let avMode: AVCaptureDevice.TorchMode
            switch mode {
            case .off: avMode = .off
            case .on: avMode = .on
            case .auto: avMode = .auto
            }

            if device.hasTorch && device.isTorchModeSupported(avMode) {
                device.torchMode = avMode

                // Set torch level if torch is on
                if avMode == .on {
                    let clampedLevel = max(0.0, min(level, 1.0))
                    try device.setTorchModeOn(level: clampedLevel)
                    self.torchLevel = clampedLevel
                }
            }

            torchMode = mode
            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi thiết lập Torch: \(error.localizedDescription)"
        }
    }

    /// Điều chỉnh zoom level
    /// - Parameter zoom: Zoom factor (1.0 = normal, 2.0 = 2x, ...)
    func setZoom(_ zoom: CGFloat) {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            // Clamp zoom trong khoảng hỗ trợ
            let minZoom = device.minAvailableVideoZoomFactor
            let maxZoom = min(device.activeFormat.videoMaxZoomFactor, 10.0)
            let clampedZoom = max(minZoom, min(zoom, maxZoom))

            device.videoZoomFactor = clampedZoom
            zoomLevel = clampedZoom

            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi thiết lập Zoom: \(error.localizedDescription)"
        }
    }

    /// Set tap to focus tại point
    /// - Parameter point: Point trên preview view (0-1 normalized)
    func setFocusPoint(_ point: CGPoint) {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            if device.isFocusPointOfInterestSupported {
                device.focusPointOfInterest = point
            }

            if device.isFocusModeSupported(.autoFocus) {
                device.focusMode = .autoFocus
            }

            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi thiết lập Focus: \(error.localizedDescription)"
        }
    }

    /// Chuyển đổi giữa các camera (front/back)
    func switchCamera() {
        let newPosition: CameraPosition = currentPosition == .back ? .front : .back
        switchCamera(to: newPosition)
    }

    /// Switch to specific camera position
    func switchCamera(to position: CameraPosition) {
        Task {
            do {
                try await setupCameraInput(for: position)
                currentPosition = position
            } catch {
                state = .error("Không thể chuyển camera: \(error.localizedDescription)")
            }
        }
    }

    // MARK: - Apply Settings to Device

    /// Áp dụng tất cả settings xuống device
    private func applySettingsToDevice() {
        guard let device = currentDevice else { return }

        do {
            try device.lockForConfiguration()

            // Apply ISO
            if device.isExposureModeSupported(.custom) {
                let clampedISO = max(device.activeFormat.minISO,
                                     min(settings.iso, device.activeFormat.maxISO))

                device.setExposureModeCustom(
                    duration: device.exposureDuration,
                    iso: clampedISO,
                    completionHandler: nil
                )
            }

            // Apply white balance
            if device.isWhiteBalanceModeSupported(.locked) {
                device.whiteBalanceMode = .locked

                let temperatureAndTint = AVCaptureDevice.WhiteBalanceTemperatureAndTintValues(
                    temperature: settings.whiteBalancePreset == .custom
                        ? settings.customTemperature
                        : settings.whiteBalancePreset.temperature,
                    tint: settings.tint
                )
                let gain = device.deviceWhiteBalanceGains(for: temperatureAndTint)

                let maxGain = device.maxWhiteBalanceGain
                let rGain = min(max(gain.redGain, 1.0), maxGain)
                let gGain = min(max(gain.greenGain, 1.0), maxGain)
                let bGain = min(max(gain.blueGain, 1.0), maxGain)

                device.setWhiteBalanceModeLocked(
                    with: AVCaptureDevice.WhiteBalanceGains(
                        redGain: rGain,
                        greenGain: gGain,
                        blueGain: bGain
                    ),
                    completionHandler: nil
                )
            }

            device.unlockForConfiguration()

        } catch {
            errorMessage = "Lỗi áp dụng cài đặt: \(error.localizedDescription)"
        }
    }

    // MARK: - Photo Capture

    /// Chụp ảnh với các settings hiện tại
    func capturePhoto() {
        guard let photoOutput = photoOutput, canCapture else {
            print("Cannot capture photo")
            return
        }

        state = .capturing
        canCapture = false

        let photoSettings = createPhotoSettings()

        photoOutput.capturePhoto(with: photoSettings, delegate: self)
    }

    /// Tạo PhotoSettings dựa trên định dạng đã chọn
    private func createPhotoSettings() -> AVCapturePhotoSettings {
        var photoSettings: AVCapturePhotoSettings

        switch settings.captureFormat {
        case .ProRAW:
            // ProRAW capture (iPhone 12 Pro+)
            if let rawFormat = photoOutput?.availableRawPhotoPixelFormatTypes.first {
                photoSettings = AVCapturePhotoSettings(
                    rawPixelFormatType: rawFormat,
                    processedFormat: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
                )
            } else {
                // Fallback to JPEG if ProRAW not available
                photoSettings = AVCapturePhotoSettings(
                    format: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
                )
            }

        case .RAW:
            // RAW DNG capture
            if let rawFormat = photoOutput?.availableRawPhotoPixelFormatTypes.first {
                photoSettings = AVCapturePhotoSettings(
                    rawPixelFormatType: rawFormat,
                    processedFormat: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
                )
            } else {
                photoSettings = AVCapturePhotoSettings(
                    format: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
                )
            }

        case .JPEG:
            // JPEG capture
            photoSettings = AVCapturePhotoSettings(
                format: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
            )

        case .PNG:
            // PNG capture (lossless)
            photoSettings = AVCapturePhotoSettings(
                format: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
            )
        }

        // Flash mode
        photoSettings.flashMode = flashMode

        // iOS 16+ use maxPhotoDimensions instead of deprecated isHighResolutionPhotoEnabled
        if #available(iOS 16.0, *) {
            photoSettings.maxPhotoDimensions = CMVideoDimensions(width: 4032, height: 3024)
        } else {
            photoSettings.isHighResolutionPhotoEnabled = true
        }

        return photoSettings
    }
}

// MARK: - AVCapturePhotoCaptureDelegate
/// Delegate xử lý kết quả capture
extension CameraManager: AVCapturePhotoCaptureDelegate {
    nonisolated func photoOutput(_ output: AVCapturePhotoOutput,
                                  didFinishProcessingPhoto photo: AVCapturePhoto,
                                  error: Error?) {
        Task { @MainActor in
            if let error = error {
                state = .error("Capture error: \(error.localizedDescription)")
                canCapture = true
                return
            }

            // Lấy photo data
            guard var photoData = photo.fileDataRepresentation() else {
                state = .error("Không thể lấy photo data")
                canCapture = true
                return
            }

            // Lấy metadata
            let metadata = photo.metadata

            // Capture values for background processing
            let isPrivacyEnabled = watermarkEngine?.isPrivacyModeEnabled ?? false
            let fakeLocation = watermarkEngine?.fakeLocation ?? "Somewhere on Earth"
            let currentFormat = settings.captureFormat

            // Xử lý Privacy Mode: xóa GPS và thêm watermark
            if isPrivacyEnabled {
                photoData = await processPrivacyData(
                    photoData,
                    fakeLocation: fakeLocation
                )
            }

            // Lưu ảnh
            savePhoto(photoData: photoData, metadata: metadata, format: currentFormat)
        }
    }

    /// Xử lý privacy: xóa GPS và thêm watermark
    private func processPrivacyData(_ photoData: Data, fakeLocation: String) async -> Data {
        return await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                // Xóa GPS metadata
                var processedData = stripGPSMetadataSync(from: photoData)

                // Áp dụng watermark nếu được bật
                if let uiImage = UIImage(data: processedData) {
                    let watermarkedImage = self.applyWatermarkSync(
                        to: uiImage,
                        date: Date(),
                        location: fakeLocation
                    )
                    if let watermarkedData = watermarkedImage.jpegData(compressionQuality: 0.95) {
                        processedData = watermarkedData
                    }
                }

                DispatchQueue.main.async {
                    continuation.resume(returning: processedData)
                }
            }
        }
    }

    /// Sync wrapper for stripping GPS metadata
    private func stripGPSMetadataSync(from data: Data) -> Data {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
            return data
        }

        guard let metadata = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any] else {
            return data
        }

        var mutableMetadata = metadata
        mutableMetadata.removeValue(forKey: kCGImagePropertyGPSDictionary as String)

        let destinationData = NSMutableData()
        let typeIdentifier = CGImageSourceGetType(source) ?? (UTType.jpeg.identifier as CFString)

        guard let destination = CGImageDestinationCreateWithData(
            destinationData,
            typeIdentifier,
            1,
            nil
        ) else {
            return data
        }

        if let image = CGImageSourceCreateImageAtIndex(source, 0, nil) {
            CGImageDestinationAddImage(destination, image, mutableMetadata as CFDictionary)
        }

        return destinationData as Data
    }

    /// Sync wrapper for applying watermark
    private func applyWatermarkSync(to image: UIImage, date: Date, location: String) -> UIImage {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        dateFormatter.locale = Locale(identifier: "en_US_POSIX")

        let displayDate = dateFormatter.string(from: date)

        let renderer = UIGraphicsImageRenderer(size: image.size)
        return renderer.image { context in
            image.draw(at: .zero)

            let ctx = context.cgContext
            ctx.saveGState()

            let margin: CGFloat = 20
            let lineHeight: CGFloat = 28
            let lineHeight2: CGFloat = 24
            let spacing: CGFloat = 8

            let dateAttributes: [NSAttributedString.Key: Any] = [
                .font: UIFont.monospacedSystemFont(ofSize: 22, weight: .bold),
                .foregroundColor: UIColor.cyan
            ]

            let locationAttributes: [NSAttributedString.Key: Any] = [
                .font: UIFont.monospacedSystemFont(ofSize: 18, weight: .medium),
                .foregroundColor: UIColor.yellow
            ]

            let dateSize = (displayDate as NSString).size(withAttributes: dateAttributes)
            let locationSize = (location as NSString).size(withAttributes: locationAttributes)

            let textWidth = max(dateSize.width, locationSize.width)
            let totalHeight = lineHeight + lineHeight2 + spacing

            let startX = image.size.width - textWidth - margin
            let startY = image.size.height - totalHeight - margin

            let bgRect = CGRect(
                x: startX - 12,
                y: startY - 8,
                width: textWidth + 24,
                height: totalHeight + 16
            )
            ctx.setFillColor(UIColor.black.withAlphaComponent(0.7).cgColor)
            ctx.fillEllipse(in: bgRect)

            ctx.setStrokeColor(UIColor.white.withAlphaComponent(0.3).cgColor)
            ctx.setLineWidth(1)
            ctx.strokeEllipse(in: bgRect.insetBy(dx: -2, dy: -2))

            let dateRect = CGRect(x: startX, y: startY, width: dateSize.width, height: lineHeight)
            (displayDate as NSString).draw(in: dateRect, withAttributes: dateAttributes)

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

    /// Lưu ảnh vào Photo Library
    private func savePhoto(photoData: Data, metadata: [String: Any], format: CaptureFormat) {
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { [weak self] status in
            guard status == .authorized || status == .limited else {
                DispatchQueue.main.async {
                    self?.state = .error("Không có quyền truy cập Photo Library")
                    self?.canCapture = true
                }
                return
            }

            PHPhotoLibrary.shared().performChanges({
                // Tạo asset request
                let request = PHAssetCreationRequest.forAsset()

                // Tạo resource options với uniform type identifier
                let resourceOptions = PHAssetResourceCreationOptions()
                resourceOptions.uniformTypeIdentifier = self?.getUTType(for: format)

                // Thêm photo data với options
                request.addResource(with: .photo, data: photoData, options: resourceOptions)

            }) { [weak self] success, error in
                DispatchQueue.main.async {
                    if success {
                        self?.state = .running
                        self?.photoSaved = true

                        // Reset photoSaved after 2 seconds
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                            self?.photoSaved = false
                        }
                    } else {
                        self?.state = .error("Lưu ảnh thất bại: \(error?.localizedDescription ?? "Unknown")")
                    }
                    self?.canCapture = true
                }
            }
        }
    }

    /// Get UTType string based on capture format
    private func getUTType(for format: CaptureFormat) -> String {
        switch format {
        case .ProRAW, .RAW:
            return "public.dng"
        case .JPEG:
            return "public.jpeg"
        case .PNG:
            return "public.png"
        }
    }
}

// MARK: - AVCaptureVideoDataOutputSampleBufferDelegate
/// Delegate xử lý video frames cho live preview
extension CameraManager: AVCaptureVideoDataOutputSampleBufferDelegate {
    nonisolated func captureOutput(_ output: AVCaptureOutput,
                                    didOutput sampleBuffer: CMSampleBuffer,
                                    from connection: AVCaptureConnection) {

        // Extract pixel buffer
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {
            return
        }

        // Process all camera data in a single MainActor Task to avoid interleaving
        Task { @MainActor in
            // Update current frame
            self.currentFrame = pixelBuffer

            // Process histogram data
            if let histogramManager = self.histogramManager, histogramManager.isAnalyzing {
                histogramManager.processPixelBuffer(pixelBuffer)
            }

            // Process focus peaking
            if let focusPeakingManager = self.focusPeakingManager, focusPeakingManager.isEnabled {
                await focusPeakingManager.processPixelBuffer(pixelBuffer)
            }

            // Apply film simulation
            if let filmSimulationManager = self.filmSimulationManager,
               filmSimulationManager.currentFilm != .original {
                filmSimulationManager.processFrame(pixelBuffer)
            }

            // Apply color filters
            if let colorFilterManager = self.colorFilterManager {
                colorFilterManager.processFrame(pixelBuffer)
            }
        }
    }
}

// MARK: - Camera Errors
/// Các lỗi có thể xảy ra
enum CameraError: Error, LocalizedError {
    case sessionNotConfigured
    case deviceNotFound
    case inputFailed
    case outputFailed
    case permissionDenied
    case captureFailed
    case saveFailed

    var errorDescription: String? {
        switch self {
        case .sessionNotConfigured:
            return "Camera session chưa được cấu hình"
        case .deviceNotFound:
            return "Không tìm thấy camera device"
        case .inputFailed:
            return "Không thể thêm camera input"
        case .outputFailed:
            return "Không thể thêm camera output"
        case .permissionDenied:
            return "Quyền truy cập camera bị từ chối"
        case .captureFailed:
            return "Chụp ảnh thất bại"
        case .saveFailed:
            return "Lưu ảnh thất bại"
        }
    }
}
