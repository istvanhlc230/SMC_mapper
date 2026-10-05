# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Human-readable and machine-readable Calendar output."""

import json
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

from html import unescape

from .config import DataIntegrityError

# Presentation state is output-local: rendered lines are derived from the supplied event/details records.

class _DetailTextParser(HTMLParser):
    def __init__(self) -> None:
        """Internal helper: __init__ performs the focused init   step in the Calendar implementation."""
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Calendar operation: handle_starttag performs the focused handle starttag step in the Calendar implementation."""
        if tag.lower() == "br":
            self.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Calendar operation: handle_startendtag performs the focused handle startendtag step in the Calendar implementation."""
        if tag.lower() == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        """Calendar operation: handle_endtag performs the focused handle endtag step in the Calendar implementation."""
        if tag.lower() in {"p", "div", "li", "tr", "table", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        """Calendar operation: handle_data performs the focused handle data step in the Calendar implementation."""
        self.parts.append(data)

def _detail_html_to_text(value: str) -> str:
    """Internal helper: _detail_html_to_text performs the focused detail html to text step in the Calendar implementation."""
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

def format_cleartext_details(details: Dict[str, Any]) -> List[str]:
    """Render details without exposing the internal dictionary representation."""
    preferred_keys = ("currency", "impact", "actual", "forecast", "previous")
    ordered_keys = [key for key in preferred_keys if key in details]
    extra_keys = [
        key for key in details
        if key not in ordered_keys and key != "specs"
    ]
    ordered_keys.extend(sorted(extra_keys))

    lines: List[str] = []
    for key in ordered_keys:
        value = details[key]
        display = "N/A" if value is None else str(value)
        label = key.replace("_", " ").title()
        lines.append(f"  {label:<9}: {display}")

    for spec in details.get("specs", []):
        title = _detail_html_to_text(str(spec.get("title", "")))
        title = re.sub(r"\s+", " ", title).strip()
        content = _detail_html_to_text(str(spec.get("html", "")))
        lines.append(f"  {title:<9}: {content or 'N/A'}")
    return lines

def public_provider_results(
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
    cleartext: bool = False,
) -> None:
    """Calendar operation: output_query_result performs the focused output query result step in the Calendar implementation."""
    public_provider_results = public_provider_results(provider_results)

    if cleartext:
        print(f"CALENDAR RESULT | {status} | {symbol}")
        for provider in public_provider_results:
            print(f"PROVIDER | {provider['provider']} | {provider['status']}")
        if not events:
            print("No matching events.")
            return
        for index, event in enumerate(events, start=1):
            print(f"--- EVENT {index:02d} ------------------------------")
            print(f"Timestamp : {event['timestamp']}")
            print(f"Source    : {event['source']}")
            print(f"Type      : {event['event_type']}")
            print(f"Symbol    : {event['symbol']}")
            print(f"Title     : {event['title']}")
            print("Details   :")
            for detail_line in format_cleartext_details(event["details"]):
                print(detail_line)
            print(f"Event ID  : {event['event_id']}")
            print()
        return

    print(json.dumps({
        "status": status,
        "symbol": symbol,
        "events": events,
        "providers": public_provider_results,
    }, ensure_ascii=False))
