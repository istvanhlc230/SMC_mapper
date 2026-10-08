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
__version__ = "2.6.1"

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
  python calendar.py SYMBOL --date YYYY.MM.DD [--time HH:MM] [refresh]
  python calendar.py SYMBOL --time HH:MM [refresh]
  python calendar.py SYMBOL HH:MM-HH:MM [refresh]
  python calendar.py SYMBOL --range YYYY.MM.DD- [refresh]
  python calendar.py SYMBOL --range YYYY.MM.DD@HH:MM- [refresh]
  python calendar.py SYMBOL --range -YYYY.MM.DD [refresh]
  python calendar.py SYMBOL --range -YYYY.MM.DD@HH:MM [refresh]
  python calendar.py SYMBOL --last-update
  python calendar.py delete
  python calendar.py delete SYMBOL <scope>
  python calendar.py delete SYMBOL --date YYYY.MM.DD [--time HH:MM]
  python calendar.py delete SYMBOL --time HH:MM
  python calendar.py --help
FLAGS
  --cleartext  Human-readable presentation only; does not change data.
  --debug      Emit diagnostic exception/traceback output to stderr only.
  --date YYYY.MM.DD Query/refresh/delete date shorthand. With --time, forms
                the canonical YYYY.MM.DD@HH:MM scope; without --time, selects
                the exact UTC calendar day.
  --time HH:MM Query/refresh/delete time shorthand. Without --date, HH:MM is
                resolved on the current UTC calendar day.
  --range RANGE  Explicit/open-ended query/refresh range. Supported forms:
                START-, START-END, and -END, where START/END are
                YYYY.MM.DD or YYYY.MM.DD@HH:MM. START- ends at current UTC
                time; -END starts from the latest recorded visible event.
  --last-update  Read the last successful provider update time for SYMBOL from
                committed Calendar watermarks. Read-only; no provider call.

SCOPE
  YYYY.MM.DD                         Exact UTC calendar day.
  YYYY.MM.DD-YYYY.MM.DD              Inclusive UTC date range.
  YYYY.MM.DD@HH:MM                   Exact UTC minute.
  YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM  Half-open UTC datetime range.
  HH:MM-HH:MM                       Current UTC day time range. Canonicalized
                                      to YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM.
  current                             Return events currently active in the UTC
                                      activity minute. Read-only; no provider call.
  current day                        Exact current UTC calendar day.
  current week                       Current ISO week (Monday-Sunday UTC).
  current month                      Current UTC calendar month.
  today                               Exact current UTC calendar day.
  tomorrow                            Exact next UTC calendar day.
  yesterday                           Exact previous UTC calendar day.
  latest                              Return the most recent past/current event for
                                      SYMBOL from the committed calendar cache.
  next                                Return the nearest future scheduled economic
                                      event for SYMBOL from ForexFactory cache.
  next day/week/month                 Return all events in the next UTC day/week/month.
  prev                                Return the nearest past scheduled economic event.
  prev day/week/month                 Return all events in the previous UTC day/week/month.
  news                                Report whether a scheduled economic news event
                                      is active in the current UTC minute.

SYMBOL
  Supported FX pair, standalone supported currency, or Yahoo ticker.
  Provider selection is automatic.

PROVIDERS
  LSE -> economic-calendar events.
  ForexFactory -> independent economic-calendar events.
  Yahoo Finance -> complementary current/history news.

CURRENT
  current is an active-event query over the committed Calendar cache.
  An event is active from its canonical timestamp through the end of that UTC minute.
  current never calls providers and never changes calendar.json, coverage, or watermarks.

REFRESH MODIFIER
  refresh is a trailing modifier, not an independent command or scope.
  Example: python calendar.py EURUSD today refresh
  It forces provider re-acquisition for the timespan represented by the scope,
  merges changed/new records, and preserves existing coverage and watermarks.
  The normal query result for the same scope is returned after refresh.
  JSON output includes a refresh summary with added/changed/unchanged counts.
  refresh is valid with current day/week/month, today, tomorrow, yesterday,
  explicit date/datetime scopes, and both open-start --range -END and open-end --range START- forms.
  current, latest, next, prev, and news cannot be combined with refresh.
  CLI refresh may block on provider I/O; the Monitor must invoke the underlying
  refresh operation asynchronously and outside its candle-close processing path.

RELATIVE DAYS
  today, tomorrow, and yesterday are exact UTC calendar-day scopes.
  They are resolved at execution time from Calendar's utc_now() clock.
  today = current UTC day; tomorrow = next UTC day; yesterday = previous UTC day.
  They use the same acquisition/query interval semantics as YYYY.MM.DD and
  are valid for normal query, explicit refresh, and scoped delete.

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
  next is a read-only nearest-future scheduled-economic-event lookup.
  It reads only the committed calendar.json snapshot, filters visible
  ForexFactory economic events for SYMBOL, keeps only timestamps strictly
  later than current UTC time, sorts chronologically, and returns the first event.
  next never calls a provider, never changes coverage, and never changes
  watermarks. No future event -> NO_NEXT_EVENT.

OUTPUT
  Default output is JSON. --cleartext changes presentation only.

ERRORS
  Invalid syntax and unsupported symbols are rejected explicitly.
  Provider failures are never converted to successful empty data.
  For current, provider error details are diagnostic-only and are not included
  in normal stdout; aggregate failure status remains machine-readable.
"""


class CalendarInputError(Exception):
    """Invalid CLI or Calendar input."""


class ProviderError(Exception):
    """External provider acquisition or parsing failure."""


class YahooForexPairUnavailable(Exception):
    """Yahoo does not expose a verified Forex instrument for a pair."""


class DataIntegrityError(Exception):
    """Persistent Calendar data integrity violation."""
