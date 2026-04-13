"""Funding rate stress calculator."""


def calculate_funding_stress(
    initial_long_oi: float,
    initial_short_oi: float,
    cascade_results: list[dict],
    max_funding_rate: float = 0.000375,  # Pacifica default cap per hour
) -> list[dict]:
    """
    Model funding rate response during a liquidation cascade.

    When longs get liquidated, long OI drops, creating short imbalance.
    Funding goes negative (shorts pay longs) to incentivize rebalancing.

    Pacifica's funding = premium / 8, where premium ~ (OI_long - OI_short) / total_OI.
    This is a simplification; real funding depends on impact bid/ask prices.
    """
    long_oi = initial_long_oi
    short_oi = initial_short_oi

    stress_data = []

    for step in cascade_results:
        # Liquidated longs reduce long OI, liquidated shorts reduce short OI
        liq_volume = step.get("liquidated_volume", 0)
        long_liq = step.get("long_liquidated_volume", 0)
        short_liq = step.get("short_liquidated_volume", 0)

        long_oi -= long_liq
        short_oi -= short_liq

        total_oi = long_oi + short_oi
        if total_oi > 0:
            imbalance = (long_oi - short_oi) / total_oi
            # Simplified funding: proportional to imbalance
            # Positive imbalance (more longs) = positive funding (longs pay shorts)
            raw_rate = imbalance * 0.001  # scaling factor
            # Clamp to funding cap
            funding_rate = max(-max_funding_rate, min(raw_rate, max_funding_rate))
        else:
            imbalance = 0
            funding_rate = 0

        stress_data.append({
            "time_step": step.get("time_step", 0),
            "round": step.get("round", 0),
            "long_oi": long_oi,
            "short_oi": short_oi,
            "imbalance": imbalance,
            "funding_rate": funding_rate,
            "funding_rate_annualized": funding_rate * 8760,  # hourly to annual
            "at_cap": abs(funding_rate) >= max_funding_rate * 0.95,
        })

    return stress_data
