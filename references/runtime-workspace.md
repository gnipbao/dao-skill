# Runtime Workspace Contract

Use this reference whenever dao-skill modifies itself, installs itself, or creates a child skill, SkillBank entry, evolution ledger, execution trace, or generated output.

## First Principle

Source code and user-generated state have different lifecycles.

The installed `dao-skill` directory is a read-mostly engine. Generated child skills and runtime state belong to the user and must not be bundled into, committed to, or silently written inside the engine repository.

## Target Resolution

First classify the target:

- **Source repository**: the Git worktree where dao-skill is maintained and committed.
- **Installed dao-skill**: the read-mostly copy discovered by Codex; update it through `scripts/install.py`, not direct edits.
- **Generated child Skill**: an independently owned artifact, never nested implicitly inside dao-skill source or installation.
- **Runtime state**: SkillBank entries, traces, ledgers, runs, outputs, and quarantine data.

Resolve `<project>` in this order: an explicit user path; the nearest ancestor of the current working directory containing `.git` or a recognized project marker; otherwise the current working directory. State when the fallback is used.

If `<project>` resolves to the dao-skill source repository or an installed dao-skill, it is the engine, not a user project. This is the normal case for a maintainer working from the dao-skill checkout; skip rule 2 below.

Resolve the destination before creating files. Use the first applicable rule:

1. **Explicit user path**: use a writable path supplied by the user. Honor a path inside the dao-skill source only as unpublished local workspace and say so before writing; the allowlist `.gitignore` keeps it out of Git. Refuse a path inside an installed dao-skill, because the next install replaces it.
2. **Project-local draft**: use `<project>/.dao/skills/<skill-name>/` when the user wants the artifact in the current project.
3. **Maintainer workspace**: when rule 2 was skipped, use `$DAO_SKILL_HOME/skills/<skill-name>/` if set; otherwise propose `<parent-of-source>/<skill-name>/`, a sibling of the source repository, and state it before the first write.
4. **Installed user skill**: use the active host's user skill directory only when the user asks to install or make the skill globally discoverable: `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/` for Codex, `$HOME/.claude/skills/<skill-name>/` for Claude Code. Ask when the host is unknown.
5. **No writable destination**: do not pretend files were created. Return the proposed tree and the exact path or permission needed.

Never choose the `dao-skill` source or installation directory as the implicit parent of a child skill. The source `examples/` directory holds flat `*.md` behavior examples, never child Skill folders.

Canonicalize source and target paths before writing. Reject a target that is a symlink, resolves inside an installed dao-skill, resolves inside the dao-skill source without an explicit user path, or is an ancestor of the source. Inspect an existing target before replacement and keep backups outside any discoverable `skills/` directory. After writing, `scripts/quality_check.py` fails a target inside an installed dao-skill and warns for one inside the source.

## Dao-Skill Self Update

Use this fixed sequence when maintaining dao-skill itself:

```txt
resolve verified source -> source status -> source patch -> full source checks
-> commit intended clean source -> installer dry-run -> authorized staged install
-> installed-package checks -> authorized push -> remote SHA verification
```

`ENGINE_ROOT` is the real directory containing the active `SKILL.md`. `SOURCE_ROOT` is an explicit or verified dao-skill Git root. `INSTALL_ROOT` is the selected global installation target. Never infer `SOURCE_ROOT` from `ENGINE_ROOT` alone; an installed copy is not a maintenance checkout.

An authorized push also authorizes the commit that carries exactly the in-scope changes. The installer must copy only the curated public payload, refuse a Git source with uncommitted or untracked changes unless `--allow-dirty` targets a disposable test location, write a path-free `.dao-install.json` receipt (source commit and per-file SHA-256) that `install.py --verify` and installed-mode `run_checks.py` check, validate staging before replacement, keep the previous installation outside `${CODEX_HOME}/skills/`, and restore it if activation fails.

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

The dao-skill public repository uses an allowlist `.gitignore`: only the public payload checked by `scripts/repository_check.py` is visible to Git. `.dao/`, SkillBank data, outputs, caches, complete child repositories, and nested example projects stay local without per-directory ignore entries. A new public file must be added to both allowlists.

Users may independently version a generated child skill in its own repository. Dao-skill must not initialize, commit, publish, or push that repository unless the user explicitly asks for those actions.

## Completion Report

Every file-producing run should report:

```md
目标路径：
创建或修改：
验证及证据级别：
未执行的外部动作：
回滚点：
下一步（仅在仍需用户决定时）：
```
