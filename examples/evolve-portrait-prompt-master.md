# Example: Evolving Portrait Prompt Master

This case records why the first two versions of `portrait-prompt-master` did not precisely solve the user's need, and what dao-skill should learn.

## User Need

The user wanted to upload an AI-generated cosplay portrait and reverse it into prompts that preserve:

- broad person type, such as Asian-presenting vs European-presenting visual aesthetics
- skin tone and skin gloss
- face structure and facial details
- lighting, especially face lighting
- overall cosplay/fantasy style

## Original Root Problem

V0 dao-skill framed the root as:

> Convert an AI portrait into a reproducible generation specification rather than recover the original prompt.

This was better than "guess the prompt," but still incomplete.

## Deeper Root Problem

The real root was:

> Convert an image into a controllable portrait reproduction system, where visual identity, face geometry, skin material, lighting map, aesthetics, tool workflow, and failure diagnosis are all explicit control dimensions.

## Why Version 1 Missed

Version 1 did one important thing right: it refused the false promise of exact prompt recovery.

But it failed because:

- It described the portrait too generally.
- It treated skin tone as enough, but omitted skin material and highlight placement.
- It avoided apparent regional/ancestry wording so strongly that it removed a useful visual control.
- It did not separate face geometry from face details.
- It said "cinematic lighting" without key/fill/rim/catchlight mapping.
- It had no failure-diagnosis loop for wrong outputs.

Dao-skill lesson:

> Honest boundaries are not enough. A generated skill must identify the control dimensions that decide success in the target domain.

## Why Version 2 Was Better But Still Incomplete

Version 2 added person-type wording, face details, skin material, and lighting maps.

But it still missed a deeper layer:

- It was reactive to feedback rather than designed to learn from feedback.
- It improved visual fidelity but did not add an explicit aesthetic judgment system.
- It did not explain how "portrait design mastery" becomes controllable prompt language.
- It lacked an evolution protocol that would turn each user failure into reusable rules.
- It improved the child skill but did not yet improve dao-skill's own generation algorithm.

Dao-skill lesson:

> If a child skill needs several corrective rounds, dao-skill must update its own root-finding questions, not only patch the child skill.

## Dao-Skill Patch

Future dao-skill generations should ask:

- What are the target domain's control dimensions?
- What fields must be first-class, not buried in prose?
- What would count as a failed output after the user tests it?
- What safe vocabulary is needed to be useful without overclaiming?
- What is the tool workflow needed beyond text?
- What aesthetic or quality lens should guide taste?
- How will feedback become a rule, example, or reference?

## Retest Prompt

```md
使用 $dao-skill：我想做一个根据 AI cosplay 人像反推提示词的 skill。它要尽量保持人物视觉类型、脸部结构、皮肤光泽、脸部光线和整体审美。请不要只给 prompt，要设计成可迭代进化的 skill。
```

Expected evolved behavior:

- dao-skill identifies the root as a controllable reproduction system.
- It asks for or defines success dimensions before generating.
- It includes failure diagnosis and self-evolution mode in the child skill.
- It separates safety boundaries from usable visual vocabulary.
- It outputs references for aesthetics, model workflow, and evolution.
