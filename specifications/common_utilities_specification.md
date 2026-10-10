# Common Python Utilities Specification

Status: Approved implementation contract.

## 1. Purpose and dependency direction

`COMMON/` contains small, provider-independent helpers that are truly shared between Calendar and Market Data. It must not import from `CALENDAR/`, `MARKET_DATA/`, or `PROVIDERS/`. Those modules may import from `COMMON/`.

Initial shared utilities:

- `COMMON/date_time.py`: reusable date/time scope parsing, UTC conversion, and ISO 8601 helpers.
- `COMMON/atomic_file.py`: atomic UTF-8 text replacement with finite optional retry.
- `COMMON/http_client.py`: standard-library HTTP GET transport, optional response decoding, and caller-configured bounded retries.
- `PROVIDERS/credentials.py` remains the canonical shared provider credential loader and is not duplicated or moved.

## 2. Date/time scope parser

Public class: `DateTimeScopeParser`. Public result type: `DateTimeScope`. Public parse errors: `DateTimeScopeError`.

The parser is a pure parser apart from its captured reference UTC time. It accepts an injectable reference time for deterministic tests, performs no I/O, and returns explicit scope kind, start/end boundaries, and open-start/open-end flags.

Canonical public syntax:

- `YYYY.MM.DD`
- `YYYY.MM.DD HH:MM`
- `YYYY.MM.DD-YYYY.MM.DD`
- `YYYY.MM.DD HH:MM-YYYY.MM.DD HH:MM`
- `HH:MM`
- `HH:MM-HH:MM`
- `YYYY.MM.DD-`, `YYYY.MM.DD HH:MM-`, `HH:MM-`
- `-YYYY.MM.DD`, `-YYYY.MM.DD HH:MM`, `-HH:MM`

Date/time is separated by a single whitespace sequence; `@` is not part of the public grammar. Time-only scopes are anchored to the captured current UTC date. A date scope covers a complete UTC day. A date/time or time-only point covers one minute. Date ranges are inclusive by calendar date and normalize to a half-open UTC interval. Explicit datetime/time ranges use a half-open interval and require the end to be later than the start. Overnight time-only ranges are rejected. Open-end means the current UTC time; open-start leaves the start unresolved for the consuming domain layer while returning a normalized explicit end boundary.

The class does not query cached data to choose an open-start boundary. Calendar resolves it using the latest visible event timestamp; Market Data uses its per-timeframe retained candle state. Neither consumer may duplicate the syntax parser.

## 3. Shared UTC and ISO 8601 helpers

Provide:

- `utc_now()` — current aware UTC datetime.
- `ensure_utc(value)` — reject naive datetimes and convert an aware datetime to UTC.
- `format_utc_iso8601(value, timespec="auto")` — serialize an aware datetime in UTC with a trailing `Z`.
- `parse_aware_datetime(value, require_utc=False)` — parse an ISO 8601 string with an explicit timezone and normalize to UTC; when `require_utc=True`, reject non-zero offsets.

Module-specific wrappers may preserve stricter validation and error types, but must delegate parsing and conversion to these shared primitives.

## 4. Atomic UTF-8 file replacement

`atomic_write_text(path, content, prefix, retry_limit=1, retry_delay_seconds=0.0)` creates a temporary UTF-8 file in the destination directory, writes and flushes content, calls `fsync`, then atomically replaces the destination with `os.replace`. It must clean up temporary files after failure, perform no unbounded retry, and raise an `OSError` subclass/instance on exhausted attempts. It does not serialize JSON, validate schemas, acquire domain-specific locks, or alter the caller's error category.

Calendar and Market Data retain their own validation, serialization, locking, and error translation. The Market Data caller may configure retries; Calendar preserves its existing single-attempt file-write behavior.

## 5. Standard-library HTTP GET client

`HttpClient.get(url, headers, timeout_seconds, response_format, retries, retry_delay_seconds)` is a transport helper using `urllib.request` only. Supported response formats are bytes, UTF-8 text, and JSON. Retry count is finite, and retry delay grows linearly by attempt. Errors must not include request headers, URLs containing credentials, or credential values.

Calendar keeps its own provider URL construction, user agent, timeout and `ProviderError` mapping. Market Data keeps API-key loading, URL/query construction, JSON payload validation, timeframe mapping and provider-specific failure policy. The shared client does not know about LSE, ForexFactory, Yahoo, currency pairs, events, candles, cache schemas, or watermarks.

## 6. Explicit non-goals

Do not merge Calendar and Market Data domain models, event/candle identities, persistence schemas, retention policies, symbol validation policy, cleartext output, HTTP payload normalization, provider mappings, retryable application semantics, or provider error categories. Similar code may be shared only when its contract is genuinely equivalent.

## 7. Acceptance

Acceptance requires:

- the shared module imports without importing Calendar or Market Data;
- every canonical scope form above parses identically regardless of which CLI invokes it;
- invalid leap dates, invalid clock values, mixed endpoint types, reversed ranges, naive datetimes, and unsupported syntax fail explicitly;
- time-only scopes are deterministic when a reference UTC time is injected;
- open-start scopes never invent a start timestamp;
- atomic writes preserve the old destination if replacement fails and clean up temporary files;
- HTTP errors never leak credentials or headers and retry count is finite;
- Calendar and Market Data CLI scope behavior, output protocols, schema validation, locks, and data semantics remain unchanged apart from the explicitly approved positional scope grammar.
