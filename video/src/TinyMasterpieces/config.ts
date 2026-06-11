/**
 * ============================================================
 *  TINY MASTERPIECES — COMMERCIAL CONTROL CENTER
 * ============================================================
 *  This file is the ONE place to edit:
 *    1. Scene timing (start / end, in seconds)
 *    2. All on-screen overlay text
 *    3. Brand colors & fonts
 *    4. Swapping placeholder scenes for real / AI-generated
 *       video clips (Veo, Runway, Kling, Pika ...)
 *    5. Music
 *
 *  HOW TO REPLACE A PLACEHOLDER SCENE WITH A REAL CLIP:
 *    1. Drop your clip into  public/assets/clips/
 *       using the exact filename listed in SCENES below
 *       (or change the filename here to match yours).
 *    2. Flip  clip.enabled  to  true  for that scene.
 *    That's it — the motion-graphics placeholder is replaced
 *    by your footage, and the text overlay automatically
 *    switches to light-on-dark with a legibility scrim.
 *
 *  See  public/assets/README.md  for the full asset guide,
 *  including ready-to-paste AI video generation prompts
 *  for every scene.
 * ============================================================
 */

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

/** Total runtime: 60 seconds. */
export const DURATION_IN_FRAMES = 60 * FPS;

/* ------------------------------------------------------------
 * BRAND
 * ---------------------------------------------------------- */
export const BRAND = {
  name: "Tiny Masterpieces",
  tagline: "Big confidence from little creations.",
  subline: "Every kid is an artist. We make sure they believe it.",
  /** The child featured in the story. Used in app UI + postcard. */
  childName: "Mia",
  childAge: 6,
  /** The loved one receiving the keepsake. */
  grandparentName: "Grandma Rose",
};

/* ------------------------------------------------------------
 * COLORS — warm, premium, family palette
 * ---------------------------------------------------------- */
export const COLORS = {
  /** Page / paper backgrounds */
  cream: "#FAF5ED",
  creamDeep: "#F1E6D7",
  paper: "#FFFDF7",

  /** Typography */
  ink: "#3B2E25", // warm near-black for headlines
  inkSoft: "#7A685B", // secondary text

  /** Brand accents */
  coral: "#E8795A",
  coralDeep: "#D96845",
  amber: "#F2A93B",
  sage: "#94B292",
  sky: "#85B3D1",
  blush: "#F3C5B2",

  /** UI */
  white: "#FFFFFF",
  uiBorder: "#EEE4D6",
  success: "#5FA876",
  toggleOn: "#5FA876",

  /** Scrim placed behind text when a real video clip is used */
  clipScrim: "rgba(30, 18, 10, 0.55)",
};

/* ------------------------------------------------------------
 * FONTS — loaded from public/assets/fonts (see fonts.ts)
 * ---------------------------------------------------------- */
export const FONTS = {
  /** Emotional headlines + wordmark (serif) */
  heading: "Fraunces",
  /** App / dashboard UI (sans) */
  ui: "Inter",
  /** Handwriting — grandma's note, postcard, kid signature */
  hand: "Caveat",
};

/* ------------------------------------------------------------
 * MUSIC
 *  Drop a 60s warm piano / acoustic track at:
 *    public/assets/music/soundtrack.mp3
 *  then set enabled: true.
 * ---------------------------------------------------------- */
export const MUSIC = {
  enabled: false,
  file: "assets/music/soundtrack.mp3",
  volume: 0.75,
  /** Seconds of fade-out at the very end */
  fadeOutSeconds: 3,
};

/* ------------------------------------------------------------
 * OPTIONAL REAL-IMAGE SWAPS
 *  Replace the built-in crayon drawing with a photo/scan of a
 *  real kid's artwork (PNG/JPG, roughly 4:3):
 * ---------------------------------------------------------- */
export const ARTWORK_IMAGE = {
  enabled: false,
  file: "assets/images/artwork-hero.png",
};

/** Replace the built-in end-card logo with your real logo file. */
export const LOGO_IMAGE = {
  enabled: false,
  file: "assets/logo/logo.png",
};

/* ------------------------------------------------------------
 * SCENES — timing, overlay copy, and clip swap per scene.
 *  start/end are in SECONDS and match the creative brief.
 *  Adjacent scenes dissolve softly through the cream base.
 * ---------------------------------------------------------- */
export type SceneClip = {
  /** Filename inside public/assets/clips/ */
  file: string;
  /** true → use the video file instead of the placeholder */
  enabled: boolean;
};

export type SceneDef = {
  id:
    | "create"
    | "moment"
    | "app"
    | "safety"
    | "keepsake"
    | "grandparents"
    | "encouragement"
    | "confidence"
    | "endcard";
  start: number;
  end: number;
  /** Main text overlay. Empty string = no overlay (end card). */
  overlay: string;
  clip: SceneClip | null;
};

export const SCENES: SceneDef[] = [
  {
    id: "create",
    start: 0,
    end: 6,
    overlay: "Every kid creates something worth celebrating.",
    clip: { file: "scene-01-child-drawing.mp4", enabled: false },
  },
  {
    id: "moment",
    start: 6,
    end: 12,
    overlay: "But sometimes those little moments disappear too fast.",
    clip: { file: "scene-02-proud-moment.mp4", enabled: false },
  },
  {
    id: "app",
    start: 12,
    end: 20,
    overlay: "Tiny Masterpieces helps families save, share, and celebrate creativity.",
    clip: { file: "scene-03-app-upload.mp4", enabled: false },
  },
  {
    id: "safety",
    start: 20,
    end: 28,
    overlay: "Safe for kids. Simple for parents.",
    clip: { file: "scene-04-parent-dashboard.mp4", enabled: false },
  },
  {
    id: "keepsake",
    start: 28,
    end: 36,
    overlay: "Turn their creations into keepsakes your family can hold.",
    clip: { file: "scene-05-keepsake-mail.mp4", enabled: false },
  },
  {
    id: "grandparents",
    start: 36,
    end: 44,
    overlay: "Share their imagination with the people who love them most.",
    clip: { file: "scene-06-grandparents.mp4", enabled: false },
  },
  {
    id: "encouragement",
    start: 44,
    end: 52,
    overlay: "Encouragement they can feel, keep, and remember.",
    clip: { file: "scene-07-encouragement.mp4", enabled: false },
  },
  {
    id: "confidence",
    start: 52,
    end: 57,
    overlay: "Because confidence grows when kids feel seen.",
    clip: { file: "scene-08-confidence.mp4", enabled: false },
  },
  {
    id: "endcard",
    start: 57,
    end: 60,
    overlay: "",
    clip: null,
  },
];

/** Frames helper: duration of a scene in frames. */
export const sceneDuration = (s: SceneDef) => Math.round((s.end - s.start) * FPS);
