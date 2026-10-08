# CURRENT AUDIT OVERRIDE — 2026-10-08 (Calendar + Market Data)

## Release-gate audit

Scope: Calendar and Market Data only. Mapper/Monitor are intentionally out of scope.

### Corrections applied
- Consolidated `specifications/market_data_specification.md` to one canonical §0–§25 set; removed the duplicated §7–§25 block.
- Canonical credential layout is now `PROVIDERS/<provider>.apikey`; no `apikeys/` directory is used.
- Shared credential loading rejects missing, empty, placeholder, and all multi-line credentials without exposing secrets.
- Market Data CLI now selects the canonical direct LSE provider instead of the obsolete Yahoo Charts provider.
- LSE Market Data acquisition now paginates forward using canonical timeframe boundaries and rejects non-progressing pagination.
- Market Data normalization now rejects provider timestamps that are not exact canonical timeframe starts.
- Persisted Market Data validation now supports W1/MN1 and validates calendar-derived completion boundaries for completed/current candles.
- Calendar LSE credentials now use the shared provider loader.
- Removed obsolete Calendar prev/next week/month public scopes from implementation, help, and specification.
- ForexFactory events now persist the canonical provider Detail URL in `details.url`; Yahoo news continues to persist its provider link.
- `next` now recognizes merged economic events whose ForexFactory contribution is present in `sources`, even when the merged primary `source` is LSE.
- Calendar and Market Data CI contract tests were synchronized with the corrected provider/scope/URL contracts.

### Static audit result
PASS for specification/code consistency across the corrected Calendar + Market Data release scope.

### Runtime validation
Fresh CI status for the latest main commit is not yet exposed by the connected GitHub status endpoint, so runtime execution evidence remains pending. No Mapper/Monitor failure is counted against this release gate.

---


## Post-audit correction — Calendar 2.4.11 + Market Data integrity

### Scope
Re-audited the active Calendar and Market Data specifications against the implementation after the open-start range changes.

### Corrections
- Calendar `next` now considers only scheduled ForexFactory economic events; Yahoo Finance published/current news is never treated as a future scheduled event.
- Plain open-start Calendar `--range -END` is cache-only; provider acquisition occurs only with the trailing `refresh` modifier.
- Yahoo acquisition persists provider/symbol coverage for the successfully queried historical/current interval while retaining `historical_coverage=NOT_GUARANTEED`.
- Normal Calendar output no longer exposes provider `ERROR` records or exception text; aggregate `PARTIAL/UNAVAILABLE` status remains available.
- Market Data range inclusion now uses canonical candle `timestamp` with an exclusive END boundary.
- Persisted Market Data validation now rejects negative volume, duplicate current/completed candle identity, invalid current completion boundaries, and unsupported timeframes.
- Yahoo malformed OHLC records now fail instead of being silently discarded.
- H4 aggregation now requires contiguous H1 source timestamps at the expected boundaries.
- Market Data help and normalization signature were synchronized with the active implementation.
- Removed the unused tracked `MARKET_DATA/market_data_cache.json` artifact.

### Validation
- Calendar workflow #435 (`d3a076a9b6693cdf1bae438bd5238b9351ca1966`) — SUCCESS.
- Market Data workflow #50 (`d3a076a9b6693cdf1bae438bd5238b9351ca1966`) — SUCCESS.
- Both workflows passed compile and their contract/regression test steps.
- Implementation and specification changes are on `main`.

### Audit status
PASS for the corrected scope. Yahoo Finance is explicitly treated as a published/current-news source, not a scheduled future-event provider.

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


## 2.4.0 post-refactor validation

The refactored Calendar source tree was revalidated after the corrective import, facade, lock, fixture, and CLI-test-boundary fixes.

Validation evidence:
- GitHub Actions Calendar workflow run `37233383361` on commit `7739fc5de903a0c247657ddd41d02156e959ce8b` completed successfully.
- Root `calendar.py` compiled successfully.
- Every `CALENDAR/` implementation module compiled successfully.
- The complete existing Calendar unit/runtime contract suite completed successfully.
- The new rendered-time regression passed: non-concrete ForexFactory time is rejected instead of becoming 00:00.
- The repository-root entrypoint and `CALENDAR/` source/cache layout are synchronized.
- Runtime cache ignore rules now include `CALENDAR/calendar.json` and its POSIX lock file.

Source-quality result:
- The former 2768-line monolith is split by responsibility.
- Generated Function/Variables/Local-variable comment noise is removed from implementation modules.
- Calendar document validation is decomposed.
- The semantic/domain boundary is explicitly documented for MQL4/MQL5 portability.
- Windows Calendar locking is isolated by the absolute Calendar file path.

Remaining deliberate scope boundary:
network provider I/O still runs within the existing Calendar transaction lock. Moving it outside the lock requires a two-phase/optimistic persistence protocol and is not mixed into this behavior-preserving source refactor.


## 2.4.1 ForexFactory Detail failure isolation and retry correction

