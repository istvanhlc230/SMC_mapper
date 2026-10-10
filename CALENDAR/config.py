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
__version__ = "2.6.8"

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
  python calendar.py SYMBOL <scope> [refresh]
  python calendar.py SYMBOL --last-update
  python calendar.py delete
  python calendar.py delete SYMBOL <scope>
  python calendar.py --help
FLAGS
  --cleartext    Human-readable presentation only; does not change stored data.
  --debug        Emit diagnostic exceptions/tracebacks to stderr only.
  --last-update  Read last successful provider update times; no provider call.
  --help         Show this help.

SCOPE
  YYYY.MM.DD                         Exact UTC calendar day.
  YYYY.MM.DD HH:MM                   Exact UTC minute.
  YYYY.MM.DD-YYYY.MM.DD              Inclusive UTC date range.
  YYYY.MM.DD HH:MM-YYYY.MM.DD HH:MM  Half-open UTC datetime range.
  HH:MM                              Exact minute on the current UTC day.
  HH:MM-HH:MM                        Half-open range within the current UTC day.
  YYYY.MM.DD-                        From that date through current UTC time.
  YYYY.MM.DD HH:MM-                  From that minute through current UTC time.
  HH:MM-                             From that time today through current UTC time.
  -YYYY.MM.DD                        From latest recorded visible event through that date.
  -YYYY.MM.DD HH:MM                  From latest recorded visible event through that minute.
  -HH:MM                             From latest recorded visible event through that minute today.
  current                            Events active in the current UTC minute.
  current day/week/month             Current UTC day, week, or month.
  today/tomorrow/yesterday           Corresponding UTC calendar day.
  next                                Nearest future scheduled economic event.
  next day/week/month                 Events in the following UTC period.
  prev                                Nearest previous scheduled economic event.
  prev day/week/month                 Events in the previous UTC period.
  latest                              Most recent past/current cached event.
  news                                Active news lookup.

SYMBOL
  Supported FX pair, standalone supported currency, or Yahoo ticker.
  Provider selection is automatic.

REFRESH
  refresh is a trailing modifier, not an independent command or scope.
  Example: python calendar.py EURUSD 2026.10.10 refresh
  Plain open-start scopes are cache-only; adding refresh requests provider acquisition.
  current refresh is permitted; latest, next, prev, and news reject refresh.

OUTPUT
  Default output is JSON. --cleartext changes presentation only.

ERRORS
  Invalid syntax and unsupported symbols are rejected explicitly.
  Provider failures are never converted to successful empty data.
  Normal output does not expose provider exception details.
"""



class CalendarInputError(Exception):
    """Invalid CLI or Calendar input."""


class ProviderError(Exception):
    """External provider acquisition or parsing failure."""


class YahooForexPairUnavailable(Exception):
    """Yahoo does not expose a verified Forex instrument for a pair."""


class DataIntegrityError(Exception):
    """Persistent Calendar data integrity violation."""
