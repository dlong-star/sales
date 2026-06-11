# Tiny Masterpieces — Asset Guide

This folder holds everything you'll swap in to take the commercial
from "polished placeholder" to "final film".

```
public/assets/
├── clips/    ← real / AI-generated video clips (one per scene)
├── images/   ← real artwork scans, app screenshots
├── logo/     ← your logo files
├── music/    ← the 60s soundtrack
└── fonts/    ← bundled typography (already set up)
```

All swaps are controlled from **`src/TinyMasterpieces/config.ts`** —
you never need to touch scene code just to replace an asset.

---

## 1. Video clips (`clips/`)

Drop a clip in this folder using the exact filename below, then set
`clip.enabled: true` for that scene in `config.ts`. The placeholder is
replaced instantly; the overlay text switches to white-on-scrim
automatically.

**Clip specs:** 1920×1080 (or larger), at least as long as the scene,
muted is fine (clips are muted on import). Warm, soft, natural light
grades best with the rest of the film.

| Scene | File | Length | What to show |
|---|---|---|---|
| 1 (0–6s) | `scene-01-child-drawing.mp4` | ≥ 6s | Child at kitchen table drawing, focused & excited |
| 2 (6–12s) | `scene-02-proud-moment.mp4` | ≥ 6s | Child proudly shows artwork; parent smiles, validates |
| 3 (12–20s) | `scene-03-app-upload.mp4` | ≥ 8s | Parent photographs artwork with phone / app upload |
| 4 (20–28s) | `scene-04-parent-dashboard.mp4` | ≥ 8s | Parent calmly reviewing app controls on phone/sofa |
| 5 (28–36s) | `scene-05-keepsake-mail.mp4` | ≥ 8s | Artwork as printed postcard / keepsake being mailed |
| 6 (36–44s) | `scene-06-grandparents.mp4` | ≥ 8s | Grandparents open mail, smile, pin art to fridge |
| 7 (44–52s) | `scene-07-encouragement.mp4` | ≥ 8s | Grandparent writes note; child receives it, smiles |
| 8 (52–57s) | `scene-08-confidence.mp4` | ≥ 5s | Child drawing again — prouder, more confident |

### Ready-to-paste AI generation prompts (Veo / Runway / Kling / Pika)

Add to every prompt: *"Cinematic family commercial, soft warm morning
light, shallow depth of field, realistic, premium TV-ad look, gentle
slow camera push-in, no text, no logos."*

- **Scene 1:** "A 6-year-old girl sits at a wooden kitchen table drawing with crayons, deeply focused, tongue slightly out in concentration, warm sunlight through a window."
- **Scene 2:** "The girl holds up her crayon drawing to her mother, beaming with pride. The mother kneels, smiles warmly and admires the drawing."
- **Scene 3:** "Close-up of a parent's hands photographing a child's crayon drawing with a smartphone at a kitchen table, clean modern app on screen."
- **Scene 4:** "A relaxed mother on a sofa reviews simple privacy settings on her phone, calm and reassured, soft evening lamp light."
- **Scene 5:** "Macro shot of a child's drawing printed as a beautiful thick postcard, hands placing it into an envelope, craft paper textures."
- **Scene 6:** "An elderly couple at their front door opens an envelope, their faces light up; cut to the drawing pinned with a magnet on their fridge."
- **Scene 7:** "Close-up of a grandmother's hands writing a short loving note with a fountain pen; then a little girl reading it and smiling."
- **Scene 8:** "The same girl at the kitchen table starting a new, bigger drawing, confident and joyful, brighter daylight than before."

---

## 2. Images (`images/`)

| File | Used for | Enable via |
|---|---|---|
| `artwork-hero.png` | A real kid's drawing (photo/scan, ~4:3, white paper) replaces the built-in crayon SVG everywhere it appears | `ARTWORK_IMAGE` in config.ts |

---

## 3. Logo (`logo/`)

| File | Used for | Enable via |
|---|---|---|
| `logo.png` | End-card logo mark (square, transparent PNG, ≥ 300×300) | `LOGO_IMAGE` in config.ts |

---

## 4. Music (`music/`)

Place a 60-second track at `music/soundtrack.mp3` and set
`MUSIC.enabled: true` in config.ts. It fades out automatically over
the last 3 seconds.

**Direction:** warm felt piano or acoustic guitar, gentle build around
0:12 (app intro) and an emotional peak around 0:36–0:50 (grandparents
/ encouragement). Search terms on Artlist / Epidemic Sound /
Musicbed: *"heartfelt piano family"*, *"warm acoustic hopeful"*.

---

## 5. Fonts (`fonts/`) — already configured

| File | Family | Role |
|---|---|---|
| `Fraunces-SemiBold.ttf` | Fraunces | Emotional headlines, wordmark |
| `Fraunces-MediumItalic.ttf` | Fraunces | Tagline |
| `Inter-Variable.ttf` | Inter | App & dashboard UI |
| `Caveat-SemiBold.ttf` | Caveat | Handwriting (notes, postcard, signatures) |

To change typography, replace the files and update
`src/TinyMasterpieces/fonts.ts` + `FONTS` in config.ts.
