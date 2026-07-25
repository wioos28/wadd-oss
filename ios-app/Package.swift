// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "WcoreX",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "WcoreX",
            targets: ["WcoreX"]
        ),
    ],
    dependencies: [
        // Add dependencies here
        // .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
    ],
    targets: [
        .target(
            name: "WcoreX",
            dependencies: [],
            path: "KEApp"
        ),
    ]
)
