import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { WarmRoom } from "../components/WarmRoom";
import { PaperSheet } from "../components/PaperSheet";
import { Crayon, CrayonScatter } from "../components/Crayons";
import { COLORS } from "../config";

/**
 * SCENE 1 (0–6s) — "Every kid creates something worth celebrating."
 *
 * PLACEHOLDER VISUAL: a kitchen-table tableau where the family
 * drawing literally draws itself, stroke by stroke, with a crayon
 * wiggling beside it — implying the focused child without showing one.
 *
 * REPLACE WITH AI CLIP: scene-01-child-drawing.mp4
 *   (child at a kitchen table drawing with focus, warm morning light)
 *   → flip clip.enabled in config.ts
 *
 * TWEAK: drawing speed via the [12, 165] frame range below.
 */
export const S1Create: React.FC = () => {
  const frame = useCurrentFrame();

  // The artwork draws itself across almost the whole scene
  const artProgress = interpolate(frame, [12, 165], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });

  // Paper settles into place at the start
  const settle = interpolate(frame, [0, 20], [18, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill>
      <WarmRoom />
      {/* Table tableau */}
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center" }}
      >
        <div
          style={{
            transform: `translateY(${settle - 40}px)`,
            position: "relative",
          }}
        >
          <PaperSheet width={640} artProgress={artProgress} rotate={-2} />
          {/* The "active" crayon, wiggling as if drawing */}
          <div style={{ position: "absolute", right: -64, bottom: 56 }}>
            <Crayon color={COLORS.coral} rotate={36} length={140} active />
          </div>
          {/* Spare crayons scattered to the left */}
          <CrayonScatter
            count={3}
            style={{ position: "absolute", left: -140, bottom: -10 }}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
