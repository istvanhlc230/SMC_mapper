# Calendar Module Specification

Status: Current V2 specification.

Scope:
- unified economic-calendar and news acquisition;
- automatic provider resolution;
- watermark-based incremental updates;
- normalized shared persistence;
- local querying;
- deterministic deletion;
- atomic persistence;
- Monitor process boundary.

Canonical SMC authority remains .agents/skills/smc/. Calendar/news data is external runtime context.

## 0. Purpose and boundaries

calendar.py is the executable boundary for the Calendar Update Engine.

The Update Engine owns provider access, normalization, provider-specific identity, deduplication, coverage, watermarks, atomic persistence, and local query semantics.

The Monitor does not call ForexFactory or Yahoo directly and does not block its candle-close path on Calendar network activity.

There is one persistent data artifact:

    <DATA_ROOT>/calendar.json

Development-only temporary artifacts belong under dev_tmp/.

## 1. Providers

ForexFactory:
- primary source for economic events;
- structured days payload is the canonical provider representation;
- normalized fields include id, dateline, currency, name, impactName/impactClass, actual, forecast, previous;
- provider country codes are never used as canonical currencies.

Yahoo Finance:
- complementary source for news;
- used for FX-pair news and ticker news;
- provider symbol is kept separate from canonical symbol;
- Yahoo news is event_type=news, never economic.

Automatic routing:

    supported three-letter currency -> ForexFactory
    recognized six-letter FX pair   -> ForexFactory + Yahoo Finance
    other valid ticker              -> Yahoo Finance

No --forex, --ticker, or --provider flags exist.

## 2. Yahoo Forex resolution

Canonical symbol examples:

    EURUSD
    EURHUF
    USDJPY

Provider mappings include:

    EURUSD -> EURUSD=X
    EURHUF -> EURHUF=X
    USDJPY -> JPY=X
    USDCHF -> CHF=X
    USDCAD -> CAD=X
    USDCNY -> CNY=X

The Yahoo instrument list observed from regional Currencies pages is a reference
snapshot, not a closed whitelist. Runtime resolution is provider-verified: the
resolver queries Yahoo Finance Search and accepts a candidate only when Yahoo
returns the exact provider symbol as a Forex currency instrument
(quoteType=CURRENCY or an explicit Currency type display). The resolver must
never synthesize a missing Yahoo Forex symbol. For a USD-base canonical pair,
the quote-currency =X form may be derived as a verification candidate
(for example GBP=X for USDGBP), but it is never accepted without the same
exact-symbol Forex/Currency verification.

If Yahoo provides no verified Forex instrument for the requested canonical pair,
the Calendar does not create Yahoo news events for that pair and does not advance
Yahoo coverage or watermark for that request. This is a provider-availability
state, not an empty successful acquisition.

Direct Yahoo Forex reference snapshot (not a closed whitelist):

    EURUSD=X GBPUSD=X AUDUSD=X NZDUSD=X EURJPY=X GBPJPY=X EURGBP=X
    EURCAD=X EURSEK=X EURCHF=X EURHUF=X AUDGBP=X AUDJPY=X AUDNZD=X
    USDCNY=X USDHKD=X USDSGD=X USDINR=X USDMXN=X USDPHP=X USDIDR=X
    USDTHB=X USDMYR=X USDZAR=X USDRUB=X GBPAUD=X GBPBRL=X GBPCAD=X
    GBPCHF=X GBPCNY=X GBPINR=X GBPNOK=X GBPQAR=X GBPZAR=X

Alternate USD-base representations:

    JPY=X -> USDJPY   CHF=X -> USDCHF   CAD=X -> USDCAD
    CNY=X -> USDCNY   HKD=X -> USDHKD   SGD=X -> USDSGD
    INR=X -> USDINR   MXN=X -> USDMXN   PHP=X -> USDPHP
    IDR=X -> USDIDR   THB=X -> USDTHB   MYR=X -> USDMYR
    ZAR=X -> USDZAR   RUB=X -> USDRUB

Additional regional observations include CADUSD=X, CADEUR=X, CADGBP=X, CADCNY=X,
SGDMYR=X, SGDJPY=X, SGDHKD=X, SGDIDR=X, and SGDCNY=X.

This is a provider reference snapshot, not a permanent whitelist. The snapshot
is descriptive only; provider verification is authoritative at runtime.

## Debug contract

`--debug` is an optional CLI diagnostic flag.

