#!/usr/bin/env python3
"""Composite subtitle text onto frame images. Only for static-frame clips."""

from PIL import Image, ImageDraw, ImageFont
import os

FRAMES_DIR = os.path.join(os.path.dirname(__file__), "frames")
COMPOSITES_DIR = os.path.join(os.path.dirname(__file__), "composites")
os.makedirs(COMPOSITES_DIR, exist_ok=True)

# Only clips that use static frames (Remotion clips don't need captions - they're self-contained)
clips = {
    "02-problem-setup": "Pacifica lets you trade with up to 50x leverage.\n63 perpetuals markets. Real money every day.",
    "03-gap": "Nobody has tested what those parameters do\nin a real crash.",
    "04-who": "Protocol teams. Risk analysts. Position sizers.\nGauntlet charges $1.6M a year for this.",
    "05-intro": "Pick a market. Pick a crash. Set your OI.\nHit run. See what breaks.",
    "06-fit": "Runs on Pacifica's public API.\nNo wallet, no auth.",
    "07-market": "Every Pacifica perp.\nLive leverage and open interest.",
    "08-scenario": "Five historical scenarios from Binance candles.\nOctober 2025. LUNA. Dec '24. SVB. Synthetic 5%.",
    "09-parameters": "Three sliders.\nHypothetical OI. Leverage override. Long/short ratio.",
    "11-stats": "612 liquidated. $56M wiped. 56% of OI gone.\n2 cascade rounds.",
    "13-funding": "Funding flips negative as OI skews.\nYou see exactly when stress hits its cap.",
    "15-limits": "Model assumptions are documented.\nLinear impact. Synthetic positions. No cross-margin.",
    "16-api-1": "Market list and live prices.\nAll from Pacifica's info endpoints.",
    "17-api-2": "Funding history. Orderbook depth.\nFour endpoints, zero auth.",
    "18-builder": "No builder code for read-only analytics.\nEverything on screen flows from Pacifica.",
    "19-who-uses": "Pacifica's live BTC OI is around $450.\nWhat breaks at $100M? At $500M?",
    "20-why-now": "Good parameters now. Good parameters after you scale.\nSeconds to check, not days.",
    "21-roadmap": "Next: multi-market correlation.\nInsurance fund modeling. Live parameter alerts.",
}

font_candidates = [
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]

font_path = next((f for f in font_candidates if os.path.exists(f)), None)
font = ImageFont.truetype(font_path, 32) if font_path else ImageFont.load_default()

for clip_name, text in clips.items():
    frame_path = os.path.join(FRAMES_DIR, f"{clip_name}.png")
    if not os.path.exists(frame_path):
        print(f"SKIP: {frame_path} not found")
        continue

    img = Image.open(frame_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = text.split("\n")
    line_height = 42
    padding = 20
    max_w = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)

    total_h = len(lines) * line_height
    box_w = max_w + padding * 2
    box_h = total_h + padding * 2
    box_x = (img.width - box_w) // 2
    box_y = img.height - box_h - 60

    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=12,
        fill=(0, 0, 0, 140),
    )

    for i, line in enumerate(lines):
        lw = draw.textbbox((0, 0), line, font=font)[2]
        tx = box_x + (box_w - lw) // 2
        ty = box_y + padding + i * line_height
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 240))

    result = Image.alpha_composite(img, overlay)
    out_path = os.path.join(COMPOSITES_DIR, f"{clip_name}.png")
    result.convert("RGB").save(out_path)
    print(f"OK: {clip_name}")

print("All composites generated.")
