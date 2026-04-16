import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Score counts down from 10.0 to 3.9 over 30 frames (1s), then settles
  const score = interpolate(frame, [0, 30], [10.0, 3.9], {
    extrapolateRight: 'clamp',
    easing: (t) => 1 - Math.pow(1 - t, 3), // ease-out cubic
  });

  // Verdict appears at frame 35 with spring
  const verdictOpacity = spring({
    frame: frame - 35,
    fps,
    config: { damping: 12, stiffness: 180 },
  });

  // Verdict shake at frame 40
  const shakeX =
    frame >= 40 && frame <= 60
      ? Math.sin((frame - 40) * 2) * (60 - frame) * 0.5
      : 0;

  const scoreColor = score >= 7 ? '#22c55e' : score >= 4 ? '#eab308' : '#ef4444';
  const glowRgb = score >= 7 ? '34,197,94' : score >= 4 ? '234,179,8' : '239,68,68';

  // Background gradient
  const bgGlow = interpolate(frame, [0, 30], [0.05, 0.25], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 40%, rgba(${glowRgb},${bgGlow}) 0%, #0a0a1a 60%)`,
        fontFamily: '-apple-system, system-ui, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
      }}
    >
      {/* Brand mark top-left */}
      <div
        style={{
          position: 'absolute',
          top: 60,
          left: 60,
          fontSize: 32,
          fontWeight: 700,
          color: '#f59e0b',
          letterSpacing: '-0.02em',
        }}
      >
        RiskLab
      </div>

      {/* Label above score */}
      <div
        style={{
          fontSize: 24,
          color: '#888',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          marginBottom: 32,
          fontWeight: 500,
        }}
      >
        Survival Score
      </div>

      {/* The big number */}
      <div
        style={{
          fontSize: 280,
          fontWeight: 800,
          color: scoreColor,
          letterSpacing: '-0.04em',
          lineHeight: 1,
          fontVariantNumeric: 'tabular-nums',
          textShadow: `0 0 80px rgba(${glowRgb},0.4)`,
          transform: `translateX(${shakeX}px)`,
        }}
      >
        {score.toFixed(1)}
        <span style={{ fontSize: 120, color: '#555', marginLeft: 16 }}>/10</span>
      </div>

      {/* Verdict */}
      <div
        style={{
          fontSize: 72,
          fontWeight: 800,
          color: scoreColor,
          letterSpacing: '0.25em',
          marginTop: 40,
          opacity: verdictOpacity,
          transform: `scale(${0.9 + verdictOpacity * 0.1})`,
        }}
      >
        CRITICAL
      </div>
    </AbsoluteFill>
  );
};
