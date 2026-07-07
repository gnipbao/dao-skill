# Skill Generation Template

Use this reference when generating a concrete skill, skill family, or repository scaffold.

## Skill Design Brief

```md
## 一句话定位

## 用户与场景

## 根问题

## 第一性原理

## 核心张力

## 三才结构
### 天
### 地
### 人

## 生产模式
skill 类型：
为什么不是更简单的类型：
资源层：
验证闭环：

## 运行流程

## 输入格式

## 输出格式

## 边界与反模式

## 质量标准
```

## Recommended Repository Shape

For a pure Codex skill:

```txt
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── ...
├── examples/
│   └── ...
└── scripts/
    └── optional-helper.py
```

Add `README.md` only when the skill is also a public GitHub repository and needs human-facing documentation.

For a skill family or production-grade repository:

```txt
repo-name/
├── README.md
├── skills/
│   ├── router-skill/
│   │   └── SKILL.md
│   └── focused-subskill/
│       ├── SKILL.md
│       └── references/
├── references/ or knowledge-base/
├── examples/
├── scripts/
└── tools/ or packaging metadata
```

Use this larger shape only when the root problem requires routing, shared knowledge, state, or multiple workflows.

## SKILL.md Skeleton

```md
---
name: skill-name
description: Clear explanation of what the skill does and when to use it. Include concrete trigger contexts and phrases here because only this metadata is available before the skill triggers.
---

# Skill Title

## Overview

State the job of the skill in 1-3 sentences.

## Resource Guide

Tell the agent when to load each reference or script.

## Workflow

Give stable steps. Each step should produce or decide something.

## Output Protocols

Define shapes for common outputs.

For image-generation skills, explicitly separate:

- direct generation mode: which image tool/model to call, with required settings
- prompt-only mode: when to stop at a reusable prompt
- platform constraints: fixed aspect ratio, safe areas, text policy, and regeneration rules
- forbidden detours: scripts, renderers, or post-processing steps that are not needed for the user's requested tool

## Boundaries

State what the skill should not do.

## Quality Standard

List checks for a good result.
```

## Example Trigger Description Pattern

```yaml
description: Creates and evaluates X by doing Y. Use when the user asks for A, B, C, or says "trigger phrase 1", "trigger phrase 2". Also use when the user provides Z and wants it converted into a reusable Codex skill.
```

## Generation Sequence

1. Write `SKILL.md` first.
2. For nontrivial skills, classify the production pattern using `production-skill-patterns.md`.
3. Move detailed frameworks, examples, and rubrics into references.
4. Add examples or retest prompts that show realistic use.
5. Add scripts only for repeatable mechanical checks.
6. Validate the skill.
7. Forward-test with realistic prompts when practical.

## Generated Skill Checklist

- The frontmatter has only `name` and `description` unless there is a clear platform reason.
- The description says when to use the skill.
- The body is concise enough to load.
- References are linked directly from `SKILL.md`.
- The workflow makes decisions, not just observations.
- The skill knows when to stop, route, or ask.
- The output is copyable or actionable.
- Tool-coupled skills name the actual tool path and required settings instead of implying a generic workflow.
- Image skills lock platform-critical aspect ratios in the workflow, prompt template, and QA checklist.
- The production pattern matches the real task.
- The verification loop is explicit enough to catch drift.
