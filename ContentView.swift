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

    @State private var showingControls = true
    @State private var showingFilterPanel = false
    @State private var showingFilmPanel = false
    @State private var showingSettings = false
    @State private var showingProTools = false
    @State private var showError = false

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

            // MARK: - Top Bar
            VStack {
                TopBarView(
                    cameraManager: cameraManager,
                    showingSettings: $showingSettings,
                    showingFilterPanel: $showingFilterPanel,
                    showingProTools: $showingProTools
                )

                Spacer()

                // MARK: - Status Bar (ISO, Shutter, Aperture)
                if showingControls {
                    StatusBarView(cameraManager: cameraManager)
                        .transition(.move(edge: .top).combined(with: .opacity))
                }

                Spacer()

                // MARK: - Compact Histogram (Top Right)
                if showHistogram {
                    VStack {
                        HStack {
                            Spacer()
                            CompactHistogramView(histogramManager: histogramManager)
                                .padding(.trailing, 16)
                                .padding(.top, 8)
                        }
                        Spacer()
                    }
                    .transition(.opacity)
                }

                // MARK: - Control Panel
                if showingControls {
                    ControlPanelView(cameraManager: cameraManager)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                }

                // MARK: - Capture Button & Bottom Controls
                CaptureButtonView(cameraManager: cameraManager)
            }
            .animation(.easeInOut(duration: 0.3), value: showingControls)
            .animation(.easeInOut(duration: 0.3), value: showingFilterPanel)

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

            // MARK: - Pro Tools Panel
            if showingProTools {
                VStack {
                    Spacer()
                    ProToolsPanelView(
                        motionManager: motionManager,
                        histogramManager: histogramManager,
                        focusPeakingManager: focusPeakingManager,
                        showGrid3x3: $showGrid3x3,
                        showLeveler: $showLeveler,
                        showHistogram: $showHistogram,
                        showFocusPeaking: $showFocusPeaking,
                        showingProTools: $showingProTools
                    )
                    .transition(.move(edge: .bottom))
                }
            }

            // MARK: - Settings Panel
            if showingSettings {
                SettingsPanelView(
                    cameraManager: cameraManager,
                    colorFilterManager: colorFilterManager,
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
            cameraManager.startSession()
        }
    }

    private func setupManagers() {
        // Start motion updates for level indicator
        motionManager.startUpdates()

        // Start histogram analysis
        histogramManager.startAnalysis()
    }

    // MARK: - Helpers

    private func handleTapToFocus(at location: CGPoint) {
        // Convert tap location to normalized coordinates
        // Assuming full screen
        let normalizedX = location.x / UIScreen.main.bounds.width
        let normalizedY = location.y / UIScreen.main.bounds.height
        cameraManager.setFocusPoint(CGPoint(x: normalizedX, y: normalizedY))
    }
}

// MARK: - TopBarView
/// Top navigation bar
struct TopBarView: View {
    @ObservedObject var cameraManager: CameraManager
    @Binding var showingSettings: Bool
    @Binding var showingFilterPanel: Bool
    @Binding var showingProTools: Bool

