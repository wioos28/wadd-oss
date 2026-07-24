//
//  ContentView.swift
//  ProCameraApp
//
//  Giao diện chính SwiftUI cho Pro Camera App
//  Designed for iOS 16+
//

import SwiftUI
import AVFoundation

// MARK: - ContentView
/// View chính của ứng dụng
struct ContentView: View {
    @StateObject private var cameraManager = CameraManager()
    @StateObject private var colorFilterManager = ColorFilterManager()
    @StateObject private var motionManager = MotionManager()
    @StateObject private var histogramManager = HistogramManager()
    @StateObject private var focusPeakingManager = FocusPeakingManager()
    @StateObject private var filmSimulationManager = FilmSimulationManager()
    @StateObject private var watermarkEngine = WatermarkEngine()

    @State private var showingSideMenu = false
    @State private var showingFilterPanel = false
    @State private var showingFilmPanel = false
    @State private var showingSettings = false
    @State private var showError = false
    @State private var isCapturing = false

    // MARK: - Overlay Options
    @State private var showGrid3x3 = true
    @State private var showLeveler = true
    @State private var showHistogram = false
    @State private var showFocusPeaking = false

    var body: some View {
        ZStack {
            // MARK: - Camera Preview Layer
            CameraPreviewView(cameraManager: cameraManager)
                .ignoresSafeArea()
                .onTapGesture { location in
                    handleTapToFocus(at: location)
                }

            // MARK: - Focus Peaking Overlay
            FocusPeakingOverlay(focusPeakingManager: focusPeakingManager)

            // MARK: - Film Simulation Overlay
            if let processedPreview = filmSimulationManager.processedPreview {
                Image(decorative: processedPreview, scale: 1)
                    .resizable()
                    .ignoresSafeArea()
                    .allowsHitTesting(false)
            }

            // MARK: - Color Filter Overlay
            if let processedPreview = colorFilterManager.processedPreview {
                Image(decorative: processedPreview, scale: 1)
                    .resizable()
                    .ignoresSafeArea()
                    .allowsHitTesting(false)
            }

            // MARK: - 3x3 Grid Overlay
            if showGrid3x3 {
                Grid3x3Overlay()
                    .allowsHitTesting(false)
            }

            // MARK: - Level Indicator Overlay
            if showLeveler {
                LevelIndicatorOverlay(motionManager: motionManager)
                    .allowsHitTesting(false)
            }

            // MARK: - Compact Histogram (Top Right)
            if showHistogram {
                VStack {
                    HStack {
                        Spacer()
                        CompactHistogramView(histogramManager: histogramManager)
                            .padding(.trailing, 16)
                            .padding(.top, 60)
                    }
                    Spacer()
                }
                .transition(.opacity)
            }

            // MARK: - Top Bar (Minimal)
            VStack {
                HStack {
                    // Menu button
                    Button(action: {
                        withAnimation(.spring(response: 0.3)) {
                            showingSideMenu.toggle()
                        }
                    }) {
                        Image(systemName: "line.3.horizontal")
                            .font(.title2)
                            .foregroundColor(.white)
                            .shadow(color: .black.opacity(0.5), radius: 2)
                    }

                    Spacer()

                    // Format selector
                    FormatSelectorView(cameraManager: cameraManager)

                    Spacer()

                    // Privacy Mode toggle
                    Button(action: {
                        withAnimation(.spring(response: 0.3)) {
                            watermarkEngine.isPrivacyModeEnabled.toggle()
                        }
                    }) {
                        ZStack {
                            Circle()
                                .fill(watermarkEngine.isPrivacyModeEnabled ? Color.blue.opacity(0.8) : Color.gray.opacity(0.5))
                                .frame(width: 36, height: 36)

                            Image(systemName: watermarkEngine.isPrivacyModeEnabled ? "lock.shield.fill" : "eye.slash")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.white)
                        }
                    }
                    .shadow(color: watermarkEngine.isPrivacyModeEnabled ? .blue.opacity(0.5) : .clear, radius: 4)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)

                Spacer()

                // MARK: - Status Bar (ISO, Shutter, Aperture)
                StatusBarView(cameraManager: cameraManager)

                Spacer()

                // MARK: - Capture Button
                CaptureButtonView(cameraManager: cameraManager, isCapturing: $isCapturing)
            }

            // MARK: - Side Menu (Slide from Left)
            if showingSideMenu {
                // Background tap to close
                Color.black.opacity(0.3)
                    .ignoresSafeArea()
                    .onTapGesture {
                        withAnimation(.spring(response: 0.3)) {
                            showingSideMenu = false
                        }
                    }

                // Menu content
                HStack {
                    SideMenuView(
                        cameraManager: cameraManager,
                        colorFilterManager: colorFilterManager,
                        watermarkEngine: watermarkEngine,
                        showGrid3x3: $showGrid3x3,
                        showLeveler: $showLeveler,
                        showHistogram: $showHistogram,
                        showFocusPeaking: $showFocusPeaking,
                        showingFilterPanel: $showingFilterPanel,
                        showingFilmPanel: $showingFilmPanel,
                        showingSettings: $showingSettings,
                        showingSideMenu: $showingSideMenu
                    )
                    .frame(width: 280)
                    .transition(.move(edge: .leading))

                    Spacer()
                }
            }

            // MARK: - Filter Panel (Slide up from bottom)
            if showingFilterPanel {
                VStack {
                    Spacer()
                    FilterPanelView(
                        colorFilterManager: colorFilterManager,
                        showingFilterPanel: $showingFilterPanel
                    )
                    .transition(.move(edge: .bottom))
                }
            }

            // MARK: - Film Simulation Panel (Slide up from bottom)
            if showingFilmPanel {
                VStack {
                    Spacer()
                    FilmSimulationPanelView(
                        filmSimulationManager: filmSimulationManager,
                        showingFilmPanel: $showingFilmPanel
                    )
                    .transition(.move(edge: .bottom))
                }
            }

            // MARK: - Settings Panel
            if showingSettings {
                SettingsPanelView(
                    cameraManager: cameraManager,
                    colorFilterManager: colorFilterManager,
                    watermarkEngine: watermarkEngine,
                    showingSettings: $showingSettings
                )
                .transition(.move(edge: .trailing))
            }
        }
        .onAppear {
            setupCamera()
            setupManagers()
        }
        .onDisappear {
            cameraManager.stopSession()
            motionManager.stopUpdates()
            histogramManager.stopAnalysis()
            focusPeakingManager.disable()
        }
        .alert("Lỗi", isPresented: $showError) {
            Button("OK") {
                cameraManager.state = .idle
            }
        } message: {
            if case .error(let message) = cameraManager.state {
                Text(message)
            }
        }
        .onChange(of: cameraManager.state) { newState in
            if case .error = newState {
                showError = true
            }
        }
    }

    // MARK: - Setup

    private func setupCamera() {
        Task {
            await cameraManager.setupSession()
            cameraManager.colorFilterManager = colorFilterManager
            cameraManager.histogramManager = histogramManager
            cameraManager.focusPeakingManager = focusPeakingManager
            cameraManager.filmSimulationManager = filmSimulationManager
            cameraManager.watermarkEngine = watermarkEngine
            cameraManager.startSession()
        }
    }

    private func setupManagers() {
        motionManager.startUpdates()
        histogramManager.startAnalysis()
    }

    // MARK: - Helpers

    private func handleTapToFocus(at location: CGPoint) {
        let normalizedX = location.x / UIScreen.main.bounds.width
        let normalizedY = location.y / UIScreen.main.bounds.height
        cameraManager.setFocusPoint(CGPoint(x: normalizedX, y: normalizedY))
    }
}

