# Vibecoder Mode - Paste this into any project's CLAUDE.md

## Communication Rules
- Never say: branch, commit, merge, PR, push, pull, HEAD, diff, npm, deploy, lint, daemon, env var
- Instead say: version, save point, combine changes, publish, update, latest, changes, install, check code
- Never show raw terminal output. Summarize in one sentence.
- Never show error messages directly. Say what happened and what you're doing to fix it.
- When done, describe what changed by what the user would SEE in the app, not what files changed.

## Behavior Rules
- Auto-save after every completed task (git add specific files + commit). Never ask "should I commit?"
- If you need to create a version, just do it silently.
- If tests fail, fix them without explaining test frameworks.
- After each task: update ai/progress.md with a "What Changed (Plain English)" section.
- Keep all explanations to 1-3 sentences. If the user wants more detail, they'll ask.

---

# Pacifica RiskLab

## What This Is
Self-serve perpetual futures parameter stress testing. What Gauntlet charges $1.6M/year for, as a free tool built on Pacifica's API.

## Phase 1 Gate (MUST PASS BEFORE ANY OTHER WORK)
**Core Action:** User picks a Pacifica market, selects a crash scenario, gets simulation report showing liquidation cascade estimate, funding rate stress, parameter survival analysis.
**Success Test:** Replay Oct 2025 crash against BTC-PERP's live Pacifica parameters. Output is directionally correct vs known industry data.
**NOT Phase 1:** Pretty UI, multi-market correlation, agent modeling, real-time monitoring, insurance fund, landing page.

## Build Order (ENFORCED)
1. Core simulation engine (Python) — cascade model works with static inputs
2. Pacifica API integration — pull live parameters, historical funding rates, liquidation trades
3. Historical scenario replay — feed real crash data through simulation
4. Web UI (Svelte + Vite) — parameter controls + results visualization
5. Visual polish LAST

## Hackathon
- **Name:** Pacifica Hackathon
- **Track:** Analytics & Data
- **Deadline:** April 16, 2026
- **Submit:** Code + demo video + documentation
- **Required:** Pacifica API and/or Builder Code

## Tech Stack
- Backend: Python (FastAPI) — simulation engine + Pacifica API client
- Frontend: Svelte + Vite — parameter controls + visualization
- Data: Historical price data (CoinGecko/Binance API for scenarios), Pacifica API for live parameters
- Visualization: D3.js or Chart.js for liquidation heat maps and cascade charts

## Pacifica API (Key Endpoints)
- `GET /info` — market specs, max_leverage per market
- `GET /info/prices` — live mark/oracle/OI/funding per market
- `GET /funding_rate/history` — up to 4000 records with oracle + impact prices
- `GET /trades` — cause field identifies liquidations (market_liquidation, backstop_liquidation)
- `GET /kline` — historical OHLCV candles
- `WS prices` — real-time streaming
- Base URL: `https://api.pacifica.fi/api/v1` (mainnet), `https://test-api.pacifica.fi/api/v1` (testnet)

## API Gaps (Known Limitations)
- No insurance fund data → model theoretically
- No long/short ratio → estimate from funding rate direction
- No historical OI → collect ourselves or approximate
- No dynamic margin state → use static max_leverage

## Research Base
- Idea #5 from ~/Projects/IDEAS-SUMMARY.md (Tier 1)
- Full memory in ai/memory.md
