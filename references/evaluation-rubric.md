# Evaluation Rubric

Use this reference when reviewing an existing skill, checking generated skill quality, or deciding whether a skill is publishable.

This rubric absorbs the portable strengths of TRACE without treating a platform framework as an absolute judge.

## Source Boundary

- External method: SkillHub, “你用的AI Skill靠谱吗？五大维度帮你快速判断”, published 2026-05-20.
- Source inspected: the full public WeChat article supplied by the user.
- Portable mechanism: evaluate trust, reliability, applicability, convention, and effectiveness as a chain from safe adoption to useful results.
- Not independently verified: SkillHub's claims about its scanner, sandbox, domestic-network tests, or platform operations.
- Integration decision: merge trust into a hard gate; merge reliability, applicability, convention, and effectiveness into dao-skill's evidence-backed score. Preserve dao-skill's root-problem, composition, validation, and evolution criteria.

## Evaluation Contract

Evaluate in this order:

```txt
evaluation mode -> Trust Gate -> 100-point score -> evidence confidence -> verdict -> P0/P1/P2 fixes
```

Do not let excellent writing, architecture, or output quality compensate for a failed trust gate. Do not award execution-level confidence from documentation alone.

## 0. Evaluation Mode And Evidence Level

Declare the strongest evidence actually inspected:

| Level | Evidence | Allowed claim |
|---|---|---|
| E0 declaration | Name, description, or claims only | Orientation only; do not score publishability |
| E1 structural | `SKILL.md`, references, scripts, metadata | Structural score; effectiveness and reliability remain unverified |
| E2 dry run | Representative prompts reasoned through or manually exercised | Provisional behavior score |
| E3 executed | Fixtures, tool runs, regression prompts, old-vs-new replay | Verified behavior for the tested environment |
| E4 independent/operational | Blind judge, independent reviewer, or production traces | Strongest available confidence |

Report both:

```md
评估模式：E0 / E1 / E2 / E3 / E4
评分置信度：低 / 中 / 高
证据缺口：
```

Rules:

- E0 cannot produce a publication verdict.
- E1 may produce a numeric structural estimate, but cannot certify reliability, effectiveness, or benchmark quality.
- E2 can support a publishable candidate verdict when the Trust Gate has no unresolved required item.
- E3 or E4 is required for a verified publishable verdict.
- A 95+ benchmark verdict requires E3 or E4; high-risk skills require E4 or an explicit human checkpoint.

## 1. Trust Gate

Rate each item `PASS`, `CONDITIONAL`, `FAIL`, `UNKNOWN`, or `N/A`, and cite evidence. `N/A` requires a reason.

| Gate | Inspect | Failure examples |
|---|---|---|
| Permission scope | Requested filesystem, network, account, shell, and external-write access is necessary and proportionate | Unrelated broad permissions; destructive action without confirmation |
| Sensitive data | Secrets, personal data, logs, prompts, and uploaded files have explicit handling boundaries | Token leakage; hidden upload; credentials in examples or docs |
| Input and action safety | Untrusted input is delimited or validated; commands and mutations have safeguards | Prompt/command injection path; silent destructive mutation |
| Dependencies and provenance | External tools, scripts, packages, sources, and licenses are disclosed and reproducible | Opaque binary; unpinned risky dependency; unclear source rights |
| Environment fitness | Required runtime, network, language, platform, and regional constraints are stated and tested where relevant | Overseas-only API presented as universally available; undocumented runtime mismatch |

Gate verdict:

- `FAIL`: reject regardless of numeric score.
- `UNKNOWN`: do not claim publishable when the unknown item is required for the skill's real execution path.
- `CONDITIONAL`: name the operating condition and user-visible limitation.
- `PASS`: all required items have evidence and no unresolved critical risk.
- A content-only skill may mark irrelevant runtime items `N/A`, but must explain why.

This is a review gate, not a malware scanner. Static reading cannot prove that code is safe. If sandboxing, dependency scanning, or dynamic execution is unavailable, say so.

## 2. Scorecard

| Dimension | Maximum |
|---|---:|
| 根问题与适用性 | 15 |
| 流程可靠性 | 20 |
| 结果有效性 | 20 |
| 边界与可信披露 | 10 |
| 规范与维护性 | 10 |
| 组合与交接能力 | 10 |
| 证据与验证闭环 | 10 |
| 可进化性 | 5 |
| **总分** | **100** |

Every dimension needs at least one evidence citation: file section, example, test result, execution trace, or observed failure. When evidence is missing, score the demonstrated artifact rather than the author's intention.

### 2.1 根问题与适用性 0-15

- 0-3: repeats a surface request and uses vague triggers.
- 4-7: identifies the domain but not the root change, success condition, or unsuitable use.
- 8-11: names the root problem, success condition, representative inputs, and trigger boundaries.
- 12-15: also defines tradeoffs, non-goals, false-positive/false-negative routing risks, and context-dependent applicability.

### 2.2 流程可靠性 0-20

- 0-5: mostly vibes, advice, or a single unconstrained prompt.
- 6-10: has steps but weak decision rules and failure handling.
- 11-15: repeatable workflow with routing, edge cases, understandable errors, and stop conditions.
- 16-20: representative normal, boundary, and failure cases have been exercised; recovery behavior is consistent and evidenced.

