# Calendar Module Specification

Status: Current V2 specification.

Calendar implementation baseline: 2.4.12.

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

ForexFactory:
- primary source for economic events;
- the implementation uses ForexFactory's native calendar query grammar;
- a single concrete calendar day uses `day=<monD.YYYY>` (for example `day=apr3.2026`);
- a multi-day interval uses `range=<monD.YYYY>-<monD.YYYY>` (for example `range=apr3.2026-apr10.2026`);
- the web UI also exposes relative/navigation forms `day=today`, `day=tomorrow`, `day=yesterday`, `week=this`, `week=next`, `week=last`, `month=this`, `month=next`, and `month=last`; these are provider-native navigation forms and are not part of the Calendar CLI grammar;
- the range-filtered ForexFactory calendar HTML is the current provider representation; the legacy embedded structured days payload is still accepted when present;
- normalized fields include id, dateline, currency, name, impactName/impactClass, actual, forecast, previous;
- the event's calendar-page `Detail` content is acquired separately as provider JSON and normalized under `details.specs`;
- `details.specs` is an ordered list of `{order, title, html}` records; provider HTML is preserved so linked Source/Next Release references are not discarded;
- the calendar-page Detail navigation is not a canonical event URL; no Detail URL is stored or synthesized;
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

Public query forms:

    python calendar.py SYMBOL YYYY.MM.DD [refresh]
    python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD [refresh]
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM [refresh]
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM [refresh]
    python calendar.py SYMBOL --time HH:MM [refresh]
    python calendar.py SYMBOL --range -YYYY.MM.DD [refresh]
    python calendar.py SYMBOL --range -YYYY.MM.DD@HH:MM [refresh]
    python calendar.py SYMBOL YYYY.MM.DD --time HH:MM [refresh]
    python calendar.py SYMBOL current [refresh]
    python calendar.py SYMBOL today [refresh]
    python calendar.py SYMBOL tomorrow [refresh]
    python calendar.py SYMBOL yesterday [refresh]
    python calendar.py SYMBOL prev_week [refresh]
    python calendar.py SYMBOL next_week [refresh]
    python calendar.py SYMBOL prev_month [refresh]
    python calendar.py SYMBOL next_month [refresh]
    python calendar.py SYMBOL latest
    python calendar.py SYMBOL next

Delete forms:

    python calendar.py delete
    python calendar.py delete SYMBOL YYYY.MM.DD
    python calendar.py delete SYMBOL YYYY.MM.DD-YYYY.MM.DD
    python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM
    python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
    python calendar.py delete SYMBOL today
    python calendar.py delete SYMBOL tomorrow
    python calendar.py delete SYMBOL yesterday
    python calendar.py delete SYMBOL prev_week
    python calendar.py delete SYMBOL next_week
    python calendar.py delete SYMBOL prev_month
    python calendar.py delete SYMBOL next_month
    python calendar.py delete SYMBOL --time HH:MM
    python calendar.py delete SYMBOL YYYY.MM.DD --time HH:MM

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
- next_day
- week
- month
Date syntax is YYYY.MM.DD. Time syntax is HH:MM. @ separates date/time. - separates interval endpoints. No .. syntax exists.

--time HH:MM is a CLI shorthand for an exact one-minute datetime query on the current UTC calendar day. With no explicit date scope, Calendar resolves it as <current UTC date>@HH:MM. With a date-only scope, SYMBOL YYYY.MM.DD --time HH:MM resolves to YYYY.MM.DD@HH:MM. --time must not be combined with an existing @HH:MM point or a date/range scope that already contains time. The shorthand is normalized to the canonical YYYY.MM.DD@HH:MM scope before domain parsing, so the underlying query/refresh/delete interval semantics remain unchanged. The current UTC date is obtained from the same Calendar utc_now() clock used by the domain layer; no local-machine date is assumed.

Date = full UTC day.
Date range = inclusive by calendar date.
Datetime = exact one-minute interval.
Datetime range = half-open start/end interval.

Preferred positional time-range shorthand:

    python calendar.py SYMBOL HH:MM-HH:MM [refresh]

