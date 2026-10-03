# Calendar Module Specification

**Status:** Current V1 implementation specification for `calendar.py`.
**Scope:** ForexFactory economic-calendar acquisition, parsing, normalized event persistence, local time-based query API, explicit deletion, coverage tracking, locking, atomic persistence, and the machine-readable contract consumed by the Monitor.
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. Calendar/news data is external runtime context and must never redefine canonical SMC rules.

---

# 0. PURPOSE AND HARD BOUNDARIES

## 0.1 Finished-product role

`calendar.py` is the standalone economic-calendar data layer.

Responsibilities:

1. acquire economic-calendar data from ForexFactory;
2. parse and normalize provider records;
3. normalize event times to canonical UTC;
4. maintain one global `calendar.json`;
5. track validated acquisition coverage;
6. provide a local time-based query API;
7. provide explicit deterministic deletion;
8. preserve last-known-good data on acquisition failure;
9. expose machine-readable query results for Monitor and other consumers.

## 0.2 Explicit non-responsibilities

`calendar.py` must not:

- calculate BOS, CHoCH, IDM, Dealing Range, retracement, POI lifecycle, target, RR, or entry authorization;
- modify Market Data or Structures JSON;
- create symbol-specific News JSON files;
- place, modify, or close orders;
- decide whether a news event makes a setup valid;
- own Monitor alert deduplication;
- decide whether an event is active for trading purposes;
- define SMC execution policy.

The Monitor decides what queried News information means for runtime warning behavior.

## 0.3 Single persistence artifact

V1 has exactly one persistent calendar data file:

```text
<DATA_ROOT>/calendar.json
```

No symbol-specific News JSON, separate cache JSON, or persistent history JSON may be created.

Temporary files used internally for atomic replacement are transient implementation artifacts and are not additional persisted data stores.

## 0.4 Missing calendar.json

`calendar.json` is optional.

When it does not exist:

- symbol-only query operations return a valid empty result;
- no automatic download occurs merely because the file is missing;
- a scope-bearing command may create it after successful acquisition;
- the Monitor may continue canonical processing and record/report no calendar data.

A malformed existing `calendar.json` is a data-integrity error and is not replaced silently.

---

# 1. SOURCE AND PROVIDER BOUNDARY

## 1.1 V1 provider

V1 uses:

```text
ForexFactory economic calendar
https://www.forexfactory.com/calendar
```

The provider implementation is isolated behind acquisition/parsing functions so a future provider can replace ForexFactory without changing the normalized event or query contract.

## 1.2 Provider request mapping

The public CLI does not expose provider-specific query flags.

The following canonical scopes are resolved internally to UTC intervals:

| CLI scope | Meaning |
|---|---|
| `today` | current UTC calendar day |
| `next_day` | following UTC calendar day |
| `week` | current UTC calendar week |
| `next_week` | following UTC calendar week |
| `month` | current UTC calendar month |
| `next_month` | following UTC calendar month |
| `YYYY.MM.DD` | explicit UTC calendar day |
| `YYYY.MM.DD-YYYY.MM.DD` | inclusive UTC date range |
| `today@HH:MM` | today plus reference time |
| `YYYY.MM.DD@HH:MM` | explicit date plus reference time |

ForexFactory-specific date spelling and URL parameters remain internal provider concerns.

The current provider parser uses ForexFactory's structured embedded `days` JSON payload as the canonical acquisition source. The `days` array boundary is determined by JSON decoding rather than a regex-selected closing bracket, so nested JSON values cannot truncate the provider payload. Each event record provides the provider event ID (`id`), canonical currency (`currency`), event title (`name`), numeric UTC epoch (`dateline`), impact (`impactName`, with `impactClass` as fallback), and source values (`actual`, `forecast`, `previous`). The provider's `country` field is not a canonical currency source and must never be used in place of `currency`. Provider-wide events may use `currency = ALL`. The HTML row parser remains available only as a compatibility parser and is not used for canonical persistence. Because the structured event `dateline` is already an epoch timestamp, no regional timezone conversion is required for canonical event timestamps.

## 1.3 Request policy

Use a bounded request timeout and the approved baseline browser headers.

A provider transport/status/parsing failure must never be converted into successful empty data.

HTTP success alone is not acquisition success; the response must parse and normalize successfully.

