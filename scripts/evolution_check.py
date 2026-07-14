#!/usr/bin/env python3
"""Check that dao-skill keeps its evolution machinery wired together."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validation_utils import strip_nonsemantic_markdown


REQUIRED_FILES = [
    "SKILL.md",
    "references/evolution-protocol.md",
    "references/self-evolving-skill-system.md",
]

REQUIRED_MARKERS = {
    "SKILL.md": [
        "### 6. 机 · Execute The Evolution Machine",
        "CHECKPOINT / STOP",
        "scripts/evolution_check.py",
        "asset action: `create`, `merge`, or `discard`",
        "deployment status (`accepted`, `provisional`, `quarantined`, or `rejected`)",
        "回滚或隔离条件",
    ],
    "references/evolution-protocol.md": [
        "## Evolution Run Contract",
        "## CHECKPOINT / STOP Gates",
        "### 1. Build The Evidence Packet",
        "### 4. Retrieve The Nearest Existing Asset",
        "### 8. Validate And Decide",
        "dry-run",
    ],
    "references/self-evolving-skill-system.md": [
        "## Agent-Level Evolution Machine",
        "## Trace Packet",
        "## Evolution Ledger",
        "### Validation Matrix",
        "## Independent Evaluation",
        "## Deployment Rule",
    ],
}


def check_file_exists(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            issues.append(f"Missing required file: {rel}")
    return issues


def check_markers(root: Path) -> list[str]:
    issues: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.is_file():
            continue
        text = strip_nonsemantic_markdown(path.read_text(encoding="utf-8"))
        for marker in markers:
            if marker not in text:
                issues.append(f"Missing marker in {rel}: {marker}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check dao-skill evolution protocol wiring.")
    parser.add_argument("path", nargs="?", default=".", help="Path to dao-skill folder")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    issues = check_file_exists(root)
    issues.extend(check_markers(root))
    if issues:
        print("Evolution check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Evolution check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