This is the preferred public shorthand when the requested interval is entirely on the current UTC calendar day. It resolves both times against the current UTC calendar date at execution time and normalizes to the canonical `YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM` datetime range before scope parsing. It is valid for normal query, trailing `refresh`, and symbol-scoped delete operations. It is mutually exclusive with `--date`, `--time`, `--range`, or another positional scope. The end time must be later than the start time; invalid clock values fail through the existing Calendar time parser.

## 3.1 --time CLI shorthand

The public Calendar CLI also accepts a time-only shorthand:

    python calendar.py SYMBOL --time HH:MM
    python calendar.py SYMBOL YYYY.MM.DD --time HH:MM

The first form targets the current UTC calendar day. The second form targets the supplied date. Both forms are converted to the canonical datetime scope before parse_scope()/resolve_scope_interval() processing.

The shorthand is CLI syntax only; the canonical internal scope remains YYYY.MM.DD@HH:MM. The same shorthand accepts the trailing refresh modifier and symbol-scoped delete operations. Bare delete cannot be combined with --time.

Open-start `--range`:
    python calendar.py SYMBOL --range -YYYY.MM.DD [refresh]
    python calendar.py SYMBOL --range -YYYY.MM.DD@HH:MM [refresh]

A leading `-` omits the start boundary. Calendar resolves that start at execution time from the latest
recorded visible event timestamp for SYMBOL in the committed `calendar.json` snapshot. The explicit END
remains the upper boundary: a date END resolves to the next UTC midnight, and a datetime END resolves to
the end of that exact UTC minute. An open-start range requires retained visible event history for SYMBOL;
otherwise the request fails explicitly. Plain open-start range is cache-only. Adding trailing `refresh`
forces provider acquisition over the same resolved interval.

The canonical time spelling is `HH:MM`. For compatibility with the approved CLI example, the open-start
datetime form also accepts `HH.MM` and normalizes it to `HH:MM`.


--time is mutually exclusive with an explicit datetime, datetime range, date range, current, latest, or next scope. Invalid HH:MM values fail through the existing Calendar time parser.

## 3.2 Relative day scopes

The public CLI accepts three relative UTC calendar-day scopes:

    python calendar.py SYMBOL today
    python calendar.py SYMBOL tomorrow
    python calendar.py SYMBOL yesterday

Semantics:

- today = the current UTC calendar day, from 00:00:00 to the next UTC midnight;
- tomorrow = the next UTC calendar day;
- yesterday = the previous UTC calendar day.

These scopes are resolved at execution time using the same utc_now() clock as
the Calendar domain. They are dynamically resolved exact-day aliases, not
persistent state and not provider-native ForexFactory navigation parameters.

They use the normal exact-day query/acquisition interval semantics and are also
valid with the trailing refresh modifier and for symbol-scoped delete. They do not mean current,
latest, or next.

## 3.3 Open-start --range

`--range -END` is a query/refresh shorthand for a range whose start is resolved from the latest recorded
visible Calendar event for SYMBOL.

Semantics:
- `--range -YYYY.MM.DD` ends at the next UTC midnight after the specified date;
- `--range -YYYY.MM.DD@HH:MM` ends at the end of the specified UTC minute;
- the start is the timestamp of the latest visible persisted event for SYMBOL;
- without retained visible event history, the request fails explicitly;
- plain open-start range is cache-only and does not contact providers;
- open-start range with trailing `refresh` forces provider acquisition over the resolved interval;
- the resolved interval is the same logical query interval used for refresh matching and result presentation;
- the range does not create or alter coverage/watermarks merely by parsing or querying.

## 3.4 Relative week and month scopes

The public CLI accepts four relative UTC calendar scopes:

    python calendar.py SYMBOL prev_week
    python calendar.py SYMBOL next_week
    python calendar.py SYMBOL prev_month
    python calendar.py SYMBOL next_month

Semantics:

- prev_week = the immediately preceding ForexFactory-style calendar week;
- next_week = the immediately following ForexFactory-style calendar week;
- the relative week starts Sunday at 00:00:00 UTC and ends at the following Sunday 00:00:00 UTC;
- prev_month = the complete UTC calendar month immediately before the current month;
- next_month = the complete UTC calendar month immediately after the current month.

