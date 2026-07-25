// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "KEApp",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "KEApp",
            targets: ["KEApp"]
        ),
    ],
    dependencies: [
        // Add dependencies here
        // .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
    ],
    targets: [
        .target(
            name: "KEApp",
            dependencies: []
        ),
    ]
)
