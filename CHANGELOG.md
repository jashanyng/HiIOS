# 变更日志（Changelog）

本文件记录 HiIOS 效率库所有公开可见的版本演进与变更内容，作为每次版本更新说明（Release Notes）的唯一事实源。版本号统一采用不带 `v` 前缀的裸 `x.y.z` 格式，由根目录 [`VERSION`](VERSION) 统一锁定；日常尚未归档版本的改动先记入 `## [Unreleased]`，升版时经由 `scripts/bump_version.py` 自动归档至对应版本节。

## [Unreleased]

## [0.0.1]

### 新增

- **纯 SwiftPM 单分发基础架构**：以根 [`Package.swift`](Package.swift) 与 [`Package.resolved`](Package.resolved) 为唯一事实源，确立 `iOS 17+` 与 `Swift 6`（`swiftLanguageModes: [.v6]`）平台基线，锁定 8 个直接第三方依赖精确稳定版本（`SwifterSwift` `8.0.0`、`DeviceKit` `5.10.0`、`Moya` `15.0.0`、`Alamofire` `5.12.2`、`RxSwift` `6.9.0`、`SwiftyBeaver` `2.1.1`、`SFSafeSymbols` `7.0.0`、`SwiftSoup` `2.11.3`）。
- **Base 家族（`HiIOSBase`）**：提供无内部与平台 UI 依赖的纯 Swift 模型、领域错误、脱敏日志与统计契约以及社会化分享（`socialsharing`）契约。
- **Core 家族（`HiIOSCore`）**：提供通用语义颜色、字体、资源读取、序列化、文件与设备描述工具（依赖 `HiIOSBase`、`SwifterSwift`、`DeviceKit`）。
- **Net 家族（`HiIOSNetCore`、`HiIOSNetRxSwift`、`HiIOSNetCombine`，聚合别名 `HiIOSNet`）**：提供基于 `Moya` / `Alamofire` 的 HTTP 传输契约与可选 RxSwift / Combine 响应式适配器。
- **Nav 家族（`HiIOSNavCore`、`HiIOSNavRxSwift`、`HiIOSNavCombine`，聚合别名 `HiIOSNav`）**：提供强类型路由、`URLRouter` 安全校验（`SanitizedURL`）、路由栈（`NavigationRouteStack`）与展示状态，以及 RxSwift / Combine 响应式适配器。
- **Store 家族（`HiIOSStoreCore`、`HiIOSStoreKeychain`、`HiIOSStoreDefaults`、`HiIOSStoreFile`，聚合组合 `HiIOSStore`）**：提供字节存储、Keychain 安全值契约与可替换本地存储适配器。
- **Suite 家族（`HiIOSSuiteCore`、`HiIOSSuiteLogOSLog`、`HiIOSSuiteLogSwiftyBeaver`，聚合别名 `HiIOSSuite`）**：提供无业务语义的通用 SwiftUI 页面外观组件与 OSLog / SwiftyBeaver 可选日志输出适配器。
- **独立可选产品与便捷入口**：提供独立可选模块 `HiIOSGHTrending`（依赖 `HiIOSNetCore` 与 `SwiftSoup`）及便捷聚合入口 `HiIOS`（组合 `HiIOSCore`、`HiIOSNetCombine`、`HiIOSNavCombine`、`HiIOSStore*`、`HiIOSSuiteCore` 与 `SFSafeSymbols`）。
- **工程与版本治理基线**：建立 SwiftPM 宿主测试与 iOS Simulator 全包测试基线、同级源码依赖 40 位 commit SHA 门禁规范（[`docs/engineering/sibling-source-dependency.md`](docs/engineering/sibling-source-dependency.md)）及版本号与治理文档校验脚本。
