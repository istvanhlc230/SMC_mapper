import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from smc_analyzer import (
    MarketDataNormalizer,
    DataNormalizationError,
    InsufficientHistoryError,
    AnalyzerContractError,
    SMCAnalyzer,
    LifecycleState,
    DetectionEvent,
    TargetCandidate,
    TargetLeg,
    TargetResolutionStatus,
    serialize_monitor_snapshot,
    write_monitor_snapshot,
)
from minor_structure_engine import PullbackDirection
from microstructure_engine import Candle, SequenceEvidence

def make_dummy_data(count, start_time=None, incomplete_last=False):
    if start_time is None:
        start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    
    data = []
    for i in range(count):
        data.append({
            'timestamp': start_time + timedelta(hours=i),
            'open': '1.1000',
            'high': '1.1050',
            'low': '1.0950',
            'close': '1.1020',
            'is_completed': True
        })
        
    if incomplete_last and count > 0:
        data[-1]['is_completed'] = False
        
    return data

def test_decimal_determinism_and_normalization():
    raw = make_dummy_data(15)
    candles = MarketDataNormalizer.normalize(raw)
    
    assert len(candles) == 15
    assert isinstance(candles[0].open, Decimal)
    assert candles[0].open == Decimal("1.1000")
    

def test_timezone_rejection():
    raw = make_dummy_data(15)
    raw[0]['timestamp'] = raw[0]['timestamp'].replace(tzinfo=None)
    
    with pytest.raises(DataNormalizationError, match="must be timezone-aware"):
        MarketDataNormalizer.normalize(raw)

def test_duplicate_timestamps_halt():
    raw = make_dummy_data(15)
    raw[5]['timestamp'] = raw[4]['timestamp']
    
    with pytest.raises(DataNormalizationError, match="Duplicate timestamp detected"):
        MarketDataNormalizer.normalize(raw)

def test_out_of_order_timestamps_halt():
    raw = make_dummy_data(15)
    raw[5]['timestamp'] = raw[4]['timestamp'] - timedelta(hours=1)
    
    with pytest.raises(DataNormalizationError, match="strictly ordered"):
        MarketDataNormalizer.normalize(raw)

def test_invalid_ohlc_halt():
    raw = make_dummy_data(15)
    raw[5]['low'] = '1.2000' # low > high
    
    with pytest.raises(DataNormalizationError, match="Invalid OHLC"):
        MarketDataNormalizer.normalize(raw)

def test_incomplete_candle_exclusion():
    raw = make_dummy_data(15, incomplete_last=True)
    candles = MarketDataNormalizer.normalize(raw)
    
    assert len(candles) == 14

def test_missing_is_completed_halts():
    raw = make_dummy_data(15)
    del raw[5]['is_completed']
    with pytest.raises(DataNormalizationError, match="Missing 'is_completed' status"):
        MarketDataNormalizer.normalize(raw)

def test_non_boolean_is_completed_halts():
    raw = make_dummy_data(15)
    raw[5]['is_completed'] = "True"
    with pytest.raises(DataNormalizationError, match="'is_completed' must be a boolean"):
        MarketDataNormalizer.normalize(raw)

def test_detection_event_enum():
    from smc_analyzer import DetectionEvent
    assert len(DetectionEvent) == 6
    expected_names = {
        "NO_EVENT_INTERNAL_PB",
        "MINOR_IDM_EVENT",
        "EXT_CONT_BREAK",
        "EXT_OPP_BREAK",
        "MAJOR_IDM_EVENT",
        "NEW_SVP_QUALIFIED"
    }
    actual_names = {e.name for e in DetectionEvent}
    assert actual_names == expected_names

def test_float_input_conversion_at_external_adapter_boundary():
    raw = make_dummy_data(15)
    raw[0]['open'] = 1.1000
    candles = MarketDataNormalizer.normalize(raw)
    assert candles[0].open == Decimal("1.1")
    assert isinstance(candles[0], __import__("microstructure_engine").Candle)


