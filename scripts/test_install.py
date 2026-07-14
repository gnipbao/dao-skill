#!/usr/bin/env python3
"""Regression tests for the safe dao-skill installer."""

from __future__ import annotations

import tempfile
import unittest
import shutil
from pathlib import Path

from install import install_payload, payload_files, restore_backup


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = Path(__file__).resolve().parents[1]

    def test_payload_excludes_repository_and_runtime_state(self) -> None:
        relative = {path.as_posix() for path in payload_files(self.source)}
        self.assertIn("SKILL.md", relative)
        self.assertIn("references/runtime-workspace.md", relative)
        self.assertNotIn(".git/config", relative)
        self.assertFalse(any(path.startswith(".github/") for path in relative))
        self.assertFalse(any(path.startswith("skill-bank/") for path in relative))
        self.assertFalse(any(path.count("/") > 1 for path in relative if path.startswith("examples/")))

    def test_install_and_safe_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills" / "dao-skill"
            files, backup = install_payload(self.source, target)
            self.assertIsNone(backup)
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertEqual(len(files), len(payload_files(self.source)))

            with self.assertRaises(FileExistsError):
                install_payload(self.source, target)

            sentinel = target / "local-sentinel.txt"
            sentinel.write_text("old installation", encoding="utf-8")
            _, backup = install_payload(self.source, target, force=True)
            self.assertIsNotNone(backup)
            assert backup is not None
            self.assertNotEqual(backup.parent, target.parent)
            self.assertNotIn(target.parent, backup.parents)
            self.assertTrue((backup / "local-sentinel.txt").is_file())
            self.assertFalse((target / "local-sentinel.txt").exists())
            self.assertTrue((target / "SKILL.md").is_file())

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills" / "dao-skill"
            files, backup = install_payload(self.source, target, dry_run=True)
            self.assertTrue(files)
            self.assertIsNone(backup)
            self.assertFalse(target.exists())

    def test_dry_run_allows_existing_target_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills" / "dao-skill"
            target.mkdir(parents=True)
            files, backup = install_payload(self.source, target, dry_run=True)
            self.assertTrue(files)
            self.assertIsNone(backup)
            self.assertTrue(target.is_dir())

    def test_rejects_source_ancestor_as_target(self) -> None:
        with self.assertRaises(ValueError):
            install_payload(self.source, self.source.parent, force=True, dry_run=True)

    def test_custom_target_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "custom skill location" / "dao-skill"
            install_payload(self.source, target)
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertFalse((target / ".git").exists())

            (target / "sentinel.txt").write_text("old", encoding="utf-8")
            _, backup = install_payload(self.source, target, force=True)
            assert backup is not None
            self.assertNotIn(target.parent, backup.parents)
            self.assertTrue((backup / "sentinel.txt").is_file())

    def test_opaque_legacy_backup_restore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills" / "dao-skill"
            install_payload(self.source, target)

            legacy = Path(tmp) / "legacy-backup"
            shutil.copytree(target, legacy)
            (legacy / "references" / "runtime-workspace.md").unlink()
            (legacy / "scripts" / "run_checks.py").unlink()
            (legacy / "legacy-only.txt").write_text("legacy", encoding="utf-8")
            (target / "current-only.txt").write_text("current", encoding="utf-8")

            current_backup = restore_backup(legacy, target)
            assert current_backup is not None
            self.assertTrue((target / "legacy-only.txt").is_file())
            self.assertFalse((target / "references" / "runtime-workspace.md").exists())
            self.assertTrue((current_backup / "current-only.txt").is_file())

    def test_rejects_state_directory_inside_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills" / "dao-skill"
            with self.assertRaises(ValueError):
                install_payload(
                    self.source,
                    target,
                    dry_run=True,
                    state_root=self.source / ".installer-state",
                )


if __name__ == "__main__":
    unittest.main()
