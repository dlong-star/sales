import React from "react";
import { interpolate, Easing } from "remotion";
import { COLORS } from "../config";

/**
 * KidArt — the recurring hand-drawn crayon artwork that carries the
 * story: drawn on paper (scene 1), uploaded to the app (scene 3),
 * printed on the postcard (scene 5), pinned to grandma's fridge
 * (scene 6), redrawn with more confidence (scene 8).
 *
 * Two variants:
 *   "familySun" — sun + cloud + parent & child holding hands + heart
 *   "rainbow"   — a bolder rainbow piece for the confidence scene
 *
 * `progress` (0..1) draws the strokes in sequence, like a child
 * actually drawing. Pass progress={1} for the finished piece.
 *
 * To use a REAL kid's drawing instead, see ARTWORK_IMAGE in config.ts.
 */

type Stroke = {
  d: string;
  color: string;
  width: number;
  /** Portion of overall progress in which this stroke draws: [from, to] */
  win: [number, number];
  fill?: string;
  /** "pop" elements scale in instead of stroke-drawing */
  pop?: boolean;
};

const wobblyCircle = (cx: number, cy: number, r: number) =>
  // Slightly irregular circle, like a hand-drawn one
  `M ${cx + r} ${cy}
   C ${cx + r} ${cy + r * 0.58}, ${cx + r * 0.52} ${cy + r * 1.04}, ${cx} ${cy + r}
   C ${cx - r * 0.6} ${cy + r * 0.96}, ${cx - r * 1.04} ${cy + r * 0.5}, ${cx - r} ${cy}
   C ${cx - r * 0.98} ${cy - r * 0.62}, ${cx - r * 0.5} ${cy - r}, ${cx} ${cy - r * 1.02}
   C ${cx + r * 0.56} ${cy - r * 0.98}, ${cx + r * 1.02} ${cy - r * 0.55}, ${cx + r} ${cy}`;

const sunRays = (cx: number, cy: number, r1: number, r2: number): string => {
  let d = "";
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2 + 0.32;
    const jit = 1 + (i % 3) * 0.06;
    d += `M ${cx + Math.cos(a) * r1} ${cy + Math.sin(a) * r1} L ${
      cx + Math.cos(a) * r2 * jit
    } ${cy + Math.sin(a) * r2 * jit} `;
  }
  return d;
};

const grassLine = (y: number, from: number, to: number): string => {
  let d = `M ${from} ${y}`;
  for (let x = from; x < to; x += 42) {
    d += ` q 21 -16 42 ${(x / 42) % 2 === 0 ? 1 : -2}`;
  }
  return d;
};

const FAMILY_SUN: Stroke[] = [
  // Sun
  { d: wobblyCircle(82, 76, 34), color: COLORS.amber, width: 8, win: [0.0, 0.13] },
  { d: sunRays(82, 76, 46, 64), color: COLORS.amber, width: 7, win: [0.11, 0.26] },
  // Cloud (three overlapping bumps)
  { d: wobblyCircle(292, 76, 17), color: COLORS.sky, width: 6, win: [0.22, 0.3] },
  { d: wobblyCircle(322, 68, 21), color: COLORS.sky, width: 6, win: [0.26, 0.34] },
  { d: wobblyCircle(352, 78, 16), color: COLORS.sky, width: 6, win: [0.3, 0.38] },
  // Grass
  { d: grassLine(292, 18, 402), color: COLORS.sage, width: 7, win: [0.34, 0.46] },
  // Parent figure
  { d: wobblyCircle(196, 168, 23), color: COLORS.coral, width: 7, win: [0.44, 0.52] },
  {
    d: "M 196 191 L 197 250 M 196 208 L 168 232 M 197 208 L 226 230 M 197 250 L 180 290 M 197 250 L 214 290",
    color: COLORS.coral,
    width: 7,
    win: [0.5, 0.64],
  },
  // Child figure (smaller, reaching for parent's hand)
  { d: wobblyCircle(278, 198, 16), color: COLORS.coralDeep, width: 6, win: [0.6, 0.68] },
  {
    d: "M 278 214 L 278 254 M 278 224 L 254 234 M 278 224 L 298 240 M 278 254 L 266 290 M 278 254 L 290 290",
    color: COLORS.coralDeep,
    width: 6,
    win: [0.66, 0.78],
  },
  // Faces: eyes + smiles (the charming finishing touch)
  {
    d: "M 188 164 a 1.6 1.6 0 1 0 0.1 0 M 204 164 a 1.6 1.6 0 1 0 0.1 0 M 187 174 q 9 9 18 0",
    color: "#7C4A35",
    width: 4.5,
    win: [0.78, 0.88],
  },
  {
    d: "M 272 195 a 1.4 1.4 0 1 0 0.1 0 M 284 195 a 1.4 1.4 0 1 0 0.1 0 M 271 202 q 7 7 14 0",
    color: "#7C4A35",
    width: 4,
    win: [0.82, 0.92],
  },
  // Heart between them — pops in last
  {
    d: "M 238 142 c -9 -15 -31 -6 -22 9 c 5 9 22 18 22 18 c 0 0 17 -9 22 -18 c 9 -15 -13 -24 -22 -9 Z",
    color: COLORS.coral,
    width: 5,
    fill: COLORS.coral,
    win: [0.9, 1.0],
    pop: true,
  },
];

