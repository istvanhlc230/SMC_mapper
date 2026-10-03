# Calendar Module Specification

**Status:** Current V1 implementation specification for \`calendar.py\`.
**Scope:** ForexFactory economic-calendar acquisition, parsing, normalized event persistence, local time-based query API, explicit deletion, coverage tracking, locking, atomic persistence, and the machine-readable contract consumed by \`smc_monitor.py\`.
**Canonical authority:** \`.agents/skills/smc/\` remains the sole authority for canonical SMC semantics. Calendar/news data is external runtime context and must never redefine canonical SMC rules.

---

# 0. PURPOSE AND HARD BOUNDARIES

## 0.1 Finished-product role

\`calendar.py\` is the standalone economic-calendar data layer.

Responsibilities:

1. acquire economic-calendar data from ForexFactory;
2. parse and normalize provider records;
3. normalize event times to canonical UTC;
4. maintain one global \`calendar.json\`;
5. track validated acquisition coverage;
6. provide a local time-based query API;
7. provide explicit deterministic deletion;
8. preserve last-known-good data on acquisition failure;
9. expose machine-readable query results for Monitor and other consumers.

## 0.2 Explicit non-responsibilities

\`calendar.py\` must not:

- calculate BOS, CHoCH, IDM, Dealing Range, retracement, POI lifecycle, target, RR, or entry authorization;
- modify Market Data or Structures JSON;
- create symbol-specific News JSON files;
- place, modify, or close orders;
- decide whether a news event makes a setup valid;
- own Monitor alert deduplication;
- decide whether an event is "active" for trading purposes;
- define SMC execution policy.

The Monitor decides what queried News information means for runtime warning behavior.

## 0.3 Single persistence artifact

V1 has exactly one persistent calendar data file:

\`\`\`text
<DATA_ROOT>/calendar.json
\`\`\`

No symbol-specific News JSON, separate cache JSON, or persistent history JSON may be created.

Temporary files used internally for atomic replacement are transient implementation artifacts and are not additional persisted data stores.

## 0.4 Missing calendar data

\`calendar.json\` is optional.

When it does not exist:

- query operations return a valid empty result;
- this is not an error condition;
- no automatic download occurs merely because the file is missing;
- the Monitor may continue normal canonical processing and record/report \`No calendar data\`;
- a successful acquisition creates the file.

A malformed existing \`calendar.json\` is a data-integrity error, not the same state as a missing file.

---

# 1. SOURCE AND PROVIDER BOUNDARY

## 1.1 V1 provider

V1 uses:

\`\`\`text
ForexFactory economic calendar
https://www.forexfactory.com/calendar
\`\`\`

The supplied working parser is the initial provider implementation baseline.

The provider layer is isolated behind acquisition/parsing functions so a future provider can replace ForexFactory without changing the normalized event or query contract.

## 1.2 Supported ForexFactory request forms

CLI period selectors map to these provider requests:

\`\`\`text
--day today
    -> ?day=today

--day tomorrow
    -> ?day=tomorrow

--day YYYY.MM.DD
    -> ?day=mmmD.YYYY

--week this
    -> ?week=this

--week next
    -> ?week=next

--week YYYY.MM.DD
    -> ?week=mmmD.YYYY

--month this
    -> ?month=this

--month next
    -> ?month=next

--range YYYY.MM.DD-YYYY.MM.DD
    -> ?range=mmmD.YYYY-mmmD.YYYY
\`\`\`

The CLI uses \`YYYY.MM.DD\`. ForexFactory-specific date spelling is an internal provider concern.

For \`--week YYYY.MM.DD\`, the supplied date is forwarded as the requested week date. It is not silently normalized to a week-start/Sunday date.

## 1.3 Request policy

Use a bounded request timeout and the approved baseline browser headers.

A provider transport/status/parsing failure must never be converted into successful empty data.

HTTP success alone is not acquisition success; the response must parse and normalize successfully.

---

# 2. CLI CONTRACT

## 2.1 Operation families

The CLI has three mutually exclusive operation families.

### Acquisition

\`\`\`text
python calendar.py --query SYMBOL
python calendar.py --query SYMBOL --day VALUE
python calendar.py --query SYMBOL --week VALUE
python calendar.py --query SYMBOL --month VALUE
python calendar.py --query SYMBOL --range VALUE
\`\`\`

Optional:

\`\`\`text
--debug
\`\`\`

Exactly one of \`--day\`, \`--week\`, \`--month\`, or \`--range\` may be supplied.

If \`--query SYMBOL\` is supplied without a period selector:

- use the existing full \`calendar.json\`;
- do not perform an HTTP request;
- return the currently stored relevant events for that symbol through the machine-readable query result;
- existing data is used as-is.

The symbol argument does not create a symbol-specific data store. Persisted acquisition data remains global so one provider download can serve multiple symbols.

### Local query API

\`\`\`text
python calendar.py --symbol SYMBOL
python calendar.py --symbol SYMBOL --current
python calendar.py --symbol SYMBOL --next
python calendar.py --symbol SYMBOL --date YYYY.MM.DD
python calendar.py --symbol SYMBOL --time HH:MM
python calendar.py --symbol SYMBOL --date YYYY.MM.DD --time HH:MM
\`\`\`

Optional:

\`\`\`text
--debug
\`\`\`

The local query API never performs network access and never changes \`calendar.json\`.

### Delete

\`\`\`text
python calendar.py --delete --before YYYY.MM.DD
python calendar.py --delete --after YYYY.MM.DD
python calendar.py --delete --before YYYY.MM.DD --after YYYY.MM.DD
python calendar.py --delete --range YYYY.MM.DD-YYYY.MM.DD
python calendar.py --delete --date YYYY.MM.DD
python calendar.py --delete --date YYYY.MM.DD --time HH:MM
python calendar.py --delete --range YYYY.MM.DD-YYYY.MM.DD --time HH:MM-HH:MM
\`\`\`

Optional:

\`\`\`text
--dry-run
--debug
\`\`\`

Delete never performs network access.

## 2.2 CLI mutual exclusion

A command must use exactly one operation family:

- acquisition/query API;
- local query API;
- delete.

Mixing \`--query\` with \`--symbol\` or \`--delete\` is invalid.

Mixing period selectors is invalid.

Delete allows one primary selector, except \`--before + --after\` may be combined to define a bounded interval.

\`--range\` must not be combined with \`--before\`, \`--after\`, or \`--date\`.

\`--date\` may be combined only with \`--time\`.

\`--time\` without \`--date\` is valid only for the local query API and current-day query semantics; for delete it is invalid unless paired with \`--date\` or \`--range\`.

Invalid or contradictory combinations fail explicitly without modifying the data file.

## 2.3 Input formats

\`\`\`text
DATE  = YYYY.MM.DD
TIME  = HH:MM
TIME_RANGE = HH:MM-HH:MM
RANGE = YYYY.MM.DD-YYYY.MM.DD
\`\`\`

All command-line query/delete boundaries are interpreted in canonical UTC.

---

# 3. LOCAL QUERY API SEMANTICS

## 3.1 Common query result contract

All local query modes return one machine-readable JSON object to stdout:

\`\`\`json
{
  "status": "OK",
  "symbol": "USDJPY",
  "events": []
}
\`\`\`

Valid statuses:

\`\`\`text
OK
NO_CALENDAR_DATA
NO_RELEVANT_EVENT
\`\`\`

No-result and missing-calendar states are successful query results, not CLI errors.

Operational diagnostics belong on stderr.

## 3.2 \`--symbol SYMBOL\`

Reference time is the current canonical UTC time.

If one or more relevant events are scheduled at the current minute, return those events.

Otherwise return the next relevant event(s) strictly after the current time.

If none exists, return:

\`\`\`json
{"status":"NO_RELEVANT_EVENT","symbol":"USDJPY","events":[]}
\`\`\`

## 3.3 \`--current\`

Return relevant event(s) whose canonical \`datetime\` falls in the current UTC minute.

No nearest-event behavior is used.

If none exists, return \`NO_RELEVANT_EVENT\`.

The Calendar layer does not assign a semantic duration to "active".

## 3.4 \`--next\`

Return the next relevant event(s) strictly after current canonical UTC time.

Multiple events with the same earliest event time are returned together.

## 3.5 \`--date\`

Reference time is the supplied UTC calendar date combined with the current UTC time.

Return the nearest relevant event(s) to that reference timestamp using absolute time distance.

## 3.6 \`--time\`

Reference time is the supplied UTC time on the current UTC date.

Return the nearest relevant event(s).

## 3.7 \`--date + --time\`

Reference timestamp is the supplied UTC date and time.

Return the nearest relevant event(s).

If multiple events are equally near, return all equally near events.

No maximum search distance is imposed by V1.

## 3.8 Query ordering

Returned events are deterministically sorted by:

1. \`datetime\`;
2. \`event_id\`.

---

# 4. NORMALIZED EVENT CONTRACT

## 4.1 Persisted event schema

Each event contains at minimum:

\`\`\`json
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
\`\`\`

Fields:

- \`event_id\`: stable provider-derived identity;
- \`datetime\`: canonical UTC event timestamp;
- \`currency\`: normalized uppercase currency code when available;
- \`impact\`: one of \`HIGH\`, \`MEDIUM\`, \`LOW\`, \`HOLIDAY\`, \`UNKNOWN\`;
- \`event\`: normalized event name;
- \`actual\`, \`forecast\`, \`previous\`: source values or null;
- \`source\`: \`forexfactory\` for V1.

Provider-specific fields do not enter this persisted cross-module contract.

## 4.2 Stable identity

For ForexFactory V1:

\`\`\`text
event_id = "forexfactory:" + provider_event_id
\`\`\`

The provider event ID must be stable across repeated downloads.

Mutable values such as actual, forecast, and previous may change without changing \`event_id\`.

A same-ID record with conflicting canonical \`datetime\` or provider identity is an acquisition data-integrity failure.

## 4.3 Normalization

Rules:

- \`dateline\` is interpreted as Unix epoch seconds;
- normalized \`datetime\` is an aware UTC timestamp;
- empty source strings become null;
- impact is mapped to the uppercase enum;
- missing optional values are not fabricated;
- malformed identity or time fails the acquisition transaction.

---

# 5. CALENDAR.JSON CONTRACT

## 5.1 Single global document

\`\`\`text
<DATA_ROOT>/calendar.json
\`\`\`

Logical shape:

\`\`\`json
{
  "schema_version": 1,
  "source": "forexfactory",
  "coverage": [
    {
      "start": "2026-10-26T00:00:00Z",
      "end": "2026-11-02T00:00:00Z",
      "requested": {
        "type": "week",
        "value": "2026.10.28"
      },
      "fetched_at": "2026-10-03T11:00:00Z"
    }
  ],
  "events": []
}
\`\`\`

Coverage intervals use a half-open UTC convention:

\`\`\`text
[start, end)
\`\`\`

This avoids end-of-day precision ambiguity.

## 5.2 Multiple periods

The same \`calendar.json\` may contain events from arbitrarily many dates and acquisition requests.

New acquisitions merge into the existing event set.

They never overwrite unrelated historical or future events.

## 5.3 Coverage

Coverage records describe successfully validated provider acquisition.

A covered interval may legitimately contain zero events.

Coverage is never inferred from first/last event timestamps.

Coverage is represented as the minimal non-overlapping union of validated covered intervals.

When overlapping/adjacent intervals are merged, the merged interval keeps the latest \`fetched_at\` and the retained request metadata needed for provenance.

A requested interval is covered only when the union of stored coverage intervals completely spans it.

If coverage is incomplete, \`calendar.py\` computes the uncovered subintervals and acquires only the missing portions where the provider interface permits.

## 5.4 No retention policy

V1 has no automatic retention and no automatic history deletion.

Old data remains indefinitely until the user explicitly invokes \`--delete\`.

Coverage is never removed merely because it is old.

---

# 6. ACQUISITION AND MERGE

## 6.1 Acquisition flow

\`\`\`text
parse CLI
  ↓
resolve requested provider period
  ↓
acquire lock
  ↓
re-read calendar.json
  ↓
re-check coverage
  ↓
if fully covered: no provider request
  ↓
otherwise fetch uncovered period(s)
  ↓
parse
  ↓
normalize
  ↓
validate complete acquired set
  ↓
merge events + coverage
  ↓
validate complete document
  ↓
atomic commit
  ↓
release lock
\`\`\`

The second coverage check after lock acquisition is mandatory to prevent duplicate parallel downloads.

## 6.2 Event merge

Merge key is \`event_id\`.

For equivalent duplicates, retain one logical event.

For an existing event whose mutable source values changed, update those mutable values from the newest successfully acquired source record.

Canonical identity/time conflicts fail the transaction.

After merge:

1. deduplicate by \`event_id\`;
2. sort events by \`datetime\`, then \`event_id\`;
3. update coverage;
4. commit atomically.

## 6.3 Explicit history acquisition

Historical requests use the same global event store.

The acquisition time is metadata only.

Historical events do not gain a special automatic retention period.

They remain until explicitly deleted.

---

# 7. CONCURRENCY, LOCKING, AND ATOMICITY

## 7.1 Lock scope

There is one shared resource:

\`\`\`text
<DATA_ROOT>/calendar.json
\`\`\`

Use an OS-level exclusive/advisory lock associated with \`calendar.json\`.

Do not create a persistent \`.lock\` data file.

## 7.2 Parallel execution

If another process owns the calendar lock:

- wait until it releases the lock;
- do not retry with a retry limit;
- do not use exponential backoff;
- do not abort because of lock age;
- after acquiring the lock, re-read the current \`calendar.json\` and re-check coverage.

This guarantees that the second process does not redundantly fetch a period already acquired by the first process.

## 7.3 Missing-file race

When \`calendar.json\` does not exist, the implementation may establish the single file with an exclusive-create/open operation, initialize the valid empty document, and then apply the same lock protocol.

No second persistent lock file is introduced.

## 7.4 Atomic write

Never truncate the existing \`calendar.json\` before the replacement document is fully serialized.

Use:

\`\`\`text
write temporary file
  ↓
flush/sync as appropriate
  ↓
atomic replace calendar.json
\`\`\`

The temporary file is removed after successful replacement.

A failed write leaves the previously committed \`calendar.json\` unchanged.

---

# 8. FAILURE AND LAST-KNOWN-GOOD CONTRACT

## 8.1 Acquisition failure

The following are failures:

- network exception;
- timeout;
- non-success HTTP status;
- missing/malformed \`days\` payload;
- malformed provider JSON;
- invalid event identity/time;
- conflicting canonical duplicate;
- incomplete validation;
- atomic-write failure.

On any acquisition failure:

\`\`\`text
previous calendar.json -> unchanged
coverage -> unchanged
events -> unchanged
\`\`\`

A provider failure must never be represented as successful empty coverage.

## 8.2 Missing calendar.json

Missing file is not an error.

Query returns \`NO_CALENDAR_DATA\`.

Monitor may continue all canonical processing.

## 8.3 Corrupt calendar.json

If an existing file is malformed or violates the schema:

- report a calendar data-integrity error;
- do not silently replace it with an empty document;
- do not silently discard existing information;
- Monitor treats the News path as unavailable for that cycle but continues canonical processing.

---

# 9. SYMBOL RELEVANCE

## 9.1 Standard FX symbols

For standard FX symbols:

\`\`\`text
USDJPY -> USD + JPY
EURUSD -> EUR + USD
GBPCHF -> GBP + CHF
\`\`\`

Normalize conventional separators when unambiguous.

If exactly two recognizable currency codes cannot be determined, return an empty relevance set rather than guessing.

## 9.2 Event relevance

An event is relevant when:

\`\`\`text
event.currency in symbol currencies
\`\`\`

Do not infer relevance from event title, country text, impact, or price behavior.

## 9.3 Non-FX symbols

V1 does not guess currency relevance for arbitrary non-FX symbols.

A valid query may therefore return no relevant events.

---

# 10. DELETE CONTRACT

## 10.1 General rule

Delete is explicit and user initiated.

No automatic cleanup exists.

Deletes are applied to both:

- \`events\`;
- coverage intervals.

Coverage must be recalculated after event/coverage deletion so metadata remains consistent with stored data.

## 10.2 \`--before DATE\`

Delete events with:

\`\`\`text
event.datetime < DATE 00:00:00Z
\`\`\`

Coverage is clipped or removed accordingly.

## 10.3 \`--after DATE\`

Delete events with:

\`\`\`text
event.datetime >= (DATE + 1 day) 00:00:00Z
\`\`\`

Coverage is clipped or removed accordingly.

This makes "after DATE" mean strictly after the complete UTC calendar day.

## 10.4 \`--before + --after\`

When both are supplied, \`after\` must define the lower boundary and \`before\` the upper boundary.

The command deletes:

\`\`\`text
(after boundary, before boundary)
\`\`\`

Only a non-empty, non-contradictory interval is accepted.

## 10.5 \`--range DATE-DATE\`

Inclusive date range:

\`\`\`text
[START_DATE 00:00Z, END_DATE + 1 day 00:00Z)
\`\`\`

Both calendar dates are included.

## 10.6 \`--date DATE\`

Deletes all events on that UTC calendar date.

## 10.7 \`--date DATE --time HH:MM\`

Deletes all events whose UTC hour and minute equal the requested \`HH:MM\`.

Delete never uses nearest-event semantics.

## 10.8 \`--range ... --time HH:MM-HH:MM\`

Deletes events whose UTC date is inside the date range and whose UTC time-of-day falls inside the inclusive requested time range.

## 10.9 Dry-run

\`\`\`text
--dry-run
\`\`\`

performs all selector validation and selection logic but does not modify \`calendar.json\`.

The result reports the matching event count and selected interval metadata.

---

# 11. MONITOR PROCESS BOUNDARY

The Monitor consumes Calendar only as external News context.

It must not parse ForexFactory HTML or provider response data.

The preferred machine-readable boundary is the local query API:

\`\`\`text
calendar.py --symbol SYMBOL --current
calendar.py --symbol SYMBOL --next
\`\`\`

The Monitor may also invoke the acquisition form when it must ensure future warning coverage.

The Monitor never writes \`calendar.json\`.

Calendar warning policy does not belong in this module.

---

# 12. TEST CONTRACT

The global developer-agent naming, portability, prompt-efficiency, and validation rules in `AGENTS.md` apply to Calendar. The Calendar validation contract is defined here; no dedicated repository test directory is prescribed.

Tests must not require a live ForexFactory request.

Required coverage:

1. CLI period validation;
2. ForexFactory date conversion;
3. supplied \`days: [...]\` extraction;
4. valid empty provider period;
5. malformed provider payload;
6. missing \`days\` marker;
7. missing event ID;
8. invalid event dateline;
9. UTC normalization;
10. stable \`event_id\`;
11. equivalent duplicate merge;
12. conflicting duplicate rejection;
13. multiple dates in one \`calendar.json\`;
14. coverage union across overlapping intervals;
15. uncovered interval acquisition;
16. cache-only query without a period;
17. local \`--current\` query;
18. local \`--next\` query;
19. nearest \`--date/--time\` query;
20. missing \`calendar.json\` returns valid empty result;
21. malformed \`calendar.json\` fails without replacement;
22. acquisition failure preserves last-known-good file;
23. concurrent acquisition waits on the lock;
24. second process re-checks coverage after locking;
25. atomic persistence;
26. no automatic retention;
27. delete \`--before\`;
28. delete \`--after\`;
29. delete bounded \`--before + --after\`;
30. delete \`--range\`;
31. delete \`--date\`;
32. delete exact-minute selector;
33. delete time-of-day range;
34. delete dry-run does not mutate;
35. coverage remains consistent after deletion;
36. FX symbol currency extraction;
37. unrelated currency exclusion.

---

# 13. IMPLEMENTATION FUNCTION CONTRACT

The global developer-agent naming and portability rules are defined in `AGENTS.md`; this section defines Calendar-specific function ownership boundaries.

Required function boundaries:

\`\`\`text
build_argument_parser
parse_calendar_request
normalize_symbol
parse_date
parse_time
parse_date_range

resolve_provider_period
fetch_calendar_source
extract_days_payload
parse_calendar_days
normalize_provider_event
normalize_calendar_events

build_empty_calendar_document
validate_calendar_document
load_calendar_document
save_calendar_atomic

resolve_coverage
find_uncovered_intervals
merge_coverage

merge_calendar_events
deduplicate_calendar_events

extract_symbol_currencies
filter_events_for_symbol

query_symbol_events
query_current_events
query_next_events
query_nearest_events

select_delete_interval
delete_events
delete_coverage
dry_run_delete

acquire_calendar_lock
run_acquisition
run_query
run_delete
run
main
\`\`\`

Each function owns one primary responsibility.

Avoid vague names such as:

\`\`\`text
process_data
handle_news
run_news
do_update
helper
util
\`\`\`

---

# 14. DEFINITION OF DONE

Calendar V1 is complete only when:

1. there is exactly one persistent \`<DATA_ROOT>/calendar.json\`;
2. multiple historical and future periods can coexist in that file;
3. no automatic retention/deletion exists;
4. history is removed only through explicit \`--delete\`;
5. acquisition CLI supports day/week/month/range selectors;
6. \`--query SYMBOL\` without a period is cache-only;
7. local query API is network-free and time-based;
8. stable provider-derived event IDs are used;
9. multiple acquisition intervals are tracked through coverage metadata;
10. redundant downloads are prevented using coverage union checks;
11. concurrent writers wait for the existing lock and re-check state after locking;
12. acquisition failure preserves the last-known-good file;
13. missing \`calendar.json\` is a valid no-data condition;
14. corrupt existing data is not silently replaced;
15. delete operations update events and coverage consistently;
16. all event times are canonical UTC;
17. Monitor receives only normalized event data and never provider HTML;
18. Calendar never modifies canonical SMC state;
19. no symbol-specific News JSON or separate cache JSON is created;
20. all deterministic Calendar tests pass;
21. no \`.agents/skills/smc/\` file is modified.
