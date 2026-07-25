# CI/CD Configuration

This directory contains all CI/CD configuration files for the Knowledge Engine project.

## Directory Structure

```
ci-cd/
├── README.md              # This file
├── ios/
│   ├── codemagic.yaml     # Codemagic CI/CD for iOS
│   └── ExportOptions.plist # App Store export options
├── android/
│   └── (future)           # Android CI/CD
└── web/
    └── (future)           # Web deployment
```

## iOS CI/CD (Codemagic)

### Setup

1. Go to [codemagic.io](https://codemagic.io)
2. Connect your GitHub repository
3. Set the workflow file path to: `ci-cd/ios/codemagic.yaml`

### Environment Variables

Create a group `apple_credentials` in Codemagic with:

| Variable | Description |
|----------|-------------|
| `APPLE_TEAM_ID` | Your Apple Developer Team ID |
| `APPLE_CONNECT_API_KEY_ID` | App Store Connect API Key ID |
| `APPLE_CONNECT_API_ISSUER_ID` | App Store Connect API Issuer ID |
| `APPLE_CONNECT_API_KEY` | Private key (PEM format) |

### Workflows

- **ke-app-ios**: Build on push to main/develop
- **ke-app-ios-testflight**: Deploy to TestFlight on tag push (v*)

## Deployment

### iOS

```bash
# Build locally
cd ios-app
xcodebuild -workspace KEApp.xcworkspace \
  -scheme KEApp \
  -sdk iphoneos \
  -configuration Release

# Or use Codemagic (push to main)
git push origin main
```

### Web (Future)

```bash
# Deploy to Vercel
vercel --prod

# Or deploy to Netlify
netlify deploy --prod
```
