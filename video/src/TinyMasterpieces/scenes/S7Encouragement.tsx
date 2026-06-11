import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { WarmRoom } from "../components/WarmRoom";
import { BRAND, COLORS, FONTS } from "../config";

/**
 * SCENE 7 (44–52s) — "Encouragement they can feel, keep, and
 * remember."
 *
 * PLACEHOLDER VISUAL: grandma's note writes itself in real
 * handwriting, a parent-approved badge confirms it was delivered
 * safely, and little hearts bloom around the card as the child
 * receives it.
 *
 * REPLACE WITH AI CLIP: scene-07-encouragement.mp4
 *
 * TWEAK: the note's wording in NOTE_LINES; writing speed via
 * CHARS_PER_FRAME.
 */
const NOTE_LINES = [
  `We love your sunshine painting, ${BRAND.childName}!`,
  "It's already on our fridge.",
  "— Love, Grandma",
];
const WRITE_START = 26; // frame the pen "touches down"
const CHARS_PER_FRAME = 0.85; // handwriting speed

/** Reveals text character by character, like handwriting. */
const Handwrite: React.FC<{
  text: string;
  startFrame: number;
  fontSize: number;
}> = ({ text, startFrame, fontSize }) => {
  const frame = useCurrentFrame();
  const visible = Math.floor((frame - startFrame) * CHARS_PER_FRAME);
  return (
    <div
      style={{
        fontFamily: FONTS.hand,
        fontSize,
        lineHeight: 1.4,
        color: COLORS.ink,
      }}
    >
      {text.split("").map((ch, i) => (
        <span key={i} style={{ opacity: i < visible ? 1 : 0 }}>
          {ch}
        </span>
      ))}
    </div>
  );
};

export const S7Encouragement: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardIn = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 70 },
  });

  // Delivery badge ("Approved by Mom") after the note is written
  const badgeIn = spring({
    frame: frame - 150,
    fps,
    config: { damping: 12, stiffness: 130 },
  });

  // Hearts bloom around the card as the child receives the note
  const hearts = [
    { x: -470, y: -160, s: 44, at: 168 },
    { x: 480, y: -210, s: 56, at: 178 },
    { x: -400, y: 170, s: 36, at: 188 },
    { x: 450, y: 140, s: 42, at: 196 },
    { x: 0, y: -300, s: 38, at: 206 },
  ];

  // Per-line start frames, based on previous line lengths
  let acc = WRITE_START;
  const lineStarts = NOTE_LINES.map((l) => {
    const s = acc;
    acc += l.length / CHARS_PER_FRAME + 8;
    return s;
  });

  return (
    <AbsoluteFill>
      <WarmRoom brightness={0.3} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {/* Blooming hearts */}
        {hearts.map((h, i) => {
          const pop = spring({
            frame: frame - h.at,
            fps,
            config: { damping: 9, stiffness: 120 },
          });
          const float = Math.max(frame - h.at, 0) * -0.6;
          return (
            <svg
              key={i}
              viewBox="0 0 24 24"
              width={h.s}
              height={h.s}
              style={{
                position: "absolute",
                transform: `translate(${h.x}px, ${h.y + float}px) scale(${Math.max(pop, 0)})`,
                opacity: pop * interpolate(frame - h.at, [0, 55], [1, 0.25], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              <path
                d="M12 21 C 7 16.5 2.5 13 2.5 8.5 C 2.5 5.5 5 3.5 7.5 3.5 C 9.5 3.5 11.2 4.6 12 6 C 12.8 4.6 14.5 3.5 16.5 3.5 C 19 3.5 21.5 5.5 21.5 8.5 C 21.5 13 17 16.5 12 21 Z"
                fill={COLORS.coral}
              />
            </svg>
          );
        })}

        {/* The note card */}
        <div
          style={{
            width: 880,
            backgroundColor: "#FFFBF1",
            borderRadius: 18,
            borderTop: `8px solid ${COLORS.coral}`,
            boxShadow: "0 36px 80px rgba(90,60,25,0.3)",
            padding: "56px 70px 48px",
            transform: `translateY(${(1 - cardIn) * 140 - 40}px) rotate(${
              (1 - cardIn) * 3 - 1
            }deg)`,
            opacity: cardIn,
            position: "relative",
          }}
        >
          {NOTE_LINES.map((line, i) => (
            <Handwrite
              key={i}
              text={line}
              startFrame={lineStarts[i]}
              fontSize={i === NOTE_LINES.length - 1 ? 44 : 52}
            />
          ))}

          {/* Safe-delivery badge — quiet trust reminder */}
          <div
            style={{
              position: "absolute",
              right: 46,
              bottom: -26,
              display: "flex",
              alignItems: "center",
              gap: 10,
              backgroundColor: "#FFFFFF",
              borderRadius: 999,
              padding: "10px 22px",
              boxShadow: "0 12px 30px rgba(90,60,25,0.22)",
              fontFamily: FONTS.ui,
              fontSize: 18,
              fontWeight: 600,
              color: COLORS.ink,
              transform: `scale(${Math.max(badgeIn, 0)})`,
            }}
          >
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: 13,
                backgroundColor: COLORS.success,
                color: "#FFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 15,
                fontWeight: 700,
              }}
            >
              ✓
            </div>
            Approved by Mom &middot; delivered to {BRAND.childName}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
