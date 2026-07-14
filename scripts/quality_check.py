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
    if issues:
        print("Quality check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Quality check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
