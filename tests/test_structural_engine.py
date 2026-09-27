from decimal import Decimal

import microstructure_engine as micro
import minor_structure_engine as minor
import structural_engine as structural


def c(i, o, h, l, cl):
    return micro.Candle(i, Decimal(o), Decimal(h), Decimal(l), Decimal(cl))


def bullish_fixture(extra=()):
    return (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb", "9", "9.5", "1", "8"),
        c("done", "8", "11", "4", "10"),
        *extra,
    )


def test_idm_is_minor_before_bos_and_is_taken_by_physical_sweep():
    candles = bullish_fixture((c("sweep", "10", "10.5", "0.5", "9"),))
    minor_result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    result = structural.analyze_layer3(candles, minor_result)
    assert result.active_idm is not None
    assert result.active_idm.idm_class is structural.IDMClass.MINOR_IDM
    assert result.active_idm.takeout_candle_id == "sweep"
    assert result.confirmed_swings[0].source_candle_id == "r"
    assert result.resolution is structural.StructuralResolution.IDM_TAKEN


def test_idm_touch_is_not_takeout():
    candles = bullish_fixture((c("touch", "10", "10.5", "1", "9"),))
    minor_result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    result = structural.analyze_layer3(candles, minor_result)
    assert result.active_idm is not None
    assert result.active_idm.takeout_candle_id is None
    assert result.resolution is structural.StructuralResolution.IDM_ACTIVE


def test_major_idm_is_not_selected_by_caller_supplied_pullback_id():
    candles = bullish_fixture((c("sweep", "10", "10.5", "0.5", "9"),))
    minor_result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    events = structural.classify_idm(minor_result)
    assert events[0].idm_class is structural.IDMClass.MINOR_IDM
    assert all(
        parameter.name != "post_bos_pullback_ids"
        for parameter in __import__("inspect").signature(structural.classify_idm).parameters.values()
    )


def test_post_bos_pullback_automatically_becomes_major_idm():
    candles = (
        c("bos", "9", "12", "8", "11"),
        c("post_start", "11", "11.5", "7", "8"),
        c("post_done", "8", "12", "8", "11"),
    )
    extreme = minor.VerifiedPullbackExtreme(
        minor.PullbackDirection.BULLISH, Decimal("7"), "post_start"
    )
    liquidity = minor.PullbackDerivedLiquidityReference(
        minor.LiquiditySide.SELL_SIDE, Decimal("7"), "post_start"
    )
    post_pullback = minor.CandleLevelValidPullback(
        minor.PullbackDirection.BULLISH,
        "bos",
        "post_start",
        "post_done",
        extreme,
        liquidity,
    )
    minor_result = minor.MinorStructureAnalysis(
        (post_pullback,),
        minor.ActivePullbackState(post_pullback),
    )
    lifecycle = structural.IDMLifecycleContext(
        after_valid_bos=True,
        valid_bos_candle_id="bos",
        protected_external_boundary=structural.ProtectedExternalBoundary(
            minor.PullbackDirection.BULLISH, Decimal("12"), "protected"
        ),
    )
    events = structural.classify_idm(minor_result, candles=candles, lifecycle=lifecycle)
    assert len(events) == 1
    assert events[0].idm_class is structural.IDMClass.MAJOR_IDM
    assert events[0].origin is structural.IDMOrigin.PULLBACK_DERIVED
    assert events[0].pullback_completion_candle_id == "post_done"


