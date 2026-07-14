# Contributing

`dao-skill` values observable control loops over additional philosophy or prompt length.

## Repository Boundary

Submit changes to the core engine only: `SKILL.md`, direct reference/example files, validation scripts, metadata, and public documentation.

Do not submit:

- generated child Skill repositories
- personal SkillBank entries or execution traces
- output files, screenshots, caches, or local backups
- private corpora, credentials, cookies, or machine-specific paths

If a child Skill reveals a reusable lesson, reduce it to the smallest routing rule, reference mechanism, test prompt, or validator change that belongs in dao-skill.

## Development Loop

1. Make the smallest behavior-changing edit.
2. Add or update a retest prompt for changed behavior.
3. Run:

```bash
python3 scripts/run_checks.py
```

4. In the pull request, state the evidence, pass signal, and rollback condition.

## Style

- Keep `SKILL.md` focused on routing and control rules; move detail into `references/`.
- Label source boundaries and uncertainty.
- Prefer standard-library validation scripts with deterministic exit codes.
- Do not claim public links, marketplace entries, benchmarks, or runtime support that have not been verified.
- Treat static behavior contracts as E1 evidence; attach replay artifacts before claiming runtime verification.
