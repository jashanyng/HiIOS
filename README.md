# HiIOS

HiIOS 效率库是独立于具体业务的 iOS 基础能力库，仅通过 **Swift Package Manager（SwiftPM）** 单一渠道分发，以根 [`Package.swift`](Package.swift) 为唯一事实源。当前仓库处于**制作期**，版本基线定为 `0.0.1`，制作期日常源码提交不预先创建 Git 标签。

## 产品家族与模块

| 家族 | 公开产品模块 | 核心职责 |
| --- | --- | --- |
| Base | `HiIOSBase` | 纯 Swift 模型、领域错误、日志、统计与社会化分享（`socialsharing`）契约 |
| Core | `HiIOSCore` | 通用语义颜色、字体、资源读取、序列化、文件与设备描述工具 |
| Net | `HiIOSNetCore`、`HiIOSNetRxSwift`、`HiIOSNetCombine`（聚合别名 `HiIOSNet`） | HTTP 传输契约、Moya transport 与可选响应式适配器 |
| Nav | `HiIOSNavCore`、`HiIOSNavRxSwift`、`HiIOSNavCombine`（聚合别名 `HiIOSNav`） | 强类型路由、`URLRouter` 安全校验、路由栈与展示状态 |
| Store | `HiIOSStoreCore`、`HiIOSStoreKeychain`、`HiIOSStoreDefaults`、`HiIOSStoreFile`（聚合组合 `HiIOSStore`） | 字节存储、Keychain 安全值契约与可替换适配器 |
| Suite | `HiIOSSuiteCore`、`HiIOSSuiteLogOSLog`、`HiIOSSuiteLogSwiftyBeaver`（聚合别名 `HiIOSSuite`） | 无业务语义的通用 SwiftUI 页面外观组件与可选日志输出通道 |
| 按需扩展 | `HiIOSGHTrending` | 独立可选的 GitHub Trending 解析与注入式客户端模块 |
| 便捷入口 | `HiIOS` | 组合 `HiIOSCore`、`HiIOSNetCombine`、`HiIOSNavCombine`、`HiIOSStore*`、`HiIOSSuiteCore` 与 `SFSafeSymbols` |

便捷入口 `HiIOS` 默认不构建或链接 `RxSwift` 适配器、`HiIOSGHTrending` 或厂商闭源 SDK；SwiftPM 仍可能解析 manifest 中其他可选 product 声明的外部依赖。消费项目源码须显式导入实际使用的具体模块，不使用 `@_exported import` 隐式重导出。

### 单向依赖图

- `HiIOSBase` 无内部模块依赖；
- `HiIOSCore` 依赖 `HiIOSBase`；
- `HiIOSNetCore`、`HiIOSNavCore` 与 `HiIOSSuiteCore` 依赖 `HiIOSCore`（各 `Net`/`Nav` 响应式适配器分别依赖对应的 `NetCore`/`NavCore`）；
- `HiIOSStoreCore` 依赖 `HiIOSBase`（各存储适配器依赖 `HiIOSStoreCore`，其中 `HiIOSStoreKeychain` 同时依赖 `HiIOSBase`）；
- 日志适配器 `HiIOSSuiteLogOSLog` 与 `HiIOSSuiteLogSwiftyBeaver` 依赖 `HiIOSBase`；
- `HiIOSGHTrending` 依赖 `HiIOSNetCore`。

直接第三方依赖均在 [`Package.swift`](Package.swift) 中锁定精确稳定版本，并与 [`Package.resolved`](Package.resolved) 保持同步。

## 接入方式

HiIOS 效率库版本号与 Git 标签统一采用无 `v` 前缀的裸 `x.y.z` 格式，消费项目按所处交付阶段接入：

