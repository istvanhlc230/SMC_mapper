# News Data Specification

**Status:** Working implementation specification for future `news_data.py`.  
**Scope:** External economic-news acquisition, normalization, update, persistence, and consumer contract for `smc_monitor.py`. V1 uses FMP as the sole concrete provider.  
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. News data is non-canonical external context.

---

# 0. PURPOSE AND HARD BOUNDARIES

## 0.1 Finished-product role

`news_data.py` is a standalone normalized economic-news data process.

Its responsibilities are:

1. acquire scheduled economic-calendar events from an external provider;
2. normalize provider-specific records into a provider-independent event contract;
3. normalize all event times to canonical UTC;
4. preserve relevant event metadata/provenance;
5. merge/deduplicate events deterministically;
6. maintain bounded operational retention;
7. persist a normalized symbol-scoped news-data JSON store;
8. expose no canonical SMC interpretation.

It is not an SMC analyzer and does not decide whether a setup, POI, target, RR, or alert is valid.

## 0.2 Ownership

```text
FMP Economic Calendar API
        ↓
FMPNewsDataProvider
        ↓
news_data.py --symbol SYMBOL
        ↓
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_news_data.json
        ↓
smc_monitor.py
```

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

## 1.1 ProviderEvent and NewsEvent ownership

The provider adapter returns **provider-native records**, not canonical `NewsEvent` objects.

Conceptual boundary:

```python
ProviderEvent = Any  # provider-specific adapter-owned record

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
```

Provider-specific transport fields remain inside the provider adapter. `normalize_source_event()` is the single boundary that converts a provider record into the normalized `NewsEvent`.

## 1.2 NewsDataRequest

```python
@dataclass(frozen=True)
class NewsDataRequest:
    symbol: str
    start_time: datetime | None
    end_time: datetime | None
    live: bool
    debug: bool
```

One `news_data.py` execution is symbol-scoped. The request symbol determines the symbol output directory and news-data file path. The existing common data root is unchanged, and no data-path CLI option is required.

## 1.3 Impact

Use an explicit normalized impact vocabulary:

```text
LOW
MEDIUM
HIGH
UNKNOWN
```

Provider-specific impact labels are normalized into this vocabulary.

`UNKNOWN` must not be silently promoted to HIGH.

## 1.4 Status

Use an explicit normalized event status:

```text
SCHEDULED
RELEASED
CANCELLED
UNKNOWN
```

For V1 Monitor warnings, only future `SCHEDULED` events are warning candidates. `RELEASED`, `CANCELLED`, and `UNKNOWN` events are not eligible for a future-event warning.

## 1.5 Time-domain contract

Datasource-native event time is source/provenance data.

Canonical `event_time_utc` is the authoritative persisted event time used for sorting, coverage, warning-window evaluation, and cross-module consumption.

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

The provider contract is intentionally provider-agnostic so a future provider can be added without changing `NewsEvent`, persistence, or Monitor contracts. V1 implements **FMP only**. There is no fallback provider and no multi-provider runtime selection in V1.

The provider contract returns provider-native records. Normalization remains owned by `news_data.py`.

```python
class NewsDataProvider:
    def fetch_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ProviderEvent]:
        ...

    def fetch_current(self) -> list[ProviderEvent]:
        ...
```

`fetch_range()` is used for explicit coverage. `fetch_current()` obtains the provider's current calendar state and is used when the request has `live=True`.

Provider-specific API transport, authentication, pagination, retries, raw field mapping, and source metadata handling belong to the provider adapter.

The provider adapter must not implement Monitor warning windows, SMC interpretation, target/RR logic, or alerting.

## 2.2 FMP provider implementation and factory

```python
class FMPNewsDataProvider(NewsDataProvider):
    ...

def create_news_provider(provider_name: str = "fmp") -> NewsDataProvider:
    ...
```

`NewsDataProvider` remains the stable abstraction boundary. `FMPNewsDataProvider` is the only V1 implementation. `create_news_provider()` is the single extension point for a future provider.

V1 must reject provider names other than `fmp`; no fallback provider and no multi-provider runtime selection are implemented.

FMP uses the Economic Calendar API endpoint and reads `FMP_API_KEY` from the environment. The key must never be hardcoded or persisted.

FMP's documented calendar timestamps are UTC. The adapter therefore normalizes FMP timestamps as UTC and must not assume host-local time.

FMP's documented calendar range is limited to a maximum 90-day interval per request. The adapter owns deterministic request chunking when a caller requests a larger range.

The FMP response fields used by V1 are provider-native: `date`, `event`, `currency`, `impact`, `estimate`, `previous`, and `actual`. They are mapped only at `normalize_source_event()` into the canonical `NewsEvent` contract.

No FMP-specific field may leak into `NewsEvent`, Monitor, or the persisted canonical news schema.

No provider CLI option is required in V1.

