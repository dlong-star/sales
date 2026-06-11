import React from "react";
import { useCurrentFrame } from "remotion";
import { COLORS } from "../config";

/** A single crayon stick. */
export const Crayon: React.FC<{
  color: string;
  rotate?: number;
  length?: number;
  style?: React.CSSProperties;
  /** Gently wiggles, implying it's being drawn with */
  active?: boolean;
}> = ({ color, rotate = 0, length = 120, style, active = false }) => {
  const frame = useCurrentFrame();
  const wiggle = active ? Math.sin(frame * 0.45) * 5 : 0;
  const bob = active ? Math.abs(Math.sin(frame * 0.3)) * -6 : 0;
  const w = length * 0.16;
  return (
    <div
      style={{
        width: w,
        height: length,
        transform: `rotate(${rotate + wiggle}deg) translateY(${bob}px)`,
        position: "relative",
        ...style,
      }}
    >
      {/* Tip */}
      <div
        style={{
          width: 0,
          height: 0,
          borderLeft: `${w / 2}px solid transparent`,
          borderRight: `${w / 2}px solid transparent`,
          borderBottom: `${length * 0.18}px solid ${color}`,
          filter: "brightness(0.88)",
        }}
      />
      {/* Body */}
      <div
        style={{
          width: w,
          height: length * 0.82,
          backgroundColor: color,
          borderRadius: w / 3,
          boxShadow: "0 6px 14px rgba(60,35,15,0.25)",
        }}
      >
        {/* Paper wrapper band */}
        <div
          style={{
            marginTop: length * 0.12,
            height: length * 0.5,
            background: "rgba(255,253,247,0.35)",
            borderTop: "2px solid rgba(255,253,247,0.6)",
            borderBottom: "2px solid rgba(255,253,247,0.6)",
          }}
        />
      </div>
    </div>
  );
};

/** A loose scatter of crayons next to the paper. */
export const CrayonScatter: React.FC<{
  count?: number;
  style?: React.CSSProperties;
}> = ({ count = 4, style }) => {
  const palette = [COLORS.coral, COLORS.amber, COLORS.sage, COLORS.sky, COLORS.coralDeep, "#B48EAD", "#E8C170"];
  const rotations = [82, 95, 74, 100, 88, 70, 105];
  return (
    <div style={{ display: "flex", gap: 4, alignItems: "center", ...style }}>
      {Array.from({ length: count }).map((_, i) => (
        <Crayon
          key={i}
          color={palette[i % palette.length]}
          rotate={rotations[i % rotations.length]}
          length={104 + (i % 3) * 14}
        />
      ))}
    </div>
  );
};
