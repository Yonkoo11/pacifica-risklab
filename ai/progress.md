# Pacifica RiskLab — Progress

## What Changed (Plain English)
The complete app is working. You can open it, pick any Pacifica market, select a historical crash scenario, and see exactly how many positions would get liquidated, how the funding rate reacts, and whether the current parameters survive. You can also compare two different parameter settings side-by-side.

## Status: Core Product Complete

### Done
1. Simulation engine — cascade model with market impact, funding rate stress
2. Pacifica API client — 63 live markets, orderbook depth, funding history
3. Historical scenarios — Oct 2025 (-14.5%), LUNA (-32%), Dec 2024, SVB, synthetic
4. FastAPI backend — 3 endpoints, full pipeline
5. Svelte frontend — market selector, scenario picker, parameter sliders, cascade chart, funding stress chart, compare mode, model limitations

### Verified Results (Oct 2025 crash, BTC 50x, $100M OI)
- Survival Score: 3.9/10
- 612/1000 positions liquidated
- $56.6M volume liquidated (56.6% of OI)
- 2 cascade rounds
- Max drawdown: -14.2%

### What's Next (Polish Phase)
- `/design pacifica-risklab` for visual polish
- GitHub repo creation + push
- README with screenshots
- Demo video
- Submission

## To Resume
```bash
cd ~/Projects/pacifica-risklab/backend && python3 -m uvicorn main:app --reload &
cd ~/Projects/pacifica-risklab/frontend && npm run dev -- --port 5173 &
# Open http://localhost:5173
```
