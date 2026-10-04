"""External Calendar providers and provider-specific normalization."""

import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from .config import (FOREXFACTORY_DETAIL_URL, FOREXFACTORY_URL, FX_CURRENCY_CODES, HTTP_TIMEOUT, YAHOO_SEARCH_URL, USER_AGENT, USD_BASE_YAHOO_SYMBOLS, CalendarInputError, ProviderError, YahooForexPairUnavailable)
from .domain import format_iso8601, is_currency, is_fx_pair, normalize_symbol, parse_iso8601
from .parsing import extract_days_payload, parse_calendar_days, parse_forexfactory_html_events

# Provider state is request-local: fetched payloads, normalized events, and Detail failures stay inside the active acquisition call.

def _fetch_yahoo_search_payload(query_symbol: str) -> Dict[str, Any]:
    """Internal helper: _fetch_yahoo_search_payload performs the focused fetch yahoo search payload step in the Calendar implementation."""
    params = {
        "q": query_symbol,
        "quotesCount": "20",
        "newsCount": "100",
        "enableFuzzyQuery": "false",
    }
    query = urllib.parse.urlencode(params)
    payload = fetch_url(f"{YAHOO_SEARCH_URL}?{query}")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Malformed Yahoo Finance JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ProviderError("Yahoo Finance response is not an object.")
    return data

def _is_verified_yahoo_forex_quote(
    """Internal helper: _is_verified_yahoo_forex_quote performs the focused is verified yahoo forex quote step in the Calendar implementation."""
    quote: Dict[str, Any],
    candidate_symbol: str,
) -> bool:
    returned_symbol = normalize_symbol(str(quote.get("symbol", "")))
    quote_type = normalize_symbol(str(quote.get("quoteType", "")))
    type_display = str(quote.get("typeDisp", "")).strip().lower()
    return (
        returned_symbol == normalize_symbol(candidate_symbol)
        and (
            quote_type == "CURRENCY"
            or type_display == "currency"
        )
    )

def _resolve_yahoo_instrument(
    """Internal helper: _resolve_yahoo_instrument performs the focused resolve yahoo instrument step in the Calendar implementation."""
    symbol: str,
) -> Tuple[str, Dict[str, Any]]:
    if not is_fx_pair(symbol):
        return symbol, _fetch_yahoo_search_payload(symbol)

    candidates: List[str] = []
    mapped = USD_BASE_YAHOO_SYMBOLS.get(symbol)
    if mapped:
        candidates.append(mapped)

    # Yahoo commonly represents USD-base FX pairs as the quote currency's
    # =X instrument (for example GBP=X for USDGBP). This is only a
    # provider candidate; it must still be verified by Yahoo Search.
    if symbol.startswith("USD") and len(symbol) == 6:
        derived_usd_base = f"{symbol[3:]}=X"
        if derived_usd_base not in candidates:
            candidates.append(derived_usd_base)

    direct = f"{symbol}=X"
    if direct not in candidates:
        candidates.append(direct)

    queried: set[str] = set()
    for candidate in candidates:
        for query_symbol in (candidate, symbol):
            if query_symbol in queried:
                continue
            queried.add(query_symbol)
            data = _fetch_yahoo_search_payload(query_symbol)
            quotes = data.get("quotes", [])
            if not isinstance(quotes, list):
                continue
            for quote in quotes:
                if not isinstance(quote, dict):
                    continue
                if _is_verified_yahoo_forex_quote(quote, candidate):
                    return candidate, data

    raise YahooForexPairUnavailable(
        f"Yahoo Finance has no verified Forex instrument for '{symbol}'."
    )

def resolve_yahoo_symbol(symbol: str) -> Optional[str]:
    """Calendar operation: resolve_yahoo_symbol performs the focused resolve yahoo symbol step in the Calendar implementation."""
    try:
        provider_symbol, _ = _resolve_yahoo_instrument(symbol)
    except YahooForexPairUnavailable:
        return None
    return provider_symbol

