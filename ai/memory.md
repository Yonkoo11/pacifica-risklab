# Pacifica RiskLab — AI Memory

## Phase 1 Gate (MUST PASS BEFORE ANY OTHER WORK)
Core Action: User picks a Pacifica market (BTC-PERP), selects a historical crash scenario, gets simulation report showing: estimated liquidation cascade size, funding rate spike, parameter stress analysis
Success Test: Replay Oct 2025 flash crash (-40% in hours) against BTC-PERP's live Pacifica parameters. Output shows estimated liquidations, funding rate stress, and margin utilization that are directionally correct vs what happened on comparable platforms.
Min Tech: Python backend (Pacifica SDK), historical price data, simulation engine, basic web UI
NOT Phase 1: Pretty design, multi-market correlation, agent-based modeling, real-time monitoring, insurance fund modeling (API doesn't expose it), landing page, social

Status: [ ] NOT STARTED

## Hackathon Context
- **Name:** Pacifica Hackathon
- **Track:** Analytics & Data
- **Deadline:** April 16, 2026
- **Judging:** Innovation, Technical Execution, UX, Potential Impact, Presentation
- **Must submit:** Code, demo video, documentation
- **Required tech:** Pacifica API and/or Builder Code
- **Partner tools:** Fuul, Rhinofi, Privy
- **Prize target:** Track Winner ($2K + 14K pts) or "Most Innovative Use" special award ($1K + 7K pts)

## Chosen Idea
**#5 DeFi parameter simulation (Tier 1)** adapted for perpetual futures.
What Gauntlet sells for $1.6M/year, democratized as a self-serve tool for Pacifica.

## Why This Wins
1. Zero open-source perp parameter simulation tools exist (verified: arXiv paper only, no usable tool)
2. High "Innovation" score — judges won't see anything like this from other teams
3. Deep "Technical Execution" — real simulation engine, not a dashboard wrapper
4. High "Potential Impact" — Pacifica themselves need this for parameter governance
5. Genuine product beyond hackathon — every perp DEX needs parameter simulation

## Competitive Landscape
- Gauntlet: $1.6M/year enterprise contracts, no self-serve
- Chaos Labs: Risk Oracles on Jupiter, Genesis Framework for GMX. No self-serve.
- PerpSim (Perpetual Protocol): LP backtesting only, not protocol risk
- LFEST: Rust strategy testbed, not risk simulation
- Academic: arXiv:2501.09404 (agent-based model, not a tool)
- Gap: NOBODY has built self-serve perp parameter simulation

## Fatal Flaws
1. No insurance fund data from Pacifica API — must model theoretically, not from real data
2. No aggregate long/short ratio — only total OI. Must estimate distribution
3. No historical OI snapshots — must collect ourselves or approximate from funding rate history
4. Trust gap: simulation results need validation against known incidents to be credible
5. Simplified model vs Gauntlet's agent-based approach — honest about what this approximates

## Pacifica API Inventory (Key Endpoints for Simulation)

### Public (no auth needed)
| Endpoint | Data | Notes |
|----------|------|-------|
| GET /info | Per-market: max_leverage, tick_size, lot_size, min/max order | 35+ pairs |
| GET /info/prices | mark, oracle, mid, funding, next_funding, open_interest, volume_24h | Real-time per symbol |
| GET /funding_rate/history | oracle_price, bid/ask_impact_price, funding_rate, next_funding_rate | Up to 4000 records, paginated |
| GET /trades | price, amount, side, **cause** (normal/market_liquidation/backstop_liquidation) | cause field identifies liquidations |
| GET /book | 10 levels per side, 5 aggregation tiers | Orderbook depth |
| GET /kline | OHLCV candles, 1m to 1d intervals | Historical prices |
| WS prices | Real-time mark/oracle/OI/funding | All markets |
| WS trades | Real-time trades with liquidation cause | Per market |

### Authenticated (need wallet signature)
| Endpoint | Data |
|----------|------|
| GET /positions | Per-position: symbol, side, amount, entry_price, margin, funding, liquidation_price |
| GET /trades/history | Historical trades with PnL and cause |
| GET /funding/history | Per-account funding payments |

### API Gaps (Confirmed Missing)
- No insurance fund balance/status
- No aggregate long/short split (only total OI)
- No aggregate position distribution
- No dynamic margin state (only static max_leverage)
- No historical OI snapshots

## Simulation Architecture (Senior Dev Approach)

### What the tool does:
1. **Pull live parameters** from Pacifica API (/info + /info/prices)
2. **Load historical price scenario** (Oct 2025 crash, LUNA spiral, JELLY attack, custom)
3. **Simulate** what happens to positions under that scenario with those parameters
4. **Output**: liquidation cascade estimate, funding rate stress, margin utilization, parameter survival score
5. **Compare**: change parameters (lower leverage, tighten margins) and re-run

### Simulation Model (Phase 1 — Simplified)
- Assume position distribution follows power law (few whales, many small)
- Given OI and max leverage, estimate position sizes and leverage distribution
- Apply price shock → calculate which positions breach maintenance margin
- Liquidated positions create market impact → recalculate prices → check next round
- Track cumulative liquidations, estimated slippage, and funding rate response

### Historical Scenarios to Implement
1. **Oct 2025 Flash Crash**: BTC -40% in hours, $19B liquidations industry-wide
2. **LUNA/UST Death Spiral (May 2022)**: $80 → $0, cascading across all venues
3. **Hyperliquid JELLY Attack (Mar 2025)**: Illiquid token pump 429%, oracle manipulation
4. **Dec 2024 BTC Drop**: -7% flash, $400M+ liquidations
5. **Custom**: User defines price path and speed

## Key Reference Incidents for Validation
- Oct 2025: $19.13B liquidations, 1.6M traders, $16.7B were longs
- JELLY: $4.1M short, 429% pump, HLP vault $13.5M unrealized loss
- 2025 full year: $154B total forced liquidations, ~$400-500M daily average

## Decisions
- Track: Analytics & Data (not DeFi Composability — this is risk intelligence)
- Backend: Python (Pacifica SDK is Python, simulation is compute-heavy)
- Frontend: Svelte + Vite (default stack per global rules)
- Model: Simplified cascade model first, not agent-based (Phase 1 constraint)
- Validation: Compare simulation output against known incident magnitudes
