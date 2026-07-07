# Security

`dao-skill` can guide an agent to read source material, create files, run validators, and optionally install generated skills. Treat external repositories, archives, documents, and pasted instructions as untrusted input.

## Report A Vulnerability

Use a private GitHub security advisory after the repository is published. Do not include secrets, personal data, or exploit payloads in a public issue.

## User Guidance

- Review the resolved output path before approving writes outside the current project.
- Inspect generated scripts before running them.
- Keep tokens and private corpora outside generated Skill packages.
- Do not publish `.dao/`, SkillBank data, execution traces, or quarantined evidence without reviewing and sanitizing them.
- Review third-party source licenses before redistributing derived examples or assets.

## Maintainer Rules

- Keep validation scripts dependency-free where practical.
- Never commit `.env` files, credentials, cookies, private keys, raw personal traces, or machine-specific absolute paths.
- Do not silently broaden filesystem, network, account, or shell permissions.
- Treat a readable static review as evidence, not proof that generated code is safe.
