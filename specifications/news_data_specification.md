# News Data Specification

**Status:** Working implementation specification for future \`news_data.py\`.  
**Scope:** External economic-news acquisition, normalization, update, persistence, and consumer contract for \`smc_monitor.py\`.  
**Canonical authority:** \`.agents/skills/smc/\` remains the sole authority for canonical SMC semantics. News data is non-canonical external context.

---

# 0. PURPOSE AND HARD BOUNDARIES

## 0.1 Finished-product role

\`news_data.py\` is a standalone normalized economic-news data process.

Its responsibilities are:

1. acquire scheduled economic-calendar events from an external provider;
2. normalize provider-specific event records into a provider-independent event contract;
3. normalize all event times to canonical UTC;
4. preserve relevant event metadata/provenance;
5. merge/deduplicate events deterministically;
6. maintain bounded operational retention;
7. persist a normalized shared news-events JSON store;
8. expose no canonical SMC interpretation.

It is not an SMC analyzer and does not decide whether a setup, POI, target, RR, or alert is valid.

## 0.2 Ownership

~~~text
News Provider(s)
        ↓
news_data.py
        ↓
news_events.json
        ↓
smc_monitor.py
~~~

The Monitor consumes persisted normalized news data. It does not call a provider directly.

The news data module must not depend on:

- smc_mapper.py;
- smc_monitor.py;
- market_data.py;
- .agents/skills/smc/;
- legacy monitoring/analyzer modules.

Canonical SMC rules do not consume news events in V1.

---

# 1. DATA MODEL

## 1.1 NewsEvent

Conceptual explicit model:

~~~python
@dataclass(frozen=True)
class NewsEvent:
    event_id: str
    source_timestamp: datetime
    source_timezone: str | None
    event_time_utc: datetime
    title: str
    impact: str
    affected_currencies: list[str]
    affected_instruments: list[str]
    status: str
    forecast: str | None
    previous: str | None
    actual: str | None
    source: str
~~~

The exact provider fields may vary, but the normalized contract must preserve at minimum:

- deterministic event identity;
- event time UTC;
- title;
- impact;
- affected currencies/instruments;
- lifecycle/status;
- source provenance.

## 1.2 Impact

Use an explicit normalized impact vocabulary:

~~~text
LOW
MEDIUM
HIGH
UNKNOWN
~~~

Provider-specific impact labels are normalized into this vocabulary.

\`UNKNOWN\` must not be silently promoted to HIGH.

## 1.3 Status

Use an explicit normalized event status:

~~~text
SCHEDULED
RELEASED
CANCELLED
UNKNOWN
~~~

A released event may carry actual data when the source provides it.

The Monitor warning logic is primarily concerned with future \`SCHEDULED\` events.

## 1.4 Time-domain contract

Datasource-native event time is source/provenance data.

Canonical \`event_time_utc\` is the only persisted time used for sorting, warning-window evaluation, and cross-module consumption.

Rules:

- timezone-aware source timestamps convert deterministically to UTC;
- absolute epoch/UTC timestamps convert directly to UTC;
- naive source timestamps without known source timezone are rejected;
- host local timezone must never be assumed to be source timezone;
- fixed UTC offsets must not replace DST-aware named timezones;
- source timestamp/timezone may be retained for provenance but is not a canonical event-time substitute.

---

# 2. PROVIDER ABSTRACTION

## 2.1 NewsDataProvider

Small provider contract:

~~~python
class NewsDataProvider:
    def fetch_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> list[NewsEvent]:
        ...
~~~

The exact provider is an implementation decision.

Provider-specific API transport, authentication, pagination, retries, field mapping, and timezone handling belong to the provider adapter.

## 2.2 create_news_provider

~~~python
def create_news_provider(provider_name: str) -> NewsDataProvider:
    ...
~~~

Keep provider selection behind one function.

No provider CLI option is required in V1 unless explicitly approved.

---

# 3. JSON PERSISTENCE

## 3.1 File

Use one shared store:

~~~text
news_events.json
~~~

This is intentionally not per-symbol because the same economic event may affect multiple symbols.

The file is not canonical SMC state.

## 3.2 Shape

~~~json
{
  "events": [
    {
      "event_id": "...",
      "source_timestamp": "...",
      "source_timezone": "America/New_York",
      "event_time_utc": "...",
      "title": "...",
      "impact": "HIGH",
      "affected_currencies": ["USD"],
      "affected_instruments": [],
      "status": "SCHEDULED",
      "forecast": "...",
      "previous": "...",
      "actual": null,
      "source": "..."
    }
  ],
  "available_start": "...",
  "available_end": "..."
}
~~~

All persisted event times are UTC.

Source-time fields are provenance only.

## 3.3 Deterministic identity

\`event_id\` must be stable across repeated provider downloads.

When the provider supplies a stable event ID, preserve it.

If not, derive a deterministic identity from stable normalized fields such as:

~~~text
source
event_time_utc
title
affected currencies/instruments
~~~

The implementation must not use array position or random IDs.

If the same event identity arrives with materially conflicting immutable fields, treat it as a data-integrity conflict rather than silently overwriting the existing event.

---

# 4. ACQUISITION AND UPDATE

## 4.1 update range

The news updater may retrieve:

- upcoming scheduled events;
- recent released events needed for source reconciliation.

Do not retrieve an arbitrary unbounded history.

## 4.2 Incremental behavior

Use deterministic range updates.

Merge by \`event_id\`.

Sort events chronologically by \`event_time_utc\`.

Deduplicate repeated provider records.

## 4.3 Retention

Retention is operational and not canonical.

Retain at least:

- all upcoming scheduled events in the configured forward warning horizon;
- a bounded recent past needed for reconciliation/debugging.

Exact V1 retention is one module-owned operational decision.

## 4.4 Stale/missing provider data

The module must distinguish:

~~~text
NO EVENTS
vs.
NO DATA AVAILABLE
~~~

An empty provider result must not automatically mean that no events exist.

A provider failure must remain observable.

---

# 5. JSON ATOMIC PERSISTENCE

Use complete read-modify-write persistence:

1. serialize complete event document deterministically;
2. write a temporary file in the same directory;
3. flush/close;
4. atomically replace target;
5. retry finite transient failures;
6. remove temporary file on failure.

Do not write JSON in place.

No separate lock file is required in V1 when one Monitor orchestrator owns news-data updates.

---

# 6. CLI AND RUNTIME CONTRACT

V1 CLI contract:

~~~text
python news_data.py
    [--starttime ISO8601]
    [--endtime ISO8601]
    [--live]
    [--debug]
~~~

The exact V1 acquisition schedule may invoke the CLI without exposing all options to end users; the process boundary remains explicit.

Debug is stderr-only.

Normal successful execution is silent.

The module emits no canonical SMC result through stdout.

---

# 7. FUNCTIONS

Required function boundaries:

~~~python
build_argument_parser()
parse_news_data_request(argv)
validate_news_data_request(request)
parse_iso8601(value)
normalize_source_event(event)
normalize_news_events(events)
build_event_id(event)
validate_news_event(event)
merge_news_events(existing, incoming)
sort_news_events(events)
apply_news_retention(events)
load_news_events(path)
save_news_events_atomic(path, document)
resolve_news_range(request, existing)
update_news_events(request, provider)
run(request)
main(argv)
~~~

Each function has one responsibility.

---

# 8. PURE-FUNCTION AND DETERMINISM CONTRACT

Pure/deterministic boundaries should include:

~~~text
parse_iso8601
normalize_source_event
build_event_id
validate_news_event
merge_news_events
sort_news_events
apply_news_retention
~~~

They must not depend on hidden global state or host timezone.

---

# 9. MQL4/MQL5 PORTABILITY

The domain contract uses explicit named fields and arrays.

Portable conceptual models:

~~~text
NewsEvent
NewsDataRequest
NewsDocument
~~~

Python-specific provider/process mechanics do not form part of the portable domain contract.

UTC timestamps and explicit timezone identifiers map naturally to MQL datetime/string representations.

---

# 10. TESTING REQUIREMENTS

At minimum:

~~~text
test_news_source_timezone_normalizes_to_utc
test_news_naive_source_time_is_rejected
test_news_event_id_is_deterministic
test_news_duplicate_events_merge
test_news_conflicting_identity_is_rejected
test_news_events_sort_by_utc_time
test_news_retention_preserves_future_events
test_news_atomic_save
test_news_empty_result_is_distinct_from_provider_failure
test_news_debug_is_stderr_only
~~~

Provider tests should use doubles and must not require live network access.

---

# 11. DEVELOPER-AGENT RULES

Do not:

- implement canonical SMC logic;
- infer event impact from title text when provider impact is unavailable;
- fabricate events;
- guess source timezone;
- make the Monitor depend on provider-specific news fields;
- write alert state into the news store;
- make news events mutate Mapper state.

When implementation decisions are not specified, choose the smallest direct implementation and record it in AGENT_REVIEW.md.

**STATUS: IMPLEMENTATION-READY NEWS-DATA CONTRACT — NORMALIZED UTC EVENTS FOR MONITOR WARNING CONSUMPTION.**
