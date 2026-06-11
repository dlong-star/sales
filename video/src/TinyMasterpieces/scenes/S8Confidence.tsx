import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { WarmRoom } from "../components/WarmRoom";
import { PaperSheet } from "../components/PaperSheet";
import { Crayon, CrayonScatter } from "../components/Crayons";
import { COLORS } from "../config";

/**
 * SCENE 8 (52–57s) — "Because confidence grows when kids feel seen."
 *
 * PLACEHOLDER VISUAL: a deliberate callback to Scene 1 — same table,
 * but brighter light, more crayons, and a bolder rainbow piece drawn
 * faster and prouder. Sparkles celebrate the strokes.
 *
 * REPLACE WITH AI CLIP: scene-08-confidence.mp4
 *   (the child drawing again, beaming, more confident)
 */
const Sparkle: React.FC<{ x: number; y: number; at: number; size?: number }> = ({
  x,
  y,
  at,
  size = 34,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({
    frame: frame - at,
    fps,
    config: { damping: 8, stiffness: 140 },
  });
  const fade = interpolate(frame - at, [12, 40], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      style={{
        position: "absolute",
        transform: `translate(${x}px, ${y}px) scale(${Math.max(pop, 0)}) rotate(${
          (frame - at) * 3
        }deg)`,
        opacity: Math.max(pop, 0) * fade,
      }}
    >
      <path
        d="M12 2 L14 9 L21 12 L14 15 L12 22 L10 15 L3 12 L10 9 Z"
        fill={COLORS.amber}
      />
    </svg>
  );
};

export const S8Confidence: React.FC = () => {
  const frame = useCurrentFrame();

  // The rainbow draws noticeably faster than scene 1 — confidence.
  const artProgress = interpolate(frame, [6, 116], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });

  const settle = interpolate(frame, [0, 16], [22, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill>
      {/* Brighter than scene 1 — the world has opened up */}
      <WarmRoom brightness={1} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ transform: `translateY(${settle - 40}px)`, position: "relative" }}>
          <PaperSheet width={640} artProgress={artProgress} variant="rainbow" rotate={1.5} />
          <div style={{ position: "absolute", right: -60, bottom: 60 }}>
            <Crayon color={COLORS.sky} rotate={34} length={140} active />
          </div>
          {/* A bigger crayon collection now */}
          <CrayonScatter count={6} style={{ position: "absolute", left: -210, bottom: -12 }} />
          {/* Celebration sparkles as strokes land */}
          <Sparkle x={-60} y={-40} at={40} />
          <Sparkle x={620} y={-60} at={68} size={28} />
          <Sparkle x={560} y={300} at={96} />
          <Sparkle x={-40} y={330} at={118} size={26} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
