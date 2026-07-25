# Firebase Integration for iOS

## Overview
Firebase is Google's app development platform with services for authentication, databases, analytics, and more.

## Setup

### Installation (SPM)
```swift
// In Xcode: File > Add Package Dependencies
// https://github.com/firebase/firebase-ios-sdk
```

### Initialization
```swift
import Firebase

@main
struct MyApp: App {
    init() {
        FirebaseApp.configure()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## Authentication

### Email/Password
```swift
import FirebaseAuth

class AuthManager: ObservableObject {
    @Published var user: User?
    
    func signIn(email: String, password: String) async throws {
        let result = try await Auth.auth().signIn(withEmail: email, password: password)
        user = result.user
    }
    
    func signUp(email: String, password: String) async throws {
        let result = try await Auth.auth().createUser(withEmail: email, password: password)
        user = result.user
    }
    
    func signOut() throws {
        try Auth.auth().signOut()
        user = nil
    }
}
```

### Google Sign-In
```swift
import GoogleSignIn

func signInWithGoogle() async throws {
    guard let clientID = FirebaseApp.app()?.options.clientID else { return }
    let config = GIDConfiguration(clientID: clientID)
    GIDSignIn.sharedInstance.configuration = config
    
    let result = try await GIDSignIn.sharedInstance.signIn(withPresenting: UIApplication.shared.rootViewController)
    let user = result.user
    let idToken = user.idToken?.tokenString ?? ""
    
    let credential = GoogleAuthProvider.credential(withIDToken: idToken, accessToken: user.accessToken.tokenString)
    try await Auth.auth().signIn(with: credential)
}
```

## Firestore

### Reading Data
```swift
import FirebaseFirestore

class FirestoreService {
    let db = Firestore.firestore()
    
    func getUsers() async throws -> [User] {
        let snapshot = try await db.collection("users").getDocuments()
        return snapshot.documents.compactMap { doc in
            try? doc.data(as: User.self)
        }
    }
    
    func getUser(id: String) async throws -> User? {
        let doc = try await db.collection("users").document(id).getDocument()
        return try doc.data(as: User.self)
    }
}
```

### Writing Data
```swift
func addUser(_ user: User) async throws {
    try db.collection("users").document(user.id).setData(from: user)
}

func updateUser(id: String, data: [String: Any]) async throws {
    try await db.collection("users").document(id).updateData(data)
}

func deleteUser(id: String) async throws {
    try await db.collection("users").document(id).delete()
}
```

### Real-time Listener
```swift
func listenToUsers() {
    db.collection("users")
        .addSnapshotListener { snapshot, error in
            guard let documents = snapshot?.documents else { return }
            let users = documents.compactMap { try? $0.data(as: User.self) }
            // Update UI
        }
}
```

## Storage

### Upload File
```swift
import FirebaseStorage

func uploadImage(_ image: UIImage, path: String) async throws -> String {
    guard let data = image.jpegData(compressionQuality: 0.8) else { throw StorageError.invalidData }
    
    let storageRef = Storage.storage().reference().child(path)
    let metadata = StorageMetadata()
    metadata.contentType = "image/jpeg"
    
    _ = try await storageRef.putDataAsync(data, metadata: metadata)
    let url = try await storageRef.downloadURL()
    return url.absoluteString
}
```

### Download File
```swift
func downloadImage(from urlString: String) async throws -> UIImage {
    let storageRef = Storage.storage().reference(forURL: urlString)
    let data = try await storageRef.data(maxSize: 10 * 1024 * 1024) // 10MB max
    guard let image = UIImage(data: data) else { throw StorageError.invalidImage }
    return image
}
```

## Analytics

### Log Events
```swift
import FirebaseAnalytics

Analytics.logEvent("content_viewed", parameters: [
    "content_id": "12345",
    "content_type": "article",
    "source": "search"
])

// Custom user properties
Analytics.setUserProperty("premium", forName: "subscription_level")
```

## Push Notifications

### Setup
```swift
import FirebaseMessaging

class NotificationManager: NSObject, MessagingDelegate, UNUserNotificationCenterDelegate {
    func setup() {
        Messaging.messaging().delegate = self
        UNUserNotificationCenter.current().delegate = self
        
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, _ in
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }
    
    func messaging(_ messaging: Messaging, didReceiveRegistrationToken fcmToken: String?) {
        guard let token = fcmToken else { return }
        print("FCM Token: \(token)")
        // Send to server
    }
}
```

## Best Practices
- Use Firebase Security Rules
- Enable offline persistence for Firestore
- Use Cloud Functions for complex logic
- Monitor with Firebase Crashlytics
- A/B test with Firebase Remote Config
