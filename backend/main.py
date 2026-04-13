"""FastAPI backend for Pacifica RiskLab."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from pacifica_client import PacificaClient
from simulation.engine import run_simulation
from simulation.impact import estimate_orderbook_depth
from scenarios.historical import load_scenario, get_price_path_absolute, list_scenarios

app = FastAPI(title="Pacifica RiskLab", description="Perpetual futures parameter stress testing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = PacificaClient()


# --- Request/Response Models ---

class SimulationRequest(BaseModel):
    symbol: str = "BTC"
    scenario: str = "oct_2025_crash"
    oi_override: Optional[float] = None  # hypothetical OI in USD
    leverage_override: Optional[float] = None
    mmr_override: Optional[float] = None
    long_ratio: float = 0.6
    num_positions: int = 1000


# --- Endpoints ---

@app.get("/api/markets")
def get_markets():
    """List all Pacifica markets with live data."""
    return client.get_combined_market_info()


@app.get("/api/scenarios")
def get_scenarios():
    """List available crash scenarios."""
    return list_scenarios()


@app.post("/api/simulate")
def simulate(req: SimulationRequest):
    """Run a liquidation cascade simulation."""
    # Get live market data from Pacifica
    all_markets = {m["symbol"]: m for m in client.get_combined_market_info()}

    if req.symbol not in all_markets:
        raise HTTPException(status_code=404, detail=f"Market {req.symbol} not found")

    market = all_markets[req.symbol]
    mark_price = market["mark"]
    max_leverage = req.leverage_override or market["max_leverage"]
    live_oi = market["open_interest"]

    # Use override OI or default to a reasonable hypothetical
    # (live OI is often tiny on Pacifica, so default to $50M for meaningful simulation)
    if req.oi_override:
        total_oi = req.oi_override
    elif live_oi < 100_000:
        total_oi = 50_000_000  # default $50M if live OI is tiny
    else:
        total_oi = live_oi

    # Get orderbook depth
    try:
        book = client.get_orderbook(req.symbol)
        live_depth = book.bid_depth_usd
    except Exception:
        live_depth = 1_000_000  # fallback $1M

    # Scale orderbook depth if using hypothetical OI
    if live_oi > 0:
        depth = estimate_orderbook_depth(live_depth, live_oi, total_oi)
    else:
        depth = total_oi * 0.05  # assume 5% depth ratio

    # Load scenario price path
    try:
        meta, scenario_path = load_scenario(req.scenario)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Scenario {req.scenario} not found")

    # Convert percentage path to absolute prices
    price_path = get_price_path_absolute(scenario_path, mark_price)

    # Downsample if too many points (keep simulation fast)
    if len(price_path) > 500:
        step = len(price_path) // 500
        price_path = price_path[::step]

    # Run simulation
    result = run_simulation(
        mark_price=mark_price,
        total_oi_usd=total_oi,
        max_leverage=max_leverage,
        price_path=price_path,
        orderbook_depth_usd=depth,
        long_ratio=req.long_ratio,
        num_positions=req.num_positions,
    )

    # Add market context to parameters
    result.parameters.update({
        "symbol": req.symbol,
        "scenario": req.scenario,
        "scenario_name": meta.get("name", req.scenario),
        "live_oi": live_oi,
        "live_mark_price": mark_price,
        "live_max_leverage": market["max_leverage"],
        "live_orderbook_depth": live_depth,
        "simulated_oi": total_oi,
        "simulated_depth": depth,
        "oi_is_hypothetical": req.oi_override is not None or live_oi < 100_000,
    })

    return result.to_dict()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
