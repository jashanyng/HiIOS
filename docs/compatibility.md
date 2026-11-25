# HiIOS 兼容性与演进契约

本文档说明 HiIOS 效率库的平台与第三方依赖兼容基线、三阶段演进与裸 `x.y.z` 版本契约，以及消费项目的接入升级与迁移路径。具体产品家族划分见 [`architecture/products.md`](architecture/products.md)。

## 环境与依赖兼容矩阵

### 平台与工具链基线

| 维度 | 当前基线 | 说明 |
| --- | --- | --- |
| 分发方式 | 纯 SwiftPM 单分发 | 根 [`Package.swift`](../Package.swift) 与 [`Package.resolved`](../Package.resolved) 为唯一事实源，不提供 CocoaPods `.podspec` |
| Swift Tools 版本 | `6.0` | `// swift-tools-version: 6.0` |
| 语言模式 | `Swift 6` | `swiftLanguageModes: [.v6]` |
| 最低支持平台 | `iOS 17+` | `platforms: [.iOS(.v17)]` |

### 直接第三方依赖精确版本（`Package.swift`）

所有直接第三方依赖在 [`Package.swift`](../Package.swift) 中使用 `exact:` 锁定精确稳定版本，并与 [`Package.resolved`](../Package.resolved) 同步提交：

| 依赖包 | 锁定版本（`exact:`） | 所属 Target / 产品范围 | 说明 |
| --- | --- | --- | --- |
| `SwifterSwift` | `8.0.0` | `HiIOSCore` | `HiIOSBase` 不引入 `SwifterSwift` |
| `DeviceKit` | `5.10.0` | `HiIOSCore` | 仅用于设备描述，不作为设备身份标识 |
| `Moya` | `15.0.0` | `HiIOSNetCore`、`HiIOSNetRxSwift`、`HiIOSNetCombine` | 含 `Moya`、`RxMoya`、`CombineMoya` |
| `Alamofire` | `5.12.2` | `HiIOSNetCore` | 作为底层传输实现，类型不穿透 HiIOS 自有契约 |
| `RxSwift` | `6.9.0` | `HiIOSNetRxSwift`、`HiIOSNavRxSwift` | 仅在使用 RxSwift 适配器时引入 |
| `SwiftyBeaver` | `2.1.1` | `HiIOSSuiteLogSwiftyBeaver` | 可选日志输出适配器 |
| `SFSafeSymbols` | `7.0.0` | `HiIOS`（便捷入口） | 仅由 `HiIOS` 便捷入口聚合 |
| `SwiftSoup` | `2.11.3` | `HiIOSGHTrending` | 仅用于独立可选产品 `HiIOSGHTrending` |

> [!NOTE]
> [`Package.resolved`](../Package.resolved) 同时锁定上述依赖带来的传递依赖解析结果（当前包含 `LRUCache` `1.3.0`、`ReactiveSwift` `6.7.0`、`swift-atomics` `1.3.1`）。`URLNavigator` 已按 MIT 协议内置源码于 `HiIOSNavRxSwift` 内部，不再作为外部 SwiftPM 依赖。

## 演进阶段与版本兼容契约

### 裸 `x.y.z` 版本与标签格式

- HiIOS 所有版本号文件（根目录 [`VERSION`](../VERSION)）、版本引用与 Git 标签一律采用**无 `v` 前缀的裸 `x.y.z` 三段非负整数格式**（如 `0.0.1`、`1.0.0`），严禁使用 `v` 前缀或前导零。
- 变更日志唯一事实源为根目录 [`CHANGELOG.md`](../CHANGELOG.md)，须保持 [`VERSION`](../VERSION) 与 [`CHANGELOG.md`](../CHANGELOG.md) 同步，并通过 `python3 scripts/verify_version_docs.py` 校验。

### 当前所处阶段与三阶段契约

HiIOS 当前处于**制作期**，未发布基线版本为 **`0.0.1`**（制作期日常源码提交不预先创建 Git 标签，也不向外部制品源公开发布）。

