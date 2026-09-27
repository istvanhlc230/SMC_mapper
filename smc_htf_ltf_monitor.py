import os
import time
import json
import urllib.request
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

class Notifier:
    @classmethod
    def alert(cls, title: str, text: str):
        print(f"\n\033[92m{'+'*70}")
        print(f"[+] NOTIFICATION: {title}")
        print(f"    {text}")
        print(f"{'+'*70}\033[0m\n")

@dataclass
class Candle:
    timestamp: datetime
    high: float
    low: float

@dataclass
class TargetSetup:
    ticker: str
    direction: str # BUY/SELL
    target_id: str
    target_type: str
    provenance: str
    target_price: float
    state: str = "WAITING" # WAITING -> TARGET_REACHED

class Monitor:
    """
    Downstream execution-observability/notification component.
    Implements only the notification behavior required by the project phase.
    Does NOT manufacture entry semantics, does not move stops, does not close positions.
    """
    def __init__(self, config_path: str = "targets.json"):
        self.config_path = config_path
        self.targets: List[TargetSetup] = []

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    new_targets = []
                    for item in data.get("targets", []):
                        new_targets.append(TargetSetup(
                            ticker=item.get("ticker", "UNKNOWN"),
                            direction=item.get("direction", "BUY"),
                            target_id=item.get("target_id", "T1"),
                            target_type=item.get("target_type", "UNKNOWN"),
                            provenance=item.get("provenance", "UNKNOWN"),
                            target_price=float(item.get("target_price", 0.0)),
                            state=item.get("state", "WAITING")
                        ))
                    self.targets = new_targets
                except Exception as e:
                    print(f"Error loading config: {e}")

    def fetch_candle(self, ticker: str, tf: str = "1m") -> Optional[Candle]:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf}&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            res = data["chart"]["result"][0]
            timestamps = res.get("timestamp", [])
            quote = res["indicators"]["quote"][0]
            if not timestamps or len(timestamps) < 2:
                return None
            for i in range(len(timestamps) - 2, -1, -1):
                if quote["high"][i] is not None and quote["low"][i] is not None:
                    return Candle(
                        timestamp=datetime.fromtimestamp(timestamps[i]),
                        high=float(quote["high"][i]),
                        low=float(quote["low"][i])
                    )
            return None
        except Exception:
            return None

    def evaluate(self, candles: Dict[str, Candle]):
        for t in self.targets:
            if t.state == "TARGET_REACHED":
                continue
                
            c = candles.get(t.ticker)
            if not c:
                continue
                
            reached = False
            if t.direction == "BUY" and c.high >= t.target_price:
                reached = True
            elif t.direction == "SELL" and c.low <= t.target_price:
                reached = True
                
            if reached:
                t.state = "TARGET_REACHED"
                Notifier.alert(
                    title=f"TARGET REACHED: {t.ticker}",
                    text=f"Direction: {t.direction} | Target ID: {t.target_id} | Type: {t.target_type} | Provenance: {t.provenance} | Price: {t.target_price} | Timestamp: {c.timestamp.isoformat()}"
                )

    def run(self):
        print("\033[96m>>> Downstream Target Monitor Started <<<\033[0m")
        while True:
            try:
                self.load_config()
                active = {t.ticker for t in self.targets if t.state != "TARGET_REACHED"}
                if not active:
                    time.sleep(60)
                    continue
                
                candles = {}
                for ticker in active:
                    c = self.fetch_candle(ticker)
                    if c:
                        candles[ticker] = c
                
                self.evaluate(candles)
                time.sleep(60)
            except KeyboardInterrupt:
                break
            except Exception as e:
                time.sleep(30)

if __name__ == "__main__":
    Monitor().run()
