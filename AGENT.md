# AGENT.md — Repository Developer Workflow

## Repository hygiene

- Keep the repository root clean.
- Put all temporary, diagnostic, generated, or scratch files under `dev_tmp/`.
- Do not create a `test/` or `tests/` directory.
- Do not commit cache files such as `calendar.json`.
- Do not overwrite user-requested specification changes.

## Specification-driven changes

- Read the relevant specification before modifying implementation behavior.
- Any structural program change must be reflected in the relevant specification.
- Keep `AGENT_REVIEW.md` synchronized with the exact tested implementation snapshot.
- Do not claim PASS when required validation was not actually executed.

## Git synchronization instruction

After any repository modification is committed and pushed, the developer agent's final response MUST include a copy-pasteable command sequence that brings the user's local checkout into sync with `origin/main`.

For a clean local working tree, always provide:

    git fetch origin
    git pull --ff-only origin main
    git status

If the user has known uncommitted local changes, the final response must provide a safe synchronization sequence that preserves those changes rather than overwriting them.

The synchronization commands must appear at the end of the developer agent's final response.

## Commit and push

- Commit all intended changes.
- Push the completed commit to `origin main`.
- Do not force-push over unrelated user work.
- Report the final commit SHA and whether push succeeded.
