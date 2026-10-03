# Calendar Implementation Design

## 1. Purpose

calendar.py is the single Calendar V1 implementation.
It acquires ForexFactory economic-calendar data, maintains a normalized global calendar.json, supports deterministic local symbol queries, and supports explicit calendar-data deletion.
The module does not implement SMC logic and does not generate symbol-specific news JSON.

## 2. Canonical CLI

Public grammar:

    python calendar.py [scope] [symbol] [evaluation]

Delete grammar:

    python calendar.py delete [scope]
    python calendar.py delete

The only flag-style options are -h and --help.

## 3. Scope Vocabulary

Relative scopes:

- today — current UTC calendar day
- next_day — following UTC calendar day
- week — current UTC calendar week
- next_week — following UTC calendar week
- month — current UTC calendar month
- next_month — following UTC calendar month

Datetime scopes:

- today@HH:MM
- YYYY.MM.DD@HH:MM

Explicit date scopes:

- YYYY.MM.DD
- YYYY.MM.DD-YYYY.MM.DD

The range is inclusive by calendar date and is represented internally as [start, end), with end at the following UTC midnight.
An @HH:MM suffix sets the evaluation reference time while acquisition covers the containing UTC calendar day.

## 4. Symbol Contract

A symbol is a six-letter FX pair made from:

    USD EUR GBP JPY CHF AUD CAD NZD CNY HUF

Examples: USDHUF, EURHUF, EURUSD, USDJPY.
Common separators /, - and _ are removed and the result is upper-cased. Invalid or unsupported symbols are rejected explicitly.
Symbol-only execution never performs provider acquisition.

## 5. Evaluation Contract

Supported evaluations:

- current — return events matching the reference date/hour/minute.
- next — return the earliest event strictly after the reference timestamp.

When evaluation is omitted, all symbol events inside the resolved scope are returned.
For symbol-only queries, the reference timestamp is the current UTC time.
For a scope with @HH:MM, the explicit timestamp is the reference.
For a relative scope without @HH:MM, the current UTC timestamp is the reference.

## 6. Execution Pipeline

The canonical pipeline is:

    SCOPE -> ACQUISITION/COVERAGE -> SYMBOL FILTER -> OPTIONAL EVALUATION

Example:

    python calendar.py today USDHUF current

1. Resolve today's UTC interval.
2. Ensure required coverage exists.
3. Use the post-acquisition calendar document.
4. Filter events to USDHUF currencies.
5. Apply current evaluation.

Symbol-only example:

    python calendar.py USDHUF current

This reads the existing local calendar document only and never acquires network data.

A scope-only command performs acquisition/coverage handling and does not emit symbol-evaluation JSON.

## 7. Delete Contract

Whole dataset:

    python calendar.py delete

Scoped deletion accepts every canonical scope, including date ranges and @HH:MM timestamps.
A datetime delete removes the one-minute half-open interval beginning at the specified UTC minute.
Delete accepts no symbol or evaluation token.

## 8. Coverage and Persistence

calendar.json contains schema_version, source, coverage, and events.
Coverage intervals are half-open [start, end).
Missing coverage is calculated before acquisition. Acquisition requests are expanded to full UTC calendar-day boundaries.
Provider events are normalized, merged, and deduplicated by stable provider identity. Identity/time conflicts are fatal.
Validated state is persisted atomically with os.replace.
Concurrent writes are serialized using a Windows named mutex or POSIX directory-inode flock.

## 9. Provider Boundary

The provider is ForexFactory.
The current implementation expects the provider HTML response to contain an embedded JSON days payload. That payload is parsed and normalized before any persistent update.
Provider fetch or payload validation failure terminates without replacing the existing calendar document.

## 10. Domain Functions

CLI and parsing:

- print_help — detailed user-facing CLI reference.
- parse_calendar_request — classify positional tokens into operation, scope, symbol, and evaluation.
- parse_scope_token — validate and decompose a scope.
- is_scope — scope classifier.
- normalize_symbol — canonicalize supported separators and case.
- validate_symbol — validate a canonical FX pair.
- is_symbol — symbol classifier.
- is_evaluation — recognize current or next.
- parse_date, parse_time, parse_date_range — validate explicit temporal syntax.

Scope resolution:

- resolve_scope_interval — map scope to a UTC half-open interval.
- resolve_scope_reference — derive the evaluation reference timestamp.
- resolve_delete_intervals — map delete scope to a deletion interval.

Provider and normalization:

- fetch_calendar_source — retrieve provider HTML.
- extract_days_payload — extract embedded days JSON.
- parse_calendar_days — decode and validate provider days.
- normalize_provider_event — map one provider event to the canonical event model.
- normalize_calendar_events — normalize a provider day collection.

Persistence and integrity:

- build_empty_calendar_document
- validate_calendar_document
- load_calendar_document
- save_calendar_atomic
- acquire_calendar_lock

Coverage and merge:

- resolve_coverage
- find_uncovered_intervals
- merge_coverage
- deduplicate_calendar_events
- merge_calendar_events

Query:

- extract_symbol_currencies
- filter_events_for_symbol
- filter_events_for_interval
- query_current_events
- query_next_events
- query_nearest_events
- output_query_result

Deletion and orchestration:

- delete_events
- delete_coverage
- run_acquisition
- run_query
- run_delete
- run
- main

Core business functions receive semantic values rather than legacy argparse namespaces or old flag-specific arguments.

## 11. Error Contract

Reject:

- missing command input;
- malformed scopes, dates, times, or ranges;
- invalid or unsupported FX symbols;
- evaluations without a symbol;
- unexpected extra positional tokens;
- delete combined with non-delete tokens.

User input errors must produce explicit CLI errors and must not fall through to raw Python exceptions.

## 12. Repository Hygiene

Temporary, intermediate, debug, downloaded, and generated development artifacts belong under dev_tmp/.
No test/ directory is required or maintained.
The implementation is kept in calendar.py and the design is kept in specifications/calendar_design.md.