## 2.3 Live acquisition semantics

`live=True` does **not** mean a streaming connection.

It means:

1. acquire the provider's current calendar state through `fetch_current()`;
2. normalize the returned provider records through the normal normalization pipeline;
3. merge/deduplicate them into the symbol-scoped persisted store;
4. persist the resulting complete document atomically;
5. advance `last_successful_update_utc` only after that atomic persistence succeeds.

The Monitor remains responsible for deciding when a live refresh is due.

If both an explicit range and `live=True` are supplied, perform both acquisitions and merge them deterministically; `live` does not discard the requested range.

---

# 3. JSON PERSISTENCE

## 3.1 File

Use one symbol-scoped store per symbol:

```text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_news_data.json
```

The same external economic event may therefore appear in multiple symbol stores. This duplication is intentional and provides filesystem-level symbol isolation.

News Data preserves explicit affected currencies/instruments and does not perform title-text relevance inference. Final analysis/event relevance remains Monitor-owned.

The file is not canonical SMC state.

## 3.2 Shape

The persisted document carries symbol identity and acquisition state alongside normalized events.

```json
{
  "symbol": "CCCC",
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
  "available_end": "...",
  "last_successful_update_utc": "..."
}
```

All persisted event times are UTC.

`available_start` and `available_end` describe the coverage represented by the persisted news dataset, not the Monitor warning window.

`last_successful_update_utc` records the UTC time of the last successful provider acquisition and atomic persistence operation. An initial store with no successful acquisition must be distinguishable from a successful empty result.

## 3.3 Deterministic identity

`event_id` must be stable across repeated provider downloads.

### Preferred identity

When the provider supplies a stable event ID, preserve it as the normalized identity.

### Fallback identity

If the provider does not supply a stable event ID, derive a deterministic fallback from normalized identity fields:

```text
source
event_time_utc
normalized title
normalized affected currencies
normalized affected instruments
```

Use a deterministic hash/encoding; never use array position, random IDs, retrieval time, or mutable values such as forecast/actual.

The fallback identity has an explicit limitation: if the provider reschedules an event or materially changes an identity field, the fallback may represent it as a new event. It must not be treated as provider-level identity stability.

If the same `event_id` arrives with materially conflicting immutable identity fields, treat it as a data-integrity conflict rather than silently overwriting the existing identity.

Mutable fields such as forecast, previous, actual, status, and provider metadata may be reconciled without changing `event_id`.

---

# 4. ACQUISITION AND UPDATE

## 4.1 Requested coverage

News Data acquires only the coverage requested by the caller plus provider-specific pagination needed to satisfy that same range.

The Monitor owns the required forward warning horizon. News Data must not calculate or invent a warning window.

The acquisition layer may retrieve:

- upcoming scheduled events;
- recent released events explicitly included by the requested range;
- current provider state when `live=True`.

Do not retrieve arbitrary unbounded history.

## 4.2 Incremental behavior

Use deterministic range updates.

Merge by `event_id`.

Sort events chronologically by `event_time_utc`.

Deduplicate repeated provider records.

A successful provider response containing zero events is a valid **empty result** and is distinct from provider failure.

## 4.3 Retention

Retention is operational and not canonical.

News Data must not retain data based on the Monitor impact/timeframe warning-window formula.

Instead:

- caller-requested coverage is always honored;
- persisted history may be bounded by one News Data-owned retention policy;
- future scheduled events within the caller-requested coverage must not be evicted;
- recent released events may be retained for reconciliation/debugging;
- retention must not silently shrink the caller-requested coverage.

Exact V1 retention duration is one News Data implementation policy and has one owner.

## 4.4 Stale/missing provider data

The module must distinguish:

```text
SUCCESSFUL EMPTY RESULT
vs.
NO DATA AVAILABLE / PROVIDER FAILURE
```

A provider failure must:

- return a non-zero process result;
- leave the last successfully persisted JSON intact;
- not fabricate events;
- remain observable through diagnostics.

A successful empty result may update acquisition metadata and coverage while containing zero events.

The Monitor determines whether persisted data is stale for runtime warning purposes using its own runtime contract.

---

# 5. JSON ATOMIC PERSISTENCE

Use complete read-modify-write persistence:

1. serialize the complete event document deterministically;
2. write a temporary file in the same directory;
3. flush/close;
4. atomically replace the target;
5. retry finite transient failures;
6. remove the temporary file on failure.

Do not write JSON in place.

No separate lock file is required in V1 when one Monitor orchestrator owns news-data updates.

`last_successful_update_utc` advances only after successful acquisition and atomic persistence.

---

# 6. CLI AND RUNTIME CONTRACT

V1 CLI contract:

```text
python news_data.py --symbol SYMBOL
    [--starttime ISO8601]
    [--endtime ISO8601]
    [--live]
    [--debug]
```

Rules:

