# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Human-readable and machine-readable Calendar output."""

import json
import re
import textwrap
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

from html import unescape

from .config import DataIntegrityError
from .domain import normalize_provider_fields

# Presentation state is output-local: rendered lines are derived from the supplied event/details records.

class _DetailTextParser(HTMLParser):
    def __init__(self) -> None:
        """Internal helper: Handle init  ."""
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Handle starttag."""
        if tag.lower() == "br":
            self.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Handle startendtag."""
        if tag.lower() == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        """Handle endtag."""
        if tag.lower() in {"p", "div", "li", "tr", "table", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        """Handle data."""
        self.parts.append(data)

def _detail_html_to_text(value: str) -> str:
    """Internal helper: Handle html to text."""
    # ForexFactory may return Detail HTML with markup escaped one or more times.
    # Decode to a stable representation before parsing so literal and escaped
    # provider markup are treated identically. HTMLParser then handles tags
    # reliably instead of relying on provider-specific regular expressions.
    text = value
    for _ in range(3):
        decoded = unescape(text)
        if decoded == text:
            break
        text = decoded

    parser = _DetailTextParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise DataIntegrityError(f"Invalid ForexFactory Detail HTML: {exc}") from exc

    text = "".join(parser.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def format_table_details(
    details: Dict[str, Any],
    source: str = "unknown",
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str, str]]]:
    """Return canonical detail rows and provider-specific field rows."""
    preferred_keys = ("currency", "impact", "actual", "forecast", "previous")
    detail_rows: List[Tuple[str, str]] = []
    for key in preferred_keys:
        if key in details:
            detail_rows.append((key.replace("_", " ").title(), _display_value(details[key])))

    # ForexFactory Detail specifications are ordered provider fields, not event
    # fields. Sanitize HTML before turning each specification into a table row.
    for spec in details.get("specs", []):
        title = _detail_html_to_text(str(spec.get("title", "")))
        title = re.sub(r"\s+", " ", title).strip()
        value = _detail_html_to_text(str(spec.get("html", "")))
        detail_rows.append((title or "Provider Detail", value or "N/A"))

    extra_keys = sorted(
        key for key in details
        if key not in preferred_keys and key not in {"specs", "provider_fields"}
    )
    detail_rows.extend(
        (key.replace("_", " ").title(), _display_value(details[key]))
        for key in extra_keys
    )

    provider_labels = {
        "lse": "LSE",
        "forexfactory": "ForexFactory",
        "yahoo_finance": "Yahoo Finance",
    }
    normalized_provider_fields = normalize_provider_fields(
        details.get("provider_fields"),
        source,
    )
    provider_rows: List[Tuple[str, str, str]] = []
    for provider_name in sorted(normalized_provider_fields):
        provider_label = provider_labels.get(provider_name, provider_name)
        for field_name in sorted(normalized_provider_fields[provider_name]):
            provider_rows.append((
                provider_label,
                str(field_name).replace("_", " ").title(),
                _display_value(normalized_provider_fields[provider_name][field_name]),
            ))
    return detail_rows, provider_rows


def _display_value(value: Any) -> str:
    """Convert a field value into deterministic, readable table-cell text."""
    if value is None:
        return "N/A"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def render_ascii_table(
    headers: List[str],
    rows: List[List[Any]],
    max_widths: Optional[List[int]] = None,
) -> List[str]:
    """Render an ASCII table with wrapped cells and deterministic column widths."""
    if not headers:
        return []

    column_count = len(headers)
    normalized_rows: List[List[str]] = []
    for row in rows:
        values = [_display_value(value) for value in row]
        if len(values) < column_count:
            values.extend([""] * (column_count - len(values)))
        normalized_rows.append(values[:column_count])

    limits = max_widths or [48] * column_count
    if len(limits) < column_count:
        limits = list(limits) + [48] * (column_count - len(limits))

    widths: List[int] = []
    for column_index, header in enumerate(headers):
        candidates = [header]
        for row in normalized_rows:
            candidates.extend(row[column_index].splitlines() or [""])
        natural_width = max((len(candidate) for candidate in candidates), default=1)
        widths.append(max(1, min(natural_width, limits[column_index])))

    def wrapped_cells(row: List[str]) -> List[List[str]]:
        wrapped_row: List[List[str]] = []
        for column_index, value in enumerate(row):
            width = widths[column_index]
            paragraphs = value.splitlines() or [""]
            cell_lines: List[str] = []
            for paragraph in paragraphs:
                wrapped = textwrap.wrap(
                    paragraph,
                    width=width,
                    replace_whitespace=True,
                    drop_whitespace=True,
                    break_long_words=True,
                    break_on_hyphens=False,
                )
                cell_lines.extend(wrapped or [""])
            wrapped_row.append(cell_lines or [""])
        return wrapped_row

    def border() -> str:
        return "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def render_row(row: List[str]) -> List[str]:
        cell_lines = wrapped_cells(row)
        line_count = max(len(lines) for lines in cell_lines)
        rendered: List[str] = []
        for line_index in range(line_count):
            cells: List[str] = []
            for column_index in range(column_count):
                cell_value = (
                    cell_lines[column_index][line_index]
                    if line_index < len(cell_lines[column_index])
                    else ""
                )
                cells.append(cell_value.ljust(widths[column_index]))
            rendered.append("| " + " | ".join(cells) + " |")
        return rendered

    output = [border(), *render_row(headers), border()]
    for row in normalized_rows:
        output.extend(render_row(row))
        output.append(border())
    return output