def test_newest_post_bos_pullback_is_the_active_major_idm():
    candles = (
        c("bos", "9", "12", "8", "11"),
        c("p1_start", "11", "11.5", "7", "8"),
        c("p1_done", "8", "12", "8", "11"),
        c("p2_start", "11", "11.5", "6", "8"),
        c("p2_done", "8", "12", "7", "11"),
    )
    def pullback(start, done, low):
        extreme = minor.VerifiedPullbackExtreme(
            minor.PullbackDirection.BULLISH, Decimal(low), start
        )
        liquidity = minor.PullbackDerivedLiquidityReference(
            minor.LiquiditySide.SELL_SIDE, Decimal(low), start
        )
        return minor.CandleLevelValidPullback(
            minor.PullbackDirection.BULLISH,
            "bos",
            start,
            done,
            extreme,
            liquidity,
        )

    p1 = pullback("p1_start", "p1_done", "7")
    p2 = pullback("p2_start", "p2_done", "6")
    minor_result = minor.MinorStructureAnalysis(
        (p1, p2),
        minor.ActivePullbackState(p2),
    )
    lifecycle = structural.IDMLifecycleContext(
        after_valid_bos=True,
        valid_bos_candle_id="bos",
        protected_external_boundary=structural.ProtectedExternalBoundary(
            minor.PullbackDirection.BULLISH, Decimal("12"), "protected"
        ),
    )
    events = structural.classify_idm(minor_result, candles=candles, lifecycle=lifecycle)
    assert [e.idm_class for e in events] == [
        structural.IDMClass.MAJOR_IDM,
        structural.IDMClass.MAJOR_IDM,
    ]
    assert events[-1].pullback_completion_candle_id == "p2_done"


def test_post_bos_without_new_pullback_uses_protected_boundary_as_major():
    lifecycle = structural.IDMLifecycleContext(
        after_valid_bos=True,
        valid_bos_candle_id="sweep",
        protected_external_boundary=structural.ProtectedExternalBoundary(
            minor.PullbackDirection.BULLISH, Decimal("12"), "protected"
        ),
    )
    events = structural.classify_idm(
        minor.MinorStructureAnalysis((), minor.ActivePullbackState(None)),
        candles=(c("sweep", "10", "11", "9", "10.5"),),
        lifecycle=lifecycle,
    )
    assert len(events) == 1
    assert events[0].idm_class is structural.IDMClass.MAJOR_IDM
    assert events[0].origin is structural.IDMOrigin.PROTECTED_EXTERNAL_BOUNDARY
    assert events[0].source_candle_id == "protected"


def test_post_bos_allows_new_major_without_preloaded_boundary():
    candles = (
        c("bos", "9", "12", "8", "11"),
        c("post_start", "11", "11.5", "7", "8"),
        c("post_done", "8", "12", "8", "11"),
    )
    extreme = minor.VerifiedPullbackExtreme(
        minor.PullbackDirection.BULLISH, Decimal("7"), "post_start"
    )
    liquidity = minor.PullbackDerivedLiquidityReference(
        minor.LiquiditySide.SELL_SIDE, Decimal("7"), "post_start"
    )
    pb = minor.CandleLevelValidPullback(
        minor.PullbackDirection.BULLISH, "bos", "post_start", "post_done",
        extreme, liquidity,
    )
    result = minor.MinorStructureAnalysis((pb,), minor.ActivePullbackState(pb))
    lifecycle = structural.IDMLifecycleContext(
        after_valid_bos=True,
        valid_bos_candle_id="bos",
    )
    events = structural.classify_idm(result, candles=candles, lifecycle=lifecycle)
    assert events[0].idm_class is structural.IDMClass.MAJOR_IDM

def test_post_bos_requires_protected_boundary_when_no_new_pullback():
    import pytest
    lifecycle = structural.IDMLifecycleContext(
        after_valid_bos=True,
        valid_bos_candle_id="bos",
    )
    with pytest.raises(micro.QuarantineError):
        structural.classify_idm(
            minor.MinorStructureAnalysis((), minor.ActivePullbackState(None)),
            candles=(c("bos", "9", "12", "8", "11"),),
            lifecycle=lifecycle,
        )


