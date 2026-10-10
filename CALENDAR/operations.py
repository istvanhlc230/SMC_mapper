# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar acquisition, refresh and deletion workflows."""

import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from time import perf_counter
from typing import Any, Dict, List, Optional, Tuple

from . import domain, providers, storage
from .config import ProviderError, YahooForexPairUnavailable

# Operation state is request-local: acquisition/refresh variables describe the current transaction and are persisted only through storage.

def _fetch_provider_events(provider: str, symbol: str, start: datetime, end: datetime, **kwargs) -> List[Dict[str, Any]]:
    """Fetch normalized events through the common Calendar provider interface."""
    return providers.get_calendar_provider(provider).fetch_events(symbol, start, end, **kwargs)


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
    document_updated = False
    acquired_event_ids: set[str] = set()
    for provider in domain.resolve_applicable_providers(symbol):
        try:
            gaps = domain.find_uncovered_intervals(document, provider, symbol, start, end)
            if not gaps:
                provider_results.append({"provider": provider, "status": "OK", "events_acquired": 0, "coverage": "CACHED"})
                successful += 1
                continue
            events: List[Dict[str, Any]] = []
            detail_failures: List[str] = []
            unresolved_event_time_ids: List[str] = []
            unresolved_event_currency_ids: List[str] = []
            for gap_start, gap_end in gaps:
                if provider == "forexfactory":
                    gap_events = _fetch_provider_events(
                        provider,
                        symbol,
                        gap_start,
                        gap_end,
                        detail_failures=detail_failures,
                        unresolved_event_time_ids=unresolved_event_time_ids,
                    )
                elif provider == "lse":
                    gap_events = _fetch_provider_events(
                        provider,
                        symbol,
                        gap_start,
                        gap_end,
                        unresolved_event_currency_ids=unresolved_event_currency_ids,
                    )
                else:
                    gap_events = _fetch_provider_events(provider, symbol, gap_start, gap_end)
                gap_events = domain.filter_events_for_interval(gap_events, gap_start, gap_end)
                events.extend(gap_events)
            failed_detail_ids = {f"forexfactory:{item}" for item in detail_failures}
            # Record canonical events actually supported by this provider response.
            # The shared merge key maps provider IDs to the canonical ID for a shared
            # economic event, allowing fresh data through even if coverage is partial.
            incoming_event_ids = {event["event_id"] for event in events}
            incoming_economic_keys = {
                domain._event_merge_key(event)
                for event in events
                if event["event_type"] == "economic"
            }
            domain.merge_events(
                document,
                events,
                clear_suppressed_symbol=symbol,
                preserve_detail_failure_ids=failed_detail_ids,
            )
            acquired_event_ids.update(incoming_event_ids)
            acquired_event_ids.update(
                event["event_id"]
                for event in document["events"]
                if event["event_type"] == "economic"
                and domain._event_merge_key(event) in incoming_economic_keys
            )
            if events:
                document_updated = True
            has_partial_provider_data = bool(
                detail_failures or unresolved_event_time_ids or unresolved_event_currency_ids
            )
            status = "PARTIAL" if has_partial_provider_data else "OK"
            coverage_status = "PARTIAL" if has_partial_provider_data else "COMPLETE"
            if unresolved_event_time_ids and debug:
                print(
                    "DEBUG | forexfactory skipped "
                    f"{len(unresolved_event_time_ids)} event row(s) without a concrete time; "
                    "the provider interval remains PARTIAL.",
                    file=sys.stderr,
                )
            if unresolved_event_currency_ids and debug:
                print(
                    "DEBUG | lse skipped "
                    f"{len(unresolved_event_currency_ids)} event row(s) with unrecognized currency/region; "
                    "the provider interval remains PARTIAL.",
                    file=sys.stderr,
                )
            if start < now:
                for gap_start, gap_end in gaps:
                    domain.merge_coverage(document, {
                        "provider": provider,
                        "symbol": symbol,
                        "start": domain.format_iso8601(gap_start),
                        "end": domain.format_iso8601(gap_end),
                        "status": coverage_status,
                        "updated_at": domain.format_iso8601(now),
                    })
                    document_updated = True
            if not has_partial_provider_data:
                if start < now:
                    domain.update_watermark(document, provider, symbol, min(end, now), events)
                successful += 1
            provider_results.append({
                "provider": provider,
                "status": "NO_MATCH" if provider == "yahoo_finance" and not events else status,
                "events_acquired": len(events),
                "coverage": "UPDATED",
                **({"detail_failures": len(detail_failures)} if detail_failures else {}),
                **({"unresolved_event_times": len(unresolved_event_time_ids)} if unresolved_event_time_ids else {}),
                **({"unresolved_event_currencies": len(unresolved_event_currency_ids)} if unresolved_event_currency_ids else {}),
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
    if successful or document_updated:
        # Persist partial events and PARTIAL coverage too. Otherwise a response
        # containing useful timed events plus untimeable rows could be discarded
        # when all other providers are unavailable.
        domain.validate_calendar_document(document)
        storage.save_calendar_atomic(document)
        if debug:
            print(f"DEBUG | Persisted Calendar file: {storage.CALENDAR_FILE}", file=sys.stderr)
    return {
        "provider_results": provider_results,
        "failures": failures,
        "acquired_event_ids": sorted(acquired_event_ids),
    }


def delete_symbol_interval(
    document: Dict[str, Any],
    symbol: str,
    start: datetime,
    end: datetime,
) -> None:
    """Internal helper: Fetch provider events."""
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
            event["symbol"] == symbol
            and "yahoo_finance" in event.get("sources", [event["source"]])
        ):
            # Yahoo news is owned by one canonical symbol, so it can be deleted.
            continue

        if (
            event["event_type"] == "economic"
            and set(event.get("sources", [event["source"]])).intersection({"lse", "forexfactory"})
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
    """Internal helper: Refresh provider window."""
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
    """Refresh all provider facts for the requested interval without changing coverage."""
    refresh_window_start, refresh_window_end = _refresh_provider_window(start, end)
    existing_events = domain.filter_events_for_interval(
        domain.filter_events_for_symbol(document["events"], symbol),
        refresh_window_start,
        refresh_window_end,
    )
    existing_ids = {event["event_id"] for event in existing_events}
    refreshed_for_symbol: List[Dict[str, Any]] = []
    reported_events: List[Dict[str, Any]] = []
    refresh_detail_failure_ids: set[str] = set()
    provider_results: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    applicable_providers = domain.resolve_applicable_providers(symbol)

    def fetch_provider_snapshot(
        provider: str,
    ) -> Tuple[List[Dict[str, Any]], List[str], List[str], float]:
        """Fetch one provider's base events and retain timing/partial-row metadata."""
        fetch_started_at = perf_counter()
        unresolved_event_time_ids: List[str] = []
        unresolved_event_currency_ids: List[str] = []
        if provider == "forexfactory":
            fetched = _fetch_provider_events(
                provider,
                symbol,
                refresh_window_start,
                refresh_window_end,
                include_details=False,
                unresolved_event_time_ids=unresolved_event_time_ids,
            )
        elif provider == "lse":
            fetched = _fetch_provider_events(
                provider,
                symbol,
                refresh_window_start,
                refresh_window_end,
                unresolved_event_currency_ids=unresolved_event_currency_ids,
            )
        else:
            fetched = _fetch_provider_events(
                provider,
                symbol,
                refresh_window_start,
                refresh_window_end,
            )
        return (
            fetched,
            unresolved_event_time_ids,
            unresolved_event_currency_ids,
            perf_counter() - fetch_started_at,
        )

    # Provider base requests are independent. Run them concurrently so their
    # network latency overlaps instead of accumulating serially.
    with ThreadPoolExecutor(
        max_workers=max(1, len(applicable_providers)),
        thread_name_prefix="calendar-provider",
    ) as provider_executor:
        provider_futures = {
            provider: provider_executor.submit(fetch_provider_snapshot, provider)
            for provider in applicable_providers
        }

    for provider in applicable_providers:
        try:
            (
                fetched,
                unresolved_event_time_ids,
                unresolved_event_currency_ids,
                fetch_elapsed,
            ) = provider_futures[provider].result()
            if debug:
                print(
                    f"DEBUG | {provider} base fetch completed in {fetch_elapsed:.2f}s "
                    f"({len(fetched)} event(s)).",
                    file=sys.stderr,
                )
            if unresolved_event_time_ids and debug:
                print(
                    "DEBUG | forexfactory skipped "
                    f"{len(unresolved_event_time_ids)} event row(s) without a concrete time; "
                    "the provider interval remains PARTIAL.",
                    file=sys.stderr,
                )
            if unresolved_event_currency_ids and debug:
                print(
                    "DEBUG | lse skipped "
                    f"{len(unresolved_event_currency_ids)} event row(s) with unrecognized currency/region; "
                    "the provider interval remains PARTIAL.",
                    file=sys.stderr,
                )
            fetched_for_symbol = domain.filter_events_for_symbol(fetched, symbol)
            selected = [
                event for event in fetched_for_symbol
                if start <= domain.parse_iso8601(event["timestamp"]) < end
                or event["event_id"] in existing_ids
            ]
            detail_failures: List[str] = []
            if provider == "forexfactory":
                detail_failures = providers._enrich_forexfactory_details(selected) or []
                refresh_detail_failure_ids.update(
                    f"forexfactory:{item}" for item in detail_failures
                )
            refreshed_for_symbol.extend(selected)
            for event in selected:
                existing = next((item for item in existing_events if item["event_id"] == event["event_id"]), None)
                if existing is None or existing["timestamp"] != event["timestamp"]:
                    reported_events.append(event)
            has_partial_provider_data = bool(
                detail_failures or unresolved_event_time_ids or unresolved_event_currency_ids
            )
            provider_results.append({
                "provider": provider,
                "status": "PARTIAL" if has_partial_provider_data else ("NO_MATCH" if not selected else "OK"),
                "events_fetched": len(fetched),
                "events_refreshed": len(selected),
                **({"detail_failures": len(detail_failures)} if detail_failures else {}),
                **({"unresolved_event_times": len(unresolved_event_time_ids)} if unresolved_event_time_ids else {}),
                **({"unresolved_event_currencies": len(unresolved_event_currency_ids)} if unresolved_event_currency_ids else {}),
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

    if not refreshed_for_symbol and failures:
        return {"events": [], "provider_results": provider_results, "failures": failures,
                "summary": {"added": 0, "changed": 0, "unchanged": 0}}

    summary = _refresh_event_records(
        document,
        refreshed_for_symbol,
        symbol,
        preserve_detail_failure_ids=refresh_detail_failure_ids,
    )
    if refreshed_for_symbol and (summary["added"] or summary["changed"]):
        domain.validate_calendar_document(document)
        storage.save_calendar_atomic(document)
    return {
        "events": reported_events,
        "provider_results": provider_results,
        "failures": failures,
        "summary": summary,
    }



