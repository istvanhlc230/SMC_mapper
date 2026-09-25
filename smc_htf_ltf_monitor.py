import os
import sys
import time
import json
import shutil
import subprocess
import threading
import urllib.request
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple

# ==============================================================================
# TERMUX RIASZTÁSOK (HANG, REZGÉS, ÉRTESÍTÉS)
# ==============================================================================
class Notifier:
    @staticmethod
    def _run(cmd):
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4)
        except Exception:
            pass

    @classmethod
    def alert(cls, title: str, text: str, spoken: str, alert_type: str = "info"):
        def _worker():
            if shutil.which("termux-tts-speak"):
                if alert_type == "tapped":
                    cls._run(["termux-vibrate", "-d", "150"])
                elif alert_type == "failed":
                    cls._run(["termux-vibrate", "-d", "500"])
                elif alert_type == "entry":
                    cls._run(["termux-vibrate", "-d", "300"])
                    time.sleep(0.1)
                    cls._run(["termux-vibrate", "-d", "300"])

                # Magyar nyelvű felolvasás
                cls._run(["termux-tts-speak", "-l", "hu-HU", "-p", "0.85", "-r", "1.0", spoken])

                # Android értesítés küldése
                cls._run([
                    "termux-notification",
                    "--title", title,
                    "--content", text.replace("\n", " "),
                    "--priority", "high"
                ])
            else:
                sys.stdout.write("\a")
                sys.stdout.flush()

        threading.Thread(target=_worker, daemon=True).start()

# ==============================================================================
# ADATMODELL
# ==============================================================================
@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open

    @property
    def dir_symbol(self) -> str:
        return "▲ Zöld" if self.is_bullish else "▼ Piros"

@dataclass
class Setup:
    ticker: str
    name: str
    direction: str
    htf: str
    ltf: str
    top_price: float
    bottom_price: float
    target: float
    probability_pct: int = 55
    state: str = "WAITING"
    poi_touch_close_time: Optional[datetime] = None

