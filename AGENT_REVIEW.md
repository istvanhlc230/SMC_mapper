# AGENT_REVIEW.md — Calendar/Monitor Update Engine Synchronization

Status: VALIDATED_CI_CONTRACT_SUITE_PENDING_LIVE_PROVIDER_SMOKE

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


## Debug CLI contract

Calendar `--debug` is now explicit and diagnostic-only. It controls detailed exception
traceback printing to stderr. Concise user-facing errors remain visible without debug.
Debug state never changes stdout machine-readable output, Calendar data, provider routing,
coverage, watermarks, or canonical semantics.


## Re-audit and automatic correction

The `--debug` change was re-audited together with the full Calendar acquisition,
watermark, Yahoo-resolution, cache-visibility, and persistence paths.

Four implementation defects were corrected in this snapshot:

1. Yahoo explicit-range acquisition now filters the rolling feed to the requested
   interval before merging, so out-of-range news is not persisted as a side effect.
2. Yahoo explicit-range acquisition no longer advances the current cursor to the
   wall-clock fetch time for an old range. Its cursor advances at most to
   `min(requested_end, now)`, never regresses, and future-only requests do not
   bootstrap Yahoo current state.
3. When Yahoo explicitly reports that an FX pair has no verified Forex instrument,
   previously cached Yahoo events for that pair are excluded from the explicit query
   result; the unavailable provider state cannot be bypassed through cache.
4. The previous `debug` parameters on `run_query()`/`run_delete()` were unused.
   They were removed, and the CLI now also gates the unexpected-exception traceback
   behind `--debug`.

Additional robustness corrections were made to reject malformed event/coverage/
watermark records as `DataIntegrityError` and to treat Yahoo UUID values of
`None`/empty as missing, using the deterministic fallback ID instead.

Yahoo USD-base resolution now also derives the quote-currency `=X` form as a
verification candidate while retaining exact provider-side verification. No
unverified provider symbol is fabricated.

### Validation boundary

Static/reasoned re-audit is complete for this snapshot. Local runtime execution and
repository-side CI are still unavailable in this environment, so the status remains
`BLOCKED_PENDING_LOCAL_RUNTIME_VALIDATION`; no PASS claim is made.


## Two-pass test/audit correction

Initial runtime test on the automated Calendar suite:
- `python -m py_compile calendar.py`: PASS.
- Contract suite: FAIL at the debug subprocess assertion. The test invoked a live
  provider path and incorrectly required stderr even when execution completed without
  an exception. This was a test-design defect, not evidence of a Calendar runtime fault.

Automatic audit correction:
- Reworked debug validation to inject an unexpected exception and verify the
  `--debug` traceback boundary without network access.
- Added provider-level `ProviderError` debug checks.
- Wired `debug` from the CLI query boundary into both provider acquisition paths.
- Added future-only and watermark non-regression checks to the suite.


## Second audit correction

The first post-fix test run compiled successfully but the contract suite stopped before
executing its assertions because the workflow script contained an accidental indentation
error. Static audit of the tested Calendar snapshot simultaneously found one real CLI defect:
the top-level `run()` parsed `--debug` but did not pass it into `run_query()`, so
provider-level diagnostics could not be enabled from the public CLI.

Both issues are corrected in this commit. The automated suite now explicitly asserts that
`run()` propagates `debug=True` into `run_query()`, and provider-error diagnostics are
tested without network access.


## Third audit correction

The second post-fix GitHub test compiled `calendar.py` successfully but the contract
suite failed with an `IndentationError` caused by a duplicated debug-test block in the
workflow script. The Calendar implementation itself was not the source of that failure.

This commit removes the duplicate test block and leaves one deterministic, network-free
debug propagation/traceback test. No dedicated `test/` directory is introduced.


## Final CI validation

The final GitHub Actions Calendar runtime suite on commit `e719a93505fbf2d54cfdfc90c70d0f88becc262d` completed successfully.

Validated:
- `python -m py_compile calendar.py`: PASS
- Calendar unit/runtime contract suite: PASS
- debug propagation and stderr-only traceback contract: PASS
- Yahoo candidate verification and cache visibility guards: PASS
- explicit Yahoo interval filtering, future-only handling, and watermark non-regression: PASS

The suite uses deterministic provider mocks for provider-dependent paths. No claim of live
ForexFactory/Yahoo integration availability is made by this CI result.


## Next-event query

Added the public `python calendar.py SYMBOL next` query.

Contract:
- `next` is read-only and uses only the committed `calendar.json` snapshot;
- provider acquisition is not triggered;
- events are filtered with the existing symbol visibility and `suppressed_for` rules;
- only timestamps strictly later than current UTC time are eligible;
- exactly the chronologically nearest event is returned;
- no matching future event returns `NO_NEXT_EVENT`;
- coverage and watermarks are never modified by `next`.

The specification and deterministic CI contract suite were updated together with the implementation.
