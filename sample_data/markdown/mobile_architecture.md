# Mobile App Architecture

## MVVM Pattern

### Model
```swift
struct User: Codable, Identifiable {
    let id: UUID
    let name: String
    let email: String
}
```

### ViewModel
```swift
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private let apiService: APIService
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    func fetchUsers() async {
        isLoading = true
        do {
            users = try await apiService.fetchUsers()
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }
}
```

### View
```swift
struct UserListView: View {
    @StateObject private var viewModel = UserViewModel()
    
    var body: some View {
        List(viewModel.users) { user in
            VStack(alignment: .leading) {
                Text(user.name).font(.headline)
                Text(user.email).font(.subheadline)
            }
        }
        .task { await viewModel.fetchUsers() }
        .overlay {
            if viewModel.isLoading {
                ProgressView()
            }
        }
    }
}
```

## Coordinator Pattern
```swift
class AppCoordinator: ObservableObject {
    @Published var path = NavigationPath()
    
    func showDetail(for item: Item) {
        path.append(item)
    }
    
    func goBack() {
        path.removeLast()
    }
}
```

## Dependency Injection
```swift
protocol UserRepositoryProtocol {
    func fetchUsers() async throws -> [User]
}

class UserRepository: UserRepositoryProtocol {
    func fetchUsers() async throws -> [User] {
        // API call
    }
}

// In ViewModel
init(repository: UserRepositoryProtocol = UserRepository()) {
    self.repository = repository
}
```

## Error Handling
```swift
enum APIError: LocalizedError {
    case invalidURL
    case networkError(Error)
    case decodingError
    case serverError(Int)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .networkError(let error): return "Network error: \(error.localizedDescription)"
        case .decodingError: return "Failed to decode response"
        case .serverError(let code): return "Server error: \(code)"
        }
    }
}
```

## Testing
```swift
// Unit Test
class UserViewModelTests: XCTestCase {
    func testFetchUsers() async {
        let mockRepo = MockUserRepository()
        let viewModel = UserViewModel(repository: mockRepo)
        
        await viewModel.fetchUsers()
        
        XCTAssertEqual(viewModel.users.count, 2)
        XCTAssertFalse(viewModel.isLoading)
    }
}

// Mock
class MockUserRepository: UserRepositoryProtocol {
    var usersToReturn: [User] = []
    
    func fetchUsers() async throws -> [User] {
        return usersToReturn
    }
}
```
