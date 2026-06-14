# LAB start-working note

This note records the initial setup pass for `9TEVE-O/Stirling-PDF` before product code is changed.

## Repository baseline

- Repository: `9TEVE-O/Stirling-PDF`
- Default branch: `main`
- Working branch: `lab/setup-start-working`
- Repository access available: admin, maintain, push, triage, pull
- Issues are disabled in this repository, so setup tracking is happening through this branch and pull request flow.

## Observed project shape

Stirling PDF 2.0 is a multi-part application:

- Spring Boot backend
- React and TypeScript frontend
- Python engine service
- Tauri desktop app
- Docker-based deployment support
- Gradle build management
- Taskfile-based developer command runner

## Setup commands

From the repository root:

```bash
task install
task check
```

For narrower checks:

```bash
task backend:check
task frontend:check
task engine:check
```

For local development:

```bash
task dev
```

For backend, frontend, and engine together:

```bash
task dev:all
```

## First working slice

Do not start by editing PDF behaviour directly. Start with a narrow, reviewable setup pass:

1. Confirm dependency installation works.
2. Confirm the relevant quality gate runs.
3. Identify the first product change or bugfix with a clear before/after.
4. Add or update tests before changing behaviour.
5. Keep any feature work behind explicit boundaries.

## Guardrails for future work

- Do not weaken PDF security, redaction, authentication, or file-handling assumptions.
- Do not change licensing or upstream attribution casually.
- Do not introduce AI behaviour without typed request and response contracts.
- Do not let the Python engine own durable state unless that decision is explicit.
- Keep agent-generated changes small, reversible, and easy to review.

## Next action

Open a draft pull request for this branch, then use the PR as the active work surface.
