#!/usr/bin/env bash
# Builds a ~37s "Tiny Masterpieces" commercial from a 6s Higgsfield (Veo 3.1 Lite)
# hero clip plus ffmpeg-generated title cards, a slow-motion replay, and an end card.
set -euxo pipefail

cd "$(dirname "$0")"

HERO_URL="https://d8j0ntlcm91z4.cloudfront.net/user_3ExfFjaun3sXTSOTTXNbjldaB4m/hf_20260610_212848_cd2b0b2b-f3e8-4f66-8fa5-f0b78fcfd444.mp4"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W=1344 H=768 FPS=24

if ! command -v ffmpeg >/dev/null; then
  sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
fi
if [ ! -f "$FONT" ]; then
  sudo apt-get update -qq && sudo apt-get install -y -qq fonts-dejavu-core
fi

mkdir -p work out
curl -fsSL -o work/hero.mp4 "$HERO_URL"

# card OUTFILE DURATION LINE1 LINE2 SIZE1 SIZE2
# Text must not contain commas, colons, or quotes (ffmpeg filtergraph syntax).
card() {
  local outfile=$1 dur=$2 line1=$3 line2=$4 size1=$5 size2=$6
  local fade_out_start
  fade_out_start=$(awk "BEGIN{print $dur-0.7}")
  ffmpeg -y \
    -f lavfi -i "color=c=0x1A1410:s=${W}x${H}:d=${dur}:r=${FPS}" \
    -f lavfi -t "$dur" -i "anullsrc=channel_layout=stereo:sample_rate=48000" \
    -vf "drawtext=fontfile=${FONT}:text=${line1}:fontcolor=0xF5E9D8:fontsize=${size1}:x=(w-text_w)/2:y=(h/2)-text_h-20,\
drawtext=fontfile=${FONT}:text=${line2}:fontcolor=0xD9B98C:fontsize=${size2}:x=(w-text_w)/2:y=(h/2)+30,\
fade=t=in:st=0:d=0.7,fade=t=out:st=${fade_out_start}:d=0.7" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -ar 48000 -ac 2 -shortest "$outfile"
}

card work/seg1.mp4 5 "Every kid is an artist." " " 72 40
card work/seg2.mp4 4 "Their best work deserves" "more than the fridge." 56 56
card work/seg5.mp4 4 "Real postcards from their drawings." "Delivered to the people they love." 50 50
card work/seg6.mp4 6 "Tiny Masterpieces" "Start free at tinymasterpieces.com" 92 44

# Hero clip at full speed with its generated voiceover and music.
ffmpeg -y -i work/hero.mp4 \
  -vf "scale=${W}:${H},fps=${FPS},fade=t=in:st=0:d=0.4" \
  -af "afade=t=in:st=0:d=0.3,afade=t=out:st=5.3:d=0.7" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 work/seg3.mp4

# Slow-motion replay (0.5x -> 12s), silent, with a tagline lower third.
ffmpeg -y -i work/hero.mp4 \
  -f lavfi -t 12 -i "anullsrc=channel_layout=stereo:sample_rate=48000" \
  -filter_complex "[0:v]scale=${W}:${H},setpts=2.0*PTS,fps=${FPS},\
drawtext=fontfile=${FONT}:text=Their art. Printed. Mailed. Treasured.:fontcolor=0xF5E9D8:fontsize=48:x=(w-text_w)/2:y=h-140:box=1:boxcolor=0x1A1410@0.45:boxborderw=18,\
fade=t=in:st=0:d=0.5,fade=t=out:st=11.3:d=0.7[v]" \
  -map "[v]" -map 1:a -t 12 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 work/seg4.mp4

# Concatenate: card / card / hero / slow-mo / card / end card  (5+4+6+12+4+6 = 37s)
ffmpeg -y \
  -i work/seg1.mp4 -i work/seg2.mp4 -i work/seg3.mp4 \
  -i work/seg4.mp4 -i work/seg5.mp4 -i work/seg6.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a][4:v][4:a][5:v][5:a]concat=n=6:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 -movflags +faststart \
  out/tiny_masterpieces_ad.mp4

ffprobe -v error -show_entries format=duration,size out/tiny_masterpieces_ad.mp4
