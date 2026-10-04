# Calendar Implementation Design

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
    python calendar.py SYMBOL latest
    python calendar.py SYMBOL next

User examples:

    python calendar.py EURUSD 2026.10.01
    python calendar.py EURUSD 2026.10.01-2026.10.31
    python calendar.py EURUSD 2026.10.01@10:00-2026.10.31@22:00
    python calendar.py EURUSD 2026.10.01@10:00
    python calendar.py NVDA current
    python calendar.py EURUSD latest

`current`, `latest`, and `next` are explicit public scopes. `latest` and `next` are read-only cache lookups; `current` performs watermark-based incremental acquisition.
Old relative date scopes remain removed.

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

current uses per-provider/per-symbol watermarks.

No watermark means BOOTSTRAP_REQUIRED and no invented start time.

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
- is surfaced as ERROR;
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


## 11.1 Provider detail URLs

ForexFactory normalized economic events expose `details.url` when the provider supplies the concrete calendar event detail-page URL in the structured payload or rendered calendar markup. The implementation captures the actual provider href or a provider-supplied event-base slug; it does not fabricate a detail URL from a calendar event-instance ID. Yahoo Finance news continues to use `details.url` for the provider article URL.
