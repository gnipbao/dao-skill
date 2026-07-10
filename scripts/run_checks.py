#!/usr/bin/env python3
"""Run the complete deterministic dao-skill validation suite."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
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