---

# 2. CLI CONTRACT

## 2.1 Canonical grammar

The CLI is strictly positional:

```text
python calendar.py [scope] [symbol] [evaluation] [--cleartext]
python calendar.py delete [scope]
python calendar.py delete
```

The supported flag-style options are:

```text
-h
--help
--cleartext
```

`--cleartext` is valid only with a symbol query. It changes presentation only; the default output remains machine-readable JSON.

There is no public compatibility mode for the former flag-based interface.

## 2.2 Scope vocabulary

Valid scope values are:

```text
today
next_day
week
next_week
month
next_month
today@HH:MM
YYYY.MM.DD
YYYY.MM.DD@HH:MM
YYYY.MM.DD-YYYY.MM.DD
```

The `@HH:MM` suffix supplies the evaluation reference time. It does not narrow acquisition below the containing calendar day.

All internal timestamps and scope boundaries are UTC.

## 2.3 Symbol

A Calendar symbol query accepts either:
- a supported standalone three-letter currency code; or
- a six-letter FX pair built from:

```text
USD EUR GBP JPY CHF AUD CAD NZD CNY HUF
```

Examples:

```text
HUF
USDHUF
EURHUF
EURUSD
USDJPY
```

Semantics:
- `HUF` matches events whose canonical `currency` is exactly `HUF`.
- `USDHUF` matches events whose canonical `currency` is either `USD` or `HUF`.
- A standalone currency query does not implicitly expand to a currency pair.
- Provider-wide `ALL` events are not implicitly injected into standalone currency results.

Common `/`, `-`, and `_` separators are normalized for FX pairs before validation:

```text
EUR/HUF -> EURHUF
USD-HUF -> USDHUF
USD_HUF -> USDHUF
```

Invalid or unsupported calendar symbols are rejected explicitly.

## 2.4 Evaluation

Supported evaluation tokens:

```text
current
next
```

- `current` returns events whose canonical timestamp matches the reference date/hour/minute.
- `next` returns the earliest event strictly after the reference timestamp.
- with no evaluation token, all relevant currency/pair events inside the resolved scope are returned.

## 2.5 Execution semantics

Scope-bearing query:

```text
python calendar.py today USDHUF current
```

executes:

```text
SCOPE
 -> ensure coverage
 -> use resulting calendar.json
 -> SYMBOL filter
 -> EVALUATION
```

A symbol-only query:

```text
python calendar.py USDHUF current
```

is cache-only and must never perform network acquisition.

A scope-only command:

```text
python calendar.py today
```

performs acquisition/coverage handling and does not emit a symbol result because no symbol was requested.

## 2.7 Output modes

Default query output is compact JSON containing `status`, `symbol`, and `events`.

With:

```text
python calendar.py next_week USDHUF --cleartext
```

the same query result is rendered as human-readable event blocks. Each block contains canonical UTC date/time, currency, impact, event title, actual, forecast, previous, and event ID.

`--cleartext` does not change acquisition, filtering, evaluation, or persisted data. It is rejected for delete commands and for commands without a symbol.

## 2.6 Delete

```text
python calendar.py delete
python calendar.py delete today
python calendar.py delete next_day
python calendar.py delete week
python calendar.py delete next_week
python calendar.py delete month
python calendar.py delete next_month
python calendar.py delete YYYY.MM.DD
python calendar.py delete YYYY.MM.DD@HH:MM
python calendar.py delete YYYY.MM.DD-YYYY.MM.DD
```

The bare `delete` removes the complete calendar dataset.

A date scope removes the complete UTC calendar day.

A datetime scope removes the one-minute interval beginning at the given minute.

A date range is inclusive by calendar date.

Delete never performs network acquisition and cannot be combined with a symbol or evaluation.

---

# 3. LOCAL QUERY API SEMANTICS

## 3.1 Result contract

Symbol query output is one JSON object:

```json
{
  "status": "OK",
  "symbol": "USDJPY",
  "events": []
}
```

Valid statuses:

```text
OK
NO_CALENDAR_DATA
NO_RELEVANT_EVENT
```

No-result and missing-data query states are valid query results, not data-integrity failures.

## 3.2 Reference time

