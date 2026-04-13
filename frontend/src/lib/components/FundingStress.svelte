<script lang="ts">
  import { onMount } from 'svelte';
  import type { FundingStressPoint } from '$lib/api';
  import Chart from 'chart.js/auto';

  let { data }: { data: FundingStressPoint[] } = $props();
  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  function buildChart() {
    if (chart) chart.destroy();
    if (!canvas || data.length === 0) return;

    const labels = data.map((_, i) => i);
    const rates = data.map(d => d.funding_rate * 100); // convert to percentage
    const imbalance = data.map(d => d.imbalance * 100);

    chart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: labels.map(l => `${l}`),
        datasets: [
          {
            label: 'Funding Rate (%)',
            data: rates,
            borderColor: '#a855f7',
            backgroundColor: 'rgba(168, 85, 247, 0.1)',
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            yAxisID: 'y',
          },
          {
            label: 'OI Imbalance (%)',
            data: imbalance,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            borderWidth: 1,
            pointRadius: 0,
            borderDash: [4, 4],
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#999' } },
        },
        scales: {
          x: {
            ticks: { color: '#666', maxTicksLimit: 10 },
            grid: { color: '#1a1a2e' },
          },
          y: {
            position: 'left',
            title: { display: true, text: 'Funding Rate (%)', color: '#999' },
            ticks: { color: '#a855f7' },
            grid: { color: '#1a1a2e' },
          },
          y1: {
            position: 'right',
            title: { display: true, text: 'OI Imbalance (%)', color: '#999' },
            ticks: { color: '#f59e0b' },
            grid: { drawOnChartArea: false },
          },
        },
      },
    });
  }

  onMount(() => buildChart());

  $effect(() => {
    data;
    buildChart();
  });
</script>

<div class="chart-container">
  <h3><span class="dot" style="background:#a855f7"></span>Funding Rate Stress</h3>
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
    position: relative;
    overflow: hidden;
  }
  .chart-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 2px;
    height: 60px;
    background: linear-gradient(to bottom, #a855f7, transparent);
    border-radius: 0 0 1px 1px;
  }
  h3 {
    margin: 0 0 1rem;
    color: #e0e0e0;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }
  .chart-wrapper {
    height: 250px;
  }
</style>