def test_analyzer_executes_real_l1_to_l5_orchestration():
    analyzer = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH)
    result = analyzer.analyze(make_dummy_data(15))

    assert result.lifecycle_state == LifecycleState.BOOTSTRAP
    assert result.detected_event == DetectionEvent.NO_EVENT_INTERNAL_PB
    assert result.l2_result is not None
    assert result.l3_result is not None
    assert result.l4_result is not None
    assert result.l5_result is not None
    assert result.rr_result.reason == "NO_RESOLVED_TARGET"


def test_analyzer_requires_direction_for_layer2_orchestration():
    analyzer = SMCAnalyzer("TEST", "1h")
    with pytest.raises(AnalyzerContractError, match="direction is required"):
        analyzer.analyze(make_dummy_data(15))


def test_target_resolution_is_explicit_and_non_universal():
    analyzer = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH)
    candidates = (
        TargetCandidate("T1", "external_liquidity", Decimal("10.50"), "CONFIGURED_TARGET_POLICY"),
        TargetCandidate("T2", "structural_destination", Decimal("11.25"), "CONFIGURED_TARGET_POLICY"),
    )
    result = analyzer.analyze(
        make_dummy_data(15),
        target_candidates=candidates,
        resolved_target_ids=("T1", "T2"),
        target_legs=(
            TargetLeg("LEG-A", "T1", Decimal("40")),
            TargetLeg("LEG-B", "T2", Decimal("60")),
        ),
        analysis_timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    assert result.target_resolution_status is TargetResolutionStatus.RESOLVED
    assert [target.target_id for target in result.resolved_targets] == ["T1", "T2"]
    assert result.resolved_target is not None
    assert result.resolved_target.target_id == "T1"
    assert result.target_plan is not None
    assert [leg.leg_id for leg in result.target_plan.legs] == ["LEG-A", "LEG-B"]
    assert result.rr_result.reason == "RR_INPUTS_UNAVAILABLE"

    data = serialize_monitor_snapshot(result)
    assert len(data["setups"]) == 2
    assert {setup["target_resolution"]["resolved_target_id"] for setup in data["setups"]} == {"T1", "T2"}
    assert all(setup["target_resolution"]["status"] == "RESOLVED" for setup in data["setups"])


def test_target_resolution_missing_is_fail_closed():
    analyzer = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH)
    result = analyzer.analyze(
        make_dummy_data(15),
        target_candidates=(
            TargetCandidate("T1", "configured", Decimal("10"), "CONFIGURED_TARGET_POLICY"),
        ),
    )

    assert result.target_resolution_status is TargetResolutionStatus.NO_RESOLVED_TARGET
    assert result.resolved_target is None
    assert result.target_candidates
    assert result.target_plan is None


def test_target_provenance_is_required():
    analyzer = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH)
    with pytest.raises(AnalyzerContractError, match="provenance is required"):
        analyzer.analyze(
            make_dummy_data(15),
            target_candidates=(
                TargetCandidate("T1", "configured", Decimal("10"), ""),
            ),
            resolved_target_id="T1",
        )


def test_structural_hash_is_stable_and_timestamp_is_not_part_of_identity():
    raw = make_dummy_data(15)
    r1 = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH).analyze(
        raw, analysis_timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    r2 = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH).analyze(
        raw, analysis_timestamp=datetime(2026, 1, 3, tzinfo=timezone.utc)
    )

    assert r1.analysis_timestamp != r2.analysis_timestamp
    assert r1.structural_hash == r2.structural_hash


