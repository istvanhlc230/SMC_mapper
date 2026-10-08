# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""ForexFactory rendered and structured parsing helpers."""

import json
import re
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import FX_CURRENCY_CODES, ProviderError

# Parser state is input-local: parsed rows and normalized values are produced from provider responses without persistent module state.

def _normalize_forexfactory_impact_value(value: str) -> str:
    """Internal helper for normalize forexfactory impact value."""
    lowered = value.strip().lower()
    if "high" in lowered:
        return "high"
    if "medium" in lowered or lowered.startswith("med"):
        return "medium"
    if "low" in lowered:
        return "low"
    if "non-economic" in lowered or "holiday" in lowered:
        return "holiday"
    return ""

def _classify_forexfactory_impact(classes: set[str]) -> str:
    """Internal helper for classify forexfactory impact."""
    for class_name in classes:
        lowered = class_name.lower()
        if lowered.endswith("--high") or lowered in {"high", "impact-red", "icon--ff-impact-red"}:
            return "high"
        if lowered.endswith("--medium") or lowered in {
            "medium", "med", "impact-orange", "icon--ff-impact-orange", "icon--ff-impact-ora"
        }:
            return "medium"
        if lowered.endswith("--low") or lowered in {
            "low",
            "impact-yellow",
            "icon--ff-impact-yellow",
            "icon--ff-impact-yel",
            "impact-green",
            "icon--ff-impact-green",
            "icon--ff-impact-grn",
        }:
            return "low"
        if lowered in {
            "holiday",
            "impact-grey",
            "impact-gray",
            "non-economic",
            "icon--ff-impact-grey",
            "icon--ff-impact-gray",
            "icon--ff-impact-gry",
        }:
            return "holiday"
    return ""

