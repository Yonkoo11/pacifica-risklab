"""Core liquidation cascade simulation engine."""

from dataclasses import dataclass, field
from .positions import Position, generate_positions
from .impact import linear_impact, estimate_orderbook_depth
from .funding import calculate_funding_stress


@dataclass
class CascadeStep:
    time_step: int
    round: int
    price_before: float
    price_after: float
    liquidated_count: int
    liquidated_volume_usd: float
    long_liquidated_volume: float
    short_liquidated_volume: float
    remaining_positions: int
    remaining_oi_usd: float


@dataclass
class SimulationResult:
    # Summary
    total_liquidated: int
    total_liquidated_volume_usd: float
    total_positions: int
    cascade_rounds: int
    max_drawdown_pct: float
    price_start: float
    price_end: float

    # Detail
    cascade_steps: list[CascadeStep] = field(default_factory=list)
    funding_stress: list[dict] = field(default_factory=list)

    # Parameters used
    parameters: dict = field(default_factory=dict)

    @property
    def survival_score(self) -> float:
        """0-10 score. 10 = no liquidations. 0 = everything liquidated."""
        if self.total_positions == 0:
            return 0.0
        survived_pct = 1.0 - (self.total_liquidated / self.total_positions)
        return round(survived_pct * 10, 1)

    @property
    def oi_wipe_pct(self) -> float:
        total_oi = self.parameters.get("total_oi_usd", 1)
        if total_oi <= 0:
            return 0.0
        return round(self.total_liquidated_volume_usd / total_oi * 100, 2)

    def to_dict(self) -> dict:
        return {
            "summary": {
                "total_liquidated": self.total_liquidated,
                "total_liquidated_volume_usd": round(self.total_liquidated_volume_usd, 2),
                "total_positions": self.total_positions,
                "cascade_rounds": self.cascade_rounds,
                "max_drawdown_pct": round(self.max_drawdown_pct, 2),
                "price_start": round(self.price_start, 2),
                "price_end": round(self.price_end, 2),
                "survival_score": self.survival_score,
                "oi_wipe_pct": self.oi_wipe_pct,
            },
            "cascade_data": [
                {
                    "time_step": s.time_step,
                    "round": s.round,
                    "price_before": round(s.price_before, 2),
                    "price_after": round(s.price_after, 2),
                    "liquidated_count": s.liquidated_count,
                    "liquidated_volume_usd": round(s.liquidated_volume_usd, 2),
                    "remaining_positions": s.remaining_positions,
                    "remaining_oi_usd": round(s.remaining_oi_usd, 2),
                }
                for s in self.cascade_steps
            ],
            "funding_stress": self.funding_stress,
            "parameters": self.parameters,
        }


def simulate_cascade(
    positions: list[Position],
    price_path: list[float],
    orderbook_depth_usd: float,
    max_cascade_rounds: int = 50,
) -> SimulationResult:
    """
    Run liquidation cascade simulation.

    price_path: list of absolute prices at each time step.
    orderbook_depth_usd: total bid-side depth in USD.
    """
    all_steps = []
    total_liquidated = 0
    total_liq_volume = 0.0
    total_positions = len(positions)
    price_start = price_path[0]
    min_price = price_start
    active_positions = list(positions)

    for time_step, base_price in enumerate(price_path):
        current_price = base_price
        round_num = 0

        while round_num < max_cascade_rounds:
            # Find liquidatable positions at current price
            liquidatable = [p for p in active_positions if p.is_liquidatable(current_price)]

            if not liquidatable:
                break

            # Split by side for funding stress tracking
            long_liqs = [p for p in liquidatable if p.side == "long"]
            short_liqs = [p for p in liquidatable if p.side == "short"]

            long_liq_vol = sum(p.notional_at_entry for p in long_liqs)
            short_liq_vol = sum(p.notional_at_entry for p in short_liqs)
            liq_volume = long_liq_vol + short_liq_vol

            price_before = current_price

            # Apply market impact from liquidations
            # Longs being liquidated = sells pushing price down
            # Shorts being liquidated = buys pushing price up
            net_sell_pressure = long_liq_vol - short_liq_vol
            if net_sell_pressure > 0:
                impact = linear_impact(net_sell_pressure, orderbook_depth_usd)
                current_price *= (1.0 - impact)
            elif net_sell_pressure < 0:
                impact = linear_impact(abs(net_sell_pressure), orderbook_depth_usd)
                current_price *= (1.0 + impact)

            # Remove liquidated positions
            for p in liquidatable:
                active_positions.remove(p)

            remaining_oi = sum(p.notional_at_entry for p in active_positions)

            step = CascadeStep(
                time_step=time_step,
                round=round_num,
                price_before=price_before,
                price_after=current_price,
                liquidated_count=len(liquidatable),
                liquidated_volume_usd=liq_volume,
                long_liquidated_volume=long_liq_vol,
                short_liquidated_volume=short_liq_vol,
                remaining_positions=len(active_positions),
                remaining_oi_usd=remaining_oi,
            )
            all_steps.append(step)

            total_liquidated += len(liquidatable)
            total_liq_volume += liq_volume
            round_num += 1

        min_price = min(min_price, current_price)

        if not active_positions:
            break

    # Calculate funding stress
    initial_long_oi = sum(p.notional_at_entry for p in positions if p.side == "long")
    initial_short_oi = sum(p.notional_at_entry for p in positions if p.side == "short")

    step_dicts = [
        {
            "time_step": s.time_step,
            "round": s.round,
            "liquidated_volume": s.liquidated_volume_usd,
            "long_liquidated_volume": s.long_liquidated_volume,
            "short_liquidated_volume": s.short_liquidated_volume,
        }
        for s in all_steps
    ]
    funding_stress = calculate_funding_stress(initial_long_oi, initial_short_oi, step_dicts)

    price_end = min_price
    max_drawdown = (price_start - min_price) / price_start * 100 if price_start > 0 else 0

    return SimulationResult(
        total_liquidated=total_liquidated,
        total_liquidated_volume_usd=total_liq_volume,
        total_positions=total_positions,
        cascade_rounds=max(s.round for s in all_steps) + 1 if all_steps else 0,
        max_drawdown_pct=max_drawdown,
        price_start=price_start,
        price_end=price_end,
        cascade_steps=all_steps,
        funding_stress=funding_stress,
        parameters={},
    )


def run_simulation(
    mark_price: float,
    total_oi_usd: float,
    max_leverage: float,
    price_path: list[float],
    orderbook_depth_usd: float,
    long_ratio: float = 0.6,
    num_positions: int = 1000,
    seed: int = 42,
) -> SimulationResult:
    """
    High-level simulation runner.

    Generates positions, runs cascade, returns results.
    """
    positions = generate_positions(
        total_oi_usd=total_oi_usd,
        max_leverage=max_leverage,
        mark_price=mark_price,
        long_ratio=long_ratio,
        num_positions=num_positions,
        seed=seed,
    )

    result = simulate_cascade(
        positions=positions,
        price_path=price_path,
        orderbook_depth_usd=orderbook_depth_usd,
    )

    result.parameters = {
        "mark_price": mark_price,
        "total_oi_usd": total_oi_usd,
        "max_leverage": max_leverage,
        "long_ratio": long_ratio,
        "num_positions": num_positions,
        "orderbook_depth_usd": orderbook_depth_usd,
        "price_path_length": len(price_path),
    }

    return result
