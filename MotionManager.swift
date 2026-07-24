//
//  MotionManager.swift
//  ProCameraApp
//
//  Xử lý cân bằng điện tử (Electronic Level) bằng CoreMotion
//  Sử dụng Gyroscope để đọc dữ liệu góc nghiêng
//

import CoreMotion
import Combine
import SwiftUI

// MARK: - MotionManager
/// ViewModel quản lý dữ liệu từ Accelerometer/Gyroscope
/// Hiển thị vạch chỉ thị cân bằng trên màn hình
@MainActor
class MotionManager: ObservableObject {
    // MARK: - Published Properties

    /// Góc nghiêng Roll (trục X) - âm: nghiêng trái, dương: nghiêng phải
    @Published var roll: Double = 0.0

    /// Góc nghiêng Pitch (trục Y) - âm: nghiêng trước, dương: nghiêng sau
    @Published var pitch: Double = 0.0

    /// Trạng thái cân bằng (true khi điện thoại gần song song mặt đất)
    @Published var isLevel: Bool = false

    /// Mức độ lệch so với phương ngang (0.0 = hoàn toàn水平, 1.0 = lệch tối đa)
    @Published var levelDeviation: Double = 0.0

    /// Trạng thái hoạt động
    @Published var isActive: Bool = false

    // MARK: - Private Properties

    /// CMMotionManager instance
    private let motionManager = CMMotionManager()

    /// DispatchQueue cho motion updates
    private let motionQueue = OperationQueue()

    /// Threshold để xác định "cân bằng" (degrees)
    /// iPhone có thể rung nhẹ, nên cần tolerance
    private let levelThreshold: Double = 1.5

    /// Smooth factor cho motion data (0.0 - 1.0)
    /// Cao hơn = responsive hơn, thấp hơn = mượt hơn
    private let smoothFactor: Double = 0.15

    /// Previous values for smoothing
    private var previousRoll: Double = 0.0
    private var previousPitch: Double = 0.0

    // MARK: - Initialization

    init() {
        motionQueue.name = "com.procamera.motionqueue"
        motionQueue.qualityOfService = .userInteractive
    }

    deinit {
        motionManager.stopDeviceMotionUpdates()
    }

    // MARK: - Control

    /// Bắt đầu cập nhật dữ liệu motion
    func startUpdates() {
        guard motionManager.isDeviceMotionAvailable else {
            print("⚠️ Device Motion not available")
            return
        }

        // Sử dụng DeviceMotion thay vì Accelerometer riêng
        // DeviceMotion đã được fused từ accelerometer + gyroscope
        motionManager.deviceMotionUpdateInterval = 1.0 / 60.0 // 60 Hz

        motionManager.startDeviceMotionUpdates(
            using: .xArbitraryZVertical,
            to: motionQueue
        ) { [weak self] motion, error in
            guard let self = self, let motion = motion else {
                if let error = error {
                    print("Motion error: \(error)")
                }
                return
            }

            Task { @MainActor in
                self.processMotionData(motion)
            }
        }

        isActive = true
    }

    /// Dừng cập nhật motion
    func stopUpdates() {
        motionManager.stopDeviceMotionUpdates()
        isActive = false
        resetValues()
    }

    // MARK: - Processing

    /// Xử lý dữ liệu từ DeviceMotion
    private func processMotionData(_ motion: CMDeviceMotion) {
        // Lấy dữ liệu attitude (góc nghiêng)
        let attitude = motion.attitude

        // Convert radians to degrees
        // Roll: xoay quanh trục Z (nghiêng trái/phải)
        // Pitch: xoay quanh trục X (nghiêng trước/sau)
        let rawRoll = attitude.roll * 180.0 / .pi
        let rawPitch = attitude.pitch * 180.0 / .pi

        // Apply smoothing để giảm noise
        roll = smoothValue(rawRoll, previous: previousRoll)
        pitch = smoothValue(rawPitch, previous: previousPitch)

        previousRoll = roll
        previousPitch = pitch

        // Tính mức độ lệch
        // Kết hợp cả roll và pitch
        let rollDeviation = abs(roll)
        let pitchDeviation = abs(pitch)
        levelDeviation = max(rollDeviation, pitchDeviation)

        // Xác định trạng thái cân bằng
        // Chỉ check roll (nghiêng trái/phải) là chính
        isLevel = abs(roll) < levelThreshold && abs(pitch) < levelThreshold
    }

    /// Smooth value using exponential moving average
    private func smoothValue(_ current: Double, previous: Double) -> Double {
        return previous + smoothFactor * (current - previous)
    }

    /// Reset tất cả giá trị
    private func resetValues() {
        roll = 0.0
        pitch = 0.0
        isLevel = false
        levelDeviation = 0.0
        previousRoll = 0.0
        previousPitch = 0.0
    }

    // MARK: - Helpers

    /// Chuyển đổi angle thành rotation cho vạch chỉ thị
    /// Trả về góc xoay (degrees) cho SwiftUI
    var indicatorRotation: Double {
        return roll
    }

    /// Màu sắc dựa trên mức độ cân bằng
    var levelColor: Color {
        if isLevel {
            return .green
        } else if levelDeviation < 3.0 {
            return .yellow
        } else {
            return .red
        }
    }

    /// Text hiển thị mức độ lệch
    var deviationText: String {
        let deviation = abs(roll)
        if deviation < 0.5 {
            return "LEVEL"
        } else {
            return String(format: "%+.1f°", roll)
        }
    }
}

// MARK: - MotionManager + FocusDistance
extension MotionManager {
    /// Tính distance từ camera đến vật thể (gần đúng)
    /// Dựa trên góc pitch và assumed height
    /// Chỉ dùng khi camera giữ ở độ cao cố định
    func estimatedFocusDistance(heightFromGround: Double = 1.5) -> Double {
        // heightFromGround: độ cao từ mắt đến vật thể (meters)
        let pitchRadians = pitch * .pi / 180.0
        return heightFromGround * tan(abs(pitchRadians))
    }
}