def fetch_url(url: str) -> str:
    """Calendar operation: fetch_url performs the focused fetch url step in the Calendar implementation."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            if response.status != 200:
                raise ProviderError(f"HTTP {response.status}")
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, UnicodeDecodeError, OSError) as exc:
        raise ProviderError(str(exc)) from exc

def _forexfactory_date_token(value: datetime) -> str:
    """Internal helper: _forexfactory_date_token performs the focused forexfactory date token step in the Calendar implementation."""
    month = value.strftime("%b").lower()
    day = value.day
    year = value.year
    return f"{month}{day}.{year}"

def build_forexfactory_query(start: datetime, end: datetime) -> str:
    """Calendar operation: build_forexfactory_query performs the focused build forexfactory query step in the Calendar implementation."""
    if end <= start:
        raise CalendarInputError("ForexFactory query interval must have a positive duration.")

    first_day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    last_day = (end - timedelta(microseconds=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if first_day == last_day:
        query = {"day": _forexfactory_date_token(first_day)}
    else:
        query = {
            "range": (
                f"{_forexfactory_date_token(first_day)}-"
                f"{_forexfactory_date_token(last_day)}"
            )
        }
    return urllib.parse.urlencode(query)

def fetch_forexfactory(
    """Calendar operation: fetch_forexfactory performs the focused fetch forexfactory step in the Calendar implementation."""
    start: datetime,
    end: datetime,
    include_details: bool = True,
    detail_failures: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    request_start = start
    request_end = end
    provider_start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    provider_end = end.replace(hour=0, minute=0, second=0, microsecond=0)
    if provider_end < end:
        provider_end += timedelta(days=1)
    query = build_forexfactory_query(provider_start, provider_end)
    html = fetch_url(f"{FOREXFACTORY_URL}?{query}")
    try:
        days = parse_calendar_days(extract_days_payload(html))
        normalized = normalize_calendar_events(days)
    except ProviderError:
        fallback_raw = parse_forexfactory_html_events(
            html,
            request_start,
            request_end,
        )
        normalized = [
            normalize_provider_event(raw_event)
            for raw_event in fallback_raw
        ]

    normalized = [
        event for event in normalized
        if request_start <= parse_iso8601(event["timestamp"]) < request_end
    ]

    # ForexFactory Detail is provider data, not a canonical event URL.
    # Detail enrichment can be disabled for discovery-only refresh acquisition.
    if include_details:
        failures = _enrich_forexfactory_details(normalized)
        if detail_failures is not None:
            detail_failures.extend(failures)

    return normalized

def _enrich_forexfactory_details(
    """Internal helper: _enrich_forexfactory_details performs the focused enrich forexfactory details step in the Calendar implementation."""
    events: List[Dict[str, Any]],
) -> List[str]:
    """Best-effort FF detail enrichment; return provider IDs that failed."""
    def fetch_detail(event: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """Calendar operation: fetch_detail performs the focused fetch detail step in the Calendar implementation."""
        provider_event_id = event["event_id"].split(":", 1)[1]
        return provider_event_id, fetch_forexfactory_event_detail(provider_event_id)

    if not events:
        return []

    max_workers = min(6, len(events))
    failures: List[str] = []
    with ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="ff-detail",
    ) as executor:
        futures = [
            (event, executor.submit(fetch_detail, event))
            for event in events
        ]
        for event, future in futures:
            provider_event_id = event["event_id"].split(":", 1)[1]
            try:
                _, specs = future.result()
            except Exception:
                # Detail enrichment must never invalidate successfully fetched
                # base calendar events. Provider-specific failures are isolated
                # to the affected event.
                event["details"]["specs"] = []
                failures.append(provider_event_id)
            else:
                event["details"]["specs"] = specs

    return failures

def fetch_forexfactory_event_detail(event_id: str) -> List[Dict[str, Any]]:
    """Calendar operation: fetch_forexfactory_event_detail performs the focused fetch forexfactory event detail step in the Calendar implementation."""
    event_id = str(event_id).strip()
    if not re.fullmatch(r"\d+", event_id):
        raise ProviderError("ForexFactory event detail has an invalid provider ID.")

    payload = fetch_url(
        FOREXFACTORY_DETAIL_URL.format(event_id=event_id)
    )
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(
            f"Malformed ForexFactory detail JSON for event {event_id}: {exc}"
        ) from exc

    if not isinstance(data, dict) or not isinstance(data.get("data"), dict):
        raise ProviderError(
            f"Malformed ForexFactory detail response for event {event_id}."
        )

    specs = data["data"].get("specs", [])
    if not isinstance(specs, list):
        raise ProviderError(
            f"ForexFactory detail specs are not a list for event {event_id}."
        )

    normalized: List[Dict[str, Any]] = []
    for spec in specs:
        if not isinstance(spec, dict):
            raise ProviderError(
                f"Malformed ForexFactory detail specification for event {event_id}."
            )
        if "order" not in spec or "title" not in spec or "html" not in spec:
            raise ProviderError(
                f"Malformed ForexFactory detail specification for event {event_id}."
            )
        if isinstance(spec["order"], bool):
            raise ProviderError(
                f"Invalid ForexFactory detail spec order for event {event_id}."
            )
        try:
            order = int(spec["order"])
        except (TypeError, ValueError) as exc:
            raise ProviderError(
                f"Invalid ForexFactory detail spec order for event {event_id}."
            ) from exc
        title = str(spec["title"]).strip()
        html_value = spec["html"]
        if not title or not isinstance(html_value, str):
            raise ProviderError(
                f"Malformed ForexFactory detail specification for event {event_id}."
            )
        normalized.append({
            "order": order,
            "title": title,
            "html": html_value,
        })

    # The provider response sequence is authoritative. The numeric order value
    # is metadata, not a local sorting key.
    return normalized

def _resolve_impact(raw: Dict[str, Any]) -> str:
    """Normalize explicit ForexFactory impact metadata without title inference."""
    impact_text = ""
    for field_name in ("impactTitle", "impactName", "impact"):
        candidate = str(raw.get(field_name, "")).strip()
        if candidate:
            impact_text = candidate.lower()
            break

    normalized_text = re.sub(r"[^a-z]+", " ", impact_text).strip()
    if re.search(r"\bhigh\b", normalized_text):
        return "HIGH"
    if re.search(r"\b(?:med|medium)\b", normalized_text):
        return "MEDIUM"
    if re.search(r"\blow\b", normalized_text):
        return "LOW"
    if "non economic" in normalized_text or "holiday" in normalized_text:
        return "HOLIDAY"

    impact_class = str(raw.get("impactClass", "")).strip().lower()
    class_tokens = re.sub(r"[^a-z]+", " ", impact_class).strip()
    if "red" in class_tokens or "high" in class_tokens:
        return "HIGH"
    if "orange" in class_tokens or re.search(r"\bora\b", class_tokens) or "medium" in class_tokens or re.search(r"\bmed\b", class_tokens):
        return "MEDIUM"
    if "yellow" in class_tokens or re.search(r"\byel\b", class_tokens) or "green" in class_tokens or re.search(r"\bgrn\b", class_tokens) or "low" in class_tokens:
        return "LOW"
    if "grey" in class_tokens or "gray" in class_tokens or re.search(r"\bgry\b", class_tokens) or re.search(r"\bgre\b", class_tokens) or "holiday" in class_tokens:
        return "HOLIDAY"
    return "UNKNOWN"

def normalize_provider_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Calendar operation: normalize_provider_event performs the focused normalize provider event step in the Calendar implementation."""
    if raw.get("id") in (None, "", "None"):
        raise ProviderError("ForexFactory event has no provider ID.")
    try:
        timestamp = datetime.fromtimestamp(
            int(raw["dateline"]), tz=timezone.utc
        )
    except (TypeError, ValueError, OSError, KeyError) as exc:
        raise ProviderError("ForexFactory event has an invalid dateline.") from exc

    currency = str(raw.get("currency", "")).strip().upper()
    if currency not in FX_CURRENCY_CODES and currency != "ALL":
        raise ProviderError(
            f"Unsupported ForexFactory currency '{currency}'."
        )
    title = str(raw.get("name", "")).strip()
    if not title:
        raise ProviderError("ForexFactory event has an empty title.")

    return {
        "event_id": f"forexfactory:{raw['id']}",
        "symbol": currency,
        "asset_type": "forex",
        "event_type": "economic",
        "source": "forexfactory",
        "timestamp": format_iso8601(timestamp),
        "title": title,
        "details": {
            "currency": currency,
            "impact": _resolve_impact(raw),
            "actual": (
                str(raw["actual"])
                if raw.get("actual") not in (None, "") else None
            ),
            "forecast": (
                str(raw["forecast"])
                if raw.get("forecast") not in (None, "") else None
            ),
            "previous": (
                str(raw["previous"])
                if raw.get("previous") not in (None, "") else None
            ),
            "specs": [],
        },
    }