Do not award more than 15 from E1 structural evidence alone.

### 2.3 结果有效性 0-20

- 0-5: output is inspirational, incorrect, incomplete, or not reusable.
- 6-10: has a rough structure but requires substantial user reconstruction.
- 11-15: output is correct enough for its declared scope, practical, and formatted for direct reuse.
- 16-20: tested outputs solve the stated task, cover required fields, improve on a baseline, and need only proportionate review.

Do not award more than 15 without at least E2 evidence. Correct formatting alone is not effectiveness.

### 2.4 边界与可信披露 0-10

- 0-2: makes universal claims or hides important limitations.
- 3-5: mentions limits vaguely.
- 6-8: names non-use cases, uncertainty, human checkpoints, privacy/source limits, and failure behavior.
- 9-10: disclosures are tied to concrete routing, refusal, escalation, or fallback behavior and match the Trust Gate.

### 2.5 规范与维护性 0-10

- 0-2: name, description, parameters, and real behavior conflict.
- 3-5: understandable but poorly organized or overloaded.
- 6-8: progressive disclosure, stable naming, linked references, examples, version notes, and clear setup requirements.
- 9-10: repository is reproducible, validation commands are usable, changes are maintainable, and known incompatibilities are explicit.

### 2.6 组合与交接能力 0-10

- 0-2: isolated or tries to perform every job itself.
- 3-5: names related skills or tools but has vague handoffs.
- 6-8: explicit routing, input/output contracts, state transfer, and conflict rules.
- 9-10: supports skill families, shared resources, bounded orchestration, and graceful fallback when a dependency is unavailable.

### 2.7 证据与验证闭环 0-10

- 0-2: no evaluation path or only self-asserted quality.
- 3-5: examples or dry-run prompts exist but lack pass/fail criteria.
- 6-8: regression prompts, fixtures, source audits, or deterministic checks have explicit pass signals.
- 9-10: old-vs-new or independent evaluation covers success invariants and failure targets, with results recorded.

### 2.8 可进化性 0-5

- 0-1: no improvement path.
- 2-3: feedback can produce prioritized fixes or versioned changes.
- 4-5: evidence becomes a rule, example, rubric, script, or retest; acceptance and rollback conditions are explicit.

## 3. Verdict Rules

Numeric bands describe observed quality, not deployment permission:

- Below 70: do not publish.
- 70-84: MVP; publish only in a clearly limited/test environment.
- 85-94: publishable candidate.
- 95+: benchmark candidate.

Final verdict must combine score, gate, and evidence:

```txt
deployment verdict = numeric band constrained by Trust Gate and evidence level
```

- Trust `FAIL` -> reject.
- Required Trust item `UNKNOWN` -> assessment incomplete; no publishable verdict.
- E0 -> orientation only.
- E1 -> structural estimate only, even when the number is high.
- Score >= 85 + Trust eligible + E2 -> publishable candidate, not verified publishable.
- Score >= 85 + Trust PASS/justified CONDITIONAL + E3/E4 -> verified publishable.
- Score >= 95 + Trust PASS + E3/E4 -> benchmark candidate; high-risk use still needs an independent/human gate.

## 4. Production Readiness Supplement

Report `低 / 中 / 高 / 未验证` for:

```md
生产模式匹配：
资源组织：
安装与维护性：
运行环境适配：
安全检测覆盖：静态审阅 / 依赖扫描 / 沙箱或动态测试 / 未执行
```

These fields explain deployment readiness; they do not add bonus points.

## 5. Review Output

```md
## 道.skill 评估
总分：/100
数值等级：不可发布 / MVP / 可发布候选 / 标杆候选
最终判定：拒绝 / 评估不完整 / 结构估分 / 可发布候选 / 已验证可发布 / 标杆候选
评估模式：E0 / E1 / E2 / E3 / E4
评分置信度：低 / 中 / 高

### Trust Gate
权限范围：PASS / CONDITIONAL / FAIL / UNKNOWN / N/A；证据：
敏感数据：；证据：
输入与动作安全：；证据：
依赖与来源：；证据：
环境适配：；证据：
门禁结论：

### 100 分评分
根问题与适用性：/15；证据：
流程可靠性：/20；证据：
结果有效性：/20；证据：
边界与可信披露：/10；证据：
规范与维护性：/10；证据：
组合与交接能力：/10；证据：
证据与验证闭环：/10；证据：
可进化性：/5；证据：

### 证据缺口与改进
证据缺口：
P0：
P1：
P2：

### 生产级补充
生产模式匹配：
资源组织：
安装与维护性：
运行环境适配：
安全检测覆盖：

### 反测与回滚
下一条反测 prompt：
通过标准：
回滚或隔离条件：
```

## 6. Calibration Rules

- Score evidence, not section count or prose length.
- A missing critical behavior cannot be offset by style.
- Do not infer runtime safety from readable instructions.
- Apply `N/A` only when the capability is genuinely outside the execution path.
- For domain-specific skills, add a domain rubric after this general rubric; do not silently change the 100-point weights.
- When two reviewers differ by more than 10 total points or 30% of a dimension, compare cited evidence before averaging.
- Always name the three most important fixes. Do not inflate scores to be encouraging.
