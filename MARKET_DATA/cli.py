"""Market Data CLI parsing and execution."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from typing import Sequence
from .models import MarketDataRequest, SUPPORTED_TIMEFRAMES
from .provider import create_provider
from .service import update_market_data

def build_argument_parser():
    parser=argparse.ArgumentParser(description="Acquire, normalize and persist market data.")
    parser.add_argument("--symbol",required=True)
    parser.add_argument("--timeframes",nargs="+",required=True)
    parser.add_argument("--starttime")
    parser.add_argument("--endtime")
    parser.add_argument("--lastcandle",action="store_true")
    parser.add_argument("--live",action="store_true")
    parser.add_argument("--debug",action="store_true")
    return parser

def normalize_symbol(symbol):
    value=symbol.strip()
    if not value: raise ValueError("symbol cannot be empty")
    if any(ch in value for ch in "/\\\x00"): raise ValueError("unsafe symbol")
    return value.upper()

def normalize_timeframe(timeframe):
    value=timeframe.strip().upper()
    if value not in SUPPORTED_TIMEFRAMES: raise ValueError(f"unsupported timeframe: {timeframe}")
    return value

def parse_iso8601(value):
    try: parsed=datetime.fromisoformat(value.strip().replace("Z","+00:00"))
    except ValueError as exc: raise ValueError(f"invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None: raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)

def validate_request(request):
    if not request.timeframes: raise ValueError("at least one timeframe is required")
    if len(set(request.timeframes)) != len(request.timeframes): raise ValueError("duplicate timeframe")
    if request.last_candle_only and (request.start_time or request.end_time): raise ValueError("--lastcandle is mutually exclusive with boundaries")
    if request.start_time and request.end_time and request.start_time>request.end_time: raise ValueError("starttime must not exceed endtime")

def parse_market_data_request(argv: Sequence[str]|None=None):
    args=build_argument_parser().parse_args(argv)
    request=MarketDataRequest(normalize_symbol(args.symbol),[normalize_timeframe(x) for x in args.timeframes],parse_iso8601(args.starttime) if args.starttime else None,parse_iso8601(args.endtime) if args.endtime else None,args.lastcandle,args.live,args.debug)
    validate_request(request); return request

def run(request):
    provider=create_provider("yahoo_charts")
    try: update_market_data(request,provider); return 0
    except Exception as exc:
        if request.debug: print(f"ERROR: {exc}",file=__import__("sys").stderr)
        else: print(f"ERROR: {exc}",file=__import__("sys").stderr)
        return 1
