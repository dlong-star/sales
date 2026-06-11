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

/**
 * SCENE 2 (6–12s) — "But sometimes those little moments disappear
 * too fast."
 *
 * PLACEHOLDER VISUAL: the finished drawing is lifted up proudly
 * ("look what I made!") and glows in a moment of validation — then
 * ghost copies drift apart and fade, the moment slipping away.
 *
 * REPLACE WITH AI CLIP: scene-02-proud-moment.mp4
 *   (child proudly showing artwork to a smiling parent)
 *
 * TWEAK: the fade-away timing in DRIFT_START below.
 */
const DRIFT_START = 95; // frame at which the moment starts to "disappear"

export const S2Moment: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Beat 1 — the proud lift toward camera
  const lift = spring({
    frame: frame - 6,
    fps,
    config: { damping: 15, stiffness: 70, mass: 0.9 },
  });

  // Warm glow of validation behind the artwork
  const glow = interpolate(frame, [25, 55, DRIFT_START, 160], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Beat 2 — the moment slips away
  const slip = interpolate(frame, [DRIFT_START, 172], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  // Ghost copies that drift outward and dissolve
  const ghosts = [
    { x: -340, y: -60, r: -14 },
    { x: 360, y: -90, r: 12 },
    { x: -160, y: -180, r: 7 },
  ];

  return (
    <AbsoluteFill>
      <WarmRoom />
      {/* Validation glow */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle 560px at 50% 46%, rgba(255,224,166,0.55) 0%, rgba(255,224,166,0) 70%)",
          opacity: glow,
        }}
      />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {/* Ghost copies — the disappearing moments */}
        {ghosts.map((g, i) => {
          const t = interpolate(slip, [0.1 + i * 0.12, 0.85 + i * 0.05], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                opacity: t === 0 ? 0 : (1 - t) * 0.45,
                transform: `translate(${g.x * t}px, ${g.y * t - 30}px) rotate(${
                  g.r * t
                }deg) scale(${0.92 - t * 0.25})`,
              }}
            >
              <PaperSheet width={560} signed={false} />
            </div>
          );
        })}

        {/* The hero artwork */}
        <div
          style={{
            transform: `
              translateY(${interpolate(lift, [0, 1], [120, -30]) + slip * 60}px)
              scale(${interpolate(lift, [0, 1], [0.86, 1.04]) - slip * 0.12})
              rotate(${-2 + lift * 3 - slip * 4}deg)`,
            opacity: 1 - slip * 0.55,
          }}
        >
          <PaperSheet width={640} rotate={0} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
