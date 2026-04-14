#!/usr/bin/env zsh
set -e

AUDIO_DIR="$(dirname "$0")/audio"
mkdir -p "$AUDIO_DIR"

VOICE_ID="nPczCjzI2devNBz1zQrb"
MODEL="eleven_multilingual_v2"

declare -A clips
clips[01-hero]="Three point nine out of ten. That's how Pacifica's BTC market scores when you replay the October crash at a hundred million in open interest."
clips[02-markets]="Pacifica lets you trade with up to 50x leverage. Sixty three markets, all live. But what actually happens to those settings when the market drops fifteen percent in an hour?"
clips[03-scenarios]="Right now, the only people who can answer that question charge one point six million a year. That's what Gauntlet costs. There's nothing else."
clips[04-fullapp]="So we built RiskLab. It connects to Pacifica's API, pulls the live parameters, and stress-tests them against real historical crashes. You pick a market, pick a scenario, set your OI, and hit run."
clips[05-cascade]="Under the hood, it generates a thousand synthetic positions and replays the crash minute by minute. When positions get liquidated, that pushes the price down further, which triggers more liquidations. That's the cascade effect."
clips[06-compare]="Here's where it gets useful. Turn on compare mode, drop the leverage from 50x to 20x, and you can see exactly what changes. 224 fewer liquidations. The score jumps from critical to stable."
clips[07-close]="RiskLab. Self-serve stress testing for perp parameters. Built on Pacifica."

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

  if file "$OUT" | grep -q "JSON\|text\|XML"; then
    echo "ERROR: $clip got error response:"
    cat "$OUT"
    rm "$OUT"
    exit 1
  fi

  echo "$clip OK ($(wc -c < "$OUT") bytes)"
done

echo "All audio clips generated."
