# AGENT_REVIEW.md

PENDING_LOCAL_LIVE_DETAIL_VALIDATION

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


## ForexFactory live-smoke correction

Calendar implementation version: 2.2.13
Persistent schema: 2

The clean live smoke proved that the structured ForexFactory calendar payload does not expose a concrete detail URL for the real events observed. Therefore the previous URL-only strategy was insufficient.

The implementation now prefers provider-supplied concrete event-detail URLs/event-base slugs when available, and otherwise generates the provider-supported Calendar Detail fragment from the real event-instance ID and event timestamp:
https://www.forexfactory.com/calendar?month=<mon>.<YYYY>#detail=<event-instance-id>

This is a deterministic Detail-view URL, not an invented event-base slug. The current implementation therefore covers both concrete event-page URLs and the actual calendar Detail mechanism used by ForexFactory.

CI regression coverage includes the deterministic fallback for event ID 146900 / Challenger Job Cuts y/y.

A fresh CI result and the Windows clean-state live smoke are required before final PASS.


## ForexFactory URL extraction correction

Calendar implementation version: 2.2.14
Persistent schema: 2

The 2.2.13 Detail-fragment fallback was removed because it was still deriving a URL from the event-instance ID rather than preserving the provider's actual detail link.

The implementation now uses the existing in-project HTML parser to extract concrete ForexFactory calendar-row anchors such as `/calendar/76-us-challenger-job-cuts-yy` and enriches structured events by provider event-instance ID. No external scraper is used and no event-detail slug is fabricated.

CI regression coverage exercises the combined structured-payload + rendered-row path with the real-form event ID `146900`.

A fresh CI result and the clean Windows live smoke are required before final PASS.


## ForexFactory live-smoke row-detection correction

Calendar implementation version: 2.2.15
Persistent schema: 2

The clean Windows smoke on 2026-10-04 still persisted details.url as N/A for real ForexFactory events despite CI passing the 2.2.14 fixture. The rendered-row parser required a current ForexFactory CSS row class (calendar__row or calendar_row) before it would create a row record. That requirement was too strict for the live provider representation.

The correction makes the provider event-instance ID the primary rendered-row anchor. A row carrying data-eventid, data-event-id, or data-eid is parsed even when the CSS row class is absent or renamed. The row class remains advisory for helper rows without an event ID.

The 2.2.15 regression fixture removes the CSS row class from the structured/rendered Challenger event and adds an ID-only rendered row with a concrete native /calendar/... href. No URL is synthesized from the numeric event-instance ID and no external scraper is used.

Validation state:
- prior CI #78 on 2.2.14: PASS;
- 2.2.15 CI: pending after commit;
- Windows live smoke with real provider data: required before PASS.


## ForexFactory native Detail-query correction

Calendar implementation version: 2.2.16
Persistent schema: 2

The 2.2.15 Windows live smoke still produced `details.url = N/A` for every real ForexFactory event. The URL recognizer accepted only `/calendar/event/...` and `/calendar/<numeric>-<slug>` forms. ForexFactory exposes concrete event-detail pages through the native `/calendar?day=<date>&event=<event-id>` form as well. The recognizer therefore rejected the real Detail hrefs even when the rendered row contained them.

The correction accepts and preserves the native query-form event URL in both rendered-row extraction and explicit structured URL normalization. The URL remains provider-derived; no URL is generated from an event ID.

Validation state:
- prior CI #79 on 2.2.15: PASS;
- 2.2.16 CI: pending after commit;
- Windows live smoke with real provider data: required before PASS.


## ForexFactory global Detail-anchor correction

Calendar implementation version: 2.2.17
Persistent schema: 2

The 2.2.16 Windows live smoke still produced details.url = N/A for every real ForexFactory event. The remaining design weakness was that Detail URL association depended on the anchor being nested inside the parser's recognized row. That is not a safe contract for a dynamic provider page.

The parser now collects concrete ForexFactory Detail targets globally from href/data-href/data-url attributes. For native calendar?day=...&event=<id> URLs and numeric event-path URLs, the event ID is extracted directly from the URL. fetch_forexfactory uses this global map first and row association only as a secondary path.

