import SwiftUI
import Combine

// MARK: - Auth Manager
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var error: String?
    
    private let apiService: APIService
    private let userDefaults = UserDefaults.standard
    private let userKey = "currentUser"
    private let tokenKey = "authToken"
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
        loadSavedUser()
    }
    
    // MARK: - Login
    func login(username: String, password: String) async {
        isLoading = true
        error = nil
        
        do {
            let user = try await apiService.login(username: username, password: password)
            await MainActor.run {
                self.currentUser = user
                self.isAuthenticated = true
                self.saveUser(user)
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
        }
        
        await MainActor.run {
            self.isLoading = false
        }
    }
    
    // MARK: - Register
    func register(username: String, email: String, password: String) async {
        isLoading = true
        error = nil
        
        do {
            let user = try await apiService.register(username: username, email: email, password: password)
            await MainActor.run {
                self.currentUser = user
                self.isAuthenticated = true
                self.saveUser(user)
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
        }
        
        await MainActor.run {
            self.isLoading = false
        }
    }
    
    // MARK: - Logout
    func logout() {
        currentUser = nil
        isAuthenticated = false
        userDefaults.removeObject(forKey: userKey)
        userDefaults.removeObject(forKey: tokenKey)
    }
    
    // MARK: - Persistence
    private func saveUser(_ user: User) {
        if let data = try? JSONEncoder().encode(user) {
            userDefaults.set(data, forKey: userKey)
        }
    }
    
    private func loadSavedUser() {
        guard let data = userDefaults.data(forKey: userKey),
              let user = try? JSONDecoder().decode(User.self, from: data) else {
            return
        }
        
        currentUser = user
        isAuthenticated = true
    }
}
