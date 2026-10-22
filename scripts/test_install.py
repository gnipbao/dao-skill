#!/usr/bin/env python3
"""Regression tests for the safe dao-skill installer."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import shutil
from pathlib import Path

from install import (
    RECEIPT_NAME,
    install_payload,
    payload_files,
    restore_backup,
    source_revision,
    verify_receipt,
)


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

    def make_git_source(self, root: Path) -> tuple[Path, str]:
        source = root / "source"
        for rel in payload_files(self.source):
            destination = source / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source / rel, destination)
        self.assertEqual(source_revision(source), (None, []))

        def git(*args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(source), *args], check=True, capture_output=True, text=True
            ).stdout

        git("init", "-q")
        git("add", "-A")
        git(
            "-c", "user.name=test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-q", "-m", "init",
        )
        return source, git("rev-parse", "HEAD").strip()

    def test_source_revision_detects_uncommitted_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, head = self.make_git_source(Path(tmp))
            self.assertEqual(source_revision(source), (head, []))

            skill = source / "SKILL.md"
            original = skill.read_text(encoding="utf-8")
            skill.write_text(original + "\nuncommitted\n", encoding="utf-8")
            commit, dirty = source_revision(source)
            self.assertEqual(commit, head)
            self.assertTrue(any("SKILL.md" in entry for entry in dirty))
            skill.write_text(original, encoding="utf-8")

            (source / "references" / "untracked.md").write_text("new", encoding="utf-8")
            self.assertTrue(any("untracked.md" in entry for entry in source_revision(source)[1]))
            (source / "references" / "untracked.md").unlink()

            (source / ".git" / "info" / "exclude").write_text("references/ignored.md\n", encoding="utf-8")
            (source / "references" / "ignored.md").write_text("hidden", encoding="utf-8")
            self.assertTrue(any("ignored.md" in entry for entry in source_revision(source)[1]))

    def test_cli_refuses_dirty_source_unless_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, head = self.make_git_source(Path(tmp))
            target = Path(tmp) / "skills" / "dao-skill"
            command = [
                sys.executable, str(self.source / "scripts" / "install.py"),
                "--source", str(source), "--target", str(target),
            ]
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            run = lambda *extra: subprocess.run(
                [*command, *extra], check=False, capture_output=True, text=True, env=env
            )

            (source / "SKILL.md").write_text(
                (source / "SKILL.md").read_text(encoding="utf-8") + "\nuncommitted\n", encoding="utf-8"
            )
            dry_run = run("--dry-run")
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertIn("refuses this source", dry_run.stdout)

            refused = run()
            self.assertEqual(refused.returncode, 1)
            self.assertIn("uncommitted", refused.stderr)
            self.assertFalse(target.exists())

            allowed = run("--allow-dirty")
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn(f"{head} with 1 uncommitted", allowed.stdout)

            subprocess.run(["git", "-C", str(source), "checkout", "--", "SKILL.md"], check=True)
            clean = run("--force")
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertIn(f"Installed source revision: {head} (clean)", clean.stdout)

    def test_allow_dirty_is_refused_for_host_skill_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, _ = self.make_git_source(Path(tmp))
            (source / "SKILL.md").write_text(
                (source / "SKILL.md").read_text(encoding="utf-8") + "\nuncommitted\n", encoding="utf-8"
            )
            home = Path(tmp) / "home"
            codex_home = Path(tmp) / "codex-home"
            env = {
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
                "HOME": str(home),
                "USERPROFILE": str(home),
                "CODEX_HOME": str(codex_home),
            }
            for target in (
                codex_home / "skills" / "dao-skill",
                home / ".codex" / "skills" / "dao-skill",
                home / ".claude" / "skills" / "dao-skill",
            ):
                result = subprocess.run(
                    [
                        sys.executable, str(self.source / "scripts" / "install.py"),
                        "--source", str(source), "--target", str(target), "--allow-dirty",
                    ],
                    check=False, capture_output=True, text=True, env=env,
                )
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("discovery directory", result.stderr)
                self.assertFalse(target.exists())

    def test_receipt_from_dirty_source_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills" / "dao-skill"
            install_payload(self.source, target, revision=("0" * 40, [" M SKILL.md"]))
            summary, issues = verify_receipt(target)
            self.assertEqual(issues, [])
            self.assertIn("with 1 uncommitted", summary)
            self.assertIn("not built from a clean commit", summary)

    def test_receipt_traces_commit_and_detects_installed_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, head = self.make_git_source(Path(tmp))
            target = Path(tmp) / "skills" / "dao-skill"
            files, _ = install_payload(source, target)

            receipt = json.loads((target / RECEIPT_NAME).read_text(encoding="utf-8"))
            self.assertEqual(receipt["source_commit"], head)
            self.assertEqual(receipt["uncommitted_changes"], 0)
            self.assertEqual(set(receipt["files"]), {rel.as_posix() for rel in files})
            self.assertNotIn(str(Path(tmp)), json.dumps(receipt))
            summary, issues = verify_receipt(target)
            self.assertEqual(issues, [])
            self.assertIn(f"{head} (clean)", summary)

            verify = [
                sys.executable, str(self.source / "scripts" / "install.py"),
                "--verify", "--target", str(target),
            ]
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(verify, check=False, capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"Installed source revision: {head} (clean)", result.stdout)

            (target / "scripts" / "__pycache__").mkdir()
            (target / "scripts" / "__pycache__" / "install.cpython.pyc").write_bytes(b"cache")
            self.assertEqual(verify_receipt(target)[1], [])

            skill = target / "SKILL.md"
            original = skill.read_text(encoding="utf-8")
            skill.write_text(original + "\nhand edit\n", encoding="utf-8")
            self.assertTrue(any("SKILL.md" in issue for issue in verify_receipt(target)[1]))
            result = subprocess.run(verify, check=False, capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 1)
            skill.write_text(original, encoding="utf-8")

            (target / "references" / "hand-added.md").write_text("x", encoding="utf-8")
            self.assertTrue(any("hand-added.md" in issue for issue in verify_receipt(target)[1]))
            (target / "references" / "hand-added.md").unlink()
            self.assertEqual(verify_receipt(target)[1], [])

            (target / RECEIPT_NAME).unlink()
            summary, issues = verify_receipt(target)
            self.assertEqual(issues, [])
            self.assertIn("unknown", summary)

    def test_receipt_rejects_paths_outside_installation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills" / "dao-skill"
            install_payload(self.source, target)
            receipt_path = target / RECEIPT_NAME
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["files"]["../outside.md"] = "0" * 64
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            self.assertTrue(any("unsafe entry" in issue for issue in verify_receipt(target)[1]))

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
