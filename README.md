# RiskLab

Stress-test Pacifica's perpetual futures parameters against historical crashes.

Pick a market, pick a crash (Oct 2025 flash crash, LUNA death spiral, etc.), and see how many positions get liquidated, how the funding rate reacts, and whether the current parameter set survives.

Built for the Pacifica Hackathon (Analytics & Data track).

## What it does

1. Pulls live parameters from Pacifica's API (63 markets, max leverage, funding rates, orderbook depth)
2. Generates synthetic positions using log-normal leverage distribution and power-law sizes
3. Replays historical crash price paths through a cascade liquidation simulator
4. Shows you the damage: liquidation count, volume wiped, funding rate stress, survival score

You can also compare two parameter sets side-by-side. Change leverage from 50x to 20x and see exactly how many fewer positions get liquidated.

## Why it matters

Gauntlet charges $1.6M/year for parameter risk simulation. There's no open-source alternative for perp protocols. This tool lets anyone test whether a protocol's parameters can survive a real crash before it happens.

Pacifica's current BTC OI is ~$450 (the platform is new). The tool defaults to hypothetical OI levels ($50M-$1B) to answer the forward-looking question: "With these parameter settings, what breaks when you scale?"

## Screenshots

### Simulation results (BTC, Oct 2025 crash, $100M hypothetical OI)
Survival Score: 3.9/10. 613 positions liquidated. $56.7M volume wiped. 2 cascade rounds.

### Liquidation cascade chart
Red bars = cumulative liquidations per time step. Blue line = price. The spike around step 86 is where the cascade accelerates.

### Funding rate stress
Purple line = funding rate response. It swings negative as longs get liquidated and OI skews short.

## Run it locally

```bash
# Backend
cd backend
pip3 install fastapi uvicorn httpx
python3 -m uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev -- --port 5173

# Open http://localhost:5173
```

Requires Python 3.10+ and Node 18+. No API keys needed -- uses Pacifica's public endpoints.

## Architecture

```
backend/
  main.py                 # FastAPI, 3 endpoints
  pacifica_client.py      # Pacifica API wrapper (public, no auth)
  simulation/
    engine.py             # Cascade simulator
    positions.py          # Synthetic position generator
    impact.py             # Market impact model
    funding.py            # Funding rate stress calculator
  scenarios/
    historical.py         # 5 crash scenarios from Binance candle data
    loader.py             # Scenario definitions

frontend/                 # SvelteKit + Chart.js
  src/routes/+page.svelte # Main app
  src/lib/api.ts          # Backend API client
  src/lib/components/     # ResultsSummary, CascadeChart, FundingStress
```

## Simulation model

**Liquidation math:**
```
liq_price_long = entry * (1 - (1/leverage - MMR))
liq_price_short = entry * (1 + (1/leverage - MMR))
MMR = 1 / (2 * max_leverage)
```

**Cascade loop:** For each time step in the price path, find all positions below maintenance margin, liquidate them, apply market impact (linear model based on orderbook depth), check if the price drop triggers more liquidations. Repeat until stable or max rounds hit.

**Position generation:** 1000 synthetic positions with log-normal leverage distribution (mean ~30% of max), power-law size distribution (top 5% hold ~40% of OI), entry prices within +/-20% of mark.

## Honest limitations

- **Linear market impact.** Real cascades are non-linear -- the orderbook evaporates as fear spreads. Our model is simpler than reality.
- **Synthetic positions.** We're guessing at the position distribution. Log-normal leverage is a reasonable assumption but unverifiable without aggregate data.
- **No cross-margin.** Each market is simulated independently. Real cross-margined accounts share equity across positions.
- **Simplified funding.** Real funding depends on impact bid/ask prices that change during the cascade. We use a static approximation.

These are model limitations, not bugs. Every one is disclosed in the UI.

## Team

RiskLab (solo). Built for the Pacifica Hackathon, Analytics & Data track.

## License

MIT
