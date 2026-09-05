# Review

Before completion, review the final diff rather than trusting the last edit.

Check:

- only intended files changed;
- the implementation matches the requested behavior;
- accepted behavior was not changed accidentally;
- tests relevant to the change passed;
- no secrets were introduced;
- configuration and documentation remain consistent;
- no speculative or unrelated cleanup slipped into the change.

For behavioral changes, verify the requirement independently from the tests. A green test suite is not proof that the requirement was interpreted correctly.

For repository work, inspect branch/base, commit scope, CI status, and review state before making claims about completion or acceptance.
