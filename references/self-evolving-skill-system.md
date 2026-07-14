# Self-Evolving Skill System

Use this reference when dao-skill must absorb an external method, article, paper, skill, feedback stream, or execution traces into a durable skill system.

The goal is not to remember more. The goal is to turn evidence into a compact, retrievable, versioned, validated control system.

## Source Pattern

This protocol was added after studying the user-provided article:

- Title: 【Agent Skills洞察与实践】08- 如何实现Skills的自进化
- Author: 王磊
- User-provided date shown in excerpt: 2026-05-25
- Evidence boundary: the article summary was pasted by the user; treat it as a secondary synthesis unless the linked papers or repositories are separately inspected.

The article synthesizes four self-evolution patterns:

- SkillRL: distill successful and failed trajectories into hierarchical SkillBank entries and recursively evolve them.
- AutoSkill: turn repeated interaction experience into explicit, versioned `SKILL.md` artifacts with retrieve-assisted add/merge/drop management.
- MemSkill: evolve memory operations as skills, maintain hard-case buffers, and roll back updates that reduce performance.
- SkillClaw: collect causal execution traces, group them by skill, conservatively refine/create/skip, and deploy only after validation beats the previous version.

## First Principle

Experience is not memory until it changes future behavior.

A self-evolving skill system must convert raw evidence into:

```txt
evidence -> candidate skill/rule -> similar-skill retrieval -> create/merge/discard -> versioned patch -> validation -> deployment or rollback
```

Do not call an update "learning" unless at least one durable asset changes:

- trigger or routing rule
- workflow step
- reference protocol
- rubric item
- example or retest prompt
- script or deterministic guardrail
- skill metadata, version, or deprecation status

## Agent-Level Evolution Machine

To reach runtime-agent quality, the system must separate fast user-facing execution from slower background evolution.

```txt
execution path: retrieve skill -> perform task -> capture trace -> return useful result
evolution path: batch traces -> extract candidates -> retrieve similar assets -> patch -> validate -> deploy/quarantine
```

Never block a user's urgent task just to perform speculative evolution. Capture enough evidence during the task, then evolve after the artifact exists or after the user gives a clear failure/success signal.

## Trace Packet

Every serious evolution starts from a trace packet. Do not store raw transcripts as the primary memory unit; compress them into this schema:

```md
trace_id:
timestamp_or_session:
user_goal:
trigger_prompt:
selected_skills:
retrieved_references:
actions_and_tools:
artifacts_created_or_changed:
observed_result:
user_signal:
success_invariants:
failure_targets:
suspected_root_miss:
candidate_learning:
privacy_or_source_boundary:
risk_level: low / medium / high
```

If only a short user complaint is available, create a partial packet and mark missing fields as unknown. A partial packet can drive a provisional patch, but not a benchmark claim.

## Evidence Intake

Classify the evidence before extracting anything.

```md
证据类型：
来源边界：
是否一手来源：
是否包含成功轨迹：
是否包含失败轨迹：
是否包含工具调用或环境反馈：
可复用性：
风险：
```

Evidence classes:

- User preference: repeated stable requirement, such as tone, formatting, safety boundary, or output policy.
- Success trace: an execution that worked; use it to extract invariants that should be preserved.
- Failure trace: an execution that failed; use it to extract target defects and retest prompts.
- External method: an article, paper, repository, or skill; use it as a candidate mechanism, not as universal truth.
- Uncovered pattern: repeated successful work that used no skill; consider creating a new skill only if future recurrence is likely.

Reject or quarantine:

- one-off requests
- vague taste comments with no future trigger
- raw transcripts without a clear behavior change
- claims that require verification before they affect real workflows
- duplicate candidates that should merge into existing skills

## Evolution Ledger

Each accepted, rejected, or quarantined update should be recordable in a simple ledger. Use this shape for a local `evolution-log.tsv`, changelog entry, or final response table:

```tsv
timestamp	asset	old_version	new_version	decision	evidence	pass_signal	rollback_condition	status
```

Status values:

- `accepted`: validation passed and the update is active
- `rejected`: validation failed and the update was not kept
- `quarantined`: evidence may matter, but is not trustworthy or broad enough yet
- `provisional`: only dry-run validation exists