class ForexFactoryHTMLCalendarParser(HTMLParser):
    """Parse rendered ForexFactory calendar rows without inventing event timestamps."""

    def __init__(self) -> None:
        """Internal helper for init ."""
        super().__init__(convert_charrefs=True)
        # rows contains provider-rendered event rows collected from one response.
        self.rows: List[Dict[str, Any]] = []
        # current_row holds the event currently being parsed.
        self.current_row: Optional[Dict[str, Any]] = None
        # current_cell identifies which semantic calendar field is receiving text.
        self.current_cell: Optional[str] = None
        # text_buffer accumulates the visible text inside the active cell/span.
        self.text_buffer: List[str] = []
        # capture_title tracks the nested event-title span.
        self.capture_title = False
        # last_date_text supports ForexFactory rows that omit repeated calendar dates.
        self.last_date_text = ""
        # Time is deliberately not inherited: a missing/non-concrete provider clock
        # must fail closed instead of attaching the previous row's time. This avoids
        # silently creating a false event timestamp.

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Internal helper for handle starttag."""
        attributes = dict(attrs)
        classes = set(str(attributes.get("class") or "").split())

        if tag == "tr":
            event_id = (
                attributes.get("data-eventid")
                or attributes.get("data-event-id")
                or attributes.get("data-eid")
            )
            is_calendar_row = (
                "calendar__row" in classes
                or "calendar_row" in classes
            )
            # The provider event-instance ID is the stable row anchor. Current
            # CSS row classes are advisory because ForexFactory may change them.
            if event_id or is_calendar_row:
                self.current_row = {
                    "id": event_id,
                    "date": "",
                    "time": "",
                    "currency": "",
                    "impact": "",
                    "title": "",
                    "actual": "",
                    "forecast": "",
                    "previous": "",
                }
                self.current_cell = None
                self.text_buffer = []
                return

        if self.current_row is None:
            return

        if tag == "td":
            self.current_cell = " ".join(classes)
            if "calendar__impact" in self.current_cell:
                impact = _classify_forexfactory_impact(classes)
                if impact:
                    self.current_row["impact"] = impact
            self.text_buffer = []
            return

        if tag == "span" and "calendar__event-title" in classes:
            self.capture_title = True
            self.text_buffer = []

        if tag == "span" and self.current_cell and "calendar__impact" in self.current_cell:
            impact_title = str(attributes.get("title") or "").strip()
            if impact_title:
                normalized_title = _normalize_forexfactory_impact_value(impact_title)
                if normalized_title:
                    self.current_row["impact"] = normalized_title
            impact = _classify_forexfactory_impact(classes)
            if impact:
                self.current_row["impact"] = impact

    def handle_endtag(self, tag: str) -> None:
        """Internal helper for handle endtag."""
        if self.current_row is None:
            return

        if tag == "span" and self.capture_title:
            self.current_row["title"] = " ".join(self.text_buffer).strip()
            self.capture_title = False
            return

        if tag == "td":
            cell_text = " ".join(self.text_buffer).strip()
            if self.current_cell:
                if "calendar__date" in self.current_cell:
                    self.current_row["date"] = cell_text
                elif "calendar__time" in self.current_cell:
                    self.current_row["time"] = cell_text
                elif "calendar__currency" in self.current_cell:
                    self.current_row["currency"] = cell_text
                elif "calendar__actual" in self.current_cell:
                    self.current_row["actual"] = cell_text
                elif "calendar__forecast" in self.current_cell:
                    self.current_row["forecast"] = cell_text
                elif "calendar__previous" in self.current_cell:
                    self.current_row["previous"] = cell_text
            self.current_cell = None
            self.text_buffer = []
            return

        if tag == "tr":
            row = self.current_row
            self.current_row = None
            self.current_cell = None
            self.text_buffer = []
            date_text = str(row.get("date") or "").strip()
            time_text = str(row.get("time") or "").strip()
            if date_text:
                self.last_date_text = date_text
            else:
                row["date"] = self.last_date_text
            # Do not inherit a previous row's clock. A missing clock must
            # remain missing so the event parser can fail closed instead of
            # fabricating a timestamp.
            self.rows.append(row)

    def handle_data(self, data: str) -> None:
        """Internal helper for handle data."""
        if self.current_row is not None:
            self.text_buffer.append(data)

def _extract_forexfactory_timezone(html: str) -> timezone:
    """Internal helper for extract forexfactory timezone."""
    match = re.search(
        r"Calendar\s+Time\s+Zone:\s*([A-Za-z_]+(?:/[A-Za-z0-9_.+-]+)+)",
        html,
        re.IGNORECASE,
    )
    if not match:
        raise ProviderError("ForexFactory response has no calendar timezone declaration.")

    timezone_name = match.group(1)
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        offset_match = re.search(
            r"Calendar\s+Time\s+Zone:.*?\(GMT\s*([+-])(\d{1,2})(?::(\d{2}))?\)",
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not offset_match:
            raise ProviderError(
                f"Unsupported ForexFactory calendar timezone '{timezone_name}'."
            )
        sign = 1 if offset_match.group(1) == "+" else -1
        hours = int(offset_match.group(2))
        minutes = int(offset_match.group(3) or "0")
        return timezone(sign * timedelta(hours=hours, minutes=minutes))

def _parse_forexfactory_date(
    date_text: str,
    reference_start: datetime,
    reference_end: datetime,
) -> datetime:
    """Internal helper for parse forexfactory date."""
    cleaned = " ".join(date_text.split())
    match = re.search(
        r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})",
        cleaned,
    )
    if not match:
        raise ProviderError(f"Invalid ForexFactory event date '{date_text}'.")

    month_text = match.group(1)
    day_text = match.group(2)
    month_numbers = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }
    month_number = month_numbers.get(month_text.title())
    if month_number is None:
        raise ProviderError(f"Invalid ForexFactory event month '{month_text}'.")
    day_number = int(day_text)
    candidates: List[datetime] = []
    for year in range(reference_start.year - 1, reference_end.year + 2):
        try:
            parsed = datetime(
                year,
                month_number,
                day_number,
                tzinfo=timezone.utc,
            )
        except ValueError:
            continue
        candidates.append(parsed)

    in_window = [
        candidate
        for candidate in candidates
        if reference_start.date() <= candidate.date() <= reference_end.date()
    ]
    if in_window:
        return min(in_window, key=lambda item: abs(item - reference_start))
    if not candidates:
        raise ProviderError(f"Unable to resolve ForexFactory event date '{date_text}'.")
    return min(candidates, key=lambda item: abs(item - reference_start))

def parse_forexfactory_html_events(
    html: str,
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    """Internal helper for parse forexfactory html events."""
    parser = ForexFactoryHTMLCalendarParser()
    parser.feed(html)
    parser.close()

    timezone_info = _extract_forexfactory_timezone(html)
    normalized_events: List[Dict[str, Any]] = []

    for row in parser.rows:
        currency = str(row.get("currency") or "").strip().upper()
        title = str(row.get("title") or "").strip()

        # Structural/helper rows may share the calendar-row CSS class but are not
        # economic event records. Ignore rows without an event title before the
        # provider-ID requirement is enforced.
        if not title:
            continue

        if currency not in FX_CURRENCY_CODES and currency != "ALL":
            raise ProviderError(f"Unsupported ForexFactory currency '{currency}'.")

        event_id = str(row.get("id") or "").strip()
        if not event_id:
            raise ProviderError("ForexFactory calendar event has no provider ID.")

        event_date = _parse_forexfactory_date(str(row.get("date") or ""), start, end)
        parsed_time = _parse_forexfactory_time(str(row.get("time") or ""))
        if parsed_time is None:
            # A titled event without a concrete clock is not safely timestampable.
            # Fail closed so "Tentative", "All Day", an empty clock, or another
            # malformed value can never be turned into a fabricated event time.
            raise ProviderError(
                f"ForexFactory event '{event_id}' has no concrete provider time."
            )
        hour, minute = parsed_time
        local_datetime = event_date.replace(
            hour=hour,
            minute=minute,
            tzinfo=timezone_info,
        )

        normalized_events.append({
            "id": event_id,
            "dateline": int(local_datetime.timestamp()),
            "currency": currency,
            "name": title,
            "impactName": str(row.get("impact") or "").replace(" Impact Expected", "").strip(),
            "actual": str(row.get("actual") or "").strip() or None,
            "forecast": str(row.get("forecast") or "").strip() or None,
            "previous": str(row.get("previous") or "").strip() or None,
        })

    return normalized_events

def extract_days_payload(html: str) -> str:
    """Internal helper for extract days payload."""
    match = re.search(r"[\"']days[\"']\s*:\s*\[", html, re.IGNORECASE)
    if not match:
        raise ProviderError("ForexFactory response has no structured days payload.")
    payload_start = match.end() - 1
    try:
        decoded, end_offset = json.JSONDecoder().raw_decode(
            html[payload_start:]
        )
    except json.JSONDecodeError as exc:
        raise ProviderError(
            f"Malformed ForexFactory days payload: {exc}"
        ) from exc
    if not isinstance(decoded, list):
        raise ProviderError("ForexFactory days payload is not a list.")
    return html[payload_start:payload_start + end_offset]

def parse_calendar_days(payload: str) -> List[Dict[str, Any]]:
    """Internal helper for parse calendar days."""
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Malformed provider JSON: {exc}") from exc
    if not isinstance(parsed, list):
        raise ProviderError("ForexFactory days payload is not a list.")
    return parsed

def _parse_forexfactory_time(time_text: str) -> Optional[Tuple[int, int]]:
    """Parse only a concrete provider clock; never synthesize midnight."""
    cleaned = " ".join(time_text.split()).lower()
    match = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)", cleaned)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 12 or minute > 59:
        raise ProviderError(f"Invalid ForexFactory event time '{time_text}'.")
    if match.group(3) == "pm" and hour < 12:
        hour += 12
    if match.group(3) == "am" and hour == 12:
        hour = 0
    return hour, minute