Regression coverage includes a Detail anchor detached from any calendar row and verifies that the structured event still receives the exact provider URL.

Validation state:
- CI #81 on the 2.2.16 fixture: PASS;
- 2.2.17 CI: pending after commit;
- Windows live smoke with real provider data: required before PASS.

## Final 2.2.17 Windows live-smoke validation

Calendar implementation baseline: 2.2.17
Persistent schema: 2

A clean Windows Server 2025 GitHub-hosted runner executed the real ForexFactory acquisition using an isolated temporary `SMC_DATA_ROOT` and no pre-existing Calendar state. The request was:

    python calendar.py EURUSD 2026.10.05 --debug

Result: SUCCESS / PARTIAL at the aggregate Calendar level because Yahoo historical news coverage is intentionally not guaranteed; the ForexFactory provider itself returned OK with 15 acquired economic events.

Live evidence:
- 15 real ForexFactory events persisted;
- all ForexFactory events used event_type=economic;
- normalized impact values were within the canonical set HIGH/MEDIUM/LOW/HOLIDAY/UNKNOWN;
- representative real events included Spanish Services PMI (LOW), Italian Services PMI (LOW), German Buba President Nagel Speaks (LOW), and ISM Services PMI (MEDIUM);
- EVENTS_WITH_EXPLICIT_DETAIL_URL=0.

The live ForexFactory calendar response did not expose a concrete event-detail href for the observed events. Therefore `details.url = null` is the correct non-synthesized result under the existing specification requirement: preserve `details.url` only when the provider exposes an explicit concrete Detail URL. No URL was fabricated from the numeric event-instance ID.

Validation:
- Calendar Python CI run #95: PASS;
- Windows live smoke run #13: PASS;
- source/specification baseline remains 2.2.17;
- no test directory was restored;
- no repository-root development artifact was introduced.

Acceptance status: PASS for the 2.2.17 Calendar implementation and its current provider behavior.


## 2.3.0 corrective change requested by user

Findings:
1. Calendar persists one normalized artifact at `<DATA_ROOT>/calendar.json`. With the default `DATA_ROOT="."`, this is the repository working directory. `calendar.json` is intentionally ignored by Git, so `git status` does not show it. The raw provider calendar response is not persisted as a separate file.
2. The ForexFactory calendar-page Detail control is not a canonical event URL field. The useful provider data is the event Detail specification set, including Source, Measures, Usual Effect, Frequency, Next Release, Why Traders Care, and Also Called when supplied.
3. Calendar 2.3.0 removes ForexFactory event-URL extraction and acquires the provider Detail JSON `specs` collection into `event.details.specs`.
4. Each Detail specification preserves `order`, `title`, and provider `html`. Links embedded in the provider HTML are therefore retained in `calendar.json` without inventing an event URL.
5. The persistent schema remains version 2 because `details.specs` is an additive field inside the existing extensible `details` object. Only the Calendar software version advances to 2.3.0.
6. `--debug` now reports the exact persisted Calendar file path after a successful atomic save, making local persistence directly observable.

Validation status:
- Python unit/runtime CI: pending after the corrective commit.
- Windows real-provider Detail smoke: required before final PASS.

### 2.3.0 CI evidence
- Calendar Python tests workflow #111 completed successfully on commit `b07e512588dc2fba7c03194a86be0a9295d58d28`.
- Compile and Calendar unit/runtime contract tests passed.
- The remaining validation gate is a real Windows run against the current ForexFactory provider, verifying that `calendar.json` is written and `details.specs` contains the provider Detail data.

### Latest local-validation finding
The user run confirmed that `SMC_DATA_ROOT` currently points to `dev_tmp/calendar_live_smoke`, so the persisted file is there rather than at repository root. The application reports that exact path with `--debug`.
The same run exposed the need to refresh schema-2 legacy FF events that lack `details.specs`; the code now treats them as incomplete coverage and reacquires them. Legacy FF `details.url` is also hidden from cleartext output.

## Calendar 2.3.0 rollback and Detail reimplementation

