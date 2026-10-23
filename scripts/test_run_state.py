#!/usr/bin/env python3
"""Regression tests for the run-record validator.

Each case below is a run that actually happened and was reported as finished.
The validator exists because none of them was caught at the time.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_state_check.py"

COMPLETE = {
    "target": "skills/example",
    "baseline": "SKILL.md 965 lines, no references/",
    "changed": "split SKILL.md into references/",
    "evidence_level": "E3",
    "evidence": "line-set comparison: 626 unique non-empty lines, none lost",
    "reverse_tested": "deleting one line from a reference turns the conservation check red",
    "rollback": "restore from the pre-change file copy",
    "not_done": "none",
}


def run(args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


class RunStateCheck(unittest.TestCase):
    def _record(self, **overrides):
        state = {**COMPLETE, **overrides}
        for key, value in list(state.items()):
            if value is None:
                del state[key]
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(state, handle, ensure_ascii=False)
        handle.close()
        return Path(handle.name)

    def test_complete_record_passes(self):
        # A validator that never passes is as useless as one that never fails.
        self.assertEqual(run(["check", str(self._record())]).returncode, 0)

    def test_missing_rollback_is_rejected(self):
        # A real run declared completion with no rollback point; the intended
        # rollback would have destroyed 248 uncommitted lines.
        result = run(["check", str(self._record(rollback=None))])
        self.assertEqual(result.returncode, 1)
        self.assertIn("rollback", result.stdout)

    def test_executed_evidence_requires_a_reverse_test(self):
        # E3 asserts executed evidence. Without a known failing input the check
        # has never been observed to fail, so the claim outruns its proof.
        result = run(["check", str(self._record(reverse_tested=None))])
        self.assertEqual(result.returncode, 1)
        self.assertIn("claims executed evidence", result.stdout)

    def test_empty_string_does_not_count_as_filled(self):
        result = run(["check", str(self._record(not_done=""))])
        self.assertEqual(result.returncode, 1)

    def test_accepted_deployment_needs_more_than_structural_evidence(self):
        result = run(["check", str(self._record(evidence_level="E1",
                                                deployment_status="accepted"))])
        self.assertEqual(result.returncode, 1)
        self.assertIn("structural estimate only", result.stdout)

    def test_trust_gate_failure_rejects_the_run(self):
        result = run(["check", str(self._record(trust_gate={"sensitive_data": "FAIL"}))])
        self.assertEqual(result.returncode, 1)

    def test_unknown_enum_values_are_rejected(self):
        for field, value in (("evidence_level", "E9"),
                             ("deployment_status", "shipped"),
                             ("asset_decision", "replace")):
            with self.subTest(field=field):
                self.assertEqual(run(["check", str(self._record(**{field: value}))]).returncode, 1)

    def test_undeclared_field_is_refused(self):
        path = self._record()
        result = run(["patch", str(path), '{"whatever": "x"}'])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("schema violation", result.stderr + result.stdout)

    def test_null_deletes_a_field(self):
        path = self._record()
        run(["patch", str(path), '{"rollback": null}'])
        self.assertNotIn("rollback", json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
