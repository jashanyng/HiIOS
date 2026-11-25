# HiIOS 产品与分发边界

## 产品边界

HiIOS 效率库当前处于**制作期**，版本基线定为 `0.0.1`（制作期日常源码提交不预先创建 Git 标签），且仅通过 **Swift Package Manager（SwiftPM）** 单一方式分发（详见 [`../adr/0001-swiftpm-only-distribution.md`](../adr/0001-swiftpm-only-distribution.md)）。所有版本号与 Git 标签一律采用不带 `v` 前缀的裸 `x.y.z` 格式。当前最低平台为 iOS 17，语言模式为 Swift 6；平台基线变更需单独验证。

| 家族 | 模块与职责 | 内部依赖 |
| --- | --- | --- |
| Base | `HiIOSBase`：纯 Swift 模型、错误、日志、统计和社会化分享契约 | 无 |
| Core | `HiIOSCore`：颜色、字体、资源、序列化、文件和设备工具 | Base |
| Net | `HiIOSNetCore` 与 RxSwift、Combine adapter：HTTP 契约和 Moya transport | NetCore → Core；adapter → NetCore |
| Nav | `HiIOSNavCore` 与 RxSwift、Combine adapter：typed route、URL 路由表与安全校验、强类型路由栈和通用展示状态 | NavCore → Core；adapter → NavCore |
| Store | `HiIOSStoreCore` 与 Keychain、Defaults、File adapter：字节存储与安全值契约 | StoreCore → Base；adapter → StoreCore（其中 `HiIOSStoreKeychain` 同时依赖 `HiIOSBase`） |
| Suite | `HiIOSSuiteCore` 与 OSLog、SwiftyBeaver adapter：通用 SwiftUI 视图与日志输出 | SuiteCore → Core；日志 adapter → Base |

`HiIOSGHTrending` 是依赖 `HiIOSNetCore` 的独立可选产品，不属于六个基础家族。`HiIOS` 便捷入口组合 Core、NetCombine、NavCombine、Store、SuiteCore 与 SFSafeSymbols；不默认链接 RxSwift、Trending 或厂商 SDK。SwiftPM 仍可能解析 manifest 中其他可选 target 的外部依赖。源码显式导入所选模块，不通过 `@_exported import` 隐式重导出。

## SwiftPM 单分发规则

- 根 [`Package.swift`](../../Package.swift)（及同步更新的 [`Package.resolved`](../../Package.resolved)）是源码、resources、平台、product 与 target 图的唯一事实源。真实子模块使用对应的 SwiftPM product 与 Swift target/module；聚合 product 只提供安装选择，不替代显式模块导入。
- 直接第三方依赖在 `Package.swift` 中使用精确稳定版本锁定（`exact:`），并与 `Package.resolved` 保持同步；已发布的裸 `x.y.z` Git 标签不可覆盖。应用通过自身的依赖解析锁与效率库版本锁固定完整依赖图。
- Base 保持无平台、UI 和 SwifterSwift 依赖；当前 SwifterSwift 的 SwiftPM product 只由 Core 使用。DeviceKit 属于 Core，SwiftyBeaver 属于可选 Suite adapter。缺少稳定可验证 SwiftPM 源的依赖不进入默认产品。
- 友盟、EMAS 等厂商闭源 SDK 或 adapter 只有在具备稳定可验证的 SwiftPM 来源时才实现，不预建空 target，也不由默认入口初始化。

每次变更分别验证受影响的 SwiftPM product 与 target；隔离验证 Core、RxSwift、Combine 与默认入口，检查 Swift module 名、公开接口、资源定位、依赖环、取消与错误语义、隐私脱敏，并覆盖 **SwiftPM 宿主测试**与 **iOS Simulator 包测试**。

## SuiteCore 页面外观组件

`HiIOSSuiteCore` 提供与业务、品牌无关的页面外观约定，消费项目在所有页面统一使用，不在页面中各自组合系统修饰符：

