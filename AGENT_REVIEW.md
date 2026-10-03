# AGENT_REVIEW.md — Calendar/Monitor Update Engine Synchronization

Status: BLOCKED_PENDING_LOCAL_RUNTIME_VALIDATION

## Follow-up audit corrections

Corrected in this iteration:

1. provider/symbol coverage union preserves prior non-overlapping intervals;
2. explicit ForexFactory acquisition reuses validated COMPLETE coverage and fetches only uncovered intervals;
3. explicit provider fetches may use provider-required day boundaries, but returned events are restricted to the exact requested interval before persistence;
4. the full pre-refactor Monitor specification is preserved outside the Calendar-related sections;
5. the Yahoo Forex reference snapshot remains documented as non-closed.

## Current contract

- old relative Calendar scopes removed;
- next removed;
- current is provider+canonical-symbol watermark based;
- missing watermark -> BOOTSTRAP_REQUIRED;
- no synthetic bootstrap timestamp;
- symbol-first explicit date/datetime syntax;
- HUF -> ForexFactory;
- FX pair -> ForexFactory + Yahoo;
- ticker such as NVDA -> Yahoo;
- Yahoo -> news;
- ForexFactory -> economic;
- provider-specific identity/deduplication;
- provider failures remain observable;
- Yahoo historical completeness is never fabricated;
- Monitor Calendar acquisition is asynchronous and non-blocking for canonical processing.

## Validation

Required deterministic checks:

    python -m py_compile calendar.py
    python calendar.py --help
    python calendar.py EURUSD 2026.10.01
    python calendar.py EURUSD 2026.10.01-2026.10.31
    python calendar.py EURUSD 2026.10.01@10:00
    python calendar.py EURUSD 2026.10.01@10:00-2026.10.31@22:00
    python calendar.py EURUSD current
    python calendar.py NVDA current
    python calendar.py HUF 2026.10.01
    python calendar.py delete

Negative checks must reject:
    python calendar.py today USDHUF
    python calendar.py EURUSD next
    python calendar.py EURUSD 2026.10.01..2026.10.31

Behavioral checks must verify:
- current without watermark -> BOOTSTRAP_REQUIRED;
- cached COMPLETE ForexFactory coverage is not refetched;
- non-overlapping coverage remains preserved;
- datetime queries persist only events inside their requested interval;
- one-provider failure plus one-provider success -> PARTIAL;
- all-provider failure -> UNAVAILABLE;
- Monitor Calendar dispatch is non-blocking.

No PASS claim until local runtime validation confirms these conditions.