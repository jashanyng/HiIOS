# HiIOS 智能体协作说明

HiIOS（专名“HiIOS 效率库”，规则与文档叙述使用该专名，仓库名、product 与代码标识符保持原样）是独立于 AtlasHub 业务的 iOS 效率库，仅通过 Swift Package Manager（SwiftPM）单分发（决策依据见 [`docs/adr/0001-swiftpm-only-distribution.md`](docs/adr/0001-swiftpm-only-distribution.md)）。修改模块、公开 API、依赖或文档前，保留工作区无关改动；具体产品边界见 [`docs/architecture/products.md`](docs/architecture/products.md)。文档归属与入口见 [`docs/README.md`](docs/README.md)。

## 硬边界

- 六个基础家族为 Base、Core、Net、Nav、Store、Suite；GitHub Trending 是独立可选产品，`HiIOS` 是便捷入口。业务 Feature、认证策略、用户文案和品牌不进入本库。
- `Package.swift`（配合 `Package.resolved`）是 SwiftPM product、target、资源与依赖图的唯一事实源，不提供 CocoaPods 分发或 `.podspec` 定义；直接第三方依赖在 `Package.swift` 中锁定精确稳定版本，已发布 Git 标签不可覆盖。
- 演进期兼容性与目录结构可变性遵循下方“演进阶段与版本治理”：当前处于制作期，不留废弃别名、兼容分支或迁移层，消费项目同批更新并验证。
- 修改公开接口、模块或依赖时，验证受影响的 SwiftPM product、target、资源及消费者；验证必须覆盖 SwiftPM 宿主测试、iOS Simulator 包测试、`SwiftLint` 检查以及 `python3 scripts/verify_version_docs.py`。日常本地统一基础验证入口为 `./scripts/check.sh`（仅校验治理文档与 Python 单测可用 `./scripts/check.sh --docs-only`）。
- 新增或升级第三方依赖时，读取 [`docs/engineering/dependencies.md`](docs/engineering/dependencies.md)。
- 日志默认经脱敏策略处理；是否脱敏由消费项目通过 `LogRedactionPolicy` 等参数显式选择并自负其责，本库不内置渠道、环境或加密策略。厂商 SDK 不进入默认产品，未经实际可用的 SwiftPM 分发验证不预建空 target。

## 演进阶段与版本治理

- **当前阶段与基线**：当前处于**制作期**，未发布版本基线由根目录 [`VERSION`](VERSION) 锁定为无 `v` 前缀裸 `x.y.z` 格式 `0.0.1`（日常源码提交不预先打 Git 标签，也不向外部制品源公开发布）。
- **变更权限与脚本硬门禁**：AI 仅被允许递增 `z`；切换演进阶段或修改 `x`/`y`（含切入 `1.0.0`、`x.(y+1).0` 或调整基线）须经维护者明确同意（严禁任务现场自行推定或修改）。递增版本号必须经由 `python3 scripts/bump_version.py <version>` 执行（默认拒绝 `x`/`y` 变更，仅维护者明确授权时方可使用 `--allow-xy-bump`），由脚本同步更新 `VERSION` 并将 [`CHANGELOG.md`](CHANGELOG.md) 的 `## [Unreleased]` 自动归档到对应版本节。
- **治理文档同步硬门禁**：
  - 修改公开 API、模块划分或依赖配置时，必须同步记录至根 [`CHANGELOG.md`](CHANGELOG.md) 的 `## [Unreleased]` 节（版本更新说明唯一事实源）。
  - 变更平台/Swift 工具链/第三方依赖精确版本基线、消费接入方式、演进阶段或引入破坏性变更时，必须同步更新 [`docs/compatibility.md`](docs/compatibility.md) 与根 [`README.md`](README.md)。
  - 所有改动须通过 `./scripts/check.sh --docs-only`（或直接运行 `python3 scripts/verify_version_docs.py` 与 `python3 -m unittest discover -s scripts -p 'test_*.py'`）校验 `VERSION`、`CHANGELOG.md` 与 `docs/compatibility.md` 的完整性与同步状态；涉及代码或 `Package.swift` 改动时运行全量 `./scripts/check.sh`。
- **按需查阅完整治理规则**：调整顶层家族/子模块结构、跨项目沉淀通用能力、评估维护期新增功能、切入 `1.0.0` 首发或切换项目版本批次前，读取 [`../tech-specs/common/adoption.md#4-效率库准入规则与两阶段门禁`](../tech-specs/common/adoption.md#4-效率库准入规则与两阶段门禁)（本机无同级目录时回退读取 GitHub `jashanyng/tech-specs` 同路径）。
- **与消费端门禁正交**：HiIOS 效率库自身的三阶段演进与版本治理独立于消费项目两阶段依赖门禁（开发期 40 位 SHA 同级源码锁 / 发布期已发布固定版本），二者正交并存、互不替代。

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
