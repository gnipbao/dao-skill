#!/usr/bin/env python3
"""Run the complete deterministic dao-skill validation suite."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Use -h/--help to see this message without running anything."
        ),
    )
    # The positional argument is not optional by accident: install.py's
    # validate_staging() invokes this script as `run_checks.py <staging>`, and
    # validate_restored_installation() invokes it with no arguments. Rejecting
    # positionals breaks both. With no argument we fall back to this script's
    # parent directory, which is the usage SKILL.md documents.
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to the skill root to validate (default: this script's parent directory)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    # Parsing arguments here is not about reading values. It makes -h/--help
    # return immediately and unknown options fail, instead of silently running
    # the whole suite: `run_checks.py --help` used to take ~1.7s, unlike the four
    # sibling checkers.`
    args = parse_args(sys.argv[1:] if argv is None else argv)

    root = Path(args.path).resolve() if args.path else Path(__file__).resolve().parents[1]
    commands: list[tuple[str, list[str]]] = [
        ("quality", [sys.executable, "scripts/quality_check.py", ".", "--profile", "dao"]),
        ("evolution", [sys.executable, "scripts/evolution_check.py", "."]),
        ("evaluation", [sys.executable, "scripts/evaluation_check.py", "."]),
        ("behavior contracts", [sys.executable, "scripts/behavior_contract_check.py", "."]),
    ]
    if (root / ".git").exists():
        commands.extend(
            [
                (
                    "repository boundary",
                    [sys.executable, "scripts/repository_check.py", ".", "--strict-license"],
                ),
                ("installer regression", [sys.executable, "scripts/test_install.py"]),
                ("validator regression", [sys.executable, "scripts/test_validators.py"]),
            ]
        )
    else:
        print("Installed-package mode: skipping Git repository and installer self-tests.")
        commands.insert(
            0,
            (
                "install receipt",
                [sys.executable, "scripts/install.py", "--verify", "--target", "."],
            ),
        )
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

    for label, command in commands:
        print(f"==> {label}", flush=True)
        result = subprocess.run(command, cwd=root, env=env, check=False)
        if result.returncode != 0:
            print(f"Check failed: {label}", file=sys.stderr)
            return result.returncode

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
