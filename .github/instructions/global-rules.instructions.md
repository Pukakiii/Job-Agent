---
applyTo: "**"
---


AI Rules - Single Source of Truth

Code style rules

- Follow existing repository patterns for formatting and linting.
- Keep functions small and focused; prefer composition over inheritance.
- Use clear, descriptive names for variables, functions, classes, and modules.
- Write tests for new logic; aim for unit tests that cover edge cases.
- For Python: follow PEP8 and type hints where practical. Use existing pyproject.toml tooling.
- For JavaScript/TypeScript (frontend): follow existing ESLint/Prettier configs. Avoid using `any` in TypeScript.

Security rules

- Never log secrets (API keys, passwords, tokens) to console, files, or telemetry.
- Sanitize all external inputs before use. Assume user-provided data is untrusted.
- Use parameterized queries or ORM query builders to prevent SQL injection.
- Validate and encode outputs sent to browsers to prevent XSS.
- Rotate credentials and avoid committing secrets to source control. Use environment variables or a secrets manager.

Architecture rules

- Keep to existing project patterns and folder structures. New features should follow the same layering (api, services, repositories, models).
- Prefer adding small, focused dependencies. Avoid introducing large frameworks or infra changes without team discussion and an ADR.
- Maintain clear boundaries between layers: business logic belongs in services, persistence in repositories, and HTTP concerns in routes/controllers.
- Favor composition and dependency injection for testability.

What NOT to do

- Do not leave debugging statements in production code (e.g., console.log, print) or commit them to main branches.
- Do not use insecure randomness for cryptographic purposes. Use well-vetted libraries and OS-provided randomness where required.
- Do not add global state or singletons that break test isolation.
- Do not commit secrets, private keys, or credentials to the repository.
- Do not introduce `any` types in TypeScript without a justification and a follow-up ticket to tighten types.

Change process

- Treat this file as the single source of truth for AI-assisted rules and infra. Update this file when rules change.
- Keep changes small and document the reason in commit messages or an accompanying ADR if the change is architectural.

Contact

- For questions about these rules, open an issue or contact the maintainers listed in the repository documentation.