These scopes are resolved at execution time using the same utc_now() clock as the
Calendar domain. They are aliases only; they do not persist relative-state and do not
mean current, latest, or next.

They use the normal exact interval query/acquisition semantics and are valid with the
trailing refresh modifier and for symbol-scoped delete.

## 4. current semantics

`current` is a read-only incremental query over the committed `calendar.json` snapshot.

For each applicable provider:

    load provider|canonical_symbol watermark
              |
              +-- missing -> no incremental events for that provider
              |
              +-- present -> return cached events newer than the watermark
                              and no later than now

`current` MUST NOT contact ForexFactory or Yahoo Finance. It MUST NOT modify
coverage, watermarks, or `calendar.json`. This makes `current` safe to call from
the Monitor's time-sensitive processing loop.

The watermark is only the local incremental-result boundary. It is not a provider
refresh trigger. Late provider Detail data is obtained only when a `refresh`
modifier is explicitly requested, either by the CLI or by the Monitor's background
Calendar refresh operation.

A provider with no committed watermark has no local incremental boundary and
therefore contributes no events to a plain `current` query. No synthetic
bootstrap timestamp is created.

`current` never means:
- current-minute event lookup;
- next event;
- latest event;
- nearest event.

## 4.1 latest semantics

`latest` is a read-only most-recent-event lookup over the committed `calendar.json` snapshot.

For `python calendar.py SYMBOL latest`:

1. load and validate the committed Calendar document under the Calendar lock;
2. filter events according to the normal SYMBOL visibility rules, including `suppressed_for`;
3. keep only events with `timestamp <= current UTC time`;
4. sort by timestamp descending, then source and event identity for deterministic ordering;
5. return exactly the first event, or `NO_LATEST_EVENT` when none exists.

`latest` does not call ForexFactory or Yahoo Finance, does not acquire data, and does not modify coverage, watermarks, or `calendar.json`.

`latest` is distinct from `current`: both are read-only cache queries, but `current` applies provider-specific incremental watermark boundaries while `latest` selects the most recent past/current event.

## 4.2 next semantics

`next` is a read-only nearest-future-event lookup over the committed `calendar.json` snapshot.

For `python calendar.py SYMBOL next`:

1. load and validate the committed Calendar document under the Calendar lock;
2. filter events according to the normal SYMBOL visibility rules, including `suppressed_for`;
3. keep only events with `timestamp > current UTC time`;
4. sort by timestamp, then source and event identity for deterministic ordering;
5. return exactly the first event, or `NO_NEXT_EVENT` when none exists.

`next` does not call ForexFactory or Yahoo Finance, does not acquire data, and does not modify coverage, watermarks, or `calendar.json`.

`next` is distinct from `current`: both are read-only cache queries, but `next` selects the nearest future event while `current` applies provider-specific incremental watermark boundaries.

No synthetic bootstrap timestamp is permitted.

Explicit date or datetime-range acquisition establishes bootstrap state.

## 4.3 Refresh modifier semantics

`refresh` is a trailing query modifier, not an independent CLI command.

Public forms:

    python calendar.py SYMBOL current refresh
    python calendar.py SYMBOL today refresh
    python calendar.py SYMBOL tomorrow refresh
    python calendar.py SYMBOL yesterday refresh
    python calendar.py SYMBOL prev_week refresh
    python calendar.py SYMBOL next_week refresh
    python calendar.py SYMBOL prev_month refresh
    python calendar.py SYMBOL next_month refresh
    python calendar.py SYMBOL YYYY.MM.DD refresh
    python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD refresh
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM refresh
    python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM refresh
    python calendar.py SYMBOL --date YYYY.MM.DD refresh
    python calendar.py SYMBOL --date YYYY.MM.DD --time HH:MM refresh
    python calendar.py SYMBOL --time HH:MM refresh

The former `refresh SYMBOL SCOPE` command grammar is removed.
`latest refresh` and `next refresh` are invalid.

Refresh behavior:

1. resolve the query scope to its UTC interval;
2. determine the same applicable providers as normal acquisition;
3. force provider acquisition even when the requested interval is already covered;
4. for ForexFactory, use a one-day provider-side envelope around the requested interval so mutable events near
   a scope boundary can still be matched by stable provider event ID;
