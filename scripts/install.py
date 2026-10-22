#!/usr/bin/env python3
"""Install dao-skill into a user-owned agent skill directory safely."""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


RECEIPT_NAME = ".dao-install.json"
RECEIPT_SCHEMA = 1
# Files the host OS or Python may drop into an installation; they are not drift.
UNTRACKED_INSTALL_NOISE = {".DS_Store", "Thumbs.db"}


TOP_LEVEL_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "test-prompts.json",
)

PAYLOAD_GLOBS = (
    "agents/*.yaml",
    "references/*.md",
    "examples/*.md",
    "scripts/*.py",
    "assets/*.png",
    "assets/*.jpg",
    "assets/*.jpeg",
    "assets/*.webp",
)

REQUIRED_INSTALLED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "test-prompts.json",
    "agents/openai.yaml",
    "assets/dao-skill-banner.png",
    "references/dao-framework.md",
    "references/evaluation-rubric.md",
    "references/evolution-protocol.md",
    "references/first-principles-framework.md",
    "references/meta-thinking-framework.md",
    "references/production-skill-patterns.md",
    "references/runtime-workspace.md",
    "references/self-evolving-skill-system.md",
    "references/skill-generation-template.md",
    "scripts/behavior_contract_check.py",
    "scripts/evaluation_check.py",
    "scripts/evolution_check.py",
    "scripts/install.py",
    "scripts/quality_check.py",
    "scripts/run_checks.py",
    "scripts/validation_utils.py",
)


def default_target() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return codex_home.expanduser() / "skills" / "dao-skill"


def host_skill_roots() -> set[Path]:
    """Directories that Codex or Claude Code scan for user Skills."""
    home = Path.home()
    roots = (default_target().parent, home / ".codex" / "skills", home / ".claude" / "skills")
    return {root.expanduser().resolve() for root in roots}


def payload_files(source: Path) -> list[Path]:
    files: set[Path] = set()
    for rel in TOP_LEVEL_FILES:
        candidate = source / rel
        if candidate.is_file():
            files.add(candidate)
    for pattern in PAYLOAD_GLOBS:
        files.update(path for path in source.glob(pattern) if path.is_file())

    relative: list[Path] = []
    for path in sorted(files):
        if path.is_symlink():
            raise ValueError(f"Refusing to install symlink: {path.relative_to(source)}")
        relative.append(path.relative_to(source))

    missing = [rel for rel in REQUIRED_INSTALLED_FILES if Path(rel) not in relative]
    if missing:
        raise FileNotFoundError(f"Source package is incomplete: {', '.join(missing)}")
    return relative


def source_revision(source: Path) -> tuple[str | None, list[str]]:
    """Return the source HEAD and its uncommitted entries; (None, []) for a non-Git copy."""
    source = source.expanduser().resolve()
    if not (source / ".git").exists():
        return None, []

    def git(*args: str) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", str(source), *args],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            raise RuntimeError(f"Cannot verify the Git state of {source}: {exc}") from exc
        if result.returncode != 0:
            detail = result.stderr.strip() or "git failed"
            raise RuntimeError(f"Cannot verify the Git state of {source}: {detail}")
        return result.stdout

    commit = git("rev-parse", "--verify", "HEAD").strip()
    dirty = [
        line
        for line in git("status", "--porcelain", "--untracked-files=all", "--", ".").splitlines()
        if line.strip()
    ]
    tracked = set(git("ls-files", "-z", "--", ".").split("\0"))
    dirty.extend(
        f"!! {rel.as_posix()} (payload file is not tracked by Git)"
        for rel in payload_files(source)
        if rel.as_posix() not in tracked
    )
    return commit, dirty


