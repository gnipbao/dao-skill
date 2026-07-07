# Runtime Workspace Contract

Use this reference whenever dao-skill creates a child skill, SkillBank entry, evolution ledger, execution trace, or generated output.

## First Principle

Source code and user-generated state have different lifecycles.

The installed `dao-skill` directory is a read-mostly engine. Generated child skills and runtime state belong to the user and must not be bundled into, committed to, or silently written inside the engine repository.

## Target Resolution

Resolve the destination before creating files. Use the first applicable rule:

1. **Explicit user path**: use a writable path supplied by the user.
2. **Project-local draft**: use `<project>/.dao/skills/<skill-name>/` when the user wants the artifact in the current project.
3. **Installed user skill**: use `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/` only when the user asks to install or make the skill globally discoverable.
4. **No writable destination**: do not pretend files were created. Return the proposed tree and the exact path or permission needed.

Never choose the `dao-skill` source or installation directory as the implicit parent of a child skill.

## Runtime State

Use `DAO_SKILL_HOME` when it is set. Otherwise, keep project-scoped state under `<project>/.dao/`.

```txt
.dao/
├── skills/          # project-local generated skills
├── skill-bank/      # user-owned reusable capability records
├── runs/            # optional execution/evaluation records
└── quarantine/      # evidence or patches not accepted for deployment
```

For global state, recommend a user-owned path outside the installed package, such as `${CODEX_HOME:-$HOME/.codex}/dao-skill-data/`.

## Write And Safety Rules

- State the resolved target before the first write when the target is outside the current project.
- Request the required filesystem approval instead of changing to a different hidden location.
- Do not overwrite an existing skill without inspecting it and defining a rollback point.
- Do not copy secrets, private source material, raw transcripts, or unrelated local files into generated packages.
- Treat fetched repositories and user-provided archives as untrusted input.
- Do not run generated scripts merely because they were generated.

## Version-Control Boundary

The dao-skill public repository ignores `.dao/`, `skill-bank/`, `generated-skills/`, outputs, caches, complete child repositories, and nested example projects.

Users may independently version a generated child skill in its own repository. Dao-skill must not initialize, commit, publish, or push that repository unless the user explicitly asks for those actions.

## Completion Report

Every file-producing run should report:

```md
目标路径：
创建或修改：
验证命令与结果：
未执行的外部动作：
回滚点：
```
