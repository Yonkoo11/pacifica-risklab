<script lang="ts">
  import type { SimulationResult } from '$lib/api';

  let { result, label = 'Results' }: { result: SimulationResult; label?: string } = $props();

  function scoreColor(score: number): string {
    if (score >= 7) return '#22c55e';
    if (score >= 4) return '#eab308';
    return '#ef4444';
  }

  function formatUsd(n: number): string {
    if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(1)}B`;
    if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
    return `$${n.toFixed(0)}`;
  }
</script>

<div class="summary">
  <h3>{label}</h3>
  <div class="stats-grid">
    <div class="stat">
      <span class="stat-value" style="color: {scoreColor(result.summary.survival_score)}">
        {result.summary.survival_score}/10
      </span>
      <span class="stat-label">Survival Score</span>
    </div>
    <div class="stat">
      <span class="stat-value">{result.summary.total_liquidated}</span>
      <span class="stat-label">Positions Liquidated</span>
    </div>
    <div class="stat">
      <span class="stat-value">{formatUsd(result.summary.total_liquidated_volume_usd)}</span>
      <span class="stat-label">Volume Liquidated</span>
    </div>
    <div class="stat">
      <span class="stat-value">{result.summary.oi_wipe_pct}%</span>
      <span class="stat-label">OI Wiped</span>
    </div>
    <div class="stat">
      <span class="stat-value">{result.summary.cascade_rounds}</span>
      <span class="stat-label">Cascade Rounds</span>
    </div>
    <div class="stat">
      <span class="stat-value">-{result.summary.max_drawdown_pct.toFixed(1)}%</span>
      <span class="stat-label">Max Drawdown</span>
    </div>
  </div>

  {#if result.parameters.oi_is_hypothetical}
    <p class="note">
      Hypothetical scenario at {formatUsd(result.parameters.simulated_oi as number)} OI.
      Live OI: {formatUsd(result.parameters.live_oi as number)}.
    </p>
  {/if}
</div>

<style>
  .summary {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 1.5rem;
  }
  h3 {
    margin: 0 0 1rem;
    color: #e0e0e0;
    font-size: 1rem;
  }
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.75rem;
    background: #0f0f1a;
    border-radius: 8px;
  }
  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
  }
  .stat-label {
    font-size: 0.75rem;
    color: #888;
    margin-top: 0.25rem;
    text-align: center;
  }
  .note {
    margin: 1rem 0 0;
    font-size: 0.75rem;
    color: #666;
    font-style: italic;
  }
</style>
