#!/usr/bin/env python3
"""Terminal frame for clip 06: public API, no wallet, no auth."""

from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "frames")
W, H = 1920, 1080
BG = (10, 10, 26)
TERM_BG = (26, 26, 46)
PROMPT = (245, 158, 11)
TEXT = (224, 224, 224)
COMMENT = (136, 136, 136)
GREEN = (34, 197, 94)
BLUE = (59, 130, 246)


def get_font(size=22):
    for p in ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_sans(size=22):
    for p in ["/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# Brand
draw.text((60, 50), "RiskLab", font=get_sans(32), fill=PROMPT)

# Terminal
term_x, term_y = 120, 180
term_w, term_h = W - 240, H - 300
draw.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + term_h], radius=16, fill=TERM_BG)

# Traffic lights
for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
    draw.ellipse([term_x + 24 + i * 24, term_y + 24, term_x + 40 + i * 24, term_y + 40], fill=color)

draw.text((term_x + 120, term_y + 20), "pacifica — curl", font=get_sans(20), fill=(180, 180, 200))

mono = get_font(26)
x = term_x + 40
y = term_y + 100

lines = [
    ("comment", "No wallet. No API key. Just hit the endpoint."),
    ("blank", ""),
    ("prompt", "curl https://api.pacifica.fi/api/v1/info"),
    ("blank", ""),
    ("output", "[", BLUE),
    ("output", '  { "symbol": "BTC",  "max_leverage": 50 },', GREEN),
    ("output", '  { "symbol": "ETH",  "max_leverage": 50 },', GREEN),
    ("output", '  { "symbol": "SOL",  "max_leverage": 20 },', GREEN),
    ("output", '  { "symbol": "HYPE", "max_leverage": 10 },', GREEN),
    ("output", "  ...  63 markets total", (120, 120, 140)),
    ("output", "]", BLUE),
]

line_h = 38
for entry in lines:
    kind = entry[0]
    if kind == "comment":
        draw.text((x, y), f"# {entry[1]}", font=mono, fill=COMMENT)
    elif kind == "prompt":
        draw.text((x, y), "$", font=mono, fill=PROMPT)
        draw.text((x + 28, y), entry[1], font=mono, fill=TEXT)
    elif kind == "output":
        color = entry[2] if len(entry) > 2 else TEXT
        draw.text((x + 20, y), entry[1], font=mono, fill=color)
    y += line_h

img.save(os.path.join(OUT_DIR, "06-fit.png"))
print("Generated 06-fit.png")
