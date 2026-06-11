## AI Rules

- Source of truth: `ai-agents/global-rules.md` contains the canonical AI rules for the repository.
- Cursor picks it up via the include in `.cursor/rules/global-rules.mdc` which contains `@include ../../ai-agents/global-rules.md`.
- Copilot and other tooling can read the full copy in `.github/instructions/global-rules.instructions.md` (this file is a straight copy of the rules with frontmatter).
- To update rules: edit only `ai-agents/global-rules.md`. The pre-commit hook will copy the body into `.github/instructions/global-rules.instructions.md` while preserving the frontmatter.
- One-time setup: run:

```
npm run setup
```
