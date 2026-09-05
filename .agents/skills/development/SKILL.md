---
name: development
description: Guides implementation work in this repository using a disciplined inspect → small change → test → next change → review workflow. Use for coding, debugging, refactoring, integration, and repository changes.
---

# Development Skill

This skill defines **HOW development work is performed** in the repository.

It does not define domain correctness. For True SMC correctness, use the separate `smc` skill.

## Core Loop

```text
TASK
 ↓
INSPECT
 ↓
SMALL CHANGE
 ↓
TEST
 ↓
NEXT SMALL CHANGE
 ↓
REVIEW
 ↓
DONE
```

Never skip the loop merely because a change appears small.

## 1. Understand the Task

Before editing:

- Identify the requested outcome.
- Identify explicit constraints.
- Identify the files and interfaces that can actually be affected.
- Preserve accepted behavior unless the task explicitly requires changing it.
- Treat requirements as authoritative; tests are evidence, not a substitute for requirements.

For this repository, keep the architecture boundaries clear:

- `development` skill = how to develop.
- `smc` skill = what True SMC means.
- `SMC_mapper.py` = implementation.
- `test_smc.py` = regression evidence.
- `data_provider.py` = data layer.

Do not move domain rules from the `smc` skill into this development skill.

## 2. Inspect Before Editing

Inspect only the context needed for the next logical change.

Preferred order:

1. repository structure
2. target file
3. directly related implementation
4. directly related tests
5. configuration/interfaces only when relevant

Do not reread large files unnecessarily. Prefer targeted ranges/searches.

Before changing behavior, establish:

- current behavior
- relevant call path
- affected state/data structures
- existing tests covering the behavior
- compatibility constraints

If the required source is unavailable, do not invent its contents.

## 3. Make the Smallest Logical Change

Use the smallest change that completely satisfies one coherent requirement.

Rules:

- Prefer one focused logical change at a time.
- Avoid unrelated cleanup.
- Avoid speculative refactoring.
- Avoid changing public interfaces unless required.
- Avoid changing domain semantics merely to make implementation easier.
- Preserve existing accepted behavior outside the requested change.
- Keep the default change budget at **≤3 files per logical change** unless the task inherently requires more.

A migration or rename should remain mechanical when the task says it is mechanical. Do not silently combine migration with methodology redesign.

## 4. Test Immediately

After each logical change:

1. run the smallest relevant test first;
2. then run the broader regression suite when appropriate;
3. inspect failures before making another change.

Tests are evidence of behavior. A passing test does not override a violated requirement.

When fixing a defect:

- reproduce or identify the failing behavior;
- add or update a focused regression test when appropriate;
- make the minimal implementation change;
- rerun the focused test;
- rerun the relevant regression suite.

Never claim a test passed unless it was actually run and observed.

## 5. Continue in Small Steps

If the task requires multiple changes, repeat:

```text
INSPECT → CHANGE → TEST
```

Do not batch unrelated fixes simply because they are in the same file.

After a failed test, diagnose the failure rather than immediately changing additional code.

## 6. Review Before Completion

Before declaring the work complete:

- review the final diff;
- verify only intended files changed;
- verify no secrets were introduced;
- verify no unrelated behavior changed;
- verify tests relevant to the change passed;
- verify documentation/configuration matches the implementation when applicable.

For repository work, also verify:

- correct branch/base;
- commit contains only intended changes;
- working tree/diff is understandable;
- CI/review status is not falsely represented.

## 7. GitHub Workflow

Use this workflow for repository changes:

```text
issue/task
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

Use meaningful, focused commits.

Do not mix unrelated fixes in one commit.

When a pull request exists, inspect its diff and review state before making claims about acceptance.

When CI is available, use it as additional evidence. Do not claim CI passed unless the actual status was checked.

## 8. Change Discipline

Do not:

- rewrite working code without a requirement;
- introduce abstractions before they are needed;
- change unrelated formatting;
- weaken domain validation to make tests pass;
- delete regression coverage because it is inconvenient;
- fabricate missing dependencies or source material;
- claim independent acceptance when external validation is required.

Do:

- make intent explicit;
- keep changes reviewable;
- preserve traceability from requirement → implementation → test;
- prefer deterministic behavior;
- leave a clear regression trail.

## 9. Token and Context Discipline

Optimize for useful context, not maximum context.

- Search before reading large files.
- Read only relevant ranges when possible.
- Reuse information already established in the current task.
- Do not repeatedly inspect unchanged files.
- Do not paste or reproduce large source files when a targeted excerpt is sufficient.

## 10. Domain Skill Separation

The development skill must remain domain-neutral.

For True SMC work:

```text
Development skill
        │
        │ HOW to work
        ▼
INSPECT → SMALL CHANGE → TEST → REVIEW
        │
        ▼
True SMC skill
        │
        │ WHAT is correct
        ▼
SMC_mapper.py
```

If implementation behavior conflicts with the canonical True SMC methodology, do not resolve the conflict by inventing a new rule. Inspect the `smc` skill and reconcile implementation against that authority.

## 11. Completion Contract

A task is complete only when:

- the requested change is implemented;
- relevant tests have been run;
- the resulting behavior has been checked against the requirement;
- the final diff has been reviewed;
- no unrelated changes remain;
- any remaining uncertainty is explicitly stated.

The goal is not merely to produce code that runs. The goal is to produce the smallest verified change that satisfies the requested behavior.
