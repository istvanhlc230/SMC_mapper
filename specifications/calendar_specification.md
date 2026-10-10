# Calendar Module Specification

Status: Current V2 specification.

Calendar implementation baseline: 2.6.7.

Default DATA_ROOT is the repository `CALENDAR/` directory, so the default persistent artifact is `<repository-root>/CALENDAR/calendar.json`. `SMC_DATA_ROOT` may explicitly override this runtime location.

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

Provider refresh requested by the Monitor is a background/non-blocking operation; the candle-close processing path must not wait for network I/O.

There is one persistent data artifact:

    <DATA_ROOT>/calendar.json

Development-only temporary artifacts belong under dev_tmp/.

## 1. Providers

Calendar uses three independent provider adapters behind one common interface. All
applicable providers are queried for an acquisition; they are not modeled as a
single fallback chain.

Provider interface:

    fetch_events(symbol, start, end, **provider_options) -> normalized events

Shared HTTP transport:
- Calendar provider HTTP requests use the common HTTP client and prefer IPv4 before IPv6 because the runtime network may have an unusable or very slow IPv6 route;
- IPv6 remains a fallback if IPv4 cannot connect;
- custom transport must preserve TLS hostname verification and default environment-proxy handling;
- this applies to ForexFactory and Yahoo Finance as well as LSE, rather than only to the LSE adapter.

Required providers:

London Strategic Edge (LSE):
- primary economic-calendar provider;
- queried through the LSE economic_calendar API;
- the adapter requests IPv4-first transport because some client networks do not have working IPv6; the transport falls back to IPv6 if IPv4 cannot connect;
- the `start` and `end` request parameters are date-only strings in `YYYY-MM-DD` format, as required by the API; precise UTC datetimes remain internal and filter returned events after acquisition;
- its `region` filter accepts provider region/country codes (for example `EU`,
  `US`, and `GB`), not ISO 4217 currency codes;
- Calendar maps each supported currency code to the matching LSE region code and
  de-duplicates regions for pairs; it must not submit raw currency codes such as
  `EUR` or `USD` as region filters;
- an unmapped currency fails the LSE provider acquisition explicitly rather than
  sending an invalid region query;
- scheduled economic events are normalized to the common Calendar event contract;
- provider fields such as actual, forecast, previous, impact, currency and provider
  event identity are retained when available;
- provider HTTP error details may be surfaced only in `--debug` diagnostics, with
  credentials and request URL query data excluded;
- provider URL/source metadata is retained when available;
- LSE does not provide stock-news events for the Calendar news role.

ForexFactory:
- independent economic-calendar provider;
- the implementation uses ForexFactory's native calendar query grammar;
- a single concrete calendar day uses day=<monD.YYYY>;
- a multi-day interval uses range=<monD.YYYY>-<monD.YYYY>;
- the range-filtered calendar HTML and legacy embedded structured payload are accepted;
- a rendered row without a concrete provider clock (for example `All Day`, `Tentative`, or an empty time) is never assigned a synthetic timestamp;
- during acquisition, an untimeable row is isolated and skipped while other timestampable rows are retained; the unresolved row count makes the provider result `PARTIAL`, and the provider watermark is not advanced; explicit-range acquisition also persists `PARTIAL` coverage so a later acquisition retries the interval, while forced refresh leaves existing coverage unchanged;
- Detail enrichment remains provider-specific and is preserved under details.specs.

Yahoo Finance:
- independent news provider;
- used for current/rolling FX-pair and ticker news;
- Yahoo news is event_type=news, never economic;
- provider symbol remains separate from canonical symbol;
- Yahoo remains a news source even when LSE and ForexFactory supply economic events.

Concrete adapters:

    LSECalendarProvider
    ForexFactoryCalendarProvider
    YahooFinanceNewsProvider

All three adapters implement the same CalendarProvider contract. Provider transport,
pagination, provider-specific parsing and provider-specific field names stay inside
the adapter. The Calendar engine consumes only normalized provider events.

Provider acquisition is independent: failure or absence from one provider must not
prevent successful events from another provider from being persisted. Aggregate status
is PARTIAL when at least one applicable provider fails while another succeeds.

