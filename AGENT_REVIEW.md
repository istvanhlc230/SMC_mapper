# AGENT_REVIEW.md

Status: FIXED_FF_URL_AND_LATEST_CI_PENDING

## Change
The Windows live smoke showed that ForexFactory acquisition succeeds, but most events persisted
with `impact=UNKNOWN`. After the first normalization fix, one real HIGH event was correctly
classified, proving the normalizer was active.

Root cause of the remaining issue: the actual structured ForexFactory event objects expose
`impactTitle` (for example `High Impact Expected` / `Low Impact Expected`) and compact
`impactClass` icon forms such as `icon--ff-impact-yel`. The implementation previously looked
for `impactName` first and did not recognize these actual fields/forms.

Calendar implementation version: 2.2.9
Persistent schema: 2

The fix now recognizes the rendered abbreviated provider icon classes `icon--ff-impact-ora`,
`icon--ff-impact-yel`, `icon--ff-impact-grn`, and `icon--ff-impact-gry`, in addition to the existing
red/high and long-form classes. Severity remains explicit only.

## Validation
Regression tests cover:
- impactTitle: High, Med, Low, Non-Economic;
- impactName compatibility forms;
- impactClass color/icon forms, including `icon--ff-impact-yel`;
- existing rendered HTML impact parsing.

A fresh CI result and a clean Windows live smoke remain required. The live smoke must explicitly
remove the existing COMPLETE coverage before reacquiring the same interval, because Calendar
intentionally does not refetch already complete coverage.

Acceptance target: real ForexFactory events persist explicit HIGH/MEDIUM/LOW/HOLIDAY values instead
of UNKNOWN whenever the provider supplies explicit impact metadata.


## Latest presentation fix

The `--cleartext` presentation previously serialized the complete normalized `details` dictionary on one line. This was machine-readable JSON embedded inside a human-readable mode and was therefore not an appropriate cleartext representation.

Calendar implementation version: 2.2.10
Persistent schema: 2

The CLI now renders `Details` as deterministic individual fields, keeps the canonical details object unchanged, and displays null values as `N/A`. Default JSON output is unchanged.

## Validation target

CI must pass the new cleartext regression assertion. A fresh Windows live smoke should confirm the resulting presentation against the real ForexFactory events.


## Latest cleartext presentation refinement

The closing dashed separator after each cleartext event was removed because the next event header already provides the event boundary. Consecutive events are separated by one blank line only. The canonical event data and machine-readable JSON output are unchanged.

Regression coverage asserts that the closing separator is absent and that adjacent cleartext event blocks use the blank-line separator.


## Latest Calendar CLI and ForexFactory detail URL

Calendar implementation version: 2.2.11
Persistent schema: 2

The public CLI now includes `python calendar.py SYMBOL latest`. It is read-only and cache-only, selecting the most recent visible event with timestamp at or before current UTC time. No provider call, coverage change, watermark change, or calendar.json mutation occurs. No qualifying event returns `NO_LATEST_EVENT`.

ForexFactory normalized economic events now also carry `details.url` when the provider supplies the concrete calendar event detail-page URL or event-base slug. The rendered HTML parser captures the actual event-detail href; structured provider data is checked for explicit URL/slug fields. The implementation does not manufacture a URL from the calendar event-instance ID.

Persistent schema remains V2. Existing Yahoo `details.url` behavior is unchanged.

Source-level validation performed:
- CLI help includes `current`, `latest`, and `next`;
- `latest` is accepted by the scope parser and dispatched to a deterministic cache lookup;
- ForexFactory rendered rows retain a matching `/calendar/event/` href;
- normalized ForexFactory details include `url`;
- specification and design files are synchronized;
- no test-directory restoration or root-level development artifact was introduced.

Runtime/CI execution was not available in this tool session, so no live-test PASS is claimed.


## Latest regression fix

Calendar implementation version: 2.2.12
Persistent schema: 2

CI run #56 exposed two defects in the 2.2.11 snapshot: the workflow retained a stale 2.2.10 version assertion, and the ForexFactory detail-URL validator used an over-escaped regular expression that rejected valid `forexfactory.com/calendar/event/` URLs.

The fix corrects the URL regex, updates the CI version assertion, and adds regression coverage for:
- rendered ForexFactory event-detail href preservation;
- normalized ForexFactory `details.url`;
- provider-supplied structured event URL normalization;
- direct `latest` selection;
- `latest` CLI parsing and read-only runtime behavior.

Specification and design baselines are synchronized to 2.2.12. No `test/` directory was introduced and no root-level development artifact was added.

A new CI result is required before declaring PASS.