5. for `current refresh`, derive the logical refresh interval from the earliest applicable committed
   `last_successful_at` through current UTC time. If no applicable watermark exists, use a bounded one-day
   interval ending at now;
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
    specs

`specs` is an ordered, possibly-empty list of:

    order
    title
    html

The `html` value is the provider's Detail specification content and may contain links.
The `title` value is also provider-controlled text and may contain HTML markup; cleartext presentation
must sanitize the title and HTML content through the same HTML-aware rendering path.

Yahoo details may include:

    publisher
    url
    provider_symbol
    summary

No Yahoo impact is invented.

## 7.5 ForexFactory HTML fallback

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

The calendar-page Detail control is presentation/navigation UI, not a canonical event URL field. For
each acquired ForexFactory event, Calendar fetches the provider Detail JSON response identified by
the provider event ID. Detail requests use bounded parallelism (maximum six concurrent requests) to avoid
serial N-request latency while preserving the normalized event order in the persisted result. Its ordered
`specs` collection is stored under `details.specs`, with provider HTML preserved so Source and Next
Release links and future Detail fields are retained. No Detail URL is extracted, persisted, or synthesized.

A complete coverage interval is not considered Detail-enriched when an existing ForexFactory event
inside the requested interval has no `details.specs`. Such an interval is reacquired so the existing
provider facts can be enriched with Detail specifications. This is an enrichment rule within schema
version 2, not a schema migration.

## 7.6 Human-readable CLI presentation

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
- `latest` returns the most recent past/current visible event from the committed snapshot without provider calls;
- `next` returns the nearest future visible event from the committed snapshot without provider calls;
- current is watermark-based and remains cache-only;
- a missing current-mode watermark contributes no events to plain `current`;
- provider acquisition for current-mode refresh is explicit through the trailing `refresh` modifier;
- `--range -YYYY.MM.DD` and `--range -YYYY.MM.DD@HH:MM` resolve their start from the latest recorded visible Calendar event and preserve the explicit END boundary;
- `next` considers only scheduled ForexFactory economic events; Yahoo published/current news is not a future-event source;
- normal public query output never exposes provider `ERROR` records or provider exception text;
- plain open-start `--range` is cache-only; trailing `refresh` performs provider acquisition over that resolved interval;
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
- ForexFactory normalized events include `details.specs` from the provider Detail JSON payload; the visible calendar Detail navigation is not stored and no URL is synthesized from the event ID;
- malformed or unavailable ForexFactory Detail JSON is surfaced as a provider failure and never silently converted into fabricated Detail content;
- `--cleartext` renders normalized event details as human-readable fields rather than a raw JSON dictionary, without changing canonical data or machine-readable output.


## 14. Source layout and portability

The repository-root `calendar.py` remains the stable CLI entrypoint. Internal Calendar modules are grouped under `CALENDAR/` by responsibility, and the default persistent cache is `CALENDAR/calendar.json`. `SMC_DATA_ROOT` remains an explicit override.

The domain layer keeps event, interval, coverage, watermark, merge, filtering, and refresh decisions represented by explicit fields and simple scalar values so the semantic core remains straightforward to port to MQL4/MQL5. Python-only provider HTTP, HTML parsing, threading, and OS-specific locking are confined to infrastructure modules.

## 14.1 Rendered ForexFactory time handling

The rendered HTML fallback requires a concrete provider clock. Missing, `Tentative`, or `All Day` time text is not converted to `00:00` or another synthetic timestamp. Such a row causes provider parsing to fail closed; invalid hour/minute values are also rejected explicitly.


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


## 10.3 Source activity documentation

Calendar Python source must document the activity of its functions and meaningful state variables without changing runtime behavior. Function docstrings/comments must identify the function's role in the Calendar flow, including whether it is a public operation or an internal helper. Important module-level state variables must have concise comments describing what they represent and how they are used. Local variables should be documented through nearby comments when their role is non-obvious or when they carry acquisition, persistence, coverage, watermark, provider-result, or presentation state. Trivial loop/index variables do not require comments. Documentation must remain synchronized with the implementation and must not introduce generated noise or duplicate the specification.


## 10.4 Source attribution

