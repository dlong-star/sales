import React from "react";
import { AbsoluteFill } from "remotion";

/**
 * Vignette — a constant, subtle darkening of the frame edges.
 * This single layer does a lot of the "cinematic, not PowerPoint"
 * work. Lower the opacity if you want a flatter look.
 */
export const Vignette: React.FC<{ strength?: number }> = ({
  strength = 0.5,
}) => {
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        background:
          "radial-gradient(ellipse 78% 72% at 50% 46%, rgba(0,0,0,0) 58%, rgba(48,28,12,0.34) 100%)",
        opacity: strength,
      }}
    />
  );
};
