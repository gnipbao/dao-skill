# Usage Verification

Use these prompts after installing `dao-skill` into the local Codex skills directory.

## 1. Explicit Invocation

Prompt:

```md
使用 $dao-skill：我想做一个帮创业者判断产品方向的 skill，先帮我归根。
```

Expected behavior:

- The skill enters Mode A: 归根.
- It outputs 道、一、二、三.
- It does not immediately write files.
- It asks at most one high-leverage question or gives a smallest next step.

## 2. Trigger Phrase

Prompt:

```md
道.skill：我想把王阳明心学变成一个能指导创业判断的 skill。
```

Expected behavior:

- The skill recognizes this as a Nuwa-style candidate.
- It first identifies the root problem.
- It explains the tension between preserving the original thought and making it operational.
- It proposes a skill shape instead of giving a lecture on Wang Yangming.

## 3. Generation Mode

Prompt:

```md
使用 $dao-skill：直接开始，帮我生成一个学习教练 skill 的第一版 SKILL.md。
```

Expected behavior:

- The skill enters Mode C: 生成.
- It does not continue asking questions.
- It resolves a user-owned target such as `.dao/skills/learning-coach/` instead of creating a child folder inside the dao-skill repository.
- It creates a repository-ready `SKILL.md` there when the path is writable.
- It includes trigger description, workflow, boundaries, and quality checks.

## 4. Direct Installation Boundary

Prompt:

```md
使用 $dao-skill：生成完成后直接安装到我的 Codex skills 目录。
```

Expected behavior:

- The skill resolves `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/`.
- It states the target and requests filesystem approval when required.
- It does not write into `dao-skill/`, commit files, create a remote repository, or push changes.
- It reports the target, validation result, unperformed external actions, and rollback point.

## 5. Evaluation Mode

Prompt:

```md
使用 $dao-skill：评估这个 skill 能不能发布，并给出分数。
```

Expected behavior:

- The skill enters Mode D: 评估.
- It declares evidence level and runs the Trust Gate before the 100-point rubric.
- It constrains the verdict by evidence and Trust, then gives P0/P1/P2 fixes.
- It avoids vague praise.

## 6. Composition/Routing

Prompt:

```md
道.skill：我想做一个类似女娲.skill 和同事.skill 的上层系统，能生成很多组织能力 skill。
```

Expected behavior:

- The skill stays in Dao mode first.
- It distinguishes root-finding from Nuwa-style distillation and Colleague-style replication.
- It proposes a skill family architecture instead of one oversized skill.

## 7. Optimize An Existing Skill

Prompt:

```md
使用 $dao-skill：把当前 skill 优化到最好的版本，直接修改文件并验证。
```

Expected behavior:

- The skill enters Mode D before Mode C because no concrete failed output was supplied.
- It defines “better” from the declared scope and captures a validation baseline before editing.
- It patches the highest-leverage P0/P1 gaps while preserving existing success behavior and unrelated changes.
- It separates deterministic structural checks from real prompt replay or independent evidence.
- It reports residual uncertainty instead of claiming an absolute or benchmark-level best.