def output_last_updates_table(status: str, symbol: str, updates: List[Dict[str, Any]]) -> None:
    """Print last-update metadata as a compact provider table."""
    print(f"CALENDAR RESULT | {status} | {symbol}")
    rows = [
        [item["provider"], item["last_successful_at"] or "N/A"]
        for item in updates
    ]
    if rows:
        for line in render_ascii_table(
            ["Provider", "Last Successful Update (UTC)"],
            rows,
            [20, 32],
        ):
            print(line)
    else:
        print("No provider update records.")


def output_refresh_summary(summary: Dict[str, Any]) -> None:
    """Print refresh totals as a small table."""
    print("REFRESH SUMMARY")
    for line in render_ascii_table(
        ["Metric", "Count"],
        [
            ["Added", summary["added"]],
            ["Changed", summary["changed"]],
            ["Unchanged", summary["unchanged"]],
        ],
        [14, 12],
    ):
        print(line)


def sanitize_provider_results(
    provider_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return provider result metadata safe for normal public output."""
    return [
        {
            key: value
            for key, value in provider.items()
            if key != "error"
        }
        for provider in provider_results
        if provider.get("status") != "ERROR"
    ]


def output_query_result(
    status: str,
    symbol: str,
    events: List[Dict[str, Any]],
    provider_results: List[Dict[str, Any]],
    table: bool = False,
) -> None:
    """Render either tabular terminal output or the default JSON response."""
    public_provider_results = sanitize_provider_results(provider_results)

    if table:
        print(f"CALENDAR RESULT | {status} | {symbol}")
        for provider in public_provider_results:
            print(f"PROVIDER | {provider['provider']} | {provider['status']}")
        if not events:
            print("No matching events.")
            return

        print()
        print(f"EVENTS | {len(events)}")
        summary_rows = []
        for event in events:
            details = event.get("details", {})
            summary_rows.append([
                event.get("timestamp", "N/A"),
                details.get("currency") or event.get("symbol", "N/A"),
                details.get("impact") or "N/A",
                event.get("source", "N/A"),
                event.get("title", "N/A"),
            ])
        for line in render_ascii_table(
            ["Timestamp (UTC)", "Currency", "Impact", "Source", "Event"],
            summary_rows,
            [20, 10, 10, 16, 48],
        ):
            print(line)

        for index, event in enumerate(events, start=1):
            print()
            print(f"EVENT DETAILS | {index:02d} | {event.get('title', 'N/A')}")
            detail_rows: List[List[Any]] = [
                ["Timestamp (UTC)", event.get("timestamp", "N/A")],
                ["Type", event.get("event_type", "N/A")],
                ["Source", event.get("source", "N/A")],
                ["Symbol", event.get("symbol", "N/A")],
                ["Title", event.get("title", "N/A")],
                ["Event ID", event.get("event_id", "N/A")],
            ]
            normalized_detail_rows, provider_rows = format_table_details(
                event.get("details", {}),
                source=str(event.get("source", "unknown")),
            )
            detail_rows.extend([[field, value] for field, value in normalized_detail_rows])
            for line in render_ascii_table(["Field", "Value"], detail_rows, [24, 72]):
                print(line)

            if provider_rows:
                print("PROVIDER FIELDS")
                for line in render_ascii_table(
                    ["Provider", "Field", "Value"],
                    [list(row) for row in provider_rows],
                    [16, 28, 64],
                ):
                    print(line)
        return

    print(json.dumps({
        "status": status,
        "symbol": symbol,
        "events": events,
        "providers": public_provider_results,
    }, ensure_ascii=False))
