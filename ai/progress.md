# Pacifica RiskLab -- Progress

## What Changed (Plain English)
The app got visual polish: the survival score is now a big hero element with a pulsing glow that changes color based on how bad the result is. Charts have colored accent dots and edge lines. The "Run Stress Test" button glows blue/purple. There's a green pulsing dot showing the live Pacifica connection. Background has subtle depth instead of flat black.

The code is now on GitHub and has a README explaining what it is, how to run it, and what the limitations are.

## Status: Polish Done, Demo Video Next

### Done
1. Simulation engine -- cascade model with market impact, funding rate stress
2. Pacifica API client -- 63 live markets, orderbook depth, funding history
3. Historical scenarios -- Oct 2025 (-14.5%), LUNA (-32%), Dec 2024, SVB, synthetic
4. FastAPI backend -- 3 endpoints, full pipeline
5. Svelte frontend -- market selector, scenario picker, parameter sliders, cascade chart, funding stress chart, compare mode, model limitations
6. Visual polish -- hero survival score, chart accents, button glow, live dot, background depth
7. GitHub repo -- https://github.com/Yonkoo11/pacifica-risklab
8. README with architecture, limitations, run instructions

### What's Next
- Demo video (do 24h before deadline)
- Submission (deadline April 16)

## To Resume
```bash
cd ~/Projects/pacifica-risklab/backend && python3 -m uvicorn main:app --reload &
cd ~/Projects/pacifica-risklab/frontend && npm run dev -- --port 5173 &
# Open http://localhost:5173
```
