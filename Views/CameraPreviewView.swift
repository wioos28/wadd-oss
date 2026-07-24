//
//  CameraPreviewView.swift
//  ProCameraApp
//
//  UIViewRepresentable để hiển thị live camera preview
//

import AVFoundation
import SwiftUI

// MARK: - CameraPreviewView
/// SwiftUI wrapper cho AVCaptureVideoPreviewLayer
struct CameraPreviewView: UIViewRepresentable {
    @ObservedObject var cameraManager: CameraManager

    func makeUIView(context: Context) -> CameraPreviewUIView {
        let view = CameraPreviewUIView()
        view.cameraManager = cameraManager

        // Connect preview layer to session when available
        if let session = cameraManager.captureSession {
            view.setupPreviewLayer(session: session)
        }

        return view
    }

    func updateUIView(_ uiView: CameraPreviewUIView, context: Context) {
        // Connect preview layer if not yet connected
        if uiView.previewLayer == nil,
           let session = cameraManager.captureSession {
            uiView.setupPreviewLayer(session: session)
        }
    }
}

// MARK: - CameraPreviewUIView
/// UIView chứa AVCaptureVideoPreviewLayer
class CameraPreviewUIView: UIView {
    var cameraManager: CameraManager?

    var previewLayer: AVCaptureVideoPreviewLayer?

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupView()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupView()
    }

    private func setupView() {
        backgroundColor = .black
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        previewLayer?.frame = bounds
    }

    /// Setup preview layer với session
    func setupPreviewLayer(session: AVCaptureSession) {
        previewLayer?.removeFromSuperlayer()

        let previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill
        if let connection = previewLayer.connection {
            if #available(iOS 17.0, *) {
                if connection.isVideoRotationAngleSupported(90) {
                    connection.videoRotationAngle = 90 // Portrait
                }
            } else {
                if connection.isVideoOrientationSupported {
                    connection.videoOrientation = .portrait
                }
            }
        }
        previewLayer.frame = bounds

        layer.addSublayer(previewLayer)
        self.previewLayer = previewLayer
    }

    /// Update video rotation angle
    func updateVideoRotationAngle(_ angle: CGFloat) {
        if let connection = previewLayer?.connection {
            if #available(iOS 17.0, *) {
                if connection.isVideoRotationAngleSupported(angle) {
                    connection.videoRotationAngle = angle
                }
            } else {
                if connection.isVideoOrientationSupported {
                    connection.videoOrientation = .portrait
                }
            }
        }
    }
}

// MARK: - CameraViewModel
/// ViewModel để manage camera preview
@MainActor
class CameraPreviewViewModel: ObservableObject {
    @Published var isReady = false
    @Published var error: String?

    let cameraManager: CameraManager

    init(cameraManager: CameraManager) {
        self.cameraManager = cameraManager
    }

    func setup() {
        Task {
            await cameraManager.setupSession()
            cameraManager.startSession()
            isReady = true
        }
    }
}

// MARK: - Preview Provider
struct CameraPreviewView_Previews: PreviewProvider {
    static var previews: some View {
        CameraPreviewView(cameraManager: CameraManager())
    }
}
