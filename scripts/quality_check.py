#!/usr/bin/env python3
"""Lightweight quality checks for Codex skill folders."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from validation_utils import strip_nonsemantic_markdown


REQUIRED_FRONTMATTER = {"name", "description"}
NAME_RE = re.compile(r"^[a-z0-9-]+$")
CATALOG_HEADING_RE = re.compile(
    r"^#{2,6}\s+.*(公式|模板|套路|句式|formula|template|catalog)", re.IGNORECASE
)
CATALOG_ITEM_RE = re.compile(r"^\s*(\d+[.)、]|[-*+]\s|\|)")
SELECTION_MARKER_RE = re.compile(
    r"适用|不适用|禁用|选用|选择|诊断|排除|fit signal|when to use|select|exclude|diagnos",
    re.IGNORECASE,
)
CATALOG_MIN_ITEMS = 8


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    closing_line = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.rstrip("\r\n") == "---"),
        None,
    )
    if closing_line is None:
        raise ValueError("SKILL.md frontmatter is not closed")
    raw = "".join(lines[1:closing_line]).strip()
    body = "".join(lines[closing_line + 1 :])
    data: dict[str, str] = {}
    current_key: str | None = None
    block_lines: list[str] = []

    def store(key: str, value: str) -> None:
        if key in data:
            raise ValueError(f"Duplicate frontmatter field: {key}")
        data[key] = value

    for line in raw.splitlines():
        if current_key and (line.startswith(" ") or line.startswith("\t")):
            block_lines.append(line.strip())
            continue
        if current_key:
            store(current_key, "\n".join(block_lines).strip())
            current_key = None
            block_lines = []
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid frontmatter line: {line}")
        value = value.strip()
        if value in {"|", ">"}:
            if key in data:
                raise ValueError(f"Duplicate frontmatter field: {key}")
            current_key = key
            block_lines = []
        else:
            store(key, value.strip('"').strip("'"))
    if current_key:
        store(current_key, "\n".join(block_lines).strip())
    return data, body


def markdown_headings(body: str) -> set[str]:
    return {
        match.group(1).strip()
        for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", body, flags=re.MULTILINE)
    }


def has_any_heading(headings: set[str], candidates: list[str]) -> bool:
    normalized = [candidate.lstrip("#").strip() for candidate in candidates]
    return any(
        heading == candidate or heading.startswith(f"{candidate} ")
        for heading in headings
        for candidate in normalized
    )


def check_skill(path: Path, profile: str = "generic") -> list[str]:
    issues: list[str] = []
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return ["Missing SKILL.md"]

    try:
        frontmatter, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [str(exc)]

    missing = REQUIRED_FRONTMATTER - set(frontmatter)
    if missing:
        issues.append(f"Missing frontmatter field(s): {', '.join(sorted(missing))}")
    extra = set(frontmatter) - REQUIRED_FRONTMATTER
    if extra:
        issues.append(f"Unexpected frontmatter field(s): {', '.join(sorted(extra))}")

    name = frontmatter.get("name", "").strip()
    if not name:
        issues.append("Skill name must not be empty")
    if name and not NAME_RE.match(name):
        issues.append("Skill name must use lowercase hyphen-case")
    if name and (name.startswith("-") or name.endswith("-") or "--" in name):
        issues.append("Skill name must not start or end with a hyphen or contain consecutive hyphens")
    if len(name) > 64:
        issues.append("Skill name must be 64 characters or fewer")

    description = frontmatter.get("description", "").strip()
    if len(description) < 80:
        issues.append("Description should be specific enough to trigger the skill")
    if len(description) > 1024:
        issues.append("Description must be 1024 characters or fewer")
    if "<" in description or ">" in description:
        issues.append("Description must not contain angle brackets")

    if not body.strip():
        issues.append("SKILL.md body must not be empty")
    if len(body.splitlines()) > 500:
        issues.append("SKILL.md body must be 500 lines or fewer; move details into linked references")

    semantic_body = strip_nonsemantic_markdown(body)
    headings = markdown_headings(semantic_body)
    section_groups = {
        "workflow/process": [
            "## Core Workflow",
            "## Workflow",
            "## Process",
            "## 工作流程",
            "## 执行流程",
            "## 诊断流程",
            "## 审计流程",
            "Phase 1",
            "Step 1",
            "### Phase",
        ],
        "boundaries/anti-patterns": [
            "## Anti-Patterns",
            "## Boundaries",
            "## 边界",
            "## 反模式",
            "## 绝不做的事",
            "## 特别警告",
            "Do not",
            "Never",
            "不要",
            "绝对不要",
            "超出能力",
        ],
        "quality/validation": [
            "## Quality Standard",
            "## Quality Gate",
            "## 质量",
            "## 验证",
            "## 质量标准",
            "## 通过标准",
            "质量验证",
            "通过标准",
            "Checklist",
            "checklist",
            "feedback loop",
            "regression test",
            "输出模板",
            "诊断报告",
            "信息充分性",
            "回顾",
            "判定",
            "判断",
            "必须拿到",
        ],
    }
    if profile == "dao":
        section_groups["mode/routing"] = [
            "## Mode Router",
            "## Operating Modes",
            "## Routing",
            "## 路由",
            "## 模式",
        ]
    for label, candidates in section_groups.items():
        if not has_any_heading(headings, candidates):
            issues.append(f"Missing section group: {label}")

    references_dir = path / "references"
    if references_dir.exists():
        for ref in sorted(references_dir.rglob("*.md")):
            marker = f"`{ref.relative_to(path).as_posix()}`"
            if marker not in semantic_body:
                issues.append(f"Reference not linked from SKILL.md: {ref.relative_to(path)}")

    public_markdown = [
        path / "README.md",
        path / "CONTRIBUTING.md",
        path / "SECURITY.md",
        skill_md,
        *sorted((path / "references").rglob("*.md")),
        *sorted((path / "examples").glob("*.md")),
    ]
    for markdown in public_markdown:
        if not markdown.is_file():
            continue
        text = markdown.read_text(encoding="utf-8")
        if text.count("```") % 2 != 0:
            issues.append(f"Unbalanced fenced code block in {markdown.relative_to(path)}")

    return issues


def catalog_selection_warning(body: str) -> str | None:
    """Flag a formula/template catalog that has no visible selection rule."""

    semantic_body = strip_nonsemantic_markdown(body)
    if SELECTION_MARKER_RE.search(semantic_body):
        return None
    lines = semantic_body.splitlines()
    for index, line in enumerate(lines):
        if not CATALOG_HEADING_RE.match(line):
            continue
        items = 0
        for following in lines[index + 1 :]:
            if re.match(r"^#{1,6}\s", following):
                break
            if CATALOG_ITEM_RE.match(following):
                items += 1
        if items >= CATALOG_MIN_ITEMS:
            return (
                f"Catalog section '{line.lstrip('#').strip()}' lists {items} entries but the "
                "Skill defines no selection rule (fit signals, exclusions, or input diagnosis); "
                "see the formula/template item in references/skill-generation-template.md."
            )
    return None


def skill_warnings(path: Path) -> list[str]:
    try:
        _, body = parse_frontmatter((path / "SKILL.md").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return []
    warning = catalog_selection_warning(body)
    return [warning] if warning else []


def dao_skill_ancestor(path: Path) -> Path | None:
    for parent in path.parents:
        skill_md = parent / "SKILL.md"
        if not skill_md.is_file():
            continue
        try:
            frontmatter, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        if frontmatter.get("name") == "dao-skill":
            return parent
    return None


def engine_nesting(path: Path) -> tuple[str, str] | None:
    """Classify a child Skill target that sits inside a dao-skill engine."""

    engine = dao_skill_ancestor(path)
    if engine is None:
        return None
    if (engine / ".git").exists():
        return (
            "warning",
            f"Target is inside the dao-skill source {engine}; it stays unpublished local "
            "workspace. Prefer $DAO_SKILL_HOME/skills/<name>/ or a sibling of the source.",
        )
    return (
        "error",
        f"Target is inside the installed dao-skill {engine}; the next install replaces it. "
        "Move it to <project>/.dao/skills/<name>/ or $DAO_SKILL_HOME/skills/<name>/.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a Codex skill folder.")
    parser.add_argument("path", nargs="?", default=".", help="Path to skill folder")
    parser.add_argument(
        "--profile",
        choices=("generic", "dao"),
        default="generic",
        help="validation profile; dao adds meta-skill routing requirements",
    )
    args = parser.parse_args()

    path = Path(args.path).resolve()
    issues = check_skill(path, args.profile)
    nesting = engine_nesting(path)
    if nesting is not None:
        level, message = nesting
        if level == "error":
            issues.append(message)
        else:
            print(f"Warning: {message}")
    for warning in skill_warnings(path):
        print(f"Warning: {warning}")
    if issues:
        print("Quality check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Quality check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
