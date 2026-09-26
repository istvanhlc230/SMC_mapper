from decimal import Decimal

import microstructure_engine as micro
import minor_structure_engine as minor


def c(i, o, h, l, cl):
    return micro.Candle(i, Decimal(o), Decimal(h), Decimal(l), Decimal(cl))


def test_bullish_pullback_forms_from_reference_low_takeout_then_high_break():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "10", "10", "1", "8"),
        c("pb2", "8", "11", "4", "10"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    pb = result.pullbacks[0]
    assert pb.reference_candle_id == "r"
    assert pb.start_candle_id == "pb1"
    assert pb.completion_candle_id == "pb2"
    assert pb.extreme.price == Decimal("1")
    assert pb.extreme.source_candle_id == "pb1"
    assert pb.liquidity_reference.side is minor.LiquiditySide.SELL_SIDE
    assert result.active.pullback is pb


def test_bearish_pullback_forms_from_reference_high_takeout_then_low_break():
    candles = (
        c("r", "9", "10", "2", "3"),
        c("cont", "3", "9", "1", "2"),
        c("pb1", "2", "11", "2", "8"),
        c("pb2", "8", "7", "1", "3"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BEARISH)
    assert len(result.pullbacks) == 1
    pb = result.pullbacks[0]
    assert pb.reference_candle_id == "r"
    assert pb.start_candle_id == "pb1"
    assert pb.completion_candle_id == "pb2"
    assert pb.extreme.price == Decimal("11")
    assert pb.extreme.source_candle_id == "pb1"
    assert pb.liquidity_reference.side is minor.LiquiditySide.BUY_SIDE


def test_breach_candle_color_is_not_a_validity_filter():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "7", "9", "1", "8"),
        c("pb2", "8", "11", "4", "10"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1


def test_inside_bar_does_not_replace_reference():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "10", "10", "1", "8"),
        c("inside", "8", "9", "2", "8.5"),
        c("pb3", "8.5", "11", "4", "10"),
    )
    assert micro.is_inside_bar(candles[3], candles[2])
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].reference_candle_id == "r"


def test_same_candle_outside_bar_cannot_confirm_intrabar_pullback_order():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("outside", "8", "12", "1", "7"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert result.pullbacks == ()


def test_later_outside_bar_cannot_confirm_pullback_completion_when_order_is_unavailable():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "10", "9", "1", "8"),
        c("outside_completion", "8", "12", "1", "7"),
        c("done", "7", "11", "4", "10"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert result.pullbacks == ()


def test_later_outside_bar_does_not_block_a_subsequent_observable_completion():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "10", "9", "1", "8"),
        c("outside_wait", "8", "12", "1", "7"),
        c("done", "7", "10", "4", "9.5"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].completion_candle_id == "done"


def test_newer_completed_pullback_becomes_active():
    candles = (
        c("r1", "5", "10", "2", "9"),
        c("c1", "9", "11", "3", "10"),
        c("p1", "10", "10", "1", "8"),
        c("done1", "8", "11", "4", "10"),
        c("r2", "10", "12", "8", "11"),
        c("c2", "11", "13", "9", "12"),
        c("p2", "12", "12", "6", "9"),
        c("done2", "9", "13", "7", "12"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) >= 2
    assert result.active.pullback is result.pullbacks[-1]
    assert result.active.reference is result.pullbacks[-1].liquidity_reference


def test_reference_does_not_jump_to_arbitrary_candle_inside_pullback():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "10", "10", "1", "8"),
        c("inside", "8", "9", "2", "8.5"),
        c("pb2", "8.5", "9", "1.5", "8"),
        c("done", "8", "11", "4", "10"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].reference_candle_id == "r"
    assert result.pullbacks[0].completion_candle_id == "done"


def test_layer2_resolution_is_explicit_when_no_event_exists():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("next", "10", "10.5", "3", "10.2"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert result.pullbacks == ()
    assert result.pending == ()
    assert result.resolution is minor.PullbackResolution.NONE


def test_layer2_exports_only_minor_structure_contract():
    assert not hasattr(minor, "IDM")
    assert not hasattr(minor, "BOS")
    assert not hasattr(minor, "CHoCH")
