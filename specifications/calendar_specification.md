# Calendar Module Specification

**Status:** Current implementation specification for V1 `calendar.py`.
**Scope:** External economic-calendar acquisition, ForexFactory parsing, normalized event persistence, symbol-specific news materialization, cache handling, and the process boundary consumed by `smc_monitor.py`.
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. Calendar/news context is external runtime information and must never redefine canonical SMC rules.

---

# 0. PURPOSE AND HARD BOUNDARIES

## 0.1 Finished-product role

`calendar.py` is the standalone economic-calendar data layer.

Its responsibilities are:

1. acquire economic-calendar data from the configured calendar source;
2. parse the source response into validated calendar records;
3. normalize event timestamps to canonical UTC;
4. maintain a shared calendar cache;
5. resolve symbol relevance from explicit currency/instrument metadata;
6. materialize a symbol-scoped News JSON view;
7. expose the News JSON through a file-based process boundary for `smc_monitor.py`;
8. fail closed on malformed source data and never fabricate events.

The Monitor consumes this layer as **warning context only**.

## 0.2 Explicit non-responsibilities

`calendar.py` must not:

- calculate BOS, CHoCH, IDM, Dealing Range, retracement, POI lifecycle, target, RR, or entry authorization;
- modify Market Data JSON;
- modify Structures JSON;
- place, modify, or close orders;
- infer a trade because a news event exists;
- suppress a canonical structural/target alert merely because News data is unavailable;
- own Monitor alert deduplication;
- decide whether a setup is canonically valid.

## 0.3 Runtime dependency direction

~~~text
ForexFactory
    |
    v
calendar.py
    |
    +--> <DATA_ROOT>/news_calendar.json
    |
    +--> <DATA_ROOT>/<SYMBOL>/<SYMBOL>_news.json
                                      |
                                      v
                              smc_monitor.py
~~~

`calendar.py` owns both News persistence artifacts. `smc_monitor.py` is read-only with respect to them.

A symbol directory therefore contains the three product JSON files:

~~~text
<DATA_ROOT>/<SYMBOL>/
    <SYMBOL>_marketdata.json
    <SYMBOL>_structures.json
    <SYMBOL>_news.json
~~~

The shared `news_calendar.json` remains outside symbol directories because the same calendar event can affect multiple symbols.

## 0.4 Machine-readable process boundary

The persisted JSON files are the machine-readable boundary.

stdout/stderr are diagnostics only.

The Monitor must not parse HTML, provider response text, debug output, or the Python parser's stdout as News data.

---

# 1. MODULE DESIGN

## 1.1 V1 file

V1 implementation file:

~~~text
calendar.py
~~~

Keep the implementation internally modular without introducing an unnecessary multi-module hierarchy.

Recommended source order:

~~~text
1. module docstring
2. imports
3. constants
4. domain/data models
5. CLI
6. source acquisition
7. source parsing
8. normalization/validation
9. cache loading/coverage
10. symbol relevance filtering
11. symbol-view materialization
12. atomic persistence
13. orchestration
14. main entrypoint
~~~

## 1.2 External source

V1 source:

~~~text
ForexFactory economic calendar
https://www.forexfactory.com/calendar
~~~

The supplied working parser is the starting implementation evidence.

Baseline request headers:

~~~python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}
~~~

The parser must use a bounded request timeout.

The source implementation must remain behind one acquisition boundary so a future provider can replace it without changing Monitor behavior or the persisted symbol-view contract.

---

# 2. CONSTANTS AND POLICY OWNERS

Use one owner for each implementation policy.

Required Calendar constants:

~~~text
CALENDAR_URL
REQUEST_TIMEOUT_SECONDS
CALENDAR_CACHE_PATH
SYMBOL_NEWS_FILENAME_PATTERN
CALENDAR_MAX_CACHE_AGE / refresh policy, if later approved
~~~

News warning policy is not owned by Calendar.

The Monitor owns:

~~~text
NEWS_WARNING_MIN_IMPACT
NEWS_WARNING_BEFORE_MINUTES
NEWS_WARNING_AFTER_MINUTES
~~~

