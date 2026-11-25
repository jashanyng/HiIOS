# 0001. HiIOS 效率库采用纯 SwiftPM 单分发

- 状态：采纳
- 日期：2026-11-25
- 决策人：Jashan Yang

## 背景

HiIOS 效率库此前同时维护 Swift Package Manager（SwiftPM）与 CocoaPods 两套分发定义：除根目录 `Package.swift` 外，仓库还维护了 21 个独立与聚合 `.podspec` 文件，并在协作规则与工程文档中要求同一公开版本在两个包管理器下保持一致的模块划分、依赖版本与双分发校验，同时文档中遗留了旧仓库时期的 `3.0.0`、`4.x` 与 CocoaPods Trunk 发布线表述。

在实际演进与消费端接入过程中，继续保留双分发不仅缺乏实际收益，还引入了不必要的维护负担：

1. **消费端已无需通过 CocoaPods 接入 `HiIOS`**：消费项目已全面转向以 SwiftPM 管理依赖；此前 `AtlasHub_iOS` 保留 CocoaPods 工作区仅因需接入闭源统计 SDK（友盟 `UMCommon` 与 `UMDevice`）；消费端（如 `AtlasHub_iOS`）同步将闭源统计框架收敛至消费仓内独立本地 SwiftPM `binaryTarget` 封装并移除 CocoaPods，无需 HiIOS 效率库保留 CocoaPods 通道。
2. **双渠道同步与校验成本高**：每次调整模块边界、资源或依赖版本时，均需同步维护 `Package.swift` 与全部 `.podspec` 并执行双分发检查，增加了工作量与配置漂移风险。
3. **历史版本号表述干扰当前治理秩序**：尚处于开发沉淀阶段的仓库沿用 `3.0.0` / `4.x` 历史编号，与当前制作期定位及跨仓库统一的裸 `x.y.z`（制作期 `0.0.1` 起步）版本治理基线相冲突。

## 选项

1. **维持 SwiftPM 与 CocoaPods 双分发**：
   - 优点：保留对纯 CocoaPods 消费工程的直接接入兼容。
   - 缺点：持续承担 21 个 `.podspec`、CocoaPods 本地校验与双渠道版本一致性维护负担，与消费端收敛至单一 SwiftPM 依赖锁的方向相悖。
2. **收敛为纯 SwiftPM 单分发**：
   - 优点：彻底消除 `.podspec` 与双分发校验成本，以根目录 `Package.swift`（配合 `Package.resolved`）作为唯一产品、target、资源与依赖事实源；直接对接消费端单一工程、单一解析锁及同级源码 40 位 commit SHA 门禁；同步清理旧版本号表述并落地制作期 `0.0.1` 基线。
   - 缺点：不再直接向纯 CocoaPods 工程提供 `pod` 接入；对于缺乏稳定可验证 SwiftPM 分发源的第三方闭源厂商 SDK，无法直接作为 `HiIOS` 默认产品分发，需由消费端按规范各自封装或兜底处理。

## 决策

采纳**选项 2**：HiIOS 效率库收敛为仅通过 **SwiftPM 单分发**，彻底移除 CocoaPods 分发支持。本决策与 `../tech-specs/ios/dependencies-and-hiios.md` 中的规范定义保持一致，不构成对通用规范的偏离。具体边界如下：

1. **彻底移除 CocoaPods 分发定义**：删除全部 21 个 `.podspec` 文件，清理规则、工程文档、忽略规则及源码注释中的 Pod/CocoaPods 与双分发校验表述，不再维护 CocoaPods 分发线与 CocoaPods Trunk 发布流程。
2. **以根 `Package.swift`（及 `Package.resolved`）为唯一事实源**：根目录 `Package.swift` 是 `HiIOS` 全部公开 SwiftPM product、target、资源定义与直接第三方依赖精确锁定版本的唯一事实源，与 `Package.resolved` 保持同步；已发布的 Git 标签不可覆盖。
3. **两阶段接入方式**：
   - **开发期**：消费项目通过同级源码检出与 `.package(path: ...)` 接入公开 SwiftPM product，并严格提交 40 位完整 Git commit SHA 版本锁与自动化阻断门禁（覆盖 Verification、CI 及 Archive/Export/Release 入口，详见 [`../engineering/sibling-source-dependency.md`](../engineering/sibling-source-dependency.md)）。
   - **发布期（对外发布、提审或上架）**：消费项目必须移除同级源码覆写，切换为引用已发布的无 `v` 前缀裸 `x.y.z` Git 标签（精确固定版本号）。
4. **厂商闭源 SDK 边界**：友盟、EMAS 等厂商闭源 SDK 不进入 `HiIOS` 默认产品；在缺乏实际可用的稳定 SwiftPM 分发源并完成验证前，不在 `HiIOS` 内预建空 target。消费项目若确需接入闭源厂商 SDK，应按通用规范在消费项目内部独立封装（如仓内独立本地 SwiftPM `binaryTarget`）并严格隔离于 `Verification` 产物之外。
5. **清理历史版本号并按制作期 `0.0.1` 基线治理**：彻底清理旧 `3.0.0`、`4.x` 表述；当前处于制作期，版本基线定为 `0.0.1`，制作期日常源码提交不预先创建 Git 标签，后续统一遵循无 `v` 前缀裸 `x.y.z` 版本治理规则（首次正式对外发布或首个消费项目提审上架锁定正式制品时定为 `1.0.0`）。

## 后果

- **正面影响**：
  - 彻底消除 `.podspec` 维护与双分发一致性校验负担，变更验证聚焦于受影响的 SwiftPM product、target、资源、SwiftPM 宿主测试、iOS Simulator 包测试与 `SwiftLint`。
  - 消费项目（如 `AtlasHub_iOS`）得以移除 CocoaPods 工作区、独立锁文件与桥接构建配置，回归单一工程与单一 SwiftPM 解析锁。
  - 清理 `3.0.0` / `4.x` 历史遗留编号，建立与 `HiAndroid`、`HiWeb`、`HiFlutter` 统一的制作期 `0.0.1` 裸版本治理基线。
- **引入的代价与约束**：
  - `HiIOS` 不再支持以 CocoaPods `pod` 方式接入。
  - 未来若确需在 `HiIOS` 中为某项能力引入第三方闭源 SDK，前提是该 SDK 具备实际可用且可验证的 SwiftPM 分发源并通过许可、安全与隐私清单审查。
- **同步动作**：
  - 移除 21 个 `.podspec`、清理 `.gitignore` 中 CocoaPods 规则与 `Sources/HiIOSCore/HiIOSResourceReader.swift` 中的 CocoaPods 注释表述；
  - 更新根目录 [`AGENTS.md`](../../AGENTS.md)、[`README.md`](../../README.md)、[`docs/README.md`](../README.md)、[`docs/architecture/products.md`](../architecture/products.md)、[`docs/engineering/dependencies.md`](../engineering/dependencies.md)、[`docs/engineering/sibling-source-dependency.md`](../engineering/sibling-source-dependency.md) 与 [`docs/engineering/gh-trending.md`](../engineering/gh-trending.md)；
  - 同步更新下游消费仓库同级源码 40 位 SHA 版本锁及 `AtlasHub` 总入口跨端公约。
- **复核条件**：仅当未来需要向外部非 SwiftPM 消费方公开发布且存在不可替代的 CocoaPods 刚需时，方可通过新建后续 ADR 重新评估，严禁绕过决策私自恢复 `.podspec`。