Forced-refresh performance contract:
- base event acquisition for all applicable providers runs concurrently, with a bounded worker count equal to the applicable provider count (maximum three);
- result normalization, symbol/interval filtering, ForexFactory Detail enrichment, merge, and atomic persistence remain deterministic after acquisition;
- `--debug` reports elapsed time for each provider's base fetch to stderr, without changing the JSON response contract;
- concurrent acquisition must preserve provider-specific error isolation and the existing PARTIAL/coverage/watermark rules.

Provider enrichment/merge:
- provider records are first normalized;
- the engine attempts to identify records representing the same real-world event;
- matching records are merged into one canonical event record;
- fields missing from the existing canonical event may be filled by another provider;
- non-conflicting provider details are added rather than discarded;
- provider provenance is retained so it is possible to see which sources contributed;
- provider-specific source metadata is retained when available. A provider-specific URL may be
retained for providers that explicitly expose one, such as Yahoo Finance news; ForexFactory
Event Detail is represented by its provider Detail specification payload under details.specs.
- conflicting values are not silently overwritten solely because one provider was queried later;
  the canonical merge keeps the existing value and records the additional provider value in
  provider-specific metadata when the schema supports it;
- provider identity must never be used as the sole canonical identity because the same event
  can have different provider IDs.

No provider is a mandatory fallback. ForexFactory is therefore an alternative economic-calendar
source as well as an independent confirmation/enrichment source. Yahoo remains the independent
news source for stock/ticker news.

No --forex, --ticker, or --provider flags exist.

## 1.1 Provider API credential storage

Calendar providers that require API credentials use the same provider-independent local credential mechanism as Market Data.

Credential files live under the repository-root:

    PROVIDERS/
        credentials.py
        <provider>.apikey

Rules:
- each provider has its own credential file;
- each file contains only that provider's API key;
- `PROVIDERS/*.apikey` is Git-ignored and must never be committed;
- the shared credential loader is responsible for file reading and optional environment-variable override;
- Calendar provider adapters do not parse credential files themselves;
- missing, empty, whitespace-only, or multi-line credentials fail closed;
- credentials must never enter `calendar.json`, provider event records, stdout, stderr diagnostics, logs, tests, or CI artifacts;
- providers that do not require an API key simply do not request one;
- adding a future provider requires only its provider identifier and credential filename; the storage architecture remains unchanged.

The shared loader is intentionally independent of the Calendar/Market Data provider implementations. An explicitly supplied provider environment variable remains a supported deployment/CI override, while the provider-local file is the canonical local source.
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

## 2.1 Debug contract

`--debug` is an optional CLI diagnostic flag.

- Provider acquisition failures are not exposed as provider error records or exception
  text in normal machine-readable/human-readable query output. Aggregate status may still
  be `PARTIAL` or `UNAVAILABLE` so the caller can detect incomplete acquisition.
- Without `--debug`, provider acquisition diagnostics are silent; detailed exception
  diagnostics and tracebacks are not printed.
- With `--debug`, diagnostic exception information and tracebacks may be printed to
  stderr only, including provider-level `try/except` diagnostics and unexpected
  exceptions that reach the CLI boundary.
- Refresh also reports the active `calendar.json` path so a refresh run can be verified against the
  exact persistent file being compared.
- `--debug` never changes the machine-readable stdout contract, event data, coverage,
  watermark semantics, or provider routing.
- `--debug` is presentation/diagnostic state only and never enters canonical data.

## 3. Canonical CLI

When `python calendar.py` is invoked without arguments, it prints the help text and exits with status 0. This operation performs no cache or provider I/O.

The public query grammar is positional:

```text
python calendar.py SYMBOL <scope> [refresh]
python calendar.py SYMBOL --last-update
python calendar.py delete
python calendar.py delete SYMBOL <scope>
python calendar.py --help
```

The public date/time grammar is shared with Market Data and implemented in `COMMON/date_time.py` by `DateTimeScopeParser`. Date and time are separated by a space, not `@`. No `--date`, `--time`, or `--range` flags are accepted; the temporal scope is positional.

Supported temporal scopes:

