"""
Data Provider Abstraction for True SMC Mapper.
Supports: Alpaca, Tiingo, Twelve Data.
Each provider returns standardized candle dicts:
  {"time": str, "open": float, "high": float, "low": float, "close": float, "volume": int}
"""
import os
import json
import time
import urllib.request
import urllib.parse
from typing import List, Optional
from dataclasses import dataclass

# ============================================================
# PROVIDER CONFIG
# ============================================================

@dataclass
class DataRequest:
    """What the engine needs from any provider."""
    symbol: str
    interval: str          # "1min","5min","15min","1h","4h","1day"
    bar_count: int = 200   # how many bars to request
    end_time: Optional[str] = None  # ISO timestamp or None for latest


@dataclass  
class ProviderConfig:
    """Which provider to use and its credentials."""
    name: str              # "alpaca", "tiingo", "twelvedata"
    api_key: str
    api_secret: str = ""   # Alpaca needs key+secret
    base_url: str = ""     # Override for paper trading etc.


# ============================================================
# INTERVAL MAPS
# ============================================================

_TWELVE_INTERVALS = {
    "1min": "1min", "5min": "5min", "15min": "15min",
    "30min": "30min", "1h": "1h", "4h": "4h", "1day": "1day",
}

_ALPACA_INTERVALS = {
    "1min": "1Min", "5min": "5Min", "15min": "15Min",
    "30min": "30Min", "1h": "1Hour", "4h": "4Hour", "1day": "1Day",
}

_TIINGO_INTERVALS = {
    "1min": "1min", "5min": "5min", "15min": "15min",
    "30min": "30min", "1h": "1hour", "4h": "4hour", "1day": "1day",
}


# ============================================================
# HTTP HELPER
# ============================================================

def _http_get(url: str, headers: dict, timeout: int = 20, retries: int = 2) -> dict:
    req = urllib.request.Request(url, headers=headers)
    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"HTTP failed after {retries+1} attempts: {last_err}")


# ============================================================
# TWELVE DATA PROVIDER
# ============================================================

def fetch_twelvedata(cfg: ProviderConfig, req: DataRequest) -> List[dict]:
    interval = _TWELVE_INTERVALS.get(req.interval)
    if not interval:
        raise ValueError(f"Unsupported interval for Twelve Data: {req.interval}")

    params = urllib.parse.urlencode({
        "symbol": req.symbol,
        "interval": interval,
        "outputsize": req.bar_count,
        "apikey": cfg.api_key,
        "format": "JSON",
    })
    url = "https://api.twelvedata.com/time_series?" + params
    data = _http_get(url, {"User-Agent": "True-SMC/2.0", "Accept": "application/json"})

    if data.get("status") == "error":
        raise RuntimeError(f"Twelve Data: {data.get('message', 'unknown error')}")

    values = data.get("values")
    if not values:
        raise RuntimeError("Twelve Data: no candle data returned")

    candles = []
    seen = set()
    for x in reversed(values):
        t = x["datetime"]
        if t in seen:
            continue
        seen.add(t)
        candles.append({
            "time": t,
            "open": float(x["open"]),
            "high": float(x["high"]),
            "low": float(x["low"]),
            "close": float(x["close"]),
            "volume": int(float(x.get("volume", 0))),
        })
    return candles


# ============================================================
# ALPACA PROVIDER
# ============================================================

def fetch_alpaca(cfg: ProviderConfig, req: DataRequest) -> List[dict]:
    interval = _ALPACA_INTERVALS.get(req.interval)
    if not interval:
        raise ValueError(f"Unsupported interval for Alpaca: {req.interval}")

    base = cfg.base_url or "https://data.alpaca.markets"
    params = urllib.parse.urlencode({
        "timeframe": interval,
        "limit": req.bar_count,
        "adjustment": "raw",
        "feed": "sip",
        "sort": "asc",
    })
    url = f"{base}/v2/stocks/{req.symbol}/bars?{params}"
    headers = {
        "APCA-API-KEY-ID": cfg.api_key,
        "APCA-API-SECRET-KEY": cfg.api_secret,
        "Accept": "application/json",
    }
    data = _http_get(url, headers)

    bars = data.get("bars", [])
    if not bars:
        raise RuntimeError(f"Alpaca: no bars returned for {req.symbol}")

    candles = []
    seen = set()
    for b in bars:
        t = b["t"]
        if t in seen:
            continue
        seen.add(t)
        candles.append({
            "time": t,
            "open": float(b["o"]),
            "high": float(b["h"]),
            "low": float(b["l"]),
            "close": float(b["c"]),
            "volume": int(b.get("v", 0)),
        })
    return candles


# ============================================================
# TIINGO PROVIDER
# ============================================================

def fetch_tiingo(cfg: ProviderConfig, req: DataRequest) -> List[dict]:
    interval = _TIINGO_INTERVALS.get(req.interval)
    if not interval:
        raise ValueError(f"Unsupported interval for Tiingo: {req.interval}")

    # Tiingo IEX for intraday
    params = urllib.parse.urlencode({
        "resampleFreq": interval,
        "columns": "open,high,low,close,volume",
        "token": cfg.api_key,
    })
    url = f"https://api.tiingo.com/iex/{req.symbol}/prices?{params}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {cfg.api_key}",
    }
    data = _http_get(url, headers)

    if not isinstance(data, list) or len(data) == 0:
        raise RuntimeError(f"Tiingo: no data for {req.symbol}")

    candles = []
    seen = set()
    for b in data:
        t = b.get("date", "")
        if t in seen:
            continue
        seen.add(t)
        candles.append({
            "time": t,
            "open": float(b["open"]),
            "high": float(b["high"]),
            "low": float(b["low"]),
            "close": float(b["close"]),
            "volume": int(b.get("volume", 0)),
        })
    return candles


