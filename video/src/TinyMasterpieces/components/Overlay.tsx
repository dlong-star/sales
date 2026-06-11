import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { COLORS, FONTS } from "../config";

/**
 * Overlay — the emotional headline for each scene.
 * Words rise in one by one with a soft spring (premium kinetic type),
 * then the whole line breathes very slightly so it never feels static.
 *
 * `onClip` — set automatically by SceneFrame when a real video clip
 * is active: switches to warm white text over a dark scrim.
 *
 * To restyle all overlays (size, font, position) edit this file once.
 */
export const Overlay: React.FC<{
  text: string;
  /** Frame (scene-local) at which the overlay starts appearing */
  enterAt?: number;
  onClip?: boolean;
  /** "low" = lower third (default) | "center" = middle of frame */
  position?: "low" | "center";
}> = ({ text, enterAt = 14, onClip = false, position = "low" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");

  const breathe = Math.sin(frame * 0.04) * 3;

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: position === "low" ? 96 : undefined,
        top: position === "center" ? "50%" : undefined,
        transform: position === "center" ? "translateY(-50%)" : undefined,
        display: "flex",
        justifyContent: "center",
        padding: "0 180px",
      }}
    >
      <h1
        style={{
          fontFamily: FONTS.heading,
          fontWeight: 600,
          fontSize: 58,
          lineHeight: 1.28,
          textAlign: "center",
          color: onClip ? "#FFF7EC" : COLORS.ink,
          textShadow: onClip
            ? "0 2px 24px rgba(0,0,0,0.45)"
            : "0 2px 18px rgba(250,245,237,0.8)",
          margin: 0,
          transform: `translateY(${breathe * 0.15}px)`,
        }}
      >
        {words.map((word, i) => {
          const s = spring({
            frame: frame - enterAt - i * 2.2,
            fps,
            config: { damping: 16, stiffness: 90, mass: 0.7 },
          });
          const o = interpolate(frame - enterAt - i * 2.2, [0, 10], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.quad),
          });
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                opacity: o,
                transform: `translateY(${(1 - s) * 26}px)`,
                marginRight: "0.28em",
              }}
            >
              {word}
            </span>
          );
        })}
      </h1>
    </div>
  );
};
