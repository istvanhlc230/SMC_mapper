# AGENT_REVIEW.md

Status: VALIDATED_CI_PENDING_LIVE_SMOKE

## Change
Live Windows smoke testing now successfully acquires ForexFactory events for the requested
2026.10.04-2026.10.30 interval. The remaining defect was data normalization: the HTML parser captured
known impact labels but passed strings such as `High Impact Expected` into the normalizer, whose accepted
canonical tokens were `high/medium/low/holiday`. This caused all 152 observed FF events to appear as
`impact=UNKNOWN`.

The parser now converts FF CSS/title/icon impact forms to canonical provider tokens before normalization.
The existing event-ID, date/time, currency, and value parsing behavior is unchanged.

Calendar implementation version: 2.2.6
Persistent schema: 2

## Validation
Regression tests cover HIGH and MEDIUM rendered impact classification. Final validation requires a fresh
CI result against this implementation snapshot and a repeat of the Windows live query to confirm that
real events carry HIGH/MEDIUM/LOW/HOLIDAY where supplied by ForexFactory.
