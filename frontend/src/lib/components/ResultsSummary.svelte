<script lang="ts">
  import type { SimulationResult } from '$lib/api';

  let { result, label = 'Results' }: { result: SimulationResult; label?: string } = $props();

  function scoreColor(score: number): string {
    if (score >= 7) return '#22c55e';
    if (score >= 4) return '#eab308';
    return '#ef4444';
  }

  function scoreRgb(score: number): string {
    if (score >= 7) return '34,197,94';
    if (score >= 4) return '234,179,8';
    return '239,68,68';
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
    <div class="stat stat-hero" style="--score-rgb: {scoreRgb(result.summary.survival_score)}">
      <span class="stat-value hero-value" style="color: {scoreColor(result.summary.survival_score)}">
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
    background: #1e1e2e;
    border: 1px solid #3a3a5a;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 24px rgba(59,130,246,0.08);
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
  .stat-hero {
    grid-column: 1 / -1;
    box-shadow: 0 0 30px rgba(var(--score-rgb), 0.15);
    animation: pulse-glow 3s ease-out infinite;
  }
  .hero-value {
    font-size: 2.5rem;
  }
  @keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 30px rgba(var(--score-rgb), 0.15); }
    50% { box-shadow: 0 0 50px rgba(var(--score-rgb), 0.25); }
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
