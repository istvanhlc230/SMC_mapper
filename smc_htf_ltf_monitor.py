import os
import time
import json
import math
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
    original_index: int = -1 # to map back to the setup array
    is_dirty: bool = False # track if we need to mutate the JSON

class Monitor:
    """
    Downstream execution-observability/notification component.
    Implements only the notification behavior required by the project phase.
    Does NOT manufacture entry semantics, does not move stops, does not close positions.
    """
    def __init__(self, config_path: str = "zones.json"):
        self.config_path = config_path
        self.targets: List[TargetSetup] = []
        self.full_config_data: dict = {}

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                    self.full_config_data = data
                    
                    new_targets = []
                    setups = data.get("setups", [])
                    if not isinstance(setups, list):
                        setups = []
                        
                    for i, item in enumerate(setups):
                        if not isinstance(item, dict):
                            continue
                            
                        raw_state = item.get("state")
                        if raw_state is None:
                            computed_state = "TARGET_ACTIVE"
                        elif raw_state in ["TARGET_ACTIVE", "TARGET_REACHED"]:
                            computed_state = raw_state
                        else:
                            computed_state = "INVALID_STATE"
                            
                        direction = item.get("direction")
                        if direction not in ["BUY", "SELL"]:
                            computed_state = "INVALID_STATE"
                            
                        target_val = item.get("target")
                        target_price = 0.0
                        if target_val is None:
                            computed_state = "INVALID_STATE"
                        else:
                            try:
                                target_price = float(target_val)
                                if math.isnan(target_price) or math.isinf(target_price):
                                    computed_state = "INVALID_STATE"
                            except (ValueError, TypeError):
                                computed_state = "INVALID_STATE"
                            
                        supplied_provenance = item.get("provenance")
                        provenance_val = supplied_provenance if supplied_provenance else f"Configuration Setup ID: {item.get('name', 'UNKNOWN')}"
                        
                        target_type_val = item.get("target_type", "configured target")
                        
                        new_targets.append(TargetSetup(
                            ticker=item.get("ticker", "UNKNOWN"),
                            direction=direction if direction in ["BUY", "SELL"] else "BUY",
                            target_id=item.get("name", "T1"),
                            target_type=target_type_val,
                            provenance=provenance_val,
                            target_price=target_price,
                            state=computed_state,
                            original_index=i,
                            is_dirty=False
                        ))
                    self.targets = new_targets
                except Exception as e:
                    print(f"Error loading config: {e}")
                    self.targets = []
                    self.full_config_data = {}

    def save_config(self):
        if not os.path.exists(self.config_path):
            return
            
        try:
            if "setups" in self.full_config_data and isinstance(self.full_config_data["setups"], list):
                for t in self.targets:
                    if t.is_dirty and 0 <= t.original_index < len(self.full_config_data["setups"]):
                        setup_node = self.full_config_data["setups"][t.original_index]
                        if isinstance(setup_node, dict):
                            setup_node["state"] = t.state
                            t.is_dirty = False
                            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.full_config_data, f, indent=2)
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
            if t.state != "TARGET_ACTIVE":
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
                t.is_dirty = True
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
                active = {t.ticker for t in self.targets if t.state == "TARGET_ACTIVE"}
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
