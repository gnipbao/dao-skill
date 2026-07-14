#!/usr/bin/env python3
"""Validate dao-skill's deterministic behavior-contract fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_CASES = {
    "root-only-mode-a",
    "design-only-mode-b",
    "create-single-skill",
    "trace-evaluation-output",
    "evolve-failed-skill",
    "absorb-external-method",
    "mode-c-file-first",
    "compound-evaluate-and-fix",
    "optimize-existing-skill",
    "no-unneeded-checkpoint",
    "active-installed-source-separate",
    "runtime-generated-child-boundary",
    "trust-gate-overrides-score",
    "structural-score-is-not-runtime-proof",
    "public-ready-skill-repo",
    "diagnosis-only-no-mutation",
    "no-fake-public-links",
}

REQUIRED_SKILL_MARKERS = (
    "## Mode Router",
    "### Compound Requests",
    "## Optimization Contract",
    "explicitly authorized",
    "## Completion Contract",
    "references/runtime-workspace.md",
)

REQUIRED_CASE_RULES = {
    "optimize-existing-skill": {
        "assertions": {
            "mode:D-then-C",
            "baseline-before-edit",
            "preserve-success-invariants",
            "targeted-retest",
            "residual-uncertainty",
        },
        "forbidden": {
            "absolute-best-claim",
            "score-gaming",
            "feature-bloat",
            "unrequested-external-action",
        },
    }
}


def check(root: Path) -> list[str]:
    issues: list[str] = []
    fixture = root / "test-prompts.json"
    skill_file = root / "SKILL.md"

    try:
        cases = json.loads(fixture.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot load test-prompts.json: {exc}"]

    if not isinstance(cases, list):
        return ["test-prompts.json must contain a JSON array"]

    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(f"Case {index} must be an object")
            continue
        case_id = case.get("id")
        prompt = case.get("prompt")
        expected = case.get("expected")
        assertions = case.get("assertions")
        forbidden = case.get("forbidden")
        if not isinstance(case_id, str) or not case_id.strip():
            issues.append(f"Case {index} has no valid id")
            continue
        if case_id in seen:
            issues.append(f"Duplicate case id: {case_id}")
        seen.add(case_id)
        if not isinstance(prompt, str) or len(prompt.strip()) < 12:
            issues.append(f"Case {case_id} has an underspecified prompt")
        if not isinstance(expected, str) or len(expected.strip()) < 30:
            issues.append(f"Case {case_id} has an underspecified expected behavior")
        if not isinstance(assertions, list) or not assertions or not all(
            isinstance(item, str) and item.strip() for item in assertions
        ):
            issues.append(f"Case {case_id} must define non-empty assertions")
        if not isinstance(forbidden, list) or not forbidden or not all(
            isinstance(item, str) and item.strip() for item in forbidden
        ):
            issues.append(f"Case {case_id} must define non-empty forbidden behaviors")
        if isinstance(assertions, list) and isinstance(forbidden, list):
            overlap = set(assertions) & set(forbidden)
            if overlap:
                issues.append(f"Case {case_id} asserts and forbids the same behavior: {sorted(overlap)}")
            required = REQUIRED_CASE_RULES.get(case_id, {})
            for field, actual in (("assertions", set(assertions)), ("forbidden", set(forbidden))):
                missing_items = required.get(field, set()) - actual
                if missing_items:
                    issues.append(
                        f"Case {case_id} is missing required {field}: {sorted(missing_items)}"
                    )

    for case_id in sorted(REQUIRED_CASES - seen):
        issues.append(f"Missing required behavior case: {case_id}")

    try:
        skill = skill_file.read_text(encoding="utf-8")
    except OSError as exc:
        return issues + [f"Cannot load SKILL.md: {exc}"]
    for marker in REQUIRED_SKILL_MARKERS:
        if marker not in skill:
            issues.append(f"SKILL.md is missing behavior-contract marker: {marker}")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check dao-skill behavior-contract fixtures.")
    parser.add_argument("path", nargs="?", default=".", help="Path to dao-skill repository")
    args = parser.parse_args()

    issues = check(Path(args.path).resolve())
    if issues:
        print("Behavior contract check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Behavior contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