const RAINBOW: Stroke[] = [
  // Four bold arcs
  { d: "M 62 286 A 148 148 0 0 1 358 286", color: COLORS.coral, width: 11, win: [0.0, 0.16] },
  { d: "M 86 286 A 124 124 0 0 1 334 286", color: COLORS.amber, width: 11, win: [0.12, 0.28] },
  { d: "M 110 286 A 100 100 0 0 1 310 286", color: COLORS.sage, width: 11, win: [0.24, 0.4] },
  { d: "M 134 286 A 76 76 0 0 1 286 286", color: COLORS.sky, width: 11, win: [0.36, 0.52] },
  // Sun peeking from the corner
  { d: wobblyCircle(58, 64, 30), color: COLORS.amber, width: 8, win: [0.5, 0.62] },
  { d: sunRays(58, 64, 40, 56), color: COLORS.amber, width: 6, win: [0.58, 0.7] },
  // Little birds
  { d: "M 312 92 q 9 -10 18 0 q 9 -10 18 0", color: "#7C4A35", width: 5, win: [0.68, 0.78] },
  { d: "M 268 124 q 7 -8 14 0 q 7 -8 14 0", color: "#7C4A35", width: 4.5, win: [0.72, 0.82] },
  // Flowers along the bottom
  { d: "M 96 286 L 96 308", color: COLORS.sage, width: 6, win: [0.78, 0.84] },
  { d: wobblyCircle(96, 278, 9), color: COLORS.coral, width: 5, fill: COLORS.blush, win: [0.82, 0.9], pop: true },
  { d: "M 326 286 L 326 308", color: COLORS.sage, width: 6, win: [0.82, 0.88] },
  { d: wobblyCircle(326, 278, 9), color: COLORS.amber, width: 5, fill: "#FBDFA8", win: [0.86, 0.94], pop: true },
  // Big proud heart in the middle of the rainbow
  {
    d: "M 210 232 c -11 -18 -37 -7 -26 11 c 6 11 26 21 26 21 c 0 0 20 -10 26 -21 c 11 -18 -15 -29 -26 -11 Z",
    color: COLORS.coral,
    width: 5,
    fill: COLORS.coral,
    win: [0.92, 1.0],
    pop: true,
  },
];

export const KidArt: React.FC<{
  variant?: "familySun" | "rainbow";
  progress?: number;
  style?: React.CSSProperties;
}> = ({ variant = "familySun", progress = 1, style }) => {
  const strokes = variant === "familySun" ? FAMILY_SUN : RAINBOW;
  return (
    <svg viewBox="0 0 420 320" style={{ width: "100%", height: "100%", ...style }}>
      {strokes.map((s, i) => {
        const local = interpolate(progress, s.win, [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        if (s.pop) {
          const scale = interpolate(local, [0, 1], [0, 1], {
            easing: Easing.out(Easing.back(2.2)),
          });
          return (
            <path
              key={i}
              d={s.d}
              stroke={s.color}
              strokeWidth={s.width}
              fill={s.fill ?? "none"}
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity={local === 0 ? 0 : 0.92}
              style={{
                transform: `scale(${scale})`,
                transformOrigin: "center",
                transformBox: "fill-box",
              }}
            />
          );
        }
        return (
          <path
            key={i}
            d={s.d}
            stroke={s.color}
            strokeWidth={s.width}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity={0.92}
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - local}
          />
        );
      })}
    </svg>
  );
};