def describe_revision(commit: str | None, dirty_count: int) -> str:
    if commit is None:
        return "not a Git work tree; the installation cannot be traced to a commit"
    if dirty_count:
        return f"{commit} with {dirty_count} uncommitted or untracked change(s)"
    return f"{commit} (clean)"


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_receipt(
    staging: Path, source: Path, files: list[Path], commit: str | None, dirty_count: int
) -> None:
    """Record which commit and bytes were installed; no local paths are stored."""
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "package": "dao-skill",
        "source_commit": commit,
        "uncommitted_changes": dirty_count,
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": {rel.as_posix(): file_digest(source / rel) for rel in files},
    }
    (staging / RECEIPT_NAME).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def verify_receipt(root: Path) -> tuple[str, list[str]]:
    """Compare an installed copy with its receipt; return (summary, drift issues)."""
    receipt_path = root / RECEIPT_NAME
    if not receipt_path.is_file():
        return (
            f"Warning: no {RECEIPT_NAME}; this installation predates receipts or was copied by hand, "
            "so its source revision is unknown. Reinstall with scripts/install.py to make it traceable.",
            [],
        )
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        files = receipt["files"]
        commit = receipt["source_commit"]
        dirty_count = int(receipt["uncommitted_changes"])
        if receipt.get("schema") != RECEIPT_SCHEMA or not isinstance(files, dict):
            raise ValueError("unsupported receipt schema")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return "", [f"{RECEIPT_NAME} is unreadable: {exc}"]

    issues: list[str] = []
    for rel, digest in sorted(files.items()):
        parts = Path(rel).parts
        if not isinstance(digest, str) or Path(rel).is_absolute() or ".." in parts or not parts:
            issues.append(f"{RECEIPT_NAME} lists an unsafe entry: {rel}")
            continue
        path = root / rel
        if path.is_symlink() or not path.is_file():
            issues.append(f"Installed file is missing: {rel}")
        elif file_digest(path) != digest:
            issues.append(f"Installed file differs from the recorded source: {rel}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        rel = relative.as_posix()
        if rel == RECEIPT_NAME or "__pycache__" in relative.parts or path.name in UNTRACKED_INSTALL_NOISE:
            continue
        if path.is_symlink() or (path.is_file() and rel not in files):
            issues.append(f"File was not placed by scripts/install.py: {rel}")
    summary = f"Installed source revision: {describe_revision(commit, dirty_count)}"
    if commit is None or dirty_count:
        summary += (
            "\nWarning: this installation was not built from a clean commit, so its SHA does not "
            "reproduce it; reinstall from a clean commit before comparing it with a remote branch."
        )
    return summary, issues


def validate_staging(staging: Path) -> None:
    checker = staging / "scripts" / "run_checks.py"
    result = subprocess.run(
        [sys.executable, str(checker), str(staging)],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        detail = result.stdout.strip() or result.stderr.strip()
        raise RuntimeError(f"Staged package validation failed: {detail}")


def reject_unsafe_target(source: Path, raw_target: Path) -> Path:
    expanded = raw_target.expanduser().absolute()
    macos_aliases = {
        Path("/var"): Path("/private/var"),
        Path("/tmp"): Path("/private/tmp"),
        Path("/etc"): Path("/private/etc"),
    }
    for candidate in (expanded, *expanded.parents):
        if not candidate.exists() or not candidate.is_symlink():
            continue
        if candidate in macos_aliases and candidate.resolve() == macos_aliases[candidate]:
            continue
        raise ValueError(f"Install target traverses a symlink: {candidate}")

    target = expanded.resolve()
    if target == source or source in target.parents or target in source.parents:
        raise ValueError("Install target must be separate from and outside the dao-skill source repository")
    return target


def state_root_for(target: Path, explicit: Path | None = None) -> Path:
    if explicit is not None:
        state_root = explicit.expanduser().resolve()
    else:
        codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()
        if target == default_target().expanduser().resolve():
            state_root = codex_home
        else:
            state_root = target.parent.parent / ".dao-skill-state"

    if state_root == target.parent or target.parent in state_root.parents:
        raise ValueError("Installer state directory must be outside the Skill discovery root")
    return state_root


def backup_root_for(target: Path, state_root: Path) -> Path:
    if target == default_target().expanduser().resolve():
        target_id = "default"
    else:
        target_id = hashlib.sha256(str(target).encode("utf-8")).hexdigest()[:12]
    return state_root / "backups" / "dao-skill" / target_id


def staging_root_for(state_root: Path) -> Path:
    return state_root / "staging" / "dao-skill"


def next_backup_path(target: Path, state_root: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = backup_root_for(target, state_root)
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = backup_root / stamp
    counter = 1
    while backup.exists():
        backup = backup_root / f"{stamp}-{counter}"
        counter += 1
    return backup


def move_directory(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        source.rename(destination)
    except OSError as exc:
        if exc.errno != errno.EXDEV:
            raise
        shutil.copytree(source, destination)
        shutil.rmtree(source)


def validate_restored_installation(target: Path) -> None:
    if not (target / "SKILL.md").is_file():
        raise RuntimeError("Backup does not contain SKILL.md")
    if (target / "scripts" / "run_checks.py").is_file():
        command = [sys.executable, str(target / "scripts" / "run_checks.py")]
    elif (target / "scripts" / "quality_check.py").is_file():
        command = [
            sys.executable,
            str(target / "scripts" / "quality_check.py"),
            str(target),
        ]
    else:
        raise RuntimeError("Backup has no runnable validation script")
    result = subprocess.run(
        command,
        cwd=target,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        detail = result.stdout.strip() or result.stderr.strip()
        raise RuntimeError(f"Restored installation validation failed: {detail}")


def restore_backup(
    backup: Path,
    target: Path,
    *,
    dry_run: bool = False,
    state_root: Path | None = None,
) -> Path | None:
    source_repo = Path(__file__).resolve().parents[1]
    target = reject_unsafe_target(source_repo, target)
    state_root = state_root_for(target, state_root)
    if state_root == source_repo or source_repo in state_root.parents:
        raise ValueError("Installer state directory must not be inside the source repository")
    if state_root == target or target in state_root.parents:
        raise ValueError("Installer state directory must not be inside the installation target")
    backup = backup.expanduser().absolute()

    if not backup.is_dir() or backup.is_symlink():
        raise ValueError(f"Backup must be a real directory: {backup}")
    if any(path.is_symlink() for path in backup.rglob("*")):
        raise ValueError("Backup contains symlinks and cannot be restored safely")
    backup = backup.resolve()
    if backup == target or backup in target.parents or target in backup.parents:
        raise ValueError("Backup and install target must be separate directories")
    if not (backup / "SKILL.md").is_file():
        raise ValueError("Backup does not contain SKILL.md")
    if dry_run:
        return None

    current_backup: Path | None = None
    original_backup_path = backup
    if target.exists():
        current_backup = next_backup_path(target, state_root)
        move_directory(target, current_backup)

    try:
        move_directory(backup, target)
        validate_restored_installation(target)
    except Exception:
        if target.exists() and not original_backup_path.exists():
            move_directory(target, original_backup_path)
        if current_backup is not None and current_backup.exists() and not target.exists():
            move_directory(current_backup, target)
        raise
    return current_backup


def install_payload(
    source: Path,
    target: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    state_root: Path | None = None,
    revision: tuple[str | None, list[str]] | None = None,
) -> tuple[list[Path], Path | None]:
    source = source.expanduser().resolve()
    target = reject_unsafe_target(source, target)
    state_root = state_root_for(target, state_root)
    if state_root == source or source in state_root.parents:
        raise ValueError("Installer state directory must not be inside the source repository")
    if state_root == target or target in state_root.parents:
        raise ValueError("Installer state directory must not be inside the installation target")
    files = payload_files(source)

    if dry_run:
        return files, None
    if target.exists() and not force:
        raise FileExistsError(f"Target already exists: {target}. Re-run with --force to replace it safely.")
    commit, dirty = revision if revision is not None else source_revision(source)

    target.parent.mkdir(parents=True, exist_ok=True)
    staging_root = staging_root_for(state_root)
    staging_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="install-", dir=staging_root))
    backup: Path | None = None

    try:
        for rel in files:
            destination = staging / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / rel, destination)
        write_receipt(staging, source, files, commit, len(dirty))

        validate_staging(staging)

        if target.exists():
            backup = next_backup_path(target, state_root)
            move_directory(target, backup)

        try:
            move_directory(staging, target)
        except Exception:
            if backup is not None and backup.exists() and not target.exists():
                move_directory(backup, target)
            raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if staging_root.exists() and not any(staging_root.iterdir()):
            staging_root.rmdir()

    return files, backup


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install dao-skill without copying Git metadata, child projects, or runtime state."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="dao-skill source repository (defaults to this script's parent repository)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=default_target(),
        help="installation directory (defaults to $CODEX_HOME/skills/dao-skill)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing installation after preserving it outside the discoverable skills directory",
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        help="staging and backup root; required only when a custom target's parent is not writable",
    )
    parser.add_argument(
        "--restore-backup",
        type=Path,
        help="restore an opaque previous installation directory, including legacy backups",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="install a Git source with uncommitted or untracked changes (disposable test targets only)",
    )
    parser.add_argument("--dry-run", action="store_true", help="show the payload without writing files")
    parser.add_argument(
        "--verify",
        action="store_true",
        help=f"check --target against its {RECEIPT_NAME} receipt and print the installed source revision",
    )
    args = parser.parse_args()

    if args.verify:
        target = args.target.expanduser().resolve()
        if not (target / "SKILL.md").is_file():
            print(f"Verify failed: no installed dao-skill at {target}", file=sys.stderr)
            return 1
        summary, issues = verify_receipt(target)
        if summary:
            print(summary)
        if issues:
            print("Install receipt check failed; reinstall instead of editing the installed copy:", file=sys.stderr)
            for issue in issues:
                print(f"- {issue}", file=sys.stderr)
            return 1
        if (target / RECEIPT_NAME).is_file():
            print("Install receipt check passed.")
        else:
            print("Install receipt check skipped: legacy installation without a receipt.")
        return 0

    try:
        if args.restore_backup is not None:
            current_backup = restore_backup(
                args.restore_backup,
                args.target,
                dry_run=args.dry_run,
                state_root=args.state_dir,
            )
            target = args.target.expanduser().resolve()
            if args.dry_run:
                print(f"Dry run: backup {args.restore_backup.expanduser()} would replace {target}")
            else:
                print(f"Restored backup to {target}")
                if current_backup is not None:
                    print(f"Replaced installation preserved at {current_backup}")
                print("Start a new Codex or Claude Code session to reload the skill catalog.")
            return 0

        source = args.source.expanduser().resolve()
        commit, dirty = source_revision(source)
        if dirty and not args.dry_run and not args.allow_dirty:
            raise RuntimeError(
                f"Source {source} has {len(dirty)} uncommitted or untracked change(s); "
                "commit them so the installation maps to an exact commit "
                "(or pass --allow-dirty for a disposable test target):\n"
                + "\n".join(f"  {entry}" for entry in dirty[:10])
            )
        discovery_root = args.target.expanduser().resolve().parent
        if dirty and not args.dry_run and discovery_root in host_skill_roots():
            raise RuntimeError(
                f"--allow-dirty is for disposable test targets; {discovery_root} is a host Skill "
                "discovery directory, where an uncommitted source would load as an untraceable "
                f"Skill. Commit the {len(dirty)} change(s) first."
            )

        files, backup = install_payload(
            args.source,
            args.target,
            force=args.force,
            dry_run=args.dry_run,
            state_root=args.state_dir,
            revision=(commit, dirty),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1

    revision = describe_revision(commit, len(dirty))
    target = args.target.expanduser().resolve()
    if args.dry_run:
        print(f"Dry run: {len(files)} files would be installed to {target}")
        print(f"Source: {source} @ {revision}")
        if dirty:
            print("A real install refuses this source until the changes are committed:")
            for entry in dirty[:10]:
                print(f"  {entry}")
        if target.exists():
            print("Existing installation detected; the real update requires --force and will preserve a backup.")
        for rel in files:
            print(f"- {rel.as_posix()}")
        return 0

    print(f"Installed {len(files)} files to {target}")
    print(f"Installed source revision: {revision}")
    print(f"Receipt: {target / RECEIPT_NAME}")
    if backup is not None:
        print(f"Previous installation preserved at {backup}")
    print("Start a new Codex or Claude Code session to reload the skill catalog.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
