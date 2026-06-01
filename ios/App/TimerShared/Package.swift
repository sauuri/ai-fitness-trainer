// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "TimerShared",
    platforms: [.iOS(.v15)],
    products: [
        .library(name: "TimerShared", targets: ["TimerShared"])
    ],
    dependencies: [],
    targets: [
        .target(name: "TimerShared", dependencies: [])
    ]
)
