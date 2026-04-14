#!/usr/bin/env python3
"""Composite subtitle text onto frame images."""

from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

FRAMES_DIR = os.path.join(os.path.dirname(__file__), "frames")
COMPOSITES_DIR = os.path.join(os.path.dirname(__file__), "composites")
os.makedirs(COMPOSITES_DIR, exist_ok=True)

# Same text as audio clips (verbatim)
clips = {
    "01-hero": "3.9 out of 10. That's how Pacifica's BTC market scores\nwhen you replay the October crash at $100M open interest.",
    "02-markets": "Pacifica lets you trade with up to 50x leverage.\n63 markets, all live. But what happens to those settings\nwhen the market drops 15% in an hour?",
    "03-scenarios": "Right now, the only people who can answer that question\ncharge $1.6M a year. That's what Gauntlet costs.\nThere's nothing else.",
    "04-fullapp": "So we built RiskLab. It connects to Pacifica's API,\npulls the live parameters, and stress-tests them\nagainst real historical crashes.",
    "05-cascade": "Under the hood, it generates 1,000 synthetic positions\nand replays the crash minute by minute.\nLiquidations push the price down. That's the cascade.",
    "06-compare": "Turn on compare mode. Drop leverage from 50x to 20x.\n224 fewer liquidations.\nThe score jumps from critical to stable.",
    "07-close": "RiskLab. Self-serve stress testing\nfor perp parameters. Built on Pacifica.",
}

# Find a suitable font
font_candidates = [
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNSText.ttf",
    "/Library/Fonts/Arial.ttf",
]

font_path = None
for f in font_candidates:
    if os.path.exists(f):
        font_path = f
        break

if font_path:
    font = ImageFont.truetype(font_path, 32)
else:
    font = ImageFont.load_default()
    print("WARNING: Using default font, no system font found")

for clip_name, text in clips.items():
    frame_path = os.path.join(FRAMES_DIR, f"{clip_name}.png")
    if not os.path.exists(frame_path):
        print(f"SKIP: {frame_path} not found")
        continue

    img = Image.open(frame_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Calculate text dimensions
    lines = text.split("\n")
    line_height = 42
    padding = 20
    margin_x = 160

    # Measure max line width
    max_w = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        if w > max_w:
            max_w = w

    total_h = len(lines) * line_height
    box_w = max_w + padding * 2
    box_h = total_h + padding * 2

    # Position at bottom center
    box_x = (img.width - box_w) // 2
    box_y = img.height - box_h - 60

    # Semi-transparent black box
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=12,
        fill=(0, 0, 0, 140),
    )

    # Draw text lines centered
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        tx = box_x + (box_w - lw) // 2
        ty = box_y + padding + i * line_height
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 240))

    result = Image.alpha_composite(img, overlay)
    out_path = os.path.join(COMPOSITES_DIR, f"{clip_name}.png")
    result.convert("RGB").save(out_path)
    print(f"OK: {clip_name}")

print("All composites generated.")