// MARK: - SideMenuView
/// Menu bên trái chứa tất cả controls
struct SideMenuView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var colorFilterManager: ColorFilterManager
    @ObservedObject var watermarkEngine: WatermarkEngine

    @Binding var showGrid3x3: Bool
    @Binding var showLeveler: Bool
    @Binding var showHistogram: Bool
    @Binding var showFocusPeaking: Bool
    @Binding var showingFilterPanel: Bool
    @Binding var showingFilmPanel: Bool
    @Binding var showingSettings: Bool
    @Binding var showingSideMenu: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Image(systemName: "camera.fill")
                    .foregroundColor(.blue)
                Text("Pro Camera")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 20)

            Divider().background(Color.gray.opacity(0.5))

            // MARK: - Quick Actions
            VStack(spacing: 4) {
                // Camera Switch
                SideMenuRow(
                    icon: "camera.rotate",
                    title: "Đổi Camera",
                    color: .white
                ) {
                    cameraManager.switchCamera()
                    closeMenu()
                }

                // Flash/Torch
                SideMenuRow(
                    icon: cameraManager.torchMode == .on ? "bolt.fill" : "bolt.slash.fill",
                    title: cameraManager.torchMode == .on ? "Tắt Đèn" : "Bật Đèn",
                    color: .yellow
                ) {
                    cameraManager.setTorch(mode: cameraManager.torchMode == .on ? .off : .on)
                }
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 8)

            Divider().background(Color.gray.opacity(0.5))

            // MARK: - Pro Tools
            VStack(spacing: 4) {
                SideMenuToggleRow(
                    icon: "squareshape.split.3x3",
                    title: "Lưới 3x3",
                    isOn: $showGrid3x3
                )

                SideMenuToggleRow(
                    icon: "ruler",
                    title: "Độ Nghiêng",
                    isOn: $showLeveler
                )

                SideMenuToggleRow(
                    icon: "chart.bar",
                    title: "Histogram",
                    isOn: $showHistogram
                )

                SideMenuToggleRow(
                    icon: "scope",
                    title: "Focus Peaking",
                    isOn: $showFocusPeaking
                )
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 8)

            Divider().background(Color.gray.opacity(0.5))

            // MARK: - Panels
            VStack(spacing: 4) {
                SideMenuRow(
                    icon: "camera.filters",
                    title: "Bộ Lọc Màu",
                    color: .purple
                ) {
                    showingFilterPanel = true
                    closeMenu()
                }

                SideMenuRow(
                    icon: "film",
                    title: "Mô Phỏng Phim",
                    color: .orange
                ) {
                    showingFilmPanel = true
                    closeMenu()
                }

                SideMenuRow(
                    icon: "gearshape.fill",
                    title: "Cài Đặt",
                    color: .gray
                ) {
                    showingSettings = true
                    closeMenu()
                }
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 8)

            Spacer()

            // Close button
            Button(action: {
                closeMenu()
            }) {
                HStack {
                    Image(systemName: "xmark.circle.fill")
                    Text("Đóng Menu")
                }
                .foregroundColor(.gray)
                .font(.caption)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
                .environment(\.colorScheme, .dark)
        )
    }

    private func closeMenu() {
        withAnimation(.spring(response: 0.3)) {
            showingSideMenu = false
        }
    }
}

