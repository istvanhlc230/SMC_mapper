# Calendar Implementation Design

Implementation baseline: 2.4.13

## 0. Source layout

    calendar.py
        stable repository-root CLI entrypoint

    CALENDAR/
        api.py
        config.py
        models.py
        domain.py
        storage.py
        providers.py
        parsing.py
        operations.py
        presentation.py
        cli.py
        source modules only

    CALENDAR/calendar.json
        canonical runtime cache (unless SMC_DATA_ROOT explicitly overrides it)

The split is structural; persistent schema and public CLI semantics remain unchanged. The default cache is `CALENDAR/calendar.json`; `SMC_DATA_ROOT` explicitly overrides the runtime data root.

## 1. Runtime architecture

    Calendar Update Engine
        |             |
        v             v
    ForexFactory   Yahoo Finance
        \             /
          normalize
              |
        provider dedupe
              |
        calendar.json
              |
        local Monitor read

The engine runs in a process that may be detached from the Monitor.

## 2. CLI

    python calendar.py SYMBOL YYYY.MM.DD
    python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
    python calendar.py SYMBOL current
    python calendar.py SYMBOL today
    python calendar.py SYMBOL tomorrow
    python calendar.py SYMBOL yesterday
    python calendar.py SYMBOL prev_week
    python calendar.py SYMBOL next_week
    python calendar.py SYMBOL prev_month
    python calendar.py SYMBOL next_month
    python calendar.py SYMBOL latest
    python calendar.py SYMBOL next

User examples:

    python calendar.py EURUSD today
    python calendar.py EURUSD prev_week
    python calendar.py EURUSD next_week
    python calendar.py EURUSD prev_month
    python calendar.py EURUSD next_month
    python calendar.py EURUSD 2026.10.01
    python calendar.py EURUSD 2026.10.01-2026.10.31
    python calendar.py EURUSD 2026.10.01@10:00-2026.10.31@22:00
    python calendar.py EURUSD 2026.10.01@10:00
    python calendar.py EURUSD 10:00-11:00 refresh
    python calendar.py EURUSD --range 2026.10.01-
    python calendar.py EURUSD --range 2026.10.01@10:00-
    python calendar.py NVDA current
    python calendar.py EURUSD latest

Both --range -END and --range START- are explicit open-ended range forms. For START-, the end boundary is current UTC time at execution; for -END, the start boundary is resolved from the latest retained visible event for SYMBOL. Both forms are query/refresh scopes and are not valid delete scopes.

`current`, `latest`, and `next` are explicit public scopes. A positional `HH:MM-HH:MM` scope is a current-UTC-day shorthand for a canonical datetime range. All three are read-only cache lookups. `current` applies provider/symbol watermark boundaries; it does not contact providers. Provider acquisition for current is explicit through the trailing `refresh` modifier (`current refresh`). `latest` selects the most recent past/current event and `next` selects the nearest future scheduled ForexFactory economic event. Relative day, week, and month scopes are explicit public aliases resolved at execution time.

## 3. Symbol/provider resolution

    HUF    -> ForexFactory
    EURHUF -> ForexFactory + Yahoo Finance
    USDJPY -> ForexFactory + Yahoo Finance
    NVDA   -> Yahoo Finance

The canonical symbol is never replaced by a provider symbol.

## 4. Debug

`--debug` controls diagnostic exception output only. Diagnostics and tracebacks are
stderr-only and are never mixed into the machine-readable stdout result or persisted
Calendar data. Without `--debug`, catch handlers emit only the concise user-facing
error and return the documented error status, including the generic unexpected-
exception boundary. With `--debug`, that boundary also prints the traceback to stderr.

## 5. Update modes

For explicit Yahoo requests, a historical range must not move a pre-existing
current cursor backward. A request intersecting the present may advance that
cursor only through `min(requested_end, now)`; a future-only request does not
bootstrap Yahoo current state.

Explicit ranges perform historical acquisition.

current uses per-provider/per-symbol watermarks for the committed cache query. A missing watermark contributes no incremental events. No synthetic bootstrap timestamp is created. `current refresh` is the explicit provider acquisition path and uses its documented bounded first-use interval when no applicable watermark exists.

## 6. Coverage

ForexFactory coverage may be COMPLETE for an acquired UTC interval.

Yahoo rolling news is not granted historical COMPLETE coverage without evidence.

For FX pairs, Yahoo Search must return an exact matching Forex/Currency instrument before Yahoo news is acquired. No generic `PAIR=X` fallback is permitted. For USD-base canonical pairs, the quote-currency `=X` form may be derived as a verification candidate, but it must still be returned exactly by Yahoo Search and classified as a Currency instrument. When no verified Yahoo Forex instrument exists, no Yahoo event, coverage interval, or watermark is persisted for that pair. Explicit Yahoo acquisition persists only the requested interval; its current cursor is capped at `min(requested_end, now)` and never regresses.

FX-pair recognition uses the full currency-code universe, while the standalone CLI
currency set may remain intentionally narrower. ForexFactory event validation uses
the same currency-code universe so valid pair components are not rejected merely
because their standalone currency is not a CLI-routable currency.

