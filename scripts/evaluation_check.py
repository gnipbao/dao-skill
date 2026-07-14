#!/usr/bin/env python3
"""Check that dao-skill's evaluation contract is internally consistent."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from validation_utils import strip_nonsemantic_markdown


EXPECTED_WEIGHTS = {
    "根问题与适用性": 15,
    "流程可靠性": 20,
    "结果有效性": 20,
    "边界与可信披露": 10,
    "规范与维护性": 10,
    "组合与交接能力": 10,
    "证据与验证闭环": 10,
    "可进化性": 5,
}

REQUIRED_RUBRIC_MARKERS = [
    "## 0. Evaluation Mode And Evidence Level",
    "## 1. Trust Gate",
    "## 2. Scorecard",
    "## 3. Verdict Rules",
    "Permission scope",
    "Sensitive data",
    "Input and action safety",
    "Dependencies and provenance",
    "Environment fitness",
    "E1 -> structural estimate only",
    "Trust `FAIL` -> reject",
]

REQUIRED_SKILL_MARKERS = [
    "evidence level -> Trust Gate -> 100-point score",
    "Trust is a hard gate",
    "scripts/evaluation_check.py",
]


def extract_weights(text: str) -> dict[str, int]:
    weights: dict[str, int] = {}
    pattern = re.compile(r"^([^\n：:]+)[：:]0-(\d+)\s*$", re.MULTILINE)
    for label, maximum in pattern.findall(text):
        label = label.strip()
        if label in EXPECTED_WEIGHTS:
            weights[label] = int(maximum)
    table_pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*$", re.MULTILINE)
    for label, maximum in table_pattern.findall(text):
        label = label.strip()
        if label in EXPECTED_WEIGHTS:
            weights[label] = int(maximum)
    return weights


def check(root: Path) -> list[str]:
    issues: list[str] = []
    skill_path = root / "SKILL.md"
    rubric_path = root / "references" / "evaluation-rubric.md"

    for path in (skill_path, rubric_path):
        if not path.is_file():
            issues.append(f"Missing required file: {path.relative_to(root)}")
    if issues:
        return issues

    skill = strip_nonsemantic_markdown(skill_path.read_text(encoding="utf-8"))
    rubric = strip_nonsemantic_markdown(rubric_path.read_text(encoding="utf-8"))

    for rel, text, markers in (
        ("SKILL.md", skill, REQUIRED_SKILL_MARKERS),
        ("references/evaluation-rubric.md", rubric, REQUIRED_RUBRIC_MARKERS),
    ):
        for marker in markers:
            if marker not in text:
                issues.append(f"Missing evaluation marker in {rel}: {marker}")

    weights = extract_weights(rubric)
    if weights != EXPECTED_WEIGHTS:
        issues.append(
            "Score weights in references/evaluation-rubric.md differ from the canonical "
            f"weights: {weights}"
        )
    elif sum(weights.values()) != 100:
        issues.append(
            "Score weights in references/evaluation-rubric.md sum to "
            f"{sum(weights.values())}, not 100"
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check dao-skill evaluation weights, gates, and evidence rules."
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to dao-skill folder")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    issues = check(root)
    if issues:
        print("Evaluation check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Evaluation check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
