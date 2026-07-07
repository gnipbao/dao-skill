#!/usr/bin/env python3
"""Lightweight quality checks for Codex skill folders."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FRONTMATTER = {"name", "description"}
NAME_RE = re.compile(r"^[a-z0-9-]+$")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed")
    raw = text[4:end].strip()
    body = text[end + 4 :]
    data: dict[str, str] = {}
    current_key: str | None = None
    block_lines: list[str] = []
    for line in raw.splitlines():
        if current_key and (line.startswith(" ") or line.startswith("\t")):
            block_lines.append(line.strip())
            continue
        if current_key:
            data[current_key] = "\n".join(block_lines).strip()
            current_key = None
            block_lines = []
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {"|", ">"}:
            current_key = key
            block_lines = []
        else:
            data[key] = value.strip('"').strip("'")
    if current_key:
        data[current_key] = "\n".join(block_lines).strip()
    return data, body


def has_any_heading(body: str, candidates: list[str]) -> bool:
    return any(candidate in body for candidate in candidates)


def check_skill(path: Path) -> list[str]:
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

    name = frontmatter.get("name", "")
    if name and not NAME_RE.match(name):
        issues.append("Skill name must use lowercase hyphen-case")
    if len(name) > 64:
        issues.append("Skill name must be 64 characters or fewer")

    description = frontmatter.get("description", "")
    if len(description) < 80:
        issues.append("Description should be specific enough to trigger the skill")
    if len(description) > 1024:
        issues.append("Description must be 1024 characters or fewer")
    if "<" in description or ">" in description:
        issues.append("Description must not contain angle brackets")

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
        "mode/routing": [
            "## Operating Modes",
            "## Routing",
            "## 路由",
            "## 模式",
            "## 特殊场景",
            "模式选择",
            "下一步建议",
            "特殊情况",
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
    for label, candidates in section_groups.items():
        if label == "mode/routing" and len(body.splitlines()) < 180:
            continue
        if not has_any_heading(body, candidates):
            issues.append(f"Missing section group: {label}")

    references_dir = path / "references"
    if references_dir.exists():
        for ref in sorted(references_dir.glob("*.md")):
            marker = f"`references/{ref.name}`"
            if marker not in body:
                issues.append(f"Reference not linked from SKILL.md: references/{ref.name}")

    public_markdown = [
        path / "README.md",
        path / "CONTRIBUTING.md",
        path / "SECURITY.md",
        skill_md,
        *sorted((path / "references").glob("*.md")),
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
    args = parser.parse_args()

    path = Path(args.path).resolve()
    issues = check_skill(path)
    if issues:
        print("Quality check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Quality check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
