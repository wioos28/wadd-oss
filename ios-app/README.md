# Wcore X - iOS

iOS client for Wcore X - AI-powered Knowledge Management.

## Features

- **Knowledge Search**: Search through your knowledge base with multiple modes (semantic, keyword, hybrid)
- **AI Chat**: Interactive chat with RAG (Retrieval-Augmented Generation)
- **Cloud Sync**: Sync knowledge to ChromaDB Cloud
- **User Accounts**: Authentication and profile management

## Requirements

- iOS 17.0+
- Xcode 15.0+
- Swift 5.9+

## Architecture

- **SwiftUI**: Declarative UI framework
- **MVVM**: Model-View-ViewModel pattern
- **Combine**: Reactive programming
- **Async/Await**: Modern concurrency

## Project Structure

```
KEApp/
├── KEApp.swift              # App entry point
├── Models/
│   └── AppState.swift       # Data models
├── Views/
│   ├── ContentView.swift    # Main view
│   ├── LoginView.swift      # Authentication
│   ├── HomeView.swift       # Dashboard
│   ├── SearchView.swift     # Knowledge search
│   ├── ChatView.swift       # AI chat
│   └── ProfileView.swift    # User profile
├── Services/
│   ├── APIService.swift     # API client (ChromaDB connected)
│   └── AuthManager.swift    # Authentication
└── Resources/
    └── Assets.xcassets      # App icons and images
```

## Setup

1. Open `KEApp.xcodeproj` in Xcode
2. Select your development team
3. Build and run

## API Configuration

The app connects to the Wcore X backend server. Configure the server URL in `APIService.swift`:

```swift
// Debug mode (local development)
static let apiBaseURL = "http://localhost:8000"

// Release mode (production)
static let apiBaseURL = "https://api.wcorex.com"
```

## CI/CD

This project uses Codemagic for CI/CD.

### Setup Codemagic

1. Go to [codemagic.io](https://codemagic.io)
2. Connect your GitHub repository
3. Create app credentials:
   - `APPLE_TEAM_ID`: Your Apple Developer Team ID
   - `APPLE_CONNECT_API_KEY_ID`: App Store Connect API Key ID
   - `APPLE_CONNECT_API_ISSUER_ID`: App Store Connect API Issuer ID
   - `APPLE_CONNECT_API_KEY`: Private key (PEM format)

### Workflows

- **ke-app-ios**: Build unsigned IPA on push to main/develop

## Building

```bash
# Build unsigned IPA (requires macOS with Xcode)
make build-ipa

# Or use the script directly
./scripts/build-ipa.sh
```

## Testing

```bash
xcodebuild test \
  -project KEApp.xcodeproj \
  -scheme KEApp \
  -destination 'platform=iOS Simulator,name=iPhone 15'
```