Calendar Python source files must retain the following attribution header:
`# (c) Istvan Jakab <istvanhlc230@gmail.com>`

The attribution is informational source ownership/authorship metadata and must not affect runtime behavior.

## 2.4.3 Calendar CLI time shorthand

The Calendar CLI now supports a time-only --time HH:MM shorthand while preserving the canonical YYYY.MM.DD@HH:MM internal scope grammar.

- SYMBOL --time HH:MM resolves to the current UTC calendar day at the supplied minute;
- SYMBOL YYYY.MM.DD --time HH:MM resolves to the supplied date at the supplied minute;
- the same shorthand is available for explicit refresh SYMBOL and symbol-scoped delete SYMBOL;
- --time is rejected when an explicit scope already contains time or represents a range/current/latest/next operation;
- the shorthand is normalized before domain interval resolution, so persistence, provider routing, coverage, watermark and query semantics remain unchanged;
- the current date comes from the Calendar UTC clock, not the machine-local date;
- help text and source comments document the behavior.

Implementation version: 2.4.3; persistent schema remains 2.

Validation requirement: run the Calendar CLI parser matrix and fresh GitHub Actions validation before marking this change PASS.

## 10.5 Refresh provider/status contract

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
- provider diagnostics remain subject to the normal `--debug` stderr contract.

The modifier does not introduce a separate `REFRESHED`, `UNCHANGED`, or
`BOOTSTRAP_REQUIRED` query status. Change detection is represented by the
refresh summary.

## 2.4.4 Calendar date flag and last-update lookup

The public CLI also accepts explicit date/time flags:

- SYMBOL --date YYYY.MM.DD selects the exact UTC calendar day;
- SYMBOL --date YYYY.MM.DD --time HH:MM selects the exact UTC minute;
- SYMBOL --time HH:MM remains the current-UTC-day shorthand;
- the same --date / --time scope construction is supported by explicit refresh SYMBOL and scoped delete SYMBOL;
- --date and --time cannot be combined with an already explicit positional scope;
- date/time flags are normalized to the existing canonical scope grammar before domain resolution.

The read-only SYMBOL --last-update operation returns the latest successful provider acquisition timestamp (watermarks[provider|symbol].last_successful_at) for every applicable provider. It does not call providers, change coverage, change watermarks, or write calendar.json.

If no applicable provider has a successful watermark, the result status is NO_LAST_UPDATE. Missing individual provider watermarks are returned as null / N/A rather than fabricated timestamps.

The help text must expose --date, --time, and --last-update once in the FLAGS section and keep usage examples concise without duplicating equivalent --time forms.

Implementation version is 2.4.4; persistent schema remains V2.
## 2.4.6 current refresh and diagnostic-output correction

**Status: IMPLEMENTED — validation pending**

`current` is an always-refreshing operation when an applicable provider already has a
committed successful watermark. The watermark remains an incremental output cursor,
not a provider-call suppression mechanism. Every `current` invocation therefore
re-acquires from the applicable providers so mutable provider fields, especially
late ForexFactory Detail specifications, can be merged into the existing cache.

Provider acquisition failures are internal diagnostic state. Normal `current` output
does not expose failed provider records or exception text. The aggregate status still
reflects the internal provider outcomes (`PARTIAL`/`UNAVAILABLE`) so callers can detect
that the refresh was incomplete. With `--debug`, diagnostic exception information is
emitted to stderr only.

A second state-consistency correction preserves previously committed ForexFactory
`details.specs` when a later Detail request fails. A failed Detail request can no longer
replace an existing non-empty Detail specification list with an empty list. The event's
other freshly acquired normalized fields remain mergeable, the acquisition remains
`PARTIAL`, and the prior successful watermark is retained so the incomplete Detail
window is retried.

Validation requirements:
- compile the root entrypoint and all `CALENDAR/` modules;
- verify `current` invokes each applicable provider on every invocation with an existing
  watermark, including when no new event timestamp exists;
- verify a later Detail acquisition replaces previously missing/old `details.specs`;
- verify a Detail failure preserves previously committed non-empty `details.specs`;
- verify provider `ERROR`, `error`, `reason`, and Detail-failure diagnostics are absent from
  normal `current` stdout;
