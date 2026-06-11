import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BRAND, COLORS, FONTS } from "../config";

/**
 * SCENE 4 (20–28s) — "Safe for kids. Simple for parents."
 *
 * PLACEHOLDER VISUAL: the parent dashboard. A shield draws itself,
 * then trust features tick in one by one: approved family list,
 * no DMs / no strangers, and message approval — with toggles
 * already ON. Calm, clean, modern UI = trust.
 *
 * REPLACE WITH AI CLIP: scene-04-parent-dashboard.mp4
 *
 * TWEAK: feature copy in the ROWS array; stagger speed in rowDelay.
 */
const ROWS = [
  {
    title: "Approved family only",
    sub: "You choose exactly who can see and send.",
    chips: ["Grandma Rose", "Grandpa Joe", "Aunt Maya"],
  },
  {
    title: "No DMs. No strangers.",
    sub: "Kids can never be contacted by anyone you haven't approved.",
    toggle: true,
  },
  {
    title: "You approve every message",
    sub: "Only encouragement gets through — reviewed by you first.",
    toggle: true,
  },
];

const CHIP_COLORS = [COLORS.coral, COLORS.sage, COLORS.sky];

const CheckCircle: React.FC<{ progress: number }> = ({ progress }) => (
  <svg width={44} height={44} viewBox="0 0 44 44">
    <circle cx={22} cy={22} r={20} fill={COLORS.success} opacity={Math.min(progress * 2, 1)} />
    <path
      d="M 13 22.5 L 19.5 29 L 31 16"
      stroke="#FFF"
      strokeWidth={4}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
      pathLength={1}
      strokeDasharray={1}
      strokeDashoffset={1 - progress}
    />
  </svg>
);

const Toggle: React.FC<{ on: number }> = ({ on }) => (
  <div
    style={{
      width: 64,
      height: 36,
      borderRadius: 18,
      backgroundColor: on > 0.5 ? COLORS.toggleOn : "#D8CCBA",
      position: "relative",
      flexShrink: 0,
    }}
  >
    <div
      style={{
        position: "absolute",
        top: 4,
        left: 4 + on * 28,
        width: 28,
        height: 28,
        borderRadius: 14,
        backgroundColor: "#FFF",
        boxShadow: "0 2px 6px rgba(0,0,0,0.2)",
      }}
    />
  </div>
);

export const S4Safety: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardIn = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 70, mass: 1 },
  });

  const shieldDraw = interpolate(frame, [14, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shieldCheck = interpolate(frame, [48, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Each trust row enters on its own beat
  const rowDelay = (i: number) => 60 + i * 34;

  return (
    <AbsoluteFill>
      {/* Calm, secure backdrop — slightly cooler than the home scenes */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(155deg, #F6F1E6 0%, ${COLORS.cream} 50%, #E9E4D2 100%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 70% 60% at 50% 30%, rgba(214,229,210,0.5) 0%, rgba(214,229,210,0) 70%)",
        }}
      />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {/* Dashboard card */}
        <div
          style={{
            width: 1340,
            borderRadius: 32,
            backgroundColor: "#FFFFFF",
            boxShadow: "0 40px 90px rgba(80,60,30,0.18)",
            display: "flex",
            overflow: "hidden",
            fontFamily: FONTS.ui,
            transform: `translateY(${(1 - cardIn) * 90 - 40}px) scale(${
              0.96 + cardIn * 0.04
            })`,
            opacity: cardIn,
          }}
        >
          {/* Left: shield panel */}
          <div
            style={{
              width: 420,
              background: `linear-gradient(170deg, #F2F7F0 0%, #E4EEE1 100%)`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: "60px 40px",
              gap: 24,
            }}
          >
            <svg width={150} height={170} viewBox="0 0 100 112">
              <path
                d="M 50 6 L 90 20 C 90 58 82 86 50 106 C 18 86 10 58 10 20 Z"
                fill="rgba(95,168,118,0.12)"
                stroke={COLORS.success}
                strokeWidth={5}
                strokeLinejoin="round"
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - shieldDraw}
              />
              <path
                d="M 33 54 L 46 67 L 69 38"
                stroke={COLORS.success}
                strokeWidth={7}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - shieldCheck}
              />
            </svg>
            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  fontFamily: FONTS.heading,
                  fontWeight: 600,
                  fontSize: 34,
                  color: COLORS.ink,
                }}
              >
                Parent Dashboard
              </div>
              <div style={{ fontSize: 19, color: COLORS.inkSoft, marginTop: 8 }}>
                You&rsquo;re in control of everything.
              </div>
            </div>
          </div>

          {/* Right: trust features */}
          <div
            style={{
              flex: 1,
              padding: "52px 56px",
              display: "flex",
              flexDirection: "column",
              gap: 34,
            }}
          >
            {ROWS.map((row, i) => {
              const p = spring({
                frame: frame - rowDelay(i),
                fps,
                config: { damping: 14, stiffness: 100 },
              });
              const check = interpolate(
                frame,
                [rowDelay(i) + 6, rowDelay(i) + 24],
                [0, 1],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
              );
              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    gap: 22,
                    alignItems: "flex-start",
                    opacity: p,
                    transform: `translateX(${(1 - p) * 50}px)`,
                  }}
                >
                  <CheckCircle progress={check} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 27, fontWeight: 700, color: COLORS.ink }}>
                      {row.title}
                    </div>
                    <div style={{ fontSize: 19, color: COLORS.inkSoft, marginTop: 5 }}>
                      {row.sub}
                    </div>
                    {/* Approved-family chips */}
                    {row.chips && (
                      <div style={{ display: "flex", gap: 12, marginTop: 14 }}>
                        {row.chips.map((name, j) => {
                          const chipIn = spring({
                            frame: frame - rowDelay(i) - 10 - j * 6,
                            fps,
                            config: { damping: 12, stiffness: 140 },
                          });
                          return (
                            <div
                              key={j}
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 9,
                                backgroundColor: "#FAF5EC",
                                border: `1px solid ${COLORS.uiBorder}`,
                                borderRadius: 999,
                                padding: "7px 18px 7px 8px",
                                transform: `scale(${Math.max(chipIn, 0)})`,
                              }}
                            >
                              <div
                                style={{
                                  width: 30,
                                  height: 30,
                                  borderRadius: 15,
                                  backgroundColor: CHIP_COLORS[j % 3],
                                  color: "#FFF",
                                  fontSize: 13,
                                  fontWeight: 700,
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                }}
                              >
                                {name
                                  .split(" ")
                                  .map((w) => w[0])
                                  .join("")}
                              </div>
                              <span style={{ fontSize: 16, fontWeight: 600, color: COLORS.ink }}>
                                {name}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                  {row.toggle && <Toggle on={Math.min(Math.max(p, 0), 1)} />}
                </div>
              );
            })}
            {/* Footer reassurance line */}
            <div
              style={{
                marginTop: 4,
                fontSize: 17,
                color: COLORS.inkSoft,
                opacity: interpolate(frame, [175, 200], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              {BRAND.childName}&rsquo;s world stays exactly as small — and as safe — as you want it.
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