# ==============================================================================
# MONITOR MOTOR
# ==============================================================================
class Monitor:
    def __init__(self, config_path: str = "zones.json"):
        self.config_path = config_path
        self.setups: List[Setup] = []
        self.last_candle_times: Dict[Tuple[str, str], datetime] = {}
        self.load_config()

    @staticmethod
    def tf_seconds(tf: str) -> int:
        tf = tf.lower().strip()
        if tf.endswith("m"): return int(tf[:-1]) * 60
        if tf.endswith("h"): return int(tf[:-1]) * 3600
        if tf.endswith("d"): return int(tf[:-1]) * 86400
        return 900

    def load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            old_states = {s.name: (s.state, s.poi_touch_close_time) for s in self.setups}
            new_setups = []

            for s in data.get("setups", []):
                name = s.get("name", s["ticker"])
                state, touch_time = old_states.get(name, ("WAITING", None))

                new_setups.append(Setup(
                    ticker=s["ticker"].strip().upper(),
                    name=name,
                    direction=s.get("direction", "BUY").upper(),
                    htf=s.get("htf", "1h").lower(),
                    ltf=s.get("ltf", "15m").lower(),
                    top_price=float(s["top_price"]),
                    bottom_price=float(s["bottom_price"]),
                    target=float(s["target"]),
                    probability_pct=int(s.get("probability_pct", 55)),
                    state=state,
                    poi_touch_close_time=touch_time
                ))

            self.setups = new_setups
            print(f"\n\033[94m[*] Konfiguráció frissítve: {len(self.setups)} setup aktív.\033[0m")
            for s in self.setups:
                print(f"    - {s.ticker} ({s.name}): {s.direction} sáv: [{s.bottom_price} - {s.top_price}] -> TP: {s.target}")
            print()
        except Exception as e:
            print(f"\033[91m[Hiba a zones.json betöltésekor]: {e}\033[0m")

    def fetch_candle(self, ticker: str, tf: str) -> Optional[Candle]:
        rng = "2d" if tf in ["1m", "5m", "15m"] else "5d"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={tf}&range={rng}"
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
                if (quote["open"][i] is not None and quote["high"][i] is not None and 
                    quote["low"][i] is not None and quote["close"][i] is not None):
                    return Candle(
                        timestamp=datetime.fromtimestamp(timestamps[i]),
                        open=float(quote["open"][i]),
                        high=float(quote["high"][i]),
                        low=float(quote["low"][i]),
                        close=float(quote["close"][i])
                    )
            return None
        except Exception as e:
            print(f"[{ticker} {tf} hiba]: {e}")
            return None

    def evaluate(self, candles: Dict[Tuple[str, str], Candle]):
        for s in self.setups:
            if s.state in ["FAILED", "TRIGGERED"]:
                continue

            is_buy = (s.direction == "BUY")
            htf_c = candles.get((s.ticker, s.htf))
            ltf_c = candles.get((s.ticker, s.ltf))

            # 1. ZÓNABUKÁS VIZSGÁLATA (Testzárás a zónán kívül)
            if htf_c:
                breached = (htf_c.close < s.bottom_price) if is_buy else (htf_c.close > s.top_price)
                if breached:
                    s.state = "FAILED"
                    print(f"\n\033[91m[!][{s.ticker}] ZÓNA ELBUKOTT! Záróár ({htf_c.close:.4f}) átütötte a szintet. ÚJ ELEMZÉS SZÜKSÉGES!\033[0m")
                    Notifier.alert(
                        f"ZÓNA ELBUKOTT: {s.ticker}",
                        f"{s.name} szint elbukott @ {htf_c.close:.4f}. Új elemzés szükséges!",
                        f"Figyelem, {s.ticker} szint elbukott. A zóna megsemmisült, új elemzés szükséges.",
                        "failed"
                    )
                    continue

            # 2. HTF ÉRINTÉS VIZSGÁLATA (Zónába ért az árfolyam)
            if s.state == "WAITING" and htf_c:
                touched = not (htf_c.high < s.bottom_price or htf_c.low > s.top_price)
                if touched:
                    s.state = "ARMED"
                    close_time = htf_c.timestamp + timedelta(seconds=self.tf_seconds(s.htf))
                    s.poi_touch_close_time = close_time

                    print(f"\n\033[93m[*][{s.ticker}] POI ÉRINTVE! Sáv: [{s.bottom_price} - {s.top_price}] -> LTF [{s.ltf.upper()}] élesítve!\033[0m")
                    Notifier.alert(
                        f"POI ÉRINTVE: {s.ticker}",
                        f"{s.name} elérte a zónát. 15 perces belépő figyelése indult.",
                        f"Figyelem, {s.ticker} elérte a zónát. Figyelés élesítve.",
                        "tapped"
                    )

            # 3. LTF BELÉPŐ & RR VIZSGÁLATA
            if s.state == "ARMED" and ltf_c:
                ltf_close = ltf_c.timestamp + timedelta(seconds=self.tf_seconds(s.ltf))

                if s.poi_touch_close_time and ltf_close > s.poi_touch_close_time:
                    mid = (s.bottom_price + s.top_price) / 2.0
                    confirmed = (ltf_c.is_bullish and ltf_c.close > mid) if is_buy else ((not ltf_c.is_bullish) and ltf_c.close < mid)

                    if confirmed:
                        sl = s.bottom_price if is_buy else s.top_price
                        risk = abs(ltf_c.close - sl)
                        reward = abs(s.target - ltf_c.close)
                        rr = (reward / risk) if risk > 0 else 0.0

                        if rr < 2.0:
                            print(f"\033[93m[!][{s.ticker}] Forduló megvan, de alacsony az R:R (1:{rr:.2f} < 1:2.0). Várakozás kedvezőbb belépőre...\033[0m")
                            continue

                        s.state = "TRIGGERED"
                        print(f"\n\033[92m{'+'*70}")
                        print(f"[+][{s.ticker}] BELÉPÉSI SZIGNÁL ({s.direction})!")
                        print(f"    Belépő: {ltf_c.close:.4f} | SL: {sl:.4f} | TP: {s.target:.4f} | R:R: 1:{rr:.2f}")
                        print(f"{'+'*70}\033[0m\n")

                        Notifier.alert(
                            f"BELÉPŐ SZIGNÁL: {s.ticker}",
                            f"{s.direction} belépő @ {ltf_c.close:.4f} | SL: {sl:.4f} | TP: {s.target:.4f} | R:R: 1:{rr:.2f}",
                            f"Figyelem, {s.ticker} belépési feltétel teljesült. Hozam kockázat egy a {int(rr)}-höz.",
                            "entry"
                        )

    def run(self):
        if shutil.which("termux-wake-lock"):
            subprocess.run(["termux-wake-lock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("\033[96m>>> True SMC Monitor elindult. Nyomj Ctrl+C-t a leállításhoz. <<<\033[0m")

        while True:
            try:
                self.load_config()

                active_tasks = set()
                for s in self.setups:
                    if s.state in ["FAILED", "TRIGGERED"]: continue
                    active_tasks.add((s.ticker, s.htf))
                    if s.state == "ARMED":
                        active_tasks.add((s.ticker, s.ltf))

                if not active_tasks:
                    print("\033[90m[*] Nincs aktív feladat. Várakozás 60 másodpercig...\033[0m")
                    time.sleep(60)
                    continue

                candles = {}
                for ticker, tf in active_tasks:
                    c = self.fetch_candle(ticker, tf)
                    if c:
                        key = (ticker, tf)
                        if self.last_candle_times.get(key) != c.timestamp:
                            self.last_candle_times[key] = c.timestamp
                            print(f"[{c.timestamp.strftime('%H:%M:%S')}][{ticker}][{tf.upper()}] Záróár: {c.close:.4f} {c.dir_symbol}")
                        candles[key] = c

                self.evaluate(candles)

                now = time.time()
                closings = [(((int(now) // self.tf_seconds(tf)) + 1) * self.tf_seconds(tf)) for _, tf in active_tasks]
                sleep_sec = max(int(min(closings) - now) + 12, 10)

                next_wake = datetime.fromtimestamp(now + sleep_sec).strftime("%H:%M:%S")
                print(f"\033[90m[Alvás] Következő zárás és ellenőrzés: {next_wake} (~{sleep_sec // 60}p {sleep_sec % 60}mp múlva)\033[0m")
                time.sleep(sleep_sec)

            except KeyboardInterrupt:
                if shutil.which("termux-wake-unlock"):
                    subprocess.run(["termux-wake-unlock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("\n[*] Monitor leállítva.")
                break
            except Exception as e:
                print(f"[Ciklus hiba]: {e}")
                time.sleep(30)

if __name__ == "__main__":
    Monitor("zones.json").run()

# target plan implementation pending