Audit identified a state-consistency defect in the 2.4.0 post-refactor implementation: Detail requests were isolated correctly and the provider was reported as PARTIAL, but the acquisition workflow still recorded the affected ForexFactory coverage as COMPLETE and advanced the watermark. Because an empty details.specs list can also be a legitimate Detail result, that state could suppress the required retry.

Correction:
- ForexFactory coverage is now recorded per acquired gap as COMPLETE only when that gap has no Detail failures;
- a gap with one or more Detail failures is recorded as PARTIAL;
- explicit acquisition does not advance the ForexFactory watermark when any acquired gap is Detail-partial;
- current-mode acquisition follows the same rule and retains its previous successful watermark;
- partial coverage remains uncovered to the existing find_uncovered_intervals logic and is therefore retried;
- the existing provider-level PARTIAL result and Detail failure count are retained;
- regression coverage now verifies three base events with one Detail failure, successful retry/promotion to COMPLETE, watermark behavior, and current-mode retry semantics;
- the stale regression expecting Detail failure to raise ProviderError was replaced with the intended isolated-failure contract.

The Calendar specification and design documents now define this retry contract explicitly. Implementation version: 2.4.1; persistent schema remains 2.

Validation status before final CI/live smoke: implementation and specification changes applied; fresh GitHub Actions validation is required for PASS.


## 2.4.2 Successful no-match status correction

Audit finding: a valid Yahoo Finance ticker with a successful empty news result was reported as `PARTIAL`, which incorrectly implied incomplete provider acquisition. For an unknown/non-matching ticker such as `CCCC`, the correct semantic state is a successful no-match.

Correction:
- Yahoo explicit/current/refresh acquisition now reports `NO_MATCH` when the provider succeeds but returns no matching events;
- `NO_MATCH` is distinct from provider failure, incomplete acquisition, and verified FX-pair unavailability;
- aggregate query status becomes `NO_RELEVANT_EVENT` when all applicable providers return `NO_MATCH`;
- successful no-match acquisition may advance the Yahoo watermark according to normal successful-acquisition semantics;
- Calendar specification and design now define this contract;
- regression coverage verifies an empty Yahoo acquisition for `CCCC` produces `NO_MATCH` and `NO_RELEVANT_EVENT` without recording a failure.

Implementation version: 2.4.2; persistent schema remains 2.
Validation: fresh GitHub Actions Calendar workflow required before final PASS.


## 2.4.2 Source activity documentation

User-requested source-quality correction: add concise source comments/docstrings describing the activity of Calendar functions and meaningful state variables.

Implementation:
- documented Calendar functions across the implementation modules with concise activity descriptions;
- documented the active Calendar storage variables PROJECT_ROOT, DATA_ROOT, and CALENDAR_FILE;
- added module-level comments clarifying that domain/provider/parser/operation/presentation/CLI state is request/input/output-local rather than hidden persistent module state;
- retained existing configuration variable comments;
- root calendar.py remains the stable entrypoint and required no additional function documentation;
- no runtime logic, persistent schema, status semantics, provider behavior, or CLI contract was changed.

Validation required:
- fresh Calendar GitHub Actions compile/runtime workflow after the documentation-only source changes;
- source inspection confirming the comments/docstrings are present without generated comment noise.


### Post-edit source audit
- Activity documentation is placed after the complete Python function signature, so multi-line signatures remain syntactically valid.
- All Calendar implementation functions have either the new activity docstring or an existing function docstring; no function was left undocumented by the source-documentation pass.
- Meaningful module-level state variables in storage are explicitly described; module-level comments clarify request/input/output-local state in the other implementation layers.
- No functional code path was intentionally changed by the documentation pass.
- CI status is not yet observable for the latest push from the available GitHub status interface, so this documentation change is not marked CI-PASS yet.


### Source attribution
- Added the requested attribution header to the Calendar Python source files: `(c) Istvan Jakab <istvanhlc230@gmail.com>`.
- No runtime logic was changed.


# Market Data implementation review

**Status: PASS**

## Scope completed
- Added the Calendar-style modular MARKET_DATA/ implementation layout.
- Kept market_data.py as the root executable entry point.
- Added UML-style module relationships, variable naming and function ownership to specifications/market_data_specification.md.
- Reconciled the former single-file V1 wording with the approved modular structure.
- Implemented models, provider abstraction, Yahoo Charts acquisition, normalization, persistence, acquisition planning, merge/deduplication, retention, current-candle handling, timeframe orchestration, symbol-level transaction handling and CLI parsing.
- Added MARKET_DATA/market_data_cache.json as the provider-cache location.
- Preserved the canonical symbol-scoped mapper-facing JSON layout under <DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json.
- Preserved volume.total; the requested removal of total volume was explicitly withdrawn.

