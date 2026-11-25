#!/usr/bin/env python3
"""校验 HiIOS 仓库根 VERSION、CHANGELOG.md 与 docs/compatibility.md 的存在性、格式与版本同步。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BARE_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
UNRELEASED_HEADING_RE = re.compile(r"^## \[Unreleased\][ \t]*$", re.MULTILINE)
FENCE_OPEN_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


def mask_fenced_code_blocks(text: str) -> str:
    """将围栏代码块（开启行、内部行、关闭行）除换行符外字符替换为空格，保持等长与 \\n 位置不变。"""
    normalized = text.replace("\r\n", "\n")
    fence_char: str | None = None
    fence_len = 0
    close_re: re.Pattern[str] | None = None
    masked_lines: list[str] = []

    lines = normalized.split("\n")
    last_idx = len(lines) - 1
    for idx, body in enumerate(lines):
        suffix = "\n" if idx < last_idx else ""

        if fence_char is None:
            open_match = FENCE_OPEN_RE.match(body)
            if open_match is not None:
                marker = open_match.group(1)
                fence_char = marker[0]
                fence_len = len(marker)
                close_re = re.compile(
                    rf"^[ \t]{{0,3}}{re.escape(fence_char)}{{{fence_len},}}[ \t]*$"
                )
                masked_lines.append((" " * len(body)) + suffix)
            else:
                masked_lines.append(body + suffix)
            continue

        masked_lines.append((" " * len(body)) + suffix)
        if close_re is not None and close_re.match(body) is not None:
            fence_char = None
            fence_len = 0
            close_re = None

    return "".join(masked_lines)


def parse_bare_semver(version: str) -> tuple[int, int, int]:
    """解析无 v 前缀的裸 x.y.z 版本号，格式非法时抛出 ValueError。"""
    match = BARE_SEMVER_RE.fullmatch(version)
    if match is None:
        raise ValueError(f"版本号必须为不带 v 前缀的裸 x.y.z 格式，当前为：{version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def read_version_file(version_path: Path) -> str:
    """读取并校验 VERSION 文件为单行裸 x.y.z 格式。"""
    if not version_path.is_file():
        raise ValueError(f"缺少版本文件：{version_path}")
    raw = version_path.read_text(encoding="utf-8")
    if raw.endswith("\r\n"):
        line = raw[:-2]
    elif raw.endswith("\n"):
        line = raw[:-1]
    else:
        line = raw
    if not line or "\n" in line or "\r" in line or line != line.strip():
        raise ValueError(f"VERSION 必须为单行裸 x.y.z 格式，当前内容为：{raw!r}")
    parse_bare_semver(line)
    return line


def validate_version_docs(repo_root: Path = REPO_ROOT) -> str:
    """校验 VERSION、CHANGELOG.md 与 docs/compatibility.md，成功返回当前版本号。"""
    version = read_version_file(repo_root / "VERSION")

    changelog_path = repo_root / "CHANGELOG.md"
    if not changelog_path.is_file():
        raise ValueError(f"缺少变更日志文件：{changelog_path}")
    changelog_text = changelog_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    masked_changelog = mask_fenced_code_blocks(changelog_text)

    unreleased_matches = UNRELEASED_HEADING_RE.findall(masked_changelog)
    if len(unreleased_matches) != 1:
        raise ValueError(
            f"CHANGELOG.md 必须且仅能包含一个 `## [Unreleased]` 章节标题（实际 {len(unreleased_matches)} 个）。"
        )

    version_heading_re = re.compile(
        rf"^## \[{re.escape(version)}\](?: - \d{{4}}-\d{{2}}-\d{{2}})?[ \t]*$",
        re.MULTILINE,
    )
    if version_heading_re.search(masked_changelog) is None:
        raise ValueError(
            f"CHANGELOG.md 与 VERSION ({version}) 失步：未找到 `## [{version}]`（或带 ` - YYYY-MM-DD` 日期）章节标题。"
        )

    compatibility_path = repo_root / "docs" / "compatibility.md"
    if not compatibility_path.is_file():
        raise ValueError(f"缺少兼容性说明文件：{compatibility_path}")
    if not compatibility_path.read_text(encoding="utf-8").strip():
        raise ValueError(f"兼容性说明文件为空：{compatibility_path}")

    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="校验 HiIOS 版本与治理文档同步门禁。")
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="待校验仓库根目录（默认为当前脚本所在仓库根）。",
    )
    args = parser.parse_args(argv)
    try:
        version = validate_version_docs(args.root.resolve())
    except (OSError, ValueError) as exc:
        print(f"版本与文档校验失败：{exc}", file=sys.stderr)
        return 1
    print(f"版本与文档校验通过：VERSION={version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
