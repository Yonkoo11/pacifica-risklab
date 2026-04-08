# Fix Plan - Pacifica RiskLab

## Tasks

- [ ] Task 1: Build liquidation cascade simulation engine (Python)
  - Acceptance: Given a position distribution, max leverage, maintenance margin, and a price shock percentage, output: number of liquidated positions per round, cumulative liquidation volume, final price after impact, and number of cascade rounds
  - Files: src/simulation/cascade.py, src/simulation/models.py

- [ ] Task 2: Build Pacifica API client
  - Acceptance: Pull live market parameters (max_leverage, OI, funding rate, mark price) for any Pacifica market. Pull funding rate history (4000 records). Pull recent liquidation trades filtered by cause field.
  - Files: src/api/pacifica.py

- [ ] Task 3: Build historical scenario loader
  - Acceptance: Load Oct 2025 crash, LUNA spiral, Hyperliquid JELLY, Dec 2024 BTC drop as price paths with timestamps. User can also define custom price paths.
  - Files: src/scenarios/historical.py, data/scenarios/

- [ ] Task 4: Connect simulation to live Pacifica data
  - Acceptance: User picks BTC-PERP on Pacifica, simulation auto-loads current parameters from API, runs Oct 2025 scenario, outputs cascade report
  - Files: src/simulation/runner.py

- [ ] Task 5: Build FastAPI backend
  - Acceptance: POST /simulate endpoint accepts market, scenario, optional parameter overrides. Returns simulation results as JSON. GET /markets returns available Pacifica markets with live parameters.
  - Files: src/api/server.py

- [ ] Task 6: Build Svelte frontend — parameter controls
  - Acceptance: User selects market (dropdown populated from API), selects scenario, can override parameters (leverage, margin). "Run Simulation" button triggers backend.
  - Files: frontend/src/routes/+page.svelte, frontend/src/lib/

- [ ] Task 7: Build Svelte frontend — results visualization
  - Acceptance: After simulation runs, display: liquidation cascade chart (rounds vs cumulative liquidations), funding rate stress timeline, parameter sensitivity heatmap, survival score
  - Files: frontend/src/lib/components/

- [ ] Task 8: Add parameter comparison mode
  - Acceptance: User runs simulation with current params, then tweaks params and runs again. Side-by-side comparison shows which config survives better.
  - Files: extends Task 6 and 7 components

- [ ] Task 9: Validate simulation against known incidents
  - Acceptance: Oct 2025 simulation output is within order of magnitude of $19B industry liquidations (scaled to Pacifica's OI). Document validation methodology.
  - Files: tests/, docs/validation.md

- [ ] Task 10: Demo video and submission prep
  - Acceptance: 2-3 min demo video showing: pick market → select crash scenario → see cascade → tweak parameters → compare → show how it helps Pacifica govern risk
  - Files: docs/

## Completed
(builder fills this in)
