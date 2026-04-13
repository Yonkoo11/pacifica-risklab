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
    "01-hero": "Survival score: 3.9 out of 10. Critical.\n612 positions liquidated in a single crash.",
    "02-markets": "Pacifica offers up to 50x leverage across 63 markets.\nBut nobody's tested what happens to these parameters during a real crash.",
    "03-scenarios": "Gauntlet charges one point six million dollars a year\nfor this kind of stress testing. There's no open source alternative.",
    "04-fullapp": "RiskLab pulls live parameters from Pacifica's API.\nPick a market. Pick a historical crash. Set your hypothetical open interest. Hit run.",
    "05-cascade": "The engine generates a thousand synthetic positions,\nthen replays the crash minute by minute.\nEach liquidation hits the price. That's the cascade.",
    "06-compare": "Compare mode shows the impact of changing parameters.\nDrop leverage from 50x to 20x. 224 fewer liquidations.\nSurvival jumps from critical to stable.",
    "07-close": "RiskLab. Self-serve parameter stress testing.\nBuilt on Pacifica.",
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
