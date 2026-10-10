"""Shared date/time scope parsing and UTC primitives for all Python modules."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

UTC = timezone.utc
DATE_PATTERN = r"\d{4}\.\d{2}\.\d{2}"
TIME_PATTERN = r"\d{2}:\d{2}"


class DateTimeScopeError(ValueError):
    """Raised when a date, time, or temporal scope violates the shared grammar."""


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    """Reject naive datetimes and normalize timezone-aware values to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise DateTimeScopeError("datetime must include an explicit timezone")
    return value.astimezone(UTC)


def format_utc_iso8601(value: datetime, timespec: str = "auto") -> str:
    """Format a timezone-aware datetime as ISO 8601 UTC with a trailing Z."""
    normalized = ensure_utc(value)
    return normalized.isoformat(timespec=timespec).replace("+00:00", "Z")


def parse_aware_datetime(value: str, *, require_utc: bool = False) -> datetime:
    """Parse an ISO 8601 timestamp with an explicit timezone and return UTC."""
    if not isinstance(value, str) or not value.strip():
        raise DateTimeScopeError("timestamp must be a non-empty ISO 8601 string")
    normalized_text = value.strip()
    if normalized_text.endswith("Z"):
        normalized_text = normalized_text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized_text)
    except ValueError as exc:
        raise DateTimeScopeError("invalid ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DateTimeScopeError("timestamp must include an explicit timezone")
    if require_utc and parsed.utcoffset() != timedelta(0):
        raise DateTimeScopeError("timestamp must use UTC")
    return parsed.astimezone(UTC)


@dataclass(frozen=True)
class DateTimeScope:
    """Parsed interval boundaries and open-boundary metadata, before domain resolution."""
    kind: str
    start: Optional[datetime]
    end: Optional[datetime]
    source: str
    open_start: bool = False
    open_end: bool = False
    reference_time: Optional[datetime] = None

    def resolve_interval(
        self,
        reference_time: Optional[datetime] = None,
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        """Resolve an open end to the reference UTC time while preserving open starts."""
        current_time = (
            ensure_utc(reference_time)
            if reference_time is not None
            else ensure_utc(self.reference_time) if self.reference_time is not None else utc_now()
        )
        if self.open_start:
            return None, self.end
        if self.open_end:
            if self.start is None:
                raise DateTimeScopeError("open-end scope is missing its start")
            if self.start >= current_time:
                raise DateTimeScopeError("open-end scope must start before the current UTC time")
            return self.start, current_time
        if self.start is None or self.end is None:
            raise DateTimeScopeError("scope is missing a required interval boundary")
        if self.end <= self.start:
            raise DateTimeScopeError("scope end must be later than its start")
        return self.start, self.end


class DateTimeScopeParser:
    """Parse the shared positional date/time scope grammar without performing I/O."""

    def __init__(self, reference_time: Optional[datetime] = None) -> None:
        """Capture one UTC reference time so all time-only endpoints use the same UTC day."""
        self.reference_time = (
            ensure_utc(reference_time) if reference_time is not None else utc_now()
        )

    @staticmethod
    def parse_date_value(value: str) -> datetime:
        """Validate YYYY.MM.DD and return UTC midnight for that date."""
        if not isinstance(value, str) or not re.fullmatch(DATE_PATTERN, value.strip()):
            raise DateTimeScopeError(f"invalid date '{value}'; expected YYYY.MM.DD")
        try:
            year, month, day = (int(part) for part in value.strip().split("."))
            return datetime(year, month, day, tzinfo=UTC)
        except (ValueError, TypeError) as exc:
            raise DateTimeScopeError(f"invalid calendar date '{value}'") from exc

    @staticmethod
    def parse_time_value(value: str) -> tuple[int, int]:
        """Validate HH:MM and return integer hour/minute values."""
        if not isinstance(value, str) or not re.fullmatch(TIME_PATTERN, value.strip()):
            raise DateTimeScopeError(f"invalid time '{value}'; expected HH:MM")
        hour, minute = (int(part) for part in value.strip().split(":"))
        if hour > 23 or minute > 59:
            raise DateTimeScopeError(f"invalid time '{value}'; expected HH:MM")
        return hour, minute

    def _parse_endpoint(self, value: str) -> tuple[str, datetime]:
        """Parse one date, date-time, or time endpoint using the captured UTC date."""
        endpoint = " ".join(value.strip().split())
        date_time_match = re.fullmatch(
            rf"({DATE_PATTERN})\s+({TIME_PATTERN})", endpoint
        )
        if date_time_match:
            date_value, time_value = date_time_match.groups()
            date_start = self.parse_date_value(date_value)
            hour, minute = self.parse_time_value(time_value)
            return "DATETIME", date_start.replace(hour=hour, minute=minute)

        if re.fullmatch(DATE_PATTERN, endpoint):
            return "DATE", self.parse_date_value(endpoint)

        if re.fullmatch(TIME_PATTERN, endpoint):
            hour, minute = self.parse_time_value(endpoint)
            utc_midnight = self.reference_time.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return "TIME", utc_midnight.replace(hour=hour, minute=minute)

        raise DateTimeScopeError(
            f"invalid scope endpoint '{value}'; expected YYYY.MM.DD, "
            "YYYY.MM.DD HH:MM, or HH:MM"
        )

    @staticmethod
    def _inclusive_endpoint_end(kind: str, endpoint: datetime) -> datetime:
        """Return the exclusive upper boundary for an inclusive date/minute endpoint."""
        return endpoint + (timedelta(days=1) if kind == "DATE" else timedelta(minutes=1))

    def parse(self, scope_text: str) -> DateTimeScope:
        """Parse one canonical scope string into validated UTC interval boundaries."""
        if not isinstance(scope_text, str) or not scope_text.strip():
            raise DateTimeScopeError("scope must not be empty")
        normalized_scope = " ".join(scope_text.strip().split())

        if normalized_scope.startswith("-"):
            endpoint_text = normalized_scope[1:].strip()
            if not endpoint_text or endpoint_text.startswith("-"):
                raise DateTimeScopeError(f"invalid open-start scope '{scope_text}'")
            endpoint_kind, endpoint = self._parse_endpoint(endpoint_text)
            end = self._inclusive_endpoint_end(endpoint_kind, endpoint)
            return DateTimeScope(
                kind="OPEN_START",
                start=None,
                end=end,
                source=normalized_scope,
                open_start=True,
                reference_time=self.reference_time,
            )

        if normalized_scope.endswith("-"):
            endpoint_text = normalized_scope[:-1].strip()
            if not endpoint_text:
                raise DateTimeScopeError(f"invalid open-end scope '{scope_text}'")
            endpoint_kind, start = self._parse_endpoint(endpoint_text)
            return DateTimeScope(
                kind="OPEN_END",
                start=start,
                end=None,
                source=normalized_scope,
                open_end=True,
                reference_time=self.reference_time,
            )

        if "-" in normalized_scope:
            if normalized_scope.count("-") != 1:
                raise DateTimeScopeError(f"invalid range '{scope_text}'")
            start_text, end_text = (
                part.strip() for part in normalized_scope.split("-", 1)
            )
            start_kind, start = self._parse_endpoint(start_text)
            end_kind, end = self._parse_endpoint(end_text)
            if start_kind != end_kind:
                raise DateTimeScopeError(
                    "range endpoints must both be dates, both date-times, "
                    "or both time-only values"
                )
            if start_kind == "DATE":
                kind = "DATE_RANGE"
                end += timedelta(days=1)
            elif start_kind == "DATETIME":
                kind = "DATETIME_RANGE"
            else:
                kind = "TIME_RANGE"
            if end <= start:
                raise DateTimeScopeError("range end must be later than its start")
            return DateTimeScope(
                kind, start, end, normalized_scope,
                reference_time=self.reference_time,
            )

        endpoint_kind, point = self._parse_endpoint(normalized_scope)
        if endpoint_kind == "DATE":
            return DateTimeScope(
                "DATE",
                point,
                point + timedelta(days=1),
                normalized_scope,
                reference_time=self.reference_time,
            )
        return DateTimeScope(
            endpoint_kind,
            point,
            point + timedelta(minutes=1),
            normalized_scope,
            reference_time=self.reference_time,
        )
