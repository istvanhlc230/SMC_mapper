# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar configuration and implementation constants."""

# FOREXFACTORY_URL — ForexFactory economic-calendar endpoint.
FOREXFACTORY_URL = "https://www.forexfactory.com/calendar"
# FOREXFACTORY_DETAIL_URL — provider event-detail JSON endpoint template.
FOREXFACTORY_DETAIL_URL = "https://www.forexfactory.com/calendar/details/1-{event_id}"
# YAHOO_SEARCH_URL — Yahoo Finance search endpoint.
YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
# USER_AGENT — HTTP User-Agent sent to providers.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)
# HTTP_TIMEOUT — provider HTTP timeout in seconds.
HTTP_TIMEOUT = 15.0
# SCHEMA_VERSION — persistent calendar.json schema version.
SCHEMA_VERSION = 2
# __version__ — Calendar CLI implementation version, independent from SCHEMA_VERSION.
__version__ = "2.4.4"

# SUPPORTED_CURRENCIES — standalone currencies accepted by the CLI.
SUPPORTED_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CHF",
    "AUD", "CAD", "NZD", "CNY", "HUF",
    "HKD", "SGD", "INR", "MXN", "PHP", "IDR", "THB", "MYR",
    "ZAR", "RUB", "BRL", "NOK", "QAR",
}

# ISO 4217 alpha-3 currency codes are used to recognize a six-letter
# candidate as an FX pair. Yahoo remains authoritative for whether the
# concrete pair actually exists as a Forex instrument.
# FX_CURRENCY_CODES — currency-code universe used for six-letter FX recognition.
FX_CURRENCY_CODES = {
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV",
    "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF",
    "CHW", "CLF", "CLP", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE",
    "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "FJD",
    "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD",
    "HNL", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD",
    "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD",
    "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA",
    "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV",
    "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB",
    "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB",
    "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL",
    "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT",
    "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USN",
    "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAF",
    "XCD", "XOF", "XPF", "YER", "ZAR", "ZMW", "ZWG",
}

# USD_BASE_YAHOO_SYMBOLS — explicit USD-base Yahoo FX representations.
USD_BASE_YAHOO_SYMBOLS = {
    "USDJPY": "JPY=X",
    "USDCHF": "CHF=X",
    "USDCAD": "CAD=X",
    "USDCNY": "CNY=X",
    "USDHKD": "HKD=X",
    "USDSGD": "SGD=X",
    "USDINR": "INR=X",
    "USDMXN": "MXN=X",
    "USDPHP": "PHP=X",
    "USDIDR": "IDR=X",
    "USDTHB": "THB=X",
    "USDMYR": "MYR=X",
    "USDZAR": "ZAR=X",
    "USDRUB": "RUB=X",
}

# DATE_RE — canonical YYYY.MM.DD date expression.
DATE_RE = r"\d{4}\.\d{2}\.\d{2}"
# TIME_RE — canonical HH:MM time expression.
TIME_RE = r"\d{2}:\d{2}"

