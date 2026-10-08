"""London Strategic Edge Market Data provider adapter."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from .models import DEFAULT_PROVIDER_NAME, ProviderCandle, TIMEFRAME_SECONDS
from PROVIDERS.credentials import ProviderCredentialError, get_provider_api_key

LSE_CANDLES_URL = "https://api.londonstrategicedge.com/vault/candles"
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


def _format_lse_timestamp(value: datetime) -> str:
    """Format a UTC datetime for the LSE API."""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _map_symbol_to_lse(symbol: str) -> str:
    """Map the canonical project symbol to the LSE symbol spelling."""
    token = symbol.strip().upper()
    if len(token) == 6 and token.isalpha():
        return f"{token[:3]}/{token[3:]}"
    return token


def _parse_lse_timestamp(value: Any) -> datetime:
    """Parse an LSE timestamp into an aware UTC datetime."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    raw = str(value).strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    elif " " in raw and "T" not in raw:
        raw = raw.replace(" ", "T", 1)
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("LSE timestamp must include an explicit timezone")
    return parsed.astimezone(timezone.utc)


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


class LSEMarketDataProvider(MarketDataProvider):
    """Direct LSE candle provider; no timeframe aggregation is performed."""

    def __init__(self, timeout_seconds: int = 30, retries: int = 3):\n        """Initialize the LSE provider with request timeout and retry limits."""
        self.timeout_seconds = timeout_seconds
        self.retries = retries

    def _request_candle_page(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
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
            "start": _format_lse_timestamp(start_time),
            "end": _format_lse_timestamp(end_time),
            "order": "asc",
            "limit": 5000,
        })
        url = f"{LSE_CANDLES_URL}?{params}"
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                request = urllib.request.Request(
                    url,
                    headers={
                        "x-api-key": api_key,
                        "User-Agent": "SMC_Mapper/LSEMarketDataProvider",
                        "Accept": "application/json",
                    },
                )
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, list):
                    raise RuntimeError("LSE candles response is not a list")
                return payload
            except urllib.error.HTTPError as exc:
                last_error = RuntimeError(f"LSE HTTP {exc.code}")
            except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt + 1 < self.retries:
                time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"LSE candle acquisition failed: {last_error}")

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
        """Fetch the requested LSE timeframe, paging forward without gaps or loops."""
        if end_time <= start_time:
            raise ValueError("LSE range end must be after start")

        from .normalization import canonical_next_interval_start

        page_start = start_time
        records: list[ProviderCandle] = []
        while page_start < end_time:
            page_rows = self._request_candle_page(symbol, timeframe, page_start, end_time)
            if not page_rows:
                break
            page_records = self._parse_lse_candle_rows(page_rows, symbol, timeframe)
            records.extend(
                record for record in page_records
                if start_time <= record.timestamp < end_time
            )
            latest_timestamp = max(record.timestamp for record in page_records)
            next_start = canonical_next_interval_start(latest_timestamp, timeframe)
            if next_start <= page_start:
                raise RuntimeError("LSE pagination made no forward progress")
            page_start = next_start
        return sorted(records, key=lambda item: item.timestamp)

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
        """Fetch the current candle directly from LSE."""
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