Calendar persistence must retain the source impact classification such as `low`, `medium`, or `high`, but must never filter events because of warning policy.

The exact Monitor warning values are intentionally absent from this Calendar specification; they belong to the Monitor policy owner.

---

# 3. CLI CONTRACT

## 3.1 Approved CLI

Primary operation:

~~~text
python calendar.py --query SYMBOL [--starttime ISO8601] [--endtime ISO8601] [--debug]
~~~

Required:

~~~text
--query SYMBOL
~~~

Optional:

~~~text
--starttime ISO8601
--endtime ISO8601
--debug
--help
~~~

No provider-specific API key option is exposed for V1.

No SMC/Mapper/Market Data option is allowed.

## 3.2 Query semantics

### No time boundaries

~~~text
--query SYMBOL
~~~

Behavior:

1. load the existing shared `news_calendar.json`;
2. do not request the provider solely because the query has no time boundary;
3. use the complete currently retained cache;
4. filter events relevant to the requested symbol;
5. atomically materialize `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_news.json`;
6. exit success when the cache is valid, even if the symbol has zero relevant events.

This is intentionally cache-only.

### Time-bounded query

~~~text
--query SYMBOL --starttime START --endtime END
~~~

Behavior:

1. validate `START <= END`;
2. determine which requested interval is already covered by the shared cache;
3. acquire only the missing interval(s) when coverage is incomplete;
4. parse and normalize the newly acquired records;
5. merge them into the shared cache;
6. filter the resulting cache to the requested symbol and time interval;
7. atomically materialize `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_news.json`;
8. exit success only after the requested interval is either covered by validated cache data or the provider explicitly returned a valid empty result for that interval.

A cache hit must not be required to trigger a provider request.

The query must never silently return an incomplete historical interval.

### Partial time boundaries

V1 treats time-bounded querying as an explicit interval operation.

Use both `--starttime` and `--endtime` together.

Supplying only one boundary fails explicitly rather than inventing the missing boundary.

---

# 4. DATA MODELS

## 4.1 Provider source event

Use a provider-local record containing the fields required to parse the supplied ForexFactory response.

Conceptual fields:

~~~text
id
ebaseId
name
prefixedName
trimmedPrefixedName
soloTitle
soloTitleFull
soloTitleShort
notice
dateline
country
currency
hasLinkedThreads
hasNotice
hasDataValues
hasGraph
checkedIn
isMasterList
firstInDay
showGridLine
greyed
upNext
releaser
checker
impactName
impactClass
impactTitle
timeLabel
timeMasked
hideHistory
hideSoloPage
actual
previous
revision
forecast
leaked
actualBetterWorse
revisionBetterWorse
isSubscribable
isSubscribed
showDetails
showGraph
enableDetailComponent
enableActualComponent
showExpanded
siteId
editUrl
date
url
soloUrl
~~~

The provider-local model may contain additional source fields when needed to preserve parsing compatibility.

Provider-specific fields must not leak into the Monitor contract.

## 4.2 Normalized CalendarEvent

The normalized event is the stable cross-module representation.

Required fields:

~~~python
@dataclass(frozen=True)
class CalendarEvent:
    event_id: str
    source_ebase_id: str | None
    name: str
    prefixed_name: str | None
    country: str | None
    currency: str | None
    event_time: datetime
    impact: str | None
    impact_title: str | None
    actual: str | None
    previous: str | None
    revision: str | None
    forecast: str | None
    url: str | None
    solo_url: str | None
~~~

Rules:

- `event_id` is the stable provider event ID from `id`;
- `source_ebase_id` preserves `ebaseId` when present;
- `event_time` is canonical UTC;
- `impact` uses the normalized lowercase source class such as `low`, `medium`, `high`;
- empty source strings normalize to null;
- display-only date/time labels are not canonical time fields;
- mutable values such as actual/forecast do not change `event_id`.

## 4.3 Cache document

The shared cache is:

~~~text
<DATA_ROOT>/news_calendar.json
~~~

Logical shape:

