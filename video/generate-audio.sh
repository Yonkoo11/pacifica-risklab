#!/usr/bin/env zsh
set -e

AUDIO_DIR="$(dirname "$0")/audio"
mkdir -p "$AUDIO_DIR"

VOICE_ID="nPczCjzI2devNBz1zQrb"
MODEL="eleven_multilingual_v2"

declare -A clips
clips[01-hero]="Survival score: 3.9 out of 10. Critical. 612 positions liquidated in a single crash."
clips[02-markets]="Pacifica offers up to 50x leverage across 63 markets. But nobody's tested what happens to these parameters during a real crash."
clips[03-scenarios]="Gauntlet charges one point six million dollars a year for this kind of stress testing. There's no open source alternative."
clips[04-fullapp]="RiskLab pulls live parameters from Pacifica's API. Pick a market. Pick a historical crash. Set your hypothetical open interest. Hit run."
clips[05-cascade]="The engine generates a thousand synthetic positions, then replays the crash minute by minute. Each liquidation hits the price. The price drop triggers more liquidations. That's the cascade."
clips[06-compare]="Compare mode shows the impact of changing parameters. Drop leverage from 50x to 20x. 224 fewer liquidations. Survival jumps from critical to stable."
clips[07-close]="RiskLab. Self-serve parameter stress testing. Built on Pacifica."

for clip in 01-hero 02-markets 03-scenarios 04-fullapp 05-cascade 06-compare 07-close; do
  OUT="$AUDIO_DIR/$clip.mp3"
  if [[ -f "$OUT" ]]; then
    echo "Skipping $clip (exists)"
    continue
  fi
  echo "Generating $clip..."

  TEXT="${clips[$clip]}"

  curl -s "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"text\": \"$TEXT\",
      \"model_id\": \"$MODEL\",
      \"voice_settings\": {
        \"stability\": 0.82,
        \"similarity_boost\": 0.65,
        \"style\": 0.03
      }
    }" \
    --output "$OUT"

  # Verify it's audio not error JSON
  if file "$OUT" | grep -q "JSON\|text\|XML"; then
    echo "ERROR: $clip got error response:"
    cat "$OUT"
    rm "$OUT"
    exit 1
  fi

  echo "$clip OK ($(wc -c < "$OUT") bytes)"
done

echo "All audio clips generated."