- **开发期（同级源码依赖）**：将本仓库作为独立 Git 仓库检出在消费项目同级目录，在本地 Swift Package 中通过 `.package(path: ...)` 接入所需公开 product，同时在消费仓库提交包含 **40 位完整 commit SHA** 的版本锁文件并启用自动化阻断门禁；详细约束见 [`docs/engineering/sibling-source-dependency.md`](docs/engineering/sibling-source-dependency.md)。
- **发布期（已发布固定版本依赖）**：消费项目进入对外发布、TestFlight 外测或 App Store 提审上架阶段后，须移除本地路径覆写，改在 SwiftPM 依赖声明中锁定正式发布的精确裸 `x.y.z` Git 标签（首次正式对外发布基线为 `1.0.0`）。

```swift
// 开发期：同级源码接入（须配套提交 40 位完整 SHA 版本锁并接入自动化门禁）
.package(path: "../HiIOS")

// 发布期：锁定精确裸 x.y.z 标签
.package(url: "https://github.com/jashanyng/HiIOS.git", exact: "1.0.0")
```

## 日志默认脱敏策略

日志经由 `LogClient(sink: OSLogSink(subsystem:category:))` 或 `LogClient(routes:)` 搭配按输出端配置的 `LogRoute(sink:policy:)` 发出；每条路由在输出端收到 `LogOutputRecord` 前各自独立过滤与脱敏。默认策略执行脱敏（`LogRedactionPolicy.release` / `.diagnostic`）；`.unredacted` 会原样透传记录，仅适用于消费项目明确加以保护（如端侧加密或受控本地开发诊断）的输出端。`SwiftyBeaverLogSink(destinations:)` 将结构化 `LogOutputRecord` 作为各 destination 的 `context` 转发。消费项目各自维护认证策略、面向用户的文案与业务模型。

## 平台基线与本地验证

- **最低平台与语言模式**：`iOS 17+`、`Swift 6`（`swiftLanguageModes: [.v6]`）。
- **本地统一基础验证入口**：[`scripts/check.sh`](scripts/check.sh)（同时用于 GitHub Actions 质量 CI）。

```bash
# 本地统一基础验证（文档校验 + Python 单测 + SwiftPM manifest/SwiftLint + HiIOSBaseTests 宿主测试）
./scripts/check.sh

# 仅执行版本治理文档校验与 Python 单元测试（无需 macOS / Swift 工具链）
./scripts/check.sh --docs-only
```

- **常用分步与模拟器验证命令**：

```bash
# 校验版本号、变更日志与兼容性文档同步
python3 scripts/verify_version_docs.py

# 校验 SwiftPM manifest 定义
swift package dump-package >/dev/null

# 构建并运行无 UI 依赖的纯跨平台宿主测试目标（示例：HiIOSBaseTests）
swift build --only-use-versions-from-resolved-file --target HiIOSBaseTests
DYLD_FRAMEWORK_PATH="$(xcrun --show-sdk-platform-path)/Developer/Library/Frameworks" \
DYLD_LIBRARY_PATH="$(xcrun --show-sdk-platform-path)/Developer/usr/lib" \
"$(xcrun --find swift | sed 's|/bin/swift$|/libexec/swift/pm/swiftpm-testing-helper|')" \
  --test-bundle-path .build/debug/HiIOSBaseTests.xctest/Contents/MacOS/HiIOSBaseTests \
  --testing-library swift-testing

# 运行 iOS Simulator 全包测试
xcodebuild test -scheme HiIOS-Package -destination 'platform=iOS Simulator,id=<SIMULATOR_UUID>' \
  -parallel-testing-enabled NO -onlyUsePackageVersionsFromResolvedFile

# 对改动路径执行严格 SwiftLint 检查
swiftlint lint --strict Package.swift <修改的 Swift 文件路径>
```

## 文档入口

- 文档总索引：[`docs/README.md`](docs/README.md)
- 兼容性矩阵、演进契约与迁移指南：[`docs/compatibility.md`](docs/compatibility.md)
- 变更日志：[`CHANGELOG.md`](CHANGELOG.md)
- 当前版本号：[`VERSION`](VERSION)
- 智能体协作与硬边界规范：[`AGENTS.md`](AGENTS.md)