- Symbol-only query: current UTC time.
- Relative scope without `@HH:MM`: current UTC time.
- `today@HH:MM`: today at the specified UTC time.
- `YYYY.MM.DD@HH:MM`: explicit UTC date/time.
- An explicit date without `@HH:MM` uses the current UTC clock time as the evaluation reference, while the event set remains restricted to that explicit date.
- An explicit date range without `@HH:MM` uses the current UTC time as the reference for `next`, while returned events remain restricted to the requested range.

## 3.3 current

Return relevant events whose canonical UTC datetime matches the reference date/hour/minute.

No nearest-event behavior is used.

## 3.4 next

Return the next relevant event strictly after the reference timestamp.

Multiple events with the same earliest timestamp are returned together.

When a scope is present, the event must also fall inside that resolved scope.

## 3.5 No evaluation

Return all relevant symbol events within the resolved scope.

For symbol-only mode, return all matching stored symbol events.

## 3.6 Deterministic ordering

Returned events are sorted by:

1. `datetime`;
2. `event_id`.

---

# 4. NORMALIZED EVENT CONTRACT

Each persisted event contains:

```json
{
  "event_id": "forexfactory:12345",
  "datetime": "2026-10-28T13:30:00Z",
  "currency": "USD",
  "impact": "HIGH",
  "event": "Example Event",
  "actual": null,
  "forecast": "150K",
  "previous": "140K",
  "source": "forexfactory"
}
```

Provider ID becomes:

```text
event_id = "forexfactory:" + provider_event_id
```

`datetime` is canonical UTC.

`currency` is one of the supported three-letter FX currencies (`USD`, `EUR`, `GBP`, `JPY`, `CHF`, `AUD`, `CAD`, `NZD`, `CNY`, `HUF`) or `ALL` for a provider-wide event that is not assigned to one currency. Provider-internal country codes such as `US`, `JN`, or `AU` are invalid canonical values.

`event` is a non-empty provider event title. Missing or empty titles are acquisition/validation errors; they are never normalized into an accepted canonical event.

Optional source values are represented as null when absent; values are never fabricated.

Impact is one of:

```text
HIGH
MEDIUM
LOW
HOLIDAY
UNKNOWN
```

---

# 5. CALENDAR.JSON CONTRACT

## 5.1 Root document

```json
{
  "schema_version": 1,
  "source": "forexfactory",
  "coverage": [],
  "events": []
}
```

Coverage intervals use:

```text
[start, end)
```

with UTC timestamps.

## 5.2 Coverage meaning

Coverage means the provider response for that interval was successfully retrieved, parsed, normalized, and validated.

A covered interval may contain zero events.

Provider events are persisted only when their canonical `datetime` falls inside the acquired coverage interval `[start, end)`. Provider records outside that interval are ignored and must never extend or implicitly create coverage.

Coverage is never inferred from event timestamps.

Coverage is maintained as a non-overlapping union.

## 5.3 Acquisition

For a requested scope, calculate the uncovered portions of its resolved interval.

Provider requests are expanded to full UTC calendar-day boundaries when required by the provider interface.

After successful acquisition:

1. normalize provider records;
2. deduplicate events by `event_id`;
3. merge coverage;
4. validate the complete document;
5. atomically replace `calendar.json`.

---

# 6. CONCURRENCY AND ATOMICITY

Use the existing single-resource lock strategy for `calendar.json`:

- Windows named mutex;
- POSIX directory-inode advisory lock.

Acquisition must re-read `calendar.json` after acquiring the lock and re-check coverage.

Never truncate the committed file before the replacement content is ready.

Use temporary write + flush/sync + atomic replace.

A provider or write failure must leave the previous committed document unchanged.

---

# 7. DELETE BEHAVIOR

Delete updates both:

- `events`;
- `coverage`.

For a full delete, both collections become empty.

For a scoped delete, event timestamps inside the deletion interval are removed and coverage intervals are clipped/split so they no longer claim deleted time as covered.

Datetime deletion uses a one-minute half-open interval.

Date-range deletion includes both endpoint dates.

---

# 8. CORE FUNCTION CONTRACT

### CLI / parsing

- `print_help` — detailed canonical CLI reference.
- `parse_calendar_request` — classify positional input into operation, scope, symbol, and evaluation.
- `parse_scope_token` — validate/decompose scope syntax.
- `is_scope` — scope classifier.
- `normalize_symbol` — normalize supported separators/case.
- `validate_symbol` — validate a six-letter supported FX pair.
- `is_symbol` — symbol classifier.
- `is_evaluation` — recognize `current` or `next`.
- `parse_date`, `parse_time`, `parse_date_range` — explicit temporal validation.