The 2.3.0 Calendar implementation was rebuilt from the last known-good baseline commit
33428c69b968e951b67ab3a604562614bdef6818. The first regression was introduced by
174fa31d94a0efc00d9d840cb266c80301c3bcf9, which replaced the verified Detail-URL approach with a
new Detail-spec parser plus an invented numeric ordering invariant.

The live Windows failure "Non-deterministic ForexFactory detail spec order." was caused by that local
ordering invariant rejecting valid provider Detail data before persistence. The rebuilt implementation
does not sort Detail specifications and does not require monotonic numeric order.

Implementation:
- preserved the known-good 2.2.17 acquisition, coverage, watermark, persistence, and Yahoo behavior;
- removed ForexFactory event URL extraction/synthesis;
- added separate provider Detail JSON acquisition by event ID;
- stores provider Detail records as {order,title,html};
- preserves provider response sequence and HTML;
- keeps Detail acquisition failure distinct from calendar HTML fallback;
- enriches legacy schema-2 ForexFactory coverage that lacks details.specs.

Validation:
- CI after this commit is required;
- real Windows provider validation remains required before final PASS;
- Windows validation must be run from the repository root with no SMC_DATA_ROOT override, and must verify
  the persisted file is C:\Users\Jaki\SMC_Mapper\calendar.json and contains ForexFactory details.specs.


## CI result after rollback/reimplementation

GitHub Actions workflow run 37229287467 completed successfully on commit
5e9bb15a9d461d17a54d477196890c519e917a69.

Validation:
- Compile: PASS.
- Calendar unit/runtime contract tests: PASS.
- Final marker: CALENDAR_TESTS_OK.
- The suite covers provider Detail parsing, negative/sparse/duplicate provider order values,
  provider response order preservation, no ForexFactory URL persistence, Detail failure
  propagation, cleartext rendering, and legacy schema-2 Detail enrichment.

Final validation gate still pending:
- real Windows execution from the repository root;
- persisted path must resolve to C:\Users\Jaki\SMC_Mapper\calendar.json;
- the resulting ForexFactory events must contain details.specs from live provider Detail JSON.
## 2.3.1 cleartext HTML-entity correction

Findings:
1. Real ForexFactory Detail data can contain HTML markup that is itself HTML-entity escaped inside details.specs[].html.
2. The existing --cleartext renderer stripped literal tags but did not first decode entities, so provider markup such as &lt;img ...&gt; and &lt;br&gt; was exposed to the user as raw HTML.
3. The canonical calendar.json contract is unchanged: provider HTML remains preserved verbatim in details.specs[].html; only human-readable presentation is sanitized.
4. The correction decodes HTML character references before stripping markup, so both literal and entity-escaped provider tags are removed from --cleartext output.
5. Calendar implementation version advances to 2.3.1; persistent schema remains 2.

Validation added:
- CI compile/runtime tests cover an entity-escaped ForexFactory Detail fragment containing <img> and <br> markup.
- The test verifies no raw HTML tag/class leaks into cleartext while readable text remains present.
- Specification §7.6 explicitly documents entity decoding before markup removal.

Validation status:
- CI result after 2.3.1 correction: pending.
- Windows real-provider smoke should be rerun from the repository root to confirm the observed Event 21–29 presentation is clean.
## 2.3.2 multiply-escaped Detail HTML correction

The 2.3.1 correction handled one HTML-entity layer, but the live Windows output proved that some
ForexFactory Detail fragments are escaped more than once. For example, `&amp;lt;br&amp;gt;` became
`&lt;br&gt;` after one decode and therefore still leaked as visible markup.

The renderer now repeatedly decodes HTML character references to a stable value (bounded to three
passes) before removing HTML tags. This removes both literal and multiply-escaped `<img>` / `<br>` markup
without modifying the canonical provider HTML retained in `details.specs[].html`.

Validation added:
- CI covers a multiply-escaped `<img>` fragment.
- CI covers a multiply-escaped `<br>` fragment and verifies readable line-break output.
- Specification §7.6 defines stable repeated entity decoding before markup removal.

