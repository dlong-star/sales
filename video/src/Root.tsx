import "./index.css";
import { Composition } from "remotion";
import { TinyMasterpieces } from "./TinyMasterpieces";
import {
  DURATION_IN_FRAMES,
  FPS,
  HEIGHT,
  WIDTH,
} from "./TinyMasterpieces/config";

/**
 * Render with:
 *   npx remotion render TinyMasterpieces out/tiny-masterpieces.mp4
 *
 * Preview / edit live:
 *   npm run dev
 */
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="TinyMasterpieces"
      component={TinyMasterpieces}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
