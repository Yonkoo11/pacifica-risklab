import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';
import { cascadeData } from './data';

const CHART_WIDTH = 1600;
const CHART_HEIGHT = 600;
const CHART_LEFT = 160;
const CHART_TOP = 300;

export const CascadeScene: React.FC = () => {
  const frame = useCurrentFrame();

  // Total animation: 300 frames (10s at 30fps)
  // Bars reveal progressively
  const progress = Math.min(frame / 280, 1);
  const visibleSteps = Math.floor(progress * cascadeData.length);

  // Find max for scale
  const maxLiq = Math.max(...cascadeData.map((d) => d.liq));
  const maxPrice = Math.max(...cascadeData.map((d) => d.price));
  const minPrice = Math.min(...cascadeData.map((d) => d.price));

  // Current running values
  const currentStep = cascadeData[Math.min(visibleSteps, cascadeData.length - 1)];
  const currentLiq = currentStep?.liq ?? 0;
  const currentPrice = currentStep?.price ?? cascadeData[0].price;

  // Build SVG path for price line up to visibleSteps
  const priceLinePoints = cascadeData
    .slice(0, visibleSteps + 1)
    .map((d, i) => {
      const x = CHART_LEFT + (i / (cascadeData.length - 1)) * CHART_WIDTH;
      const y =
        CHART_TOP +
        CHART_HEIGHT -
        ((d.price - minPrice) / (maxPrice - minPrice)) * CHART_HEIGHT;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <AbsoluteFill
      style={{
        background: '#0a0a1a',
        fontFamily: '-apple-system, system-ui, sans-serif',
      }}
    >
      {/* Brand */}
      <div style={{ position: 'absolute', top: 60, left: 60, fontSize: 32, fontWeight: 700, color: '#f59e0b' }}>
        RiskLab
      </div>

      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: 140,
          left: 160,
          fontSize: 40,
          fontWeight: 700,
          color: '#e0e0e0',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
        }}
      >
        <span
          style={{
            width: 16,
            height: 16,
            borderRadius: '50%',
            background: '#ef4444',
            display: 'inline-block',
            boxShadow: '0 0 20px rgba(239,68,68,0.6)',
          }}
        />
        Liquidation Cascade
      </div>

      {/* Live counters */}
      <div
        style={{
          position: 'absolute',
          top: 200,
          left: 160,
          display: 'flex',
          gap: 64,
          fontSize: 28,
          color: '#888',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        <div>
          Liquidated:{' '}
          <span style={{ color: '#ef4444', fontWeight: 700, fontSize: 36 }}>
            {currentLiq}
          </span>
        </div>
        <div>
          Price:{' '}
          <span style={{ color: '#3b82f6', fontWeight: 700, fontSize: 36 }}>
            ${currentPrice.toLocaleString()}
          </span>
        </div>
      </div>

      {/* SVG chart */}
      <svg
        width={1920}
        height={1080}
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((p, i) => (
          <line
            key={i}
            x1={CHART_LEFT}
            y1={CHART_TOP + p * CHART_HEIGHT}
            x2={CHART_LEFT + CHART_WIDTH}
            y2={CHART_TOP + p * CHART_HEIGHT}
            stroke="rgba(255,255,255,0.05)"
            strokeWidth={1}
          />
        ))}

        {/* Bars */}
        {cascadeData.slice(0, visibleSteps).map((d, i) => {
          const x = CHART_LEFT + (i / (cascadeData.length - 1)) * CHART_WIDTH;
          const barWidth = CHART_WIDTH / cascadeData.length - 2;
          const barHeight = (d.liq / maxLiq) * CHART_HEIGHT;
          const y = CHART_TOP + CHART_HEIGHT - barHeight;

          // Fade in each bar
          const ageInFrames = frame - (i / cascadeData.length) * 280;
          const opacity = Math.min(ageInFrames / 6, 1);

          return (
            <rect
              key={i}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              fill={`rgba(239,68,68,${0.6 * opacity})`}
              stroke={`rgba(239,68,68,${0.9 * opacity})`}
              strokeWidth={1}
              rx={2}
            />
          );
        })}

        {/* Price line */}
        {priceLinePoints && (
          <polyline
            points={priceLinePoints}
            fill="none"
            stroke="#3b82f6"
            strokeWidth={3}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Y-axis labels (left - liquidations) */}
        {[0, 0.5, 1].map((p, i) => (
          <text
            key={i}
            x={CHART_LEFT - 20}
            y={CHART_TOP + (1 - p) * CHART_HEIGHT + 8}
            fill="#ef4444"
            fontSize={20}
            textAnchor="end"
            fontFamily="-apple-system, system-ui, sans-serif"
          >
            {Math.round(p * maxLiq)}
          </text>
        ))}

        {/* Y-axis labels (right - price) */}
        {[0, 0.5, 1].map((p, i) => (
          <text
            key={i}
            x={CHART_LEFT + CHART_WIDTH + 20}
            y={CHART_TOP + (1 - p) * CHART_HEIGHT + 8}
            fill="#3b82f6"
            fontSize={20}
            textAnchor="start"
            fontFamily="-apple-system, system-ui, sans-serif"
          >
            ${Math.round((minPrice + p * (maxPrice - minPrice)) / 1000)}K
          </text>
        ))}
      </svg>
    </AbsoluteFill>
  );
};
