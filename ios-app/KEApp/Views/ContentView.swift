import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var authManager: AuthManager
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
        .preferredColorScheme(.dark)
    }
}

// MARK: - Main Tab View
struct MainTabView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        TabView(selection: $appState.selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: AppState.Tab.home.rawValue)
                }
                .tag(AppState.Tab.home)
            
            SearchView()
                .tabItem {
                    Label("Search", systemImage: AppState.Tab.search.rawValue)
                }
                .tag(AppState.Tab.search)
            
            ChatView()
                .tabItem {
                    Label("Chat", systemImage: AppState.Tab.chat.rawValue)
                }
                .tag(AppState.Tab.chat)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: AppState.Tab.profile.rawValue)
                }
                .tag(AppState.Tab.profile)
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
        .environmentObject(AuthManager())
}
