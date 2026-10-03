# Calendar Implementation Design

## 1. Responsibilities and Non-Responsibilities
**Responsibilities:**
- Acquire ForexFactory economic calendar data without modifying SMC files.
- Parse provider HTML payload, normalizing to UTC and stable event_id.
- Maintain a single global calendar.json with tracking for coverage intervals.
- Provide time-based local queries for FX symbols.
- Provide explicit deterministic deletion with interval coverage update.
- Ensure atomic, locked persistence of calendar.json using an OS-level lock on a temporary .lock file.
- Fail cleanly on acquisition failures, leaving the last-known-good file intact.
- Correctly compute uncovered subintervals to minimize network requests.

**Non-Responsibilities:**
- No SMC calculation (BOS, CHoCH, IDM, Dealing Range, POI, etc.).
- No generation of symbol-specific News JSON.
- No automatic retention or cleanup (only explicit --delete).
- No evaluation of setup validity or trading decisions.
- Monitor execution policy does not belong in this module.

## 2. Boundaries and Dependencies
- **Inputs:** CLI arguments, ForexFactory HTML response, existing calendar.json.
- **Outputs:** Console output (JSON format for local queries), updated calendar.json.
- **Side effects:** Atomic update of calendar.json, locking mechanism via OS-level file lock (using cntl on POSIX and msvcrt.locking on Windows over a .lock file).
- **Dependencies:** Standard library (json, datetime, urllib.request, rgparse, 	empfile, os, 
e, sys).
- **Dependency Direction:** Downstream dependencies only.

## 3. Main Execution Flows

### Acquisition Flow
`mermaid
sequenceDiagram
    participant CLI
    participant Lock
    participant FF as ForexFactory
    participant FS as FileSystem
    
    CLI->>Lock: Acquire exclusive OS lock (calendar.json.lock)
    Lock-->>CLI: Lock acquired
    CLI->>FS: Read existing calendar.json
    CLI->>CLI: Re-check if requested interval is covered
    alt Fully Covered
        CLI->>CLI: No provider request
    else Needs Data
        CLI->>CLI: Compute uncovered subintervals
        CLI->>FF: Request exact uncovered intervals via range
        FF-->>CLI: HTML payload
        CLI->>CLI: Parse, validate & normalize
        CLI->>CLI: Merge events and coverage
        CLI->>CLI: Validate complete document
        CLI->>FS: Atomic write to temporary file & replace calendar.json
    end
    CLI->>Lock: Release lock
    CLI->>CLI: Output JSON result
`

### Local Query Flow
`mermaid
flowchart TD
    Start[CLI Local Query] --> FS[Read calendar.json]
    FS --> FilterSym[Filter by Symbol Relevance]
    FilterSym --> TimeBound[Extract Current/Next/Nearest]
    TimeBound --> Output[Format and Print JSON to stdout]
`

### Delete Flow
`mermaid
flowchart TD
    Start[CLI Delete] --> ValidateArgs[Enforce Strict Boundary Arguments]
    ValidateArgs --> Lock[Acquire Lock & Read]
    Lock --> DelEvents[Filter out events outside bounds]
    DelEvents --> DelCov[Compute clipped coverage intervals]
    DelCov --> DryRun{Is Dry Run?}
    DryRun -- Yes --> Output[Print Stats/Metadata to stderr & Exit]
    DryRun -- No --> ValidateDoc[Validate Document Integrity]
    ValidateDoc --> Write[Atomic Save & Release Lock]
`

## 4. Domain Data Structures

`mermaid
classDiagram
    class CalendarDocument {
        +int schema_version
        +string source
        +List~Coverage~ coverage
        +List~Event~ events
    }
    
    class Coverage {
        +string start
        +string end
        +dict requested
        +string fetched_at
    }
    
    class Event {
        +string event_id
        +string datetime
        +string currency
        +string impact
        +string event
        +string actual
        +string forecast
        +string previous
        +string source
    }
    
    CalendarDocument "1" *-- "many" Coverage
    CalendarDocument "1" *-- "many" Event
`

## 5. Required Functions

**CLI & Parsing:**
- uild_argument_parser(): Defines args.
- parse_calendar_request(): Resolves arguments, strict mutual exclusion, invalid combinations.
- 
ormalize_symbol(): Formatting.
- parse_date(), parse_time(), parse_date_range(): Timestamp conversions, rigid formats.

**Provider/Network:**
- 
esolve_provider_period(): Maps CLI intervals to provider URL params. Rejects invalid months explicitly.
- etch_calendar_source(): HTTP GET.
- extract_days_payload(): Regex extraction of days json payload.
- parse_calendar_days(): Safely converts string to dict structure.

**Normalization:**
- 
ormalize_provider_event(): Applies UTC normalization and structure.
- 
ormalize_calendar_events(): Normalizes a list of provider events.

**Persistence:**
- uild_empty_calendar_document(): Empty state structure.
- alidate_calendar_document(): Complete structural and semantic integrity verification.
- load_calendar_document(): File IO and triggering validation. Missing returns empty, corrupt fails.
- save_calendar_atomic(): Writes via tmp file and replaces target.
- cquire_calendar_lock(): Safe ephemeral .lock generation preventing race conditions.

**Coverage & Merge:**
- 
esolve_coverage(): Consolidates/merges overlapping coverage ranges.
- ind_uncovered_intervals(): Exact calculation of missing sub-intervals based on existing coverage bounds.
- merge_coverage(): Aggregation.
- deduplicate_calendar_events(): Deduplicates events based on event_id, updating mutable properties, and enforcing strict identity/time consistency.
- merge_calendar_events(): Concatenates and deduplicates.

**Queries & Filters:**
- extract_symbol_currencies(): Exact 2-currency resolution.
- ilter_events_for_symbol(): Relevance filtering.
- query_symbol_events(): Aggregation of relevant events.
- query_current_events(), query_next_events(), query_nearest_events(): Time boundaries.

**Deletion:**
- select_delete_interval(): Parses delete filters into limits.
- get_deleted_ranges(): Turns complex ranges/times into specific boundaries.
- delete_events(): Trims event list.
- delete_coverage(): Intelligently clips/splits coverage lists.
- dry_run_delete(): Evaluates impact and prints info without disk modification.

**Orchestration:**
- 
un_acquisition(): Locking, uncovered search, fetching, merging, atomic save.
- 
un_query(): API extraction.
- 
un_delete(): Lock, delete logic, validation, atomic save.
- 
un(): Entry point.
- main(): Script init.
