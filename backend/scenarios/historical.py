"""Fetch historical crash data from Binance API for scenario replay."""

import requests
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'scenarios')


def fetch_binance_klines(symbol: str, interval: str, start_ms: int, end_ms: int) -> list[dict]:
    """Fetch kline data from Binance API. Returns list of {timestamp, open, high, low, close}."""
    url = "https://api.binance.com/api/v3/klines"
    all_candles = []
    current_start = start_ms

    while current_start < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "endTime": end_ms,
            "limit": 1000,
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        for candle in data:
            all_candles.append({
                "timestamp": candle[0],
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
            })

        # Move past the last candle
        current_start = data[-1][0] + 1

        if len(data) < 1000:
            break

    return all_candles


def normalize_to_pct_path(candles: list[dict]) -> list[dict]:
    """Convert absolute prices to percentage changes from the first candle."""
    if not candles:
        return []

    base_price = candles[0]["close"]
    path = []
    for c in candles:
        path.append({
            "timestamp": c["timestamp"],
            "price_pct": c["close"] / base_price,  # 1.0 = no change, 0.6 = -40%
            "price_abs": c["close"],
        })
    return path


# --- Scenario Definitions ---

SCENARIOS = {
    "oct_2025_crash": {
        "name": "October 2025 Flash Crash",
        "description": "BTC dropped ~18% from $122K to $102K intraday. $19B liquidated industry-wide, 1.6M traders affected.",
        "symbol": "BTCUSDT",
        "interval": "1m",
        # Oct 9, 2025 12:00 UTC to Oct 11, 2025 12:00 UTC (captures the full crash window)
        "start_ms": 1760097600000,
        "end_ms": 1760270400000,
        "severity": "extreme",
    },
    "luna_spiral": {
        "name": "LUNA/UST Death Spiral (May 2022)",
        "description": "BTC dropped ~40% over 10 days as LUNA collapsed. Cascading liquidations across all venues.",
        "symbol": "BTCUSDT",
        "interval": "15m",
        # May 5, 2022 to May 15, 2022
        "start_ms": 1651708800000,
        "end_ms": 1652572800000,
        "severity": "catastrophic",
    },
    "dec_2024_flash": {
        "name": "December 2024 BTC Flash Drop",
        "description": "BTC dropped ~7% from $103K to $92K in hours. $400M+ liquidated.",
        "symbol": "BTCUSDT",
        "interval": "1m",
        # Dec 9, 2024 12:00 to Dec 10, 2024 12:00 UTC
        "start_ms": 1733745600000,
        "end_ms": 1733832000000,
        "severity": "moderate",
    },
    "svb_crash_2023": {
        "name": "SVB Bank Run (March 2023)",
        "description": "BTC dropped ~10% in hours as Silicon Valley Bank collapsed.",
        "symbol": "BTCUSDT",
        "interval": "5m",
        # Mar 10, 2023 to Mar 12, 2023
        "start_ms": 1678406400000,
        "end_ms": 1678579200000,
        "severity": "moderate",
    },
    "mild_correction": {
        "name": "Mild 5% Correction",
        "description": "Synthetic scenario: steady 5% decline over 6 hours. Tests parameter sensitivity.",
        "symbol": None,  # synthetic, no Binance fetch needed
        "interval": "1m",
        "severity": "mild",
    },
}


def generate_synthetic_scenario(name: str, steps: int = 360) -> list[dict]:
    """Generate synthetic price paths for non-historical scenarios."""
    if name == "mild_correction":
        # Linear 5% drop over 360 steps (6 hours at 1m)
        return [{"timestamp": i * 60000, "price_pct": 1.0 - (0.05 * i / steps)} for i in range(steps + 1)]
    return []


def fetch_and_save_scenario(scenario_id: str) -> list[dict]:
    """Fetch historical data from Binance and save as JSON."""
    scenario = SCENARIOS[scenario_id]

    if scenario["symbol"] is None:
        path = generate_synthetic_scenario(scenario_id)
    else:
        candles = fetch_binance_klines(
            scenario["symbol"],
            scenario["interval"],
            scenario["start_ms"],
            scenario["end_ms"],
        )
        path = normalize_to_pct_path(candles)

    # Save to disk
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{scenario_id}.json")
    with open(filepath, "w") as f:
        json.dump({
            "id": scenario_id,
            "meta": {k: v for k, v in scenario.items() if k != "symbol"},
            "path": path,
        }, f, indent=2)

    return path


def load_scenario(scenario_id: str) -> tuple[dict, list[dict]]:
    """Load a scenario. Fetch from Binance if not cached."""
    filepath = os.path.join(DATA_DIR, f"{scenario_id}.json")

    if os.path.exists(filepath):
        with open(filepath) as f:
            data = json.load(f)
            return data["meta"], data["path"]

    if scenario_id not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_id}")

    path = fetch_and_save_scenario(scenario_id)
    meta = {k: v for k, v in SCENARIOS[scenario_id].items() if k != "symbol"}
    return meta, path


def get_price_path_absolute(scenario_path: list[dict], start_price: float) -> list[float]:
    """Convert percentage price path to absolute prices given a starting price."""
    return [start_price * p["price_pct"] for p in scenario_path]


def list_scenarios() -> list[dict]:
    """List all available scenarios with metadata."""
    result = []
    for sid, s in SCENARIOS.items():
        cached = os.path.exists(os.path.join(DATA_DIR, f"{sid}.json"))
        result.append({
            "id": sid,
            "name": s["name"],
            "description": s["description"],
            "severity": s["severity"],
            "cached": cached,
        })
    return result


if __name__ == "__main__":
    print("Fetching all scenarios from Binance...")
    for sid in SCENARIOS:
        print(f"\n--- {SCENARIOS[sid]['name']} ---")
        meta, path = load_scenario(sid)
        if path:
            start = path[0]["price_pct"]
            end = path[-1]["price_pct"]
            low = min(p["price_pct"] for p in path)
            print(f"  Points: {len(path)}")
            print(f"  Start→End: {start:.4f} → {end:.4f} ({(end-1)*100:+.1f}%)")
            print(f"  Lowest: {low:.4f} ({(low-1)*100:+.1f}%)")
        else:
            print("  No data")
