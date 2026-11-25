#!/usr/bin/env python3
"""严格递增 HiIOS 根 VERSION 并自动将 CHANGELOG.md 的 [Unreleased] 正文归档到目标版本。"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import verify_version_docs  # noqa: E402

REPO_ROOT = verify_version_docs.REPO_ROOT
NEXT_SECTION_RE = re.compile(r"^## \[", re.MULTILINE)
DEFAULT_EMPTY_NOTE = "- 版本号对齐（无行为变更）。"


def archive_unreleased_changelog(
    changelog_text: str,
    new_version: str,
    *,
    release_date: str | None = None,
) -> str:
    """将 CHANGELOG.md 中 `## [Unreleased]` 下的正文归档到 `## [<new_version>] - YYYY-MM-DD`。"""
    normalized_text = changelog_text.replace("\r\n", "\n")
    masked_text = verify_version_docs.mask_fenced_code_blocks(normalized_text)

    matches = list(verify_version_docs.UNRELEASED_HEADING_RE.finditer(masked_text))
    if len(matches) != 1:
        raise ValueError("CHANGELOG.md 必须且仅能包含一个 `## [Unreleased]` 章节标题。")

    unreleased_match = matches[0]
    body_start = unreleased_match.end()
    next_match = NEXT_SECTION_RE.search(masked_text, pos=body_start)
    body_end = next_match.start() if next_match is not None else len(masked_text)

    existing_target = re.search(
        rf"^## \[{re.escape(new_version)}\](?: - \d{{4}}-\d{{2}}-\d{{2}})?[ \t]*$",
        masked_text,
        re.MULTILINE,
    )
    if existing_target is not None:
        raise ValueError(f"CHANGELOG.md 已存在目标版本节 `## [{new_version}]`。")

    unreleased_body = normalized_text[body_start:body_end].strip()
    if not unreleased_body:
        unreleased_body = DEFAULT_EMPTY_NOTE

    date_str = release_date or dt.date.today().isoformat()
    prefix = normalized_text[: unreleased_match.start()]
    suffix = normalized_text[body_end:].lstrip("\r\n")

    archived_block = (
        "## [Unreleased]\n\n"
        f"## [{new_version}] - {date_str}\n\n"
        f"{unreleased_body}\n"
    )
    if suffix:
        return f"{prefix}{archived_block}\n{suffix.rstrip()}\n"
    return f"{prefix}{archived_block}"


def bump_version(
    new_version: str,
    *,
    repo_root: Path = REPO_ROOT,
    allow_xy_bump: bool = False,
    release_date: str | None = None,
) -> tuple[str, str]:
    """递增仓库 VERSION 并同步归档 CHANGELOG.md，返回 `(old_version, new_version)`。"""
    new_tuple = verify_version_docs.parse_bare_semver(new_version)
    version_path = repo_root / "VERSION"
    old_version = verify_version_docs.read_version_file(version_path)
    old_tuple = verify_version_docs.parse_bare_semver(old_version)

    if new_tuple <= old_tuple:
        raise ValueError(f"目标版本 {new_version} 必须严格大于当前版本 {old_version}。")

    if (new_tuple[0] != old_tuple[0] or new_tuple[1] != old_tuple[1]) and not allow_xy_bump:
        raise ValueError(
            f"默认仅允许递增 z（当前 {old_version} -> 目标 {new_version} 涉及 x/y 变更，须经维护者明确同意并传入 --allow-xy-bump）。"
        )

    changelog_path = repo_root / "CHANGELOG.md"
    if not changelog_path.is_file():
        raise ValueError(f"缺少变更日志文件：{changelog_path}")
    changelog_text = changelog_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    updated_changelog = archive_unreleased_changelog(
        changelog_text,
        new_version,
        release_date=release_date,
    )

    old_version_text = version_path.read_text(encoding="utf-8")
    try:
        version_path.write_text(f"{new_version}\n", encoding="utf-8")
        changelog_path.write_text(updated_changelog, encoding="utf-8")
    except Exception:
        version_path.write_text(old_version_text, encoding="utf-8")
        changelog_path.write_text(changelog_text, encoding="utf-8")
        raise
    return old_version, new_version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="递增 HiIOS 版本号并归档根 CHANGELOG.md。")
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="目标仓库根目录（默认为当前脚本所在仓库根）。",
    )
    parser.add_argument(
        "--allow-xy-bump",
        action="store_true",
        help="显式允许变更 x 或 y（仅维护者明确同意时使用）。",
    )
    parser.add_argument("version", help="目标裸 x.y.z 版本号。")
    args = parser.parse_args(argv)
    try:
        old_version, new_version = bump_version(
            args.version,
            repo_root=args.root.resolve(),
            allow_xy_bump=args.allow_xy_bump,
        )
    except (OSError, ValueError) as exc:
        print(f"版本递增失败：{exc}", file=sys.stderr)
        return 1
    print(f"版本已更新：{old_version} -> {new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