- `--symbol` is required;
- `--starttime` and `--endtime` define explicit UTC-resolved requested coverage;
- if both are present, start must not be after end;
- `--live` requests current provider-state acquisition as defined in §2.3;
- no per-file data-path option exists;
- the symbol directory is resolved automatically;
- debug is stderr-only;
- normal successful execution is silent;
- the module emits no canonical SMC result through stdout.

The process boundary is explicit even when the Monitor invokes the CLI automatically.

---

# 7. FUNCTIONS

Required function boundaries:

```python
build_argument_parser()
parse_news_data_request(argv)
validate_news_data_request(request)
parse_iso8601(value)
normalize_source_event(event)
normalize_news_events(events)
normalize_impact(value)
normalize_status(value)
normalize_affected_metadata(value)
build_event_id(event)
validate_news_event(event)
merge_news_events(existing, incoming)
sort_news_events(events)
apply_news_retention(events)
get_symbol_data_directory(symbol, data_directory)
get_news_data_path(symbol, data_directory)
load_news_data(path, symbol)
save_news_data_atomic(path, document)
resolve_news_range(request, existing)
update_news_events(request, provider)
run(request)
main(argv)
```

Provider acquisition remains behind the provider interface and does not leak provider-specific fields into the normalized contract.

Each function has one responsibility.

---

# 8. PURE-FUNCTION AND DETERMINISM CONTRACT

Pure/deterministic boundaries should include:

```text
parse_iso8601
normalize_source_event
normalize_impact
normalize_status
normalize_affected_metadata
build_event_id
validate_news_event
merge_news_events
sort_news_events
apply_news_retention
```

They must not depend on hidden global state or host timezone.

Acquisition time used for `last_successful_update_utc` is supplied by the orchestration boundary; pure normalization functions must not read the wall clock.

---

# 9. MQL4/MQL5 PORTABILITY

The domain contract uses explicit named fields and arrays.

Portable conceptual models:

```text
NewsEvent
NewsDataRequest
NewsDocument
```

Python-specific provider/process mechanics do not form part of the portable domain contract.

UTC timestamps and explicit timezone identifiers map naturally to MQL datetime/string representations.

---

# 10. TESTING REQUIREMENTS

At minimum:

```text
test_news_source_timezone_normalizes_to_utc
test_news_naive_source_time_is_rejected
test_news_provider_returns_raw_events_before_normalization
test_news_live_uses_current_provider_state
test_news_range_and_live_are_merged_deterministically
test_news_event_id_is_deterministic
test_news_provider_id_is_preserved
test_news_fallback_identity_ignores_mutable_fields
test_news_duplicate_events_merge
test_news_conflicting_identity_is_rejected
test_news_events_sort_by_utc_time
test_news_requires_symbol
test_news_data_path_is_symbol_scoped
test_news_symbol_identity_matches_path
test_news_retention_preserves_requested_future_coverage
test_news_atomic_save
test_news_last_successful_update_advances_only_after_atomic_persist
test_news_failed_provider_keeps_last_good_store
test_news_empty_result_is_distinct_from_provider_failure
test_news_debug_is_stderr_only
test_news_only_scheduled_future_events_are_warning_candidates
```

Provider tests should use doubles and must not require live network access.

---

# 11. DEVELOPER-AGENT RULES

Do not:

- implement canonical SMC logic;
- infer event impact from title text when provider impact is unavailable;
- fabricate events;
- guess source timezone;
- calculate or persist Monitor warning windows;
- make the Monitor depend on provider-specific news fields;
- perform final symbol/event relevance inference from title text;
- read or write another symbol's news-data file;
- write alert state into the news store;
- make news events mutate Mapper state;
- silently treat provider failure as a successful empty result.

Ownership rules:

- Provider adapter owns provider transport and raw provider records.
- News Data owns normalization, UTC conversion, event identity, merge/deduplication, retention, and JSON persistence.
- Monitor owns final symbol/event relevance evaluation, warning-window calculation, warning scheduling, and warning deduplication.
- Canonical SMC remains independent of news.

When implementation decisions are not specified, choose the smallest direct implementation and record it in AGENT_REVIEW.md.

**STATUS: IMPLEMENTATION-READY NEWS-DATA CONTRACT — PROVIDER-RAW → NORMALIZED UTC EVENTS → SYMBOL-SCOPED STORE → MONITOR WARNING CONSUMPTION.**


---

# 9. V1 PROVIDER DECISION

**FMP is the sole concrete News Data provider in V1.** The architecture remains provider-agnostic through `NewsDataProvider`, `ProviderEvent`, `normalize_source_event()`, and `create_news_provider()`. A future provider may be added behind that boundary without changing the canonical `NewsEvent` contract.

There is **no fallback provider** in V1. Provider failure is a failed News Data update: the last good symbol-scoped JSON remains intact and the process returns non-zero.
