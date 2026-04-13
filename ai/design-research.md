# Design Research Brief

## Product Category: DeFi Risk Analytics Dashboard
## Comparables Studied: Hyperliquid, Chaos Labs, Grafana, Linear, TradingView

## Common Patterns (table stakes):
- Dark-first, single-column or sidebar+main layout
- Neutral sans-serif (Inter, system-ui) with tabular-nums for data
- Metric cards for KPIs at top, charts below
- Muted text hierarchy (bright for values, dim for labels)
- Red/green for directional data (bad/good, loss/gain)

## Differentiation Opportunities:
- Most risk dashboards are pure data grids with zero personality. Adding a product metaphor (pressure gauge, stress meter) would stand out
- Chaos Labs and Gauntlet dashboards are enterprise-only, never self-serve. The "anyone can use this" angle is the differentiator
- None of these use the survival score concept as a hero element. This is unique to RiskLab

## Design Constraints:
- Must handle dense data (6 metrics + 2 charts + limitations)
- Sidebar controls + main results is already the right layout
- Charts are Chart.js (limited styling control vs D3)
- Single page app, no routing needed

## Anti-patterns (must avoid):
- Purple-blue gradient anything (style config hard-no)
- Gradient text (style config hard-no)  
- Generic SaaS template aesthetic
- Same card treatment on every component
- AI slop feature cards

## Stolen Elements:
- From Hyperliquid: three-tier density (large/medium/small text), price flash animations for changing data
- From Grafana: colored left-border on panels matching their chart color, panel headers with icon dots
- From Linear: ambient glow behind focal element, card borders brighten on hover
