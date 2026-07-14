#!/usr/bin/env python3
"""Check the exact public dao-skill repository boundary before publication."""

from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = {
    ".gitignore",
    "README.md",
    "SKILL.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "agents/openai.yaml",
    "assets/dao-skill-banner.png",
    "references/runtime-workspace.md",
    "scripts/behavior_contract_check.py",
    "scripts/evaluation_check.py",
    "scripts/evolution_check.py",
    "scripts/install.py",
    "scripts/quality_check.py",
    "scripts/repository_check.py",
    "scripts/run_checks.py",
    "scripts/test_install.py",
    "scripts/test_validators.py",
    "scripts/validation_utils.py",
    "test-prompts.json",
}

ALLOWED_ROOT_FILES = REQUIRED_FILES | {"LICENSE"}
ALLOWED_TOP_LEVEL = {".github", "agents", "assets", "examples", "references", "scripts"}

FORBIDDEN_NAMES = {".DS_Store", ".env"}
TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}

SENSITIVE_PATTERNS = {
    "private macOS path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "private Linux path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "npm token": re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b"),
}


def run_git(root: Path, args: list[str]) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "Git command failed")
    return result.stdout


def git_file_sets(root: Path) -> tuple[set[str], set[str]]:
    try:
        cached_raw = run_git(root, ["ls-files", "--cached", "-z"])
        untracked_raw = run_git(root, ["ls-files", "--others", "--exclude-standard", "-z"])
    except RuntimeError as exc:
        raise RuntimeError(
            "not a Git work tree; run `git init` before the publication check"
        ) from exc

    decode = lambda raw: {
        item.decode("utf-8") for item in raw.split(b"\0") if item
    }
    return decode(cached_raw), decode(untracked_raw)


def git_index_modes(root: Path) -> dict[str, str]:
    raw = run_git(root, ["ls-files", "--stage", "-z"])
    modes: dict[str, str] = {}
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, path = item.split(b"\t", 1)
        mode = metadata.split(b" ", 1)[0].decode("ascii")
        modes[path.decode("utf-8")] = mode
    return modes


def git_staged_paths(root: Path) -> set[str]:
    raw = run_git(root, ["diff", "--cached", "--name-only", "-z"])
    return {item.decode("utf-8") for item in raw.split(b"\0") if item}


def allowed_layout(rel: str) -> bool:
    path = Path(rel)
    if len(path.parts) == 1:
        return rel in ALLOWED_ROOT_FILES
    if path.parts[0] not in ALLOWED_TOP_LEVEL:
        return False
    if path.parts[0] == ".github":
        return len(path.parts) == 3 and path.parts[1] == "workflows" and path.suffix in {".yml", ".yaml"}
    if path.parts[0] == "agents":
        return rel == "agents/openai.yaml"
    if path.parts[0] == "assets":
        return len(path.parts) == 2 and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    if path.parts[0] in {"examples", "references"}:
        return len(path.parts) == 2 and path.suffix == ".md"
    if path.parts[0] == "scripts":
        return len(path.parts) == 2 and path.suffix == ".py"
    return False


def content_variants(root: Path, rel: str, cached: bool) -> list[tuple[str, bytes]]:
    variants: list[tuple[str, bytes]] = []
    if cached:
        try:
            variants.append(("index", run_git(root, ["show", f":{rel}"])))
        except RuntimeError:
            pass
    worktree = root / rel
    if worktree.is_file():
        variants.append(("worktree", worktree.read_bytes()))
    return variants


def check_png(data: bytes, rel: str) -> list[str]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return [f"Invalid PNG file: {rel}"]
    width, height = struct.unpack(">II", data[16:24])
    if rel == "assets/dao-skill-banner.png":
        if width < 1200 or height < 350 or not 2.5 <= width / height <= 3.5:
            return [
                f"Banner dimensions must be a wide 2.5:1-3.5:1 image at least 1200x350; got {width}x{height}"
            ]
    return []


def parse_fixed_metadata(text: str) -> dict[str, dict[str, object]]:
    data: dict[str, dict[str, object]] = {}
    section: str | None = None
    for line_number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            raise ValueError(f"tabs are not allowed on line {line_number}")
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            if section in data:
                raise ValueError(f"duplicate section: {section}")
            data[section] = {}
            continue
        if indent != 2 or section is None or ":" not in stripped:
            raise ValueError(f"invalid fixed metadata structure on line {line_number}")
        key, raw_value = stripped.split(":", 1)
        raw_value = raw_value.strip()
        if key in data[section]:
            raise ValueError(f"duplicate key: {section}.{key}")
        if raw_value in {"true", "false"}:
            value: object = raw_value == "true"
        elif raw_value.startswith('"'):
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid quoted value on line {line_number}") from exc
        else:
            raise ValueError(f"values must be quoted strings or booleans on line {line_number}")
        data[section][key] = value
    return data