- Without `--debug`, normal errors remain concise and are written to stderr; detailed
  exception diagnostics and tracebacks are not printed.
- With `--debug`, diagnostic exception information and tracebacks may be printed to
  stderr only, including provider-level `try/except` diagnostics and unexpected
  exceptions that reach the CLI boundary.
- `--debug` never changes the machine-readable stdout contract, event data, coverage,
  watermark semantics, or provider routing.
- `--debug` is presentation/diagnostic state only and never enters canonical data.

## 3. Canonical CLI

Public query forms:

    python calendar.py SYMBOL YYYY.MM.DD
    python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
    python calendar.py SYMBOL current
    python calendar.py SYMBOL next

Delete forms:

    python calendar.py delete
    python calendar.py delete SYMBOL YYYY.MM.DD
    python calendar.py delete SYMBOL YYYY.MM.DD-YYYY.MM.DD
    python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM
    python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM

Bare delete is the explicit full-cache reset.

Scoped delete is always symbol-scoped. The scope must be a date, date range,
datetime, or datetime range. current is not a delete scope.

Yahoo Finance news is symbol-owned, so a symbol-scoped deletion removes only
matching Yahoo events in the requested interval.

ForexFactory events may carry optional suppressed_for symbol metadata. A symbol
query excludes an event when its canonical symbol is present in suppressed_for.
Successful reacquisition clears that symbol's suppression for the returned facts.

ForexFactory economic events are shared currency facts. A symbol-scoped deletion
therefore invalidates only the matching provider+canonical-symbol coverage in
the requested interval and keeps the shared event record. This prevents
deleting an EUR event from breaking EURGBP when deleting EURUSD.

If the deleted interval contains the newest known event timestamp for a
provider+canonical-symbol watermark, that watermark is removed. No synthetic
watermark is created.

Removed from the public grammar:
- today
- next_day
- week
- next_week
- month
- next_month
Date syntax is YYYY.MM.DD. Time syntax is HH:MM. @ separates date/time. - separates interval endpoints. No .. syntax exists.

Date = full UTC day.
Date range = inclusive by calendar date.
Datetime = exact one-minute interval.
Datetime range = half-open start/end interval.

## 4. current semantics

current is an incremental update/query.

For each applicable provider:

    load provider|canonical_symbol watermark
              |
              +-- missing -> BOOTSTRAP_REQUIRED
              |
              +-- present -> overlap-safe incremental acquisition
                                    |
                                normalize
                                    |
                          provider-specific dedupe
                                    |
                               persist atomically
                                    |
                         return events newer than
                         watermark and no later than now

current never means:
- current-minute event lookup;
- next event;
- latest event;
- nearest event.

## 4.1 next semantics

`next` is a read-only nearest-future-event lookup over the committed `calendar.json` snapshot.

For `python calendar.py SYMBOL next`:

1. load and validate the committed Calendar document under the Calendar lock;
2. filter events according to the normal SYMBOL visibility rules, including `suppressed_for`;
3. keep only events with `timestamp > current UTC time`;
4. sort by timestamp, then source and event identity for deterministic ordering;
5. return exactly the first event, or `NO_NEXT_EVENT` when none exists.

`next` does not call ForexFactory or Yahoo Finance, does not acquire data, and does not modify coverage, watermarks, or `calendar.json`.

`next` is distinct from `current`: `current` performs incremental provider acquisition based on watermarks, while `next` only reads the committed snapshot.

No synthetic bootstrap timestamp is permitted.

Explicit date or datetime-range acquisition establishes bootstrap state.

## 5. Explicit-range acquisition

For an explicit date/time range:

1. resolve UTC interval;
2. determine applicable providers;
3. acquire provider data;
4. normalize;
5. filter timestamped records to the requested interval;
6. merge provider identities;
7. update provider/symbol coverage;
8. advance provider/symbol watermark only after successful acquisition. For Yahoo
   explicit ranges, only records inside the requested interval are persisted; the
   current cursor advances at most to min(requested_end, now) and never moves
   backward. A future-only Yahoo request does not create a bootstrap cursor;
9. validate the whole document;
10. atomically persist.

Provider failures are isolated.

A successful provider update is preserved when another applicable provider fails.

## 6. Yahoo historical limitation

Yahoo news is a rolling feed.

The implementation may fetch the currently exposed rolling news collection. For
explicit-range acquisition, only events whose timestamps fall inside the requested
interval are merged into Calendar. The fetched rolling collection must not advance
a historical request current cursor to the wall-clock acquisition time.