// MARK: - SideMenuRow
/// Row trong side menu
struct SideMenuRow: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .frame(width: 24)
                    .foregroundColor(color)
                Text(title)
                    .font(.subheadline)
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(Color.white.opacity(0.05))
            .cornerRadius(8)
        }
    }
}

// MARK: - SideMenuToggleRow
/// Toggle row trong side menu
struct SideMenuToggleRow: View {
    let icon: String
    let title: String
    @Binding var isOn: Bool

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .frame(width: 24)
                .foregroundColor(isOn ? .blue : .gray)
            Text(title)
                .font(.subheadline)
                .foregroundColor(.white)
            Spacer()
            Toggle("", isOn: $isOn)
                .tint(.blue)
                .labelsHidden()
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.05))
        .cornerRadius(8)
    }
}

// MARK: - TopBarView (Simplified - just format and privacy)
/// Top navigation bar
struct TopBarView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var watermarkEngine: WatermarkEngine
    @Binding var showingSettings: Bool
    @Binding var showingFilterPanel: Bool
    @Binding var showingFilmPanel: Bool
    @Binding var showingProTools: Bool

    var body: some View {
        HStack {
            Spacer()

            // Format selector
            FormatSelectorView(cameraManager: cameraManager)

            Spacer()

            // Privacy Mode toggle
            Button(action: {
                withAnimation(.spring(response: 0.3)) {
                    watermarkEngine.isPrivacyModeEnabled.toggle()
                }
            }) {
                ZStack {
                    Circle()
                        .fill(watermarkEngine.isPrivacyModeEnabled ? Color.blue.opacity(0.8) : Color.gray.opacity(0.5))
                        .frame(width: 36, height: 36)

                    Image(systemName: watermarkEngine.isPrivacyModeEnabled ? "lock.shield.fill" : "eye.slash")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.white)
                }
            }
            .shadow(color: watermarkEngine.isPrivacyModeEnabled ? .blue.opacity(0.5) : .clear, radius: 4)
        }
        .padding(.horizontal, 16)
        .padding(.top, 8)
    }
}