Do not mix rejected evidence into global rules or quarantine. Keep it only in the audit ledger; use `quarantined` for evidence that remains plausible but is not deployable yet.

## SkillBank Structure

A self-evolving SkillBank needs at least two layers.

```txt
SkillBank
├── general-principles
│   ├── cross-task heuristics
│   ├── shared failure patterns
│   └── routing and verification rules
└── task-specific-skills
    ├── task category
    ├── trigger conditions
    ├── workflow
    ├── constraints
    ├── failure modes
    └── retest prompts
```

Minimal skill fields:

```md
名称：
一句话描述：
适用条件：
不适用条件：
核心原则：
执行流程：
验证信号：
失败模式：
版本：
来源：
最近一次进化：
```

For large banks, retrieval should combine:

- semantic similarity for meaning
- lexical/BM25-style matching for exact terms, tool names, APIs, and file paths
- thresholding so irrelevant skills are not injected
- top-k limits so context does not swell

## Candidate Lifecycle

Every candidate update must pass this lifecycle.

### 1. Extract

From evidence, extract a reusable candidate:

```md
候选名称：
来源证据：
解决的问题：
适用触发：
可迁移机制：
具体约束：
验证信号：
旧系统缺口：
```

Use successful traces to define invariants:

- which steps consistently worked
- which constraints must not be loosened
- which outputs users accepted
- which tool order or parameters proved stable

Use failed traces to define targets:

- which step failed
- which assumption was wrong
- which missing check would have caught it
- which retest prompt exposes the failure

### 2. Retrieve Similar

Before adding anything, retrieve the nearest existing skill, rule, reference, or rubric item.

Ask:

- Is this truly new, or a refinement of an existing capability?
- Does it belong in a child skill, dao-skill, a reference file, an example, or a validation script?
- Would adding it create duplicate routing?
- Can the same behavior be achieved by tightening retrieval or compliance rather than changing the skill?

Retrieval minimum:

```md
搜索词：
命中资产：
为什么相似：
为什么不足：
放置位置：
```

If retrieval finds an existing rule that the agent ignored, do not rewrite the rule first. Add a compliance check, routing reminder, or retest prompt that forces retrieval and use.

### 3. Decide

Use three decisions:

- Create: new reusable capability, no good existing home, likely to recur.
- Merge: same capability with new constraints, failure modes, or examples.
- Discard: one-off, duplicate, unverified, too narrow, or not behavior-changing.

Prefer merge over create when the root problem and trigger are the same.

Keep asset decisions separate from deployment status:

- asset decision: `create`, `merge`, or `discard`
- deployment status: `accepted`, `provisional`, `quarantined`, or `rejected`

### 4. Patch Conservatively

Conservative editing rules:

- Preserve stable identifiers and triggers unless evidence shows they are wrong.
- Add the smallest rule that changes future behavior.
- Keep source-specific claims in references, not in global instructions.
- Do not change API details, paths, tool names, or output schemas without evidence.
- Separate skill failure from agent noncompliance. If the skill was already correct, add a retrieval, routing, checklist, or compliance check.
- Add a retest prompt whenever the update fixes a failure mode.

### 5. Version

For generated skills and skill banks, track semantic intent:

- patch version: tighter wording, examples, small guardrail
- minor version: new workflow branch, trigger, or validation loop
- major version: root problem, artifact type, or routing contract changed

For dao-skill itself, record the version intent in the final response or changelog when a formal version file exists.

### 6. Validate

Validation should compare the new behavior against the old failure or risk.

Options:

- quality checker for structure
- dry-run prompt for routing and output protocol
- fixture replay for deterministic workflows
- old-vs-new comparison for generated artifacts
- source audit for external claims
- regression prompt for a previous failure

Accept the patch only if it improves the relevant pass/fail signal without breaking preserved invariants.

### Validation Matrix

Choose the validation strength by risk:

