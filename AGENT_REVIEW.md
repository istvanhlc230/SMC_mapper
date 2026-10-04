# AGENT_REVIEW.md

Status: IMPLEMENTED_PENDING_CI

## Change
ForexFactory provider query construction follows the native calendar query forms:
- one concrete provider calendar day -> `day=<monD.YYYY>`;
- multi-day provider interval -> `range=<monD.YYYY>-<monD.YYYY>`.

The Calendar internal interval remains half-open, while the ForexFactory range endpoint uses concrete
calendar-day endpoints. Returned records are filtered again against the canonical UTC interval.

The rendered HTML fallback date parser no longer calls `datetime.strptime()`. This avoids the standard-library
module-name collision caused by the executable file being named `calendar.py`.

Relative provider navigation aliases remain documented only and are not added to the public Calendar CLI grammar.

## Implementation snapshot
- Calendar version: 2.2.3
- Persistent schema: 2
- No `test/` or `tests/` directory added.
- Temporary artifacts remain under `dev_tmp/` by repository policy.
- Canonical interval filtering remains in UTC after provider acquisition.

## Validation
The CI run for commit 2a55c3e7cf9d957aa8ab9110a4c509f6c45f7767 failed in the HTML fallback test because
`datetime.strptime()` loaded the local `calendar.py` instead of the standard-library `calendar` module.
The fallback date conversion is now locale-free and avoids that namespace collision.
A fresh CI run against this exact commit is required before validation can be marked complete.

CI trigger snapshot: 2026-10-04T17:08Z.