// MARK: - FormatSelectorView
/// Chọn định dạng ảnh
struct FormatSelectorView: View {
    @ObservedObject var cameraManager: CameraManager

    var body: some View {
        Menu {
            ForEach(CaptureFormat.allCases) { format in
                Button(action: {
                    cameraManager.settings.captureFormat = format
                }) {
                    HStack {
                        Text(format.rawValue)
                        if cameraManager.settings.captureFormat == format {
                            Image(systemName: "checkmark")
                        }
                    }
                }
            }
        } label: {
            Text(cameraManager.settings.captureFormat.rawValue)
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.white)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.black.opacity(0.6))
                .clipShape(Capsule())
        }
    }
}

// MARK: - StatusBarView
/// Hiển thị thông số camera hiện tại
struct StatusBarView: View {
    @ObservedObject var cameraManager: CameraManager

    var body: some View {
        HStack(spacing: 16) {
            InfoPill(icon: "iso", text: cameraManager.settings.isoDisplay)
            InfoPill(icon: "shutter.speed", text: cameraManager.settings.shutterSpeedDisplay)
            InfoPill(icon: "aperture", text: cameraManager.settings.apertureDisplay)
            InfoPill(icon: "exposure", text: cameraManager.settings.evDisplay)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.black.opacity(0.6))
        .clipShape(Capsule())
    }
}

// MARK: - InfoPill
/// Component hiển thị thông tin nhỏ
struct InfoPill: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: iconForType(icon))
                .font(.caption2)
            Text(text)
                .font(.caption)
                .fontWeight(.medium)
        }
        .foregroundColor(.white)
    }

    private func iconForType(_ type: String) -> String {
        switch type {
        case "iso": return "number"
        case "shutter.speed": return "timer"
        case "aperture": return "camera.aperture"
        case "exposure": return "sun.max"
        default: return "info.circle"
        }
    }
}

// MARK: - CaptureButtonView
/// Nút chụp ảnh
struct CaptureButtonView: View {
    @ObservedObject var cameraManager: CameraManager
    @Binding var isCapturing: Bool

    var body: some View {
        HStack(spacing: 32) {
            // Gallery preview (optional)
            Button(action: {
                // Open photo library
            }) {
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.5))
                    .frame(width: 50, height: 50)
                    .overlay(
                        Image(systemName: "photo.on.rectangle")
                            .foregroundColor(.white)
                    )
            }

            // Capture button
            Button(action: {
                withAnimation(.easeOut(duration: 0.1)) {
                    isCapturing = true
                }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                    withAnimation {
                        isCapturing = false
                    }
                }
                cameraManager.capturePhoto()
            }) {
                ZStack {
                    // Outer ring
                    Circle()
                        .stroke(Color.white, lineWidth: 4)
                        .frame(width: 80, height: 80)

                    // Inner circle
                    Circle()
                        .fill(cameraManager.canCapture ? Color.white : Color.gray)
                        .frame(width: 65, height: 65)
                }
            }
            .disabled(!cameraManager.canCapture)
            .scaleEffect(isCapturing ? 0.85 : (cameraManager.canCapture ? 1.0 : 0.9))
            .animation(.spring(), value: cameraManager.canCapture)

            // Camera switch button
            Button(action: {
                cameraManager.switchCamera()
            }) {
                Image(systemName: "camera.rotate")
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(Color.black.opacity(0.5))
                    .clipShape(Circle())
            }
        }
        .padding(.bottom, 30)
        .padding(.horizontal, 40)
    }
}

// MARK: - FilterPanelView
/// Panel chọn và điều chỉnh bộ lọc màu
struct FilterPanelView: View {
    @ObservedObject var colorFilterManager: ColorFilterManager
    @Binding var showingFilterPanel: Bool

