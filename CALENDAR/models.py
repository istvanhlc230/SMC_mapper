"""Explicit Calendar domain record shapes.

Runtime persistence remains plain JSON-compatible dictionaries so the same fields
map naturally to MQL4/MQL5 structures at the semantic boundary.
"""

from typing import List, Optional, TypedDict


class DetailSpec(TypedDict):
    order: int
    title: str
    html: str


class CalendarEventDetails(TypedDict, total=False):
    currency: str
    impact: str
    actual: Optional[str]
    forecast: Optional[str]
    previous: Optional[str]
    specs: List[DetailSpec]
    publisher: Optional[str]
    url: Optional[str]
    provider_symbol: str
    summary: Optional[str]


class CalendarEvent(TypedDict, total=False):
    event_id: str
    symbol: str
    asset_type: str
    event_type: str
    source: str
    timestamp: str
    title: str
    details: CalendarEventDetails
    suppressed_for: List[str]


class CoverageRecord(TypedDict):
    provider: str
    symbol: str
    start: str
    end: str
    status: str
    updated_at: str


class ProviderWatermark(TypedDict):
    provider: str
    symbol: str
    last_successful_at: Optional[str]
    last_event_timestamp: Optional[str]


class ProviderResult(TypedDict, total=False):
    provider: str
    status: str
    events_acquired: int
    events_returned: int
    events_fetched: int
    events_refreshed: int
    coverage: str
    historical_coverage: str
    reason: str
    error: str


class RefreshSummary(TypedDict):
    added: int
    changed: int
    unchanged: int


class CalendarDocument(TypedDict):
    schema_version: int
    events: List[CalendarEvent]
    coverage: List[CoverageRecord]
    watermarks: dict[str, ProviderWatermark]
