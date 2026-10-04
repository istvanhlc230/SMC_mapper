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
    """Internal helper: _normalize_forexfactory_impact_value performs the focused normalize forexfactory impact value step in the Calendar implementation."""
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
    """Internal helper: _classify_forexfactory_impact performs the focused classify forexfactory impact step in the Calendar implementation."""
    for class_name in classes:
        lowered = class_name.lower()
        if lowered.endswith("--high") or lowered in {"high", "icon--ff-impact-red"}:
            return "high"
        if lowered.endswith("--medium") or lowered in {
            "medium", "med", "icon--ff-impact-orange", "icon--ff-impact-ora"
        }:
            return "medium"
        if lowered.endswith("--low") or lowered in {
            "low",
            "icon--ff-impact-yellow",
            "icon--ff-impact-yel",
            "icon--ff-impact-green",
            "icon--ff-impact-grn",
        }:
            return "low"
        if lowered in {
            "holiday",
            "non-economic",
            "icon--ff-impact-grey",
            "icon--ff-impact-gray",
            "icon--ff-impact-gry",
        }:
            return "holiday"
    return ""

class ForexFactoryHTMLCalendarParser(HTMLParser):
    def __init__(self) -> None:
        """Internal helper: __init__ performs the focused init   step in the Calendar implementation."""
        super().__init__(convert_charrefs=True)
        self.rows: List[Dict[str, Any]] = []
        self.current_row: Optional[Dict[str, Any]] = None
        self.current_cell: Optional[str] = None
        self.text_buffer: List[str] = []
        self.capture_title = False
        self.last_date_text = ""
        self.last_time_text = ""

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Calendar operation: handle_starttag performs the focused handle starttag step in the Calendar implementation."""
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
        """Calendar operation: handle_endtag performs the focused handle endtag step in the Calendar implementation."""
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
            if time_text and re.search(r"\d{1,2}:\d{2}\s*(?:am|pm)", time_text, re.IGNORECASE):
                self.last_time_text = time_text
            elif not time_text:
                row["time"] = self.last_time_text
            self.rows.append(row)

    def handle_data(self, data: str) -> None:
        """Calendar operation: handle_data performs the focused handle data step in the Calendar implementation."""
        if self.current_row is not None:
            self.text_buffer.append(data)

def _extract_forexfactory_timezone(html: str) -> timezone:
    """Internal helper: _extract_forexfactory_timezone performs the focused extract forexfactory timezone step in the Calendar implementation."""
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
    """Internal helper: _parse_forexfactory_date performs the focused parse forexfactory date step in the Calendar implementation."""
    date_text: str,
    reference_start: datetime,
    reference_end: datetime,
) -> datetime:
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
    """Calendar operation: parse_forexfactory_html_events performs the focused parse forexfactory html events step in the Calendar implementation."""
    html: str,
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
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
            # ForexFactory publishes legitimate all-day/tentative rows (for
            # example bank holidays) without a concrete clock. The canonical
            # Calendar event contract requires an exact timestamp, so these
            # rows are intentionally excluded rather than synthesized at
            # midnight or allowed to invalidate the whole provider response.
            continue
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
    """Calendar operation: extract_days_payload performs the focused extract days payload step in the Calendar implementation."""
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
    """Calendar operation: parse_calendar_days performs the focused parse calendar days step in the Calendar implementation."""
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
