import SwiftUI

@main
struct KEApp: App {
    @StateObject private var appState = AppState()
    @StateObject private var authManager = AuthManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(authManager)
        }
    }
}
