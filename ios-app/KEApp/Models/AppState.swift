import SwiftUI
import Combine

// MARK: - App State
class AppState: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var selectedTab: Tab = .home
    @Published var isLoading = false
    @Published var error: String?
    
    enum Tab: String, CaseIterable {
        case home = "house"
        case search = "magnifyingglass"
        case chat = "bubble.left.and.bubble.right"
        case profile = "person"
        
        var title: String {
            switch self {
            case .home: return "Home"
            case .search: return "Search"
            case .chat: return "Chat"
            case .profile: return "Profile"
            }
        }
    }
}

// MARK: - User Model
struct User: Codable, Identifiable {
    let id: String
    let username: String
    let email: String
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, username, email
        case createdAt = "created_at"
    }
}

// MARK: - Knowledge Entry Model
struct KnowledgeEntry: Codable, Identifiable {
    let id: String
    let content: String
    let sourceType: String
    let sourcePath: String?
    let tags: [String]
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, content, tags
        case sourceType = "source_type"
        case sourcePath = "source_path"
        case createdAt = "created_at"
    }
}

// MARK: - Chat Message Model
struct ChatMessage: Identifiable {
    let id = UUID()
    let role: MessageRole
    let content: String
    let timestamp: Date
    
    enum MessageRole: String {
        case user
        case assistant
    }
}

// MARK: - Query Result Model
struct QueryResult: Codable, Identifiable {
    let id: String
    let entry: KnowledgeEntry
    let score: Double
    let retrievalMode: String
    
    enum CodingKeys: String, CodingKey {
        case id, entry, score
        case retrievalMode = "retrieval_mode"
    }
}