    var body: some View {
        HStack {
            // Close button
            Button(action: {
                // Exit app or dismiss
            }) {
                Image(systemName: "xmark.circle.fill")
                    .font(.title2)
                    .foregroundColor(.white)
                    .shadow(color: .black.opacity(0.5), radius: 2)
            }

            Spacer()

            // Format selector
            FormatSelectorView(cameraManager: cameraManager)

            Spacer()

            // Pro Tools button
            Button(action: {
                showingProTools.toggle()
            }) {
                Image(systemName: "slider.horizontal.3")
                    .font(.title2)
                    .foregroundColor(.white)
                    .shadow(color: .black.opacity(0.5), radius: 2)
            }

            // Film Simulation button
            Button(action: {
                showingFilmPanel.toggle()
            }) {
                Image(systemName: "film")
                    .font(.title2)
                    .foregroundColor(filmSimulationManager.currentFilm == .original ? .white : filmSimulationManager.currentFilm.accentColor)
                    .shadow(color: .black.opacity(0.5), radius: 2)
            }

            // Filter button
            Button(action: {
                showingFilterPanel.toggle()
            }) {
                Image(systemName: "camera.filters")
                    .font(.title2)
                    .foregroundColor(.white)
                    .shadow(color: .black.opacity(0.5), radius: 2)
            }

            // Settings button
            Button(action: {
                showingSettings.toggle()
            }) {
                Image(systemName: "gearshape.fill")
                    .font(.title2)
                    .foregroundColor(.white)
                    .shadow(color: .black.opacity(0.5), radius: 2)
            }
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
            // ISO
            InfoPill(
                icon: "iso",
                text: cameraManager.settings.isoDisplay
            )

            // Shutter Speed
            InfoPill(
                icon: "shutter.speed",
                text: cameraManager.settings.shutterSpeedDisplay
            )

            // Aperture
            InfoPill(
                icon: "aperture",
                text: cameraManager.settings.apertureDisplay
            )

            // EV
            InfoPill(
                icon: "exposure",
                text: cameraManager.settings.evDisplay
            )
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

// MARK: - ControlPanelView
/// Panel điều khiển chính
struct ControlPanelView: View {
    @ObservedObject var cameraManager: CameraManager
    @State private var selectedTab: ControlTab = .manual

    enum ControlTab: String, CaseIterable {
        case manual = "Manual"
        case color = "Color"
        case wb = "WB"
    }

    var body: some View {
        VStack(spacing: 0) {
            // Tab selector
            Picker("Control Tab", selection: $selectedTab) {
                ForEach(ControlTab.allCases, id: \.self) { tab in
                    Text(tab.rawValue).tag(tab)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 40)
            .padding(.bottom, 8)

            // Control content
            switch selectedTab {
            case .manual:
                ManualControlsView(cameraManager: cameraManager)
            case .color:
                ColorControlsView(cameraManager: cameraManager)
            case .wb:
                WhiteBalanceControlsView(cameraManager: cameraManager)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color.black.opacity(0.7))
        .cornerRadius(20)
    }
}

// MARK: - ManualControlsView
/// Điều khiển thủ công: ISO, Shutter Speed, EV
struct ManualControlsView: View {
    @ObservedObject var cameraManager: CameraManager

    var body: some View {
        VStack(spacing: 12) {
            // ISO Slider
            HStack {
                Text("ISO")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.iso,
                       in: 25...2500,
                       step: 25) { _ in
                    cameraManager.setISO(cameraManager.settings.iso)
                }
                .tint(.orange)

                Text(cameraManager.settings.isoDisplay)
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 60, alignment: .trailing)
            }

            // Shutter Speed Slider
            HStack {
                Text("SS")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.shutterSpeed,
                       in: 0.001...2.0,
                       step: 0.001) { _ in
                    cameraManager.setShutterSpeed(cameraManager.settings.shutterSpeed)
                }
                .tint(.blue)

                Text(cameraManager.settings.shutterSpeedDisplay)
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 60, alignment: .trailing)
            }

            // EV Slider
            HStack {
                Text("EV")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.exposureCompensation,
                       in: -3.0...3.0,
                       step: 0.3) { _ in
                    cameraManager.setExposureCompensation(cameraManager.settings.exposureCompensation)
                }
                .tint(.green)

                Text(cameraManager.settings.evDisplay)
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 60, alignment: .trailing)
            }

            // Torch Toggle
            HStack {
                Text("Torch")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Toggle("", isOn: Binding(
                    get: { cameraManager.torchMode == .on },
                    set: { isOn in
                        cameraManager.setTorch(mode: isOn ? .on : .off)
                    }
                ))
                .tint(.yellow)

                Spacer()

                if cameraManager.torchMode == .on {
                    Slider(value: $cameraManager.torchLevel, in: 0...1) { _ in
                        cameraManager.setTorch(mode: .on, level: cameraManager.torchLevel)
                    }
                    .frame(width: 100)
                    .tint(.yellow)
                }
            }
        }
        .padding(.horizontal, 12)
    }
}