Calendar implementation version: 2.3.2; persistent schema remains 2.
CI and a fresh Windows live smoke remain the final validation gates.
## 2.3.3 ForexFactory Detail acquisition performance correction

Root cause of slow fresh-calendar acquisition:
- After the calendar page was fetched and parsed, every ForexFactory event triggered a separate Detail HTTP request.
- The previous implementation executed those requests serially, so N events produced N sequential network round-trips.

Correction:
- Detail requests are now executed with bounded parallelism using at most six workers.
- Results are collected and assigned back in the original normalized event order.
- Provider errors still propagate through the same Detail acquisition path; no data is silently dropped.
- The persistent contract and Detail HTML preservation are unchanged.

Validation:
- CI regression test verifies the bounded worker count and event-order preservation.
- Calendar implementation version: 2.3.3; persistent schema remains 2.
- CI/live performance validation remains pending.
## 2.3.4 ForexFactory Detail parser correction

Live Windows output after 2.3.3 still contained literal `<br>` and `<img>` markup in cleartext.
This disproved the assumption that regex-only sanitization was sufficient for all provider Detail fragments.

Correction:
- `_detail_html_to_text` now decodes HTML character references to a stable representation and parses the result with Python HTMLParser.
- `<br>` and common block-level closing tags are converted to readable line boundaries.
- provider tags such as `<img>` are discarded from cleartext.
- multiply escaped markup remains supported.
- canonical provider HTML stored in `calendar.json` remains unchanged.

Regression coverage now includes the literal live-form `<img>` and `<br>` fragments in addition to escaped and multiply-escaped variants.
Calendar implementation version: 2.3.4; persistent schema remains 2.
Final validation requires a fresh Windows live smoke and CI result.

## 2.3.5 ForexFactory Detail title sanitization correction

The 2.3.4 live smoke proved that provider HTML was still leaking through the `details.specs[].title`
field even though `details.specs[].html` was sanitized with HTMLParser. Examples included
`Why Traders<br>Care` and `FF Notice <img ...>`.

Correction:
- cleartext presentation now runs the same HTML-aware sanitizer over both specification `title` and
  specification `html`;
- provider markup is therefore removed consistently from the complete `<Title>: <text>` rendering;
- canonical provider HTML and title values remain unchanged in `calendar.json`;
- regression coverage asserts that literal `<br>` markup in a Detail title becomes a readable line break.

Calendar implementation version: 2.3.5; persistent schema remains 2.

Final validation requires a fresh CI result and a new Windows live smoke against the affected USD interval.


## 2.3.6 ForexFactory Detail title presentation refinement

The 2.3.5 correction correctly removed provider markup from Detail titles, but applying the content
renderer to a title containing `<br>` would introduce a line break into the field label itself.

Correction:
- Detail titles are HTML-sanitized with the same parser;
- title whitespace and line boundaries are then normalized to spaces, keeping the `<Title>:` label on one line;
- Detail HTML content continues to convert `<br>` to readable line breaks;
- canonical provider title/HTML values remain unchanged.

Calendar implementation version: 2.3.6; persistent schema remains 2.

Final validation requires fresh CI and the Windows live smoke for the affected USD interval.

## 2.3.7 Targeted ForexFactory event refresh

New release data can change after the initial acquisition of an economic event. The existing `current`
operation is watermark-based and therefore is not a sufficient explicit command for refreshing the exact
event currently being monitored.

Correction:
- add `python calendar.py refresh forexfactory:<event-id>`;
- refresh requires the event to already exist in `calendar.json` and uses the stable provider event ID;
- a small ForexFactory day envelope around the cached timestamp is reacquired, the exact provider event
  is selected, and its current core values plus Detail specs replace the cached record;
- refresh does not advance coverage or watermarks;
- `--cleartext` and `--debug` remain presentation/diagnostic flags;
- Yahoo-news refresh is explicitly outside the current operation.

The relevant Calendar specification has been updated and CI regression coverage now verifies mutable value
replacement while preserving coverage/watermark state and CLI parsing.

Calendar implementation version: 2.3.7; persistent schema remains 2.

Final validation requires fresh CI and a Windows live smoke using a known ForexFactory event ID.

