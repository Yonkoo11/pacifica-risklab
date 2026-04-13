"""Tests for the simulation engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.simulation.positions import Position, generate_positions
from backend.simulation.engine import run_simulation


def test_position_liquidation_price_long():
    """BTC 50x long should liquidate at ~1% drop."""
    p = Position(side="long", entry_price=72000, size_usd=10000, leverage=50)
    # MMR = 1/(2*50) = 1%
    # drop_pct = 1/50 - 1/100 = 0.01
    # liq_price = 72000 * (1 - 0.01) = 71280
    assert abs(p.liquidation_price - 71280) < 1
    assert p.is_liquidatable(71280)
    assert not p.is_liquidatable(71500)


def test_position_liquidation_price_short():
    """BTC 50x short should liquidate at ~1% rise."""
    p = Position(side="short", entry_price=72000, size_usd=10000, leverage=50)
    # liq_price = 72000 * (1 + 0.01) = 72720
    assert abs(p.liquidation_price - 72720) < 1
    assert p.is_liquidatable(72720)
    assert not p.is_liquidatable(72500)


def test_position_liquidation_low_leverage():
    """SOL 20x should liquidate at ~2.5% drop."""
    p = Position(side="long", entry_price=100, size_usd=5000, leverage=20)
    # drop_pct = 1/20 - 1/40 = 0.025
    # liq = 100 * 0.975 = 97.5
    assert abs(p.liquidation_price - 97.5) < 0.01


def test_position_liquidation_5x():
    """PUMP 5x should liquidate at ~10% drop."""
    p = Position(side="long", entry_price=1.0, size_usd=1000, leverage=5)
    # drop_pct = 1/5 - 1/10 = 0.1
    # liq = 1.0 * 0.9 = 0.9
    assert abs(p.liquidation_price - 0.9) < 0.001


def test_generate_positions_total_oi():
    """Generated positions should sum to the specified OI."""
    positions = generate_positions(
        total_oi_usd=100_000_000,
        max_leverage=50,
        mark_price=72000,
    )
    total = sum(p.size_usd for p in positions)
    assert abs(total - 100_000_000) < 1  # within $1


def test_generate_positions_leverage_bounds():
    """All leverages should be between 1 and max_leverage."""
    positions = generate_positions(
        total_oi_usd=50_000_000,
        max_leverage=20,
        mark_price=80,
    )
    for p in positions:
        assert 1.0 <= p.leverage <= 20.0


def test_generate_positions_long_ratio():
    """Long/short split should match requested ratio."""
    positions = generate_positions(
        total_oi_usd=10_000_000,
        max_leverage=50,
        mark_price=72000,
        long_ratio=0.7,
    )
    longs = sum(1 for p in positions if p.side == "long")
    assert longs == 700  # 70% of 1000


def test_simulation_produces_liquidations():
    """A -40% crash at 50x leverage must produce liquidations."""
    mark_price = 72000
    # Price path: drop 40% in 10 steps
    price_path = [mark_price * (1 - 0.04 * i) for i in range(11)]

    result = run_simulation(
        mark_price=mark_price,
        total_oi_usd=100_000_000,
        max_leverage=50,
        price_path=price_path,
        orderbook_depth_usd=50_000_000,  # $50M depth
        long_ratio=0.6,
    )

    assert result.total_liquidated > 0
    assert result.total_liquidated_volume_usd > 0
    assert result.cascade_rounds > 0
    assert len(result.cascade_steps) > 0
    assert result.survival_score < 10.0  # some positions liquidated
    print(f"\n--- Simulation Results ---")
    print(f"Liquidated: {result.total_liquidated}/{result.total_positions} positions")
    print(f"Volume: ${result.total_liquidated_volume_usd:,.0f}")
    print(f"Cascade rounds: {result.cascade_rounds}")
    print(f"Max drawdown: {result.max_drawdown_pct:.1f}%")
    print(f"Survival score: {result.survival_score}/10")
    print(f"OI wiped: {result.oi_wipe_pct}%")


def test_simulation_no_liquidation_small_drop():
    """A -0.5% drop should liquidate very few positions at 10x leverage."""
    mark_price = 100
    price_path = [mark_price * (1 - 0.005)]

    result = run_simulation(
        mark_price=mark_price,
        total_oi_usd=10_000_000,
        max_leverage=10,
        price_path=price_path,
        orderbook_depth_usd=5_000_000,
    )

    # At 10x, liquidation requires ~5% drop. 0.5% should liquidate very few.
    assert result.total_liquidated < 100  # less than 10% of positions


def test_higher_leverage_more_liquidations():
    """50x leverage should produce more liquidations than 10x for the same crash."""
    mark_price = 72000
    price_path = [mark_price * (1 - 0.02 * i) for i in range(11)]

    result_50x = run_simulation(
        mark_price=mark_price,
        total_oi_usd=100_000_000,
        max_leverage=50,
        price_path=price_path,
        orderbook_depth_usd=50_000_000,
    )

    result_10x = run_simulation(
        mark_price=mark_price,
        total_oi_usd=100_000_000,
        max_leverage=10,
        price_path=price_path,
        orderbook_depth_usd=50_000_000,
    )

    assert result_50x.total_liquidated > result_10x.total_liquidated
    print(f"\n50x: {result_50x.total_liquidated} liquidated, 10x: {result_10x.total_liquidated} liquidated")


if __name__ == "__main__":
    test_position_liquidation_price_long()
    test_position_liquidation_price_short()
    test_position_liquidation_low_leverage()
    test_position_liquidation_5x()
    test_generate_positions_total_oi()
    test_generate_positions_leverage_bounds()
    test_generate_positions_long_ratio()
    test_simulation_produces_liquidations()
    test_simulation_no_liquidation_small_drop()
    test_higher_leverage_more_liquidations()
    print("\n✅ All tests passed")