~~~json
{
  "schema_version": 1,
  "source": "forexfactory",
  "retrieved_at": "2026-10-03T10:00:00Z",
  "coverage": {
    "start": "2026-09-27T00:00:00Z",
    "end": "2026-10-10T23:59:59Z"
  },
  "events": []
}
~~~

Rules:

- `retrieved_at` is metadata, not an event time;
- `coverage` describes validated acquisition coverage;
- an empty `events` array is valid when the provider returns a valid empty interval;
- cache coverage must not be inferred merely from the first/last event timestamps;
- a covered interval may contain zero events;
- unrelated events remain in the shared cache because the cache is cross-symbol.

## 4.4 Symbol News document

The symbol materialized view is:

~~~text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_news.json
~~~

Logical shape:

~~~json
{
  "schema_version": 1,
  "symbol": "USDJPY",
  "generated_at": "2026-10-03T10:00:00Z",
  "source": "forexfactory",
  "coverage": {
    "start": "2026-09-27T00:00:00Z",
    "end": "2026-10-10T23:59:59Z"
  },
  "events": []
}
~~~

The `events` array contains only events relevant to the symbol.

The file is a materialized view, not a second source of acquisition truth.

---

# 5. FOREXFACTORY PARSER CONTRACT

## 5.1 Request

The starting parser performs:

~~~python
response = requests.get(
    CALENDAR_URL,
    headers=headers,
    timeout=REQUEST_TIMEOUT_SECONDS,
)
~~~

Failure handling:

- HTTP 200: parse;
- HTTP 403: provider-access failure;
- other non-2xx: provider-access failure;
- request exception/timeout: provider-access failure.

No failure may be converted into an empty event set.

## 5.2 Calendar payload extraction

The supplied working parser extracts the JavaScript `days` array using:

~~~python
pattern = re.compile(
    r'days:\s*(\[.*?\]),\s*time:\s*[\'"]',
    re.DOTALL,
)
~~~

This exact extraction approach is the current V1 parsing baseline.

Rules:

1. locate the `days` array;
2. extract only the array payload;
3. parse it with `json.loads()`;
4. require a valid JSON array;
5. reject the source if the marker is not found;
6. reject the source if the extracted JSON is malformed;
7. do not salvage a partial array;
8. do not treat parser failure as a successful no-events response.

The implementation may later replace the extraction mechanism if the source markup changes, but the normalized `CalendarEvent` contract must remain stable.

## 5.3 Day records

Each extracted day record has conceptually:

~~~text
date
dateline
add
events[]
~~~

`events[]` may be empty.

An empty day is valid provider data and must not be treated as an error.

## 5.4 Event normalization

For each provider event:

- require a stable `id` or fail the event normalization;
- require a valid `dateline` or fail the event normalization;
- convert `dateline` from Unix epoch seconds to an aware UTC `datetime`;
- normalize `impactName`;
- normalize empty strings;
- preserve actual/previous/revision/forecast text exactly as source values after empty-string normalization;
- preserve provider URLs as source metadata;
- do not invent missing forecasts, actuals, or revisions.

An event with malformed identity/time must fail the acquisition transaction rather than silently disappear.

## 5.5 Source event ordering

Before persistence:

1. normalize every event;
2. deduplicate by `event_id`;
3. detect conflicting same-ID records;
4. sort deterministically by:
   1. `event_time`
   2. `event_id`

Equivalent duplicate records are merged/ignored.

Same `event_id` with conflicting canonical identity/time is a data-integrity failure.

Mutable event fields may change on later refreshes without changing event identity.

---

# 6. TIME CONTRACT

## 6.1 Canonical time

All normalized event times are UTC.

No host-local timezone assumption is permitted.

`dateline` is interpreted as a Unix epoch instant.

## 6.2 Display fields

The source fields:

~~~text
date
timeLabel
~~~

are informational display values only.

They must never be used as the canonical event time when `dateline` is available.

## 6.3 Query boundaries

`--starttime` and `--endtime` are parsed as timezone-aware datetimes and normalized to UTC.

A query fails explicitly if:

~~~text
start > end
~~~

No naive timestamp may enter the normalized domain.