### Scope / query resolution

- `resolve_scope_interval` — calculate UTC acquisition interval.
- `resolve_scope_reference` — calculate evaluation reference timestamp.
- `filter_events_for_interval` — restrict events to a half-open interval.
- `filter_events_for_symbol` — restrict events to the two symbol currencies.
- `query_current_events` — minute-matched events.
- `query_next_events` — earliest future events.
- `query_nearest_events` — retained internal helper for nearest-reference use where required.
- `output_query_result` — emit machine-readable query output.

### Provider / normalization

- `fetch_calendar_source`
- `parse_calendar_html`
- `extract_days_payload` — extract the structured embedded `days` JSON payload used by canonical acquisition.
- `parse_calendar_days` — decode and validate the canonical structured provider days collection.
- `normalize_provider_event`
- `normalize_calendar_events`

### Persistence / integrity

- `build_empty_calendar_document`
- `validate_calendar_document`
- `load_calendar_document`
- `save_calendar_atomic`
- `acquire_calendar_lock`

### Coverage / merge

- `resolve_coverage`
- `find_uncovered_intervals`
- `merge_coverage`
- `deduplicate_calendar_events`
- `merge_calendar_events`

### Deletion / orchestration

- `resolve_delete_intervals`
- `delete_events`
- `delete_coverage`
- `run_acquisition`
- `run_query`
- `run_delete`
- `run`
- `main`

Core business functions operate on semantic values and do not depend on legacy flag-specific argument objects.

---

# 9. ERROR CONTRACT

Reject explicitly:

- no command;
- malformed scope;
- invalid date/time;
- reversed date range;
- invalid/unsupported FX symbol;
- evaluation without symbol;
- extra positional tokens;
- delete combined with symbol/evaluation;
- delete with more than one scope.

User input errors must not fall through to raw Python exceptions.

---

# 10. MONITOR BOUNDARY

The Monitor consumes normalized Calendar query results only.

The Monitor must not parse ForexFactory HTML or provider-specific payloads.

Examples:

```text
python calendar.py today USDHUF current
python calendar.py today USDHUF next
python calendar.py next_day EURUSD next
```

Calendar acquisition and query semantics remain owned by this specification. News warning policy remains owned by the Monitor specification.

---

# 11. VALIDATION CONTRACT

Live provider availability must not be required for deterministic Calendar tests.

Required validation includes:

1. detailed help output;
2. syntax/compile validation;
3. all relative scopes;
4. explicit date and datetime scopes;
5. inclusive date ranges;
6. valid and invalid symbols;
7. separator normalization;
8. cache-only symbol queries;
9. scope + symbol + evaluation pipeline;
10. scope-only acquisition path;
11. current and next evaluations;
12. delete full dataset;
13. delete scoped date/day/week/month/range/datetime selections;
14. malformed-input rejection;
15. provider payload parsing/normalization;
16. coverage union and uncovered intervals;
17. duplicate and conflict handling;
18. atomic persistence;
19. last-known-good preservation after acquisition failure.

---

# 12. DEFINITION OF DONE

Calendar V1 is complete when:

1. exactly one persistent `<DATA_ROOT>/calendar.json` exists;
2. historical and future calendar periods coexist in that document;
3. the public CLI follows the positional grammar;
4. symbol-only queries never acquire from the network;
5. scope-bearing queries acquire only missing coverage;
6. scope + symbol uses the resulting post-acquisition dataset;
7. HUF and other supported currencies are normalized and filtered correctly;
8. event identity is stable and duplicates are deterministic;
9. coverage is explicit and non-overlapping;
10. deletion updates both events and coverage;
11. acquisition failure preserves last-known-good state;
12. malformed input fails explicitly;
13. detailed help documents the complete public interface;
14. Monitor receives normalized Calendar data and not provider HTML;
15. no automatic retention exists;
16. no symbol-specific Calendar persistence is created;
17. temporary development artifacts stay under `dev_tmp/`;
19. deterministic Calendar validation passes;
20. no canonical SMC skill file is modified.
