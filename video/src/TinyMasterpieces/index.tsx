import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  staticFile,
} from "remotion";
import { loadFonts } from "./fonts";
import {
  COLORS,
  DURATION_IN_FRAMES,
  FPS,
  MUSIC,
  SCENES,
  SceneDef,
  sceneDuration,
} from "./config";
import { SceneFrame } from "./components/SceneFrame";
import { Vignette } from "./components/Vignette";
import { S1Create } from "./scenes/S1Create";
import { S2Moment } from "./scenes/S2Moment";
import { S3App } from "./scenes/S3App";
import { S4Safety } from "./scenes/S4Safety";
import { S5Keepsake } from "./scenes/S5Keepsake";
import { S6Grandparents } from "./scenes/S6Grandparents";
import { S7Encouragement } from "./scenes/S7Encouragement";
import { S8Confidence } from "./scenes/S8Confidence";
import { S9EndCard } from "./scenes/S9EndCard";

/**
 * TINY MASTERPIECES — 60s parent commercial
 *
 * The film is assembled here from the SCENES timeline in config.ts.
 * Each scene lives in its own file under scenes/ — open one to tweak
 * its visuals; open config.ts to change timing, copy, colors, or to
 * swap any placeholder for real / AI-generated footage.
 */
const SCENE_COMPONENTS: Record<SceneDef["id"], React.FC> = {
  create: S1Create,
  moment: S2Moment,
  app: S3App,
  safety: S4Safety,
  keepsake: S5Keepsake,
  grandparents: S6Grandparents,
  encouragement: S7Encouragement,
  confidence: S8Confidence,
  endcard: S9EndCard,
};

export const TinyMasterpieces: React.FC = () => {
  // Load the bundled fonts (no-op after the first call)
  loadFonts();

  // Music fades out over the last seconds (see MUSIC in config.ts)
  const musicVolume = (f: number) =>
    MUSIC.volume *
    interpolate(
      f,
      [DURATION_IN_FRAMES - MUSIC.fadeOutSeconds * FPS, DURATION_IN_FRAMES - 5],
      [1, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
    );

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cream }}>
      {SCENES.map((scene) => {
        const Component = SCENE_COMPONENTS[scene.id];
        return (
          <Sequence
            key={scene.id}
            from={scene.start * FPS}
            durationInFrames={sceneDuration(scene)}
            name={`${scene.start}s–${scene.end}s  ${scene.id}`}
          >
            <SceneFrame
              scene={scene}
              // The end card handles its own layout & has no drift
              drift={scene.id === "endcard" ? 0 : undefined}
            >
              <Component />
            </SceneFrame>
          </Sequence>
        );
      })}

      {/* Constant cinematic vignette over everything */}
      <Vignette />

      {/* Soundtrack — enable in config.ts once you add the file */}
      {MUSIC.enabled && (
        <Audio src={staticFile(MUSIC.file)} volume={musicVolume} />
      )}
    </AbsoluteFill>
  );
};