def check_metadata(text: str) -> list[str]:
    issues: list[str] = []
    try:
        data = parse_fixed_metadata(text)
    except ValueError as exc:
        return [f"agents/openai.yaml is invalid: {exc}"]

    expected = {
        "interface": {"display_name", "short_description", "default_prompt"},
        "policy": {"allow_implicit_invocation"},
    }
    if set(data) != set(expected):
        issues.append(f"agents/openai.yaml sections must be exactly: {sorted(expected)}")
    for section, keys in expected.items():
        actual = set(data.get(section, {}))
        if actual != keys:
            issues.append(f"agents/openai.yaml {section} keys must be exactly: {sorted(keys)}")

    interface = data.get("interface", {})
    for key in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(key), str) or not str(interface.get(key)).strip():
            issues.append(f"agents/openai.yaml interface.{key} must be a non-empty string")
    short_description = interface.get("short_description", "")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        issues.append("agents/openai.yaml interface.short_description must be 25-64 characters")
    prompt = interface.get("default_prompt", "")
    if isinstance(prompt, str):
        for marker in ("$dao-skill", "explicitly requests"):
            if marker not in prompt:
                issues.append(f"agents/openai.yaml default_prompt is missing guard: {marker}")
    allow_implicit = data.get("policy", {}).get("allow_implicit_invocation")
    if not isinstance(allow_implicit, bool):
        issues.append("agents/openai.yaml policy.allow_implicit_invocation must be boolean")
    return issues


def check_relative_links(root: Path, rel: str, text: str) -> list[str]:
    issues: list[str] = []
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if "$" in target or "{" in target:
            continue
        destination = (root / rel).parent / target
        if not destination.exists():
            issues.append(f"Broken relative Markdown link in {rel}: {target}")
    return issues


def check(root: Path, strict_license: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        cached, untracked = git_file_sets(root)
        index_modes = git_index_modes(root)
        staged_paths = git_staged_paths(root)
    except RuntimeError as exc:
        return [str(exc)], warnings

    relative = cached | untracked
    for required in sorted(REQUIRED_FILES - relative):
        errors.append(f"Missing public file: {required}")

    licenses = sorted(
        name
        for name in relative
        if len(Path(name).parts) == 1
        and (Path(name).name == "LICENSE" or Path(name).name.startswith("LICENSE."))
    )
    if not licenses:
        message = "No LICENSE file; source-visible is not open source until the maintainer chooses a license"
        (errors if strict_license else warnings).append(message)

    for rel in sorted(relative):
        path = Path(rel)
        worktree_path = root / rel
        if not allowed_layout(rel):
            errors.append(f"File is outside the public allowlist: {rel}")
        if index_modes.get(rel) == "120000":
            errors.append(f"Symlinks are not allowed in the Git index: {rel}")
        if worktree_path.is_symlink():
            errors.append(f"Symlinks are not allowed in the public package: {rel}")
        if path.name == "SKILL.md" and rel != "SKILL.md":
            errors.append(f"Child Skill must not be published in the core repository: {rel}")
        if path.name in FORBIDDEN_NAMES or path.suffix in {".pyc", ".bak", ".tmp", ".log"}:
            errors.append(f"Local/generated file would be published: {rel}")
        if ".bak." in path.name or "__pycache__" in path.parts:
            errors.append(f"Backup/cache file would be published: {rel}")

        for origin, data in content_variants(root, rel, rel in cached):
            if path.suffix.lower() == ".png":
                errors.extend(check_png(data, rel))
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = data.decode("utf-8", errors="replace")
            for label, pattern in SENSITIVE_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"Possible {label} in {origin} version of {rel}")
            if path.suffix == ".md" and (origin == "worktree" or rel in staged_paths):
                errors.extend(check_relative_links(root, rel, text))

    for license_name in licenses:
        for origin, data in content_variants(root, license_name, license_name in cached):
            text = data.decode("utf-8", errors="replace")
            for marker in (
                "MIT License",
                "Permission is hereby granted, free of charge",
                'THE SOFTWARE IS PROVIDED "AS IS"',
            ):
                if marker not in text:
                    errors.append(f"{origin} version of {license_name} is not a complete MIT license")
                    break

    for origin, data in content_variants(root, "README.md", "README.md" in cached):
        if origin == "index" and "README.md" not in staged_paths:
            continue
        readme = data.decode("utf-8", errors="replace")
        for marker in ("## 仓库边界：子 Skill 动态生成", "## 本地验证", "scripts/run_checks.py"):
            if marker not in readme:
                errors.append(f"{origin} README.md is missing publication marker: {marker}")

    for origin, data in content_variants(root, "SKILL.md", "SKILL.md" in cached):
        if origin == "index" and "SKILL.md" not in staged_paths:
            continue
        skill = data.decode("utf-8", errors="replace")
        for marker in ("references/runtime-workspace.md", "Never use the dao-skill source"):
            if marker not in skill:
                errors.append(f"{origin} SKILL.md is missing runtime boundary marker: {marker}")

    for origin, data in content_variants(
        root, "agents/openai.yaml", "agents/openai.yaml" in cached
    ):
        if origin == "index" and "agents/openai.yaml" not in staged_paths:
            continue
        errors.extend(
            f"{origin} {issue}" for issue in check_metadata(data.decode("utf-8", errors="replace"))
        )

    return sorted(set(errors)), sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check dao-skill's public repository boundary.")
    parser.add_argument("path", nargs="?", default=".", help="Path to dao-skill repository")
    parser.add_argument(
        "--strict-license",
        action="store_true",
        help="Fail instead of warning when LICENSE has not been selected",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    errors, warnings = check(root, args.strict_license)
    for warning in warnings:
        print(f"Warning: {warning}")
    if errors:
        print("Repository check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
