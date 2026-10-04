# AGENT_REVIEW.md

Status: IMPLEMENTED_PENDING_CI

## Change
ForexFactory provider query construction follows the native calendar query forms:
- one concrete provider calendar day -> `day=<monD.YYYY>`;
- multi-day provider interval -> `range=<monD.YYYY>-<monD.YYYY>`.

The Calendar's internal interval remains half-open, so a date-range request ending on 2026.04.10
resolves to the provider range through 2026.04.10 by passing the exclusive UTC endpoint 2026.04.11.
Returned records are still filtered against the canonical UTC half-open interval after acquisition.

Relative provider navigation aliases remain documented only and are not added to the public Calendar CLI
grammar.

## Implementation snapshot
- Calendar version: 2.2.2
- Persistent schema: 2
- No `test/` or `tests/` directory added.
- Temporary artifacts remain under `dev_tmp/` by repository policy.
- Canonical interval filtering remains in UTC after provider acquisition.

## Validation
The previous CI attempt failed only because the new test expected the inclusive provider end date while
passing an exclusive internal end date. The test now reflects the documented half-open Calendar interval.
A fresh CI run against this exact commit is required before validation can be marked complete.
