import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

export const CompareScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Current params show first, then proposed params slides in
  const currentOpacity = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 180 },
  });

  const proposedOpacity = spring({
    frame: frame - 40,
    fps,
    config: { damping: 12, stiffness: 180 },
  });

  // Diff numbers count in
  const diffStart = 90;
  const liqDiff = interpolate(frame, [diffStart, diffStart + 30], [0, -224], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  const scoreDiff = interpolate(frame, [diffStart, diffStart + 30], [0, 2.2], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  const oiDiff = interpolate(frame, [diffStart, diffStart + 30], [0, -19.8], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });

  const diffOpacity = spring({
    frame: frame - 80,
    fps,
    config: { damping: 12, stiffness: 180 },
  });

  return (
    <AbsoluteFill
      style={{
        background: '#0a0a1a',
        fontFamily: '-apple-system, system-ui, sans-serif',
        padding: 120,
      }}
    >
      <div style={{ position: 'absolute', top: 60, left: 60, fontSize: 32, fontWeight: 700, color: '#f59e0b' }}>
        RiskLab
      </div>

      <div
        style={{
          display: 'flex',
          gap: 40,
          marginTop: 80,
          justifyContent: 'center',
        }}
      >
        {/* Current Parameters */}
        <div
          style={{
            background: '#1a1a2e',
            border: '1px solid #2a2a4a',
            borderRadius: 16,
            padding: 40,
            width: 700,
            opacity: currentOpacity,
            transform: `translateX(${(1 - currentOpacity) * -40}px)`,
          }}
        >
          <div style={{ fontSize: 24, color: '#888', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 32 }}>
            Current — 50x leverage
          </div>
          <div style={{ fontSize: 120, fontWeight: 800, color: '#ef4444', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
            3.9<span style={{ fontSize: 60, color: '#555' }}>/10</span>
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#ef4444', letterSpacing: '0.2em', marginTop: 16 }}>
            CRITICAL
          </div>
          <div style={{ fontSize: 28, color: '#999', marginTop: 32, fontVariantNumeric: 'tabular-nums' }}>
            612 positions liquidated
          </div>
        </div>

        {/* Proposed Parameters */}
        <div
          style={{
            background: '#1a1a2e',
            border: '1px solid #2a2a4a',
            borderRadius: 16,
            padding: 40,
            width: 700,
            opacity: proposedOpacity,
            transform: `translateX(${(1 - proposedOpacity) * 40}px)`,
          }}
        >
          <div style={{ fontSize: 24, color: '#888', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 32 }}>
            Proposed — 20x leverage
          </div>
          <div style={{ fontSize: 120, fontWeight: 800, color: '#eab308', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
            6.1<span style={{ fontSize: 60, color: '#555' }}>/10</span>
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#eab308', letterSpacing: '0.2em', marginTop: 16 }}>
            STABLE
          </div>
          <div style={{ fontSize: 28, color: '#999', marginTop: 32, fontVariantNumeric: 'tabular-nums' }}>
            388 positions liquidated
          </div>
        </div>
      </div>

      {/* Diff section */}
      <div
        style={{
          marginTop: 80,
          padding: 40,
          background: '#1a1a2e',
          border: '1px solid #2a2a4a',
          borderRadius: 16,
          display: 'flex',
          justifyContent: 'space-around',
          opacity: diffOpacity,
        }}
      >
        <DiffStat label="Liquidations" value={Math.round(liqDiff)} />
        <DiffStat label="Survival Score" value={`+${scoreDiff.toFixed(1)}`} positive />
        <DiffStat label="OI Wiped" value={`${oiDiff.toFixed(1)}%`} />
      </div>
    </AbsoluteFill>
  );
};

const DiffStat: React.FC<{ label: string; value: string | number; positive?: boolean }> = ({
  label,
  value,
  positive,
}) => (
  <div style={{ textAlign: 'center' }}>
    <div style={{ fontSize: 22, color: '#888', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{label}</div>
    <div
      style={{
        fontSize: 64,
        fontWeight: 800,
        color: '#22c55e',
        marginTop: 12,
        fontVariantNumeric: 'tabular-nums',
      }}
    >
      {value}
    </div>
  </div>
);