def test_analyzer_serializes_only_resolved_targets_for_monitor():
    analyzer = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH)
    unresolved = analyzer.analyze(
        make_dummy_data(15),
        target_candidates=(
            TargetCandidate("T1", "configured", Decimal("10"), "CONFIGURED_TARGET_POLICY"),
        ),
        analysis_timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    data = serialize_monitor_snapshot(unresolved)
    assert data["schema_version"] == 1
    assert data["source"] == "ANALYZER"
    assert data["setups"] == []

    resolved = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH).analyze(
        make_dummy_data(15),
        target_candidates=(
            TargetCandidate("T1", "configured", Decimal("10"), "CONFIGURED_TARGET_POLICY"),
        ),
        resolved_target_id="T1",
        analysis_timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    data = serialize_monitor_snapshot(resolved)
    assert len(data["setups"]) == 1
    setup = data["setups"][0]
    assert setup["monitor_id"] == "TEST:1h:DIRECT"
    assert setup["direction"] == "BUY"
    assert setup["target_resolution"]["status"] == "RESOLVED"
    assert setup["target"]["target_id"] == "T1"
    assert setup["target"]["provenance"] == "CONFIGURED_TARGET_POLICY"
    assert setup["target_plan"]["allocation_pct"] == "100"


def test_analyzer_to_zones_to_monitor_round_trip(tmp_path):
    from smc_htf_ltf_monitor import Candle as MonitorCandle, Monitor

    path = tmp_path / "zones.json"
    analyzer = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH)
    result = analyzer.analyze(
        make_dummy_data(15),
        target_candidates=(
            TargetCandidate("T1", "configured", Decimal("10"), "CONFIGURED_TARGET_POLICY"),
        ),
        resolved_target_id="T1",
        analysis_timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    write_monitor_snapshot(result, path)

    monitor = Monitor(str(path))
    monitor.load_config()
    assert len(monitor.targets) == 1
    assert monitor.targets[0].direction == "BUY"
    assert monitor.targets[0].target_price == Decimal("10")
    assert monitor.targets[0].structural_hash == result.structural_hash

    with pytest.MonkeyPatch.context() as mp:
        from smc_htf_ltf_monitor import Notifier
        mp.setattr(Notifier, "alert", lambda *args, **kwargs: None)
        monitor.evaluate({
            "TEST": MonitorCandle(
                datetime(2026, 1, 2, 12, tzinfo=timezone.utc),
                Decimal("10.25"),
                Decimal("9.75"),
            )
        })

    persisted = __import__("json").loads(path.read_text(encoding="utf-8"))
    assert persisted["setups"][0]["state"] == "TARGET_REACHED"


def test_analyzer_snapshot_preserves_reached_state_only_for_same_version_and_target(tmp_path):
    from smc_htf_ltf_monitor import Monitor, Candle as MonitorCandle, Notifier

    path = tmp_path / "zones.json"
    try:
        candidates = (
            TargetCandidate("T1", "configured", Decimal("10"), "CONFIGURED_TARGET_POLICY"),
        )
        timestamp = datetime(2026, 1, 2, tzinfo=timezone.utc)
        result = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH).analyze(
            make_dummy_data(15),
            target_candidates=candidates,
            resolved_target_id="T1",
            analysis_timestamp=timestamp,
        )
        write_monitor_snapshot(result, path)

        monitor = Monitor(str(path))
        monitor.load_config()
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(Notifier, "alert", lambda *args, **kwargs: None)
            monitor.evaluate({
                "TEST": MonitorCandle(
                    timestamp,
                    Decimal("10.20"),
                    Decimal("9.80"),
                )
            })

        reached = __import__("json").loads(path.read_text(encoding="utf-8"))
        assert reached["setups"][0]["state"] == "TARGET_REACHED"

        same_version = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH).analyze(
            make_dummy_data(15),
            target_candidates=candidates,
            resolved_target_id="T1",
            analysis_timestamp=datetime(2026, 1, 3, tzinfo=timezone.utc),
        )
        write_monitor_snapshot(same_version, path)
        preserved = __import__("json").loads(path.read_text(encoding="utf-8"))
        assert preserved["setups"][0]["state"] == "TARGET_REACHED"

        changed_target = SMCAnalyzer("TEST", "1h", PullbackDirection.BULLISH).analyze(
            make_dummy_data(15),
            target_candidates=(
                TargetCandidate("T1", "configured", Decimal("10.10"), "CONFIGURED_TARGET_POLICY"),
            ),
            resolved_target_id="T1",
            analysis_timestamp=datetime(2026, 1, 4, tzinfo=timezone.utc),
        )
        write_monitor_snapshot(changed_target, path)
        reset = __import__("json").loads(path.read_text(encoding="utf-8"))
        assert reset["setups"][0]["state"] == "TARGET_ACTIVE"
    finally:
        path.unlink(missing_ok=True)
