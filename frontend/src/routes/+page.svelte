<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchMarkets, fetchScenarios, runSimulation, type Market, type Scenario, type SimulationResult } from '$lib/api';
  import ResultsSummary from '$lib/components/ResultsSummary.svelte';
  import CascadeChart from '$lib/components/CascadeChart.svelte';
  import FundingStress from '$lib/components/FundingStress.svelte';

  let markets = $state<Market[]>([]);
  let scenarios = $state<Scenario[]>([]);
  let selectedMarket = $state('BTC');
  let selectedScenario = $state('oct_2025_crash');
  let oiOverride = $state(100_000_000);
  let leverageOverride = $state<number | null>(null);
  let longRatio = $state(0.6);
  let isSimulating = $state(false);
  let result = $state<SimulationResult | null>(null);
  let error = $state('');

  // Compare mode
  let compareMode = $state(false);
  let compareResult = $state<SimulationResult | null>(null);
  let compareLeverage = $state<number | null>(null);
  let compareOi = $state<number | null>(null);

  let currentMarket = $derived(markets.find(m => m.symbol === selectedMarket));

  onMount(async () => {
    try {
      [markets, scenarios] = await Promise.all([fetchMarkets(), fetchScenarios()]);
    } catch (e) {
      error = 'Failed to connect to backend. Is the server running on port 8000?';
    }
  });

  async function simulate() {
    isSimulating = true;
    error = '';
    try {
      result = await runSimulation({
        symbol: selectedMarket,
        scenario: selectedScenario,
        oi_override: oiOverride,
        leverage_override: leverageOverride ?? undefined,
        long_ratio: longRatio,
      });

      // Run comparison if in compare mode
      if (compareMode) {
        compareResult = await runSimulation({
          symbol: selectedMarket,
          scenario: selectedScenario,
          oi_override: compareOi ?? oiOverride,
          leverage_override: compareLeverage ?? leverageOverride ?? undefined,
          long_ratio: longRatio,
        });
      }
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : 'Simulation failed';
    }
    isSimulating = false;
  }

  function formatUsd(n: number): string {
    if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
    if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}K`;
    return `$${n.toFixed(0)}`;
  }

  function severityColor(s: string): string {
    if (s === 'catastrophic') return '#ef4444';
    if (s === 'extreme') return '#f97316';
    if (s === 'moderate') return '#eab308';
    return '#22c55e';
  }
</script>

<svelte:head>
  <title>RiskLab — Pacifica Stress Testing</title>
</svelte:head>

<main>
  <header>
    <div class="brand">
      <h1>RiskLab</h1>
      <span class="subtitle">Perpetual Futures Parameter Stress Testing</span>
    </div>
    <span class="powered"><span class="live-dot"></span>Powered by Pacifica API</span>
  </header>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <div class="layout">
    <!-- Controls Panel -->
    <aside class="controls">
      <section>
        <label>Market</label>
        <select bind:value={selectedMarket}>
          {#each markets as m}
            <option value={m.symbol}>
              {m.symbol} — {m.max_leverage}x — {formatUsd(m.open_interest)} OI
            </option>
          {/each}
        </select>
        {#if currentMarket}
          <div class="market-info">
            <span>Mark: ${currentMarket.mark.toLocaleString()}</span>
            <span>Vol: {formatUsd(currentMarket.volume_24h)}</span>
          </div>
        {/if}
      </section>

      <section>
        <label>Crash Scenario</label>
        {#each scenarios as s}
          <button
            class="scenario-btn"
            class:active={selectedScenario === s.id}
            onclick={() => selectedScenario = s.id}
          >
            <span class="scenario-name">{s.name}</span>
            <span class="scenario-severity" style="color: {severityColor(s.severity)}">
              {s.severity}
            </span>
          </button>
        {/each}
      </section>

      <section>
        <label>
          Hypothetical OI
          <span class="value">{formatUsd(oiOverride)}</span>
        </label>
        <input type="range" min={1000000} max={1000000000} step={1000000}
          bind:value={oiOverride} />
        <div class="range-labels">
          <span>$1M</span><span>$1B</span>
        </div>
      </section>

      <section>
        <label>
          Max Leverage Override
          <span class="value">
            {leverageOverride ? `${leverageOverride}x` : `Default (${currentMarket?.max_leverage ?? '?'}x)`}
          </span>
        </label>
        <input type="range" min={1} max={100} step={1}
          value={leverageOverride ?? currentMarket?.max_leverage ?? 50}
          oninput={(e) => leverageOverride = Number((e.target as HTMLInputElement).value)} />
        <button class="reset-btn" onclick={() => leverageOverride = null}>Reset to default</button>
      </section>

      <section>
        <label>
          Long/Short Ratio
          <span class="value">{Math.round(longRatio * 100)}% / {Math.round((1 - longRatio) * 100)}%</span>
        </label>
        <input type="range" min={0.1} max={0.9} step={0.05} bind:value={longRatio} />
      </section>

      <section>
        <label class="toggle-label">
          <input type="checkbox" bind:checked={compareMode} />
          Compare Mode
        </label>
        {#if compareMode}
          <div class="compare-controls">
            <label>
              Compare Leverage
              <span class="value">{compareLeverage ?? 'Same'}x</span>
            </label>
            <input type="range" min={1} max={100} step={1}
              value={compareLeverage ?? leverageOverride ?? currentMarket?.max_leverage ?? 50}
              oninput={(e) => compareLeverage = Number((e.target as HTMLInputElement).value)} />
          </div>
        {/if}
      </section>

      <button class="run-btn" onclick={simulate} disabled={isSimulating}>
        {isSimulating ? 'Simulating...' : 'Run Stress Test'}
      </button>
    </aside>

    <!-- Results Area -->
    <div class="results">
      {#if isSimulating}
        <div class="loading">
          <div class="spinner"></div>
          <p>Running simulation...</p>
        </div>
      {:else if result}
        <ResultsSummary {result} label={compareMode ? 'Current Parameters' : 'Simulation Results'} />

        {#if compareMode && compareResult}
          <ResultsSummary result={compareResult} label="Proposed Parameters" />
          <div class="compare-diff">
            <h3>Parameter Change Impact</h3>
            <div class="diff-grid">
              <div class="diff-item">
                <span class="diff-label">Liquidations</span>
                <span class="diff-value" class:improved={compareResult.summary.total_liquidated < result.summary.total_liquidated}
                  class:worsened={compareResult.summary.total_liquidated > result.summary.total_liquidated}>
                  {compareResult.summary.total_liquidated - result.summary.total_liquidated > 0 ? '+' : ''}
                  {compareResult.summary.total_liquidated - result.summary.total_liquidated}
                </span>
              </div>
              <div class="diff-item">
                <span class="diff-label">Survival Score</span>
                <span class="diff-value" class:improved={compareResult.summary.survival_score > result.summary.survival_score}
                  class:worsened={compareResult.summary.survival_score < result.summary.survival_score}>
                  {(compareResult.summary.survival_score - result.summary.survival_score) > 0 ? '+' : ''}
                  {(compareResult.summary.survival_score - result.summary.survival_score).toFixed(1)}
                </span>
              </div>
              <div class="diff-item">
                <span class="diff-label">OI Wiped</span>
                <span class="diff-value" class:improved={compareResult.summary.oi_wipe_pct < result.summary.oi_wipe_pct}
                  class:worsened={compareResult.summary.oi_wipe_pct > result.summary.oi_wipe_pct}>
                  {(compareResult.summary.oi_wipe_pct - result.summary.oi_wipe_pct) > 0 ? '+' : ''}
                  {(compareResult.summary.oi_wipe_pct - result.summary.oi_wipe_pct).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        {/if}

        <CascadeChart steps={result.cascade_data} />
        <FundingStress data={result.funding_stress} />

        <div class="limitations">
          <h4>Model Limitations</h4>
          <ul>
            <li>Linear market impact model (real cascades have non-linear dynamics)</li>
            <li>Synthetic position distribution (log-normal leverage, power-law sizes)</li>
            <li>No cross-margin effects between markets</li>
            <li>Funding rate approximation (real funding depends on impact bid/ask)</li>
          </ul>
        </div>
      {:else}
        <div class="empty-state">
          <h2>Select parameters and run a stress test</h2>
          <p>Choose a Pacifica market, pick a historical crash scenario, and see how the current parameters hold up.</p>
          <p class="hint">Tip: Use Compare Mode to evaluate parameter changes side-by-side.</p>
        </div>
      {/if}
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: #0a0a1a;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  }

  :global(body::before) {
    content: '';
    position: fixed;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(245,158,11,0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }

  :global(body::after) {
    content: '';
    position: fixed;
    inset: 0;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 256px 256px;
    pointer-events: none;
    z-index: 0;
  }

  main {
    position: relative;
    z-index: 1;
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #1a1a2e;
  }

  h1 {
    margin: 0;
    font-size: 1.75rem;
    color: #f59e0b;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .subtitle {
    display: block;
    font-size: 0.8rem;
    color: #666;
  }

  .powered {
    font-size: 0.75rem;
    color: #444;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  .live-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
    animation: pulse-dot 2s ease-in-out infinite;
  }

  @keyframes pulse-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(34, 197, 94, 0.4); }
    50% { opacity: 0.5; box-shadow: 0 0 4px rgba(34, 197, 94, 0.2); }
  }

  :global(::selection) {
    background: rgba(245, 158, 11, 0.3);
  }

  :global(::-webkit-scrollbar) {
    width: 6px;
  }
  :global(::-webkit-scrollbar-track) {
    background: #0a0a1a;
  }
  :global(::-webkit-scrollbar-thumb) {
    background: #2a2a4a;
    border-radius: 3px;
  }
  :global(::-webkit-scrollbar-thumb:hover) {
    background: #f59e0b;
  }

  .error {
    background: #2a1515;
    border: 1px solid #ef4444;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    color: #ef4444;
  }

  .layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 2rem;
  }

  .controls {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  section {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-left: 2px solid transparent;
    border-radius: 8px;
    padding: 1rem;
    transition: border-left-color 0.2s ease-out;
  }

  section:focus-within {
    border-left-color: #f59e0b;
  }

  label {
    display: block;
    font-size: 0.8rem;
    color: #999;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .value {
    float: right;
    color: #f59e0b;
    font-weight: 600;
    text-transform: none;
    letter-spacing: 0;
  }

  select {
    width: 100%;
    padding: 0.5rem;
    background: #0f0f1a;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    color: #e0e0e0;
    font-size: 0.85rem;
  }

  .market-info {
    display: flex;
    justify-content: space-between;
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #666;
  }

  .scenario-btn {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0.75rem;
    background: #0f0f1a;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    color: #e0e0e0;
    cursor: pointer;
    margin-bottom: 0.25rem;
    font-size: 0.8rem;
    transition: border-color 0.15s;
  }

  .scenario-btn:hover {
    border-color: rgba(245, 158, 11, 0.4);
  }

  .scenario-btn.active {
    border-color: rgba(245, 158, 11, 0.4);
    border-left: 2px solid #f59e0b;
    background: linear-gradient(90deg, rgba(245,158,11,0.06) 0%, #0f0f1a 100%);
  }

  .scenario-severity {
    font-size: 0.7rem;
    text-transform: uppercase;
    font-weight: 600;
  }

  input[type="range"] {
    width: 100%;
    accent-color: #f59e0b;
  }

  .range-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: #555;
  }

  .reset-btn {
    width: 100%;
    padding: 0.25rem;
    background: transparent;
    border: 1px solid #2a2a4a;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
    font-size: 0.7rem;
    margin-top: 0.25rem;
  }

  .reset-btn:hover {
    color: #999;
    border-color: rgba(245, 158, 11, 0.4);
  }

  .toggle-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .toggle-label input {
    accent-color: #f59e0b;
  }

  .compare-controls {
    margin-top: 0.75rem;
  }

  .run-btn {
    width: 100%;
    padding: 0.85rem;
    background: #f59e0b;
    border: none;
    border-radius: 8px;
    color: #000;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);
    transition: box-shadow 0.15s cubic-bezier(0.23, 1, 0.32, 1), transform 0.1s cubic-bezier(0.23, 1, 0.32, 1);
  }

  .run-btn:hover {
    box-shadow: 0 6px 30px rgba(245, 158, 11, 0.4);
    transform: translateY(-1px);
  }

  .run-btn:active {
    transform: scale(0.97);
  }

  .run-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }

  .results {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
    color: #666;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #2a2a4a;
    border-top-color: #f59e0b;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    background: radial-gradient(ellipse at 50% 30%, rgba(245,158,11,0.04) 0%, #1a1a2e 60%);
    border: 1px solid #2a2a4a;
    border-radius: 12px;
  }

  .empty-state h2 {
    color: #ccc;
    margin: 0 0 0.5rem;
    font-size: 1.25rem;
  }

  .empty-state p {
    color: #666;
    margin: 0.25rem 0;
    max-width: 400px;
  }

  .hint {
    font-style: italic;
    font-size: 0.85rem;
  }

  .compare-diff {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 1.5rem;
  }

  .compare-diff h3 {
    margin: 0 0 1rem;
    color: #e0e0e0;
    font-size: 1rem;
  }

  .diff-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .diff-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.75rem;
    background: #0f0f1a;
    border-radius: 8px;
  }

  .diff-label {
    font-size: 0.75rem;
    color: #888;
  }

  .diff-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #666;
  }

  .diff-value.improved {
    color: #22c55e;
  }

  .diff-value.worsened {
    color: #ef4444;
  }

  .limitations {
    background: #141422;
    border: 1px solid rgba(42,42,74,0.5);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .limitations h4 {
    margin: 0 0 0.5rem;
    color: #888;
    font-size: 0.8rem;
    text-transform: uppercase;
  }

  .limitations ul {
    margin: 0;
    padding-left: 1.25rem;
    font-size: 0.75rem;
    color: #555;
    line-height: 1.6;
  }
</style>
