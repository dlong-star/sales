#!/usr/bin/env bash
# Builds a ~33s "Tiny Masterpieces" commercial from a 6s Higgsfield (Veo 3.1 Lite)
# hero clip plus ffmpeg-generated animated title cards, a slow-motion replay,
# and an end card, joined with crossfades over a soft ambient music pad.
# Narration: ElevenLabs (if ELEVENLABS_API_KEY is set) -> Edge neural TTS -> gTTS.
set -euxo pipefail

cd "$(dirname "$0")"

HERO_URL="https://d8j0ntlcm91z4.cloudfront.net/user_3ExfFjaun3sXTSOTTXNbjldaB4m/hf_20260610_212848_cd2b0b2b-f3e8-4f66-8fa5-f0b78fcfd444.mp4"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W=1344 H=768 FPS=24
XF=0.5  # crossfade duration

if ! command -v ffmpeg >/dev/null; then
  sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
fi
if [ ! -f "$FONT" ]; then
  sudo apt-get update -qq && sudo apt-get install -y -qq fonts-dejavu-core
fi

mkdir -p work out
curl -fsSL -o work/hero.mp4 "$HERO_URL"

pip3 install --quiet edge-tts gTTS || pip3 install --quiet --break-system-packages edge-tts gTTS

dur_of() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }

# say OUTFILE.wav TEXT — ElevenLabs Rachel if key present, else Edge Jenny, else gTTS.
say() {
  local out=$1 text=$2
  rm -f "$out" "$out.mp3"
  if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
    curl -fsS -X POST \
      "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM?output_format=mp3_44100_128" \
      -H "xi-api-key: ${ELEVENLABS_API_KEY}" -H "Content-Type: application/json" \
      -d "{\"text\": \"$text\", \"model_id\": \"eleven_multilingual_v2\"}" \
      -o "$out.mp3" || true
  fi
  if [ ! -s "$out.mp3" ] || ! ffprobe -v error "$out.mp3"; then
    edge-tts --voice en-US-JennyNeural --rate=-5% --text "$text" --write-media "$out.mp3" || true
  fi
  if [ ! -s "$out.mp3" ] || ! ffprobe -v error "$out.mp3"; then
    gtts-cli "$text" -o "$out.mp3"
  fi
  ffmpeg -y -i "$out.mp3" -ar 48000 -ac 2 "$out"
}

say work/vo1.wav "Every kid is an artist."
say work/vo2.wav "But their best work deserves more than the fridge."
say work/vo4.wav "Their art. Printed. Mailed. Treasured."
say work/vo5.wav "Real postcards, made from their drawings, delivered to the people they love."
say work/vo6.wav "Tiny Masterpieces. Start free today at tiny masterpieces dot com."

# Animated warm gradient background if this ffmpeg supports it, else flat color.
if ffmpeg -v error -f lavfi -i "gradients=s=64x64:c0=0x2A1E14:c1=0x0D0905:n=2:speed=0.02:d=0.1:r=24" -frames:v 1 -f null - ; then
  bg_src() { echo "gradients=s=${W}x${H}:c0=0x261B11:c1=0x0D0905:n=2:speed=0.015:d=$1:r=${FPS}"; }
else
  bg_src() { echo "color=c=0x1A1410:s=${W}x${H}:d=$1:r=${FPS}"; }
fi

VO_CHAIN="loudnorm=I=-16:TP=-1.5,aresample=48000,aformat=channel_layouts=stereo,adelay=600|600,apad"

# card OUTFILE VOFILE LINE1 LINE2 SIZE1 SIZE2 [MIN_DUR]
# Card duration stretches to fit its narration; text drifts up gently.
# Text must not contain commas, colons, or quotes (filtergraph syntax).
card() {
  local outfile=$1 vo=$2 line1=$3 line2=$4 size1=$5 size2=$6 min=${7:-4}
  local vo_dur dur
  vo_dur=$(dur_of "$vo")
  dur=$(awk "BEGIN{d=$vo_dur+1.6; if(d<$min)d=$min; printf \"%.2f\", d}")
  ffmpeg -y \
    -f lavfi -i "$(bg_src "$dur")" \
    -i "$vo" \
    -filter_complex "[0:v]drawtext=fontfile=${FONT}:text=${line1}:fontcolor=0xF5E9D8:fontsize=${size1}:x=(w-text_w)/2:y=(h/2)-text_h-16-2*t,\
drawtext=fontfile=${FONT}:text=${line2}:fontcolor=0xD9B98C:fontsize=${size2}:x=(w-text_w)/2:y=(h/2)+34-2*t[v];\
[1:a]${VO_CHAIN}[a]" \
    -map "[v]" -map "[a]" -t "$dur" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -ar 48000 -ac 2 "$outfile"
}

