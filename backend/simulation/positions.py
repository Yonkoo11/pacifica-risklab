"""Synthetic position generator for liquidation cascade simulation."""

import numpy as np
from dataclasses import dataclass


@dataclass
class Position:
    side: str  # "long" or "short"
    entry_price: float
    size_usd: float  # notional in USD
    leverage: float

    @property
    def size_base(self) -> float:
        return self.size_usd / self.entry_price

    @property
    def margin(self) -> float:
        return self.size_usd / self.leverage

    @property
    def mmr(self) -> float:
        """Maintenance margin ratio = half of initial margin ratio."""
        return 1.0 / (2.0 * self.leverage)

    @property
    def liquidation_price(self) -> float:
        drop_pct = (1.0 / self.leverage) - self.mmr
        if self.side == "long":
            return self.entry_price * (1.0 - drop_pct)
        else:
            return self.entry_price * (1.0 + drop_pct)

    def is_liquidatable(self, current_price: float) -> bool:
        if self.side == "long":
            return current_price <= self.liquidation_price
        else:
            return current_price >= self.liquidation_price

    @property
    def notional_at_entry(self) -> float:
        return self.size_usd


def generate_positions(
    total_oi_usd: float,
    max_leverage: float,
    mark_price: float,
    long_ratio: float = 0.6,
    num_positions: int = 1000,
    seed: int = 42,
) -> list[Position]:
    """
    Generate synthetic positions matching a given OI and leverage distribution.

    Leverage: log-normal, mean at ~30% of max, fat tail toward max.
    Position sizes: power-law (Pareto). Top 5% hold ~40% of OI.
    Entry prices: normal distribution around mark_price, std = 5% of price.
    """
    rng = np.random.default_rng(seed)

    # --- Leverage distribution ---
    # Log-normal with mean around 30% of max leverage
    target_mean = max_leverage * 0.3
    sigma_lev = 0.8  # controls spread
    mu_lev = np.log(target_mean) - (sigma_lev ** 2) / 2
    leverages = rng.lognormal(mu_lev, sigma_lev, num_positions)
    # Clip to [1, max_leverage]
    leverages = np.clip(leverages, 1.0, max_leverage)

    # --- Position size distribution (Pareto / power-law) ---
    # alpha=1.5 gives ~40% of value in top 5% of positions
    alpha = 1.5
    raw_sizes = (rng.pareto(alpha, num_positions) + 1)
    # Normalize so they sum to total_oi_usd
    raw_sizes = raw_sizes / raw_sizes.sum() * total_oi_usd

    # --- Entry price distribution ---
    # Normal around mark_price, std = 5%
    entry_prices = rng.normal(mark_price, mark_price * 0.05, num_positions)
    entry_prices = np.clip(entry_prices, mark_price * 0.5, mark_price * 1.5)

    # --- Long/short assignment ---
    num_longs = int(num_positions * long_ratio)
    sides = ["long"] * num_longs + ["short"] * (num_positions - num_longs)
    rng.shuffle(sides)

    positions = []
    for i in range(num_positions):
        positions.append(Position(
            side=sides[i],
            entry_price=float(entry_prices[i]),
            size_usd=float(raw_sizes[i]),
            leverage=float(leverages[i]),
        ))

    return positions
