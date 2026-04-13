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
    const rates = data.map(d => d.funding_rate * 100);
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
            backgroundColor: (ctx) => {
              const chart = ctx.chart;
              const { ctx: c, chartArea } = chart;
              if (!chartArea) return 'rgba(168, 85, 247, 0.1)';
              const gradient = c.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
              gradient.addColorStop(0, 'rgba(168, 85, 247, 0)');
              gradient.addColorStop(1, 'rgba(168, 85, 247, 0.15)');
              return gradient;
            },
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
            pointHoverBackgroundColor: '#a855f7',
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 2,
            fill: true,
            tension: 0.2,
            yAxisID: 'y',
          },
          {
            label: 'OI Imbalance (%)',
            data: imbalance,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 3,
            pointHoverBackgroundColor: '#f59e0b',
            borderDash: [4, 4],
            tension: 0.2,
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
              title: (items: any[]) => `Hour ${items[0].label}`,
              label: (ctx: any) => {
                if (ctx.datasetIndex === 0) return ` Funding: ${ctx.parsed.y.toFixed(3)}%`;
                return ` Imbalance: ${ctx.parsed.y.toFixed(1)}%`;
              },
            },
          },
        },
        scales: {
          x: {
            ticks: {
              color: '#555',
              font: { size: 11 },
              maxTicksLimit: 10,
            },
            grid: { color: 'rgba(255,255,255,0.03)', lineWidth: 1 },
            border: { color: 'rgba(255,255,255,0.06)' },
          },
          y: {
            position: 'left',
            title: {
              display: true,
              text: 'Funding Rate (%)',
              color: '#666',
              font: { size: 11 },
            },
            ticks: {
              color: '#a855f7',
              font: { size: 11 },
              callback: (v: unknown) => `${Number(v).toFixed(2)}%`,
            },
            grid: { color: 'rgba(255,255,255,0.03)', lineWidth: 1 },
            border: { display: false },
          },
          y1: {
            position: 'right',
            title: {
              display: true,
              text: 'OI Imbalance (%)',
              color: '#666',
              font: { size: 11 },
            },
            ticks: {
              color: '#f59e0b',
              font: { size: 11 },
              callback: (v: unknown) => `${Number(v).toFixed(0)}%`,
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