card work/seg1.mp4 work/vo1.wav "Every kid is an artist." " " 72 40
card work/seg2.mp4 work/vo2.wav "Their best work deserves" "more than the fridge." 56 56
card work/seg5.mp4 work/vo5.wav "Real postcards from their drawings." "Delivered to the people they love." 50 50
card work/seg6.mp4 work/vo6.wav "Tiny Masterpieces" "Start free at tinymasterpieces.com" 92 44 6

# Hero clip at full speed with its generated voiceover and music.
ffmpeg -y -i work/hero.mp4 \
  -vf "scale=${W}:${H},fps=${FPS}" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 work/seg3.mp4

# Slow-motion replay of the emotional payoff (2.5s-6s at half speed -> 7s),
# narrated with the tagline lower third.
ffmpeg -y -ss 2.5 -to 6 -i work/hero.mp4 -i work/vo4.wav \
  -filter_complex "[0:v]scale=${W}:${H},setpts=2.0*PTS,fps=${FPS},\
drawtext=fontfile=${FONT}:text=Their art. Printed. Mailed. Treasured.:fontcolor=0xF5E9D8:fontsize=48:x=(w-text_w)/2:y=h-140:box=1:boxcolor=0x1A1410@0.45:boxborderw=18[v];\
[1:a]loudnorm=I=-16:TP=-1.5,aresample=48000,aformat=channel_layouts=stereo,adelay=900|900,apad[a]" \
  -map "[v]" -map "[a]" -t 7 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 work/seg4.mp4

# --- Assemble with crossfades + soft ambient pad ---
d1=$(dur_of work/seg1.mp4); d2=$(dur_of work/seg2.mp4); d3=$(dur_of work/seg3.mp4)
d4=$(dur_of work/seg4.mp4); d5=$(dur_of work/seg5.mp4); d6=$(dur_of work/seg6.mp4)
o1=$(awk "BEGIN{printf \"%.3f\", $d1-$XF}")
o2=$(awk "BEGIN{printf \"%.3f\", $o1+$d2-$XF}")
o3=$(awk "BEGIN{printf \"%.3f\", $o2+$d3-$XF}")
o4=$(awk "BEGIN{printf \"%.3f\", $o3+$d4-$XF}")
o5=$(awk "BEGIN{printf \"%.3f\", $o4+$d5-$XF}")
total=$(awk "BEGIN{printf \"%.3f\", $o5+$d6}")
fade_out_start=$(awk "BEGIN{printf \"%.3f\", $total-1.2}")
pad_fade_out=$(awk "BEGIN{printf \"%.3f\", $total-3}")

# Warm A-major sine pad, slow attack, low in the mix.
PAD="aevalsrc=0.05*sin(2*PI*110*t)+0.05*sin(2*PI*164.81*t)+0.04*sin(2*PI*220*t)+0.03*sin(2*PI*277.18*t):s=48000:d=${total},lowpass=f=900,tremolo=f=0.15:d=0.3,volume=0.16,afade=t=in:st=0:d=3,afade=t=out:st=${pad_fade_out}:d=3,aformat=channel_layouts=stereo"

ffmpeg -y \
  -i work/seg1.mp4 -i work/seg2.mp4 -i work/seg3.mp4 \
  -i work/seg4.mp4 -i work/seg5.mp4 -i work/seg6.mp4 \
  -f lavfi -i "$PAD" \
  -filter_complex "\
[0:v][1:v]xfade=transition=fade:duration=${XF}:offset=${o1}[v1];\
[v1][2:v]xfade=transition=fade:duration=${XF}:offset=${o2}[v2];\
[v2][3:v]xfade=transition=fade:duration=${XF}:offset=${o3}[v3];\
[v3][4:v]xfade=transition=fade:duration=${XF}:offset=${o4}[v4];\
[v4][5:v]xfade=transition=fade:duration=${XF}:offset=${o5},\
fade=t=in:st=0:d=0.6,fade=t=out:st=${fade_out_start}:d=1.2[v];\
[0:a][1:a]acrossfade=d=${XF}[a1];\
[a1][2:a]acrossfade=d=${XF}[a2];\
[a2][3:a]acrossfade=d=${XF}[a3];\
[a3][4:a]acrossfade=d=${XF}[a4];\
[a4][5:a]acrossfade=d=${XF}[a5];\
[a5][6:a]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=${fade_out_start}:d=1.2[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 -movflags +faststart \
  out/tiny_masterpieces_ad.mp4

ffprobe -v error -show_entries format=duration,size out/tiny_masterpieces_ad.mp4