## Automatic audit corrections
1. Added the missing CLI main delegation.
2. Corrected incremental acquisition to begin after the persisted last completed candle.
3. Corrected empty-state acquisition so the latest completed candle is obtained.
4. Corrected latest-candle selection to use canonical completion time and a timeframe-aware window.
5. Corrected completion-hint handling so a provider hint cannot mark a future canonical boundary complete.
6. Corrected persisted availability validation to fail closed instead of silently repairing inconsistent bounds.
7. Expanded persisted OHLC and volume integrity validation.
8. Corrected stale current-snapshot promotion after its completion boundary.
9. Corrected H4 current-state acquisition through hourly aggregation.

## Structural audit
- Dependency direction is acyclic: CLI -> service -> provider/normalization/persistence/models.
- Provider-specific state terminates at the provider boundary.
- Persistence does not perform SMC interpretation.
- Current snapshots remain separate from completed candles.
- Candle identity is deterministic.
- Multi-timeframe updates are assembled in memory and atomically persisted only after all requested timeframes succeed.
- No Market Data runtime dependency on mapper, monitor or legacy SMC engines was introduced.
- No canonical SMC logic was introduced.

## Runtime validation note
The connected repository currently exposes no Python test runner or CI workflow for this module, and the execution environment cannot resolve the public GitHub host for a local checkout. No false claim of a live provider integration test is made. The final PASS is the result of the specification/code structural audit after the automatic correction loop.

## Final result
**PASS — Market Data specification structure and implementation audit complete.**

# Market Data date/time alignment review

**Status: IMPLEMENTED — validation pending**

## Change requested
Market Data CLI date/time handling is now aligned with the established Calendar convention.

## Implementation
- Replaced ISO-8601 `--starttime` / `--endtime` input semantics with independent:
  - `--startdate YYYY.MM.DD`
  - `--starttime HH:MM`
  - `--enddate YYYY.MM.DD`
  - `--endtime HH:MM`
- Date and time parsing is strict and UTC-based.
- No machine-local timezone is assumed.
- Date-only start resolves to UTC `00:00`.
- Date-only end resolves to the following UTC day `00:00` as an exclusive boundary.
- Time-only boundaries use the current UTC calendar date.
- A single UTC `now` value is captured during request parsing so defaults are internally consistent.
- Seconds, offsets, malformed dates, malformed times and invalid calendar values are rejected.
- `--lastcandle` is mutually exclusive with any explicit date/time boundary component.
- Existing completed-candle acquisition modes and `--live` semantics remain unchanged.

## Specification synchronization
`specifications/market_data_specification.md` was updated in the same implementation iteration with the CLI contract, resolution table, validation rules, and new function ownership for `parse_calendar_date`, `parse_calendar_time`, and `resolve_boundary`.

## Validation
Repository-level runtime/CI execution remains unavailable from the current environment. The implementation should be syntax-checked and the CLI boundary matrix tested in the developer environment before marking this change PASS.


## Market Data CLI mode correction

**Status: IMPLEMENTED — validation pending**

The previous Market Data date/time CLI iteration used independent `--startdate`, `--starttime`, `--enddate`, and `--endtime` options and a `--live` flag. That was not aligned with the Calendar scope grammar.

Correction:
- historical acquisition now uses Calendar-compatible `--range` scope forms;
- `--range current` is the current in-progress candle mode;
- `--lastclosed` is the explicit latest completed/closed candle mode;
- `--live` and the old `lastcandle` terminology are removed from the Market Data request contract;
- the request model now uses `current` and `last_closed_only`;
- `lastclosed` uses the latest-completed provider path and completion validation;
- `current` and `lastclosed` are mutually exclusive.

Specification synchronized in `specifications/market_data_specification.md`.

Validation status:
- Repository source changes are committed.
- Python runtime/CLI matrix validation remains pending because no local execution environment is available through the connected repository interface.


# Calendar 2.4.3 --time CLI correction

**Status: IMPLEMENTED — validation pending**

## Change requested
Restore a Calendar CLI time-only shorthand so a concrete --time HH:MM without an explicit date resolves on the current UTC calendar day, while retaining the canonical internal YYYY.MM.DD@HH:MM scope grammar.

## Implementation
- Added --time HH:MM to the Calendar CLI.
- python calendar.py SYMBOL --time HH:MM resolves to <current UTC date>@HH:MM.
- python calendar.py SYMBOL YYYY.MM.DD --time HH:MM resolves to YYYY.MM.DD@HH:MM.
- The same shorthand is accepted for explicit refresh and symbol-scoped delete operations.
- --time is rejected when combined with an explicit scope that already contains time or represents a range/current/latest/next operation.
- Bare delete cannot use --time.
- The current date is obtained from the Calendar domain's canonical UTC clock (utc_now()), not the machine-local date.
- The CLI normalizes the shorthand before existing scope parsing, so provider routing, coverage, watermark, persistence and interval semantics are unchanged.
- Added concise source comments explaining why the shorthand is normalized to the canonical date@time grammar.
- Updated Calendar help text and specifications/calendar_specification.md.
- Bumped Calendar implementation version from 2.4.2 to 2.4.3; persistent schema remains V2.

