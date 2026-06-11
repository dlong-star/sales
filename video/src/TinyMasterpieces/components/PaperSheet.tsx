import React from "react";
import { Img, staticFile } from "remotion";
import { ARTWORK_IMAGE, BRAND, COLORS, FONTS } from "../config";
import { KidArt } from "./KidArt";

/**
 * PaperSheet — a sheet of drawing paper with soft shadow that hosts
 * the kid's artwork. If ARTWORK_IMAGE.enabled is true in config.ts,
 * a real photo/scan of artwork is shown instead of the crayon SVG.
 */
export const PaperSheet: React.FC<{
  width?: number;
  artProgress?: number;
  variant?: "familySun" | "rainbow";
  rotate?: number;
  /** Show the "Mia · age 6" signature once the drawing is finished */
  signed?: boolean;
  style?: React.CSSProperties;
}> = ({ width = 620, artProgress = 1, variant = "familySun", rotate = 0, signed = true, style }) => {
  const height = width * 0.74;
  return (
    <div
      style={{
        width,
        height,
        backgroundColor: COLORS.paper,
        borderRadius: 8,
        boxShadow:
          "0 18px 45px rgba(82, 54, 28, 0.28), 0 4px 12px rgba(82, 54, 28, 0.15)",
        transform: `rotate(${rotate}deg)`,
        position: "relative",
        padding: width * 0.04,
        ...style,
      }}
    >
      {ARTWORK_IMAGE.enabled ? (
        <Img
          src={staticFile(ARTWORK_IMAGE.file)}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      ) : (
        <KidArt variant={variant} progress={artProgress} />
      )}
      {/* Child's signature, bottom-right corner */}
      {signed && artProgress >= 0.97 && (
        <div
          style={{
            position: "absolute",
            right: width * 0.06,
            bottom: width * 0.025,
            fontFamily: FONTS.hand,
            fontSize: width * 0.052,
            color: "#A08868",
            transform: "rotate(-3deg)",
          }}
        >
          {BRAND.childName}, age {BRAND.childAge}
        </div>
      )}
    </div>
  );
};