def test_post_bos_requires_bos_candle_provenance():
    import pytest
    with pytest.raises(micro.QuarantineError):
        structural.IDMLifecycleContext(
            after_valid_bos=True,
            protected_external_boundary=structural.ProtectedExternalBoundary(
                minor.PullbackDirection.BULLISH, Decimal("12"), "protected"
            ),
        )


def test_post_bos_boundary_provenance_is_preserved():
    lifecycle = structural.IDMLifecycleContext(
        after_valid_bos=True,
        valid_bos_candle_id="protected-bos",
        protected_external_boundary=structural.ProtectedExternalBoundary(
            minor.PullbackDirection.BULLISH, Decimal("12"), "protected"
        ),
    )
    events = structural.classify_idm(
        minor.MinorStructureAnalysis((), minor.ActivePullbackState(None)),
        candles=(c("protected-bos", "10", "11", "9", "10.5"),),
        lifecycle=lifecycle,
    )
    assert events[0].idm_class is structural.IDMClass.MAJOR_IDM
    assert events[0].origin is structural.IDMOrigin.PROTECTED_EXTERNAL_BOUNDARY
    assert events[0].source_candle_id == "protected"


def test_pre_bos_pullback_does_not_become_major_idm_after_bos():
    candles = bullish_fixture((c("sweep", "10", "10.5", "0.5", "9"),))
    minor_result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    lifecycle = structural.IDMLifecycleContext(
        after_valid_bos=True,
        valid_bos_candle_id="sweep",
        protected_external_boundary=structural.ProtectedExternalBoundary(
            minor.PullbackDirection.BULLISH, Decimal("12"), "protected"
        ),
    )
    events = structural.classify_idm(minor_result, candles=candles, lifecycle=lifecycle)
    assert len(events) == 2
    assert events[0].idm_class is structural.IDMClass.MINOR_IDM
    assert events[1].idm_class is structural.IDMClass.MAJOR_IDM
    assert events[1].origin is structural.IDMOrigin.PROTECTED_EXTERNAL_BOUNDARY


