"""London Strategic Edge Market Data provider adapter."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from .models import (
    DEFAULT_PROVIDER_NAME,
    MarketDepthSnapshot,
    ProviderCandle,
    TIMEFRAME_SECONDS,
)
from PROVIDERS.credentials import ProviderCredentialError, get_provider_api_key
from COMMON.date_time import DateTimeScopeError, parse_aware_datetime
from COMMON.http_client import HttpClient, HttpRequestError

LSE_CANDLES_URL = "https://api.londonstrategicedge.com/vault/candles"
# The candle API is date-filtered and caps a response at 5,000 rows. A two-day
# request window stays below that cap for M1 even if the end date is inclusive.
CANDLE_QUERY_WINDOW_DAYS = 2
TIMEFRAME_INTERVALS = {
    "M1": "1m",
    "M5": "5m",
    "M15": "15m",
    "M30": "30m",
    "H1": "1h",
    "H4": "4h",
    "D1": "1d",
    "W1": "1w",
    "MN1": "1mo",
}


def _format_lse_date(value: datetime) -> str:
    """Format an LSE candle filter as a UTC calendar date, without a time component."""
    return value.astimezone(timezone.utc).date().isoformat()




def _map_symbol_to_lse(symbol: str) -> str:
    """Map the canonical project symbol to the LSE symbol spelling."""
    token = symbol.strip().upper()
    if len(token) == 6 and token.isalpha():
        return f"{token[:3]}/{token[3:]}"
    return token


def _parse_lse_timestamp(value: Any) -> datetime:
    """Parse an LSE timestamp, interpreting the Vault's documented naive row format as UTC."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    raw_timestamp = str(value).strip()
    if raw_timestamp.endswith("Z"):
        raw_timestamp = raw_timestamp[:-1] + "+00:00"
    elif " " in raw_timestamp and "T" not in raw_timestamp:
        # The LSE Vault JSON row API returns UTC timestamps as
        # "YYYY-MM-DD HH:MM:SS[.ffffff]" without an offset. Its official client
        # normalizes this exact provider format by appending the UTC marker.
        is_documented_vault_timestamp = re.fullmatch(
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?",
            raw_timestamp,
        ) is not None
        raw_timestamp = raw_timestamp.replace(" ", "T", 1)
        if is_documented_vault_timestamp:
            raw_timestamp += "+00:00"

    try:
        return parse_aware_datetime(raw_timestamp)
    except DateTimeScopeError as exc:
        if "explicit timezone" in str(exc):
            raise ValueError(
                "LSE timestamp is timezone-naive and does not match the documented UTC Vault row format"
            ) from exc
        raise ValueError("invalid LSE timestamp") from exc




def _parse_lse_decimal(value: Any, field_name: str) -> Any:
    """Validate an LSE numeric field before handing it to normalization."""
    if value is None:
        raise ValueError(f"LSE candle missing {field_name}")
    try:
        return Decimal(str(value))
    except (ValueError, TypeError, ArithmeticError) as exc:
        raise ValueError(f"invalid LSE {field_name}") from exc


class MarketDataProvider:
    """Provider-neutral Market Data acquisition contract."""

    def fetch_range(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ProviderCandle]:
        raise NotImplementedError

    def fetch_latest_completed(
        self,
        symbol: str,
        timeframe: str,
    ) -> ProviderCandle | None:
        raise NotImplementedError

    def fetch_current(
        self,
        symbol: str,
        timeframe: str,
    ) -> ProviderCandle | None:
        raise NotImplementedError

    def fetch_market_depth(
        self,
        symbol: str,
        as_of: datetime | None = None,
    ) -> MarketDepthSnapshot | None:
        """Return optional L2 depth; return None when unsupported or unavailable.

        If as_of is provided, only providers with historical depth support may
        return a snapshot appropriate to that point in time. A live-only
        snapshot must not be substituted for a historical request.
        """
        return None


