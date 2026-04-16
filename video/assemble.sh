#!/usr/bin/env zsh
setopt +o nomatch
set -e

VIDEO_DIR="$(dirname "$0")"
cd "$VIDEO_DIR/.."
VIDEO_DIR="$(pwd)/video"

COMPOSITES_DIR="$VIDEO_DIR/composites"
AUDIO_DIR="$VIDEO_DIR/audio"
REMOTION_DIR="$VIDEO_DIR/remotion-out"
SEGMENTS_DIR="$VIDEO_DIR/segments"
mkdir -p "$SEGMENTS_DIR"

VFADE_IN=0.2
AUDIO_DELAY=0.5
BREATH=0.3
VFADE_OUT=0.2
GAP=0.3

# Clips: name|type|source
# type=static uses composites/<name>.png
# type=remotion uses remotion-out/<source>.mp4
CLIPS=(
  "01-hook|remotion|hook.mp4"
  "02-problem-setup|static|"
  "03-gap|static|"
  "04-who|static|"
  "05-intro|static|"
  "06-fit|static|"
  "07-market|static|"
  "08-scenario|static|"
  "09-parameters|static|"
  "10-run-hero|remotion|hook.mp4"
  "11-stats|static|"
  "12-cascade|remotion|cascade.mp4"
  "13-funding|static|"
  "14-compare|remotion|compare.mp4"
  "15-limits|static|"
  "16-api-1|static|"
  "17-api-2|static|"
  "18-builder|static|"
  "19-who-uses|static|"
  "20-why-now|static|"
  "21-roadmap|static|"
  "22-close|remotion|hook.mp4"
)

echo "=== Building segments ==="

build_static_segment() {
  local clip="$1"
  local SEG="$SEGMENTS_DIR/$clip.mp4"
  local COMP="$COMPOSITES_DIR/$clip.png"
  local AUD="$AUDIO_DIR/$clip.mp3"

  [[ ! -f "$COMP" || ! -f "$AUD" ]] && { echo "MISSING: $COMP or $AUD"; exit 1; }

  local AUDIO_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$AUD")
  local TOTAL=$(python3 -c "print(round($AUDIO_DELAY + $AUDIO_DUR + $BREATH + $VFADE_OUT, 3))")
  local FO_START=$(python3 -c "print(round($TOTAL - $VFADE_OUT, 3))")
  local AFO_START=$(python3 -c "print(round($AUDIO_DELAY + $AUDIO_DUR - 0.25, 3))")

  echo "Static $clip: audio=${AUDIO_DUR}s total=${TOTAL}s"

  ffmpeg -y \
    -loop 1 -i "$COMP" \
    -i "$AUD" \
    -filter_complex "
      anullsrc=r=44100:cl=stereo,atrim=0:${AUDIO_DELAY}[silence];
      [silence][1:a]concat=n=2:v=0:a=1[joined];
      [joined]afade=t=in:st=${AUDIO_DELAY}:d=0.15,afade=t=out:st=${AFO_START}:d=0.25,apad=whole_dur=${TOTAL}[a];
      [0:v]scale=1920:1080,fade=t=in:st=0:d=${VFADE_IN},fade=t=out:st=${FO_START}:d=${VFADE_OUT}[v]
    " \
    -map "[v]" -map "[a]" \
    -t "$TOTAL" \
    -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
    -c:a aac -b:a 128k \
    -r 30 "$SEG" 2>/dev/null
}

build_remotion_segment() {
  local clip="$1"
  local source="$2"
  local SEG="$SEGMENTS_DIR/$clip.mp4"
  local VID="$REMOTION_DIR/$source"
  local AUD="$AUDIO_DIR/$clip.mp3"

  [[ ! -f "$VID" || ! -f "$AUD" ]] && { echo "MISSING: $VID or $AUD"; exit 1; }

  local AUDIO_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$AUD")
  local TOTAL=$(python3 -c "print(round($AUDIO_DELAY + $AUDIO_DUR + $BREATH + $VFADE_OUT, 3))")
  local FO_START=$(python3 -c "print(round($TOTAL - $VFADE_OUT, 3))")
  local AFO_START=$(python3 -c "print(round($AUDIO_DELAY + $AUDIO_DUR - 0.25, 3))")
  local VID_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VID")

  echo "Remotion $clip: audio=${AUDIO_DUR}s vid=${VID_DUR}s total=${TOTAL}s"

  # Loop the remotion video if audio is longer
  ffmpeg -y \
    -stream_loop -1 -i "$VID" \
    -i "$AUD" \
    -filter_complex "
      anullsrc=r=44100:cl=stereo,atrim=0:${AUDIO_DELAY}[silence];
      [silence][1:a]concat=n=2:v=0:a=1[joined];
      [joined]afade=t=in:st=${AUDIO_DELAY}:d=0.15,afade=t=out:st=${AFO_START}:d=0.25,apad=whole_dur=${TOTAL}[a];
      [0:v]scale=1920:1080,fade=t=in:st=0:d=${VFADE_IN},fade=t=out:st=${FO_START}:d=${VFADE_OUT}[v]
    " \
    -map "[v]" -map "[a]" \
    -t "$TOTAL" \
    -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
    -c:a aac -b:a 128k \
    -r 30 "$SEG" 2>/dev/null
}

for entry in "${CLIPS[@]}"; do
  IFS='|' read -r clip type source <<< "$entry"
  if [[ "$type" == "static" ]]; then
    build_static_segment "$clip"
  else
    build_remotion_segment "$clip" "$source"
  fi
done

# Gap segment
echo "=== Creating gap ==="
ffmpeg -y \
  -f lavfi -i "color=c=black:s=1920x1080:d=${GAP}" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -t "$GAP" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -r 30 "$SEGMENTS_DIR/gap.mp4" 2>/dev/null

# Concat
echo "=== Concat ==="
CONCAT_FILE="$SEGMENTS_DIR/concat.txt"
rm -f "$CONCAT_FILE"
for entry in "${CLIPS[@]}"; do
  IFS='|' read -r clip type source <<< "$entry"
  echo "file '$clip.mp4'" >> "$CONCAT_FILE"
  echo "file 'gap.mp4'" >> "$CONCAT_FILE"
done
sed -i '' '$ d' "$CONCAT_FILE"

ffmpeg -y \
  -f concat -safe 0 -i "$CONCAT_FILE" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_DIR/risklab-demo.mp4" 2>/dev/null

FINAL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO_DIR/risklab-demo.mp4")
echo "=== DONE ==="
echo "Output: $VIDEO_DIR/risklab-demo.mp4"
echo "Duration: ${FINAL_DUR}s"
