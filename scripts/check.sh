#!/usr/bin/env bash
set -euo pipefail

DOCS_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --docs-only)
      DOCS_ONLY=true
      shift
      ;;
    -h|--help)
      echo "用法: $0 [--docs-only]"
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      echo "用法: $0 [--docs-only]" >&2
      exit 2
      ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 scripts/verify_version_docs.py
python3 -m unittest discover -s scripts -p 'test_*.py'

if [[ "$DOCS_ONLY" == true ]]; then
  exit 0
fi

swift package dump-package >/dev/null

if command -v swiftlint >/dev/null 2>&1; then
  swiftlint lint --strict Package.swift
fi

swift build --only-use-versions-from-resolved-file --target HiIOSBaseTests

SDK_PLATFORM_PATH="$(xcrun --show-sdk-platform-path)"
TESTING_HELPER="$(xcrun --find swift | sed 's|/bin/swift$|/libexec/swift/pm/swiftpm-testing-helper|')"

DYLD_FRAMEWORK_PATH="${SDK_PLATFORM_PATH}/Developer/Library/Frameworks" \
DYLD_LIBRARY_PATH="${SDK_PLATFORM_PATH}/Developer/usr/lib" \
"$TESTING_HELPER" \
  --test-bundle-path .build/debug/HiIOSBaseTests.xctest/Contents/MacOS/HiIOSBaseTests \
  --testing-library swift-testing
