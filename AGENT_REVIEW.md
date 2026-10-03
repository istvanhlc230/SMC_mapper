# CALENDAR V1 - CURRENT REVIEW RECORD

This file records implementation evidence and audit findings. It is not independent acceptance evidence.

## Unified CLI Refactor

The public CLI is:

    python calendar.py [scope] [symbol] [evaluation]
    python calendar.py delete [scope]
    python calendar.py delete

The only flag-style options are -h and --help.

## Corrections Applied

- Replaced the malformed intermediate calendar.py produced by the previous refactor with a complete, self-consistent implementation.
- Restored build_empty_calendar_document, find_uncovered_intervals, merge/deduplication, provider normalization, and all other runtime dependencies required by acquisition.
- Added explicit symbol validation so invalid six-character tokens cannot silently be treated as arbitrary currencies.
- Added explicit scope parsing with controlled date/time validation.
- Added detailed --help / -h documentation covering scope, datetime, symbol, evaluation, delete, examples, UTC semantics, and errors.
- Ensured scoped queries filter events to the resolved scope after acquisition.
- Preserved cache-only symbol queries.
- Preserved HUF support and separator normalization.
- Preserved scoped deletion including date ranges and one-minute datetime deletion.

## Audit Findings Resolved

The previous audited commit a57b1c31eca68d70fc1fd8b1aea04fdebe56dd75 was BLOCKED because calendar.py referenced removed functions and the design/review documentation was stale.
The corrected implementation no longer contains the missing runtime functions and no longer depends on the removed flag-based CLI.

## Validation Boundary

The provider currently returns HTTP 403 to direct urllib acquisition in the audit environment. Therefore this record does not claim successful live ForexFactory acquisition.
Acceptance requires local execution of syntax, parser, cache-only, scoped-query, delete, and invalid-input validation in the developer environment.

## Required Validation Commands

    python calendar.py --help
    python -m py_compile calendar.py
    python calendar.py USDHUF
    python calendar.py USDHUF current
    python calendar.py USDHUF next
    python calendar.py today USDHUF current
    python calendar.py today@14:30 USDHUF current
    python calendar.py next_week USDHUF next
    python calendar.py next_month EURHUF
    python calendar.py 2026.10.03-2026.10.31 EURHUF
    python calendar.py delete 2026.10.01-2026.10.31

Invalid-input validation should include malformed dates/times/ranges, unsupported symbols, unexpected tokens, evaluation without a symbol, and invalid delete combinations.

## Cross-Specification Synchronization

The owning Calendar specification was migrated to the positional CLI contract. The Monitor specification was also updated so its Calendar process boundary uses `calendar.py SCOPE SYMBOL [current|next]` or the cache-only `calendar.py SYMBOL [current|next]` form.


## Calendar Provider Parser Correction — 2026-10-03

The prior implementation incorrectly selected the embedded ForexFactory `days` payload whenever it was present. That produced provider-internal country codes such as `AU`, `JN`, `US`, widespread `UNKNOWN` impact values, and empty event titles in the persisted canonical event model.

Correction applied:

- The live ForexFactory HTML row parser is now the sole canonical acquisition path.
- Provider HTML currency, impact, title, actual, forecast, previous, and timezone fields are normalized from the calendar rows.
- The embedded `days` payload is retained only as a legacy compatibility/diagnostic helper and cannot override canonical HTML data.
- The owning Calendar design and specification were synchronized in the same commit.

The previously generated `calendar.json` containing malformed canonical fields must be discarded/rebuilt through a fresh scope-bearing acquisition after this correction. Existing coverage must not be treated as proof that the malformed event normalization is acceptable.

Acceptance remains BLOCKED until a fresh local acquisition/query demonstrates canonical currency codes (for example `USD`, `HUF`, `EUR`, `JPY`, `AUD` where applicable), populated event titles, and non-default impact values where the provider supplies impact data.