## Validation
- Static source inspection completed after the implementation.
- Repository test directory is intentionally absent under the current project structure, so no repository-root test suite was added.
- Fresh runtime/CI validation is still required before marking this change PASS.


## Calendar 2.4.3 post-audit correction

**Status: IMPLEMENTED — validation pending**

The Calendar audit identified two consistency issues and both were corrected:

- CALENDAR/operations.py: successful Yahoo explicit acquisition with matching events now reports OK instead of PARTIAL. PARTIAL remains reserved for genuinely incomplete acquisition. Successful empty acquisition remains NO_MATCH.
- specifications/calendar_specification.md: the public delete grammar now explicitly documents delete SYMBOL --time HH:MM and delete SYMBOL YYYY.MM.DD --time HH:MM, matching the already-supported CLI implementation.

The existing --time semantics, UTC normalization, provider routing, watermark handling, atomic persistence, and persistent schema were not otherwise changed.

Implementation version is 2.4.4; persistent schema remains V2.

Validation requirement: run the Calendar CLI/parser matrix and fresh GitHub Actions validation before marking this correction PASS.

## Calendar 2.4.3 refresh aggregate-status correction

**Status: IMPLEMENTED — validation pending**

The post-audit refresh status inconsistency is corrected.

- CALENDAR/cli.py no longer derives refresh status only from failures and changed/added counts.
- Refresh now uses the canonical domain provider-status aggregation before applying the refresh-specific REFRESHED/UNCHANGED distinction.
- All SKIPPED_NO_FOREX_PAIR results now surface as NO_FOREX_PAIR.
- A successful provider combined with SKIPPED_NO_FOREX_PAIR surfaces as PARTIAL.
- Provider ERROR combinations remain UNAVAILABLE when all providers fail and PARTIAL when at least one provider succeeds.
- BOOTSTRAP_REQUIRED remains observable instead of being collapsed into UNCHANGED.
- Successful refreshes with changes remain REFRESHED; successful refreshes without changes remain UNCHANGED.
- specifications/calendar_specification.md now defines these refresh aggregate rules explicitly.
- Added concise source comments explaining why verified Yahoo FX-pair unavailability must not be hidden by UNCHANGED.

Implementation version is 2.4.4; persistent schema remains V2.

Validation requirement: run the Calendar CLI status matrix and fresh GitHub Actions validation before marking this correction PASS.

## CLI help/parameter restoration correction — 2026-10-05

**Status: IMPLEMENTED — validation pending**

The CLI audit found two presentation/contract regressions:

- Calendar --time HH:MM was listed redundantly in both the FLAGS and SCOPE help sections. The duplicate SCOPE entry was removed; --time remains documented once as a flag and in the concrete usage forms.
- Market Data's explicit current mode had been lost from the actual CLI surface even though the specification model already used current. MARKET_DATA/cli.py now exposes --current and rejects combining it with --range or --lastclosed.
- Market Data help/specification now present --current as the public current-candle parameter instead of the obsolete --range current form.
- Existing useful Market Data parameters remain: --symbol, --timeframes, --range, --lastclosed, --debug, and --help.

No SMC semantics or persistent schema were changed.

Validation requirement: run the CLI help/parser matrix for both Calendar and Market Data before marking this correction PASS.

## Calendar 2.4.4 date / last-update CLI correction

**Status: IMPLEMENTED — validation pending**

The CLI/help audit identified that the public help did not expose --date and repeated equivalent --time usage forms.

Corrections:
- --date YYYY.MM.DD is now supported for exact-day scope selection;
- --date YYYY.MM.DD --time HH:MM is supported for exact-minute lookup;
- --time HH:MM without --date still resolves to the current UTC calendar day;
- the same date/time flag construction is supported by query, explicit refresh, and scoped delete;
- --last-update is now a read-only watermark lookup returning last_successful_at for each applicable provider;
- missing provider watermarks are reported as null/N/A and never fabricated;
- help usage was consolidated so equivalent --time forms are not redundantly listed;
- specifications/calendar_specification.md records the new CLI contract;
- source comments/docstrings were retained for the new semantic paths.

Implementation version is 2.4.4; persistent schema remains V2.

Validation requirement: run the CLI parser matrix covering --date, --time, --date+--time, invalid combinations, and --last-update, then run fresh GitHub Actions validation before marking PASS.


## Calendar 2.4.5 relative-day CLI scopes

**Status: IMPLEMENTED — validation pending**

Added the requested public relative-day scope parameters:
- `today` — current UTC calendar day;
- `tomorrow` — next UTC calendar day;
- `yesterday` — previous UTC calendar day.

The three scopes are resolved dynamically from Calendar's canonical `utc_now()`
clock and use the existing exact-day interval semantics. They are available to
normal query/acquisition, explicit refresh, and symbol-scoped delete. They are
not provider-native ForexFactory navigation parameters and are distinct from
`current`, `latest`, and `next`.

