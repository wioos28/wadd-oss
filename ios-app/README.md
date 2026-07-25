# KE App - iOS

iOS client for Knowledge Engine AI.

## Features

- **Knowledge Search**: Search through your knowledge base with multiple modes
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
├── ViewModels/
│   └── (ViewModel files)
├── Views/
│   ├── ContentView.swift    # Main view
│   ├── LoginView.swift      # Authentication
│   ├── HomeView.swift       # Dashboard
│   ├── SearchView.swift     # Knowledge search
│   ├── ChatView.swift       # AI chat
│   └── ProfileView.swift    # User profile
├── Services/
│   ├── APIService.swift     # API client
│   └── AuthManager.swift    # Authentication
└── Utils/
    └── (Utility files)
```

## Setup

1. Open `KEApp.xcodeproj` in Xcode
2. Select your development team
3. Build and run

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

- **ke-app-ios**: Build on push to main/develop
- **ke-app-ios-testflight**: Deploy to TestFlight on tag push (v*)

## Environment Variables

Set these in Codemagic UI under Teams > apple_credentials:

| Variable | Description |
|----------|-------------|
| `APPLE_TEAM_ID` | Apple Developer Team ID |
| `APPLE_CONNECT_API_KEY_ID` | App Store Connect API Key ID |
| `APPLE_CONNECT_API_ISSUER_ID` | App Store Connect API Issuer ID |
| `APPLE_CONNECT_API_KEY` | Private key (PEM format) |

## Building

```bash
# Install dependencies
cd ios && pod install

# Build
xcodebuild -workspace KEApp.xcworkspace \
  -scheme KEApp \
  -sdk iphoneos \
  -configuration Release
```

## Testing

```bash
xcodebuild test \
  -workspace KEApp.xcworkspace \
  -scheme KEApp \
  -destination 'platform=iOS Simulator,name=iPhone 15'
```
