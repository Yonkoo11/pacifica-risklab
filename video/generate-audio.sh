#!/usr/bin/env zsh
set -e

AUDIO_DIR="$(dirname "$0")/audio"
mkdir -p "$AUDIO_DIR"

VOICE_ID="nPczCjzI2devNBz1zQrb"
MODEL="eleven_multilingual_v2"

declare -A clips
clips[01-hook]="Three point nine out of ten. Critical."
clips[02-hook-context]="That's how Pacifica's BTC market scores when you replay the October crash at a hundred million in open interest."
clips[03-problem]="Pacifica lets you trade with up to 50x leverage across 63 markets. But what happens to those settings when the market drops fifteen percent in an hour?"
clips[04-agitation]="Right now, the only people who can answer that question charge one point six million a year. That's Gauntlet. There's nothing else."
clips[05-solution-intro]="So we built RiskLab. It connects to Pacifica's API and stress-tests live parameters against real crashes."
clips[06-walkthrough]="Pick a market. Pick a scenario. Set your OI. Hit run. The simulation takes about three seconds."
clips[07-cascade]="Under the hood, a thousand synthetic positions get liquidated minute by minute. Each liquidation pushes the price down. That triggers more liquidations. That's the cascade."
clips[08-funding]="The funding rate flips negative as open interest skews. You can see exactly when the stress peaks."
clips[09-compare]="Compare mode. Drop leverage from 50x to 20x. 224 fewer liquidations. The score jumps from critical to stable."
clips[10-close]="RiskLab. Self-serve stress testing for perp parameters. Built on Pacifica."

for clip in 01-hook 02-hook-context 03-problem 04-agitation 05-solution-intro 06-walkthrough 07-cascade 08-funding 09-compare 10-close; do
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

  # Check if output is valid audio (MP3 starts with ID3 or ff fb)
  if file "$OUT" | grep -q "ASCII text\|JSON data\|XML"; then
    echo "ERROR: $clip got error response"
    rm "$OUT"
    exit 1
  fi

  echo "$clip OK ($(wc -c < "$OUT") bytes)"
done

echo "All audio clips generated."
