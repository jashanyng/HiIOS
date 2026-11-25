from __future__ import annotations

import datetime as dt
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def write_fixture_repo(
    root: Path,
    *,
    version: str = "0.0.1",
    changelog: str | None = None,
    compatibility: str | None = "# 兼容性说明\n\n- iOS 17+ / Swift 6\n",
) -> None:
    if version is not None:
        (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    if changelog is None:
        changelog = (
            "# 变更日志（Changelog）\n\n"
            "## [Unreleased]\n\n"
            f"## [{version}]\n\n"
            "### 新增\n\n"
            "- 初始化基础基线。\n"
        )
    if changelog is not None:
        (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    if compatibility is not None:
        docs_dir = root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "compatibility.md").write_text(compatibility, encoding="utf-8")


class VersionGuardTest(unittest.TestCase):
    def test_verify_real_repo_passes(self) -> None:
        import verify_version_docs

        version = verify_version_docs.validate_version_docs(REPO_ROOT)
        self.assertRegex(version, r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

    def test_verify_accepts_dated_release_heading(self) -> None:
        import verify_version_docs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(
                root,
                version="0.0.2",
                changelog=(
                    "# 变更日志（Changelog）\n\n"
                    "## [Unreleased]\n\n"
                    "## [0.0.2] - 2026-11-25\n\n"
                    "- 增量修复。\n"
                ),
            )
            self.assertEqual(verify_version_docs.validate_version_docs(root), "0.0.2")

    def test_verify_rejects_missing_or_invalid_version_file(self) -> None:
        import verify_version_docs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root)
            (root / "VERSION").unlink()
            with self.assertRaises(ValueError):
                verify_version_docs.validate_version_docs(root)

        for bad_version in ("v0.0.1\n", "0.0.1\n0.0.2\n", " 0.0.1\n", "", "0.01.0\n", "1.0\n"):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_fixture_repo(root, version="0.0.1")
                (root / "VERSION").write_text(bad_version, encoding="utf-8")
                with self.assertRaises(ValueError):
                    verify_version_docs.validate_version_docs(root)

    def test_verify_rejects_missing_changelog_or_sections_or_sync_mismatch(self) -> None:
        import verify_version_docs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root)
            (root / "CHANGELOG.md").unlink()
            with self.assertRaises(ValueError):
                verify_version_docs.validate_version_docs(root)

        bad_changelogs = [
            "# 变更日志（Changelog）\n\n## [0.0.1]\n\n- 缺少 Unreleased。\n",
            "# 变更日志（Changelog）\n\n## [Unreleased] extra\n\n## [0.0.1]\n",
            "# 变更日志（Changelog）\n\n## [Unreleased]\n\n## [0.0.2]\n",
            "# 变更日志（Changelog）\n\n## [Unreleased]\n\n## [v0.0.1]\n",
        ]
        for content in bad_changelogs:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_fixture_repo(root, version="0.0.1", changelog=content)
                with self.assertRaises(ValueError):
                    verify_version_docs.validate_version_docs(root)

    def test_verify_rejects_missing_or_empty_compatibility_doc(self) -> None:
        import verify_version_docs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root)
            (root / "docs" / "compatibility.md").unlink()
            with self.assertRaises(ValueError):
                verify_version_docs.validate_version_docs(root)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root, compatibility="   \n\n")
            with self.assertRaises(ValueError):
                verify_version_docs.validate_version_docs(root)

    def test_verify_cli_nonzero_on_failure(self) -> None:
        script = SCRIPTS_DIR / "verify_version_docs.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root, version="0.0.1")
            (root / "VERSION").write_text("v0.0.1\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("裸 x.y.z", result.stderr)

    def test_bump_rejects_xy_change_without_flag_and_leaves_files_untouched(self) -> None:
        import bump_version

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root, version="0.0.1")
            before_ver = (root / "VERSION").read_text(encoding="utf-8")
            before_log = (root / "CHANGELOG.md").read_text(encoding="utf-8")

            for candidate in ("0.1.0", "1.0.0"):
                with self.assertRaises(ValueError):
                    bump_version.bump_version(candidate, repo_root=root)

            script = SCRIPTS_DIR / "bump_version.py"
            result = subprocess.run(
                [sys.executable, str(script), "--root", str(root), "1.0.0"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--allow-xy-bump", result.stderr)
            self.assertEqual((root / "VERSION").read_text(encoding="utf-8"), before_ver)
            self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), before_log)

    def test_bump_rejects_non_increasing_or_invalid_version_without_modifying_files(self) -> None:
        import bump_version

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root, version="0.0.3")
            before_ver = (root / "VERSION").read_text(encoding="utf-8")
            before_log = (root / "CHANGELOG.md").read_text(encoding="utf-8")

            for candidate in ("0.0.3", "0.0.2", "0.0.0", "v0.0.4"):
                with self.assertRaises(ValueError):
                    bump_version.bump_version(candidate, repo_root=root, allow_xy_bump=True)

            self.assertEqual((root / "VERSION").read_text(encoding="utf-8"), before_ver)
            self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), before_log)

    def test_bump_z_archives_unreleased_notes_and_passes_verify(self) -> None:
        import bump_version
        import verify_version_docs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(
                root,
                version="0.0.1",
                changelog=(
                    "# 变更日志（Changelog）\n\n"
                    "## [Unreleased]\n\n"
                    "### 修复\n\n"
                    "- 修复路由参数解码边界。\n\n"
                    "## [0.0.1]\n\n"
                    "- 初始版本。\n"
                ),
            )
            script = SCRIPTS_DIR / "bump_version.py"
            result = subprocess.run(
                [sys.executable, str(script), "--root", str(root), "0.0.2"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual((root / "VERSION").read_text(encoding="utf-8"), "0.0.2\n")

            today = dt.date.today().isoformat()
            changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertIn("## [Unreleased]", changelog)
            self.assertIn(f"## [0.0.2] - {today}", changelog)
            self.assertIn("- 修复路由参数解码边界。", changelog)
            self.assertLess(
                changelog.index("## [Unreleased]"),
                changelog.index(f"## [0.0.2] - {today}"),
            )
            self.assertLess(
                changelog.index(f"## [0.0.2] - {today}"),
                changelog.index("## [0.0.1]"),
            )
            self.assertEqual(verify_version_docs.validate_version_docs(root), "0.0.2")

    def test_bump_empty_unreleased_inserts_default_bullet_and_supports_allow_xy_flag(self) -> None:
        import bump_version
        import verify_version_docs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(
                root,
                version="0.0.1",
                changelog=(
                    "# 变更日志（Changelog）\n\n"
                    "## [Unreleased]\n\n"
                    "## [0.0.1]\n\n"
                    "- 初始版本。\n"
                ),
            )
            script = SCRIPTS_DIR / "bump_version.py"
            result = subprocess.run(
                [sys.executable, str(script), "--root", str(root), "--allow-xy-bump", "0.1.0"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual((root / "VERSION").read_text(encoding="utf-8"), "0.1.0\n")

            today = dt.date.today().isoformat()
            changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            expected_section = (
                f"## [Unreleased]\n\n## [0.1.0] - {today}\n\n- 版本号对齐（无行为变更）。\n"
            )
            self.assertIn(expected_section, changelog)
            self.assertEqual(verify_version_docs.validate_version_docs(root), "0.1.0")
            # 确认函数入口也可用
            old_v, new_v = bump_version.bump_version("0.1.1", repo_root=root)
            self.assertEqual((old_v, new_v), ("0.1.0", "0.1.1"))

    def test_fenced_code_block_headings_do_not_break_verify_or_bump(self) -> None:
        import bump_version
        import verify_version_docs

        changelog = (
            "# 变更日志（Changelog）\n\n"
            "## [Unreleased]\n\n"
            "- 代码块前的真实变更。\n\n"
            "```markdown\n"
            "## [Unreleased]\n\n"
            "## [0.0.2]\n"
            "```\n\n"
            "- 代码块后的真实变更。\n\n"
            "## [0.0.1]\n\n"
            "- 初始版本。\n\n"
            "```markdown\n"
            "## [Unreleased]\n\n"
            "## [0.0.2] - 2026-11-25\n"
            "```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture_repo(root, version="0.0.1", changelog=changelog)

            self.assertEqual(verify_version_docs.validate_version_docs(root), "0.0.1")

            old_v, new_v = bump_version.bump_version(
                "0.0.2",
                repo_root=root,
                release_date="2026-11-25",
            )
            self.assertEqual((old_v, new_v), ("0.0.1", "0.0.2"))

            updated = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertIn(
                "## [Unreleased]\n\n"
                "## [0.0.2] - 2026-11-25\n\n"
                "- 代码块前的真实变更。\n\n"
                "```markdown\n"
                "## [Unreleased]\n\n"
                "## [0.0.2]\n"
                "```\n\n"
                "- 代码块后的真实变更。\n\n"
                "## [0.0.1]\n",
                updated,
            )
            self.assertEqual(verify_version_docs.validate_version_docs(root), "0.0.2")

    def test_mask_fenced_code_blocks_preserves_length_newlines_and_nested_fences(self) -> None:
        import verify_version_docs

        sample = (
            "## [Unreleased]\r\n"
            "  ````markdown\r\n"
            "```\r\n"
            "## [0.0.2]\r\n"
            "~~~~\r\n"
            "  ````   \r\n"
            "~~~text\r\n"
            "## [Unreleased]\r\n"
            "~~~\r\n"
            "## [0.0.1]\r\n"
        )
        normalized = sample.replace("\r\n", "\n")
        masked = verify_version_docs.mask_fenced_code_blocks(sample)

        self.assertEqual(len(masked), len(normalized))
        self.assertEqual(
            [i for i, ch in enumerate(masked) if ch == "\n"],
            [i for i, ch in enumerate(normalized) if ch == "\n"],
        )
        self.assertEqual(
            verify_version_docs.UNRELEASED_HEADING_RE.findall(masked),
            ["## [Unreleased]"],
        )
        self.assertIsNone(
            verify_version_docs.re.search(r"^## \[0\.0\.2\]$", masked, verify_version_docs.re.MULTILINE)
        )
        self.assertIsNotNone(
            verify_version_docs.re.search(r"^## \[0\.0\.1\]$", masked, verify_version_docs.re.MULTILINE)
        )


if __name__ == "__main__":
    unittest.main()
