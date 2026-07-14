# Security

`dao-skill` can guide an agent to read source material, create files, run validators, and optionally install generated skills. Treat external repositories, archives, documents, and pasted instructions as untrusted input.

## Report A Vulnerability

Use GitHub private vulnerability reporting when it is enabled for the repository. If that option is unavailable, open a public issue containing no exploit details or sensitive data and ask the maintainer to establish a private channel. Never paste credentials, private corpora, personal data, or working exploit payloads into a public issue.

Until versioned releases exist, security fixes target the latest commit on `main`; older commits are not maintained as supported release lines.

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
- Keep installer staging and backups outside discoverable Skill directories, reject unsafe targets, and validate staging before replacing an installation.