class LSEMarketDataProvider(MarketDataProvider):
    """Direct LSE candle provider; no timeframe aggregation is performed."""

    def __init__(self, timeout_seconds: int = 30, retries: int = 3):
        """Initialize the LSE provider with request timeout and retry limits."""
        self.timeout_seconds = timeout_seconds
        self.retries = retries

    def fetch_market_depth(
        self,
        symbol: str,
        as_of: datetime | None = None,
    ) -> MarketDepthSnapshot | None:
        """Report no L2 snapshot because the configured LSE adapter is candle-only."""
        return None

    def _request_candle_page(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Fetch one LSE candle page using the shared HTTP client and provider credentials."""
        try:
            api_key = get_provider_api_key("lse")
        except ProviderCredentialError as exc:
            raise RuntimeError(str(exc)) from exc
        interval = TIMEFRAME_INTERVALS.get(timeframe)
        if interval is None:
            raise ValueError(f"LSE does not have a mapping for {timeframe}")
        params = urllib.parse.urlencode({
            "symbol": _map_symbol_to_lse(symbol),
            "timeframe": interval,
            "start": _format_lse_date(start_time),
            "end": _format_lse_date(end_time),
            "order": "asc",
            "limit": 5000,
        })
        url = f"{LSE_CANDLES_URL}?{params}"
        try:
            payload = HttpClient.get(
                url,
                headers={
                    "x-api-key": api_key,
                    "User-Agent": "SMC_Mapper/LSEMarketDataProvider",
                    "Accept": "application/json",
                },
                timeout_seconds=self.timeout_seconds,
                response_format="json",
                retries=self.retries,
                retry_delay_seconds=0.5,
                ipv4_first=True,
            )
        except HttpRequestError as exc:
            raise RuntimeError(
                "LSE candle acquisition failed for "
                f"{_map_symbol_to_lse(symbol)} timeframe={interval} "
                f"date_window={_format_lse_date(start_time)}..{_format_lse_date(end_time)} "
                f"(end-exclusive): {exc}"
            ) from exc
        if not isinstance(payload, list):
            raise RuntimeError("LSE candles response is not a list")
        return payload



    def _parse_lse_candle_rows(self, rows: list[dict[str, Any]], symbol: str, timeframe: str) -> list[ProviderCandle]:
        """Convert direct LSE candle rows to provider-neutral candles."""
        records: list[ProviderCandle] = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("malformed LSE candle record")
            timestamp = _parse_lse_timestamp(row.get("timestamp", row.get("ts")))
            open_price = _parse_lse_decimal(row.get("open"), "open")
            high_price = _parse_lse_decimal(row.get("high"), "high")
            low_price = _parse_lse_decimal(row.get("low"), "low")
            close_price = _parse_lse_decimal(row.get("close"), "close")
            volume = row.get("volume")
            records.append(
                ProviderCandle(
                    source_timestamp=row.get("timestamp", row.get("ts")),
                    source_timezone="UTC",
                    timestamp=timestamp,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    total_volume=volume,
                    provider_metadata={
                        "provider": "lse",
                        "interval": timeframe,
                        "provider_symbol": _map_symbol_to_lse(symbol),
                    },
                )
            )
        return sorted(records, key=lambda item: item.timestamp)

    def fetch_range(self, symbol, timeframe, start_time, end_time):
        """Fetch a precise UTC interval using bounded date-only LSE query windows."""
        utc_start = start_time.astimezone(timezone.utc)
        utc_end = end_time.astimezone(timezone.utc)
        if utc_end <= utc_start:
            raise ValueError("LSE range end must be after start")

        # LSE candle filters are calendar-date based. Query all of the first date
        # and, when END is not midnight, all of its date too; exact time filtering
        # below restores the requested half-open interval.
        query_day = utc_start.date()
        exclusive_end_day = utc_end.date()
        if utc_end.time() != datetime.min.time():
            exclusive_end_day += timedelta(days=1)

        records_by_timestamp: dict[datetime, ProviderCandle] = {}
        while query_day < exclusive_end_day:
            window_end_day = min(
                query_day + timedelta(days=CANDLE_QUERY_WINDOW_DAYS),
                exclusive_end_day,
            )
            page_start = datetime.combine(
                query_day,
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
            page_end = datetime.combine(
                window_end_day,
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
            page_rows = self._request_candle_page(
                symbol,
                timeframe,
                page_start,
                page_end,
            )
            page_records = self._parse_lse_candle_rows(page_rows, symbol, timeframe)

            for record in page_records:
                if not utc_start <= record.timestamp < utc_end:
                    continue
                existing_record = records_by_timestamp.get(record.timestamp)
                if existing_record is not None and existing_record != record:
                    raise RuntimeError(
                        "conflicting LSE candle content at timestamp "
                        f"{record.timestamp.isoformat()}"
                    )
                records_by_timestamp[record.timestamp] = record

            # Advance by the requested calendar window, not the latest returned
            # candle. Weekends, holidays, and empty provider pages cannot stall
            # or repeat the query loop.
            query_day = window_end_day

        return sorted(records_by_timestamp.values(), key=lambda item: item.timestamp)

    def _lookup_window(self, timeframe: str, now: datetime) -> datetime:
        """Return a bounded same-timeframe lookup start for latest/current reads."""
        from .normalization import canonical_interval_start
        start = canonical_interval_start(now, timeframe)
        if timeframe in TIMEFRAME_SECONDS:
            return start - timedelta(seconds=TIMEFRAME_SECONDS[timeframe] * 3)
        if timeframe == "W1":
            return start - timedelta(days=21)
        if timeframe == "MN1":
            for _ in range(3):
                if start.month == 1:
                    start = start.replace(year=start.year - 1, month=12, day=1)
                else:
                    start = start.replace(month=start.month - 1, day=1)
            return start
        raise ValueError(f"unsupported timeframe: {timeframe}")

    def fetch_latest_completed(self, symbol, timeframe):
        """Fetch the latest completed candle directly from LSE."""
        now = datetime.now(timezone.utc)
        records = self.fetch_range(symbol, timeframe, self._lookup_window(timeframe, now), now)
        if not records:
            return None
        from .normalization import derive_completion_time
        completed = [
            record for record in records
            if derive_completion_time(record.timestamp, timeframe) <= now
        ]
        return max(completed, key=lambda record: record.timestamp) if completed else None

    def fetch_current(self, symbol, timeframe):
        """Fetch the current in-progress candle directly from LSE."""
        now = datetime.now(timezone.utc)
        from .normalization import canonical_interval_start, derive_completion_time
        start = canonical_interval_start(now, timeframe)
        records = self.fetch_range(symbol, timeframe, start, now + timedelta(seconds=1))
        if not records:
            return None
        current = [
            record for record in records
            if record.timestamp >= start
            and derive_completion_time(record.timestamp, timeframe) > now
        ]
        return max(current, key=lambda record: record.timestamp) if current else None


def create_provider(provider_name: str) -> MarketDataProvider:
    """Create the configured Market Data provider."""
    if provider_name != DEFAULT_PROVIDER_NAME:
        raise ValueError(f"unsupported provider: {provider_name}")
    return LSEMarketDataProvider()