// MARK: - ColorControlsView
/// Điều chỉnh màu sắc
struct ColorControlsView: View {
    @ObservedObject var cameraManager: CameraManager

    var body: some View {
        VStack(spacing: 12) {
            // Saturation
            HStack {
                Text("Sat")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.saturation,
                       in: 0...2.0,
                       step: 0.05) { _ in
                    cameraManager.colorFilterManager?.setSaturation(cameraManager.settings.saturation)
                }
                .tint(.purple)

                Text(String(format: "%.1f", cameraManager.settings.saturation))
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 40, alignment: .trailing)
            }

            // Contrast
            HStack {
                Text("Con")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.contrast,
                       in: 0...2.0,
                       step: 0.05) { _ in
                    cameraManager.colorFilterManager?.setContrast(cameraManager.settings.contrast)
                }
                .tint(.pink)

                Text(String(format: "%.1f", cameraManager.settings.contrast))
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 40, alignment: .trailing)
            }

            // Brightness
            HStack {
                Text("Bri")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.brightness,
                       in: -1.0...1.0,
                       step: 0.05) { _ in
                    cameraManager.colorFilterManager?.setBrightness(cameraManager.settings.brightness)
                }
                .tint(.cyan)

                Text(String(format: "%.1f", cameraManager.settings.brightness))
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 40, alignment: .trailing)
            }

            // Vignette
            HStack {
                Text("Vig")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.vignette,
                       in: 0...1.0,
                       step: 0.05) { _ in
                    cameraManager.colorFilterManager?.setVignette(cameraManager.settings.vignette)
                }
                .tint(.gray)

                Text(String(format: "%.1f", cameraManager.settings.vignette))
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 40, alignment: .trailing)
            }
        }
        .padding(.horizontal, 12)
    }
}

// MARK: - WhiteBalanceControlsView
/// Điều khiển White Balance
struct WhiteBalanceControlsView: View {
    @ObservedObject var cameraManager: CameraManager

    var body: some View {
        VStack(spacing: 12) {
            // Temperature Slider
            HStack {
                Text("Temp")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.customTemperature,
                       in: 2000...10000,
                       step: 100) { _ in
                    cameraManager.setWhiteBalanceTemperature(cameraManager.settings.customTemperature)
                }
                .tint(.orange)

                Text("\(Int(cameraManager.settings.customTemperature))K")
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 50, alignment: .trailing)
            }

            // Tint Slider
            HStack {
                Text("Tint")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(width: 40, alignment: .leading)

                Slider(value: $cameraManager.settings.tint,
                       in: -1.0...1.0,
                       step: 0.05) { _ in
                    cameraManager.setTint(cameraManager.settings.tint)
                }
                .tint(.green)

                Text(String(format: "%.1f", cameraManager.settings.tint))
                    .font(.caption)
                    .foregroundColor(.white)
                    .frame(width: 40, alignment: .trailing)
            }

            // Quick Presets
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(WhiteBalancePreset.allCases) { preset in
                        Button(action: {
                            cameraManager.setWhiteBalancePreset(preset)
                        }) {
                            Text(preset.rawValue)
                                .font(.caption)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(cameraManager.settings.whiteBalancePreset == preset
                                           ? Color.white.opacity(0.3)
                                           : Color.gray.opacity(0.3))
                                .cornerRadius(8)
                        }
                        .foregroundColor(.white)
                    }
                }
            }
        }
        .padding(.horizontal, 12)
    }
}

// MARK: - CaptureButtonView
/// Nút chụp ảnh
struct CaptureButtonView: View {
    @ObservedObject var cameraManager: CameraManager

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
            .scaleEffect(cameraManager.canCapture ? 1.0 : 0.9)
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
                    // No filter
                    FilterPreviewButton(
                        name: "None",
                        isSelected: colorFilterManager.currentLUT == nil,
                        action: {
                            colorFilterManager.removeFilter()
                        }
                    )

