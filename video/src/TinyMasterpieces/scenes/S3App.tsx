import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { WarmRoom } from "../components/WarmRoom";
import { KidArt } from "../components/KidArt";
import { BRAND, COLORS, FONTS } from "../config";

/**
 * SCENE 3 (12–20s) — "Tiny Masterpieces helps families save, share,
 * and celebrate creativity."
 *
 * PLACEHOLDER VISUAL: a clean, modern phone mockup. The parent
 * captures the drawing → it uploads → lands in "Mia's Gallery".
 * The app UI here is built in React, so you can keep it even after
 * swapping other scenes for footage — or replace this whole scene
 * with a screen-recording clip: scene-03-app-upload.mp4
 *
 * TWEAK: beat timing in the BEATS object below; UI copy inline.
 */
const BEATS = {
  phoneIn: 0, // phone rises into frame
  photoSnap: 30, // artwork appears in the upload card
  uploadBar: 55, // progress bar fills (until ~85)
  saved: 92, // checkmark + "Saved" confirmation
  scrollToGallery: 130, // screen scrolls down to the gallery
  hearts: 168, // hearts pop on gallery items
};

const Heart: React.FC<{ size?: number; color?: string }> = ({
  size = 20,
  color = COLORS.coral,
}) => (
  <svg viewBox="0 0 24 24" width={size} height={size}>
    <path
      d="M12 21 C 7 16.5 2.5 13 2.5 8.5 C 2.5 5.5 5 3.5 7.5 3.5 C 9.5 3.5 11.2 4.6 12 6 C 12.8 4.6 14.5 3.5 16.5 3.5 C 19 3.5 21.5 5.5 21.5 8.5 C 21.5 13 17 16.5 12 21 Z"
      fill={color}
    />
  </svg>
);

/** Small app logo: a coral rounded square with a white heart. */
const AppMark: React.FC<{ size?: number }> = ({ size = 34 }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size * 0.28,
      background: `linear-gradient(135deg, ${COLORS.coral}, ${COLORS.coralDeep})`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    <Heart size={size * 0.55} color="#FFF" />
  </div>
);

