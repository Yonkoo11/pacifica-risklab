# RiskLab Demo — Voiceover Clips (v5 - Pacifica-compliant structure)

Target: 4-5 minutes
Structure enforced by Pacifica submission rules

---

## Section 1: Problem & Idea (30-45s)

### Clip 01 — Hook (3s) [Remotion: Hook]
**Audio:** "Three point nine out of ten. Critical."

### Clip 02 — Problem setup (10s) [Live: market selector]
**Audio:** "Pacifica offers up to 50x leverage across 63 perpetuals markets. Active traders put real capital behind those settings every day."

### Clip 03 — The gap (12s) [Live: scenario selector with badges]
**Audio:** "But nobody has tested what those parameters do in a real crash. When Bitcoin dropped 15 percent in an hour last October, would Pacifica's current setup survive? Nobody knows."

### Clip 04 — Who this is for (10s) [Live: full app view]
**Audio:** "This matters for anyone running a perp market. Protocol teams, risk analysts, traders sizing positions. Gauntlet charges one point six million a year to answer it. There's nothing else."

---

## Section 2: Solution Overview (30-45s)

### Clip 05 — Introducing RiskLab (12s) [Live: empty state flow diagram]
**Audio:** "So we built RiskLab. Self-serve parameter stress testing. You pick a Pacifica market, pick a historical crash, set your hypothetical open interest, and see exactly what breaks."

### Clip 06 — How it fits (10s) [Live: market+scenario selected]
**Audio:** "It runs entirely on Pacifica's public API. No auth, no wallet needed. This is the Analytics and Data track, built to help Pacifica scale safely."

---

## Section 3: Live Product Walkthrough (2-3 min)

### Clip 07 — Market selection (10s) [Live: BTC dropdown open]
**Audio:** "We start with a market. Every Pacifica perpetual is listed with its live leverage and open interest. Let's pick BTC at 50x."

### Clip 08 — Scenario selection (12s) [Live: scenario list, selecting Oct 2025]
**Audio:** "Five historical crash scenarios, pulled from Binance candle data. October 2025, the LUNA collapse, December 2024 flash drop, SVB week, and a synthetic five percent correction."

### Clip 09 — Parameters (10s) [Live: sliders being adjusted]
**Audio:** "Three sliders. Hypothetical open interest from one million to one billion. Leverage override if you want to test a proposal. And the long short ratio."

### Clip 10 — Run + hero (8s) [Remotion: Hook animation]
**Audio:** "Hit run. The simulation takes about three seconds. Three point nine out of ten. Critical."

### Clip 11 — The stats (10s) [Live: full results with stats visible]
**Audio:** "612 positions liquidated. Fifty six million dollars of volume wiped. Fifty six percent of open interest gone. Two cascade rounds."

### Clip 12 — Cascade explanation (14s) [Remotion: Cascade animation]
**Audio:** "Here's the cascade. A thousand synthetic positions get stress-tested minute by minute. Each liquidation pushes the price down, which triggers the next wave. You can watch it accelerate at step 88."

### Clip 13 — Funding stress (10s) [Live: funding chart scroll]
**Audio:** "Funding flips negative as open interest skews short. You can see exactly when the stress hits its cap."

### Clip 14 — Compare mode (16s) [Remotion: Compare animation]
**Audio:** "Compare mode is where this gets useful. Drop the leverage from 50x to 20x and rerun. 224 fewer liquidations. 19 percent less open interest wiped. The score jumps from critical to stable."

### Clip 15 — Limitations honesty (10s) [Live: limitations section]
**Audio:** "The model is documented. Linear market impact, synthetic position distribution, no cross-margin. Every simplification is disclosed."

---

## Section 4: Pacifica Integration (30-60s)

### Clip 16 — API calls (14s) [Terminal: curl /info and /info/prices]
**Audio:** "Everything you see comes from Pacifica's public API. The market list, max leverage, live open interest, and mark price all pull from info and info prices."

### Clip 17 — Funding + orderbook (14s) [Terminal: funding_rate/history and /book]
**Audio:** "Funding rate history powers the stress chart. The orderbook endpoint feeds the market impact model. Four endpoints, zero authentication."

### Clip 18 — Builder angle (10s) [Live: market info card]
**Audio:** "No builder code was needed for a read-only analytics tool. But every parameter surfaced here flows directly from Pacifica. Nothing is hardcoded."

---

## Section 5: Value & Impact (20-40s)

### Clip 19 — Who uses this (12s) [Live: BTC view with low live OI noted]
**Audio:** "Pacifica's BTC open interest is currently around 450 dollars. The platform is young. RiskLab is forward-looking. What happens when you scale to 100 million? 500 million?"

### Clip 20 — Why now (12s) [Live: compare showing dramatic difference]
**Audio:** "Pacifica grows by getting the parameters right before it's too late. This tool lets the team test changes in seconds, not days."

---

## Section 6: What's Next (20-30s)

### Clip 21 — Roadmap (14s) [Live: full app clean shot]
**Audio:** "With more time, multi-market correlation for cross-asset crashes. Insurance fund depletion modeling. And real-time alerts when live parameters drift into danger zones."

### Clip 22 — Close (6s) [Remotion: Hook end state or clean RiskLab brand]
**Audio:** "RiskLab. Built on Pacifica."