## 6.4 Warning evaluation time

The Monitor evaluates News warnings against canonical UTC `event_time` and canonical UTC current time.

Local timezone conversion is presentation-only.

---

# 7. CACHE OWNERSHIP AND COVERAGE

## 7.1 Shared cache ownership

Only `calendar.py` writes:

~~~text
<DATA_ROOT>/news_calendar.json
~~~

Monitor is read-only.

## 7.2 Coverage semantics

Coverage is an acquisition statement, not proof that every instant contains an event.

A covered interval may contain no events.

Coverage must never be synthesized from:

- first event timestamp;
- last event timestamp;
- symbol Market Data availability;
- Monitor wall-clock observations.

## 7.3 Cache query without time

For:

~~~text
--query SYMBOL
~~~

the complete currently retained cache is the input.

No provider request is made.

## 7.4 Time-bounded coverage

For:

~~~text
--query SYMBOL --starttime START --endtime END
~~~

the query must establish validated coverage for the full interval.

If the cache contains multiple disjoint coverage intervals, missing portions must be acquired explicitly.

Do not falsely mark the union as continuous coverage.

## 7.5 Empty provider result vs provider failure

These are distinct:

~~~text
valid provider response + zero events
    -> successful empty coverage

HTTP/API/parser/network failure
    -> acquisition failure
~~~

A successful empty interval may produce an empty symbol News view.

---

# 8. SYMBOL RELEVANCE

## 8.1 Forex symbol currency extraction

For a standard six-letter FX symbol:

~~~text
USDJPY -> USD + JPY
EURUSD -> EUR + USD
GBPCHF -> GBP + CHF
~~~

The implementation should also normalize conventional separators where unambiguous.

The extraction function must be deterministic:

~~~python
def extract_symbol_currencies(symbol: str) -> list[str]:
    ...
~~~

If the symbol does not expose exactly two recognizable currency codes, the function returns an empty relevance set rather than guessing.

## 8.2 Event relevance

An event is relevant to an FX symbol when:

~~~text
event.currency in symbol currencies
~~~

No relevance may be inferred from:

- event name text;
- country-name text;
- free-form description text;
- impact class;
- historical price behavior.

## 8.3 Non-FX symbols

V1 does not guess currency relevance for arbitrary non-FX symbols.

The symbol News view may therefore be valid and empty for a non-FX symbol.

The relevance function is an extension point for future explicit instrument mappings.

---

# 9. SYMBOL VIEW MATERIALIZATION

## 9.1 Materialization function

Required boundary:

~~~python
def materialize_symbol_news(
    symbol: str,
    events: list[CalendarEvent],
    coverage_start: datetime,
    coverage_end: datetime,
) -> bool:
    ...
~~~

Responsibilities:

- normalize and validate symbol;
- select relevant events;
- create the symbol News document;
- persist it atomically;
- never modify Market Data or Structures JSON.

## 9.2 Event filtering order

Use this deterministic sequence:

~~~text
load valid shared cache
        ↓
resolve symbol currencies
        ↓
filter by currency
        ↓
filter by requested time interval, if any
        ↓
sort by event_time + event_id
        ↓
serialize
        ↓
atomic write
~~~

Impact filtering does **not** happen in Calendar materialization. All relevant impact levels remain available to Monitor warning policy.

This prevents the Calendar layer from hiding a lower-impact event that a future Monitor policy may need.

## 9.3 Empty symbol result

A valid symbol query with no relevant events writes:

~~~json
"events": []
~~~

This is success, not failure.

---

# 10. ATOMIC PERSISTENCE

## 10.1 Shared cache

The shared cache must be written atomically.

Do not truncate the existing cache and then write the new document.

On write failure, the previous valid cache remains intact.

## 10.2 Symbol News JSON

The symbol-specific file must also be written atomically.

A failed symbol-view write must not partially overwrite the previous valid symbol News view.

## 10.3 Cross-file transaction boundary

The shared cache and symbol News view do not require a single cross-file transaction.

Required order:

~~~text
validate/acquire
    ↓
atomically persist shared cache
    ↓
