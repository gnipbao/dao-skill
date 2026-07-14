# Dao Evolution Protocol

Use this when a generated skill fails, the user reports a mismatch, or dao-skill needs to improve itself.

## Core Principle

Every failure is a question about the root, not only about the artifact.

Do not stop at:

> Add more fields to the generated skill.

Ask:

> Why did dao-skill fail to predict that those fields were essential?

Experience is not memory until it changes future behavior. Treat feedback, traces, external methods, and user corrections as evidence that must become a rule, reference, rubric, example, script, or validation check before calling it learning.

## Evolution Run Contract

An evolution run is valid only when it produces all five artifacts below:

1. Evidence packet: what happened, where it happened, and what signal proves it matters.
2. Asset retrieval: the nearest existing rule, reference, example, script, child skill, or rubric item.
3. Asset decision: `create`, `merge`, or `discard`.
4. Retest prompt: a prompt or fixture that exposes the old failure.
5. Validation and deployment: pass/fail signal, preserved invariants, deployment status (`accepted`, `provisional`, `quarantined`, or `rejected`), and rollback or quarantine condition.

If any artifact is missing, label the run `provisional` and do not claim that dao-skill has learned.

## CHECKPOINT / STOP Gates

Explicit authorization already granted for the named repository, installation, or deployment scope does not require a second confirmation. Local reversible patching and retesting may proceed within that scope.

Stop for human review before an unauthorized deployment or scope expansion when:

- the evidence is weak but the patch would affect many future generated skills
- the patch changes trigger routing, safety boundaries, or output schemas
- the nearest existing asset is unclear after retrieval
- validation is only dry-run and the task has high stakes
- the update conflicts with a stronger existing rule

For low-risk wording, examples, or retest prompts, proceed and report the validation result.

## Evolution Workflow

### 0. Interactive Feedback Intake

The user should not need to memorize a feedback template. If feedback is vague, dao-skill must guide the user into useful evidence.

When the user says things like "不好用", "不对", "太泛", "没有解决", or "这不是我要的":

1. Restate the suspected mismatch in one sentence.
2. Ask at most two short questions.
3. Ask only for information that changes the root diagnosis.
4. Use the user's answers to fill the evolution fields yourself.
5. If the user does not answer every question, proceed with a provisional diagnosis and mark uncertainty.

Default question set:

```md
我先帮你把反馈变成可进化证据。你简单回答这 2 个就行：

1. 哪个 skill 或输出不好用，它实际哪里让你卡住？
2. 你希望它下次怎么做才算好用？
```

If the user already gave the failed object, ask only:

```md
它实际哪里卡住了？你希望下次变成什么样？
```

If the user already gave actual and desired behavior, do not ask more. Continue to the postmortem.

Do not dump a long form unless the user asks for one. The job of dao-skill is to turn messy feedback into structured evolution evidence.

### 1. Build The Evidence Packet

Write the user's feedback as concrete failure signals. If there is an execution trace, preserve the causal chain rather than only the final complaint.

```md
用户原话：
失败对象：
失败发生在哪一步：
用户真正无法完成什么：
触发 prompt：
被调用的 skill / rule：
关键动作或工具：
产出物路径：
实际结果：
期望结果：
证据强度：strong / medium / weak
不确定点：
```

### 2. Reopen The Root

Compare the original root problem with the tested reality.

```md
原始根问题：
真实根问题：
差异：
```

Common shifts:

- from "generate a skill" to "generate a skill that survives real outputs"
- from "create prompt" to "create a control system"
- from "describe a workflow" to "diagnose drift and iterate"
- from "safe boundary" to "usable safe vocabulary"

### 3. Identify Missing Control Dimensions

A skill often fails because a necessary dimension stayed implicit.

Common missing dimensions:

