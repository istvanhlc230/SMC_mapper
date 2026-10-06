"""Yahoo Charts provider adapter."""
from __future__ import annotations
import json, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from .models import DEFAULT_PROVIDER_NAME, ProviderCandle

_INTERVALS = {"M1":"1m","M5":"5m","M15":"15m","M30":"30m","H1":"1h","D1":"1d","W1":"1wk","MN1":"1mo"}

def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00","Z")

class MarketDataProvider:
    def fetch_range(self, symbol: str, timeframe: str, start_time: datetime, end_time: datetime) -> list[ProviderCandle]: raise NotImplementedError
    def fetch_latest_completed(self, symbol: str, timeframe: str) -> ProviderCandle | None: raise NotImplementedError
    def fetch_current(self, symbol: str, timeframe: str) -> ProviderCandle | None: raise NotImplementedError

class YahooChartsProvider(MarketDataProvider):
    def __init__(self, timeout_seconds: int = 20, retries: int = 3):
        self.timeout_seconds, self.retries = timeout_seconds, retries

    def _request(self, symbol: str, interval: str, start_time: datetime, end_time: datetime) -> dict[str, Any]:
        query = urllib.parse.urlencode({"period1": int(start_time.timestamp()), "period2": int(end_time.timestamp()), "interval": interval, "events":"history", "includeAdjustedClose":"true"})
        url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol, safe="") + "?" + query
        last_error = None
        for attempt in range(self.retries):
            try:
                request = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                last_error = exc
                if attempt + 1 < self.retries: time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"Yahoo Charts acquisition failed: {last_error}")

    def _parse(self, payload: dict[str, Any], symbol: str, interval: str) -> list[ProviderCandle]:
        chart = payload.get("chart", {})
        error = chart.get("error")
        if error: raise RuntimeError(f"Yahoo Charts error: {error}")
        result = (chart.get("result") or [None])[0]
        if not result: return []
        timestamps = result.get("timestamp") or []
        quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
        volume = quote.get("volume") or []
        records=[]
        for index, raw_timestamp in enumerate(timestamps):
            try:
                values = [
                    quote.get(key, [None] * len(timestamps))[index]
                    for key in ("open", "high", "low", "close")
                ]
                if any(value is None for value in values):
                    raise ValueError("malformed Yahoo candle: missing OHLC field")
                stamp=datetime.fromtimestamp(raw_timestamp, tz=timezone.utc)
                records.append(ProviderCandle(stamp, "UTC", stamp, *values, volume[index] if index < len(volume) else None, provider_metadata={"provider":"yahoo_charts","interval":interval}))
            except (ValueError, TypeError, IndexError):
                raise ValueError("malformed Yahoo candle")
        return records

    def fetch_range(self, symbol, timeframe, start_time, end_time):
        if timeframe == "H4":
            return self._aggregate_hourly(symbol, start_time, end_time, 4)
        interval=_INTERVALS.get(timeframe)
        if interval is None: raise ValueError(f"Yahoo Charts does not support {timeframe} directly")
        return self._parse(self._request(symbol, interval, start_time, end_time), symbol, interval)

    def _aggregate_hourly(self, symbol, start_time, end_time, hours):
        records=self._parse(self._request(symbol,"1h",start_time,end_time),symbol,"1h")
        if not records: return []
        from .models import TIMEFRAME_SECONDS
        buckets={}
        for candle in records:
            epoch=int(candle.timestamp.timestamp())
            bucket=epoch-(epoch % (hours*3600))
            buckets.setdefault(bucket,[]).append(candle)
        output=[]
        for bucket, group in sorted(buckets.items()):
            group = sorted(group, key=lambda candle: candle.timestamp)
            if len(group) != hours:
                continue
            expected = [
                datetime.fromtimestamp(bucket, tz=timezone.utc)
                + timedelta(hours=offset)
                for offset in range(hours)
            ]
            if [candle.timestamp for candle in group] != expected:
                continue
            stamp=datetime.fromtimestamp(bucket,tz=timezone.utc)
            total=sum((Decimal(str(x.total_volume or 0)) for x in group), Decimal("0"))
            output.append(ProviderCandle(stamp,"UTC",stamp,group[0].open_price,max(x.high_price for x in group),min(x.low_price for x in group),group[-1].close_price,total,provider_metadata={"provider":"yahoo_charts","aggregated_from":"1h"}))
        return output

    def _window_start(self, timeframe: str, now: datetime) -> datetime:
        from .models import TIMEFRAME_SECONDS
        seconds = TIMEFRAME_SECONDS[timeframe]
        epoch = int(now.timestamp())
        return datetime.fromtimestamp(epoch - (epoch % seconds), tz=timezone.utc)

    def fetch_latest_completed(self, symbol, timeframe):
        now = datetime.now(timezone.utc)
        from .models import TIMEFRAME_SECONDS
        start = self._window_start(timeframe, now) - timedelta(seconds=TIMEFRAME_SECONDS[timeframe] * 3)
        records = self.fetch_range(symbol, timeframe, start, now)
        if not records:
            return None
        from .normalization import derive_completion_time
        completed = [record for record in records if derive_completion_time(record.timestamp, timeframe) <= now]
        return max(completed, key=lambda record: record.timestamp) if completed else None

    def fetch_current(self, symbol, timeframe):
        now = datetime.now(timezone.utc)
        start = self._window_start(timeframe, now)
        if timeframe == "H4":
            hourly = self._parse(
                self._request(
                    symbol,
                    "1h",
                    start,
                    now + timedelta(seconds=1),
                ),
                symbol,
                "1h",
            )
            hourly = sorted(
                [item for item in hourly if item.timestamp >= start],
                key=lambda item: item.timestamp,
            )
            expected = [
                start + timedelta(hours=offset)
                for offset in range(4)
                if start + timedelta(hours=offset) <= now
            ]
            if not hourly or [item.timestamp for item in hourly] != expected:
                return None
            return ProviderCandle(
                start,
                "UTC",
                start,
                hourly[0].open_price,
                max(item.high_price for item in hourly),
                min(item.low_price for item in hourly),
                hourly[-1].close_price,
                sum(
                    (Decimal(str(item.total_volume or 0)) for item in hourly),
                    Decimal("0"),
                ),
                provider_metadata={
                    "provider": "yahoo_charts",
                    "aggregated_from": "1h",
                    "complete": False,
                },
            )
        records = self.fetch_range(symbol, timeframe, start, now + timedelta(seconds=1))
        if not records:
            return None
        from .normalization import derive_completion_time
        incomplete = [record for record in records if derive_completion_time(record.timestamp, timeframe) > now]
        return max(incomplete, key=lambda record: record.timestamp) if incomplete else None


def create_provider(provider_name: str) -> MarketDataProvider:
    if provider_name != DEFAULT_PROVIDER_NAME: raise ValueError(f"unsupported provider: {provider_name}")
    return YahooChartsProvider()
