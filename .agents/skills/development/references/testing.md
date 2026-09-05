# Testing

Testing is evidence, not a substitute for requirements.

## Workflow

1. Run the smallest relevant test after each logical change.
2. Add or update a focused regression test when fixing a defect.
3. Run the relevant broader regression suite after the focused test passes.
4. Investigate failures before changing additional code.
5. Report only tests that were actually executed.

## Defect loop

```text
reproduce / identify failure
        ↓
focused regression test
        ↓
minimal fix
        ↓
focused test
        ↓
regression suite
```

Do not delete or weaken tests simply because they conflict with an implementation. Reconcile the implementation with the requirement and authoritative domain rules instead.
