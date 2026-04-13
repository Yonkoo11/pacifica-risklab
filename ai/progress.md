# Pacifica RiskLab — Progress

## What Changed (Plain English)
The simulation engine is built and working end-to-end. You can now stress-test any Pacifica market against real historical crash data.

## Status: Backend Complete, Frontend Next

### Done
1. **Simulation engine** — generates 1000 synthetic positions, runs liquidation cascade with market impact, tracks funding rate stress. All tests pass.
2. **Pacifica API client** — pulls live data from all 63 markets (prices, OI, funding, orderbook). Verified against live API.
3. **Historical crash scenarios** — fetched from Binance: Oct 2025 (-14.5%), LUNA spiral (-32%), Dec 2024 (-3.3%), SVB (-3.6%), plus synthetic 5% correction.
4. **FastAPI backend** — 3 endpoints working: GET /api/markets, GET /api/scenarios, POST /api/simulate. Full pipeline tested.

### Test Results
- BTC @ $72,340, 50x leverage, $100M hypothetical OI, Oct 2025 crash:
  - 613/1000 positions liquidated
  - 57% of OI wiped
  - Survival score: 3.9/10
- 50x produces significantly more liquidations than 10x (verified)

### In Progress
5. Svelte frontend with visualization

### Not Started
6. Comparison mode (two simulations side-by-side)
7. Visual polish + demo prep

## Key Findings During Build
- Pacifica BTC OI is only $452. Tool uses hypothetical OI levels by default.
- BTC orderbook has $4M bid depth (surprisingly deep for the OI level).
- Oct 2025 crash was -14.5% (from $122K to $104K), not -40% as initially stated.
- LUNA spiral is the most dramatic real scenario at -32%.
- All API values are strings (must parse to float). max_leverage is the only int.

## To Resume
Start FastAPI backend: `cd backend && python3 -m uvicorn main:app --reload`
Then build Svelte frontend in `frontend/` directory.