- success metric: what counts as solved
- control hierarchy: which fields dominate output quality
- failure diagnosis: what to do when the result drifts
- domain vocabulary: safe but useful words
- tool coupling: which tools/settings are required
- aesthetic judgment: how to improve taste without losing fidelity
- evolution loop: how feedback changes future behavior
- candidate management: whether new evidence should create, merge into, or discard a skill/rule
- validation gate: how to prove the update improves behavior without breaking existing invariants
- rollback path: what to do if the update causes drift, over-triggering, or lower quality

### 4. Retrieve The Nearest Existing Asset

Before writing anything, locate the nearest existing home for the learning:

```md
候选学习：
最近已有资产：
相似原因：
差异：
资产决策：create / merge / discard
部署状态：accepted / provisional / quarantined / rejected
为什么不是新建：
为什么不是只改当前 child skill：
```

Use `create` only when no existing asset owns the trigger, root problem, or behavior. Use deployment status `quarantined` when the evidence may matter later but is not trustworthy enough to become an active rule.

### 5. Convert Learning Into A Patch

Learning must become one or more concrete changes:

- new trigger phrase
- new mode
- new workflow step
- new output field
- new reference file
- new example
- new rubric item
- new validation check

Before adding a new skill, rule, or reference, retrieve the nearest existing home and decide:

- Create: the evidence reveals a new reusable capability.
- Merge: the evidence refines an existing capability with a new constraint, failure mode, or example.
- Discard: the evidence is one-off, duplicate, unverified, or not behavior-changing.

Prefer merge over create when the root problem and trigger are the same. This avoids skill-bank bloat.

### 6. Write A Retest Prompt

Every evolution should include a prompt that would have exposed the old failure.

```md
反测 prompt：
旧版本可能失败方式：
新版本应该表现：
```

### 7. Preserve Invariants And Patch Conservatively

When evidence includes both success and failure, success traces define invariants and failure traces define targets.

Conservative patch rules:

- preserve working triggers, identifiers, output schemas, tool names, and stable constraints
- change the smallest instruction that would alter future behavior
- keep source-specific claims in references instead of global rules
- distinguish skill defects from agent noncompliance; if the instruction was already correct, improve retrieval, routing, or compliance checks instead
- do not deploy an evolution without a pass/fail signal or rollback condition proportional to risk

### 8. Validate And Decide

Validation must compare the new behavior against the old failure and preserved success cases.

```md
结构检查：
行为反测：
旧版失败：
新版表现：
保留的不变量：
独立评估：full_test / independent_judge / old_vs_new / dry_run
通过标准：
失败处理：rollback / quarantine / revise
```

Use `dry_run` only when real execution or independent judging is unavailable. Do not treat dry-run evidence as benchmark-level proof.

## Evolution Output

```md
## 道.skill 返观
用户反馈：
交互式追问：
表层失败：
根因失败：
v1 学到什么：
v2 学到什么：
dao-skill 自身缺口：
新增规则：
资产决策：create / merge / discard
部署状态：accepted / provisional / quarantined / rejected
文件更新计划：
验证方式：
回滚条件：
```

## Case Pattern: Child Skill Misses The Need

If a child skill fails:

1. Review the child skill's root problem.
2. Review dao-skill's generation decision.
3. Separate child-skill flaws from dao-skill flaws.
4. Retrieve the nearest dao-skill rule that should have prevented the miss.
5. Update the child skill for the concrete domain.
6. Update dao-skill so future child skills include the missing design dimension earlier.
7. Add a retest prompt that fails on the old generation pattern.

## Anti-Patterns

- Symptom patching: adding fields without changing the root design.
- Local-only learning: fixing one skill but not dao-skill.
- Vague learning: saying "be more precise" without a checklist.
- Template burden: making the user remember a long feedback format before dao-skill can learn.
- Over-expansion: adding a universal module when a mode or reference would do.
- False certainty: claiming the evolved skill will now solve everything.
- No retrieval before creation: adding a new rule or skill without checking the nearest existing home.
- No rollback: deploying a patch without a condition for reverting or quarantining it.
- Dry-run inflation: presenting simulated validation as if it were independent proof.
