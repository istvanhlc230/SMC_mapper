# Small Changes

## Default Rule

Make the smallest logical change that fully satisfies one requirement.

## Before editing

- State the requested outcome.
- Identify the smallest affected surface.
- Inspect the relevant implementation and tests.
- Confirm existing behavior before changing it.

## While editing

- One coherent change at a time.
- Avoid unrelated cleanup and refactoring.
- Preserve interfaces unless the requirement changes them.
- Keep the default budget at three files or fewer per logical change.

## After editing

- Run the focused test.
- Inspect the failure before making another change.
- Review the diff before moving on.

## Anti-patterns

Do not batch unrelated fixes, rewrite working code without a requirement, or weaken domain rules merely to make a test pass.
