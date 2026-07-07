# First Principles Framework

Use this reference when a request risks becoming feature-driven, overbuilt, or unclear.

## Goal

Reduce a skill idea to the smallest set of truths that must be true for the skill to work.

## Questions

Ask internally:

1. What job is the user hiring this skill to do?
2. What changes after the skill succeeds?
3. What must be true for that change to happen?
4. What can be removed without damaging the core job?
5. What would make this skill fail even if it looks impressive?

## Root Problem Formula

Use this pattern:

```md
用户表面上想要 [surface request]。
真正的问题是 [root change needed]。
这个 skill 的第一性原理是 [irreducible principle]。
因此它必须 [essential behavior]，而不是 [tempting but wrong behavior]。
```

## Feature Filtering

Classify requested features:

| Feature Type | Keep? | Test |
| --- | --- | --- |
| Core mechanism | Yes | Without it, the skill cannot solve the root problem |
| Support structure | Usually | It improves repeatability or verification |
| Interface convenience | Maybe | It helps the user invoke or understand the skill |
| Decorative concept | No | It does not change decisions, workflow, or output |
| Scope creep | No | It creates a second skill disguised as a feature |

## Minimum Viable Skill

A first version needs:

- accurate triggering metadata
- a stable operating workflow
- clear output contracts
- honest boundaries
- one or more examples
- optional references for deeper cases

It does not need:

- every future feature
- broad philosophical exposition
- a large scripts folder
- a README unless the repository itself needs public-facing documentation

## Root Problem Quality Test

Score the root problem from 0-5:

- 0: only repeats the user's words
- 1: identifies a topic but not a change
- 2: names a change but not the mechanism
- 3: names change and mechanism
- 4: also names success and failure
- 5: clearly constrains what the skill should and should not do

Do not generate a complex skill below 3 unless the user explicitly asks for a draft.