| Scope | Meaning |
|---|---|
| `YYYY.MM.DD` | Entire UTC calendar day |
| `YYYY.MM.DD HH:MM` | Exact one-minute interval |
| `YYYY.MM.DD-YYYY.MM.DD` | Inclusive date range; end resolves to the following UTC midnight |
| `YYYY.MM.DD HH:MM-YYYY.MM.DD HH:MM` | Half-open datetime range `[start, end)` |
| `HH:MM` | Exact minute on the current UTC calendar day |
| `HH:MM-HH:MM` | Half-open time range on the current UTC calendar day; end must be later than start |
| `YYYY.MM.DD-` | From that date's UTC midnight through the current UTC time |
| `YYYY.MM.DD HH:MM-` | From that exact UTC minute through the current UTC time |
| `HH:MM-` | From that time today through the current UTC time |
| `-YYYY.MM.DD` | From the latest recorded visible event for SYMBOL through the end of the selected UTC date |
| `-YYYY.MM.DD HH:MM` | From the latest recorded visible event for SYMBOL through the selected minute |
| `-HH:MM` | From the latest recorded visible event for SYMBOL through the selected minute today |

An open-start scope requires retained visible Calendar event history for SYMBOL. Its start is resolved at execution time from the latest visible event timestamp in the committed `calendar.json`; it is not guessed from the machine clock. A date endpoint includes the full UTC date, while a datetime/time endpoint includes its entire minute. Plain open-start scopes are cache-only; adding trailing `refresh` requests provider acquisition over the resolved interval.

An open-end scope resolves its end to the current UTC time at execution. A future start, reversed range, invalid date, or invalid time is rejected. Time-only scopes use the UTC date captured at parsing time. The parser receives an injectable reference time so these rules can be tested deterministically.

The Calendar retains these non-date query scopes:

```text
current
current day
current week
current month
today
tomorrow
yesterday
next
next day
next week
next month
prev
prev day
prev week
prev month
latest
news
```

`current` is an active-event cache query. Trailing `refresh` is valid for temporal scopes and for `current`, but not for `latest`, `next`, `prev`, or `news`. `refresh` is a trailing modifier, never an independent command.

Delete forms:

```text
python calendar.py delete
python calendar.py delete SYMBOL <scope>
```

Bare delete is the explicit full-cache reset. Scoped delete uses the same temporal grammar as query and is always symbol-scoped. Relative event queries such as `current`, `next`, `prev`, `latest`, and `news` are not delete scopes. `today`, `tomorrow`, and `yesterday` remain valid exact-day delete scopes.

`--last-update` is a read-only operation that returns the latest successful provider acquisition timestamp for each applicable provider. It does not call providers or alter coverage, watermarks, or `calendar.json`.

## 3.1 Shared date/time implementation

`COMMON/date_time.py` is the provider-independent owner of date/time parsing, scope classification, UTC normalization, and ISO 8601 parsing/formatting helpers. Calendar may add domain-specific validation and resolves open-start scopes from visible stored events; it must not implement a separate date/time grammar.

## 3.2 Relative day semantics

- `today` is the current UTC calendar day.
- `tomorrow` is the next UTC calendar day.
- `yesterday` is the previous UTC calendar day.

These aliases are resolved at execution time using the same injectable UTC clock. They do not mean `current`, `latest`, or `next`.

## 3.3 Last-update lookup

The read-only `SYMBOL --last-update` operation returns `last_successful_at` for every applicable provider+canonical-symbol watermark. If no applicable provider has a successful watermark, status is `NO_LAST_UPDATE`. Missing individual provider watermarks are represented as null / N/A, never as fabricated timestamps.

Implementation version is 2.6.7; persistent schema remains V2.

## 4. current semantics

`current` is a read-only active-event lookup over the committed `calendar.json` snapshot.

An event is considered active from its canonical `timestamp` through the end of that UTC minute because
the canonical event contract contains a point timestamp and no provider-independent duration field.
`current` returns all visible events satisfying:

    timestamp <= current UTC time < timestamp + 1 minute

`current` MUST NOT contact providers. It MUST NOT modify coverage, watermarks, or `calendar.json`.

If no visible event is active, the public status is `NO_CURRENT_EVENT`.

## 4.1 latest semantics

`latest` is a read-only most-recent-event lookup over the committed `calendar.json` snapshot.
It keeps only visible events with `timestamp <= current UTC time` and returns exactly the most recent
event, or `NO_LATEST_EVENT`.

## 4.2 next and prev semantics

`next` and `prev` are read-only event-relative lookups over the committed snapshot.