    var body: some View {
        VStack(spacing: 16) {
            // Header
            HStack {
                Text("Color Filters")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Button(action: {
                    showingFilterPanel = false
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.white)
                }
            }
            .padding(.horizontal, 16)

            // Filter presets
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    FilterPreviewButton(
                        name: "None",
                        isSelected: colorFilterManager.currentLUT == nil,
                        action: { colorFilterManager.removeFilter() }
                    )

                    ForEach(FilterPreset.builtInPresets) { preset in
                        FilterPreviewButton(
                            name: preset.name,
                            isSelected: colorFilterManager.currentLUT?.id == preset.id,
                            action: { colorFilterManager.applyFilter(preset) }
                        )
                    }
                }
                .padding(.horizontal, 16)
            }

            // Filter intensity
            HStack {
                Text("Intensity")
                    .font(.caption)
                    .foregroundColor(.gray)
                Slider(value: $colorFilterManager.filterIntensity, in: 0...1.0)
                    .tint(.blue)
                Text(String(format: "%.0f%%", colorFilterManager.filterIntensity * 100))
                    .font(.caption)
                    .foregroundColor(.white)
            }
            .padding(.horizontal, 16)

            // Reset button
            Button(action: {
                colorFilterManager.resetAll()
            }) {
                Text("Reset All")
                    .font(.caption)
                    .foregroundColor(.red)
            }
        }
        .padding(.vertical, 16)
        .background(Color.black.opacity(0.85))
        .cornerRadius(20)
    }
}

// MARK: - FilterPreviewButton
struct FilterPreviewButton: View {
    let name: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.3))
                    .frame(width: 60, height: 60)
                    .overlay(
                        Image(systemName: "camera.filters")
                            .foregroundColor(.white)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 2)
                    )
                Text(name)
                    .font(.caption2)
                    .foregroundColor(.white)
            }
        }
    }
}

// MARK: - SettingsPanelView
/// Panel cài đặt
struct SettingsPanelView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var colorFilterManager: ColorFilterManager
    @ObservedObject var watermarkEngine: WatermarkEngine
    @Binding var showingSettings: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header
            HStack {
                Text("Settings")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Button(action: {
                    showingSettings = false
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.white)
                }
            }

            Divider().background(Color.gray)

            // Camera position
            SettingRow(title: "Camera") {
                Picker("", selection: $cameraManager.currentPosition) {
                    ForEach(CameraPosition.allCases) { position in
                        Text(position.rawValue).tag(position)
                    }
                }
                .pickerStyle(.segmented)
                .onChange(of: cameraManager.currentPosition) { newValue in
                    cameraManager.switchCamera(to: newValue)
                }
            }

            // Focus mode
            SettingRow(title: "Focus") {
                Picker("", selection: $cameraManager.focusMode) {
                    ForEach(FocusModeOption.allCases) { mode in
                        Text(mode.rawValue).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
            }

            // Exposure mode
            SettingRow(title: "Exposure") {
                Picker("", selection: $cameraManager.exposureMode) {
                    ForEach(ExposureModeOption.allCases) { mode in
                        Text(mode.rawValue).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
            }

            // Capture format
            SettingRow(title: "Format") {
                ForEach(CaptureFormat.allCases) { format in
                    Button(action: {
                        cameraManager.settings.captureFormat = format
                    }) {
                        HStack {
                            Text(format.rawValue)
                                .foregroundColor(.white)
                            Spacer()
                            Text(format.description)
                                .font(.caption)
                                .foregroundColor(.gray)
                            if cameraManager.settings.captureFormat == format {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                }
            }

            Divider().background(Color.gray)

            // Privacy Mode Settings
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Image(systemName: "lock.shield.fill")
                        .foregroundColor(.blue)
                    Text("Privacy Mode")
                        .font(.subheadline)
                        .foregroundColor(.white)
                }

                Toggle(isOn: $watermarkEngine.isPrivacyModeEnabled) {
                    HStack {
                        Image(systemName: watermarkEngine.isPrivacyModeEnabled ? "eye.slash.fill" : "eye.fill")
                            .foregroundColor(watermarkEngine.isPrivacyModeEnabled ? .blue : .gray)
                        VStack(alignment: .leading) {
                            Text("GPS Protection")
                                .font(.caption)
                                .foregroundColor(.white)
                            Text("Strip GPS & Add Watermark")
                                .font(.caption2)
                                .foregroundColor(.gray)
                        }
                    }
                }
                .tint(.blue)

                if watermarkEngine.isPrivacyModeEnabled {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Fake Location")
                            .font(.caption)
                            .foregroundColor(.gray)

                        TextField("Enter fake location...", text: $watermarkEngine.fakeLocation)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .font(.caption)

                        Text("Watermark will show this location instead of real GPS")
                            .font(.caption2)
                            .foregroundColor(.gray)
                            .italic()
                    }
                    .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
            .padding(12)
            .background(Color.blue.opacity(0.1))
            .cornerRadius(8)

            Divider().background(Color.gray)

            // Reset
            Button(action: {
                cameraManager.settings = CameraSettings()
                colorFilterManager.resetAll()
                watermarkEngine.isPrivacyModeEnabled = false
                watermarkEngine.fakeLocation = "Somewhere on Earth"
            }) {
                HStack {
                    Image(systemName: "arrow.counterclockwise")
                    Text("Reset All Settings")
                }
                .foregroundColor(.red)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(Color.red.opacity(0.1))
                .cornerRadius(8)
            }
        }
        .padding(20)
        .frame(width: 300)
        .background(Color.black.opacity(0.9))
    }
}

// MARK: - SettingRow
struct SettingRow<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption)
                .foregroundColor(.gray)
            content
        }
    }
}