| Risk | Required checks | Pass signal | Deployment |
|---|---|---|---|
| Low: wording, example, small trigger | structure check + retest dry-run | old failure is explicitly handled | accept or mark provisional |
| Medium: workflow branch, reference protocol, generated skill pattern | structure check + old-vs-new behavior comparison + one regression prompt | new behavior fixes failure and preserves an old success invariant | accept after reporting rollback condition |
| High: router behavior, safety boundary, SkillBank lifecycle, broad generation policy | structure check + independent judge or full test + old-vs-new + human checkpoint when deployment was not already authorized | at least one external signal agrees and no preserved invariant breaks | deploy only after required validation and authorization |

When independent judges or full tests are unavailable, label the update `provisional` and keep the rollback condition visible.

### 7. Roll Back Or Quarantine

Do not keep an evolution that makes the system worse.

Roll back or quarantine when:

- the new rule causes over-triggering
- generated skills become larger but less actionable
- validation fails
- the change conflicts with stronger existing rules
- the evidence was later found unreliable

Rollback target:

```md
资产：
回滚动作：
触发条件：
保留的证据：
下次需要的新证据：
```

## Autonomous Evolution Loop

Use this loop when designing a self-evolving skill family or repository.

```txt
1. Run tasks with current skills.
2. Capture causal traces: prompt -> selected skills -> actions/tools -> feedback/errors -> final output -> user signal.
3. Group traces by selected skill; keep an uncovered group for tasks that used no skill.
4. Distill success invariants and failure targets.
5. Extract candidate skills/rules.
6. Retrieve nearest existing assets.
7. Decide create/merge/discard.
8. Patch conservatively.
9. Validate against old failures and preserved success cases.
10. Deploy accepted updates, quarantine plausible provisional evidence, and keep rejected evidence only in the audit ledger.
11. Repeat on the next batch.
```

For high-latency or high-volume systems, run evolution asynchronously in the background; keep the user-facing response path focused on retrieval and execution.

## Independent Evaluation

The editor of a rule is not enough to certify the rule.

Use the strongest available option:

1. `full_test`: run the old failure prompt against the evolved skill and inspect the artifact.
2. `independent_judge`: ask a separate agent or reviewer to compare old vs new without knowing which is which.
3. `old_vs_new`: simulate both versions explicitly and compare against the pass signal.
4. `dry_run`: reason through the expected behavior when tools are unavailable.

Record the mode. Do not upgrade `dry_run` to `full_test` language in the final report.

## Deployment Rule

An evolution is deployed only when:

- the changed asset is named
- the evidence packet is summarized
- create/merge/discard asset decision is explicit
- accepted/provisional/quarantined/rejected deployment status is explicit
- validation mode is named
- rollback condition exists
- the next retest prompt is stored or reported

If broad propagation was not already explicitly authorized, stop at CHECKPOINT / STOP before copying the rule into sibling skills. Explicit authorization removes duplicate confirmation, not validation or rollback requirements.

## Output Protocol: Absorption Report

```md
## 道.skill 自化吸收
来源：
证据边界：

### 机制提取
1.
2.
3.

### 候选决策
新增：
合并：
丢弃：
资产决策：create / merge / discard
部署状态：accepted / provisional / quarantined / rejected

### 已落地更新
文件：
规则：
验证：
回滚条件：

### 反测
旧版本可能失败：
新版本应该表现：
```

## Retest Prompts

Use these prompts to test whether dao-skill absorbed this protocol.

```md
研究这篇关于 Agent 技能自进化的文章，并吸收到 dao-skill 里。不要只总结文章，要更新系统规则，并说明新增、合并、丢弃了什么。
```

Expected behavior:

- names the source boundary
- extracts mechanisms instead of copying claims
- updates files when local repo is available
- runs the quality checker
- reports durable changes and retest prompt

```md
这个生成的 skill 上次失败了：它每次都新建一个类似技能，没有合并旧技能。请让 dao-skill 进化。
```

Expected behavior:

- reads `references/evolution-protocol.md` and this file if needed
- diagnoses skill bloat as the root failure
- adds create/merge/discard or similar-skill retrieval rules
- writes a retest prompt that exposes duplicate-skill creation

```md
我们有 100 条 agent 执行轨迹，里面有成功和失败。帮我设计一个自进化 SkillBank。
```

Expected behavior:

- separates evidence intake, trace grouping, SkillBank layers, candidate lifecycle, validation, and rollback
- treats success traces as invariants and failure traces as targets
- does not propose storing all raw traces in prompts