- `next` returns exactly the nearest future scheduled economic event;
- `prev` returns exactly the nearest past scheduled economic event;
- both consider only events represented by ForexFactory as scheduled economic events;
- Yahoo Finance published/current news is not a scheduled future-event source;
- neither operation contacts providers or changes persistent state.

## 4.3 Refresh modifier semantics

`refresh` is a trailing query modifier, not an independent CLI command.

Public forms:

    python calendar.py SYMBOL current refresh
    python calendar.py SYMBOL current day refresh
    python calendar.py SYMBOL current week refresh
    python calendar.py SYMBOL current month refresh
    python calendar.py SYMBOL today refresh
    python calendar.py SYMBOL tomorrow refresh
    python calendar.py SYMBOL yesterday refresh
    python calendar.py SYMBOL YYYY.MM.DD refresh
    python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD refresh
    python calendar.py SYMBOL YYYY.MM.DD HH:MM refresh
    python calendar.py SYMBOL YYYY.MM.DD HH:MM-YYYY.MM.DD HH:MM refresh
    python calendar.py SYMBOL YYYY.MM.DD refresh
    python calendar.py SYMBOL YYYY.MM.DD HH:MM refresh
    python calendar.py SYMBOL HH:MM refresh

The former `refresh SYMBOL SCOPE` command grammar is removed.
`current refresh` is valid and is the only refresh form permitted among `current`, `latest`, `next`, `prev`, and `news`. `latest refresh`, `next refresh`, `prev refresh`, and `news refresh` are invalid.

Refresh behavior:

1. resolve the query scope to its UTC interval;
2. determine the same applicable providers as normal acquisition;
3. force provider acquisition even when the requested interval is already covered;
4. for ForexFactory, use a one-day provider-side envelope around the requested interval so mutable events near
   a scope boundary can still be matched by stable provider event ID;
6. select fresh events whose new timestamp falls inside the logical interval or whose stable provider event ID
   matches an existing event visible for the symbol in the provider-side envelope. The envelope is required so
   late mutable Detail data for an event just before the incremental boundary can still be refreshed by identity;
7. compare fresh records with existing records by stable `event_id`;
8. replace changed records and add newly discovered records, including late ForexFactory Detail changes. Overlap-boundary records may be merged into the cache even when they are outside the logical query interval;
9. provider identity remains authoritative even if a refreshed event changes its timestamp;
10. an existing event absent from the fresh provider response is not deleted;
11. preserve existing coverage and watermarks. Refresh does not establish coverage and does not advance
    `last_successful_at`;
12. validate and atomically persist when refreshed records produce additions or changes;
13. after refresh, the refresh operation is the authoritative source of the public `events` result. Return events whose
    refreshed timestamp is inside the logical query scope, plus records whose stable ID belonged to an event already visible
    in the logical scope before refresh (this preserves rescheduled-event results). Records refreshed only because they fall
    within the provider-side overlap and were outside the logical scope before refresh are merged into the cache but are not
    returned. The CLI MUST NOT reapply committed coverage or watermark filters to the refresh result, because refresh is
    allowed to return first-use acquisitions and rescheduled records that are not representable by a normal cache query.
    Machine-readable output includes the `added`/`changed`/`unchanged` refresh summary. In `--cleartext` mode the normal
    event output is followed by one refresh summary line.

A refresh performed by the Monitor MUST run outside the candle-close processing path and MUST NOT block candle
processing on provider/network I/O. The CLI may remain synchronous because the user explicitly requested the
refresh operation.

Yahoo Finance refresh follows the same compare-and-replace model over the provider's currently exposed rolling
feed. Yahoo news represents already published/current news, not scheduled future events. Historical completeness
remains subject to the Yahoo rolling-feed limitation.

### Refresh provider/status contract

The trailing `refresh` modifier uses the same isolated-provider acquisition semantics
as normal Calendar acquisition.

The refresh result exposes:
- provider-level acquisition results in the `providers` collection;
- `events` containing the normal query result for the requested scope after the
  refresh merge;
- `refresh.added`, `refresh.changed`, and `refresh.unchanged` counts.

Provider failure semantics remain fail-closed:
- all applicable providers fail -> aggregate status `UNAVAILABLE`;
- a mixture of successful and failed providers -> aggregate status `PARTIAL`;
- `SKIPPED_NO_FOREX_PAIR` remains distinguishable and is never treated as a
  successful empty acquisition;
