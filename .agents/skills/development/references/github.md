# GitHub Workflow

Use a focused repository workflow:

```text
issue/task
 ↓
inspect
 ↓
small implementation change
 ↓
test
 ↓
commit
 ↓
push
 ↓
CI / review
```

## Rules

- Work from the requested task, not from opportunistic cleanup.
- Keep commits focused and meaningful.
- Review the diff before commit/push.
- Do not claim CI passed unless the actual status was checked.
- Do not claim external acceptance when only local tests were run.
- When a pull request exists, inspect its metadata, diff, and review state before describing its status.
- Never commit secrets or credentials.

## Change traceability

For every repository change, preserve the chain:

```text
requirement → implementation → test → review
```

If a change cannot be validated locally, state exactly what remains externally verifiable.