build symbol view from persisted/validated state
    ↓
atomically persist symbol News JSON
~~~

If symbol materialization fails after successful cache persistence, the cache remains valid and the command fails explicitly.

---

# 11. ERROR CONTRACT

Use explicit failure categories:

1. CLI/input validation;
2. symbol validation;
3. provider transport;
4. provider HTTP/status;
5. parser extraction;
6. malformed source JSON;
7. event identity/time normalization;
8. conflicting duplicate event;
9. cache load/schema;
10. coverage resolution;
11. symbol materialization;
12. atomic-write failure.

Rules:

- no provider failure becomes empty success;
- no malformed source event is silently dropped;
- no invalid persisted cache is silently replaced with an empty cache;
- diagnostics are non-machine data;
- finite provider retry policy may be used, but retries must be bounded and deterministic.

---

# 12. MONITOR WARNING CONSUMPTION CONTRACT

The Calendar layer provides data. The Monitor owns warning evaluation.

## 12.1 Monitor input

Monitor reads:

~~~text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_news.json
~~~

It validates at least:

- symbol identity;
- schema version;
- UTC event_time values;
- event identity uniqueness;
- event currency;
- event impact;
- event ordering;
- coverage metadata.

## 12.2 Dynamic warning concept

The warning is time-relative to each event.

For an eligible event:

~~~text
event_time - now
~~~

determines the warning phase.

The logical phases are:

~~~text
NO_WARNING
PRE_EVENT
EVENT_ACTIVE
POST_EVENT
~~~

A warning is emitted only when the current UTC time lies inside the configured pre/post windows.

The exact window values are single-owner policy constants:

~~~text
NEWS_WARNING_BEFORE_MINUTES
NEWS_WARNING_AFTER_MINUTES
~~~

The Monitor must not embed duplicate window values in multiple functions.

## 12.3 Impact policy

Monitor warning eligibility is policy-driven.

At minimum, the event impact is compared against:

~~~text
NEWS_WARNING_MIN_IMPACT
~~~

The source impact is retained exactly enough for deterministic normalization, while the Monitor decides whether low/medium/high events are warning eligible.

The Calendar layer does not remove events based on impact.

## 12.4 Warning event identity

Use a deterministic transient identity containing:

~~~text
NEWS_WARNING
+ symbol
+ event_id
+ warning_phase
~~~

The Monitor records an emitted warning only after successful notification.

A failed notification remains retryable.

A later phase may produce a distinct warning for the same economic event.

## 12.5 Warning payload

At minimum:

~~~text
alert_type = NEWS_WARNING
symbol
event_id
event_time
event_name
currency
impact
warning_phase
minutes_to_event / minutes_since_event
forecast
previous
actual
evaluation_time
~~~

Local display time may be included as presentation metadata but never replaces UTC event/evaluation timestamps.

## 12.6 News is informational only

News warning must never:

- mutate Structures JSON;
- mutate Market Data JSON;
- advance or reset Mapper checkpoints;
- change canonical POI lifecycle;
- change target coordinates;
- alter projected RR calculation;
- invalidate a structural setup;
- submit/cancel/modify orders;
- close/open positions;
- suppress a canonical setup alert merely because News data is missing.

When News JSON is unavailable or invalid, the Monitor reports the News warning path as unavailable and continues the canonical/target evaluation path independently.

---

# 13. MONITOR PROCESS ORCHESTRATION

The normal Monitor cycle becomes:

~~~text
discover/load analyses
        ↓
plan Market Data updates
        ↓
invoke market_data.py
        ↓
reload Market Data
        ↓
invoke smc_mapper.py as required
        ↓
reload Structures
        ↓
refresh current market reference
        ↓
update session context
        ↓
invoke calendar.py --query SYMBOL
        ↓
reload SYMBOL News JSON
        ↓
evaluate News warning
        ↓
evaluate target / RR / canonical alerts
        ↓
schedule next cycle
~~~

Calendar refresh/reload occurs before News warning evaluation.

News processing does not become a mapper prerequisite.

A calendar acquisition failure must not block Market Data or Mapper processing already due for the cycle.

