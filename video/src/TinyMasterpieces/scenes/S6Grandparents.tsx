import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { BRAND, COLORS, FONTS } from "../config";
import { PaperSheet } from "../components/PaperSheet";
import { KidArt } from "../components/KidArt";

/**
 * SCENE 6 (36–44s) — "Share their imagination with the people who
 * love them most."
 *
 * PLACEHOLDER VISUAL, two beats:
 *   Beat 1 — the envelope arrives and opens; the postcard rises out
 *            in a warm glow.
 *   Beat 2 — dissolve to grandma's fridge: the artwork gets pinned
 *            under a red magnet next to a hand-written sticky note.
 *
 * REPLACE WITH AI CLIP: scene-06-grandparents.mp4
 *   (grandparents opening mail, smiling, pinning art to the fridge)
 *
 * TWEAK: BEAT2_AT controls when the fridge moment starts.
 */
const BEAT2_AT = 96;

export const S6Grandparents: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  /* ---------- Beat 1: the envelope ---------- */
  const envIn = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 70 },
  });
  const flapOpen = interpolate(frame, [30, 58], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const cardOut = interpolate(frame, [52, 96], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const beat1Fade = interpolate(frame, [BEAT2_AT - 14, BEAT2_AT], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  /* ---------- Beat 2: grandma's fridge ---------- */
  const beat2Fade = interpolate(frame, [BEAT2_AT - 4, BEAT2_AT + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pin = spring({
    frame: frame - (BEAT2_AT + 14),
    fps,
    config: { damping: 11, stiffness: 90, mass: 1 },
  });
  const stickyIn = spring({
    frame: frame - (BEAT2_AT + 50),
    fps,
    config: { damping: 13, stiffness: 110 },
  });
  // Warm light sweeping across the fridge door
  const sweep = interpolate(frame, [BEAT2_AT + 20, 240], [-40, 120], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      {/* Grandma's hallway light — slightly rosier than the home scenes */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(150deg, #FBF3E6 0%, ${COLORS.cream} 50%, #EBD9C4 100%)`,
        }}
      />

      {/* ============ BEAT 1 — envelope opens ============ */}
      {beat1Fade > 0 && (
        <AbsoluteFill
          style={{
            justifyContent: "center",
            alignItems: "center",
            opacity: beat1Fade,
          }}
        >
          <AbsoluteFill
            style={{
              background:
                "radial-gradient(circle 560px at 50% 48%, rgba(255,231,190,0.7) 0%, rgba(255,231,190,0) 70%)",
              opacity: cardOut,
            }}
          />
          <div
            style={{
              position: "relative",
              transform: `translateY(${(1 - envIn) * 200 + 110}px)`,
            }}
          >
            {/* Postcard rising out of the envelope */}
            <div
              style={{
                position: "absolute",
                left: 70,
                bottom: 150,
                width: 460,
                transform: `translateY(${(1 - cardOut) * 270}px) rotate(${
                  -3 + cardOut * 4
                }deg)`,
                zIndex: 1,
              }}
            >
              <div
                style={{
                  backgroundColor: "#FFF",
                  borderRadius: 10,
                  padding: 18,
                  boxShadow: "0 24px 60px rgba(90,60,25,0.3)",
                }}
              >
                <div style={{ height: 300 }}>
                  <KidArt progress={1} />
                </div>
              </div>
            </div>
            {/* Envelope body */}
            <div
              style={{
                width: 600,
                height: 360,
                backgroundColor: "#F3E6CF",
                borderRadius: 12,
                boxShadow: "0 30px 70px rgba(90,60,25,0.35)",
                position: "relative",
                zIndex: 2,
                overflow: "hidden",
              }}
            >
              {/* Inner shadow giving the envelope depth */}
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  background:
                    "linear-gradient(180deg, rgba(120,90,50,0.18) 0%, rgba(120,90,50,0) 30%)",
                }}
              />
              {/* Address on the envelope */}
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  right: 0,
                  top: 130,
                  textAlign: "center",
                  fontFamily: FONTS.hand,
                  fontSize: 42,
                  color: COLORS.ink,
                }}
              >
                {BRAND.grandparentName}
              </div>
              {/* Heart seal */}
              <svg
                width={56}
                height={56}
                viewBox="0 0 24 24"
                style={{
                  position: "absolute",
                  left: "50%",
                  top: 36,
                  transform: "translateX(-50%)",
                  opacity: 1 - flapOpen,
                }}
              >
                <path
                  d="M12 21 C 7 16.5 2.5 13 2.5 8.5 C 2.5 5.5 5 3.5 7.5 3.5 C 9.5 3.5 11.2 4.6 12 6 C 12.8 4.6 14.5 3.5 16.5 3.5 C 19 3.5 21.5 5.5 21.5 8.5 C 21.5 13 17 16.5 12 21 Z"
                  fill={COLORS.coral}
                />
              </svg>
            </div>
            {/* Envelope flap (opens backwards) */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: 0,
                height: 0,
                borderLeft: "300px solid transparent",
                borderRight: "300px solid transparent",
                borderTop: "190px solid #EBD9B8",
                transformOrigin: "top center",
                transform: `rotateX(${flapOpen * 165}deg)`,
                zIndex: flapOpen > 0.45 ? 0 : 3,
                filter: `brightness(${1 - flapOpen * 0.18})`,
              }}
            />
          </div>
        </AbsoluteFill>
      )}

      {/* ============ BEAT 2 — pinned to the fridge ============ */}
      {beat2Fade > 0 && (
        <AbsoluteFill
          style={{
            justifyContent: "center",
            alignItems: "center",
            opacity: beat2Fade,
          }}
        >
          {/* Fridge door */}
          <div
            style={{
              width: 1080,
              height: 980,
              marginTop: 60,
              borderRadius: 34,
              background: "linear-gradient(105deg, #F3F0E9 0%, #E9E4DA 55%, #DFD8CB 100%)",
              boxShadow: "0 50px 110px rgba(70,50,25,0.25), inset 0 2px 0 rgba(255,255,255,0.8)",
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Door handle */}
            <div
              style={{
                position: "absolute",
                left: 44,
                top: 90,
                width: 22,
                height: 360,
                borderRadius: 11,
                background: "linear-gradient(90deg, #C9C2B4, #EFEAE0)",
                boxShadow: "0 8px 20px rgba(70,50,25,0.25)",
              }}
            />
            {/* Light sweep across the door */}
            <div
              style={{
                position: "absolute",
                top: 0,
                bottom: 0,
                left: `${sweep}%`,
                width: 300,
                background:
                  "linear-gradient(100deg, rgba(255,248,230,0) 0%, rgba(255,248,230,0.75) 50%, rgba(255,248,230,0) 100%)",
              }}
            />
            {/* The pinned artwork */}
            <div
              style={{
                position: "absolute",
                left: "50%",
                top: 150,
                transform: `translateX(-50%)
                  translateY(${(1 - pin) * -70}px)
                  rotate(${-3 + pin * 1.5}deg)
                  scale(${0.94 + pin * 0.06})`,
                opacity: Math.min(pin * 2, 1),
              }}
            >
              <PaperSheet width={520} />
              {/* Round red magnet */}
              <div
                style={{
                  position: "absolute",
                  top: -16,
                  left: "50%",
                  transform: `translateX(-50%) scale(${Math.min(Math.max(pin, 0), 1)})`,
                  width: 52,
                  height: 52,
                  borderRadius: 26,
                  background: "radial-gradient(circle at 35% 30%, #F2876B, #C84B2E)",
                  boxShadow: "0 8px 16px rgba(70,30,10,0.35)",
                }}
              />
            </div>
            {/* Grandma's sticky note */}
            <div
              style={{
                position: "absolute",
                right: 130,
                top: 620,
                width: 230,
                height: 220,
                backgroundColor: "#FBE7A2",
                boxShadow: "0 14px 30px rgba(70,50,25,0.22)",
                transform: `rotate(4deg) scale(${Math.max(stickyIn, 0)})`,
                padding: 20,
                fontFamily: FONTS.hand,
                fontSize: 32,
                lineHeight: 1.25,
                color: "#6B4F2A",
              }}
            >
              Call {BRAND.childName} Sunday — tell her it&rsquo;s beautiful!
            </div>
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
