# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar configuration and implementation constants."""

# FOREXFACTORY_URL — ForexFactory economic-calendar endpoint.
FOREXFACTORY_URL = "https://www.forexfactory.com/calendar"
# FOREXFACTORY_DETAIL_URL — provider event-detail JSON endpoint template.
FOREXFACTORY_DETAIL_URL = "https://www.forexfactory.com/calendar/details/1-{event_id}"
# LSE_API_URL — London Strategic Edge economic-calendar REST endpoint.
LSE_API_URL = "https://api.londonstrategicedge.com/vault/ref/economic_calendar"
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
__version__ = "2.8.0"

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
HELP_TEXT = f"""Calendar CLI v{__version__} (schema {SCHEMA_VERSION})

Usage:
  python calendar.py SYMBOL SCOPE [refresh] [--table] [--debug]
  python calendar.py SYMBOL --last-update [--table]
  python calendar.py delete [SYMBOL SCOPE]
  python calendar.py --help

Scopes (UTC):
  DATE | DATE HH:MM | DATE-DATE | DATE HH:MM-DATE HH:MM
  TIME | TIME-TIME (today); DATE[ HH:MM]- (through now)
  -DATE[ HH:MM] (from latest stored event)
  today | tomorrow | yesterday
  current/next/prev [day|week|month] | latest | news

Options:
  --table       Tables instead of JSON
  --debug       Diagnostics/tracebacks to stderr
  --last-update Show last successful provider update times

SYMBOL: Supported FX pair, currency, or Yahoo ticker; providers are selected automatically.
refresh: Trailing modifier for provider refresh; not valid with latest, next, prev, or news.
"""


class CalendarInputError(Exception):
    """Invalid CLI or Calendar input."""


class ProviderError(Exception):
    """External provider acquisition or parsing failure."""


class YahooForexPairUnavailable(Exception):
    """Yahoo does not expose a verified Forex instrument for a pair."""


class DataIntegrityError(Exception):
    """Persistent Calendar data integrity violation."""
