#!/usr/bin/env zsh
set -e

AUDIO_DIR="$(dirname "$0")/audio"
mkdir -p "$AUDIO_DIR"

VOICE_ID="nPczCjzI2devNBz1zQrb"
MODEL="eleven_multilingual_v2"

declare -A clips
clips[01-hook]="Three point nine out of ten. Critical."
clips[02-problem-setup]="Pacifica lets you trade with up to 50x leverage across 63 perpetuals markets. People put real money behind those settings every day."
clips[03-gap]="Nobody has actually tested what those parameters do in a real crash. When Bitcoin dropped fifteen percent in an hour last October, would Pacifica's current setup have survived? I don't know. You don't know."
clips[04-who]="This matters if you run a perp market, size a position, or write risk reports. Gauntlet charges one point six million a year to answer it. Nothing open source exists."
clips[05-intro]="So I built RiskLab. Pick a Pacifica market. Pick a crash. Set your hypothetical open interest. Hit run. The tool shows you what breaks."
clips[06-fit]="It runs on Pacifica's public API. No wallet, no auth. This is an Analytics and Data track project."
clips[07-market]="Start with a market. Every Pacifica perp is here with its live leverage and open interest. Let's pick BTC at 50x."
clips[08-scenario]="Five historical scenarios, pulled from Binance candles. October 2025. The LUNA collapse. December 2024 flash drop. SVB week. And a mild five percent correction."
clips[09-parameters]="Three sliders. Hypothetical open interest from one million to one billion. Leverage override if you want to test a proposal. Long short ratio."
clips[10-run-hero]="Hit run. Three seconds later: three point nine out of ten. Critical."
clips[11-stats]="612 positions liquidated. Fifty six million dollars of volume wiped. Fifty six percent of open interest gone."
clips[12-cascade]="Here's the cascade. A thousand synthetic positions, minute by minute. Each liquidation pushes the price down. That triggers the next wave. Watch it accelerate at step 88."
clips[13-funding]="Funding flips negative as open interest skews short. You can see exactly when the stress hits its cap."
clips[14-compare]="Compare mode is where this gets useful. Drop leverage from 50x to 20x and rerun. 224 fewer liquidations. 19 percent less open interest wiped. The score jumps from critical to stable."
clips[15-limits]="The model's assumptions are documented. Linear market impact. Synthetic positions. No cross-margin. Every simplification is in the UI."
clips[16-api-1]="Everything you see is live from Pacifica. The info endpoint gives us every market's specs. The prices endpoint gives us live leverage, open interest, and mark price."
clips[17-api-2]="Funding rate history powers the stress chart. The orderbook endpoint feeds the market impact model. Four endpoints, zero auth."
clips[18-builder]="I didn't need builder code for a read-only analytics tool. But every number on screen comes directly from Pacifica. Nothing is faked."
clips[19-who-uses]="Pacifica's live BTC open interest is currently around 450 dollars. The platform is new. RiskLab is forward-looking. What happens when you scale to 100 million? Or 500 million?"
clips[20-why-now]="Good parameters today. Good parameters after you scale. This tool lets the team check that in seconds, not days."
clips[21-roadmap]="With more time: multi-market correlation, so you can crash BTC and ETH together. Insurance fund depletion. And alerts when live parameters drift close to the edge."
clips[22-close]="RiskLab. Built on Pacifica."

CLIP_ORDER=(01-hook 02-problem-setup 03-gap 04-who 05-intro 06-fit 07-market 08-scenario 09-parameters 10-run-hero 11-stats 12-cascade 13-funding 14-compare 15-limits 16-api-1 17-api-2 18-builder 19-who-uses 20-why-now 21-roadmap 22-close)

for clip in "${CLIP_ORDER[@]}"; do
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

  if file "$OUT" | grep -q "ASCII text\|JSON data\|XML"; then
    echo "ERROR: $clip got error response"
    rm "$OUT"
    exit 1
  fi

  echo "$clip OK ($(wc -c < "$OUT") bytes)"
done

echo "All audio clips generated."
