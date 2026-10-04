# AGENT_REVIEW.md

Status: VALIDATED_CI_CONTRACT_SUITE

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
The failed intermediate CI runs were corrected: the range test now respects the half-open internal interval,
and the fallback date conversion is locale-free and avoids the local `calendar.py` / standard-library module
name collision.

CI validation: SUCCESS
- Workflow run: 37219439727
- Validated implementation commit: c1850d29d2911e48d975dd7b7bd14c8c5d776f8f
- Head review snapshot: this commit

CI trigger snapshot: 2026-10-04T17:10Z.
