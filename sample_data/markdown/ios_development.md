# iOS Development with SwiftUI

## Overview
SwiftUI is Apple's declarative UI framework for building apps across all Apple platforms.

## Key Concepts

### 1. Views
```swift
struct ContentView: View {
    var body: some View {
        VStack {
            Text("Hello, World!")
                .font(.largeTitle)
                .foregroundColor(.blue)
            Image(systemName: "star.fill")
                .foregroundColor(.yellow)
        }
    }
}
```

### 2. State Management
```swift
// @State - Local state
@State private var count = 0

// @Binding - Two-way binding
@Binding var isOn: Bool

// @ObservedObject - Reference type observable
@ObservedObject var viewModel: MyViewModel

// @StateObject - Own observable
@StateObject var viewModel = MyViewModel()

// @EnvironmentObject - Shared observable
@EnvironmentObject var appState: AppState
```

### 3. Navigation
```swift
// iOS 16+
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            Text(item.name)
        }
    }
    .navigationDestination(for: Item.self) { item in
        DetailView(item: item)
    }
}
```

### 4. Lists and Data
```swift
List {
    Section("Favorites") {
        ForEach(favorites) { item in
            Text(item.name)
        }
        .onDelete(perform: deleteItems)
        .onMove(perform: moveItems)
    }
}
```

### 5. Networking
```swift
func fetchData() async throws -> Data {
    let url = URL(string: "https://api.example.com/data")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}
```

### 6. Core Data Integration
```swift
@FetchRequest(
    sortDescriptors: [NSSortDescriptor(keyPath: \Item.timestamp, ascending: true)],
    animation: .default
)
private var items: FetchedResults<Item>
```

### 7. App Lifecycle
```swift
@main
struct MyApp: App {
    @StateObject var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}
```

## Best Practices
- Use MVVM pattern
- Keep views small and composable
- Use @StateObject for owned objects
- Prefer async/await over Combine
- Use SwiftUI previews for development
