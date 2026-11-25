# HiIOS 智能体协作说明

HiIOS（专名“HiIOS 效率库”，规则与文档叙述使用该专名，仓库名、product 与代码标识符保持原样）是独立于 AtlasHub 业务的 iOS 效率库，仅通过 Swift Package Manager（SwiftPM）单分发（决策依据见 [`docs/adr/0001-swiftpm-only-distribution.md`](docs/adr/0001-swiftpm-only-distribution.md)）。修改模块、公开 API、依赖或文档前，保留工作区无关改动；具体产品边界见 [`docs/architecture/products.md`](docs/architecture/products.md)。文档归属与入口见 [`docs/README.md`](docs/README.md)。

## 硬边界

- 六个基础家族为 Base、Core、Net、Nav、Store、Suite；GitHub Trending 是独立可选产品，`HiIOS` 是便捷入口。业务 Feature、认证策略、用户文案和品牌不进入本库。
- `Package.swift`（配合 `Package.resolved`）是 SwiftPM product、target、资源与依赖图的唯一事实源，不提供 CocoaPods 分发或 `.podspec` 定义；直接第三方依赖在 `Package.swift` 中锁定精确稳定版本，已发布 Git 标签不可覆盖。
- 演进期兼容性与目录结构可变性遵循下方“演进生命周期”与“版本与标签治理”：当前处于制作期，不留废弃别名、兼容分支或迁移层，消费项目同批更新并验证。
- 修改公开接口、模块或依赖时，验证受影响的 SwiftPM product、target、资源及消费者；验证必须覆盖 SwiftPM 宿主测试、iOS Simulator 包测试与 `SwiftLint` 检查。
- 新增或升级第三方依赖时，读取 [`docs/engineering/dependencies.md`](docs/engineering/dependencies.md)。
- 日志默认经脱敏策略处理；是否脱敏由消费项目通过 `LogRedactionPolicy` 等参数显式选择并自负其责，本库不内置渠道、环境或加密策略。厂商 SDK 不进入默认产品，未经实际可用的 SwiftPM 分发验证不预建空 target。

## 演进生命周期

- **当前所处阶段**：**制作期**（当前版本基线 `0.0.1`）。
- **三阶段定义与边界**：
  1. **制作期（当前阶段）**：允许为产品化定型调整与重塑顶层家族、子模块划分及整体组织结构；不保留代码与公开接口向后兼容，不留废弃别名、兼容分支或迁移层；处于开发期的消费项目随 HiIOS 效率库改动同批更新并验证。智能体在消费项目开发时识别出剥离业务语义与品牌后可供多数同平台项目复用的通用能力或组件，必须主动沉淀回 HiIOS 效率库。
  2. **改进完善期**：严格保持既定的顶层家族、子模块划分与组织方式不变（若确需突破既有边界，必须先获维护者明确批准），仅在既有职责边界内扩充、改进和完善能力；在既有边界内调整时仍无需保留代码向后兼容，消费项目在开发期同步更新调用。
  3. **维护期**：严格冻结模块组织结构并严格遵守代码与公开接口向后兼容，日常聚焦平台新特性适配、安全升级与修 bug；当确有新增功能诉求时，智能体必须先输出包含复用广度、职责契合度、兼容性与维护成本的可行性与必要性验证评估报告，并获维护者明确同意后方可实施。
- **阶段切换权归属**：演进阶段的切换权完全归属维护者显式决定，严禁智能体在任何任务现场自行推定或切换阶段（智能体仅可在观察到成熟信号时给出提醒建议，获维护者明确授权后方可修改本声明）。
- **与消费项目两阶段门禁正交**：HiIOS 效率库自身的三阶段演进生命周期（制作期 / 改进完善期 / 维护期）与消费项目的两阶段依赖门禁（开发期同级源码 40 位 SHA 版本锁 / 发布期已发布固定版本依赖）正交并存、互不替代。

## 版本与标签治理

- **裸 `x.y.z` 格式**：所有版本号定义、锁引用与 Git 标签一律采用不带 `v` 前缀的裸 `x.y.z` 三段非负整数格式（如 `0.0.1`、`1.0.0`），严禁使用 `v` 前缀标签。
- **制作期基线与打标约定**：制作期版本基线定为 `0.0.1` 且仅递增 `z`；制作期日常源码提交不预先打 Git 标签，也不向外部制品源公开发布。
- **`1.0.0` 首发基准**：首次正式对外发布或首个消费项目提审上架锁定正式制品时，版本定为 `1.0.0` 并创建裸标签 `1.0.0`。
- **`1.0.0` 后协同演进**：`x` 代表重大架构、组织结构或品牌代际；`y` 代表开发期项目周期批次（某消费项目提审锁定当前 `x.y.z` 后，其余在研项目切入 `x.(y+1).0` 继续源码演进，原 `x.y.*` 仅用于已上架项目紧急热修并递增 `z`）；`z` 代表同批次内的功能与修复递增。
- **智能体仅可递增 `z`**：智能体在任何版本更新操作中仅被允许递增 `z`；任何对 `x` 或 `y` 的修改（含切入 `1.0.0`、切入 `x.(y+1).0` 或基线调整）必须经维护者明确同意。

## 消费项目的同级源码依赖

消费项目选择 SwiftPM local package 的同级源码检出时，必须遵守 [`docs/engineering/sibling-source-dependency.md`](docs/engineering/sibling-source-dependency.md) 的版本锁和 Git 对齐门禁，并将其接入实际 Verification、CI 与 Archive/Release 入口。本库不规定消费项目的锁文件名、scheme 或签名配置。

GitHub Trending 的独立限制见 [`docs/engineering/gh-trending.md`](docs/engineering/gh-trending.md)。

## Agent skills

### Issue tracker

本仓库的 Issue 与规格说明使用 GitHub Issues（`jashanyng/HiIOS`，通过 `gh` CLI 操作）。详见 [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md)。

### Triage labels

使用五个默认 Triage 角色标签（`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`）。详见 [`docs/agents/triage-labels.md`](docs/agents/triage-labels.md)。

### Domain docs

采用单上下文（single-context）布局：根目录 `GLOSSARY.md` 与 `docs/adr/`。详见 [`docs/agents/domain.md`](docs/agents/domain.md)。