| 演进阶段 | 结构可变性 | 向后兼容性 | 消费项目联动与准入边界 |
| --- | --- | --- | --- |
| **制作期（当前阶段，`0.0.x`）** | 允许调整顶层家族、子模块划分与组织结构 | **不保留**废弃别名、兼容垫片或迁移层 | 处于开发期的消费项目随效率库改动同批更新并验证 |
| **改进完善期** | 顶层家族与子模块划分**必须**冻结不变（突破需维护者批准） | 既有职责边界内扩充、改进时仍无需保留向后兼容 | 围绕既定结构补齐通用能力并同步更新开发期消费端 |
| **维护期** | 模块组织结构严格冻结 | **必须**严格遵守公开 API 与模块向后兼容 | 聚焦平台适配、安全升级与缺陷修复；新增功能须先提交可行性与必要性评估报告并获维护者批准 |

> [!IMPORTANT]
> 演进阶段切换完全由维护者评估拍板；智能体在日常版本递增中**仅允许递增 `z`**，任何修改 `x` 或 `y`（如切入 `1.0.0` 或 `x.(y+1).0`）必须经维护者明确同意并在 `scripts/bump_version.py` 中显式传入 `--allow-xy-bump`。

### `1.0.0` 后 `x.y.z` 批次与热修语义

1. **首次正式发布（`1.0.0`）**：当首个消费项目进入对外发布、TestFlight 外测或 App Store 提审上架阶段并需锁定正式制品时，HiIOS 切入 `1.0.0` 并创建不可覆盖的裸 Git 标签 `1.0.0`。
2. **主版本 `x`**：代表重大架构重构、组织结构代际调整或跨代不兼容变更。
3. **项目周期批次 `y`**：当同一批次内某个消费项目进入提审上架阶段时，将当前 `x.y.z` 正式发布并打裸标签供该项目锁定；其余仍在同级源码开发的消费项目立即切入 `x.(y+1).0` 继续源码演进，原 `x.y.*` 仅保留作已上架项目的独立紧急热修通道。
4. **修订号 `z`**：同一 `x.y` 批次内的常规能力扩充、依赖安全更新与缺陷修复（或已上架批次的热修）递增 `z`。

## 升级与迁移指南

### 1. 开发期同级源码接入升级（`.package(path: "../HiIOS")` + 40 位 SHA 锁）

开发期消费项目以本地同级检出接入 HiIOS（详细硬门禁见 [`engineering/sibling-source-dependency.md`](engineering/sibling-source-dependency.md)）：

```swift
dependencies: [
    .package(path: "../HiIOS")
]
```

升级到新版 HiIOS 提交的标准步骤：

1. 在 `HiIOS` 仓库完成修改并推送到可信远端跟踪分支，确保目标提交的 **40 位完整 commit SHA** 远端可达且工作区干净。
2. 在本地同级 `HiIOS/` 检出该目标 SHA，更新消费项目中的 40 位 SHA 版本锁文件。
3. 在 `HiIOS` 运行本地验证门禁（`verify_version_docs.py`、SwiftPM 宿主测试、iOS Simulator 包测试与 `SwiftLint`），并在消费项目运行完整验证门禁，确认消费端与效率库改动同批适配通过。
4. 提交并推送消费项目更新后的版本锁文件。

### 2. 切换为发布期已发布固定版本（`.package(url: ..., exact: "1.0.0")`）

当消费项目进入对外发布、TestFlight 外测或 App Store 提审上架阶段时，必须移除同级源码路径覆写，改为锁定精确裸 `x.y.z` Git 标签：

```swift
dependencies: [
    .package(url: "https://github.com/jashanyng/HiIOS.git", exact: "1.0.0")
]
```

切换检查清单：

1. 确认目标版本已在 `HiIOS` 远端存在对应的不可变裸 `x.y.z` 标签，且根 [`VERSION`](../VERSION) 与 [`CHANGELOG.md`](../CHANGELOG.md) 已完成归档。
2. 移除消费项目 `Package.swift` 或 Xcode 项目中的 `.package(path: "../HiIOS")` 本地路径依赖覆写，改为 `exact: "<x.y.z>"` 并重新生成消费项目 `Package.resolved`。
3. 确认消费项目的 CI、Archive 与 Release 入口门禁在检测到残留本地路径覆写时能够直接非零退出阻断。

### 3. 跨版本破坏性变更记录

当前仓库处于制作期初始基线 `0.0.1`，尚无已对外发布的跨版本破坏性变更历史。自 `1.0.0` 正式发布起，凡涉及公开模块划分、最低平台/Swift 版本基线或公开 API 的破坏性调整，均须在本节按版本倒序记录迁移对照与替换步骤。
