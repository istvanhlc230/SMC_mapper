# AGENT_REVIEW.md — Calendar/Monitor Update Engine Synchronization

Status: BLOCKED_PENDING_LOCAL_RUNTIME_VALIDATION

## Follow-up audit correction

Re-audit found a section-boundary regression in the previous Monitor rewrite: the 4.6/6.6 subsection replacement could consume the next top-level section header.

Corrected here by rebuilding the Monitor specification from the pre-refactor full document and terminating subsection replacements at the next same-or-higher-level heading.

Unrelated Monitor contracts are preserved, including target, RR, session, checkpoint, alert, persistence, portability, and validation sections.

Calendar implementation/specification corrections from the preceding commits remain intact: coverage reuse, non-overlapping coverage preservation, exact requested-interval filtering, explicit symbol-first CLI, watermark current semantics, and provider isolation.

## Validation boundary

The committed GitHub working tree could not be materialized into the local runtime in this environment; GitHub reports no associated CI status for the commit.

Required repository-side checks remain:

    python -m py_compile calendar.py
    python calendar.py --help
    python calendar.py EURUSD current
    python calendar.py NVDA current
    python calendar.py HUF 2026.10.01
    python calendar.py delete


Negative CLI checks must reject old today/next_week/next_month forms, next evaluation, and `..` ranges.

## Deletion contract added

Supported scoped delete forms:

    delete SYMBOL YYYY.MM.DD
    delete SYMBOL YYYY.MM.DD-YYYY.MM.DD
    delete SYMBOL YYYY.MM.DD@HH:MM
    delete SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM

Bare delete remains full-cache deletion; scoped deletion requires a symbol.
current is rejected as a delete scope.

ForexFactory economic events remain physically shared; symbol deletion
invalidates only that symbol/provider coverage. Yahoo symbol-owned news is
physically deleted. The newest affected watermark is removed when necessary.

No PASS claim until local runtime validation is complete.

This follow-up also serializes Calendar acquisition/read-modify-write paths under the Calendar lock to prevent concurrent writer loss.


## Deletion hardening

ForexFactory shared events now carry optional symbol suppression metadata so symbol-scoped deletion is visible to both Calendar queries and the Monitor without globally deleting a shared currency fact. Successful provider reacquisition clears the relevant symbol suppression. Yahoo symbol-owned news remains physically deletable.


## Monitor contract cleanup

Removed remaining legacy Calendar function names and stdout-query boundary from the Monitor specification. The Monitor now uses request_calendar_update_async and the committed calendar.json snapshot, including suppressed_for visibility semantics.


## Yahoo Forex resolution hardening

The previous implementation incorrectly synthesized unknown FX provider symbols with a generic
`PAIR=X` fallback. The Calendar now recognizes six-letter FX candidates from a currency-code
universe, but Yahoo Finance remains authoritative for the concrete instrument.

For FX pairs the Yahoo Search response must contain the exact candidate symbol and explicitly
classify it as a currency instrument. Only then are Yahoo news events normalized and persisted.
If no verified Yahoo Forex instrument exists, the provider result is
`SKIPPED_NO_FOREX_PAIR`; no Yahoo event, coverage interval, or watermark is created or advanced.

USD-base alternate symbols remain explicit candidates (for example `JPY=X` for `USDJPY`),
and direct `PAIR=X` is tried only as a candidate that must still be independently verified by Yahoo.
No provider symbol is fabricated from string concatenation.

The Calendar specification/design were updated to make provider verification normative. Runtime
validation is still required before PASS.


## Resolver return-contract correction

The public `resolve_yahoo_symbol()` helper now returns `None` when no verified Yahoo Forex
instrument exists, matching its `Optional[str]` contract. The acquisition path still uses the
explicit `YahooForexPairUnavailable` signal so missing provider instruments cannot be converted
to empty-success coverage or watermark advancement.


## Re-audit corrections

The prior audit identified three concrete implementation defects and one stale wording item.
This commit corrects all four:

1. `is_fx_pair()` and `validate_symbol()` now use `FX_CURRENCY_CODES`, allowing
   valid six-letter FX candidates outside the narrower standalone-currency CLI set.
2. `normalize_provider_event()` now validates ForexFactory currency codes against
   `FX_CURRENCY_CODES`, so valid pair components such as SEK/NOK/QAR/BRL are not
   rejected at normalization.
3. `acquire_current()` now passes `clear_suppressed_symbol=symbol` when merging
   ForexFactory events, so successful reacquisition restores visibility after a
   symbol-scoped deletion.
4. Monitor Phase 9 now describes Calendar Update Engine acquisition versus Monitor
   local committed-snapshot reading rather than the obsolete "local query" wording.

The Calendar specification/design acceptance language was synchronized with these
implementation rules. Runtime validation remains the only unperformed validation boundary.


## Re-audit correction: missing coverage-gap function

Static symbol inspection found that `find_uncovered_intervals()` was called by explicit
Calendar acquisition and by the query visibility guard, but had no definition in the committed
module. This would cause a runtime `NameError` on every explicit range acquisition.

The function is now implemented according to the Calendar coverage contract: only matching
provider+canonical-symbol intervals with status `COMPLETE` satisfy requested coverage;
`PARTIAL` intervals remain gaps. Multiple complete intervals are clipped to the requested
boundary and merged logically while calculating uncovered gaps.

Runtime validation is still required before PASS.