Synchronized:
- `CALENDAR/domain.py`
- `CALENDAR/config.py` (implementation version 2.4.5)
- `specifications/calendar_specification.md`

Validation requirement: run the relative-scope parser matrix around UTC midnight,
plus query/refresh/delete routing checks, and fresh GitHub Actions before marking
this change PASS.

# Calendar 2.4.6 current refresh/error-visibility audit and correction

**Status: IMPLEMENTED — validation pending**

## Audit findings

The `current` acquisition path already re-contacted applicable providers on every invocation when a committed
provider+symbol watermark existed. The watermark was therefore correctly acting as an incremental result cursor,
not a provider-call suppression mechanism. The public specification was misleading because it described `current`
primarily as incremental acquisition and did not explicitly guarantee unconditional provider refresh.

A concrete output-boundary defect was also found: `CALENDAR/cli.py` passed the complete internal
`provider_results` list directly to the public query presentation. A caught provider `ERROR` record could therefore
expose its `error` text in normal JSON/cleartext output instead of remaining diagnostic-only.

A state-consistency defect was found in both normal/current acquisition and forced refresh: a failed ForexFactory
Detail request produces an empty `details.specs` list. A normal event merge could replace an already populated cached
Detail list with that empty list before marking the acquisition PARTIAL.

## Automatic corrections

- Updated `specifications/calendar_specification.md` to baseline 2.4.6.
- Defined `current` as an always-refreshing acquisition/query operation whenever the applicable provider has a
  committed successful watermark.
- Explicitly defined the watermark as an incremental output boundary, not a reason to skip provider acquisition.
- Defined provider acquisition errors as diagnostic-only for normal `current` output.
- Added the `current` public-output rule: provider `ERROR` records are omitted and diagnostic fields
  (`error`, `reason`, `detail_failures`) are not returned.
- Preserved aggregate status semantics, so `UNAVAILABLE` and `PARTIAL` remain machine-readable.
- Kept `--debug` provider diagnostics on stderr only.
- Extended `domain.merge_events()` with stable-ID-aware Detail-failure preservation.
- Updated explicit acquisition and `current` acquisition to pass failed ForexFactory Detail IDs into the merge.
- Updated explicit refresh merge handling with the same preservation rule.
- A failed Detail refresh can no longer erase an already committed non-empty `details.specs` list.
- Updated `CALENDAR/config.py` implementation version to 2.4.6 and synchronized CURRENT/ERROR help text.
- Corrected the Calendar GitHub Actions regression suite: `today` is now tested as a valid relative-day scope.
- Added regressions proving `current` calls a provider on every invocation with an existing watermark.
- Added regressions proving Detail-failure preservation.
- Added a regression proving normal `current` stdout contains no provider exception text or `ERROR` provider record.

## Validation requirement

The updated Calendar source and inline CI contract must be run by GitHub Actions. PASS is not claimed until the
fresh workflow run for this change completes successfully.

# Calendar 2.4.6 audit correction — strict rendered ForexFactory event time

**Status: PASS — validated**

The first fresh CI run after the 2.4.6 changes exposed an existing parser/test inconsistency:
`parse_forexfactory_html_events()` silently discarded a titled rendered event whose provider time
was non-concrete (for example `Tentative`), while the Calendar regression contract requires fail-closed
handling for an event that cannot receive an exact timestamp.

Automatic correction:
- `CALENDAR/parsing.py` now raises `ProviderError` for a titled rendered row without a concrete HH:MM AM/PM clock;
- repeated/missing row times are no longer inherited from the previous event, preventing fabricated timestamps;
- `ForexFactoryHTMLCalendarParser` now has a class-level activity docstring and state-variable comments;
- the correction preserves the existing requirement that no synthetic midnight timestamp is created.

The existing Calendar specification already states that invalid rendered event clocks fail closed, so
no semantic specification change beyond the 2.4.6 current-refresh contract was required for this parser fix.

Fresh GitHub Actions validation completed successfully.

Validation run: `37297403084`
Commit: `1ad4747b83e9d5acdda6d6ae51884784a1f4ff55`
Compile: PASS
Calendar unit/runtime contract tests: PASS

# Calendar 2.4.7 audit — first-use current bootstrap refresh

**Status: PASS — validated**

The user-facing execution `python calendar.py USDHUF current` exposed a semantic contradiction:
the specification described `current` as always-refreshing, but `acquire_current()` still returned
`BOOTSTRAP_REQUIRED` and made no provider call when the watermark was missing.

Automatic correction:
- `acquire_current()` now performs provider acquisition on first use instead of terminating at a missing watermark;
- ForexFactory first-use `current` uses the bounded `(now - 1 day)` to `(now + 1 day)` midnight-aligned window;
- Yahoo first-use `current` performs its normal news acquisition;
- first-use successful acquisition persists `last_successful_at=now`;
- successful Yahoo `NO_MATCH` now persists its watermark because persistence is based on successful acquisition state,
  not only on non-empty result events;