It must never infer complete historical coverage merely because the CLI request contains an old date.

Historical Yahoo results may be PARTIAL or NOT_AVAILABLE.

No historical news is fabricated.

## 7. Normalized event contract

Common envelope:

    event_id
    symbol
    asset_type
    event_type
    source
    timestamp
    title
    details
    suppressed_for (optional symbol-scope visibility metadata)

Allowed event_type values:

    economic
    news
    earnings
    press_release
    sec_filing

ForexFactory details include:

    currency
    impact
    actual
    forecast
    previous

Yahoo details may include:

    publisher
    url
    provider_symbol
    summary

No Yahoo impact is invented.

## 8. Persistent schema

### Software version

The Calendar CLI implementation version is exposed in `calendar.py` as `__version__` and is shown
by `python calendar.py --help`. The software version is independent from `SCHEMA_VERSION`;
changing the implementation version does not by itself change the persistent JSON schema.



If a local `calendar.json` has a schema version that differs from the expected `SCHEMA_VERSION` (e.g., version 1 vs 2), the script strictly rejects the file with `Unsupported calendar schema version.` to guarantee data integrity.
The script must never silently destroy or automatically migrate an old cache to fulfill a query. The user must explicitly purge the obsolete state using the bare `python calendar.py delete`
command or by manually removing the file. Bare delete is an explicit full-cache reset and is
intentionally allowed to replace an incompatible legacy cache without first validating its schema.
Scoped delete continues to require a valid current-schema document.

    {
      "schema_version": 2,
      "events": [],
      "coverage": [],
      "watermarks": {}
    }

Coverage is provider+canonical-symbol scoped.

Watermarks are keyed:

    provider|canonical_symbol

Watermark values contain:

    last_successful_at
    last_event_timestamp

last_successful_at advances only after successful acquisition and validated persistence preparation.

## 9. Identity and dedupe

ForexFactory identity:

    forexfactory:<provider id>

Yahoo identity:

    yahoo:<uuid>

When Yahoo provides no stable UUID, a deterministic digest of provider symbol, title, timestamp, and URL is used.

Cross-provider title similarity never causes deduplication.

Identity/time conflicts are data-integrity failures.

## 10. Failure and atomicity

Provider failure is not an empty success.

For multi-provider FX:
- one provider may succeed while the other fails;
- result is PARTIAL;
- UNAVAILABLE is used only when all applicable providers fail.

All writes use a shared Calendar lock plus temporary-file write, flush, fsync, and atomic replacement.

A write failure leaves the previously committed file unchanged.

## 11. Monitor boundary

Monitor:
- never calls a provider;
- never parses provider payloads;
- never writes calendar.json;
- may launch calendar.py as a detached/background subprocess;
- reads only the committed normalized calendar.json snapshot.

## 12. News warning boundary

Existing HIGH/MEDIUM/LOW warning-window logic applies to ForexFactory economic events because only those events have the normalized Calendar impact contract.

Yahoo news is context-only by default.

Monitor must not infer warning severity from publisher, title, URL, or source.

Any Yahoo-news severity requires an explicit future Monitor specification change.

## 13. Acceptance

Acceptance requires:
- old relative scopes removed;
- `next` returns the nearest future visible event from the committed snapshot without provider calls;
- current is watermark-based;
- missing watermark is BOOTSTRAP_REQUIRED;
- EURUSD date, date range, datetime, and datetime range parse correctly;
- NVDA routes to Yahoo;
- HUF routes to ForexFactory;
- USDJPY has independent ForexFactory and Yahoo watermarks;
- Yahoo events are news;
- Yahoo FX news is persisted only after exact provider-side Forex instrument verification;
- ForexFactory events are economic;
- provider failures remain observable;
- explicit Yahoo acquisition persists only the requested interval and does not
  jump the current cursor past the requested boundary;
- an unavailable Yahoo FX instrument cannot expose previously cached Yahoo events
  through an explicit query;
- Yahoo historical completeness is never falsely claimed;
- a missing Yahoo Forex pair is reported as provider-unavailable for that pair and
  never converted into a fabricated `=X` instrument or persisted Yahoo coverage;
- six-letter FX recognition uses the currency-code universe independently of the
  narrower standalone-currency CLI set;
- successful current-mode ForexFactory reacquisition clears the target symbol's
  `suppressed_for` marker.