- **传统导航栏**：`suiteNavigationTitle(_:)` 设置标准高度、标题居中的导航栏，不使用大标题；标题由工具栏自定义内容承担时用 `suiteNavigationBar()`。
- **页面画布与内容表面**：`Color.suitePageCanvas`（浅灰，深色下纯黑）与 `Color.suiteContentSurface`（白色，深色下深灰）始终有色差。整页用 `suitePageCanvas()`；平铺列表用 `suiteListCanvas()` 并为内容行加 `suiteListRowSurface()`；阅读页的正文、评论等内容块用 `suiteContentBlock(padding:)`，块间露出画布。
- **分页尾**：`LoadMoreFooter` 按 `LoadMoreState`（加载中、加载更多、已全部加载、失败）显示列表底部状态，文案由 `LoadMoreLabels` 提供；在 `List` 中自身无分隔线、透明行背景。`LoadMoreLabels.finished` 为空时全部加载后不显示结尾文字。
- **列表分组与行**：`SuiteListSection`、`SuiteListRow`、`SuiteListButtonRow` 与 `SuiteListStyle`；单行最小高度为 `SuiteListRowMetrics.minimumHeight`（52pt，与 iOS 26 系统列表一致）。
- **单选行与分段行**：`SuiteSelectableListRow` 与 `SuiteListRow` 同外观，选中项尾部显示 tint 色对勾；`SuiteListSegmentedRow` 左侧标题、右侧固定宽度（默认 `SuiteListSegmentedRowMetrics.selectorWidth`，148pt）的系统分段选择器，用于“搜索类型”这类二三选一的设置项。
- **搜索框与可搜索单选页**：`SuiteSearchField` 是常驻显示的胶囊搜索框，高度 `SuiteSearchFieldMetrics.height`（48pt，比系统搜索栏高约 1/3），不依赖系统 `.searchable`，首次进入即显示；`SuiteSearchableSelectionList` 在其下方放惰性加载的通栏单选列表，搜索词由组件自己保存，按 `SuiteSelectionOption` 的标题与关键字过滤，可选“不限”项只在未输入时显示，无匹配时显示空态。
- **工具栏**：页面用 `suiteToolbar { … }` 代替 `.toolbar { … }`，其中每一项只显示图标或文字本身，不带 iOS 26 起的玻璃背景。版本判断放在视图层：`ToolbarContentBuilder` 中的 `if #available` 会引用位于 SwiftUICore 的 `buildLimitedAvailability`，动态库产品无法链接。
- **工具栏按钮外观**：`suiteToolbarItemStyle()`（`SuiteToolbarButtonStyle`）让导航栏中的按钮、菜单与分享入口使用主文字色，与返回图标一致；按下变淡、禁用置灰。
- **导航栏按钮组**：`SuiteToolbarTrailingGroup` 把导航栏右侧多个按钮放进同一个工具栏项，图标间距固定为 `SuiteToolbarMetrics.itemSpacing`（20pt），按书写顺序从左到右排列。
- **主操作按钮**：`.buttonStyle(.suitePrimary)` / `.suitePrimary(shape:minHeight:)`（`SuitePrimaryButtonStyle`）以当前 `tint` 为实心底、白色文字与加载动画，禁用时系统灰底；外形分圆角矩形与胶囊，代替 `.borderedProminent`。
- **页面首屏加载**：`SuitePageLoadingView` 只显示放大一档的加载动画，不显示文字；动画由 `SuiteActivityIndicator` 绘制，颜色取当前 `tint`。说明文字通过 `accessibilityLabel` 交给 VoiceOver。
- **横向分页**：`SuitePager` 是可左右滑动翻页的内容区，使用 `SuitePagingScrollTargetBehavior`：松手时拖动超过页宽的 `SuitePagerMetrics.defaultSwipeThreshold`（20%）或快速甩动即翻到相邻页，一次最多一页，比系统 `TabView(.page)` 需要拖过半页更容易切换；各页保留不重建。
- **翻页标签**：`SuitePagerTabs` 与 `SuitePagerTab` 提供顶部可横向滚动的等宽标签（选中项 tint 色、与文字同宽的 3pt 指示条），内容区为 `SuitePager`。
- **锚定气泡**：`suiteAnchoredTooltip(text:anchor:reservedTop:autoDismissAfter:onDismiss:)` 在视图上显示指向锚点的反色气泡，上方空间不足时显示在下方；默认 5 秒后 0.3 秒渐隐。位置计算 `SuiteAnchoredTooltipLayout` 独立可测。
- **传统标签栏**：`SuiteTabBar` 与 `SuiteTabBarItem` 绘制与屏幕同宽的通栏标签栏（内容高 `SuiteTabBar.height`，背景延伸到底部安全区；`itemOffset` 可让图标与文字整体下移）。iOS 26 起系统标签栏只有悬浮玻璃样式，需要通栏样式的项目隐藏系统标签栏，把它以 `safeAreaInset(edge: .bottom, spacing: 0)` 挂在各 Tab 导航栈的根页上，push 时随根页滑出。

## NavCore 导航基础

`HiIOSNavCore` 只提供与 UI 框架和架构无关的导航基础，UIKit、SwiftUI 与 TCA 项目都可以使用；不依赖 swift-navigation、URLNavigator 等第三方导航库，状态驱动的页面呈现由消费项目自行选择实现。

- **URL 路由表**：`URLRouter<Context, Route>` 先用 `SanitizedURL` 做结构安全检查（拒绝 user-info、显式或空端口、编码过的主机名、空段、`.`/`..`，以及解码后含 `/`、`\`、`%`、`?`、`#` 或控制字符的路径段），再按 `URLRouteRule` 的顺序匹配 `URLRouteTemplate`（scheme、精确或参数化主机、`/{owner}/{repo}` 形式的路径模板、是否允许 query 与 fragment）。每条规则声明可达的入口上下文（由项目定义，如外部入口与 App 内导航），`resolve` 做保留名、数字范围、query 等业务校验，返回 nil 即拒绝。
- **路由栈**：`NavigationRouteStack<Route>` 是可绑定到 `NavigationStack(path:)` 的强类型路由序列，每次写入都返回出栈的路由，供调用方释放页面独占的资源。
- **展示状态**：`NavigationAction`、`ToastState`、`NavigationAlertState`、`NavigationDialogState`、`NavigationPresentationAction` 与 `PopupState`；命名带 `Navigation` 前缀，避免与 TCA、swift-navigation 的 `AlertState`、`PresentationAction` 同时导入时冲突。
- `HiIOSNavRxSwift` 中基于 URLNavigator 的 `RxURLNavigator` 只适用于 UIKit；SwiftUI 项目使用 `URLRouter` 加自身的状态驱动导航。

