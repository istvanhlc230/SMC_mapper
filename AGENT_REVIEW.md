# AGENT_REVIEW.md — Calendar/Monitor Update Engine Synchronization

Status: BLOCKED_PENDING_LOCAL_RUNTIME_VALIDATION

## Implementation changes

calendar.py was moved to Calendar V2.

Applied:
- removed today/next_day/week/next_week/month/next_month;
- removed next evaluation;
- symbol-first explicit date/datetime CLI;
- current is provider+canonical-symbol watermark incremental update;
- missing watermark is BOOTSTRAP_REQUIRED;
- added ticker support such as NVDA;
- automatic provider routing;
- common normalized event envelope;
- ForexFactory = economic;
- Yahoo Finance = news;
- provider-specific identity and dedupe;
- provider/symbol coverage;
- provider/symbol watermarks;
- provider failure isolation;
- atomic last-known-good persistence;
- no false Yahoo historical completeness.

## Specification synchronization

The same commit updates:
- specifications/calendar_specification.md
- specifications/calendar_design.md
- specifications/smc_monitor_specification.md

Monitor now launches Calendar work asynchronously and reads the committed local calendar.json without blocking canonical processing.

## Required local validation

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

Acceptance must verify:
- old relative scopes are rejected;
- next is rejected;
- current without watermark returns BOOTSTRAP_REQUIRED;
- explicit acquisition creates provider/symbol watermark state when successful;
- Yahoo events are news;
- ForexFactory events are economic;
- partial provider failure is not empty success;
- atomic write failure preserves the last committed file.

No PASS claim is made until local runtime validation is performed.
