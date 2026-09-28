"""Downstream target observer for the versioned analyzer/monitor JSON contract."""
from __future__ import annotations

import json
import math
import os
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

MONITOR_SCHEMA_VERSION = 1
ALLOWED_SOURCES = {"ANALYZER", "CONFIGURATION"}


class MonitorContractError(Exception):
    """Invalid or incomplete analyzer/monitor integration contract."""


class Notifier:
    @classmethod
    def alert(cls, title: str, text: str):
        print(f"\n\033[92m{'+' * 70}")
        print(f"[+] NOTIFICATION: {title}")
        print(f"    {text}")
        print(f"{'+' * 70}\033[0m\n")


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    high: Decimal
    low: Decimal

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None or self.timestamp.tzinfo.utcoffset(self.timestamp) is None:
            raise MonitorContractError("Candle timestamp must be timezone-aware")
        if not self.high.is_finite() or not self.low.is_finite():
            raise MonitorContractError("Candle prices must be finite")
        if self.high < self.low:
            raise MonitorContractError("Candle high cannot be below low")


@dataclass
class TargetSetup:
    ticker: str
    direction: str
    target_id: str
    target_type: str
    provenance: str
    target_price: Decimal
    monitor_id: str
    setup_id: str
    leg_id: str
    state: str = "TARGET_ACTIVE"
    analysis_timestamp: Optional[datetime] = None
    structural_hash: Optional[str] = None
    original_index: int = -1
    is_dirty: bool = False


