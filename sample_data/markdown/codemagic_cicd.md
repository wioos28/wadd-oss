# Codemagic CI/CD for iOS

## Overview
Codemagic is a CI/CD platform designed specifically for mobile app development.

## codemagic.yaml Configuration

### Basic Setup
```yaml
workflows:
  ios-workflow:
    name: iOS Build
    max_build_duration: 60
    environment:
      groups:
        - apple_credentials
      flutter: stable
      xcode: latest
      cocoapods: default
    triggering:
      events:
        - push
      branch_patterns:
        - pattern: 'main'
          include: true
    scripts:
      - name: Install dependencies
        script: |
          flutter pub get
      - name: Build iOS
        script: |
          flutter build ios --release --no-codesign
    artifacts:
      - build/ios/ipa/*.ipa
    publishing:
      email:
        recipients:
          - team@example.com
```

### Flutter + iOS
```yaml
workflows:
  flutter-ios:
    name: Flutter iOS
    environment:
      flutter: stable
      xcode: latest
      cocoapods: default
    scripts:
      - name: Setup
        script: flutter pub get
      - name: Build
        script: flutter build ios --release
      - name: Upload to TestFlight
        script: |
          cd ios
          fastlane ios beta
    artifacts:
      - build/ios/ipa/*.ipa
```

### Fastlane Integration
```yaml
workflows:
  fastlane-ios:
    name: Fastlane iOS
    environment:
      ruby: default
      cocoapods: default
    scripts:
      - name: Install bundle
        script: bundle install
      - name: Run tests
        script: bundle exec fastlane test
      - name: Build
        script: bundle exec fastlane build
      - name: Deploy
        script: bundle exec fastlane deploy
```

## Environment Variables

### Apple Credentials
```yaml
environment:
  groups:
    - apple_credentials
```

In Codemagic UI, create group `apple_credentials` with:
- `APPLE_TEAM_ID`: Your Apple Developer Team ID
- `APPLE_CONNECT_API_KEY_ID`: App Store Connect API Key ID
- `APPLE_CONNECT_API_ISSUER_ID`: App Store Connect API Issuer ID
- `APPLE_CONNECT_API_KEY`: Private key (PEM format)

### Signing
```yaml
environment:
  groups:
    - app_store_credentials
  variables:
    APP_STORE_CONNECT_API_KEY_ID: $APPLE_CONNECT_API_KEY_ID
```

## Build Scripts

### Flutter Build
```yaml
scripts:
  - name: Flutter pub get
    script: flutter pub get
  - name: Flutter analyze
    script: flutter analyze
  - name: Flutter test
    script: flutter test
  - name: Build iOS release
    script: flutter build ios --release
  - name: Build iOS release (no codesign)
    script: flutter build ios --release --no-codesign
```

### CocoaPods
```yaml
scripts:
  - name: CocoaPods install
    script: |
      cd ios
      pod install --repo-update
```

## Artifacts

### IPA Files
```yaml
artifacts:
  - build/ios/ipa/*.ipa
  - build/ios/archive/*.xcarchive
  - ios/Pods/**
```

## Publishing

### App Store
```yaml
publishing:
  app_store_connect:
    api_key: $APPLE_CONNECT_API_KEY
    key_id: $APPLE_CONNECT_API_KEY_ID
    issuer_id: $APPLE_CONNECT_API_ISSUER_ID
```

### Firebase App Distribution
```yaml
publishing:
  firebase:
    firebase_token: $FIREBASE_TOKEN
    app_id: "1:1234567890:ios:abcdef123456"
    groups:
      - testers
```

### Email
```yaml
publishing:
  email:
    recipients:
      - team@example.com
    subject: "Build Complete"
    body: "Build {{build_number}} completed successfully."
```

## Caching

### CocoaPods Cache
```yaml
cache:
  cache_paths:
    - ~/.cocoapods
    - ios/Pods
```

### Flutter Cache
```yaml
cache:
  cache_paths:
    - $FLUTTER_ROOT/.pub-cache
```

## Monorepo Support
```yaml
workflows:
  app-ios:
    name: App iOS
    max_build_duration: 60
    environment:
      flutter: stable
    triggering:
      events:
        - push
      branch_patterns:
        - pattern: 'main'
          include: true
      changeset:
        include_paths:
          - app/**
          - shared/**
    scripts:
      - name: Build app
        script: |
          cd app
          flutter pub get
          flutter build ios
```
