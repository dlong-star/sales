import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { COLORS, SceneDef, sceneDuration } from "../config";
import { Overlay } from "./Overlay";

/**
 * SceneFrame — wraps every scene and provides:
 *
 *  1. CLIP SWAPPING — if `scene.clip.enabled` is true in config.ts,
 *     the placeholder visuals are replaced by your real / AI-generated
 *     footage from public/assets/clips/, with a dark scrim added so
 *     the overlay text stays readable.
 *
 *  2. SOFT DISSOLVES — every scene fades in/out through the warm
 *     cream base color (a gentle "dip to cream", not a hard cut).
 *
 *  3. CINEMATIC DRIFT — a slow Ken Burns push-in on the placeholder
 *     content so no frame ever feels frozen.
 *
 *  4. THE TEXT OVERLAY for the scene.
 */
export const SceneFrame: React.FC<{
  scene: SceneDef;
  children: React.ReactNode;
  /** Where the overlay sits for this scene */
  overlayPosition?: "low" | "center";
  /** Strength of the slow push-in (0 disables) */
  drift?: number;
}> = ({ scene, children, overlayPosition = "low", drift = 0.045 }) => {
  const frame = useCurrentFrame();
  const dur = sceneDuration(scene);

  // Soft dissolve at scene edges (first scene fades from cream too —
  // it reads as the commercial "breathing in").
  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [dur - 10, dur - 1], [1, 0], {
    extrapolateLeft: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);

  // Slow cinematic push-in
  const scale = 1 + (frame / dur) * drift;

  const useClip = scene.clip?.enabled === true;

  return (
    <AbsoluteFill style={{ opacity }}>
      {useClip && scene.clip ? (
        <>
          {/* ===== REAL FOOTAGE MODE =====
              Your clip from public/assets/clips/. It is muted and
              cover-fitted; trim/grade the clip itself for best results. */}
          <OffthreadVideo
            muted
            src={staticFile(`assets/clips/${scene.clip.file}`)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
          {/* Legibility scrim behind the overlay text */}
          <AbsoluteFill
            style={{
              background: `linear-gradient(180deg, rgba(0,0,0,0) 55%, ${COLORS.clipScrim} 100%)`,
            }}
          />
        </>
      ) : (
        /* ===== PLACEHOLDER MODE ===== */
        <AbsoluteFill style={{ transform: `scale(${scale})` }}>
          {children}
        </AbsoluteFill>
      )}

      {scene.overlay !== "" && (
        <Overlay
          text={scene.overlay}
          onClip={useClip}
          position={overlayPosition}
        />
      )}
    </AbsoluteFill>
  );
};