                    // Built-in filters
                    ForEach(FilterPreset.builtInPresets) { preset in
                        FilterPreviewButton(
                            name: preset.name,
                            isSelected: colorFilterManager.currentLUT?.id == preset.id,
                            action: {
                                colorFilterManager.applyFilter(preset)
                            }
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
/// Button hiển thị preview filter
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

            // Reset
            Button(action: {
                cameraManager.settings = CameraSettings()
                colorFilterManager.resetAll()
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
/// Row trong settings
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
/// Lưới 3x3 (Rule of Thirds) overlay trên camera preview
struct Grid3x3Overlay: View {
    var body: some View {
        GeometryReader { geometry in
            let width = geometry.size.width
            let height = geometry.size.height
            let thirdWidth = width / 3
            let thirdHeight = height / 3

            Canvas { context, size in
                // Draw vertical lines
                for i in 1...2 {
                    let x = thirdWidth * CGFloat(i)
                    var path = Path()
                    path.move(to: CGPoint(x: x, y: 0))
                    path.addLine(to: CGPoint(x: x, y: height))
                    context.stroke(path, with: .color(.white.opacity(0.5)), lineWidth: 0.5)
                }

                // Draw horizontal lines
                for i in 1...2 {
                    let y = thirdHeight * CGFloat(i)
                    var path = Path()
                    path.move(to: CGPoint(x: 0, y: y))
                    path.addLine(to: CGPoint(x: width, y: y))
                    context.stroke(path, with: .color(.white.opacity(0.5)), lineWidth: 0.5)
                }

                // Draw intersection points (power points)
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
/// Vạch chỉ thị cân bằng điện tử
struct LevelIndicatorOverlay: View {
    @ObservedObject var motionManager: MotionManager

    var body: some View {
        GeometryReader { geometry in
            let centerX = geometry.size.width / 2
            let centerY = geometry.size.height / 2
            let indicatorWidth: CGFloat = 200
            let indicatorHeight: CGFloat = 4

            ZStack {
                // Main level line
                RoundedRectangle(cornerRadius: 2)
                    .fill(motionManager.levelColor)
                    .frame(width: indicatorWidth, height: indicatorHeight)
                    .position(x: centerX, y: centerY)
                    .rotationEffect(.degrees(motionManager.indicatorRotation))

                // Center reference point
                Circle()
                    .fill(Color.white.opacity(0.8))
                    .frame(width: 8, height: 8)
                    .position(x: centerX, y: centerY)

                // Deviation text
                Text(motionManager.deviationText)
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(motionManager.levelColor)
                    .position(x: centerX, y: centerY + 20)

                // Fixed reference lines (horizontal)
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

// MARK: - ProToolsPanelView
/// Panel hiển thị các công cụ chuyên nghiệp
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
            // Header
            HStack {
                Text("Pro Tools")
                    .font(.headline)
                    .foregroundColor(.white)

                Spacer()

                Button(action: {
                    showingProTools = false
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.white)
                }
            }
            .padding(.horizontal, 16)

            Divider().background(Color.gray)

            // Grid Toggle
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

            // Leveler Toggle
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

            // Histogram Toggle
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

            // Focus Peaking Controls
            FocusPeakingControls(focusPeakingManager: focusPeakingManager)
                .padding(.horizontal, 16)

            Divider().background(Color.gray)

            // Level Status
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
/// Panel chọn và điều chỉnh mô phỏng phim
struct FilmSimulationPanelView: View {
    @ObservedObject var filmSimulationManager: FilmSimulationManager
    @Binding var showingFilmPanel: Bool

    var body: some View {
        VStack(spacing: 16) {
            // Header
            HStack {
                Text("Film Simulation")
                    .font(.headline)
                    .foregroundColor(.white)

                Spacer()

                Button(action: {
                    showingFilmPanel = false
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.white)
                }
            }
            .padding(.horizontal, 16)

            // Film presets horizontal scroll
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

            // Film description
            if filmSimulationManager.currentFilm != .original {
                Text(filmSimulationManager.currentFilm.description)
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.horizontal, 16)
                    .multilineTextAlignment(.center)
            }

            // Intensity slider
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

            // Reset button
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
/// Button hiển thị preview phim mô phỏng
struct FilmPresetButton: View {
    let type: FilmPresetType
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                // Film icon with accent color
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

                // Film name
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
