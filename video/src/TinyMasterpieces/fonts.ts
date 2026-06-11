/**
 * Font loading — fonts are bundled locally in public/assets/fonts
 * so the project renders with zero network access.
 *
 * To change typography: drop new .ttf files into public/assets/fonts,
 * update the paths below, and update FONTS in config.ts.
 */
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Exported as a function (called from the composition component)
// rather than a bare side-effect import: package.json's "sideEffects"
// field would let webpack tree-shake a side-effect-only module away,
// and delayRender() requires a mounted composition anyway.
let loaded = false;

export const loadFonts = () => {
  if (loaded) {
    return;
  }
  loaded = true;

  loadFont({
    family: "Fraunces",
    url: staticFile("assets/fonts/Fraunces-SemiBold.ttf"),
    weight: "600",
  });

  loadFont({
    family: "Fraunces",
    url: staticFile("assets/fonts/Fraunces-MediumItalic.ttf"),
    weight: "500",
    style: "italic",
  });

  loadFont({
    family: "Inter",
    url: staticFile("assets/fonts/Inter-Variable.ttf"),
  });

  loadFont({
    family: "Caveat",
    url: staticFile("assets/fonts/Caveat-SemiBold.ttf"),
    weight: "600",
  });
};
