import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BRAND, COLORS, FONTS, LOGO_IMAGE } from "../config";

/**
 * SCENE 9 (57–60s) — END CARD
 *
 *   Tiny Masterpieces
 *   Big confidence from little creations.
 *   Every kid is an artist. We make sure they believe it.
 *
 * To use your real logo: drop it at public/assets/logo/logo.png and
 * set LOGO_IMAGE.enabled = true in config.ts. All copy comes from
 * BRAND in config.ts.
 */
export const S9EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const markIn = spring({
    frame,
    fps,
    config: { damping: 13, stiffness: 90 },
  });
  const heartDraw = interpolate(frame, [6, 26], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lineIn = (at: number) =>
    spring({ frame: frame - at, fps, config: { damping: 15, stiffness: 80 } });

  const w1 = lineIn(14);
  const w2 = lineIn(26);
  const w3 = lineIn(38);

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: COLORS.cream }} />
      {/* Gentle center glow */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle 720px at 50% 44%, rgba(255,238,210,0.9) 0%, rgba(255,238,210,0) 70%)",
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          gap: 30,
        }}
      >
        {/* Logo mark */}
        <div style={{ transform: `scale(${markIn})` }}>
          {LOGO_IMAGE.enabled ? (
            <Img
              src={staticFile(LOGO_IMAGE.file)}
              style={{ width: 150, height: 150, objectFit: "contain" }}
            />
          ) : (
            <div
              style={{
                width: 150,
                height: 150,
                borderRadius: 42,
                background: `linear-gradient(135deg, ${COLORS.coral}, ${COLORS.coralDeep})`,
                boxShadow: "0 26px 60px rgba(216,104,69,0.45)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {/* Crayon-style heart drawing itself */}
              <svg viewBox="0 0 100 100" width={92} height={92}>
                <path
                  d="M 50 82 C 30 66 14 53 14 36 C 14 24 24 16 34 16 C 42 16 48 21 50 27 C 52 21 58 16 66 16 C 76 16 86 24 86 36 C 86 53 70 66 50 82 Z"
                  stroke="#FFF"
                  strokeWidth={8}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - heartDraw}
                />
              </svg>
            </div>
          )}
        </div>

        {/* Wordmark */}
        <div
          style={{
            fontFamily: FONTS.heading,
            fontWeight: 600,
            fontSize: 86,
            color: COLORS.ink,
            opacity: w1,
            transform: `translateY(${(1 - w1) * 30}px)`,
          }}
        >
          {BRAND.name}
        </div>

        {/* Tagline */}
        <div
          style={{
            fontFamily: FONTS.heading,
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 40,
            color: COLORS.coralDeep,
            marginTop: -14,
            opacity: w2,
            transform: `translateY(${(1 - w2) * 24}px)`,
          }}
        >
          {BRAND.tagline}
        </div>

        {/* Subline */}
        <div
          style={{
            fontFamily: FONTS.ui,
            fontSize: 26,
            color: COLORS.inkSoft,
            letterSpacing: 0.4,
            opacity: w3,
            transform: `translateY(${(1 - w3) * 20}px)`,
          }}
        >
          {BRAND.subline}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