## 13.1 invoke_calendar

Monitor-side function:

~~~python
def invoke_calendar(
    symbol: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    debug: bool = False,
) -> ProcessResult:
    ...
~~~

Launch:

~~~text
python calendar.py --query SYMBOL [--starttime ... --endtime ...] [--debug]
~~~

The Monitor does not call ForexFactory directly.

The Monitor does not parse calendar HTML or stdout.

## 13.2 Query time used by Monitor

The Monitor should request the minimum useful operational interval required for warning evaluation rather than an arbitrarily large historical interval.

The exact warning-horizon calculation is Monitor-owned and must cover:

~~~text
now - NEWS_WARNING_AFTER_MINUTES
through
now + NEWS_WARNING_BEFORE_MINUTES
~~~

when those values are configured.

If the Monitor only needs currently relevant warnings, it should not repeatedly request the full historical cache.

## 13.3 Missing News path

If:

- Calendar process fails;
- symbol News JSON is unavailable;
- News JSON is malformed;

then:

~~~text
news_warning_state = UNAVAILABLE
~~~

and canonical/target evaluation continues.

A valid empty symbol News JSON means:

~~~text
news_warning_state = NO_RELEVANT_EVENT
~~~

These states are not interchangeable.

---

# 14. TEST CONTRACT

Tests must not depend on a live ForexFactory request.

Provide deterministic fixtures for:

1. supplied `days: [...] ` payload extraction;
2. valid empty day;
3. valid event normalization;
4. malformed `days` payload;
5. missing `days` marker;
6. malformed event JSON;
7. missing event ID;
8. invalid Unix event time;
9. duplicate equivalent event;
10. conflicting same-ID event;
11. UTC normalization;
12. symbol currency filtering;
13. USDJPY receiving USD and JPY events;
14. unrelated currency exclusion;
15. no-time query using cache only;
16. time-bounded query acquiring missing coverage;
17. valid empty provider interval;
18. provider failure distinct from empty;
19. shared-cache atomic persistence;
20. symbol-News atomic persistence;
21. malformed cache rejection;
22. PRE_EVENT warning;
23. EVENT_ACTIVE warning boundary;
24. POST_EVENT warning;
25. warning outside configured window;
26. impact-policy filtering;
27. repeated warning deduplication;
28. failed notification remains retryable;
29. News unavailable does not block canonical alert evaluation;
30. malformed/non-FX symbol yields valid empty relevance without guessing.

Provider parsing tests may use the exact supplied ForexFactory sample structure.

---

# 15. IMPLEMENTATION FUNCTION CONTRACT

Required function names:

~~~text
build_argument_parser
parse_calendar_request
normalize_symbol
parse_iso8601
fetch_calendar_source
extract_days_payload
parse_calendar_days
normalize_provider_event
normalize_calendar_events
deduplicate_calendar_events
validate_calendar_cache
load_calendar_cache
save_calendar_cache_atomic
resolve_calendar_coverage
extract_symbol_currencies
filter_events_for_symbol
materialize_symbol_news
save_symbol_news_atomic
run_query
run
main
~~~

Avoid vague names such as:

~~~text
process_data
handle_news
run_news
helper
util
~~~

Every function has one ownership responsibility.

---

# 16. DEFINITION OF DONE

Calendar V1 is complete only when:

1. `calendar.py --query SYMBOL` works from an existing valid cache without network access;
2. time-bounded queries establish validated requested coverage;
3. the supplied ForexFactory `days` parser is implemented behind the source boundary;
4. canonical event times are UTC;
5. source event identity is stable and deterministic;
6. shared cache and symbol News JSON are atomic;
7. symbol relevance is deterministic;
8. every symbol directory contains Market Data, Structures and News JSON without cross-symbol leakage;
9. Monitor consumes only the symbol News JSON boundary;
10. News warning is transient/informational and cannot alter canonical SMC state;
11. missing News never suppresses canonical setup/target evaluation;
12. all deterministic Calendar and Monitor warning tests pass;
13. no `.agents/skills/smc/` file is modified;
14. provider details remain isolated from the Monitor.