- verify `--debug` retains provider exception diagnostics on stderr;
- verify aggregate status still reports `UNAVAILABLE` for all-provider failure and
  `PARTIAL` for mixed successful/failed acquisition;
- run fresh GitHub Actions validation before marking this change PASS.

## 2.4.7 current bootstrap refresh correction

**Status: IMPLEMENTED — validation pending**

`current` now refreshes an applicable provider even when its provider+canonical-symbol
watermark is missing. Missing watermark means bootstrap acquisition, not `BOOTSTRAP_REQUIRED`
termination.

For ForexFactory the bootstrap current window is `(now - 1 day)` rounded down to UTC midnight
through `(now + 1 day)` rounded down to UTC midnight, with Detail enrichment enabled. For Yahoo
Finance the normal provider news acquisition is executed. Successful provider acquisition updates
the provider watermark to the current UTC timestamp; a successful zero-result Yahoo acquisition
therefore also commits its watermark and does not repeatedly bootstrap on the next invocation.

Because bootstrap has no previous incremental cursor, bootstrap-acquired events are persisted but
not returned in the incremental `events` array. The aggregate provider status remains normal
(`OK`, `NO_MATCH`, or `PARTIAL`).

Validation requirements:
- verify `SYMBOL current` performs provider acquisition on first use with no watermark;
- verify first-use successful acquisition persists a watermark;
- verify successful Yahoo `NO_MATCH` bootstrap also persists its watermark;
- verify a second `current` call uses the normal existing-watermark refresh path;
- verify no `BOOTSTRAP_REQUIRED` provider status is emitted by `current`;
- run fresh GitHub Actions validation before marking this change PASS.
## 2.4.8 read-only current and trailing refresh modifier

**Status: IMPLEMENTED — validation pending**

The public `current` query is now cache-only. It reads committed provider-specific watermark boundaries
and returns matching cached events without provider/network I/O or persistent-state mutation.

Provider acquisition is requested with the trailing `refresh` modifier. The previous standalone
`refresh SYMBOL SCOPE` command grammar is removed. The modifier applies the requested scope timespan;
`current refresh` derives its logical interval from the current incremental watermark state and uses
a bounded first-use interval when no watermark exists.

Monitor-triggered refresh is a background operation and must not block the candle-close processing path.
The refresh summary reports additions/changes/unchanged counts rather than introducing a separate
refresh query status.

Validation requirements:
- verify plain `current` performs no provider call;
- verify `current refresh` performs the refresh operation;
- verify trailing `refresh` parsing for current/relative/date/datetime scopes;
- verify old standalone `refresh SYMBOL SCOPE` syntax is rejected;
- run fresh GitHub Actions validation before marking this change PASS.


## 2.4.9 CLI refresh result-boundary correction

**Status: IMPLEMENTED — validation pending**

The refresh operation is the authoritative source of the public post-refresh `events` result.
The CLI no longer reconstructs refresh output from the committed cache after the refresh operation.

This correction is required because a post-refresh cache query can incorrectly hide valid refresh results:
- first-use refresh events may exist before refresh establishes coverage/watermark state;
- rescheduled events may have moved outside the original logical interval while remaining visible by stable event ID;
- `current refresh` has an explicit logical interval even when no prior watermark exists.

The CLI therefore passes `refresh_result["events"]` directly to presentation and machine-readable output.
Plain `current` remains cache-only.

Implementation version: 2.4.9; persistent schema remains V2.

Validation requirements:
- compile the Calendar entrypoint and all `CALENDAR/` modules;
- verify explicit first-use refresh events are returned by the CLI;
- verify first-use `current refresh` events are returned by the CLI;
- verify rescheduled refresh events remain in CLI output by stable event ID;
- verify the refresh result is not filtered by committed coverage/watermark state;
- run fresh GitHub Actions validation before marking this change PASS.


## 2.4.10 Open-start range correction

**Status: IMPLEMENTED — validation pending**

The Calendar CLI supports open-start `--range -END` queries and refreshes. The start is resolved from the
latest recorded visible event for SYMBOL in the committed cache. Date and datetime END forms are supported;
`HH.MM` is accepted as a compatibility alias for the datetime END and normalized to `HH:MM`.

