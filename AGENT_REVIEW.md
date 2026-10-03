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


## Canonical Event Contract Guard — 2026-10-03

Static re-audit of the preceding calendar parser correction found one remaining integrity gap: validate_calendar_document() still accepted provider-internal currency values such as US/AU and empty event titles if malformed records already existed or entered through another internal path.

The guard is now tightened in calendar.py:

- persisted currency must be one of USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD, CNY, HUF, or the provider-wide ALL marker;
- provider-internal country codes are rejected;
- normalized provider event titles must be non-empty;
- acquisition fails before persistence when the provider supplies an unsupported currency or empty title.

The owning Calendar specification and design are synchronized with this behavior.

Fresh local acquisition/query validation is still required before PASS. The live ForexFactory calendar currently exposes canonical three-letter currency labels and legitimate provider-wide All events, so allowing ALL is required rather than invented.

## Provider Field Mapping Correction — 2026-10-03

The supplied ForexFactory structured event payload exposed the exact provider fields needed by the canonical event contract. The previous normalization incorrectly read `country`, `title`, and numeric `impact`, even though the provider record supplies the canonical values in `currency`, `name`, and `impactName`.

Correct mapping implemented in `calendar.py`:

- `id` → `event_id`
- `dateline` → UTC `datetime`
- `currency` → canonical `currency`
- `name` → canonical `event`
- `impactName` (with `impactClass` fallback) → canonical `impact`
- `actual`, `forecast`, `previous` → corresponding canonical values
- `country` is deliberately not used for canonical currency.

The structured `days` payload is now the canonical acquisition source. The HTML parser is compatibility-only.

Fresh local validation is required: delete and reacquire the calendar, then verify canonical currencies, non-empty event names, and actual LOW/MEDIUM/HIGH/HOLIDAY impact values.


## Superseding Provider Contract Finding — 2026-10-03

The supplied raw ForexFactory event objects establish that the structured `days` payload is the correct canonical provider source. The earlier HTML-only correction was therefore incorrect and is superseded.

The provider event object explicitly supplies:

- `id`
- `dateline`
- `currency` (canonical three-letter code or provider-wide `ALL`)
- `name` (event title)
- `impactName` (for example `low`)
- `impactClass` (fallback representation)
- `actual`
- `forecast`
- `previous`

The previous implementation incorrectly normalized `country` as currency, `title` as event name, and numeric `impact` as impact. This explains the observed `WW/AU/JN/US/... + UNKNOWN + empty event` output exactly.

The correction now uses the structured `days` payload for canonical acquisition and maps the fields above directly. The HTML parser is compatibility-only.

Acceptance remains BLOCKED until the developer runs the corrected version locally against a fresh acquisition and verifies the resulting `calendar.json`.

## Repository Synchronization and Validation
- **Action**: Synchronized local state with remote `main` (commit `44b92c1`). 
- **Validation**:
  - `python calendar.py delete` -> successfully cleared the old malformed cache containing internal ForexFactory country codes.
  - `python calendar.py week` -> downloaded live HTML calendar and correctly populated `calendar.json` with canonical 3-letter currency codes and valid UTC representations.
  - `python calendar.py week USDHUF` -> filtered properly, matching `USD` and `HUF` events perfectly against the live payload.
- **Integrity**: `validate_calendar_document()` passes perfectly; no provider internal country codes (`US`, `AU`) or empty titles survive the validation checks. `impact` reflects the provider's supplied impact seamlessly.
- **System dependencies**: Validated that `tzdata` is required on Windows for `zoneinfo` instantiation. `tzdata-2026.5` installed locally to support pipeline execution.


## Remaining Calendar Integrity Corrections — 2026-10-03

Follow-up audit identified two implementation hardening issues that did not change the canonical provider contract:

1. extract_days_payload() previously used a non-greedy regex to determine the end of the JSON array. This could truncate a valid structured payload if nested JSON/string content contained a closing bracket. The field is now located by regex, but the complete array boundary is determined by json.JSONDecoder().raw_decode().

2. Canonical acquisition previously normalized every provider event returned by the response before persistence without explicitly restricting new events to the exact acquired UTC interval. Normalized provider events are now filtered to [fetch_start, fetch_end) before merge/persistence. Events outside coverage cannot silently extend the cache.

Additionally, impactName = non-economic is normalized to canonical HOLIDAY.

The Calendar specification and design were synchronized with these corrections.

Fresh local runtime validation remains required after this iteration.


## Cleartext Query Output — 2026-10-04

Added the `--cleartext` query-output option without changing the machine-readable JSON contract.

Behavior:

- `--cleartext` may be combined with a scope, symbol, and optional evaluation token.
- It is valid only when a symbol query is present.
- It is rejected for `delete` commands and scope-only commands.
- Default output remains unchanged JSON.
- Cleartext output renders one human-readable block per event with UTC date/time, currency, impact, event title, actual, forecast, previous, and event ID.
- Acquisition, filtering, evaluation, persistence, and coverage semantics are unchanged.

Required local validation:

    python -m py_compile calendar.py
    python calendar.py next_week USDHUF --cleartext
    python calendar.py next_week USDHUF
    python calendar.py USDHUF --cleartext
    python calendar.py delete --cleartext

Expected: the first, third commands render event blocks; the second remains JSON; the delete form is explicitly rejected. No SMC methodology or canonical event contract is changed.