def test_qualified_retracement_at_50_percent_requires_three_opposing_closes():
    candles = (
        c("s", "5", "10", "5", "9"),
        c("a", "9", "9.5", "8", "8.5"),
        c("b", "8.5", "9", "7", "7.5"),
        c("c", "7.5", "8", "5", "6.5"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    q = structural.qualify_retracement(
        candles, swing, range_high=Decimal("10"), range_low=Decimal("0")
    )
    assert q.qualified
    assert q.reason == "STANDARD_EQUILIBRIUM"


def test_one_candle_non_outlier_is_rejected_at_equilibrium():
    candles = (
        c("s", "5", "10", "5", "9"),
        c("a", "9", "9.5", "0", "8"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    q = structural.qualify_retracement(
        candles, swing, range_high=Decimal("10"), range_low=Decimal("0")
    )
    assert not q.qualified
    assert q.reason == "INSUFFICIENT_CANDLE_STRUCTURE"


def test_one_candle_displacement_outlier_is_explicit_exception():
    candles = (
        c("p1", "8", "9", "4", "8"),
        c("p2", "8", "9", "3.5", "8"),
        c("p3", "8", "9", "3", "8"),
        c("p4", "8", "9", "2.5", "8"),
        c("p5", "8", "9", "2", "8"),
        c("s", "5", "10", "5", "9"),
        c("outlier", "8", "9", "0", "7"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    q = structural.qualify_retracement(
        candles, swing, range_high=Decimal("10"), range_low=Decimal("0"),
        attempt_end_candle_id="outlier",
    )
    assert q.qualified
    assert q.used_outlier_exception
    assert q.reason == "REDUCED_DISPLACEMENT_EXCEPTION"


def test_two_candle_displacement_exception_is_allowed_when_standard_count_is_not_met():
    candles = (
        c("p1", "8", "9", "4", "8"),
        c("p2", "8", "9", "3.5", "8"),
        c("p3", "8", "9", "3", "8"),
        c("p4", "8", "9", "2.5", "8"),
        c("p5", "8", "9", "2", "8"),
        c("s", "5", "10", "5", "9"),
        c("outlier1", "8", "9", "1", "7"),
        c("outlier2", "7", "8", "0", "7.5"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    q = structural.qualify_retracement(
        candles, swing, range_high=Decimal("10"), range_low=Decimal("0"),
        attempt_end_candle_id="outlier2",
    )
    assert q.qualified
    assert q.used_outlier_exception
    assert q.reason == "REDUCED_DISPLACEMENT_EXCEPTION"


def test_two_candle_displacement_exception_counts_collective_taken_extremes():
    candles = (
        c("p1", "8", "9", "5", "8"),
        c("p2", "8", "9", "4", "8"),
        c("p3", "8", "9", "3", "8"),
        c("p4", "8", "9", "2", "8"),
        c("p5", "8", "9", "1", "8"),
        c("s", "5", "10", "5", "9"),
        c("outlier1", "8", "9", "2.5", "7"),
        c("outlier2", "7", "9", "0.5", "7.5"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    q = structural.qualify_retracement(
        candles,
        swing,
        range_high=Decimal("10"),
        range_low=Decimal("0"),
        attempt_end_candle_id="outlier2",
    )
    assert q.qualified
    assert q.used_outlier_exception
    assert q.reason == "REDUCED_DISPLACEMENT_EXCEPTION"


def test_38_2_to_50_requires_explicit_htf_valid_pullback():
    candles = (
        c("s", "5", "10", "5", "9"),
        c("a", "9", "9.5", "6", "7"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    no_htf = structural.qualify_retracement(
        candles, swing, range_high=Decimal("10"), range_low=Decimal("0"),
        htf_valid_pullback=False
    )
    yes_htf = structural.qualify_retracement(
        candles, swing, range_high=Decimal("10"), range_low=Decimal("0"),
        htf_valid_pullback=True
    )
    assert not no_htf.qualified
    assert yes_htf.qualified
    assert yes_htf.reason == "HTF_VALID_PULLBACK"


def test_missing_retracement_attempt_end_is_quarantined():
    import pytest
    candles = (
        c("s", "5", "10", "5", "9"),
        c("a", "9", "9.5", "6", "7"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    with pytest.raises(micro.QuarantineError):
        structural.qualify_retracement(
            candles,
            swing,
            range_high=Decimal("10"),
            range_low=Decimal("0"),
            attempt_end_candle_id="missing",
        )


def test_below_38_2_is_rejected():
    candles = (
        c("s", "5", "10", "5", "9"),
        c("a", "9", "9.5", "8", "8.5"),
    )
    swing = structural.ConfirmedStructuralSwing(
        minor.PullbackDirection.BULLISH, Decimal("10"), "s", "idm", "s"
    )
    q = structural.qualify_retracement(
        candles, swing, range_high=Decimal("10"), range_low=Decimal("0")
    )
    assert not q.qualified
    assert q.reason == "BELOW_CONDITIONAL_THRESHOLD"


def test_missing_range_is_fail_closed():
    candles = bullish_fixture((c("sweep", "10", "10.5", "0.5", "9"),))
    minor_result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    result = structural.analyze_layer3(candles, minor_result)
    assert result.resolution is structural.StructuralResolution.IDM_TAKEN
    assert result.retracement is None


def test_no_layer2_evidence_is_no_evidence():
    candles = (c("a", "1", "2", "0", "1.5"),)
    result = structural.analyze_layer3(
        candles, minor.MinorStructureAnalysis((), minor.ActivePullbackState(None))
    )
    assert result.resolution is structural.StructuralResolution.NO_EVIDENCE


def test_layer3_does_not_export_bos_or_choch():
    assert not hasattr(structural, "BOS")
    assert not hasattr(structural, "CHoCH")
    assert not hasattr(structural, "POI")
    assert not hasattr(structural, "RR")
