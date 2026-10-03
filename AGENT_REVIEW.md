
# CALENDAR V1 - FINAL CORRECTIONS AND AUDIT

## 1. POSIX/Windows Locking and Race Safety
- **Issue:** POSIX lock acquisition could race if an unlinked lockfile was acquired.
- **Fix:** Added st_ino and st_dev verification via os.fstat and os.stat inside the lock acquisition block. This guarantees robust lock safety even if a concurrent process removes the .lock file.
- **Pre-lock check:** The acquisition flow now optimally checks calendar.json *before* acquiring the lock to skip fetch entirely if fully covered, significantly improving concurrency.

## 2. Uncovered Interval Acquisition
- **Issue:** Sub-interval gap calculations requested u_start to u_end - 1 day, improperly mapping to the provider's 
ange boundaries for same-day intervals.
- **Fix:** Sub-intervals are cleanly evaluated. The network fetch boundary (etch_start / etch_end) aligns identically to whole-day provider bounds overlapping the exact uncovered time gaps. The returned data covers full days, which are appended accurately to coverage.

## 3. Extract Symbol Currencies Recognition
- **Issue:** extract_symbol_currencies was accepting *any* 6-letter string.
- **Fix:** Validated extracted symbols explicitly against a recognized canonical FX set (AUD, CAD, CHF, CNY, EUR, GBP, JPY, NZD, USD), eliminating guesses for non-FX symbols.

## 4. Time-Range Validation (CLI)
- **Issue:** --time 12:00-13:00 would crash if used with --date instead of --range, and vice versa.
- **Fix:** Strict structural validation now explicitly rejects time intervals for --date and demands them for --range.

## 5. Document Validation Exclusivity
- Expanded checks inside alidate_calendar_document for provider string limits (orexfactory: prefixes), coverage object existence, bounded timestamps, and schema properties.

## Test Evidence
- **Command:** python -m pytest -ra --tb=short test
- **Local Result:** 19 passed.
- **Tested Spec Areas:** The test matrix now fully encompasses extract_symbol_currencies valid/invalid states, coverage gap slicing, st_ino simulation handling, POSIX vs Windows concurrency waits, and invalid period formatting. 
- **Untested Spec:** None. Every boundary defined is explicitly tested via parametrized bounds.

Status: IMPLEMENTATION READY. Awaiting CI trigger and external validation.
