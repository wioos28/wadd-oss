import Foundation
import Combine
import Network

// MARK: - Configuration
struct AppConfig {
    static let shared = AppConfig()

    #if DEBUG
    static let apiBaseURL = "http://localhost:8000"
    static let chromaDBURL = "http://localhost:8000/api"
    #else
    static let apiBaseURL = "https://api.wcorex.com"
    static let chromaDBURL = "https://api.wcorex.com/api"
    #endif
}

// MARK: - API Service
class APIService: ObservableObject {
    static let shared = APIService()

    private let baseURL: String
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()
    private let monitor = NWPathMonitor()
    private let monitorQueue = DispatchQueue(label: "NetworkMonitor")

    @Published var isOnline = true
    @Published var offlineModeEnabled = true

    init(baseURL: String = AppConfig.apiBaseURL) {
        self.baseURL = baseURL

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.waitsForConnectivity = true
        self.session = URLSession(configuration: config)

        startNetworkMonitoring()
    }

    // MARK: - Network Monitoring
    private func startNetworkMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isOnline = path.status == .satisfied
            }
        }
        monitor.start(queue: monitorQueue)
    }

    // MARK: - Smart Chat (Auto-switch Online/Offline)
    func sendChatMessage(_ message: String, history: [[String: String]]) async throws -> String {
        // Try online first
        if isOnline {
            do {
                return try await sendChatOnline(message: message, history: history)
            } catch {
                // If server fails, fall back to offline
                if offlineModeEnabled {
                    return try await sendChatOffline(message: message, history: history)
                }
                throw error
            }
        }

        // Offline mode
        if offlineModeEnabled {
            return try await sendChatOffline(message: message, history: history)
        }

        throw APIError.serverUnavailable
    }

    // MARK: - Online Chat (Server)
    private func sendChatOnline(message: String, history: [[String: String]]) async throws -> String {
        let url = URL(string: "\(baseURL)/api/chat")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ["message": message, "history": history] as [String: Any]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.chatFailed
        }

        let result = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        return result?["response"] as? String ?? "No response"
    }

    // MARK: - Offline Chat (Local AI)
    private func sendChatOffline(message: String, history: [[String: String]]) async throws -> String {
        let llmService = LocalLLMService.shared

        guard llmService.isModelReady() else {
            throw LLMError.modelNotLoaded
        }

        return try await llmService.generateChatResponse(message: message, history: history)
    }

    // MARK: - Auth
    func login(username: String, password: String) async throws -> User {
        let url = URL(string: "\(baseURL)/api/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ["username": username, "password": password]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.unauthorized
        }

        return try JSONDecoder().decode(User.self, from: data)
    }

    func register(username: String, email: String, password: String) async throws -> User {
        let url = URL(string: "\(baseURL)/api/auth/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ["username": username, "email": email, "password": password]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 201 else {
            throw APIError.registrationFailed
        }

        return try JSONDecoder().decode(User.self, from: data)
    }

    // MARK: - Knowledge
    func queryKnowledge(text: String, mode: String = "hybrid", limit: Int = 10) async throws -> [QueryResult] {
        let encodedText = text.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? text
        let url = URL(string: "\(baseURL)/api/knowledge/query?text=\(encodedText)&mode=\(mode)&limit=\(limit)")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode([QueryResult].self, from: data)
    }

    func getKnowledgeEntries(sourceType: String? = nil, limit: Int = 20) async throws -> [KnowledgeEntry] {
        var urlComponents = URLComponents(string: "\(baseURL)/api/knowledge/entries")!
        var queryItems = [URLQueryItem(name: "limit", value: String(limit))]
        if let sourceType = sourceType {
            queryItems.append(URLQueryItem(name: "source_type", value: sourceType))
        }
        urlComponents.queryItems = queryItems

        let (data, _) = try await session.data(from: urlComponents.url!)
        return try JSONDecoder().decode([KnowledgeEntry].self, from: data)
    }

    func searchKnowledge(query: String, sourceType: String? = nil) async throws -> [KnowledgeEntry] {
        let encodedQuery = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? query
        var urlComponents = URLComponents(string: "\(baseURL)/api/knowledge/search")!
        var queryItems = [URLQueryItem(name: "q", value: encodedQuery)]
        if let sourceType = sourceType {
            queryItems.append(URLQueryItem(name: "source_type", value: sourceType))
        }
        urlComponents.queryItems = queryItems

        let (data, _) = try await session.data(from: urlComponents.url!)
        return try JSONDecoder().decode([KnowledgeEntry].self, from: data)
    }

    // MARK: - Health Check
    func checkServerHealth() async throws -> Bool {
        let url = URL(string: "\(baseURL)/")!
        let (_, response) = try await session.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse else {
            return false
        }
        return httpResponse.statusCode == 200
    }

    // MARK: - Get Status
    func getStatus() async -> [String: Any] {
        let modelInfo = await LocalLLMService.shared.getModelInfo()
        return [
            "isOnline": isOnline,
            "offlineModeEnabled": offlineModeEnabled,
            "serverURL": baseURL,
            "localModel": modelInfo
        ]
    }
}

// MARK: - API Errors
enum APIError: LocalizedError {
    case invalidURL
    case networkError(Error)
    case unauthorized
    case registrationFailed
    case chatFailed
    case decodingError
    case serverError(Int)
    case serverUnavailable

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .networkError(let error): return "Network error: \(error.localizedDescription)"
        case .unauthorized: return "Invalid credentials"
        case .registrationFailed: return "Registration failed"
        case .chatFailed: return "Chat request failed"
        case .decodingError: return "Failed to decode response"
        case .serverError(let code): return "Server error: \(code)"
        case .serverUnavailable: return "Server is unavailable. Please check your connection."
        }
    }
}
