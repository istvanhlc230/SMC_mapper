import os
import time
import json
import urllib.request
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any

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
    state: str = "TARGET_ACTIVE" # TARGET_ACTIVE -> TARGET_REACHED
    raw_data: dict = None # Store the original JSON dict to write back cleanly

class Monitor:
    """
    Downstream execution-observability/notification component.
    Implements only the notification behavior required by the project phase.
    Does NOT manufacture entry semantics, does not move stops, does not close positions.
    """
    def __init__(self, config_path: str = "zones.json"):
        self.config_path = config_path
        self.targets: List[TargetSetup] = []

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    new_targets = []
                    # Map from the existing zones.json "setups" structure
                    for item in data.get("setups", []):
                        new_targets.append(TargetSetup(
                            ticker=item.get("ticker", "UNKNOWN"),
                            direction=item.get("direction", "BUY"),
                            target_id=item.get("name", "T1"), # Map name to target_id
                            target_type=item.get("target_type", "CONFIGURED_ZONE"),
                            provenance=item.get("name", "UNKNOWN"),
                            target_price=float(item.get("target", 0.0)),
                            state=item.get("state", "TARGET_ACTIVE"),
                            raw_data=item
                        ))
                    self.targets = new_targets
                except Exception as e:
                    print(f"Error loading config: {e}")

    def save_config(self):
        if not os.path.exists(self.config_path):
            return
            
        try:
            # We preserve the original structure and just update the state field
            output_setups = []
            for t in self.targets:
                raw = dict(t.raw_data) if t.raw_data else {}
                raw["state"] = t.state
                output_setups.append(raw)
                
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"setups": output_setups}, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

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
        state_changed = False
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
                state_changed = True
                Notifier.alert(
                    title=f"TARGET REACHED: {t.ticker}",
                    text=f"Direction: {t.direction} | Target ID: {t.target_id} | Type: {t.target_type} | Provenance: {t.provenance} | Price: {t.target_price} | Timestamp: {c.timestamp.isoformat()}"
                )
                
        if state_changed:
            self.save_config()

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