- Detail-partial ForexFactory acquisition remains `PARTIAL`;
- ForexFactory rows without concrete time remain visible as an unresolved-event count and keep provider status `PARTIAL`; explicit acquisition records `PARTIAL` coverage, while forced refresh preserves existing coverage; these rows never become fabricated midnight events and do not advance the watermark;
- provider diagnostics remain subject to the normal `--debug` stderr contract.

The modifier does not introduce a separate `REFRESHED`, `UNCHANGED`, or
`BOOTSTRAP_REQUIRED` query status. Change detection is represented by the
refresh summary.
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

Yahoo explicit acquisition creates provider/symbol coverage for the portion of the requested interval
that is at or before acquisition time and actually queried successfully. This coverage means the Calendar
completed the requested provider operation; it does not guarantee that Yahoo's rolling feed was historically
complete. The provider result must therefore retain `historical_coverage=NOT_GUARANTEED` while the persisted
coverage record may be `COMPLETE` for the successfully completed acquisition interval.

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
    sources
    timestamp
    title
    details
    suppressed_for (optional symbol-scope visibility metadata)

source is the canonical primary source for the normalized event identity. sources is the
ordered list of provider names that contributed to the merged event. The list is unique and
deterministic.

Allowed source values:

    lse
    forexfactory
    yahoo_finance

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
    specs

`specs` is an ordered, possibly-empty list of:

    order
    title
    html

The `html` value is the provider's Detail specification content and may contain links.
The `title` value is also provider-controlled text and may contain HTML markup; cleartext presentation
must sanitize the title and HTML content through the same HTML-aware rendering path.

LSE details may include:

    currency
    impact
    actual
    forecast
    previous
    provider_event_id
    url
    provider_fields

Yahoo details may include:

    publisher
    url
    provider_symbol
    summary

Provider-specific fields not mapped to canonical fields may be retained under provider_fields.
No provider severity or economic value is invented.

## 7.1 ForexFactory HTML fallback

The Calendar must not fail solely because the legacy embedded days JSON payload is absent from the
ForexFactory HTML response.

The acquisition path first attempts the structured days payload. When it is absent, it parses the
current rendered calendar rows using the provider event identifier, visible date/time, currency,
impact, title, actual, forecast, and previous fields.

For the structured payload, explicit ForexFactory impactTitle, impactName (compatibility alias),
and/or impactClass representations are normalized to the canonical HIGH/MEDIUM/LOW/HOLIDAY values.
Known impactTitle forms include High Impact Expected, Med Impact Expected, Medium Impact Expected,
Low Impact Expected, and Non-Economic. Known impactClass forms include provider color/icon tokens
such as impact-red, icon--ff-impact-red, impact-orange, icon--ff-impact-ora, impact-yellow,
icon--ff-impact-yel, impact-green, icon--ff-impact-grn, impact-grey, and the corresponding grey/gray
variants. Known provider severity must not silently collapse to UNKNOWN. Severity must never be
inferred from an event title or other unrelated field.

Rendered event times are interpreted using the provider-declared Calendar Time Zone. An IANA timezone
is preferred. When the runtime has no matching IANA timezone database entry, the provider-declared
GMT offset is used as a fallback.

The rendered-row parser identifies an event row by the provider event-instance ID first. Current
ForexFactory CSS row classes are advisory only; they are not a required condition for event parsing.
The fallback produces the same canonical normalized event contract and does not alter provider routing,
coverage, watermark, or atomic persistence semantics.

Provider-query construction is deterministic from the requested interval. The requested interval is
still filtered against canonical UTC event timestamps after acquisition, so provider query inclusivity
cannot widen the persisted/result interval.

ForexFactory event Detail is not persisted as a synthetic or derived event URL. Calendar
fetches the provider Detail JSON response identified by the provider event ID and stores its specification
records under `details.specs`. Provider HTML inside each specification is preserved verbatim so embedded
Source, Next Release, and other provider links remain available without inventing a canonical event URL.
For each acquired ForexFactory event, Calendar fetches the provider Detail JSON response identified by
the provider event ID. Detail requests use bounded parallelism (maximum six concurrent requests) to avoid
serial N-request latency while preserving the normalized event order in the persisted result. Its ordered
`specs` collection is stored under `details.specs`, with provider HTML preserved so Source and Next
Release links and future Detail fields are retained.

