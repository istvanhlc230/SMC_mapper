"""Provider-neutral Market Data domain models and policy constants."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

DEFAULT_DATA_DIRECTORY = Path("data")
# SUPPORTED_TIMEFRAMES — canonical timeframes accepted by the Market Data CLI and process contract.
SUPPORTED_TIMEFRAMES = (
    "M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"
)
# TIMEFRAME_SECONDS — fixed-duration timeframe lengths in seconds; calendar-based W1/MN1 are excluded.
TIMEFRAME_SECONDS = {
    "M1": 60, "M5": 300, "M15": 900, "M30": 1800,
    "H1": 3600, "H4": 14400, "D1": 86400,
}
DEFAULT_PROVIDER_NAME = "lse"
DEFAULT_CANDLE_RETENTION = 5000
WRITE_RETRY_LIMIT = 5
WRITE_RETRY_DELAY_SECONDS = 0.25
DECIMAL_PERSISTENCE_PLACES = 18
CALENDAR_BASED_TIMEFRAMES = ("W1", "MN1")

@dataclass(frozen=True)
class MarketDataRequest:
    """Validated command-line request passed through the Market Data acquisition layer."""
    symbol: str
    timeframes: list[str]
    start_time: datetime | None
    end_time: datetime | None
    last_closed_only: bool
    current: bool
    debug: bool
    table: bool = False

@dataclass(frozen=True)
class ProviderCandle:
    """Provider-normalized candle before canonical Market Data persistence."""
    source_timestamp: Any
    source_timezone: str | None
    timestamp: datetime
    open_price: Any
    high_price: Any
    low_price: Any
    close_price: Any
    total_volume: Any | None = None
    orderflow_buy: Any | None = None
    orderflow_sell: Any | None = None
    completion_hint: Any | None = None
    provider_metadata: dict[str, Any] | None = None

@dataclass(frozen=True)
class VolumeState:
    """Explicit availability state for optional provider volume fields."""
    has_total: bool
    total: Decimal | None
    has_ohlc: bool
    ohlc_buy: Decimal | None
    ohlc_sell: Decimal | None
    has_orderflow: bool
    orderflow_buy: Decimal | None
    orderflow_sell: Decimal | None

@dataclass(frozen=True)
class MarketDepthLevel:
    """One provider-reported Level 2 price level and its available size."""
    price: Decimal
    volume: Decimal


@dataclass(frozen=True)
class MarketDepthSnapshot:
    """A timestamped provider order-book snapshot, independent of OHLC candles."""
    symbol: str
    provider: str
    timestamp: datetime
    bids: list[MarketDepthLevel]
    asks: list[MarketDepthLevel]


@dataclass(frozen=True)
class NormalizedCandle:
    """Canonical candle representation used by Market Data process serialization."""
    candle_id: str
    timestamp: datetime
    completion_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: VolumeState

@dataclass
class TimeframeState:
    """Persisted state and current snapshot for one canonical timeframe."""
    timeframe: str
    available_start: datetime | None
    available_end: datetime | None
    candles: list[NormalizedCandle]
    current: NormalizedCandle | None

@dataclass
class MarketDataDocument:
    """Provider-independent in-memory representation of one symbol data document."""
    symbol: str
    timeframes: list[TimeframeState]