- bootstrap-acquired events are persisted but are not returned as incremental `current` events because there is no prior
  watermark boundary;
- provider `BOOTSTRAP_REQUIRED` is no longer emitted by the `current` acquisition path;
- source comments/docstrings were extended for the new bootstrap state and variables.

Fresh GitHub Actions validation completed successfully.

Validation run: `37297837871`
Commit: `95ab66a8f5ddd4a9b7cb4ad625bff801d670bf9e` 
Compile: PASS
Calendar unit/runtime contract tests: PASS

# Calendar 2.4.8 — final audit snapshot

**Status: PASS — validated**

## Audit findings and corrections
- Plain `current` is cache-only and performs no provider/network I/O.
- The obsolete standalone `refresh SYMBOL SCOPE` command is removed.
- `refresh` is a trailing query modifier for current, relative-day, date and datetime scopes.
- `current refresh` uses the current incremental watermark interval, with a bounded first-use interval when no watermark exists.
- Refresh matching includes stable event IDs from the provider-side overlap envelope, so late ForexFactory Detail data can update an already committed event immediately before the incremental watermark.
- Rescheduled events that were already visible in the logical scope remain in refresh output by stable ID; overlap-only records outside the logical scope are merged silently.
- Obsolete `acquire_current`, `run_refresh`, and `BOOTSTRAP_REQUIRED` production paths were removed.
- The specification and CI contract were corrected for the trailing modifier grammar, overlap-boundary Detail semantics, rescheduled-event output, and Calendar 2.4.8 version alignment.

## Validation evidence
- Validated implementation snapshot: `0ca92512f359f03d1841131d27f5c6ebba5853c1`
- GitHub Actions run: `37300650748`
- Compile: PASS
- Calendar unit/runtime contract tests: PASS
- Job conclusion: SUCCESS

The passing run includes regression coverage for plain read-only `current`, trailing `refresh` parsing, `current refresh` delegation, late ForexFactory Detail refresh across the watermark boundary, explicit refresh rescheduling behavior, and the existing Calendar contract suite.

The final documentation synchronization is revalidated on the validation snapshot.

# Calendar 2.4.9 — CLI refresh result-boundary correction

**Status: PASS — validated**

A re-audit of the 2.4.8 snapshot found a real CLI-layer contract defect: `run_query()` reconstructed refresh output from the committed cache after the refresh operation had already produced its authoritative result. That second filtering pass could hide valid first-use refresh events and rescheduled events that moved outside the original logical interval. The same defect affected first-use `current refresh` because a missing watermark intentionally produces no plain-current cache boundary.

Automatic corrections:
- `CALENDAR/cli.py` now uses `refresh_result["events"]` directly for every refresh scope;
- CLI refresh output no longer reapplies committed coverage or watermark filters;
- Calendar version is 2.4.9;
- the acceptance specification explicitly makes the refresh operation result authoritative for public refresh events;
- CI adds CLI regressions for explicit first-use refresh, first-use `current refresh`, and rescheduled-event output;
- the obsolete active acceptance statement requiring `BOOTSTRAP_REQUIRED` for a missing watermark is removed;
- the Calendar CI workflow's remaining 2.4.8 version assertion was corrected to 2.4.9.

## Validation evidence

- Validated implementation snapshot: `c9ca9220980f5a036ef965e8465c635fe3599c7e`
- GitHub Actions run: `37303811257`
- Run number: `373`
- Compile: PASS
- Calendar unit/runtime contract tests: PASS
- Job conclusion: SUCCESS

The validation covers the existing Calendar contract suite plus CLI regressions for:
- first-use explicit refresh output;
- first-use `current refresh` output;
- rescheduled-event output by stable provider ID;
- trailing refresh grammar and rejection of the obsolete standalone refresh command.

The validated implementation source/specification snapshot is unchanged by the final documentation-only synchronization on `main`.

# Calendar + Market Data open-start range correction — 2.4.10

**Status: PASS — validated**

The requested open-start range form was restored across both CLI boundaries.

Supported forms:

    python calendar.py SYMBOL --range -YYYY.MM.DD
    python calendar.py SYMBOL --range -YYYY.MM.DD@HH:MM
    python calendar.py SYMBOL --range -YYYY.MM.DD@HH.MM
    python market_data.py --symbol SYMBOL --timeframes TF [TF ...] --range -YYYY.MM.DD
    python market_data.py --symbol SYMBOL --timeframes TF [TF ...] --range -YYYY.MM.DD@HH:MM
    python market_data.py --symbol SYMBOL --timeframes TF [TF ...] --range -YYYY.MM.DD@HH.MM

A leading `-` omits the start boundary. Calendar resolves the start from the latest recorded visible event for
the requested symbol. Market Data resolves the start independently for each requested timeframe from `available_end`,
the latest persisted completed candle. The explicit END remains the upper boundary.

The `HH.MM` spelling is accepted as a compatibility alias for the open-start datetime END and is normalized to
the canonical `HH:MM` representation.