A complete coverage interval is not considered Detail-enriched when an existing ForexFactory event
inside the requested interval has no `details.specs`. Such an interval is reacquired so the existing
provider facts can be enriched with Detail specifications. This is an enrichment rule within schema
version 2, not a schema migration.

## 7.2 Human-readable CLI presentation

`--cleartext` is presentation-only and must not modify the canonical event data or persistent schema.

The `Details` section in cleartext output must render the normalized `details` object as individual human-readable fields, not as a serialized JSON dictionary. ForexFactory core details are presented in this order when present:

    Currency
    Impact
    Actual
    Forecast
    Previous

ForexFactory `specs` follow the core fields in provider order. Each specification renders as
`<Title>: <text content>` after applying HTML-aware cleartext sanitization to both the provider
`title` and `html` fields. For the `title`, provider markup is removed and any resulting line
boundaries are normalized to spaces so the title remains a single-line field label. For the `html`
content, `<br>` becomes a readable line break. HTML character references are decoded to a stable value
before parsing, including markup escaped more than once such as `&amp;lt;br&amp;gt;` or
`&amp;lt;img ...&amp;gt;`. Raw provider markup or escaped markup must never leak from either field into
`--cleartext` output. The canonical `calendar.json` retains the original provider HTML so links and
formatting information are not lost.
A null detail value is displayed as `N/A`. Additional non-spec detail fields are rendered afterward in
deterministic key order. Each cleartext event block ends after `Event ID`; there is no closing separator
line, and adjacent event blocks are separated by one blank line. The default machine-readable JSON output
remains unchanged.

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

## 10.1 ForexFactory Detail failure and retry contract

ForexFactory base-event acquisition is considered provider-successful only when the acquired interval
also has successful Detail enrichment for every acquired event whose Detail was requested.

If one or more Detail requests fail after the base calendar rows were acquired:

- base events remain persisted;
- the affected event may retain an empty `details.specs` list for that attempt;
- the provider result is `PARTIAL` and reports the number of Detail failures;
- the affected coverage interval is `PARTIAL`, never `COMPLETE`;
- the ForexFactory watermark is not advanced;
- subsequent explicit acquisition treats that interval as uncovered and retries it;
- `current` retains the previous successful watermark and therefore retries the incomplete window;
- a later acquisition that completes all Detail requests may promote the interval to `COMPLETE` and advance
  the watermark.

Coverage state, not the presence or absence of `details.specs`, is the authoritative retry indicator.
A legitimately empty Detail response is not itself a failure.

## 10.2 Successful no-match provider result semantics

A provider may successfully complete an acquisition and return zero matching events for the requested canonical symbol and interval. This is a valid empty result, not a partial provider failure.

For this state:
- provider status is `NO_MATCH`;
- no provider failure is recorded;
- normal successful acquisition state may be persisted, including the provider watermark where the acquisition semantics permit it;
- the aggregate query status is `NO_RELEVANT_EVENT` when all applicable providers return `NO_MATCH`;
- `NO_MATCH` must not be converted to `PARTIAL` merely because the provider has no matching events;
- `PARTIAL` remains reserved for an acquisition that completed with incomplete provider coverage or another explicitly partial provider result.

For Yahoo Finance specifically, an empty successful news collection is `NO_MATCH`. A verified Yahoo Forex-pair unavailability remains the separate `SKIPPED_NO_FOREX_PAIR` state.

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
- invoking `python calendar.py` with no arguments prints the CLI help and exits successfully without provider or cache I/O;
- old relative scopes removed;
- `latest` returns the most recent past/current visible event from the committed snapshot without provider calls;
- `next` returns the nearest future visible event from the committed snapshot without provider calls;
- current is watermark-based and remains cache-only;
- a missing current-mode watermark contributes no events to plain `current`;
- provider acquisition for current-mode refresh is explicit through the trailing `refresh` modifier;
- `-YYYY.MM.DD` and `-YYYY.MM.DD HH:MM` resolve their start from the latest recorded visible Calendar event and preserve the explicit END boundary;
- `next` considers only scheduled ForexFactory economic events; Yahoo published/current news is not a future-event source;
- normal public query output never exposes provider `ERROR` records or provider exception text;
- plain open-start scopes are cache-only; trailing `refresh` performs provider acquisition over that resolved interval;
- EURUSD date, date range, datetime, and datetime range parse correctly;
- NVDA routes to Yahoo;
- HUF routes to ForexFactory;
- USDJPY has independent ForexFactory and Yahoo watermarks;
- Yahoo events are news;
- Yahoo FX news is persisted only after exact provider-side Forex instrument verification;
- ForexFactory events are economic;
- provider failures remain observable through aggregate PARTIAL/UNAVAILABLE status and debug diagnostics, while normal stdout omits provider ERROR records and exception text;
- bare `python calendar.py delete` can reset an incompatible legacy schema cache;
- the CLI help exposes the Calendar software version and persistent schema version;
- the source implementation documents function responsibilities and variable roles with comments;
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
  `suppressed_for` marker;
