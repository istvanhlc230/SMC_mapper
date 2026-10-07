# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar acquisition, refresh and deletion workflows."""

import sys
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from . import domain, providers, storage
from .config import ProviderError, YahooForexPairUnavailable

# Operation state is request-local: acquisition/refresh variables describe the current transaction and are persisted only through storage.

def _fetch_provider_events(provider: str, symbol: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Fetch normalized events from one provider adapter."""
    if provider == "lse":
        return providers.fetch_lse_calendar(symbol, start, end)
    if provider == "forexfactory":
        return providers.fetch_forexfactory(symbol, start, end) if False else providers.fetch_forexfactory(start, end)
    if provider == "yahoo_finance":
        return providers.fetch_yahoo_news(symbol)
    raise ProviderError(f"Unsupported Calendar provider: {provider}")


def acquire_explicit(
    document: Dict[str, Any],
    symbol: str,
    start: datetime,
    end: datetime,
    debug: bool = False,
) -> Dict[str, Any]:
    """Acquire all applicable provider sources and merge their facts."""
    now = domain.utc_now()
    provider_results: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []
    successful = 0
    for provider in domain.resolve_applicable_providers(symbol):
        try:
            gaps = domain.find_uncovered_intervals(document, provider, symbol, start, end)
            if not gaps:
                provider_results.append({"provider": provider, "status": "OK", "events_acquired": 0, "coverage": "CACHED"})
                successful += 1
                continue
            events: List[Dict[str, Any]] = []
            detail_failures: List[str] = []
            for gap_start, gap_end in gaps:
                if provider == "forexfactory":
                    gap_events = providers.fetch_forexfactory(gap_start, gap_end, detail_failures=detail_failures)
                else:
                    gap_events = _fetch_provider_events(provider, symbol, gap_start, gap_end)
                events.extend(gap_events)
            failed_detail_ids = {f"forexfactory:{item}" for item in detail_failures}
            domain.merge_events(
                document,
                events,
                clear_suppressed_symbol=symbol,
                preserve_detail_failure_ids=failed_detail_ids,
            )
            status = "PARTIAL" if detail_failures else "OK"
            for gap_start, gap_end in gaps:
                domain.merge_coverage(document, {
                    "provider": provider,
                    "symbol": symbol,
                    "start": domain.format_iso8601(gap_start),
                    "end": domain.format_iso8601(gap_end),
                    "status": status,
                    "updated_at": domain.format_iso8601(now),
                })
            if not detail_failures:
                domain.update_watermark(document, provider, symbol, now, events)
                successful += 1
            provider_results.append({
                "provider": provider,
                "status": status,
                "events_acquired": len(events),
                "coverage": "UPDATED",
                **({"detail_failures": len(detail_failures)} if detail_failures else {}),
            })
        except YahooForexPairUnavailable as exc:
            if debug:
                print(f"DEBUG | {provider} YahooForexPairUnavailable: {exc}", file=sys.stderr)
            provider_results.append({"provider": provider, "status": "SKIPPED_NO_FOREX_PAIR", "reason": str(exc)})
        except ProviderError as exc:
            if debug:
                print(f"DEBUG | {provider} ProviderError traceback:", file=sys.stderr)
                traceback.print_exc()
            failures.append({"provider": provider, "error": str(exc)})
            provider_results.append({"provider": provider, "status": "ERROR", "error": str(exc)})
    if successful:
        domain.validate_calendar_document(document)
        storage.save_calendar_atomic(document)
        if debug:
            print(f"DEBUG | Persisted Calendar file: {storage.CALENDAR_FILE}", file=sys.stderr)
    return {"provider_results": provider_results, "failures": failures}


def delete_symbol_interval(
    document: Dict[str, Any],
    symbol: str,
    start: datetime,
    end: datetime,
) -> None:
    """Calendar operation: delete_symbol_interval performs the focused delete symbol interval step in the Calendar implementation."""
    applicable_providers = set(domain.resolve_applicable_providers(symbol))
    currencies = ({symbol} if domain.is_currency(symbol) else
                  {symbol[:3], symbol[3:]} if domain.is_fx_pair(symbol) else set())

    retained_events: List[Dict[str, Any]] = []
    for event in document["events"]:
        timestamp = domain.parse_iso8601(event["timestamp"])
        if timestamp < start or timestamp >= end:
            retained_events.append(event)
            continue

        if (
            event["source"] == "yahoo_finance"
            and event["symbol"] == symbol
            and "yahoo_finance" in applicable_providers
        ):
            # Yahoo news is owned by one canonical symbol, so it can be deleted.
            continue

        if (
            event["source"] == "forexfactory"
            and "forexfactory" in applicable_providers
            and event["details"].get("currency") in currencies
        ):
            # ForexFactory facts are shared. Record a symbol-level suppression
            # instead of deleting the provider fact for every other FX symbol.
            suppressed = set(event.get("suppressed_for", []))
            suppressed.add(symbol)
            updated = event.copy()
            updated["suppressed_for"] = sorted(suppressed)
            retained_events.append(updated)
            continue

        retained_events.append(event)

    document["events"] = retained_events

    retained_coverage: List[Dict[str, Any]] = []
    for coverage in document["coverage"]:
        if (
            coverage["symbol"] != symbol
            or coverage["provider"] not in applicable_providers
        ):
            retained_coverage.append(coverage)
            continue

        coverage_start = domain.parse_iso8601(coverage["start"])
        coverage_end = domain.parse_iso8601(coverage["end"])
        if end <= coverage_start or start >= coverage_end:
            retained_coverage.append(coverage)
            continue

        if coverage_start < start:
            left = coverage.copy()
            left["end"] = domain.format_iso8601(start)
            retained_coverage.append(left)

        if end < coverage_end:
            right = coverage.copy()
            right["start"] = domain.format_iso8601(end)
            retained_coverage.append(right)

    document["coverage"] = retained_coverage

    for provider in applicable_providers:
        key = domain.watermark_key(provider, symbol)
        watermark = document["watermarks"].get(key)
        if watermark is None:
            continue
        last_event_timestamp = watermark.get("last_event_timestamp")
        if last_event_timestamp is None:
            continue
        last_event = domain.parse_iso8601(last_event_timestamp)
        if start <= last_event < end:
            del document["watermarks"][key]

def _refresh_provider_window(
    start: datetime,
    end: datetime,
) -> Tuple[datetime, datetime]:
    """Internal helper: _refresh_provider_window performs the focused refresh provider window step in the Calendar implementation."""
    expanded_start = (
        start.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    )
    expanded_end = (
        (end - timedelta(microseconds=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=2)
    )
    return expanded_start, expanded_end

# changed event records without treating provider timestamp changes as identity conflicts.
# symbol=canonical symbol used for suppression ownership.
# normalized=merged record; refreshed_ids=stable IDs; unchanged=unchanged existing records.

def _refresh_event_records(
    document: Dict[str, Any],
    refreshed_events: List[Dict[str, Any]],
    symbol: str,
    preserve_detail_failure_ids: Optional[set[str]] = None,
) -> Dict[str, int]:
    """Compare and merge refreshed records without destroying good Detail data."""
    # by_id is the committed event snapshot keyed by stable provider event ID.
    by_id = {event["event_id"]: event for event in document["events"]}
    # Failed Detail IDs identify records whose new Detail payload was unavailable.
    failed_detail_ids = preserve_detail_failure_ids or set()
    changed = 0
    added = 0
    unchanged = 0

    for event in refreshed_events:
        event_id = event["event_id"]
        old = by_id.get(event_id)
        normalized = event.copy()

        # A failed Detail refresh returns an empty specs list. Keep the prior
        # non-empty list while accepting all other freshly fetched fields.
        if (
            event_id in failed_detail_ids
            and old is not None
            and old.get("details", {}).get("specs")
            and not normalized.get("details", {}).get("specs")
        ):
            normalized["details"] = normalized.get("details", {}).copy()
            normalized["details"]["specs"] = old["details"]["specs"]

        # suppressed_for is symbol-scoped visibility metadata and survives a
        # refresh except for the symbol whose facts were successfully reacquired.
        inherited = set(old.get("suppressed_for", [])) if old else set()
        incoming = set(normalized.get("suppressed_for", []))
        suppressed = inherited | incoming
        suppressed.discard(symbol)
        if suppressed:
            normalized["suppressed_for"] = sorted(suppressed)
        else:
            normalized.pop("suppressed_for", None)

        if old is None:
            added += 1
        elif old == normalized:
            unchanged += 1
        else:
            changed += 1

        by_id[event_id] = normalized

    # Keep event ordering deterministic for stable persistence and audit diffs.
    document["events"] = sorted(
        by_id.values(),
        key=lambda item: (
            domain.parse_iso8601(item["timestamp"]),
            item["source"],
            item["event_id"],
        ),
    )
    return {
        "added": added,
        "changed": changed,
        "unchanged": unchanged,
    }

def refresh_current_scope(
    document: Dict[str, Any],
    symbol: str,
    debug: bool = False,
) -> Dict[str, Any]:
    """Force-refresh the provider interval represented by the current scope."""
    now = domain.utc_now()
    # Current refresh follows the earliest applicable watermark so it refreshes
    # the same incremental timespan that a current cache query represents.
    watermark_times: List[datetime] = []
    for provider in domain.resolve_applicable_providers(symbol):
        watermark = document["watermarks"].get(
            domain.watermark_key(provider, symbol)
        )
        if watermark and watermark.get("last_successful_at"):
            watermark_times.append(
                domain.parse_iso8601(watermark["last_successful_at"])
            )

    # First-use current has no prior cursor; use a bounded one-day interval ending now.
    refresh_start = (
        min(watermark_times)
        if watermark_times
        else now - timedelta(days=1)
    )
    refresh_end = now

    return refresh_calendar_scope(
        document,
        symbol,
        refresh_start,
        refresh_end,
        debug=debug,
    )
def refresh_calendar_scope(
    document: Dict[str, Any],
    symbol: str,
    start: datetime,
    end: datetime,
    debug: bool = False,
) -> Dict[str, Any]:
    """Calendar operation: refresh_calendar_scope performs the focused refresh calendar scope step in the Calendar implementation."""
    refresh_window_start, refresh_window_end = _refresh_provider_window(start, end)
    # Existing IDs are collected from the provider-side envelope, not only the
    # logical query interval, so late mutable Detail data on an event just outside
    # the incremental boundary can still be refreshed by stable provider identity.
    existing_events = domain.filter_events_for_interval(
        domain.filter_events_for_symbol(document["events"], symbol),
        refresh_window_start,
        refresh_window_end,
    )
    existing_ids = {event["event_id"] for event in existing_events}
    # logical_existing_ids identify records that were already visible in the
    # requested query interval; these may be returned even when the provider
    # reschedules them outside the interval during refresh.
    logical_existing_events = domain.filter_events_for_interval(
        domain.filter_events_for_symbol(document["events"], symbol),
        start,
        end,
    )
    logical_existing_ids = {
        event["event_id"] for event in logical_existing_events
    }
    # refreshed_for_symbol collects selected provider records that may replace or add cache entries.
    refreshed_for_symbol: List[Dict[str, Any]] = []
    # refresh_detail_failure_ids records stable IDs whose Detail retrieval failed.
    refresh_detail_failure_ids: set[str] = set()
    provider_results: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    for provider in domain.resolve_applicable_providers(symbol):
        try:
            if provider == "forexfactory":
                fetched = providers.fetch_forexfactory(
                    refresh_window_start,
                    refresh_window_end,
                    include_details=False,
                )
            else:
                fetched = providers.fetch_yahoo_news(symbol)

            fetched_for_symbol = domain.filter_events_for_symbol(fetched, symbol)
            selected = [
                event for event in fetched_for_symbol
                if (
                    start <= domain.parse_iso8601(event["timestamp"]) < end
                    or event["event_id"] in existing_ids
                )
            ]
            detail_failures: List[str] = []
            if provider == "forexfactory":
                # Preserve the stable event IDs of failed Detail requests for the merge stage.
                # A provider helper may return no failure collection when all Detail work succeeded;
                # normalize that case to an empty set before recording failed IDs.
                detail_failures = providers._enrich_forexfactory_details(selected) or []
                refresh_detail_failure_ids.update(
                    f"forexfactory:{provider_event_id}"
                    for provider_event_id in detail_failures
                )

            refreshed_for_symbol.extend(selected)
            provider_results.append({
                "provider": provider,
                "status": (
                    "PARTIAL"
                    if detail_failures
                    else ("NO_MATCH" if not selected else "OK")
                    if provider == "yahoo_finance"
                    else "OK"
                ),
                "events_fetched": len(fetched),
                "events_refreshed": len(selected),
                **({"detail_failures": len(detail_failures)} if detail_failures else {}),
            })
        except YahooForexPairUnavailable as exc:
            if debug:
                print(
                    f"DEBUG | {provider} YahooForexPairUnavailable: {exc}",
                    file=sys.stderr,
                )
            provider_results.append({
                "provider": provider,
                "status": "SKIPPED_NO_FOREX_PAIR",
                "reason": str(exc),
            })
        except ProviderError as exc:
            if debug:
                print(
                    f"DEBUG | {provider} ProviderError traceback:",
                    file=sys.stderr,
                )
                traceback.print_exc()
            failures.append({"provider": provider, "error": str(exc)})
            provider_results.append({
                "provider": provider,
                "status": "ERROR",
                "error": str(exc),
            })

    if not refreshed_for_symbol and failures:
        return {
            "events": [],
            "provider_results": provider_results,
            "failures": failures,
            "summary": {"added": 0, "changed": 0, "unchanged": 0},
        }

    # Refresh is deliberately not a coverage/watermark operation. It only
    # updates provider facts already in or newly discovered for the requested scope.
    summary = _refresh_event_records(
        document,
        refreshed_for_symbol,
        symbol,
        preserve_detail_failure_ids=refresh_detail_failure_ids,
    )
    if refreshed_for_symbol and (
        summary["added"] or summary["changed"]
    ):
        domain.validate_calendar_document(document)
        storage.save_calendar_atomic(document)
        if debug:
            print(
                f"DEBUG | Persisted Calendar file: {storage.CALENDAR_FILE}",
                file=sys.stderr,
            )

    refreshed_ids = {event["event_id"] for event in refreshed_for_symbol}
    # Overlap-only records are merged silently. A record is returned when its
    # refreshed timestamp is inside the logical scope or its stable ID belonged
    # to an existing event already visible in that scope before refresh.
    refreshed_visible = [
        event
        for event in domain.filter_events_for_symbol(document["events"], symbol)
        if (
            event["event_id"] in refreshed_ids
            and (
                start <= domain.parse_iso8601(event["timestamp"]) < end
                or event["event_id"] in logical_existing_ids
            )
        )
    ]
    refreshed_visible.sort(
        key=lambda event: (
            domain.parse_iso8601(event["timestamp"]),
            event["source"],
            event["event_id"],
        )
    )

    return {
        "events": refreshed_visible,
        "provider_results": provider_results,
        "failures": failures,
        "summary": summary,
    }

# debug=diagnostic flag.