Coverage never comes from the mere presence of an event.

For explicit Yahoo requests, rolling-feed records outside the requested interval are
not persisted as part of that acquisition.



### 6.1 ForexFactory Detail failure semantics

ForexFactory base-event acquisition and Detail enrichment are independently failure-isolated.
If the calendar rows are acquired successfully but one or more event Detail requests fail:

- successfully acquired base events remain persisted;
- the affected event retains `details.specs=[]` for this acquisition attempt;
- the provider result is `PARTIAL` and reports the number of Detail failures;
- the affected acquisition coverage interval is `PARTIAL`, never `COMPLETE`;
- the ForexFactory watermark is not advanced by that acquisition;
- a later explicit acquisition must treat the partial interval as uncovered and retry it;
- `current` must follow the same rule and retain its previous successful watermark until the
  Detail-complete acquisition succeeds.

A Detail failure must therefore never become an apparently complete cached interval merely because
an empty `specs` list is present. A legitimately empty Detail response remains valid; retry state is
represented by coverage status, not by the `specs` list itself.

## 7. Persistence

Shared schema version is 2.

Event envelope is:

    event_id
    symbol
    asset_type
    event_type
    source
    timestamp
    title
    details

Watermarks are keyed by provider|canonical_symbol.

## 8. Failure isolation

A failed provider:
- leaves previous provider data intact;
- contributes diagnostic state internally and aggregate `PARTIAL`/`UNAVAILABLE` status as documented;
- does not expose provider `ERROR` records or exception text in normal public output;
- does not erase another provider result.

All-provider failure is UNAVAILABLE.

## 9. Local consumer boundary

Monitor validates schema and reads committed JSON.

Monitor does not perform provider access or provider-specific parsing.

## 10. Symbol-scoped deletion

Public forms:

    python calendar.py delete SYMBOL YYYY.MM.DD
    python calendar.py delete SYMBOL YYYY.MM.DD-YYYY.MM.DD
    python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM
    python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM

Bare delete remains the full-cache reset.

Deletion is performed without provider access and under the Calendar lock.

All Calendar read/modify/persist acquisition paths are also serialized by the same lock.

For Yahoo Finance, matching symbol-owned news events are physically removed.
For ForexFactory, economic events are shared facts and are retained; only the
symbol/provider coverage is invalidated. This makes the deletion safe when the
same economic event is consumed by multiple FX symbols.

If deletion reaches the newest known event timestamp for a provider/symbol,
that watermark is removed so current cannot silently skip the deleted tail.

## 11. Repository hygiene

Development artifacts belong under dev_tmp/. The repository root must not receive ad-hoc downloads, caches, debug outputs, or experiments.


## 11.1 Provider Detail specifications

Rendered-row recognition is event-ID-first: a rendered row carrying the provider event-instance ID must be
parsed even when the current CSS row class is absent or renamed; the CSS row class is advisory only.

The calendar-page Detail control is a presentation/navigation element, not a canonical event URL field.
For each acquired ForexFactory event, Calendar requests the provider Detail JSON using the numeric
provider event ID and stores its ordered `specs` under `details.specs` as:

    { "order": <integer>, "title": <string>, "html": <string> }

The provider `html` is preserved verbatim. This retains Source and Next Release hyperlinks and future
provider formatting without requiring the Calendar to invent an event URL.

A malformed or unavailable Detail JSON response is a ForexFactory provider failure. No synthetic URL or
placeholder Detail content is generated. Yahoo Finance continues to use `details.url` for article URLs.


## 11.2 Legacy Detail enrichment

A complete schema-2 ForexFactory coverage interval is considered incomplete when an existing ForexFactory
event inside the requested overlap lacks details.specs. The interval is reacquired so the provider Detail
specifications can be added. This is an enrichment rule within schema version 2, not schema migration.


## 12. Portability boundary

Provider networking, HTML parsing, threading, and OS-specific file locking are infrastructure concerns. Domain decisions use explicit event, interval, coverage, watermark, filtering, merge, and refresh fields so the semantic layer can be represented naturally in MQL4/MQL5.

## 13. Rendered time rule

A rendered ForexFactory event without a concrete clock is rejected by the fallback parser instead of being assigned midnight.


### 6.2 Successful no-match semantics

An acquisition that reaches the provider successfully but yields no events for the requested symbol and interval is a successful empty result. It is represented as `NO_MATCH`, not `PARTIAL`. The query layer maps an all-`NO_MATCH` provider result set to `NO_RELEVANT_EVENT`. `PARTIAL` is reserved for actual incomplete acquisition state. Yahoo Finance uses `NO_MATCH` for an empty successful news collection; `SKIPPED_NO_FOREX_PAIR` remains the distinct verified-instrument-unavailable state.


### 6.3 Source activity documentation

The Calendar implementation documents function activity and meaningful state variables directly in the Python source. Documentation is concise and implementation-oriented: functions state their role in the Calendar flow, important module state variables state their purpose, and non-obvious transactional/local state is explained where needed. This is documentation only and must not alter Calendar behavior or persistent contracts.