def normalize_calendar_events(days_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calendar operation: normalize_calendar_events performs the focused normalize calendar events step in the Calendar implementation."""
    normalized: List[Dict[str, Any]] = []
    for day in days_data:
        if not isinstance(day, dict):
            raise ProviderError("Malformed ForexFactory day record.")
        for raw in day.get("events", []):
            if not isinstance(raw, dict):
                raise ProviderError("Malformed ForexFactory event record.")
            normalized.append(normalize_provider_event(raw))
    return normalized

def fetch_yahoo_news(symbol: str) -> List[Dict[str, Any]]:
    """Calendar operation: fetch_yahoo_news performs the focused fetch yahoo news step in the Calendar implementation."""
    provider_symbol, data = _resolve_yahoo_instrument(symbol)

    news = data.get("news")
    if not isinstance(news, list):
        raise ProviderError(
            "Yahoo Finance response has no valid news collection."
        )

    normalized: List[Dict[str, Any]] = []
    for item in news:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        publish_epoch = item.get("providerPublishTime")
        if publish_epoch in (None, ""):
            continue
        try:
            timestamp = datetime.fromtimestamp(
                int(publish_epoch), tz=timezone.utc
            )
        except (TypeError, ValueError, OSError):
            continue

        link = str(item.get("link", "")).strip() or None
        publisher = str(item.get("publisher", "")).strip() or None
        uuid_raw = item.get("uuid")
        uuid = (
            str(uuid_raw).strip()
            if uuid_raw not in (None, "")
            else ""
        )
        stable_id = uuid or hashlib.sha256(
            f"{provider_symbol}|{title}|{timestamp.isoformat()}|{link or ''}".encode(
                "utf-8"
            )
        ).hexdigest()

        normalized.append(
            {
                "event_id": f"yahoo:{stable_id}",
                "symbol": symbol,
                "asset_type": "forex" if is_fx_pair(symbol) else "ticker",
                "event_type": "news",
                "source": "yahoo_finance",
                "timestamp": format_iso8601(timestamp),
                "title": title,
                "details": {
                    "publisher": publisher,
                    "url": link,
                    "provider_symbol": provider_symbol,
                    "summary": (
                        str(item.get("summary")).strip()
                        if item.get("summary") not in (None, "")
                        else None
                    ),
                },
            }
        )
    return normalized
