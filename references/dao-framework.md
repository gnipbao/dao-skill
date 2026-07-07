# Dao Framework

Use this reference when a user asks for deep grounding, philosophical framing, or the full method behind Dao skill.

## Core Thesis

A good skill does not begin from features. It begins from the root problem that makes the skill necessary.

Dao skill translates "道生一，一生二，二生三，三生万物" into an engineering workflow:

1. 道: receive ambiguous intent without flattening it too soon.
2. 一: find the single root problem.
3. 二: name the central productive tension.
4. 三: create a stable operating structure.
5. 万物: generate concrete files, workflows, or skill systems.
6. 返观: learn from the artifact when real feedback shows the root was incomplete.

## 道: The Original Chaos

The user's first expression may be:

- an inspiration
- a feature request
- a pain point
- a philosophical metaphor
- a desire to create "something"
- a reference to an existing skill

The task is to hold the ambiguity long enough to extract its shape.

Useful output:

```md
## 道：原始混沌
用户表层表达：
用户可能真正关心：
当前不确定点：
是否需要追问：是/否
```

Only ask if the answer changes the next design move.

## 一: The Root

The root problem should be deeper than the surface request and operational enough to guide design.

Good root problem:

> 用户不是要一个提示词集合，而是要一种可重复的判断流程，把模糊创作意图变成稳定产物。

Weak root problem:

> 用户想做一个创作 skill。

Checklist:

- Is it a problem, not a feature?
- Can it explain why the skill should exist?
- Does it rule out some tempting but wrong designs?
- Can success be tested?

## 二: The Tension

Every meaningful skill carries tension. The design should govern the tension rather than pretend it does not exist.

Examples:

| Tension | Failure If One-Sided | Design Rule |
| --- | --- | --- |
| 抽象 vs 落地 | Only slogans or only tools | Each concept must produce a workflow choice |
| 自由 vs 结构 | Random output or rigid templates | Use stable stages with flexible contents |
| 哲学 vs 工程 | Mysticism or sterile mechanics | Explain principles only when they change execution |
| 人味 vs 可验证 | Pretty but unreliable output | Keep voice, add checks |
| 快速 vs 深度 | Shallow answers or paralysis | Use mode selection |

## 三: Heaven, Earth, Human

Use this as the standard architecture for a skill:

### 天: Principle Layer

Define what the skill believes and refuses to violate.

Examples:

- Start from root problems, not feature lists.
- Prefer useful boundaries over universal claims.
- Make hidden assumptions explicit.

### 地: Scenario Layer

Define fit, boundaries, routing, and non-use cases.

Examples:

- Fit: create a new skill, evaluate an existing skill, design a skill family.
- Route: Nuwa-style for cognitive/persona distillation, Colleague-style for real coworker replication.
- Non-fit: professional facts requiring external verification without sources.

### 人: Interaction Layer

Define how the skill behaves in conversation.

Examples:

- Ask no more than two questions before making progress.
- If the user says "start", generate files.
- Keep evaluation concrete and scored.

## 万物: Artifact Generation

Only generate after the root, tension, and structure are clear enough.

Artifact choices:

- A single skill when the root problem is bounded.
- A skill family when the root problem spans multiple roles or workflows.
- A composition plan when existing skills already cover parts of the work.
- An evaluation when the artifact already exists.
- A roadmap when the skill needs staged evolution.

## 返观: Feedback-Driven Evolution

Generation is not the end. A skill becomes real only when it meets use.

Use 返观 when:

- the user says the generated skill missed the point
- a generated prompt or workflow fails in practice
- version 1 and version 2 improved symptoms but still missed the root
- the user asks dao-skill to improve itself

The task is to go one layer deeper than the fix:

```md
## 返观：进化复盘
原始根问题：
当时的版本假设：
失败信号：
更深一层的根因：
缺失的控制维度：
新原则：
应更新的文件：
反测 prompt：
```

Good evolution changes one of these:

- trigger description
- workflow step
- output protocol
- reference document
- example
- rubric
- validation script

Bad evolution only says "next time pay attention."

## Failure Modes

- Treating Dao as authority instead of inquiry.
- Writing poetic language that does not affect behavior.
- Generating a huge skill from a vague prompt.
- Naming many concepts but producing no file.
- Ignoring the user's existing examples and desired lineage.
- Treating feedback as a child-skill bug when it reveals a dao-skill design bug.