- single-day ForexFactory acquisition uses the native `day=` query form;
- multi-day ForexFactory acquisition uses the native `range=` query form;
- rendered ForexFactory helper rows without an event title do not fail the provider acquisition path;
- structured and rendered ForexFactory impact representations normalize known HIGH/MEDIUM/LOW/HOLIDAY values without silent UNKNOWN collapse;
- rendered ForexFactory impact classification must not silently collapse known HIGH/MEDIUM/LOW events to UNKNOWN;
- relative ForexFactory navigation aliases are documented but are not accepted as public Calendar CLI scopes;
- `latest` is read-only and returns `NO_LATEST_EVENT` when the committed snapshot contains no visible event at or before current UTC time;
- ForexFactory normalized events include `details.specs` from the provider Detail JSON payload; no event URL is synthesized from the provider event ID;
- malformed or unavailable ForexFactory Detail JSON is surfaced as a provider failure and never silently converted into fabricated Detail content;
- `--cleartext` renders normalized event details as human-readable fields rather than a raw JSON dictionary, without changing canonical data or machine-readable output.

## 14. Source layout and portability

The repository-root `calendar.py` remains the stable CLI entrypoint. Internal Calendar modules are grouped under `CALENDAR/` by responsibility, and the default persistent cache is `CALENDAR/calendar.json`. `SMC_DATA_ROOT` remains an explicit override.

Calendar persistence uses `COMMON/atomic_file.py` for same-directory atomic UTF-8 replacement, while retaining Calendar-specific JSON validation, locking, and `DataIntegrityError` translation. Provider HTTP transport uses `COMMON/http_client.py`; all Calendar provider URL construction, headers, event parsing, and `ProviderError` mapping remain in the Calendar layer.

The domain layer keeps event, interval, coverage, watermark, merge, filtering, and refresh decisions represented by explicit fields and simple scalar values so the semantic core remains straightforward to port to MQL4/MQL5. Python-only provider HTTP, HTML parsing, threading, and OS-specific locking are confined to infrastructure modules.

## 14.1 Rendered ForexFactory time handling

The rendered HTML fallback requires a concrete provider clock. Missing, `Tentative`, or `All Day` time text is not converted to `00:00` or another synthetic timestamp. A strict direct parser call rejects such a row. During provider acquisition, the caller collects its event ID as unresolved and skips only that row; the provider result becomes `PARTIAL`, and the watermark does not advance. Explicit acquisition records `PARTIAL` coverage so the interval can be retried. Forced refresh does not alter prior coverage. Other timestampable events in the same response remain usable and partial data is persisted. Invalid hour/minute values are still rejected explicitly.

## 14.2 Source activity documentation

Calendar Python source must document the activity of its functions and meaningful state variables without changing runtime behavior. Function docstrings/comments must identify the function's role in the Calendar flow, including whether it is a public operation or an internal helper. Important module-level state variables must have concise comments describing what they represent and how they are used. Local variables should be documented through nearby comments when their role is non-obvious or when they carry acquisition, persistence, coverage, watermark, provider-result, or presentation state. Trivial loop/index variables do not require comments. Documentation must remain synchronized with the implementation and must not introduce generated noise or duplicate the specification.

## 14.3 Source attribution

Calendar Python source files must retain the following attribution header:
`# (c) Istvan Jakab <istvanhlc230@gmail.com>`

The attribution is informational source ownership/authorship metadata and must not affect runtime behavior.
