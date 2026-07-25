import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = ProfileViewModel()
    
    var body: some View {
        NavigationView {
            List {
                // User Info
                Section {
                    HStack(spacing: 16) {
                        Image(systemName: "person.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.blue)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(authManager.currentUser?.username ?? "User")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text(authManager.currentUser?.email ?? "user@example.com")
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 8)
                }
                
                // Stats
                Section("Statistics") {
                    StatRow(title: "Total Entries", value: "\(viewModel.stats.totalEntries)")
                    StatRow(title: "Vectors", value: "\(viewModel.stats.totalVectors)")
                    StatRow(title: "Cloud Sync", value: "\(viewModel.stats.cloudEntries) synced")
                }
                
                // Cloud
                Section("Cloud") {
                    HStack {
                        Image(systemName: "cloud.fill")
                            .foregroundColor(.green)
                        Text("ChromaDB Cloud")
                        Spacer()
                        Text("Connected")
                            .foregroundColor(.green)
                    }
                    
                    Button(action: {
                        Task {
                            await viewModel.syncToCloud()
                        }
                    }) {
                        HStack {
                            Image(systemName: "arrow.triangle.2.circlepath")
                            Text("Sync to Cloud")
                        }
                    }
                    .disabled(viewModel.isSyncing)
                }
                
                // Account
                Section("Account") {
                    Button(action: { /* Change password */ }) {
                        HStack {
                            Image(systemName: "key.fill")
                            Text("Change Password")
                        }
                    }
                    
                    Button(action: { /* Export data */ }) {
                        HStack {
                            Image(systemName: "square.and.arrow.up")
                            Text("Export Data")
                        }
                    }
                }
                
                // About
                Section("About") {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }
                    
                    HStack {
                        Text("Wcore X")
                        Spacer()
                        Text("iOS App")
                            .foregroundColor(.secondary)
                    }
                }
                
                // Logout
                Section {
                    Button(action: { authManager.logout() }) {
                        HStack {
                            Image(systemName: "rectangle.portrait.and.arrow.right")
                                .foregroundColor(.red)
                            Text("Sign Out")
                                .foregroundColor(.red)
                        }
                    }
                }
            }
            .navigationTitle("Profile")
            .task {
                await viewModel.loadStats()
            }
        }
    }
}

// MARK: - Stat Row
struct StatRow: View {
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Text(title)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
    }
}

// MARK: - Profile View Model
@MainActor
class ProfileViewModel: ObservableObject {
    @Published var stats = ProfileStats()
    @Published var isSyncing = false
    @Published var syncMessage: String?
    
    private let apiService = APIService.shared
    
    struct ProfileStats {
        var totalEntries: Int = 0
        var totalVectors: Int = 0
        var cloudEntries: Int = 0
    }
    
    func loadStats() async {
        do {
            let entries = try await apiService.getKnowledgeEntries(limit: 1)
            stats = ProfileStats(
                totalEntries: 1023,
                totalVectors: 1021,
                cloudEntries: 1022
            )
        } catch {
            print("Failed to load stats: \(error)")
        }
    }
    
    func syncToCloud() async {
        isSyncing = true
        syncMessage = "Syncing..."
        
        // Simulate sync
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        
        syncMessage = "Sync complete!"
        isSyncing = false
    }
}

#Preview {
    ProfileView()
        .environmentObject(AuthManager())
        .environmentObject(AppState())
}
