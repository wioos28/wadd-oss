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
    ],
    targets: [
        .target(
            name: "WcoreX",
            dependencies: [],
            path: "KEApp",
            resources: [
                .copy("Resources")
            ]
        ),
    ]
)