// MARK: - Grid3x3Overlay
struct Grid3x3Overlay: View {
    var body: some View {
        GeometryReader { geometry in
            let width = geometry.size.width
            let height = geometry.size.height
            let thirdWidth = width / 3
            let thirdHeight = height / 3

            Canvas { context, size in
                for i in 1...2 {
                    let x = thirdWidth * CGFloat(i)
                    var path = Path()
                    path.move(to: CGPoint(x: x, y: 0))
                    path.addLine(to: CGPoint(x: x, y: height))
                    context.stroke(path, with: .color(.white.opacity(0.5)), lineWidth: 0.5)
                }

                for i in 1...2 {
                    let y = thirdHeight * CGFloat(i)
                    var path = Path()
                    path.move(to: CGPoint(x: 0, y: y))
                    path.addLine(to: CGPoint(x: width, y: y))
                    context.stroke(path, with: .color(.white.opacity(0.5)), lineWidth: 0.5)
                }

                let points = [
                    CGPoint(x: thirdWidth, y: thirdHeight),
                    CGPoint(x: thirdWidth * 2, y: thirdHeight),
                    CGPoint(x: thirdWidth, y: thirdHeight * 2),
                    CGPoint(x: thirdWidth * 2, y: thirdHeight * 2)
                ]

                for point in points {
                    let circle = Path(ellipseIn: CGRect(
                        x: point.x - 4,
                        y: point.y - 4,
                        width: 8,
                        height: 8
                    ))
                    context.fill(circle, with: .color(.white.opacity(0.6)))
                }
            }
        }
    }
}

// MARK: - LevelIndicatorOverlay
struct LevelIndicatorOverlay: View {
    @ObservedObject var motionManager: MotionManager

    var body: some View {
        GeometryReader { geometry in
            let centerX = geometry.size.width / 2
            let centerY = geometry.size.height / 2
            let indicatorWidth: CGFloat = 200
            let indicatorHeight: CGFloat = 4

            ZStack {
                RoundedRectangle(cornerRadius: 2)
                    .fill(motionManager.levelColor)
                    .frame(width: indicatorWidth, height: indicatorHeight)
                    .position(x: centerX, y: centerY)
                    .rotationEffect(.degrees(motionManager.indicatorRotation))

                Circle()
                    .fill(Color.white.opacity(0.8))
                    .frame(width: 8, height: 8)
                    .position(x: centerX, y: centerY)

                Text(motionManager.deviationText)
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(motionManager.levelColor)
                    .position(x: centerX, y: centerY + 20)

                Path { path in
                    path.move(to: CGPoint(x: centerX - 40, y: centerY))
                    path.addLine(to: CGPoint(x: centerX - 15, y: centerY))
                }
                .stroke(Color.white.opacity(0.3), lineWidth: 1)

                Path { path in
                    path.move(to: CGPoint(x: centerX + 15, y: centerY))
                    path.addLine(to: CGPoint(x: centerX + 40, y: centerY))
                }
                .stroke(Color.white.opacity(0.3), lineWidth: 1)
            }
        }
    }
}