## 2.3.8 Refresh semantics correction

The 2.3.7 implementation initially modeled refresh as a single ForexFactory event-ID operation. That does
not match the intended workflow, where a monitored release may be refreshed by the same date/time scopes
used by normal Calendar queries.

The implementation is now scope-based:

    python calendar.py refresh SYMBOL YYYY.MM.DD
    python calendar.py refresh SYMBOL YYYY.MM.DD-YYYY.MM.DD
    python calendar.py refresh SYMBOL YYYY.MM.DD@HH:MM
    python calendar.py refresh SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM

Refresh deliberately bypasses existing coverage, compares fresh provider records with cached records by
stable event identity, replaces changed records, adds newly discovered records, and preserves unchanged
records. A provider timestamp change is accepted during refresh so a rescheduled event can be updated.
Missing provider rows are not automatically deleted.

Coverage and acquisition watermarks are preserved because refresh is a state correction operation, not
coverage acquisition. The relevant Calendar specification is updated accordingly.

Calendar implementation version: 2.3.8; persistent schema remains 2.

Final validation requires fresh CI and Windows live-smoke validation using a known release interval.
Implementation refinements within 2.3.8:
- Refresh Detail enrichment is limited to ForexFactory events; Yahoo refresh never calls the ForexFactory Detail endpoint.
- Refresh machine-readable output is a single JSON document containing the refresh summary.
- An unchanged refresh does not rewrite calendar.json.

## 2.3.9 Refresh output duplication correction

The Windows refresh smoke revealed that machine-readable refresh output was emitted twice: first through the
generic query renderer and then again through the dedicated refresh JSON payload.

Correction:
- refresh machine-readable mode now emits exactly one JSON document;
- cleartext mode retains the event blocks plus one human-readable refresh summary;
- regression coverage asserts that machine-readable refresh produces exactly one non-empty stdout line;
- Calendar implementation version: 2.3.9; persistent schema remains 2.

Fresh CI and Windows refresh smoke remain required before PASS.
## 2.3.10 Refresh mutation-detection validation

A Windows smoke raised a concern that a manually changed cached release value was not detected by refresh.
Source inspection showed that the refresh comparator already compares complete event records, but the regression
suite did not reproduce a locally mutated actual field. Therefore the behavior was insufficiently tested.

Correction:
- CI now explicitly changes cached actual to a synthetic wrong value and verifies refresh replaces it with
  the fresh provider value and reports changed=1;
- refresh --debug now prints the active calendar.json path before loading it, making an incorrect
  SMC_DATA_ROOT immediately observable;
- specification now explicitly requires local cache mutations to be detected and corrected.

Calendar implementation version: 2.3.10; persistent schema remains 2.

Fresh CI and a Windows refresh smoke using --debug remain required before PASS.


## 2.4.0 source-quality implementation

Applied the full Calendar source-quality refactor after the 2.3.10 refresh fixes.

- Root `calendar.py` remains the stable executable entrypoint.
- Calendar implementation modules moved under `CALENDAR/`; default cache is `CALENDAR/calendar.json`.
- Configuration, explicit record shapes, domain rules, persistence/locking, provider access, parsing, operations, presentation, CLI dispatch, and compatibility facade are separated.
- Generated `Function/Variables/Local variables/Local state` comment noise was removed while meaningful rationale comments remain.
- Calendar document validation was decomposed into focused validators.
- Windows lock identity is derived from the absolute Calendar file path, so distinct DATA_ROOT values do not share one fixed mutex.
- Rendered ForexFactory rows without a concrete clock no longer become fabricated 00:00 events; invalid clocks fail closed.
- TypedDict contracts document event, Detail, coverage, watermark, provider-result, and refresh-summary fields.
- Provider HTTP error handling is narrowed to expected network/decode failures.
- Persistent schema remains V2; implementation version advances to 2.4.0.

The existing acquisition transaction still holds the Calendar lock across provider I/O. Moving network I/O outside that lock requires an optimistic/two-phase commit protocol to preserve concurrent deletion and refresh semantics, so it remains a separate future change rather than being mixed into this behavior-preserving refactor.
