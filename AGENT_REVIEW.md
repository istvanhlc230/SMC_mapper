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

No PASS claim until local runtime validation is complete.