export const S3App: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const phoneIn = spring({
    frame: frame - BEATS.phoneIn,
    fps,
    config: { damping: 17, stiffness: 60, mass: 1.1 },
  });
  const photo = spring({
    frame: frame - BEATS.photoSnap,
    fps,
    config: { damping: 13, stiffness: 110 },
  });
  const upload = interpolate(frame, [BEATS.uploadBar, BEATS.uploadBar + 32], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
  const saved = spring({
    frame: frame - BEATS.saved,
    fps,
    config: { damping: 11, stiffness: 130 },
  });
  const scroll = interpolate(
    frame,
    [BEATS.scrollToGallery, BEATS.scrollToGallery + 26],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    },
  );

  const galleryArts: Array<{ variant: "familySun" | "rainbow"; likes: number }> = [
    { variant: "familySun", likes: 4 },
    { variant: "rainbow", likes: 6 },
    { variant: "rainbow", likes: 3 },
    { variant: "familySun", likes: 5 },
  ];

  return (
    <AbsoluteFill>
      <WarmRoom />
      {/* Soft focus pool of light behind the phone */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle 620px at 50% 50%, rgba(255,250,238,0.75) 0%, rgba(255,250,238,0) 70%)",
        }}
      />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {/* ---- Phone ---- */}
        <div
          style={{
            width: 440,
            height: 920,
            borderRadius: 64,
            backgroundColor: "#241C16",
            padding: 14,
            boxShadow:
              "0 50px 100px rgba(60,32,10,0.45), 0 10px 30px rgba(60,32,10,0.3)",
            // Scaled to leave room for the text overlay below the phone
            transform: `translateY(${interpolate(phoneIn, [0, 1], [640, -56])}px) rotate(${
              (1 - phoneIn) * -5
            }deg) scale(0.74)`,
          }}
        >
          {/* Screen */}
          <div
            style={{
              width: "100%",
              height: "100%",
              borderRadius: 52,
              backgroundColor: "#FFFCF6",
              overflow: "hidden",
              position: "relative",
              fontFamily: FONTS.ui,
            }}
          >
            {/* Scrolling screen content */}
            <div style={{ transform: `translateY(${scroll * -480}px)` }}>
              {/* App header */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "54px 26px 18px",
                }}
              >
                <AppMark />
                <div
                  style={{
                    fontFamily: FONTS.heading,
                    fontWeight: 600,
                    fontSize: 26,
                    color: COLORS.ink,
                  }}
                >
                  {BRAND.name}
                </div>
              </div>

              {/* Upload card */}
              <div
                style={{
                  margin: "8px 26px",
                  borderRadius: 24,
                  border: `2px dashed ${upload >= 1 ? COLORS.success : "#DECDB4"}`,
                  backgroundColor: "#FFF",
                  padding: 18,
                  boxShadow: "0 8px 24px rgba(120,90,50,0.08)",
                }}
              >
                <div
                  style={{
                    fontSize: 17,
                    fontWeight: 600,
                    color: COLORS.inkSoft,
                    marginBottom: 12,
                  }}
                >
                  Add {BRAND.childName}&rsquo;s newest masterpiece
                </div>
                {/* The captured artwork */}
                <div
                  style={{
                    height: 250,
                    borderRadius: 16,
                    backgroundColor: COLORS.paper,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    transform: `scale(${interpolate(photo, [0, 1], [0.6, 1])})`,
                    opacity: photo,
                    border: `1px solid ${COLORS.uiBorder}`,
                  }}
                >
                  <div style={{ width: 300, height: 226 }}>
                    <KidArt progress={1} />
                  </div>
                </div>
                {/* Upload progress bar */}
                <div
                  style={{
                    marginTop: 16,
                    height: 10,
                    borderRadius: 5,
                    backgroundColor: "#F1E6D4",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${upload * 100}%`,
                      height: "100%",
                      borderRadius: 5,
                      background: `linear-gradient(90deg, ${COLORS.amber}, ${COLORS.coral})`,
                    }}
                  />
                </div>
                {/* Saved confirmation */}
                <div
                  style={{
                    marginTop: 12,
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    opacity: saved,
                    transform: `translateY(${(1 - saved) * 10}px)`,
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
                      transform: `scale(${saved})`,
                    }}
                  >
                    ✓
                  </div>
                  <span style={{ fontSize: 16, fontWeight: 600, color: COLORS.success }}>
                    Saved to {BRAND.childName}&rsquo;s gallery
                  </span>
                </div>
              </div>

              {/* Gallery */}
              <div style={{ padding: "22px 26px" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "baseline",
                    gap: 10,
                    marginBottom: 14,
                  }}
                >
                  <span
                    style={{
                      fontFamily: FONTS.heading,
                      fontWeight: 600,
                      fontSize: 24,
                      color: COLORS.ink,
                    }}
                  >
                    {BRAND.childName}&rsquo;s Gallery
                  </span>
                  <span
                    style={{
                      fontSize: 14,
                      color: COLORS.inkSoft,
                      backgroundColor: COLORS.creamDeep,
                      borderRadius: 999,
                      padding: "3px 12px",
                    }}
                  >
                    age {BRAND.childAge}
                  </span>
                </div>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 14,
                  }}
                >
                  {galleryArts.map((g, i) => {
                    const pop = spring({
                      frame: frame - BEATS.hearts - i * 5,
                      fps,
                      config: { damping: 10, stiffness: 160 },
                    });
                    return (
                      <div
                        key={i}
                        style={{
                          borderRadius: 16,
                          backgroundColor: "#FFF",
                          border: `1px solid ${COLORS.uiBorder}`,
                          padding: 10,
                          boxShadow: "0 6px 18px rgba(120,90,50,0.07)",
                        }}
                      >
                        <div style={{ height: 110 }}>
                          <KidArt variant={g.variant} progress={1} />
                        </div>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 6,
                            marginTop: 8,
                          }}
                        >
                          <div style={{ transform: `scale(${Math.max(pop, 0)})` }}>
                            <Heart size={18} />
                          </div>
                          <span style={{ fontSize: 14, color: COLORS.inkSoft }}>
                            {g.likes} from family
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
