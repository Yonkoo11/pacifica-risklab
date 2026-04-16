# Pacifica Hackathon 2026 — Submission Answers

Submission form answers for copy-paste. Written direct and specific.

Deadline: April 16, 2026 at 16:59
Email on record: alexmustapha11@gmail.com

---

## Project Basics

**Project Name**

```
RiskLab
```

**Track**

```
Analytics & Data
```

**One-Sentence Pitch** *(clear, concise description of what you built)*

```
Self-serve parameter stress testing for Pacifica perps — pick a market, pick a crash, see what breaks.
```

---

## Project Description

**What does your project do? What problem does it solve? Who is it for?** *(150-200 words)*

```
RiskLab is a stress-testing tool for perpetual futures parameters. You pick a Pacifica market, pick a historical crash (October 2025, LUNA, December 2024 flash drop, SVB week, or a synthetic correction), set a hypothetical open interest, and the simulator replays the crash minute by minute against 1,000 synthetic positions.

The problem: Pacifica offers up to 50x leverage across 63 markets, but nobody has tested whether those parameters survive a real crash. Gauntlet charges $1.6M a year to answer this for other protocols. Nothing open source exists. If BTC drops 15% in an hour, how many positions get liquidated? What does funding do? Does the cascade stop on its own?

This is for protocol teams sizing risk, risk analysts writing reports, and active traders choosing leverage before they size in. The Pacifica team can use it to evaluate parameter changes in seconds instead of waiting weeks on a consulting engagement.
```

**Bullet list of core functionality / key features**

```
- Replays 5 historical crashes (Oct 2025, LUNA, Dec 2024 flash, SVB, synthetic 5%) against any of Pacifica's 63 markets
- Pulls live parameters (max leverage, open interest, mark price, funding, orderbook depth) directly from Pacifica's public API
- Cascade liquidation simulator: 1,000 synthetic positions, minute-by-minute price path, linear market impact model calibrated to live orderbook
- Outputs a 0-10 survival score with verdict (RESILIENT / STABLE / FRAGILE / CRITICAL / CATASTROPHIC), positions liquidated, volume wiped, funding stress curve, max drawdown
- Compare mode runs two parameter sets side-by-side (e.g. 50x vs 20x leverage) and shows the diff
- Every simplification — linear impact, synthetic position distribution, no cross-margin effects — is disclosed in the UI, not hidden
```

**What makes this unique?** *(Differentiator vs existing tools or approaches)*

```
No open-source equivalent exists. Gauntlet and Chaos Labs sell this as an enterprise service starting around $1M a year, and their engagements take weeks. RiskLab is self-serve, runs in the browser, and uses only public Pacifica endpoints.

The second differentiator: it's built for Pacifica's actual current state, not its theoretical one. BTC open interest on Pacifica is around $450 right now, so stress-testing against today's live OI tells you nothing useful. RiskLab defaults to hypothetical OI levels between $1M and $1B, because the honest question isn't "what happened last week" — it's "what breaks when you scale to $100M or $500M."
```

---

## Technical Implementation

**How does your project use Pacifica's infrastructure?**

```
Four public API endpoints under api.pacifica.fi/api/v1:

- GET /info — every market's specs (symbol, max_leverage, tick_size, lot_size, min_order_size). Powers the market selector.
- GET /info/prices — live mark, oracle, open interest, and funding rate per market. Shown as the live defaults in the UI and passed into the simulator.
- GET /funding_rate/history — up to 4,000 records of historical funding with bid/ask impact prices. Grounds the funding stress model.
- GET /book — 10-level orderbook depth. Used to calibrate the linear market impact coefficient before the cascade runs.

The entire 63-market dropdown and every live number in the results panel comes from Pacifica on page load. No builder code was needed for a read-only analytics tool, but every parameter that drives the simulation flows directly from Pacifica. Nothing is hardcoded.
```

**Where can we review your code?** *(Repository link)*

```
https://github.com/Yonkoo11/pacifica-risklab
```

**What is the current deployment status of your project?**

```
Local/Demo Only
```

**Is there a live app, dashboard, or UI we can access?** *(If yes, enter link)*

```
Not deployed publicly — the README has one-command run instructions (python3 -m uvicorn main:app for the backend, npm run dev for the frontend). The demo video shows the full app running against Pacifica's live API.
```

---

## Impact & Continuation

**Who did you have in mind when this product was built?** *(Traders, quants, protocols, retail users, etc.)*

```
Primarily protocol teams and risk analysts — the Pacifica team themselves, risk consultants evaluating a deployment, anyone who has to answer "is this parameter change safe." Secondarily quants and active traders sizing positions who want to know what their leverage actually costs them in a crash. Not retail users — the tool assumes you understand maintenance margin, funding rates, and OI imbalance.
```

**Why would users adopt this in production?**

```
It answers a question that currently costs $1.6M a year to answer commercially. Running a cascade simulation manually takes hours of Python and a lot of assumptions. RiskLab does it in three seconds in a browser tab.

For the Pacifica team: every time someone proposes "add this market" or "raise BTC leverage to 75x," this gives a concrete answer with real historical data behind it. For risk analysts: it produces the same kind of outputs Gauntlet reports show, without the consulting engagement. For traders: you see what happens to your position at different leverage before you commit capital.
```

**If you had more time, what would you build or improve next?**

```
Three things, in order:

1. Multi-market correlation — crash BTC and ETH together, not just one at a time. Real crashes are correlated; single-market simulations underestimate cascade severity because they miss cross-asset contagion.

2. Insurance fund depletion modeling — Pacifica's API doesn't expose insurance fund state yet. Once it does, the simulator can answer the real question: "does the insurance fund cover these liquidation losses, or does it get wiped out and socialize to traders?"

3. Live parameter drift alerts — continuously compare live open interest and leverage against the last stress-test result. If parameters drift into a zone the simulator flagged as unsafe, notify the team automatically.
```

**Are you interested in continuing as a long-term Pacifica ecosystem builder?**

```
Yes
```

---

## Final Confirmation (check every box)

- [x] This project was built during the hackathon
- [x] The submitted repository is complete and accessible
- [x] A demo video has been provided
- [x] The project uses Pacifica infrastructure
- [x] This submission complies with the hackathon rules and code of conduct
- [x] Yes, I confirm this is original work and does not infringe on third-party rights

---

## Pre-Submission Checklist

- [ ] Upload `video/risklab-demo-final.mp4` to YouTube (unlisted) and note the URL
- [ ] Verify repo is publicly accessible at https://github.com/Yonkoo11/pacifica-risklab
- [ ] Confirm email on form matches: alexmustapha11@gmail.com
- [ ] Also submit on DoraHacks if that's the alternate submission platform

---

## Asset Links (for the submission)

- **Repo:** https://github.com/Yonkoo11/pacifica-risklab
- **Demo video file:** `~/Projects/pacifica-risklab/video/risklab-demo-final.mp4` (3.6 min, 25MB)
- **README:** https://github.com/Yonkoo11/pacifica-risklab/blob/main/README.md
