"""Market impact model for liquidation cascades."""


def linear_impact(liquidation_volume_usd: float, orderbook_depth_usd: float) -> float:
    """
    Simplified linear market impact model.

    Returns the fractional price change caused by liquidating a given volume
    into an orderbook of a given depth.

    E.g., liquidating $1M into a $10M deep orderbook moves price by 10%.

    This is intentionally simple. Real cascades have non-linear dynamics
    (orderbook evaporates as fear spreads, market makers pull quotes).
    We state this limitation in the UI.
    """
    if orderbook_depth_usd <= 0:
        return 1.0  # total price collapse if no depth

    impact = liquidation_volume_usd / orderbook_depth_usd
    return min(impact, 1.0)  # cap at 100% price move


def sqrt_impact(liquidation_volume_usd: float, daily_volume_usd: float, k: float = 0.1) -> float:
    """
    Square-root market impact model (Almgren-Chriss inspired).

    impact = k * sqrt(V / ADV)

    More realistic for large volumes but requires daily volume data.
    k is market-specific; 0.1 is a reasonable default for crypto.
    """
    if daily_volume_usd <= 0:
        return 1.0

    import math
    impact = k * math.sqrt(liquidation_volume_usd / daily_volume_usd)
    return min(impact, 1.0)


def estimate_orderbook_depth(
    current_depth_usd: float,
    current_oi_usd: float,
    hypothetical_oi_usd: float,
) -> float:
    """
    Scale orderbook depth proportionally with OI for hypothetical scenarios.

    If Pacifica currently has $452 BTC OI and $1.2M orderbook depth,
    at $100M OI we'd expect proportionally deeper books (~$265M depth).

    This is a rough approximation. In reality, depth scales sub-linearly
    with volume (market makers don't scale infinitely).
    """
    if current_oi_usd <= 0:
        return current_depth_usd

    scale = hypothetical_oi_usd / current_oi_usd
    # Sub-linear scaling: depth ~ OI^0.7 (empirical from crypto markets)
    import math
    return current_depth_usd * (scale ** 0.7)
