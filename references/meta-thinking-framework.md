# Meta-Thinking Framework

Use this reference when designing upper-layer systems, skill families, or reusable thinking tools.

## What Meta-Thinking Means Here

Meta-thinking is not "thinking abstractly." It is thinking about:

- what kind of problem this is
- what level of abstraction is useful
- which process should handle it
- how the process should know when it is done
- how the output can be evaluated and improved

## Levels Of Skill Design

| Level | Question | Artifact |
| --- | --- | --- |
| L0 Task | How do I do this one job? | answer, script, document |
| L1 Workflow | How do I repeat this job? | skill |
| L2 System | How do multiple workflows cooperate? | skill family |
| L3 Generator | How do new workflows get born? | meta-skill |
| L4 Evaluator | How do we judge and evolve workflows? | rubric, tests, governance |

Dao skill primarily works at L2-L4, then generates L1 artifacts when needed.

## Meta Moves

Use these moves explicitly:

- Reframe: name the deeper job.
- Route: decide whether an existing skill should handle the work.
- Factor: split one messy skill into smaller cooperating skills.
- Compose: define how multiple skills hand off to each other.
- Bound: state what the system should not try to do.
- Evaluate: score the artifact and name next revisions.

## Skill Family Pattern

When the user wants a system rather than one skill, produce:

```md
## Skill Family
母体 skill：
子 skill：
触发关系：
共享 references：
分流规则：
共同质量标准：
演化路线：
```

## Routing Rules

Use a specialized skill path when the user's root problem already matches it:

- Nuwa-style: distill a person, text, philosophy, brand, creator, or worldview into a runnable thinking frame.
- Colleague-style: reconstruct a real working style or collaboration pattern from artifacts.
- Dao-style: find the root, design the architecture, generate or evaluate the skill system.

## Avoid Meta-Traps

- Do not add a meta-layer when a simple skill is enough.
- Do not use abstraction to avoid implementation.
- Do not build a hierarchy of authority between skills.
- Do not create a "universal" skill that swallows concrete expertise.
