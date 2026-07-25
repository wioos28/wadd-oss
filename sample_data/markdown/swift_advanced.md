# Advanced Swift Programming

## Protocols and Generics

### Protocol with Associated Types
```swift
protocol Repository {
    associatedtype Item
    
    func fetchAll() async throws -> [Item]
    func fetch(id: String) async throws -> Item?
    func save(_ item: Item) async throws
    func delete(_ item: Item) async throws
}

// Generic implementation
class UserRepository: Repository {
    typealias Item = User
    
    func fetchAll() async throws -> [User] {
        // Implementation
    }
    
    func fetch(id: String) async throws -> User? {
        // Implementation
    }
    
    func save(_ item: User) async throws {
        // Implementation
    }
    
    func delete(_ item: User) async throws {
        // Implementation
    }
}
```

### Protocol Extensions
```swift
protocol Loggable {
    var logTag: String { get }
}

extension Loggable {
    var logTag: String {
        String(describing: Self.self)
    }
    
    func log(_ message: String) {
        print("[\(logTag)] \(message)")
    }
}

struct UserManager: Loggable {
    func loadUsers() {
        log("Loading users") // Auto-provides logTag
    }
}
```

## Result Builders

### ViewBuilder
```swift
@resultBuilder
struct ArrayBuilder {
    static func buildBlock(_ components: Int...) -> [Int] {
        components
    }
    
    static func buildOptional(_ component: [Int]?) -> [Int] {
        component ?? []
    }
    
    static func buildEither(first component: [Int]) -> [Int] {
        component
    }
    
    static func buildEither(second component: [Int]) -> [Int] {
        component
    }
}

@ArrayBuilder
func makeArray() -> [Int] {
    1
    2
    3
}
```

### HTML Builder
```swift
@resultBuilder
struct HTMLBuilder {
    static func buildBlock(_ components: String...) -> String {
        components.joined(separator: "\n")
    }
    
    static func buildOptional(_ component: String?) -> String {
        component ?? ""
    }
    
    static func buildEither(first component: String) -> String {
        component
    }
    
    static func buildEither(second component: String) -> String {
        component
    }
}

func html(@HTMLBuilder content: () -> String) -> String {
    "<html>\n\(content())\n</html>"
}

let page = html {
    "<head><title>Test</title></head>"
    "<body><h1>Hello</h1></body>"
}
```

## Property Wrappers

### Published Alternative
```swift
@propertyWrapper
class UserDefault<T> {
    let key: String
    let defaultValue: T
    
    var wrappedValue: T {
        get { UserDefaults.standard.object(forKey: key) as? T ?? defaultValue }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }
    
    init(_ key: String, defaultValue: T) {
        self.key = key
        self.defaultValue = defaultValue
    }
}

class Settings {
    @UserDefault("theme", defaultValue: "light")
    var theme: String
    
    @UserDefault("notifications", defaultValue: true)
    var notifications: Bool
}
```

### Clamped
```swift
@propertyWrapper
struct Clamped<Value: Comparable> {
    var wrappedValue: Value {
        didSet { wrappedValue = min(max(wrappedValue, range.lowerBound), range.upperBound) }
    }
    
    let range: ClosedRange<Value>
    
    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.wrappedValue = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

struct Player {
    @Clamped(0...100)
    var health: Int = 100
    
    @Clamped(0...999)
    var score: Int = 0
}
```

## Structured Concurrency

### Actors
```swift
actor BankAccount {
    private var balance: Double = 0
    
    var currentBalance: Double {
        balance
    }
    
    func deposit(_ amount: Double) {
        balance += amount
    }
    
    func withdraw(_ amount: Double) throws {
        guard balance >= amount else {
            throw BankError.insufficientFunds
        }
        balance -= amount
    }
}

// Usage
let account = BankAccount()
Task {
    await account.deposit(100)
    let balance = await account.currentBalance
}
```

### Task Groups
```swift
func processItems(_ items: [Item]) async throws -> [Result] {
    try await withThrowingTaskGroup(of: Result.self) { group in
        for item in items {
            group.addTask {
                try await self.process(item)
            }
        }
        
        var results: [Result] = []
        for try await result in group {
            results.append(result)
        }
        return results
    }
}
```

### Async Sequences
```swift
func fetchPages() async throws -> [Page] {
    var pages: [Page] = []
    
    for try await page in fetchPagesStream() {
        pages.append(page)
    }
    
    return pages
}

func fetchPagesStream() -> AsyncThrowingStream<Page, Error> {
    AsyncThrowingStream { continuation in
        Task {
            var page = 1
            while true {
                let data = try await fetchPage(page)
                continuation.yield(data)
                page += 1
            }
        }
    }
}
```

## Macros (Swift 5.9+)

### External Macro
```swift
@attached(member, names: named(init), named(description))
@attached(extension, conformances: CustomStringConvertible)
macro AutoInit()
```

### Custom Macro
```swift
@attached(member, names: arbitrary)
public macro AutoCodable() = #externalMacro(
    module: "Macros",
    type: "AutoCodableMacro"
)
```

## Best Practices
- Use actors for thread-safe state
- Prefer value types over reference types
- Use property wrappers for reusable behavior
- Leverage result builders for DSLs
- Use structured concurrency over completion handlers
