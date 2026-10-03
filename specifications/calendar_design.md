# Calendar Implementation Design

## 1. Responsibilities and Non-Responsibilities
**Responsibilities:**
- Acquire ForexFactory economic calendar data without modifying SMC files.
- Parse provider HTML payload, normalizing to UTC and stable event_id.
- Maintain a single global calendar.json with tracking for coverage intervals.
- Provide time-based local queries for FX symbols.
- Provide explicit deterministic deletion with interval coverage update.
- Ensure atomic, locked persistence of calendar.json using stable, persistent OS-level locking (directory lock on POSIX, Named Mutex on Windows).
- Fail cleanly on acquisition failures, leaving the last-known-good file intact.
- Correctly compute uncovered subintervals to minimize network requests.

**Non-Responsibilities:**
- No SMC calculation (BOS, CHoCH, IDM, Dealing Range, POI, etc.).
- No generation of symbol-specific News JSON.
- No automatic retention or cleanup (only explicit --delete).
- No evaluation of setup validity or trading decisions.
- Monitor execution policy does not belong in this module.

## 2. Boundaries and Dependencies
- **Module Architecture:** calendar.py is the single calendar implementation/module containing both the CLI wrapper and the core execution engine. The `--query` (acquisition) and `--symbol` (evaluation) operations are independent but composable stages within a single invocation pipeline.
- **Inputs:** CLI arguments, ForexFactory HTML response, existing calendar.json.
- **Outputs:** Console output (JSON format for local queries), updated calendar.json.
- **Side effects:** Atomic update of calendar.json.
- **Concurrency:** Indefinite waiting. POSIX utilizes fcntl.flock(LOCK_EX) on the parent directory inode. Windows utilizes CreateMutexW(WaitForSingleObject) for a non-file-backed stable identity SMC_Calendar_Lock. Both are intrinsically race-safe against the os.replace operation of calendar.json.
- **Dependencies:** Standard library (json, datetime, urllib.request, argparse, tempfile, os, re, sys, ctypes, fcntl).

## 3. Main Execution Flows

### Acquisition Flow
- **Pre-lock Evaluation:** Checks local file explicitly before blocking on locks.
- **Lock Acquisition:** Indefinitely waits for exclusive mutex/directory lock.
- **Post-lock Re-evaluation:** Re-reads calendar.json post-acquisition to verify if a preceding process fetched the required coverage gap.
- **Acquisition Request:** Computes exact range queries aligned strictly to 00:00:00Z full-day boundaries to satisfy sub-interval gaps. Fully missing canonical queries (--week this) directly invoke the provider semantics.
- **Provider Derivation:** Calculates the precise interval acquired by scraping the provider days length and aligns the fetched bounds appropriately. Validates payload to ensure incomplete queries reject atomic saves.
- **Commit:** Merges normalized unique events and unions coverage. Triggers strict validate_calendar_document before os.replace.

### Local Query Flow
- Reads calendar.json -> Normalizes symbol -> Extracts exact ISO 4217 FX pairs -> Discards unrelated records -> Limits chronologically via --current, --next, or nearest timestamp logic -> Dumps string array.

### Delete Flow
- Enforces strict mutual exclusion rules across delete bounding flags.
- Re-reads post-lock.
- Subtracts bounded events entirely.
- Subtracts/clips intervals inside coverage (generating sub-ranges on partial intersections).
- Validates data integrity of remaining sets before saving.
- --dry-run performs interval math, suppresses file I/O, outputs metrics to stderr.

## 4. Domain Data Structures

- CalendarDocument: Root dict schema containing schema_version, source, coverage, events.
- Coverage: Dict detailing start, end, fetched_at, and the requested criteria defining it.
- Event: Normalized explicit dict detailing event_id, canonical UTC datetime, mapped FX currency, normalized impact, structural event labels, and mutable actual/forecast parameters.

## 5. Required Functions

**CLI & Parsing:** build_argument_parser(), parse_calendar_request(), normalize_symbol(), parse_date(), parse_time(), parse_date_range()
**Provider/Network:** resolve_provider_period(), fetch_calendar_source(), extract_days_payload(), parse_calendar_days()
**Normalization:** normalize_provider_event(), normalize_calendar_events()
**Persistence:** build_empty_calendar_document(), validate_calendar_document(), load_calendar_document(), save_calendar_atomic(), acquire_calendar_lock()
**Coverage & Merge:** resolve_coverage(), find_uncovered_intervals(), merge_coverage(), deduplicate_calendar_events(), merge_calendar_events(), get_interval_for_period()
**Queries & Filters:** extract_symbol_currencies(), filter_events_for_symbol(), query_symbol_events(), query_current_events(), query_next_events(), query_nearest_events(), output_query_result()
**Deletion:** select_delete_interval(), get_deleted_ranges(), delete_events(), delete_coverage(), dry_run_delete()
**Orchestration:** run_acquisition(), run_query(), run_delete(), run(), main()
