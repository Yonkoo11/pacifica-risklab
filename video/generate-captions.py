#!/usr/bin/env python3
"""Composite subtitle text onto frame images."""

from PIL import Image, ImageDraw, ImageFont
import os

FRAMES_DIR = os.path.join(os.path.dirname(__file__), "frames")
COMPOSITES_DIR = os.path.join(os.path.dirname(__file__), "composites")
os.makedirs(COMPOSITES_DIR, exist_ok=True)

clips = {
    "01-hook": "3.9 out of 10. Critical.",
    "02-hook-context": "That's how Pacifica's BTC market scores\nwhen you replay the October crash at $100M open interest.",
    "03-problem": "Pacifica lets you trade with up to 50x leverage.\n63 markets, all live. But what happens when\nthe market drops 15% in an hour?",
    "04-agitation": "Right now, the only people who can answer that\ncharge $1.6M a year. That's Gauntlet.\nThere's nothing else.",
    "05-solution-intro": "So we built RiskLab. It connects to Pacifica's API\nand stress-tests live parameters against real crashes.",
    "06-walkthrough": "Pick a market. Pick a scenario. Set your OI.\nHit run. Three seconds.",
    "07-cascade": "A thousand synthetic positions get liquidated\nminute by minute. Each liquidation pushes\nthe price down. That's the cascade.",
    "08-funding": "The funding rate flips negative as OI skews.\nYou can see exactly when the stress peaks.",
    "09-compare": "Compare mode. Drop leverage from 50x to 20x.\n224 fewer liquidations.\nThe score jumps from critical to stable.",
    "10-close": "RiskLab. Self-serve stress testing\nfor perp parameters. Built on Pacifica.",
}

font_candidates = [
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]

font_path = None
for f in font_candidates:
    if os.path.exists(f):
        font_path = f
        break

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
