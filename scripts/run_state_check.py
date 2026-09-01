#!/usr/bin/env python3
"""Deterministic validator for a dao-skill run record.

dao-skill already defines the vocabulary of a run: evidence levels E0-E4, the
Trust Gate verdicts, the asset decision, the deployment status, and the
Completion Contract. What it does not define is anything that *enforces* them.
Today the model is asked to follow that contract by reading it; nothing checks
that it did. This script closes that gap: schema ownership moves out of the
model and into a deterministic runtime, so a run cannot be reported complete
while a required field is missing or an evidence claim outruns its proof.

Usage:
    python3 scripts/run_state_check.py patch run.json '{"evidence_level": "E3"}'
    python3 scripts/run_state_check.py check run.json

`check` exits non-zero when the record is incomplete or internally
inconsistent. `patch` applies a delta with null-deletion semantics.

The rules below are intentionally few. Each one exists because a real run
failed without it; none of them encodes taste.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EVIDENCE_LEVELS = ["E0", "E1", "E2", "E3", "E4"]
TRUST_VERDICTS = ["PASS", "CONDITIONAL", "FAIL", "UNKNOWN", "N/A"]
ASSET_DECISIONS = ["create", "merge", "discard"]
DEPLOYMENT_STATUS = ["accepted", "provisional", "quarantined", "rejected"]

# field -> (required for a completion claim, description)
FIELDS = {
    "target": (True, "path the run acted on"),
    "baseline": (True, "state before the change; without it nothing can be compared afterwards"),
    "changed": (True, "files created or modified"),
    "evidence_level": (True, f"one of {EVIDENCE_LEVELS}"),
    "evidence": (True, "what was actually run, and what it returned"),
    "reverse_tested": (True, "which change makes the check go red; a check nobody has seen fail is not a check"),
    "rollback": (True, "how to undo this run"),
    "not_done": (True, "external actions not performed; write 'none' rather than leaving it empty"),
    "trust_gate": (False, f"mapping of gate -> {TRUST_VERDICTS}"),
    "asset_decision": (False, f"one of {ASSET_DECISIONS}"),
    "deployment_status": (False, f"one of {DEPLOYMENT_STATUS}"),
    "findings_open": (False, "findings still unresolved"),
    "findings_declined": (False, "findings deliberately not fixed, with the reason"),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def patch(path: Path, delta: dict) -> None:
    unknown = sorted(set(delta) - set(FIELDS))
    if unknown:
        sys.exit(f"schema violation: undeclared field(s) {unknown}")
    state = load(path)
    for key, value in delta.items():
        if value is None:
            state.pop(key, None)
        else:
            state[key] = value
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {sorted(delta)}; {len(state)}/{len(FIELDS)} fields present")


def _filled(state: dict, key: str) -> bool:
    return bool(str(state.get(key, "")).strip())


def check(path: Path) -> None:
    state = load(path)
    issues: list[str] = []

    for key, (required, description) in FIELDS.items():
        if required and not _filled(state, key):
            issues.append(f"missing required field `{key}` ({description})")

    level = state.get("evidence_level")
    if level and level not in EVIDENCE_LEVELS:
        issues.append(f"`evidence_level` must be one of {EVIDENCE_LEVELS}, got {level!r}")

    # An E3/E4 claim asserts executed or independent evidence. The rubric already
    # says E1 cannot certify reliability; this makes the same statement checkable.
    if level in ("E3", "E4") and not _filled(state, "reverse_tested"):
        issues.append(f"`evidence_level` {level} claims executed evidence but `reverse_tested` is empty")

    for gate, verdict in (state.get("trust_gate") or {}).items():
        if verdict not in TRUST_VERDICTS:
            issues.append(f"trust_gate[{gate}] must be one of {TRUST_VERDICTS}, got {verdict!r}")
        if verdict == "FAIL":
            issues.append(f"trust_gate[{gate}] is FAIL; the rubric rejects the run regardless of score")

    for key, allowed in (("asset_decision", ASSET_DECISIONS), ("deployment_status", DEPLOYMENT_STATUS)):
        value = state.get(key)
        if value and value not in allowed:
            issues.append(f"`{key}` must be one of {allowed}, got {value!r}")

    if state.get("deployment_status") == "accepted" and level in ("E0", "E1"):
        issues.append(f"`deployment_status` accepted requires more than {level}; E1 yields a structural estimate only")

    if issues:
        print("run record incomplete:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    print(f"run record complete ({len(state)} fields, evidence {level}).")


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    command, target = sys.argv[1], Path(sys.argv[2])
    if command == "check":
        check(target)
    elif command == "patch":
        if len(sys.argv) < 4:
            sys.exit("patch requires a JSON delta")
        patch(target, json.loads(sys.argv[3]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
