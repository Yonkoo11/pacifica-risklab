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
        labels: labels.map(l => `${l}`),
        datasets: [
          {
            label: 'Cumulative Liquidations',
            data: liqData,
            backgroundColor: (ctx) => {
              const chart = ctx.chart;
              const { ctx: c, chartArea } = chart;
              if (!chartArea) return 'rgba(239, 68, 68, 0.6)';
              const gradient = c.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
              gradient.addColorStop(0, 'rgba(239, 68, 68, 0.3)');
              gradient.addColorStop(1, 'rgba(239, 68, 68, 0.8)');
              return gradient;
            },
            borderColor: 'rgba(239, 68, 68, 0.9)',
            borderWidth: 1,
            borderRadius: 2,
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
            pointHoverRadius: 4,
            pointHoverBackgroundColor: '#3b82f6',
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 2,
            tension: 0.1,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            labels: {
              color: '#888',
              font: { size: 11, family: '-apple-system, system-ui, sans-serif' },
              padding: 16,
              usePointStyle: true,
              pointStyleWidth: 8,
            },
          },
          tooltip: {
            backgroundColor: 'rgba(15, 15, 26, 0.95)',
            titleColor: '#e0e0e0',
            bodyColor: '#b0b0b8',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            titleFont: { size: 12, weight: '600' },
            bodyFont: { size: 12 },
            callbacks: {
              title: (items: any[]) => `Time Step ${items[0].label}`,
              label: (ctx: any) => {
                if (ctx.datasetIndex === 0) return ` ${ctx.parsed.y.toLocaleString()} liquidated`;
                return ` $${ctx.parsed.y.toLocaleString()}`;
              },
            },
          },
        },
        scales: {
          x: {
            ticks: {
              color: '#555',
              font: { size: 11 },
              maxTicksLimit: 8,
              autoSkip: true,
              maxRotation: 0,
            },
            grid: { color: 'rgba(255,255,255,0.03)', lineWidth: 1 },
            border: { color: 'rgba(255,255,255,0.06)' },
          },
          y: {
            position: 'left',
            title: {
              display: true,
              text: 'Liquidations',
              color: '#666',
              font: { size: 11 },
            },
            ticks: {
              color: '#ef4444',
              font: { size: 11 },
              callback: (v: unknown) => Number(v).toLocaleString(),
            },
            grid: { color: 'rgba(255,255,255,0.03)', lineWidth: 1 },
            border: { display: false },
          },
          y1: {
            position: 'right',
            title: {
              display: true,
              text: 'Price',
              color: '#666',
              font: { size: 11 },
            },
            ticks: {
              color: '#3b82f6',
              font: { size: 11 },
              callback: (v: unknown) => {
                const n = Number(v);
                return n >= 1000 ? `$${(n / 1000).toFixed(0)}K` : `$${n}`;
              },
            },
            grid: { drawOnChartArea: false },
            border: { display: false },
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
  <h3><span class="dot" style="background:#ef4444"></span>Liquidation Cascade</h3>
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
    background: linear-gradient(to bottom, #ef4444, transparent);
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
    height: 300px;
  }
</style>
