# Production Skill Patterns

Use this reference when the user wants dao-skill to generate or evaluate benchmark-level skills, skill families, or repositories comparable to `nuwa-skill`, `mattpocock/skills`, or `dbskill`.

The goal is not to imitate their surface style. Extract the production pattern: what control loop, evidence flow, packaging, validation, and routing make the skill work.

## Pattern 1: Cognitive Distillation Skill

Inspired by nuwa-style skill generation.

Use when the user wants to distill a person, theme, creator, thinker, company, worldview, or field into a runnable cognitive lens.

Root problem:

- Transform messy public or private evidence into a usable thinking framework without pretending to reproduce the real person.

Core architecture:

1. Intake and route: named person/theme vs vague need.
2. Evidence plan: decide public research, user-provided materials, or local-only materials.
3. Research dimensions:
   - writings and long-form thought
   - conversations and improvisational thinking
   - expression DNA
   - external views and criticism
   - decisions and actions
   - timeline and recent changes
4. Research review checkpoint: source count, source quality, contradictions, weak dimensions.
5. Synthesis:
   - 3-7 mental models
   - 5-10 decision heuristics
   - expression rules
   - values and anti-patterns
   - internal tensions
   - honest boundaries
6. Skill construction: concise `SKILL.md` plus linked references.
7. Verification:
   - known-position sanity checks
   - edge-case uncertainty checks
   - voice/style checks
   - source traceability checks

Output resources:

- `SKILL.md`
- `references/research/*.md`
- `references/synthesis.md` when useful
- `examples/*.md` with realistic prompts and expected behavior
- scripts only for deterministic source processing or quality checks

Quality gates:

- Separate "said by them", "said about them", and "inferred by us".
- Prefer first-hand sources.
- Preserve contradictions instead of smoothing them away.
- Do not over-personify. Frame the result as a perspective lens or thinking operating system, not the real person.
- Mark cutoff date and weak evidence areas.

Failure modes:

- Quote collage instead of thinking model.
- Generic wisdom with a famous name attached.
- Voice imitation without decision logic.
- Confident claims from weak sources.
- Research files stored outside the skill directory, making the skill non-portable.

## Pattern 2: Engineering Workflow Pack

Inspired by Matt Pocock-style engineering skills.

Use when the user wants skills for coding, debugging, architecture, TDD, triage, product requirements, issues, PRs, or repeatable engineering work.

Root problem:

- Convert engineering discipline into small composable workflows that keep the agent aligned with reality through feedback loops.

Core architecture:

1. Setup skill: establish project context, glossary, issue tracker, ADR location, and local conventions.
2. Small composable skills: one skill per workflow, not one giant engineering brain.
3. Feedback loop first:
   - failing test
   - deterministic command
   - browser/curl loop
   - fixture replay
   - profiler or benchmark
   - issue/PR checklist
4. Shared language:
   - domain glossary
   - architecture vocabulary
   - ADRs for load-bearing decisions
5. Vertical slices:
   - one behavior/test at a time
   - avoid writing all tests then all implementation
   - refactor only when green
6. Postmortem and handoff:
   - what fixed it
   - what would prevent it
   - what architecture follow-up exists

Output resources:

- multiple small skill folders
- setup skill
- reference vocabulary files
- templates for ADR, context, issue, PRD, handoff
- scripts for deterministic guardrails or loops

Quality gates:

- Every debugging or build workflow must name its pass/fail signal.
- Every architecture recommendation must connect to locality, leverage, testability, or navigation.
- Every TDD workflow must test behavior through public interfaces.
- Avoid author-specific assumptions that do not travel to the user's codebase.

Failure modes:

- Advice without a runnable feedback loop.
- Giant overgeneral engineering prompt.
- Glossary/ADR dependency hidden instead of set up.
- Refactor plans that ignore tests or current seams.

## Pattern 3: Methodology Toolbox

Inspired by dbskill-style author methodology systems.

Use when the user wants a business, content, creator, coaching, consulting, writing, strategy, or diagnosis toolkit based on a strong worldview or body of work.

Root problem:

- Turn an author's method into a routed set of diagnostic tools without confusing worldview, evidence, and fact.

Core architecture:

1. Main router skill:
   - routes only
   - asks one intent question when ambiguous
   - does not perform deep diagnosis itself
2. Vertical diagnostic skills:
   - each solves one diagnostic job
   - each has a clear start question, phases, stop conditions, and output protocol
3. Shared knowledge layer:
   - knowledge atoms
   - method references
   - case library
   - glossary
4. State lifecycle:
   - save
   - restore
   - report
   - project/session boundaries
5. Handoff rules:
   - diagnosis -> benchmark -> content
   - content -> title/hook/AI-check
   - goal -> action/content/business
   - any conclusion -> save

Output resources:

- router `SKILL.md`
- several focused subskill folders
- shared `references/` or knowledge base
- examples for common routes
- optional scripts for state management or packaging

Quality gates:

- Label strong author positions as method or diagnostic stance, not universal fact.
- Make each subskill smaller than the whole worldview.
- Route when a neighboring skill is better.
- Preserve product voice without letting style overpower evidence.
- Use state management only when diagnosis continues across sessions.

Failure modes:

- One large prompt trying to do every diagnosis.
- Strong claims with no boundary language.
- Router starts diagnosing instead of routing.
- Knowledge base exists but subskills do not know when to load it.
- No save/restore/report, causing repeated context loss.

## Pattern 4: Single Procedural Skill

Use when the task is bounded and repeatable.

Root problem:

- Help the agent perform one class of task reliably with minimal context.

Core architecture:

1. Clear trigger description.
2. Short workflow.
3. Output protocol.
4. Boundaries.
5. Optional script for deterministic repeated work.
6. One or two examples.

Quality gates:

- Keep `SKILL.md` lean.
- Avoid unnecessary references.
- Do not turn a small procedure into a toolbox.

## Pattern Selection Checklist

Before generating, answer:

```md
【skill 类型】
【为什么不是更简单的类型】
【需要几个 skill】
【是否需要 router】
【是否需要 references】
【是否需要 scripts】
【是否需要 examples】
【验证闭环】
【状态管理需求】
【安装/打包需求】
```

## Production Generation Protocol

For benchmark-level work, add this pass after root/tension/structure and before writing files:

1. Classify the pattern.
2. Define evidence requirements.
3. Define resource layout.
4. Define validation loop.
5. Define failure modes.
6. Define retest prompts.
7. Generate the smallest artifact set that can satisfy the real success standard.

## Retest Prompt Shapes

Cognitive distillation:

```md
Use the generated skill to answer a question the subject never directly discussed. The answer must show the subject's mental model, cite uncertainty, and avoid invented facts.
```

Engineering workflow:

```md
Use the generated skill on a bug with no obvious cause. It must build a reproducible feedback loop before hypothesizing and must remove temporary instrumentation before finishing.
```

Methodology toolbox:

```md
Give the router a vague multi-intent request. It must route to one subskill, ask at most one clarifying question if needed, and not perform diagnosis inside the router.
```

Single procedural skill:

```md
Ask for the target task with minimal context. The skill must complete it without loading irrelevant references or asking unnecessary questions.
```