# HELP_TEXT — CLI help text containing software/schema versions.
HELP_TEXT = f"""Calendar CLI v{__version__} (schema {SCHEMA_VERSION}) - unified economic calendar and news update engine

USAGE
  python calendar.py SYMBOL YYYY.MM.DD
  python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
  python calendar.py SYMBOL YYYY.MM.DD@HH:MM
  python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
  python calendar.py SYMBOL current
  python calendar.py SYMBOL latest
  python calendar.py SYMBOL next
  python calendar.py SYMBOL --date YYYY.MM.DD [--time HH:MM]
  python calendar.py SYMBOL --time HH:MM
  python calendar.py SYMBOL --last-update
  python calendar.py refresh SYMBOL --date YYYY.MM.DD [--time HH:MM]
  python calendar.py refresh SYMBOL --time HH:MM
  python calendar.py refresh SYMBOL YYYY.MM.DD --time HH:MM
  python calendar.py refresh SYMBOL YYYY.MM.DD
  python calendar.py refresh SYMBOL YYYY.MM.DD-YYYY.MM.DD
  python calendar.py refresh SYMBOL YYYY.MM.DD@HH:MM
  python calendar.py refresh SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
  python calendar.py refresh SYMBOL <scope> --cleartext
  python calendar.py refresh SYMBOL <scope> --debug
  python calendar.py delete
  python calendar.py delete --debug
  python calendar.py delete SYMBOL YYYY.MM.DD
  python calendar.py delete SYMBOL YYYY.MM.DD-YYYY.MM.DD
  python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM
  python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
  python calendar.py delete SYMBOL --time HH:MM
  python calendar.py delete SYMBOL YYYY.MM.DD --time HH:MM
  python calendar.py SYMBOL <scope> --cleartext
  python calendar.py SYMBOL <scope> --debug
  python calendar.py SYMBOL <scope> --cleartext --debug
  python calendar.py --help

FLAGS
  --cleartext  Human-readable presentation only; does not change data.
  --debug      Emit diagnostic exception/traceback output to stderr only.
  --date YYYY.MM.DD Query/refresh/delete date shorthand. With --time, forms
                the canonical YYYY.MM.DD@HH:MM scope; without --time, selects
                the exact UTC calendar day.
  --time HH:MM Query/refresh/delete time shorthand. Without --date, HH:MM is
                resolved on the current UTC calendar day.
  --last-update  Read the last successful provider update time for SYMBOL from
                committed Calendar watermarks. Read-only; no provider call.

SCOPE
  YYYY.MM.DD                         Exact UTC calendar day.
  YYYY.MM.DD-YYYY.MM.DD              Inclusive UTC date range.
  YYYY.MM.DD@HH:MM                   Exact UTC minute.
  YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM  Half-open UTC datetime range.
  current                             Incremental update from each
                                      provider+canonical-symbol watermark
                                      through current UTC time.
  latest                              Return the most recent past/current event for
                                      SYMBOL from the committed calendar cache.
  next                                Return the nearest future event for
                                      SYMBOL from the committed calendar cache.

SYMBOL
  Supported FX pair, standalone supported currency, or Yahoo ticker.
  Provider selection is automatic.

PROVIDERS
  ForexFactory -> primary economic-calendar events.
  Yahoo Finance -> complementary news.

CURRENT
  current is not "event at the current minute" and not "next".
  It loads each applicable provider+canonical-symbol watermark, performs
  incremental acquisition, normalizes/deduplicates, atomically persists,
  and returns events newer than the watermark through now.
  Missing watermark -> BOOTSTRAP_REQUIRED. No timestamp is fabricated.

LATEST
  latest is a read-only most-recent-event lookup.
  It reads only the committed calendar.json snapshot, filters events visible
  for SYMBOL, keeps only timestamps at or before current UTC time, selects the
  most recent event deterministically by timestamp, source, and event identity,
  and never calls a provider or changes persistent state.
  No past/current event -> NO_LATEST_EVENT.

LAST UPDATE
  --last-update is a read-only watermark lookup. It reads last_successful_at
  for each applicable provider+canonical-symbol watermark from calendar.json,
  never calls a provider, and never changes persistent state. Missing provider
  watermark is reported explicitly as NO_LAST_UPDATE.

NEXT
  next is a read-only nearest-future-event lookup.
  It reads only the committed calendar.json snapshot, filters events visible
  for SYMBOL, keeps only timestamps strictly later than current UTC time,
  sorts chronologically, and returns the first event.
  next never calls a provider, never changes coverage, and never changes
  watermarks. No future event -> NO_NEXT_EVENT.

OUTPUT
  Default output is JSON. --cleartext changes presentation only.

ERRORS
  Invalid syntax and unsupported symbols are rejected explicitly.
  Provider failures are never converted to successful empty data.
"""


class CalendarInputError(Exception):
    """Invalid CLI or Calendar input."""


class ProviderError(Exception):
    """External provider acquisition or parsing failure."""


class YahooForexPairUnavailable(Exception):
    """Yahoo does not expose a verified Forex instrument for a pair."""


class DataIntegrityError(Exception):
    """Persistent Calendar data integrity violation."""