Automatic corrections:
- Calendar parser accepts `--range` open-start syntax and resolves it against retained Calendar history;
- Calendar refresh reuses the same resolved interval;
- Market Data parser accepts the exact separate-token negative form `--range -END` through CLI preprocessing;
- Market Data acquisition planning starts from `available_end` rather than `available_start` for open-start ranges;
- Market Data date/time parsing no longer depends on Python's standard `calendar` module, avoiding the repository-root
  `calendar.py` name collision;
- Market Data retention normalizes persisted ISO timestamp strings before datetime comparison;
- Market Data request-mode field references were aligned with the canonical `last_closed_only` / `current` model;
- Calendar and Market Data specifications document the open-start range concept;
- Calendar CI covers parser and range-boundary resolution;
- Market Data CI covers parser, per-timeframe range resolution, and the production timeframe update path.

## Validation evidence

- Tested implementation snapshot: `3b7d5deb296b86db26416a2174c89c408c894900`
- Calendar GitHub Actions run: `37305301336` (run #395) — SUCCESS
- Market Data GitHub Actions run: `37305301440` (run #10) — SUCCESS
- Compile: PASS
- Calendar contract tests: PASS
- Market Data range contract tests: PASS

The final implementation and specification state are on `main`.

# Calendar + Market Data post-audit correction — 2.4.11 / current Market Data integrity

**Status: PASS — validated**

The post-2.4.10 audit was completed against the active Calendar and Market Data specifications and the implementation on `main`.

## Corrected findings

- Calendar next now considers only scheduled ForexFactory economic events. Yahoo Finance is treated as a published/current-news source and is never a future scheduled-event source.
- Calendar plain open-start --range -END is cache-only. It resolves the lower boundary from retained visible event history and does not contact providers unless the trailing refresh modifier is present.
- Calendar explicit Yahoo acquisition now records provider+symbol coverage for the successfully completed historical portion of the requested interval while retaining historical_coverage=NOT_GUARANTEED.
- Calendar normal public output no longer exposes provider ERROR records or provider exception text; aggregate PARTIAL/UNAVAILABLE status remains observable.
- Calendar scoped delete now rejects current, latest, next, and open-start range scopes.
- Market Data historical range inclusion now uses the canonical candle interval start: start_time <= timestamp < end_time; completion is validated separately.
- Market Data persisted-state validation now rejects negative persisted volume and current/completed candle identity overlap, and verifies current completion boundaries against the timeframe.
- Yahoo H4 aggregation now requires a contiguous expected H1 sequence before producing a composite candle.
- Yahoo Charts malformed OHLC records now fail explicitly instead of being silently discarded.
- Market Data CLI help no longer advertises the obsolete --range current form.
- The obsolete committed Market Data cache artifact and unused provider cache state were removed.

## Validation evidence

Validated implementation snapshot:

d877edf11167dab3636f283235d2bebb050df489

Calendar GitHub Actions:
- run #423
- run ID 37308308110
- Compile: PASS
- Calendar contract tests: PASS

Market Data GitHub Actions:
- run #38
- run ID 37308308128
- Compile: PASS
- Market Data range/integrity contract tests: PASS

The final validated CI state is green. The next behavior is intentionally consistent with the provider boundary: Yahoo provides historical/current news, while scheduled future events come from ForexFactory.

# Calendar + Market Data post-audit correction — 2.4.11 final validation

**Status: PASS — validated**

The post-2.4.10 audit was completed against the current implementation and owner specifications. The
Yahoo provider boundary was also corrected: Yahoo supplies published/current news and is not a source of
scheduled future Calendar events. `next` therefore considers only visible ForexFactory economic events.

## Corrections validated

- Calendar `next` excludes Yahoo Finance news from future-event lookup.
- Calendar plain open-start `--range -END` is cache-only; only trailing `refresh` performs provider acquisition.
- Calendar explicit Yahoo acquisition records successful provider/symbol coverage while preserving
  `historical_coverage=NOT_GUARANTEED`.
- Calendar normal query and refresh JSON output omit provider `ERROR` records and exception text while
  retaining aggregate failure status.
- Calendar scoped delete rejects query-only `current/latest/next` and open-start ranges.
- Market Data range inclusion uses canonical candle start timestamps with half-open `[start,end)` semantics.
- Market Data persisted validation rejects negative volume and completed/current identity conflicts and
  validates timeframe-derived completion boundaries.
- Canonical completion time is authoritative; provider completion hints cannot override the timeframe boundary.
- H4 aggregation requires contiguous H1 source intervals.
- Malformed Yahoo OHLC records fail explicitly instead of being silently dropped.
- The obsolete persistent Market Data cache artifact and cache-path contract were removed.
- Specifications and CI regression tests were updated to cover these contracts.

## Validation evidence

Final validated implementation snapshot:

`62bb5a5ffc170f13d7093160bfa28d583b260bc3`

Calendar GitHub Actions:
- run #433
- run ID `37326180189`
- Compile: PASS
- Calendar unit/runtime contract tests: PASS
- Conclusion: SUCCESS

Market Data GitHub Actions:
- run #48
- run ID `37326180436`
- Compile: PASS
- Market Data range/integrity contract tests: PASS
- Conclusion: SUCCESS

Earlier intermediate failing workflow runs were caused by outdated CI version assertions and one test-fixture
timestamp choice, plus a temporary helper naming collision; these were corrected and are not part of the
final validated snapshot.

The final main branch therefore has a green Calendar and Market Data validation state at the snapshot above.
# Market Data post-audit correction — incremental boundary / persistence integrity

**Status: CI PASS — re-audit completed**

Audit findings corrected against the active Market Data specification:

- normal incremental acquisition now starts at the next canonical timeframe interval after `available_end`;
- open-start `--range -END` remains intentionally inclusive at `available_end` for boundary reacquisition/deduplication;
- Market Data completed-range filtering is canonical candle-start based (`start_time <= timestamp < end_time`) with completion checked independently;
- H4 current aggregation now fails closed when its hourly source sequence is not contiguous;
- persisted Decimal validation now enforces plain base-10 strings and the approved maximum of 18 fractional places;
- specification terminology was synchronized to `--current` / `--lastclosed` and removed stale `live` / `lastcandle` references;
- the specification no longer claims `--lastclosed` refreshes the current snapshot.

Validation evidence:

- Final source/spec commit: `f4508c12099f5310843ee0296021dde4d8622e9d`;
- Market Data GitHub Actions run: `37539850382` — SUCCESS;
- Calendar GitHub Actions run: `37539850350` — SUCCESS.

Remaining audit note: Yahoo-specific W1/MN1 and session-calendar boundary behavior is not changed here because the canonical project contract does not yet define calendar-session completion semantics for those provider intervals. No provider-specific boundary rule was invented during this correction.

## Market Data corrective audit — LSE pagination and persisted-boundary validation

### Scope
Corrected the latest re-audit findings for the Market Data implementation.

### Corrections
- LSEMarketDataProvider.fetch_range() now pages forward within one logical requested range instead of treating the 5000-row REST page cap as a complete result.
- Pagination advances from the last returned candle to the canonical next interval boundary and fails closed if a page does not make forward progress.
- Persisted completed candles now require timestamp == canonical_interval_start(timestamp, timeframe) and completion_time == canonical_interval_end(timestamp, timeframe).
- W1 and MN1 completed-candle boundary rejection is covered by regression tests.
- --lastclosed is now rejected with every historical range form, including open-start --range -END.
- Regression coverage now includes LSE multi-page range acquisition and the open-start --lastclosed conflict.
- Market Data specification now explicitly documents LSE pagination behavior and persisted canonical timestamp/completion invariants.

### Validation
- Implementation commit sequence before CI:
  - be642fbe3184b2877c71cc252804b22808dc34c3 — LSE pagination.
  - ab00f77191d061b89e2d493dcb1c5bd58989a13 — persisted canonical candle boundaries.
  - c719ad33bd774f8d7d6249196cde8fcde0136399 — --lastclosed range exclusion.
  - 6a4a73507bdcc58241251a2a273b1df426c8ad96 — pagination/CLI regressions.
  - 9eaf6ff808992c2a60049987327fad31d5ffe477 — specification pagination/test contract.
  - 9a8f9b0cbd48fb7c575064db87b4a0f309624913 — W1/MN1 completed-boundary regression tests.
  - fa2c0016238fccd29c6d5475923aa7052c56d9cd — canonical persisted timestamp specification update.
- Market Data CI run 37662822203 on commit c9ab8d63f651c9b520f70937fcd05f1cc71b7d60 — SUCCESS.
- Calendar CI run 37662822220 on the same commit — SUCCESS.
- Compile and Market Data contract/regression tests passed.

### Audit status
PASS


## Calendar relative-query audit — 2026-10-08

Scope: Calendar only; Mapper/Monitor remain out of release scope.

Specification/code audit:
- RESTORED actual as the canonical current-UTC-day query; today remains a compatibility alias.
- Added relative CLI grammar: current day/week/month, next, next day/week/month, prev, prev day/week/month.
- next and prev remain event-relative single-event lookups.
- Added news active-event query with NEWS_ACTIVE / NO_ACTIVE_NEWS status.
- Added CLI parsing, domain interval resolution, query functions, help text, version 2.6.0, and CI contract tests.
- Relative period queries are cache-only unless trailing refresh is used.
- next, prev, latest, and news reject refresh.
- Relative scopes are rejected for deletion.
- Active news uses economic events from LSE and/or ForexFactory whose timestamp is within the current UTC minute; Yahoo published news is not treated as a scheduled active event.

Static audit result: PASS for the implemented grammar and cross-module consistency.

Runtime CI status: PENDING. GitHub combined-status endpoint currently reports no status entries for the latest commit, so runtime PASS is not claimed.
