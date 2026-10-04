# AGENT_REVIEW.md

Status: CI_TRIGGERED_FINAL_RUN

## Change
ForexFactory provider query construction follows the native calendar query forms:
- one concrete provider calendar day -> `day=<monD.YYYY>`;
- multi-day provider interval -> `range=<monD.YYYY>-<monD.YYYY>`.

The rendered HTML fallback now ignores helper/calendar rows that do not contain an event title before
requiring a provider event ID. Event rows remain strict: a titled economic event without a provider ID
is still a provider-integrity failure. The parser accepts the established `data-eventid` and `data-event-id`
forms and the additional equivalent `data-eid` attribute.

Calendar implementation version: 2.2.4
Persistent schema: 2
No `test/` or `tests/` directory was added.

## Validation
The previous CI failures were analyzed and corrected. A fresh CI run against the resulting snapshot is
required before this review can be marked validated.

CI trigger commit reflects parser-row handling fix from 8de2427847937ede8035c79e9d512079afde6a21.
