import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLORS } from "../config";

/**
 * WarmRoom — the soft, cinematic "home" background used behind
 * table-top scenes. Pure gradients (no filters) so it renders fast:
 *   - warm window light from the upper left
 *   - a darker table band at the bottom
 *   - slowly drifting bokeh orbs (out-of-focus morning light)
 *
 * Props:
 *   brightness  0..1 — scene 8 uses a higher value than scene 1
 *                      to show the world literally getting brighter.
 */
export const WarmRoom: React.FC<{ brightness?: number }> = ({
  brightness = 0,
}) => {
  const frame = useCurrentFrame();

  // Bokeh orbs: position, size, color, drift speed. Soft edges are
  // baked into the radial-gradient so no expensive blur filter is needed.
  const orbs = [
    { x: 14, y: 22, r: 260, c: "242,169,59", s: 0.013, o: 0.20 },
    { x: 78, y: 14, r: 210, c: "232,121,90", s: 0.017, o: 0.13 },
    { x: 88, y: 55, r: 300, c: "243,197,178", s: 0.011, o: 0.16 },
    { x: 30, y: 60, r: 180, c: "242,169,59", s: 0.021, o: 0.11 },
    { x: 58, y: 30, r: 150, c: "255,236,200", s: 0.015, o: 0.18 },
  ];

  return (
    <AbsoluteFill>
      {/* Base wall: warm cream, brighter when `brightness` is raised */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(160deg, #FDF8EF 0%, ${COLORS.cream} 45%, #EFE1CC 100%)`,
        }}
      />
      {/* Morning window light from upper-left */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 90% 80% at 18% 8%, rgba(255,241,214,0.95) 0%, rgba(255,241,214,0) 60%)",
          opacity: 0.7 + brightness * 0.3,
        }}
      />
      {/* Drifting bokeh */}
      {orbs.map((b, i) => {
        const dx = Math.sin(frame * b.s + i * 1.7) * 28;
        const dy = Math.cos(frame * b.s * 0.8 + i * 2.3) * 18;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `calc(${b.x}% - ${b.r}px)`,
              top: `calc(${b.y}% - ${b.r}px)`,
              width: b.r * 2,
              height: b.r * 2,
              transform: `translate(${dx}px, ${dy}px)`,
              background: `radial-gradient(circle, rgba(${b.c},${
                b.o + brightness * 0.06
              }) 0%, rgba(${b.c},0) 65%)`,
            }}
          />
        );
      })}
      {/* Wooden table band along the bottom of frame */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: "34%",
          background:
            "linear-gradient(180deg, #D9B98F 0%, #C9A578 35%, #B08A5E 100%)",
        }}
      />
      {/* Soft light reflection on the table */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: "34%",
          background:
            "radial-gradient(ellipse 70% 100% at 35% 0%, rgba(255,243,219,0.55) 0%, rgba(255,243,219,0) 70%)",
          opacity: 0.8 + brightness * 0.2,
        }}
      />
      {/* Very slow ambient light shift to keep the frame alive */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(115deg, rgba(255,228,180,0.18) 0%, rgba(255,228,180,0) 45%)",
          opacity: interpolate(Math.sin(frame * 0.02), [-1, 1], [0.4, 1]),
        }}
      />
    </AbsoluteFill>
  );
};