class Monitor:
    """
    Downstream execution-observability/notification component.

    It consumes only RESOLVED target records from the versioned contract.
    It does not manufacture target IDs/provenance, resolve targets, move stops,
    submit orders, or close positions.
    """

    def __init__(self, config_path: str = "zones.json"):
        self.config_path = config_path
        self.targets: List[TargetSetup] = []
        self.full_config_data: dict = {}

    @staticmethod
    def _parse_decimal(value, field_name: str) -> Decimal:
        try:
            parsed = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise MonitorContractError(f"{field_name} must be a finite decimal") from exc
        if not parsed.is_finite():
            raise MonitorContractError(f"{field_name} must be a finite decimal")
        return parsed

    @staticmethod
    def _parse_timestamp(value, field_name: str) -> Optional[datetime]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise MonitorContractError(f"{field_name} must be an ISO-8601 string or null")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise MonitorContractError(f"{field_name} must be a valid ISO-8601 timestamp") from exc
        if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
            raise MonitorContractError(f"{field_name} must be timezone-aware")
        return parsed.astimezone(timezone.utc)

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise MonitorContractError(f"monitor configuration not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise MonitorContractError(f"cannot load monitor configuration: {exc}") from exc

        if not isinstance(data, dict):
            raise MonitorContractError("monitor configuration root must be an object")
        if data.get("schema_version") != MONITOR_SCHEMA_VERSION:
            raise MonitorContractError(
                f"unsupported monitor schema_version: {data.get('schema_version')!r}"
            )
        source = data.get("source")
        if source not in ALLOWED_SOURCES:
            raise MonitorContractError(f"unsupported monitor source: {source!r}")

        setups = data.get("setups")
        if not isinstance(setups, list):
            raise MonitorContractError("monitor configuration 'setups' must be a list")

        new_targets: List[TargetSetup] = []
        seen_monitor_ids: set[str] = set()
        for i, item in enumerate(setups):
            if not isinstance(item, dict):
                raise MonitorContractError(f"setup[{i}] must be an object")

            monitor_id = item.get("monitor_id")
            setup_id = item.get("setup_id")
            leg_id = item.get("leg_id")
            ticker = item.get("ticker")
            direction = item.get("direction")
            state = item.get("state")

            for value, name in (
                (monitor_id, "monitor_id"),
                (setup_id, "setup_id"),
                (leg_id, "leg_id"),
                (ticker, "ticker"),
            ):
                if not isinstance(value, str) or not value:
                    raise MonitorContractError(f"setup[{i}] requires explicit {name}")

            if monitor_id in seen_monitor_ids:
                raise MonitorContractError(f"duplicate monitor_id: {monitor_id}")
            seen_monitor_ids.add(monitor_id)

            if direction not in {"BUY", "SELL"}:
                raise MonitorContractError(f"setup[{i}] direction must be BUY or SELL")
            if state not in {"TARGET_ACTIVE", "TARGET_REACHED"}:
                raise MonitorContractError(f"setup[{i}] has invalid state: {state!r}")

            resolution = item.get("target_resolution")
            if not isinstance(resolution, dict):
                raise MonitorContractError(f"setup[{i}] requires target_resolution")
            if resolution.get("status") != "RESOLVED":
                raise MonitorContractError(f"setup[{i}] target is not resolved")
            resolved_target_id = resolution.get("resolved_target_id")
            if not isinstance(resolved_target_id, str) or not resolved_target_id:
                raise MonitorContractError(f"setup[{i}] requires resolved_target_id")

            candidates = item.get("target_candidates")
            if not isinstance(candidates, list) or not candidates:
                raise MonitorContractError(f"setup[{i}] requires target_candidates")
            matching_candidates = [
                candidate
                for candidate in candidates
                if isinstance(candidate, dict) and candidate.get("target_id") == resolved_target_id
            ]
            if len(matching_candidates) != 1:
                raise MonitorContractError(
                    f"setup[{i}] resolved_target_id must match exactly one candidate"
                )

            target = item.get("target")
            if not isinstance(target, dict):
                raise MonitorContractError(f"setup[{i}] requires resolved target object")
            if target.get("target_id") != resolved_target_id:
                raise MonitorContractError(f"setup[{i}] target_id disagrees with target_resolution")

            target_id = target.get("target_id")
            target_type = target.get("target_type")
            provenance = target.get("provenance")
            if not isinstance(target_id, str) or not target_id:
                raise MonitorContractError(f"setup[{i}] target_id is required")
            if not isinstance(target_type, str) or not target_type:
                raise MonitorContractError(f"setup[{i}] target_type is required")
            if not isinstance(provenance, str) or not provenance:
                raise MonitorContractError(f"setup[{i}] provenance is required")

            target_price = self._parse_decimal(target.get("price"), f"setup[{i}] target.price")
            candidate = matching_candidates[0]
            if (
                candidate.get("target_type") != target_type
                or candidate.get("provenance") != provenance
                or self._parse_decimal(candidate.get("price"), f"setup[{i}] candidate.price") != target_price
            ):
                raise MonitorContractError(
                    f"setup[{i}] resolved target does not match its target candidate"
                )

            plan = item.get("target_plan")
            if not isinstance(plan, dict):
                raise MonitorContractError(f"setup[{i}] requires target_plan")
            if plan.get("leg_id") != leg_id or plan.get("target_id") != target_id:
                raise MonitorContractError(f"setup[{i}] target_plan does not match setup leg")

            analysis_timestamp = self._parse_timestamp(
                item.get("analysis_timestamp"), f"setup[{i}] analysis_timestamp"
            )
            structural_hash = item.get("structural_hash")
            if structural_hash is not None and (
                not isinstance(structural_hash, str) or not structural_hash
            ):
                raise MonitorContractError(f"setup[{i}] structural_hash must be a non-empty string or null")

            if source == "ANALYZER":
                if analysis_timestamp is None or structural_hash is None:
                    raise MonitorContractError(
                        f"setup[{i}] analyzer output requires analysis_timestamp and structural_hash"
                    )

            new_targets.append(
                TargetSetup(
                    ticker=ticker,
                    direction=direction,
                    target_id=target_id,
                    target_type=target_type,
                    provenance=provenance,
                    target_price=target_price,
                    monitor_id=monitor_id,
                    setup_id=setup_id,
                    leg_id=leg_id,
                    state=state,
                    analysis_timestamp=analysis_timestamp,
                    structural_hash=structural_hash,
                    original_index=i,
                )
            )

        self.full_config_data = data
        self.targets = new_targets

    def save_config(self) -> None:
        if "setups" not in self.full_config_data or not isinstance(
            self.full_config_data["setups"], list
        ):
            raise MonitorContractError("loaded configuration has no setup list")

        setup_by_monitor_id = {
            node.get("monitor_id"): node
            for node in self.full_config_data["setups"]
            if isinstance(node, dict)
        }

        dirty_targets = [target for target in self.targets if target.is_dirty]
        for target in dirty_targets:
            node = setup_by_monitor_id.get(target.monitor_id)
            if not isinstance(node, dict):
                raise MonitorContractError(
                    f"cannot persist target state: monitor_id {target.monitor_id!r} not found"
                )
            node["state"] = target.state

        if not dirty_targets:
            return

        directory = os.path.dirname(os.path.abspath(self.config_path)) or "."
        fd, temp_path = tempfile.mkstemp(prefix=".zones.", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self.full_config_data, f, indent=2, ensure_ascii=False)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.config_path)
        except Exception:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

        for target in dirty_targets:
            target.is_dirty = False

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
                high_raw = quote["high"][i]
                low_raw = quote["low"][i]
                if high_raw is not None and low_raw is not None:
                    timestamp = datetime.fromtimestamp(timestamps[i], tz=timezone.utc)
                    return Candle(
                        timestamp=timestamp,
                        high=Decimal(str(high_raw)),
                        low=Decimal(str(low_raw)),
                    )
            return None
        except Exception:
            return None

    def evaluate(self, candles: Dict[str, Candle]) -> None:
        reached: list[TargetSetup] = []
        for target in self.targets:
            if target.state != "TARGET_ACTIVE":
                continue
            candle = candles.get(target.ticker)
            if candle is None:
                continue

            if target.direction == "BUY" and candle.high >= target.target_price:
                reached.append(target)
            elif target.direction == "SELL" and candle.low <= target.target_price:
                reached.append(target)

        if not reached:
            return

        for target in reached:
            target.state = "TARGET_REACHED"
            target.is_dirty = True

        try:
            self.save_config()
        except Exception as exc:
            for target in reached:
                target.state = "TARGET_ACTIVE"
                target.is_dirty = True
            print(f"Error saving config; notifications suppressed: {exc}")
            return

        for target in reached:
            candle = candles[target.ticker]
            Notifier.alert(
                title=f"TARGET REACHED: {target.ticker}",
                text=(
                    f"Direction: {target.direction} | Target ID: {target.target_id} | "
                    f"Leg ID: {target.leg_id} | Type: {target.target_type} | "
                    f"Provenance: {target.provenance} | Price: {target.target_price} | "
                    f"Timestamp: {candle.timestamp.isoformat()}"
                ),
            )

    def run(self):
        print("\033[96m>>> Downstream Target Monitor Started <<<\033[0m")
        while True:
            try:
                self.load_config()
                active = {target.ticker for target in self.targets if target.state == "TARGET_ACTIVE"}
                if not active:
                    time.sleep(60)
                    continue

                candles = {}
                for ticker in active:
                    candle = self.fetch_candle(ticker)
                    if candle:
                        candles[ticker] = candle

                self.evaluate(candles)
                time.sleep(60)
            except KeyboardInterrupt:
                break
            except Exception as exc:
                print(f"Monitor cycle error: {exc}")
                time.sleep(30)


if __name__ == "__main__":
    Monitor().run()
