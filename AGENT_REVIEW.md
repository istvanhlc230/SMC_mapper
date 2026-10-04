# AGENT_REVIEW.md

Status: IMPLEMENTED_PENDING_CI

## Change
ForexFactory provider query construction now follows the native calendar query forms supplied for the
provider:
- one concrete calendar day -> `day=<monD.YYYY>`;
- multi-day acquisition interval -> `range=<monD.YYYY>-<monD.YYYY>`.

Relative provider navigation aliases remain documented only and are not added to the public Calendar CLI
grammar.

## Implementation snapshot
- Calendar version: 2.2.2
- Persistent schema: 2
- No `test/` or `tests/` directory added.
- Temporary artifacts remain under `dev_tmp/` by repository policy.
- Canonical interval filtering remains in UTC after provider acquisition.

## Validation
Deterministic CI contract coverage was extended for the native ForexFactory day/range query forms.
CI validation must complete against this exact commit before this review can be marked validated.
