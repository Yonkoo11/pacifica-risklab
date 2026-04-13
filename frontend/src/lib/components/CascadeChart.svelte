<script lang="ts">
  import { onMount } from 'svelte';
  import type { CascadeStep } from '$lib/api';
  import Chart from 'chart.js/auto';

  let { steps }: { steps: CascadeStep[] } = $props();
  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  function buildChart() {
    if (chart) chart.destroy();
    if (!canvas || steps.length === 0) return;

    // Aggregate by time_step: cumulative liquidations and price
    const byStep = new Map<number, { cumLiq: number; price: number; cumVol: number }>();
    let cumLiq = 0;
    let cumVol = 0;
    for (const s of steps) {
      cumLiq += s.liquidated_count;
      cumVol += s.liquidated_volume_usd;
      byStep.set(s.time_step, { cumLiq, price: s.price_after, cumVol });
    }

    const labels = Array.from(byStep.keys());
    const liqData = labels.map(k => byStep.get(k)!.cumLiq);
    const priceData = labels.map(k => byStep.get(k)!.price);

    chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels.map(l => `Step ${l}`),
        datasets: [
          {
            label: 'Cumulative Liquidations',
            data: liqData,
            backgroundColor: 'rgba(239, 68, 68, 0.7)',
            borderColor: 'rgba(239, 68, 68, 1)',
            borderWidth: 1,
            yAxisID: 'y',
          },
          {
            label: 'Price',
            data: priceData,
            type: 'line',
            borderColor: '#3b82f6',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#999' },
          },
        },
        scales: {
          x: {
            ticks: { color: '#666', maxTicksLimit: 10 },
            grid: { color: '#1a1a2e' },
          },
          y: {
            position: 'left',
            title: { display: true, text: 'Cumulative Liquidations', color: '#999' },
            ticks: { color: '#ef4444' },
            grid: { color: '#1a1a2e' },
          },
          y1: {
            position: 'right',
            title: { display: true, text: 'Price ($)', color: '#999' },
            ticks: {
              color: '#3b82f6',
              callback: (v: unknown) => `$${Number(v).toLocaleString()}`,
            },
            grid: { drawOnChartArea: false },
          },
        },
      },
    });
  }

  onMount(() => buildChart());

  $effect(() => {
    steps;
    buildChart();
  });
</script>

<div class="chart-container">
  <h3>Liquidation Cascade</h3>
  <div class="chart-wrapper">
    <canvas bind:this={canvas}></canvas>
  </div>
</div>

<style>
  .chart-container {
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
  .chart-wrapper {
    height: 300px;
  }
</style>
