import Foundation
import Combine

// MARK: - Local LLM Service
class LocalLLMService: ObservableObject {
    static let shared = LocalLLMService()

    @MainActor @Published var isModelLoaded = false
    @MainActor @Published var modelPath: String?
    @MainActor @Published var errorMessage: String?

    private var inferenceEngine: LlamaInference?

    init() {
        Task {
            await loadModel()
        }
    }

    // MARK: - Load Model from Bundle
    @MainActor
    func loadModel() {
        print("Attempting to load embedded AI model...")

        // Method 1: Look for model.gguf directly in bundle
        if let modelPath = Bundle.main.path(forResource: "model", ofType: "gguf") {
            print("FOUND EMBEDDED MODEL AT: \(modelPath)")
            self.modelPath = modelPath
            initializeEngine(path: modelPath)
            return
        }

        // Method 2: Look in Resources/ subdirectory
        if let modelURL = Bundle.main.url(forResource: "model", withExtension: "gguf", subdirectory: "Resources") {
            print("FOUND EMBEDDED MODEL AT: \(modelURL.path)")
            self.modelPath = modelURL.path
            initializeEngine(path: modelURL.path)
            return
        }

        // Method 3: Search all bundle resources
        if let resourcePath = Bundle.main.resourcePath {
            let possiblePaths = [
                "\(resourcePath)/model.gguf",
                "\(resourcePath)/Resources/model.gguf",
                "\(resourcePath)/KEApp/model.gguf",
                "\(resourcePath)/KEApp/Resources/model.gguf"
            ]

            for path in possiblePaths {
                if FileManager.default.fileExists(atPath: path) {
                    print("FOUND EMBEDDED MODEL AT: \(path)")
                    self.modelPath = path
                    initializeEngine(path: path)
                    return
                }
            }
        }

        // Model not found
        let error = "Model file not found in bundle! Please ensure model.gguf is included in the app resources."
        print(error)
        self.errorMessage = error
        self.isModelLoaded = false
    }

    // MARK: - Initialize Inference Engine
    private func initializeEngine(path: String) {
        do {
            inferenceEngine = try LlamaInference(modelPath: path)
            isModelLoaded = true
            print("AI model loaded successfully!")
        } catch {
            let error = "Failed to initialize LLM engine: \(error.localizedDescription)"
            print(error)
            self.errorMessage = error
            self.isModelLoaded = false
        }
    }

    // MARK: - Check if model is loaded (nonisolated for cross-actor access)
    nonisolated func isModelReady() -> Bool {
        MainActor.assumeIsolated {
            self.isModelLoaded
        }
    }

    // MARK: - Generate Response (Offline)
    func generateResponse(prompt: String, maxTokens: Int = 512) async throws -> String {
        let isLoaded = await isModelReady()
        guard isLoaded, let engine = inferenceEngine else {
            throw LLMError.modelNotLoaded
        }

        return try await withCheckedThrowingContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                do {
                    let response = try engine.generate(
                        prompt: prompt,
                        maxTokens: maxTokens,
                        temperature: 0.7,
                        topP: 0.9
                    )
                    continuation.resume(returning: response)
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // MARK: - Generate Chat Response (Offline)
    func generateChatResponse(message: String, history: [[String: String]]) async throws -> String {
        // Build prompt from history
        var prompt = "You are Wcore X, a helpful AI assistant.\n\n"

        for msg in history {
            if let role = msg["role"], let content = msg["content"] {
                if role == "user" {
                    prompt += "User: \(content)\n"
                } else {
                    prompt += "Assistant: \(content)\n"
                }
            }
        }

        prompt += "User: \(message)\nAssistant:"

        return try await generateResponse(prompt: prompt)
    }

    // MARK: - Get Model Info
    @MainActor
    func getModelInfo() -> [String: Any] {
        var info: [String: Any] = [
            "isLoaded": isModelLoaded,
            "modelPath": modelPath ?? "Not found"
        ]

        if let path = modelPath, let attributes = try? FileManager.default.attributesOfItem(atPath: path) {
            if let size = attributes[.size] as? Int64 {
                info["modelSize"] = ByteCountFormatter.string(fromByteCount: size, countStyle: .file)
            }
        }

        return info
    }
}

// MARK: - LLM Errors
enum LLMError: LocalizedError, Sendable {
    case modelNotLoaded
    case modelLoadFailed(String)
    case inferenceFailed(String)

    var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "AI model is not loaded. Please restart the app."
        case .modelLoadFailed(let reason):
            return "Failed to load AI model: \(reason)"
        case .inferenceFailed(let reason):
            return "AI inference failed: \(reason)"
        }
    }
}

// MARK: - Llama Inference Engine (Placeholder)
// TODO: Replace with actual llama.cpp Swift bindings
final class LlamaInference: @unchecked Sendable {
    private let modelPath: String
    private let context: OpaquePointer?

    init(modelPath: String) throws {
        self.modelPath = modelPath
        // Initialize llama.cpp context
        // This is a placeholder - implement with actual llama.cpp Swift API
        self.context = nil
        print("LlamaInference initialized with model: \(modelPath)")
    }

    func generate(prompt: String, maxTokens: Int, temperature: Float, topP: Float) throws -> String {
        // Placeholder implementation
        // Replace with actual llama.cpp inference calls
        return "[Offline AI Response] This is a placeholder response. Connect llama.cpp to enable real inference."
    }

    deinit {
        // Clean up llama.cpp context
    }
}