# ============================================================
# DEMO / SYNTHETIC PROVIDER
# ============================================================

def fetch_demo(cfg: ProviderConfig, req: DataRequest) -> List[dict]:
    import random
    from datetime import datetime, timedelta

    seed = sum(ord(c) * (idx + 1) for idx, c in enumerate(req.symbol))
    rng = random.Random(seed)

    base_prices = {
        "NVDA": 125.0, "MRVL": 68.0, "CRWD": 255.0, "CRM": 280.0, "PLTR": 26.0
    }
    price = base_prices.get(req.symbol, 100.0)

    candles = []
    start_time = datetime(2026, 8, 28, 9, 30) - timedelta(minutes=5 * req.bar_count)

    trend = 1.0
    for i in range(req.bar_count):
        if i % 45 == 0 and i > 0:
            trend *= -1.0

        volatility = price * 0.004
        delta = (rng.gauss(0.15 * trend, 1.0)) * volatility

        open_p = price
        close_p = price + delta
        high_p = max(open_p, close_p) + abs(rng.gauss(0, volatility * 0.5))
        low_p = min(open_p, close_p) - abs(rng.gauss(0, volatility * 0.5))

        if i % 15 == 0:
            if trend > 0:
                low_p -= volatility * 1.2
            else:
                high_p += volatility * 1.2

        t_str = (start_time + timedelta(minutes=5 * i)).strftime("%Y-%m-%d %H:%M:%S")
        candles.append({
            "time": t_str,
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": int(rng.randint(5000, 50000)),
        })
        price = close_p

    return candles


# ============================================================
# PROVIDER DISPATCHER
# ============================================================

_PROVIDERS = {
    "twelvedata": fetch_twelvedata,
    "alpaca": fetch_alpaca,
    "tiingo": fetch_tiingo,
    "demo": fetch_demo,
}

def fetch_candles(cfg: ProviderConfig, req: DataRequest) -> List[dict]:
    """Universal entry point. Returns chronologically ordered candles."""
    provider_fn = _PROVIDERS.get(cfg.name)
    if not provider_fn:
        raise ValueError(f"Unknown provider: {cfg.name}. Use: {list(_PROVIDERS.keys())}")
    return provider_fn(cfg, req)


def _load_config_file() -> dict:
    """Helper to load config.json if present."""
    cfg_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not parse config.json: {e}")
    return {}


def _load_env_file():
    """Helper to load key-value pairs from a local .env file into os.environ."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'").strip('"')
                    os.environ[k] = v


def auto_detect_provider() -> ProviderConfig:
    """Auto-detect provider from config.json, environment variables, or default to demo provider."""
    cfg_file = _load_config_file()
    api_keys = cfg_file.get("api_keys", {})
    chosen_provider = cfg_file.get("provider", "").lower()

    # 1. Check config.json settings
    if chosen_provider == "twelvedata":
        key = api_keys.get("twelvedata", "")
        if key and not key.startswith("YOUR_"):
            print(f"[INFO] Using Twelve Data Provider from config.json (Key: {key[:4]}***)")
            return ProviderConfig(name="twelvedata", api_key=key)

    if chosen_provider == "alpaca":
        key = api_keys.get("alpaca_key", "")
        sec = api_keys.get("alpaca_secret", "")
        if key and sec and not key.startswith("YOUR_"):
            print(f"[INFO] Using Alpaca Data Provider from config.json (Key: {key[:4]}***)")
            return ProviderConfig(name="alpaca", api_key=key, api_secret=sec)

    if chosen_provider == "tiingo":
        key = api_keys.get("tiingo", "")
        if key and not key.startswith("YOUR_"):
            print("[INFO] Using Tiingo Data Provider from config.json")
            return ProviderConfig(name="tiingo", api_key=key)

    if chosen_provider == "demo":
        print("[INFO] Using built-in SMC Demo Data Provider (configured in config.json)")
        return ProviderConfig(name="demo", api_key="demo")

    # 2. Fallback to .env / OS environment variables
    _load_env_file()
    twelve_key = os.environ.get("TWELVE_API_KEY", "")
    if twelve_key and not twelve_key.startswith("YOUR_"):
        print(f"[INFO] Using Twelve Data Provider (Key: {twelve_key[:4]}***)")
        return ProviderConfig(name="twelvedata", api_key=twelve_key)

    alpaca_key = os.environ.get("ALPACA_API_KEY", "")
    alpaca_secret = os.environ.get("ALPACA_API_SECRET", "")
    if alpaca_key and alpaca_secret and not alpaca_key.startswith("YOUR_"):
        print(f"[INFO] Using Alpaca Data Provider (Key: {alpaca_key[:4]}***)")
        return ProviderConfig(name="alpaca", api_key=alpaca_key, api_secret=alpaca_secret)

    tiingo_key = os.environ.get("TIINGO_API_KEY", "")
    if tiingo_key and not tiingo_key.startswith("YOUR_"):
        print("[INFO] Using Tiingo Data Provider")
        return ProviderConfig(name="tiingo", api_key=tiingo_key)

    print("[INFO] No valid external API keys configured. Falling back to built-in SMC Demo Data Provider.")
    return ProviderConfig(name="demo", api_key="demo")




