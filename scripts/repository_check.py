#!/usr/bin/env python3
"""Check the public dao-skill repository boundary before publication."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = {
    ".gitignore",
    "README.md",
    "SKILL.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "agents/openai.yaml",
    "assets/dao-skill-banner.png",
    "references/runtime-workspace.md",
    "scripts/quality_check.py",
    "scripts/evolution_check.py",
    "scripts/evaluation_check.py",
    "scripts/repository_check.py",
    "test-prompts.json",
}

FORBIDDEN_PREFIXES = (
    ".dao/",
    ".firecrawl/",
    ".tmp/",
    "content-to-skill/",
    "find-skill/",
    "generated-skills/",
    "how-to-understand-anything-skill/",
    "knowledge-cat-ppt-skill/",
    "output/",
    "runs/",
    "skill-bank/",
)

FORBIDDEN_NAMES = {
    ".DS_Store",
    ".env",
}

SENSITIVE_PATTERNS = {
    "private macOS path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "private Linux path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
}

TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".tsv"}


def git_candidates(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError("not a Git work tree; run `git init` before the publication check")
    return [root / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def check(root: Path, strict_license: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        candidates = git_candidates(root)
    except RuntimeError as exc:
        return [str(exc)], warnings

    relative = {path.relative_to(root).as_posix() for path in candidates if path.is_file()}
    for required in sorted(REQUIRED_FILES - relative):
        errors.append(f"Missing public file: {required}")

    licenses = sorted(name for name in relative if Path(name).name.startswith("LICENSE"))
    if not licenses:
        message = "No LICENSE file; source-visible is not open source until the maintainer chooses a license"
        if strict_license:
            errors.append(message)
        else:
            warnings.append(message)

    for rel in sorted(relative):
        path = Path(rel)
        if rel.startswith(FORBIDDEN_PREFIXES):
            errors.append(f"Runtime or child-project file would be published: {rel}")
        if rel.startswith("examples/") and len(path.parts) > 2:
            errors.append(f"Nested child project would be published as an example: {rel}")
        if path.name in FORBIDDEN_NAMES or path.suffix in {".pyc", ".bak", ".tmp", ".log"}:
            errors.append(f"Local/generated file would be published: {rel}")
        if ".bak." in path.name or "__pycache__" in path.parts:
            errors.append(f"Backup/cache file would be published: {rel}")

    for rel in sorted(relative):
        path = root / rel
        if path.suffix not in TEXT_SUFFIXES or path.stat().st_size > 1_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"Possible {label} in {rel}")

    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    for marker in ("## 仓库边界：子 Skill 动态生成", "## 本地验证", "scripts/repository_check.py"):
        if marker not in readme:
            errors.append(f"README.md is missing publication marker: {marker}")

    skill = (root / "SKILL.md").read_text(encoding="utf-8") if (root / "SKILL.md").is_file() else ""
    for marker in ("references/runtime-workspace.md", "Never use the dao-skill source"):
        if marker not in skill:
            errors.append(f"SKILL.md is missing runtime boundary marker: {marker}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check dao-skill's public repository boundary.")
    parser.add_argument("path", nargs="?", default=".", help="Path to dao-skill repository")
    parser.add_argument(
        "--strict-license",
        action="store_true",
        help="Fail instead of warning when LICENSE has not been selected",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    errors, warnings = check(root, args.strict_license)
    for warning in warnings:
        print(f"Warning: {warning}")
    if errors:
        print("Repository check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
