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
import { KidArt } from "../components/KidArt";

/**
 * SCENE 5 (28–36s) — "Turn their creations into keepsakes your
 * family can hold."
 *
 * PLACEHOLDER VISUAL: the artwork becomes a printed postcard —
 * it flips over to reveal a handwritten address to Grandma, a stamp
 * pops on, and it glides away into the mail.
 *
 * REPLACE WITH AI CLIP: scene-05-keepsake-mail.mp4
 *
 * TWEAK: beat timings below; address text in ADDRESS.
 */
const BEATS = {
  cardIn: 0,
  flip: 70, // postcard flips to the address side
  stamp: 118, // stamp thumps on
  mailAway: 168, // card glides off to be mailed
};

const ADDRESS = [BRAND.grandparentName, "42 Maple Lane", "Cedar Falls"];

export const S5Keepsake: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardIn = spring({
    frame: frame - BEATS.cardIn,
    fps,
    config: { damping: 15, stiffness: 65, mass: 1 },
  });

  const flip = interpolate(frame, [BEATS.flip, BEATS.flip + 28], [0, 180], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const stamp = spring({
    frame: frame - BEATS.stamp,
    fps,
    config: { damping: 12, stiffness: 180, mass: 0.8 },
  });

  const away = interpolate(frame, [BEATS.mailAway, BEATS.mailAway + 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });

  const cardW = 760;
  const cardH = 540;

  return (
    <AbsoluteFill>
      {/* Studio-warm backdrop: the "premium print" environment */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(165deg, #F8F0E2 0%, ${COLORS.creamDeep} 60%, #E2D2BA 100%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle 700px at 50% 42%, rgba(255,247,230,0.9) 0%, rgba(255,247,230,0) 70%)",
        }}
      />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ perspective: 1600 }}>
          <div
            style={{
              width: cardW,
              height: cardH,
              position: "relative",
              transformStyle: "preserve-3d",
              transform: `
                translateY(${(1 - cardIn) * 160 - 40}px)
                translateX(${away * 1400}px)
                rotate(${away * 14}deg)
                rotateY(${flip}deg)
                scale(${0.9 + cardIn * 0.1 - away * 0.15})`,
              opacity: 1 - away * 0.2,
            }}
          >
            {/* ---------- FRONT: the printed artwork ---------- */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                backfaceVisibility: "hidden",
                backgroundColor: "#FFFFFF",
                borderRadius: 14,
                boxShadow: "0 36px 80px rgba(90,60,25,0.32)",
                padding: 30,
                display: "flex",
                flexDirection: "column",
              }}
            >
              <div style={{ flex: 1 }}>
                <KidArt progress={1} />
              </div>
              <div
                style={{
                  textAlign: "center",
                  fontFamily: FONTS.hand,
                  fontSize: 34,
                  color: COLORS.inkSoft,
                  marginTop: 6,
                }}
              >
                {BRAND.childName}, age {BRAND.childAge}
              </div>
            </div>

            {/* ---------- BACK: address + stamp ---------- */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                backfaceVisibility: "hidden",
                transform: "rotateY(180deg)",
                backgroundColor: "#FFFDF6",
                borderRadius: 14,
                boxShadow: "0 36px 80px rgba(90,60,25,0.32)",
                display: "flex",
                padding: 44,
              }}
            >
              {/* Message side */}
              <div style={{ flex: 1.1, paddingRight: 36 }}>
                <div
                  style={{
                    fontFamily: FONTS.hand,
                    fontSize: 37,
                    lineHeight: 1.45,
                    color: COLORS.ink,
                    transform: "rotate(-1deg)",
                  }}
                >
                  Hi Grandma! I made this just for you.
                  <br />
                  xoxo, {BRAND.childName}
                </div>
                <div
                  style={{
                    marginTop: 28,
                    fontFamily: FONTS.ui,
                    fontSize: 15,
                    color: "#B9A88F",
                    letterSpacing: 1.5,
                  }}
                >
                  PRINTED WITH LOVE BY TINY MASTERPIECES
                </div>
              </div>
              {/* Divider */}
              <div style={{ width: 2, backgroundColor: "#E9DCC5" }} />
              {/* Address side */}
              <div
                style={{
                  flex: 1,
                  paddingLeft: 40,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  position: "relative",
                }}
              >
                {/* Stamp */}
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    right: 4,
                    width: 110,
                    height: 130,
                    backgroundColor: "#FFF",
                    border: "3px dashed #D9C8A8",
                    borderRadius: 6,
                    padding: 10,
                    transform: `scale(${interpolate(stamp, [0, 1], [2.2, 1])}) rotate(${
                      (1 - stamp) * 20 - 4
                    }deg)`,
                    opacity: Math.min(stamp * 2, 1),
                  }}
                >
                  <KidArt variant="rainbow" progress={1} />
                </div>
                {ADDRESS.map((line, i) => (
                  <div
                    key={i}
                    style={{
                      fontFamily: FONTS.hand,
                      fontSize: i === 0 ? 44 : 36,
                      color: COLORS.ink,
                      borderBottom: "2px solid #EADDC4",
                      paddingBottom: 6,
                      marginBottom: 16,
                      marginTop: i === 0 ? 90 : 0,
                    }}
                  >
                    {i === 0 ? `To: ${line}` : line}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
