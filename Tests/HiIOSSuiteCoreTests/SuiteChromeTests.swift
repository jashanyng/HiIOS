#if canImport(UIKit)
import HiIOSSuiteCore
import Observation
import SwiftUI
import Testing
import UIKit

@Test @MainActor
func suiteTabBarRendersSelectedAndUnselectedItemsInBothAppearances() {
    let items = [
        SuiteTabBarItem(tag: 0, title: "Home", systemImage: "house", accessibilityIdentifier: "tab.home"),
        SuiteTabBarItem(tag: 1, title: "Search", systemImage: "magnifyingglass"),
        SuiteTabBarItem(tag: 2, title: "A very long tab title", systemImage: "person.crop.circle")
    ]
    for appearance in [ColorScheme.light, .dark] {
        let renderer = ImageRenderer(
            content: SuiteTabBar(items: items, selection: 1) { _ in }
                .frame(width: 320)
                .preferredColorScheme(appearance)
        )
        #expect(renderer.uiImage != nil)
    }
    #expect(SuiteTabBar<Int>.height == 49)
}

@Test @MainActor
func suitePageLoadingViewRendersWithAndWithoutAccessibilityLabel() {
    for label in [nil, "Loading repository"] as [String?] {
        let renderer = ImageRenderer(
            content: SuitePageLoadingView(accessibilityLabel: label).frame(width: 200, height: 200)
        )
        #expect(renderer.uiImage != nil)
    }
}

@Test @MainActor
func suiteToolbarRendersPlainItemsInsideNavigationStack() {
    let renderer = ImageRenderer(
        content: NavigationStack {
            Text("Body")
                .suiteToolbar {
                    ToolbarItem(placement: .topBarTrailing) { Button("Done") {} }
                    ToolbarItem(placement: .topBarLeading) { Image(systemName: "chevron.backward") }
                }
        }
        .frame(width: 320, height: 200)
    )
    #expect(renderer.uiImage != nil)
}

@Test @MainActor
func suiteTabBarAcceptsItemOffset() {
    let items = [SuiteTabBarItem(tag: 0, title: "Home", systemImage: "house")]
    let renderer = ImageRenderer(
        content: SuiteTabBar(items: items, selection: 0, itemOffset: 12) { _ in }.frame(width: 320)
    )
    #expect(renderer.uiImage != nil)
}

@Test @MainActor
func suiteToolbarItemStyleRendersEnabledAndDisabledButtons() {
    for disabled in [false, true] {
        let renderer = ImageRenderer(
            content: Button {} label: { Image(systemName: "square.and.arrow.up") }
                .suiteToolbarItemStyle()
                .disabled(disabled)
                .frame(width: 44, height: 44)
        )
        #expect(renderer.uiImage != nil)
    }
}

@Test
func suiteActivityIndicatorFadesSpokesBehindTheLeadingOne() {
    #expect(SuiteActivityIndicator.spokeOpacity(spoke: 3, head: 3) == 1)
    #expect(SuiteActivityIndicator.spokeOpacity(spoke: 2, head: 3) < 1)
    #expect(SuiteActivityIndicator.spokeOpacity(spoke: 4, head: 3) == 0.2)
}

@Test @MainActor
func suitePagerTabsRenderInBothAppearances() {
    let tabs = [
        SuitePagerTab(tag: 0, title: "Repositories"), SuitePagerTab(tag: 1, title: "Followers"),
        SuitePagerTab(tag: 2, title: "Following"), SuitePagerTab(tag: 3, title: "Stars"),
        SuitePagerTab(tag: 4, title: "Watching")
    ]
    for appearance in [ColorScheme.light, .dark] {
        let renderer = ImageRenderer(
            content: SuitePagerTabs(tabs: tabs, selection: .constant(1)) { Text("Page \($0)") }
                .frame(width: 320, height: 240)
                .preferredColorScheme(appearance)
        )
        #expect(renderer.uiImage != nil)
    }
    #expect(SuitePagerTabs<Int, Text>.tabHeight == 48)
}