// MARK: - ProToolsPanelView (Legacy - kept for compatibility)
struct ProToolsPanelView: View {
    @ObservedObject var motionManager: MotionManager
    @ObservedObject var histogramManager: HistogramManager
    @ObservedObject var focusPeakingManager: FocusPeakingManager

    @Binding var showGrid3x3: Bool
    @Binding var showLeveler: Bool
    @Binding var showHistogram: Bool
    @Binding var showFocusPeaking: Bool
    @Binding var showingProTools: Bool

    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Text("Pro Tools")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Button(action: { showingProTools = false }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.white)
                }
            }
            .padding(.horizontal, 16)

            Divider().background(Color.gray)

            Toggle(isOn: $showGrid3x3) {
                HStack {
                    Image(systemName: "squareshape.split.3x3")
                    Text("3x3 Grid")
                }
                .font(.caption)
                .foregroundColor(.white)
            }
            .tint(.blue)
            .padding(.horizontal, 16)

            Toggle(isOn: $showLeveler) {
                HStack {
                    Image(systemName: "ruler")
                    Text("Level Indicator")
                }
                .font(.caption)
                .foregroundColor(.white)
            }
            .tint(.blue)
            .padding(.horizontal, 16)

            Toggle(isOn: $showHistogram) {
                HStack {
                    Image(systemName: "chart.bar")
                    Text("Live Histogram")
                }
                .font(.caption)
                .foregroundColor(.white)
            }
            .tint(.blue)
            .padding(.horizontal, 16)

            FocusPeakingControls(focusPeakingManager: focusPeakingManager)
                .padding(.horizontal, 16)

            Divider().background(Color.gray)

            HStack {
                Circle()
                    .fill(motionManager.levelColor)
                    .frame(width: 10, height: 10)
                Text(motionManager.isLevel ? "Device is Level" : "Adjust device angle")
                    .font(.caption)
                    .foregroundColor(.gray)
                Spacer()
                Text(String(format: "Roll: %+.1f°", motionManager.roll))
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.white)
            }
            .padding(.horizontal, 16)
        }
        .padding(.vertical, 16)
        .background(Color.black.opacity(0.85))
        .cornerRadius(20)
    }
}

// MARK: - FilmSimulationPanelView
struct FilmSimulationPanelView: View {
    @ObservedObject var filmSimulationManager: FilmSimulationManager
    @Binding var showingFilmPanel: Bool

    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Text("Film Simulation")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Button(action: { showingFilmPanel = false }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.white)
                }
            }
            .padding(.horizontal, 16)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(FilmPresetType.allCases) { filmType in
                        FilmPresetButton(
                            type: filmType,
                            isSelected: filmSimulationManager.currentFilm == filmType,
                            action: {
                                withAnimation(.spring(response: 0.3)) {
                                    filmSimulationManager.selectFilm(filmType)
                                }
                            }
                        )
                    }
                }
                .padding(.horizontal, 16)
            }

            if filmSimulationManager.currentFilm != .original {
                Text(filmSimulationManager.currentFilm.description)
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.horizontal, 16)
                    .multilineTextAlignment(.center)
            }

            HStack {
                Text("Intensity")
                    .font(.caption)
                    .foregroundColor(.gray)
                Slider(value: $filmSimulationManager.intensity, in: 0...1.0)
                    .tint(filmSimulationManager.currentFilm.accentColor)
                Text(String(format: "%.0f%%", filmSimulationManager.intensity * 100))
                    .font(.caption)
                    .foregroundColor(.white)
            }
            .padding(.horizontal, 16)

            Button(action: {
                withAnimation {
                    filmSimulationManager.reset()
                }
            }) {
                Text("Reset")
                    .font(.caption)
                    .foregroundColor(.red)
            }
        }
        .padding(.vertical, 16)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(.ultraThinMaterial)
                .environment(\.colorScheme, .dark)
        )
    }
}

// MARK: - FilmPresetButton
struct FilmPresetButton: View {
    let type: FilmPresetType
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(type.accentColor.opacity(0.2))
                        .frame(width: 70, height: 70)
                    Image(systemName: type.iconName)
                        .font(.title2)
                        .foregroundColor(type.accentColor)
                }
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(isSelected ? type.accentColor : Color.clear, lineWidth: 2)
                )
                Text(type.rawValue)
                    .font(.caption2)
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
