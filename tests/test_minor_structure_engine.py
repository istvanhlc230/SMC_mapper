from decimal import Decimal

import microstructure_engine as micro
import minor_structure_engine as minor


def c(i, o, h, l, cl):
    return micro.Candle(i, Decimal(o), Decimal(h), Decimal(l), Decimal(cl))


def test_bullish_pullback_forms_from_reference_low_takeout_then_high_break():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "9", "9.5", "1", "8"),
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
        c("pb1", "3", "11", "2.5", "8"),
        c("pb2", "8", "9", "1", "3"),
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
        c("pb1", "9", "9.5", "1", "8"),
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
    assert result.resolution is minor.PullbackResolution.PENDING_UNAVAILABLE_SEQUENCE
    assert len(result.pending) == 1
    assert result.pending[0].reference_candle_id == "r"
    assert result.pending[0].start_candle_id == "outside"


def test_later_outside_bar_cannot_confirm_pullback_completion_when_order_is_unavailable():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "9", "9.5", "1", "8"),
        c("outside_completion", "8", "12", "1", "7"),
        c("done", "7", "11", "4", "10"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].completion_candle_id == "done"
    assert result.pending == ()
    assert result.resolution is minor.PullbackResolution.CONFIRMED


def test_later_outside_bar_does_not_block_a_subsequent_observable_completion():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "9", "9.5", "1", "8"),
        c("outside_wait", "8", "12", "1", "7"),
        c("done", "7", "11", "4", "9.5"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].completion_candle_id == "done"
    assert result.pending == ()
    assert result.resolution is minor.PullbackResolution.CONFIRMED


def test_newer_completed_pullback_becomes_active():
    candles = (
        c("r1", "5", "10", "2", "9"),
        c("c1", "9", "11", "3", "10"),
        c("p1", "9.5", "9.5", "1", "8"),
        c("done1", "8", "11", "4", "10"),
        c("r2", "10", "12", "8", "11"),
        c("c2", "11", "13", "9", "12"),
        c("p2", "11.5", "11.5", "6", "9"),
        c("done2", "9", "14", "7", "12"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) >= 2
    assert result.active.pullback is result.pullbacks[-1]
    assert result.active.reference is result.pullbacks[-1].liquidity_reference


def test_reference_does_not_jump_to_arbitrary_candle_inside_pullback():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "9", "9.5", "1", "8"),
        c("inside", "8", "9", "2", "8.5"),
        c("pb2", "8.5", "9", "1.5", "8"),
        c("done", "8", "11", "4", "10"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].reference_candle_id == "r"
    assert result.pullbacks[0].completion_candle_id == "done"


def test_equal_high_transfers_active_reference_before_pullback_takeout():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("eqh", "9", "10", "4", "8"),
        c("take", "8", "10.5", "1", "7"),
        c("done", "7", "12", "5", "11"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    pb = result.pullbacks[0]
    assert pb.reference_candle_id == "eqh"
    assert pb.start_candle_id == "take"


def test_equal_low_transfers_active_reference_before_pullback_takeout():
    candles = (
        c("r", "5", "10", "2", "3"),
        c("cont", "3", "9", "1", "2"),
        c("eql", "2", "8", "2", "7"),
        c("take", "7", "9", "3", "8"),
        c("done", "3", "3.5", "0.5", "1"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BEARISH)
    assert len(result.pullbacks) == 1
    pb = result.pullbacks[0]
    assert pb.reference_candle_id == "eql"
    assert pb.start_candle_id == "take"


def test_non_directional_completion_does_not_reuse_already_broken_reference():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "9", "9.5", "1", "8"),
        c("done", "8", "11", "4", "9"),
        c("later", "9", "10.5", "1", "8"),
        c("new", "8", "12", "5", "11"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 2
    assert result.pullbacks[0].reference_candle_id == "r"


def test_equal_high_transfer_candle_cannot_take_its_own_new_reference_low():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("eqh", "10", "10", "1", "8"),
        c("take", "8", "9", "0.5", "7"),
        c("done", "7", "12", "5", "11"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].reference_candle_id == "eqh"
    assert result.pullbacks[0].start_candle_id == "take"


def test_equal_low_transfer_candle_cannot_take_its_own_new_reference_high():
    candles = (
        c("r", "5", "10", "2", "3"),
        c("cont", "3", "9", "1", "2"),
        c("eql", "2", "8", "2", "7"),
        c("take", "7", "9", "3", "8"),
        c("done", "3", "3.5", "0.5", "1"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BEARISH)
    assert len(result.pullbacks) == 1
    assert result.pullbacks[0].reference_candle_id == "eql"
    assert result.pullbacks[0].start_candle_id == "take"


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


def test_reference_touch_is_not_a_pullback_takeout():
    bullish = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("touch", "9", "9.5", "2", "8"),
    )
    bearish = (
        c("r", "9", "10", "2", "3"),
        c("cont", "3", "9", "1", "2"),
        c("touch", "2", "10", "1", "8"),
    )
    assert minor.detect_valid_pullbacks(
        bullish, minor.PullbackDirection.BULLISH
    ).resolution is minor.PullbackResolution.NONE
    assert minor.detect_valid_pullbacks(
        bearish, minor.PullbackDirection.BEARISH
    ).resolution is minor.PullbackResolution.NONE



def test_pending_latest_state_overrides_historical_confirmation():
    candles = (
        c("r", "5", "10", "2", "9"),
        c("cont", "9", "11", "3", "10"),
        c("pb1", "9", "9.5", "1", "8"),
        c("done", "8", "11", "4", "10"),
        c("outside_pending", "10", "12", "1", "7"),
    )
    result = minor.detect_valid_pullbacks(candles, minor.PullbackDirection.BULLISH)
    assert len(result.pullbacks) == 1
    assert result.active.pullback is result.pullbacks[0]
    assert len(result.pending) == 1
    assert result.resolution is minor.PullbackResolution.PENDING_UNAVAILABLE_SEQUENCE


def test_layer2_exports_only_minor_structure_contract():
    assert not hasattr(minor, "IDM")
    assert not hasattr(minor, "BOS")
    assert not hasattr(minor, "CHoCH")