@Test @MainActor
func suiteAnchoredTooltipRendersOverItsContent() {
    let renderer = ImageRenderer(
        content: Color.clear
            .frame(width: 320, height: 120)
            .suiteAnchoredTooltip(
                text: "2026-08-03: 9", anchor: CGRect(x: 100, y: 60, width: 10, height: 10), reservedTop: 0) {}
    )
    #expect(renderer.uiImage != nil)
}

@Test
func suiteListRowMinimumHeightMatchesSystemListRows() {
    #expect(SuiteListRowMetrics.minimumHeight == 52)
}
@Test @MainActor
func suiteToolbarTrailingGroupKeepsFixedSpacing() {
    let renderer = ImageRenderer(
        content: NavigationStack {
            Text("Body")
                .suiteToolbar {
                    SuiteToolbarTrailingGroup {
                        Button {} label: { Image(systemName: "star") }
                        Button {} label: { Image(systemName: "square.and.arrow.up") }
                    }
                }
        }
        .frame(width: 320, height: 200)
    )
    #expect(renderer.uiImage != nil)
    #expect(SuiteToolbarMetrics.itemSpacing == 20)
}

@Test @MainActor
func suitePrimaryButtonRendersEnabledAndDisabledInBothShapesAndAppearances() {
    for appearance in [ColorScheme.light, .dark] {
        for shape in [SuitePrimaryButtonStyle.Shape.roundedRectangle, .capsule] {
            for disabled in [false, true] {
                let renderer = ImageRenderer(
                    content: Button("Submit") {}
                        .buttonStyle(.suitePrimary(shape: shape, minHeight: 46))
                        .disabled(disabled)
                        .tint(.indigo)
                        .preferredColorScheme(appearance)
                        .frame(width: 240)
                )
                #expect(renderer.uiImage != nil)
            }
        }
    }
}

@Test @MainActor
func suitePagerTabsAlignsInitialNonFirstSelectionOffset() async throws {
    let selectionState = PagerTestSelection(value: 1)
    let tabs = [
        SuitePagerTab(tag: 0, title: "Repositories"),
        SuitePagerTab(tag: 1, title: "Followers"),
        SuitePagerTab(tag: 2, title: "Following"),
        SuitePagerTab(tag: 3, title: "Stars")
    ]
    let content = PagerTestHost(tabs: tabs, state: selectionState)
        .frame(width: 320, height: 240)

    let window: UIWindow = if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
        UIWindow(windowScene: scene)
    } else {
        UIWindow(frame: CGRect(x: 0, y: 0, width: 320, height: 240))
    }
    window.frame = CGRect(x: 0, y: 0, width: 320, height: 240)
    let controller = UIHostingController(rootView: content)
    window.rootViewController = controller
    window.makeKeyAndVisible()
    controller.view.frame = window.bounds
    defer {
        window.isHidden = true
        window.rootViewController = nil
    }

    for _ in 0..<10 {
        window.layoutIfNeeded()
        controller.view.layoutIfNeeded()
        try await Task.sleep(for: .milliseconds(50))
    }

    let pagerScrollView = try #require(
        findHorizontalPagerScrollView(in: controller.view, expectedWidth: 320)
    )
    #expect(abs(pagerScrollView.contentOffset.x - 320) < 1)
    #expect(selectionState.value == 1)
}

private struct PagerTestHost: View {
    let tabs: [SuitePagerTab<Int>]
    @Bindable var state: PagerTestSelection

    var body: some View {
        SuitePagerTabs(tabs: tabs, selection: $state.value) { tag in
            Text("Page \(tag)")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }
}

@MainActor
@Observable
private final class PagerTestSelection {
    var value: Int

    init(value: Int) {
        self.value = value
    }
}

@MainActor
private func findHorizontalPagerScrollView(in root: UIView, expectedWidth: CGFloat) -> UIScrollView? {
    if let scrollView = root as? UIScrollView,
       abs(scrollView.bounds.width - expectedWidth) < 1,
       scrollView.contentSize.width > expectedWidth * 2 {
        return scrollView
    }
    for subview in root.subviews {
        if let found = findHorizontalPagerScrollView(in: subview, expectedWidth: expectedWidth) {
            return found
        }
    }
    return nil
}

#endif
