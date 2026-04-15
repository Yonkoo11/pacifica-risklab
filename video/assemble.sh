#!/usr/bin/env zsh
setopt +o nomatch
set -e

VIDEO_DIR="$(dirname "$0")"
COMPOSITES_DIR="$VIDEO_DIR/composites"
AUDIO_DIR="$VIDEO_DIR/audio"
SEGMENTS_DIR="$VIDEO_DIR/segments"
mkdir -p "$SEGMENTS_DIR"

VFADE_IN=0.2
AUDIO_DELAY=0.5
BREATH=0.3
VFADE_OUT=0.2
GAP=0.3

CLIPS=(01-hook 02-hook-context 03-problem 04-agitation 05-solution-intro 06-walkthrough 07-cascade 08-funding 09-compare 10-close)

echo "=== Building segments ==="

for clip in "${CLIPS[@]}"; do
  SEG="$SEGMENTS_DIR/$clip.mp4"
  COMP="$COMPOSITES_DIR/$clip.png"
  AUD="$AUDIO_DIR/$clip.mp3"

  if [[ ! -f "$COMP" || ! -f "$AUD" ]]; then
    echo "MISSING: $COMP or $AUD"
    exit 1
  fi

  AUDIO_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$AUD")
  TOTAL=$(python3 -c "print(round($AUDIO_DELAY + $AUDIO_DUR + $BREATH + $VFADE_OUT, 3))")
  FO_START=$(python3 -c "print(round($TOTAL - $VFADE_OUT, 3))")
  AFO_START=$(python3 -c "print(round($AUDIO_DELAY + $AUDIO_DUR - 0.25, 3))")

  echo "Building $clip: audio=${AUDIO_DUR}s total=${TOTAL}s"

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

  echo "  -> $clip done"
done

# Gap segment
echo "=== Creating gap segment ==="
ffmpeg -y \
  -f lavfi -i "color=c=black:s=1920x1080:d=${GAP}" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -t "$GAP" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -r 30 "$SEGMENTS_DIR/gap.mp4" 2>/dev/null

# Concat
echo "=== Assembling final video ==="
CONCAT_FILE="$SEGMENTS_DIR/concat.txt"
rm -f "$CONCAT_FILE"
for i in "${CLIPS[@]}"; do
  echo "file '$i.mp4'" >> "$CONCAT_FILE"
  echo "file 'gap.mp4'" >> "$CONCAT_FILE"
done
sed -i '' '$ d' "$CONCAT_FILE"

# No background music — clean voiceover only
ffmpeg -y \
  -f concat -safe 0 -i "$CONCAT_FILE" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  "$VIDEO_DIR/risklab-demo.mp4" 2>/dev/null

FINAL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO_DIR/risklab-demo.mp4")
echo "=== DONE ==="
echo "Output: $VIDEO_DIR/risklab-demo.mp4"
echo "Duration: ${FINAL_DUR}s"
