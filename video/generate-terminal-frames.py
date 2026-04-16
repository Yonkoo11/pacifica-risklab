#!/usr/bin/env python3
"""Generate terminal frames showing Pacifica API calls."""

from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "frames")

W, H = 1920, 1080
BG = (10, 10, 26)
TERM_BG = (26, 26, 46)
PROMPT = (245, 158, 11)
TEXT = (224, 224, 224)
COMMENT = (136, 136, 136)
OUTPUT = (160, 160, 180)
GREEN = (34, 197, 94)
BLUE = (59, 130, 246)
RED = (239, 68, 68)


def get_font(size=22):
    for p in ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf", "/System/Library/Fonts/Courier.ttc"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_sans(size=22, bold=False):
    for p in ["/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_frame(filename, lines):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Brand top-left
    draw.text((60, 50), "RiskLab", font=get_sans(32), fill=PROMPT)

    # Terminal window
    term_x, term_y = 120, 160
    term_w, term_h = W - 240, H - 280
    draw.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + term_h], radius=16, fill=TERM_BG)

    # Traffic lights
    draw.ellipse([term_x + 24, term_y + 24, term_x + 40, term_y + 40], fill=(255, 95, 86))
    draw.ellipse([term_x + 48, term_y + 24, term_x + 64, term_y + 40], fill=(255, 189, 46))
    draw.ellipse([term_x + 72, term_y + 24, term_x + 88, term_y + 40], fill=(39, 201, 63))

    # Title
    draw.text((term_x + 120, term_y + 20), "pacifica — curl", font=get_sans(20), fill=(180, 180, 200))

    # Content
    mono = get_font(24)
    x = term_x + 40
    y = term_y + 80

    for line in lines:
        if line.get("type") == "prompt":
            draw.text((x, y), "$", font=mono, fill=PROMPT)
            draw.text((x + 28, y), line["text"], font=mono, fill=TEXT)
        elif line.get("type") == "comment":
            draw.text((x, y), f"# {line['text']}", font=mono, fill=COMMENT)
        elif line.get("type") == "output":
            color = line.get("color", OUTPUT)
            draw.text((x + 20, y), line["text"], font=mono, fill=color)
        elif line.get("type") == "blank":
            pass
        y += 36

    img.save(os.path.join(OUT_DIR, filename))
    print(f"Generated {filename}")


# Frame 16: /info and /info/prices
make_frame("16-api-1.png", [
    {"type": "comment", "text": "Pull every market's specs from Pacifica"},
    {"type": "prompt", "text": "curl -s https://api.pacifica.fi/api/v1/info"},
    {"type": "blank"},
    {"type": "output", "text": "[", "color": OUTPUT},
    {"type": "output", "text": '  { "symbol": "BTC", "max_leverage": 50, "tick_size": 0.01 },', "color": GREEN},
    {"type": "output", "text": '  { "symbol": "ETH", "max_leverage": 50, "tick_size": 0.01 },', "color": GREEN},
    {"type": "output", "text": '  { "symbol": "SOL", "max_leverage": 20, "tick_size": 0.001 },', "color": GREEN},
    {"type": "output", "text": "  ...  63 markets total", "color": COMMENT},
    {"type": "output", "text": "]", "color": OUTPUT},
    {"type": "blank"},
    {"type": "comment", "text": "Live open interest, mark price, funding rate"},
    {"type": "prompt", "text": "curl -s https://api.pacifica.fi/api/v1/info/prices"},
    {"type": "blank"},
    {"type": "output", "text": '{ "symbol": "BTC", "mark": "74890.48",', "color": BLUE},
    {"type": "output", "text": '  "open_interest": "445.12",', "color": BLUE},
    {"type": "output", "text": '  "funding_rate": "0.0001989" }', "color": BLUE},
])

# Frame 17: /funding_rate/history and /book
make_frame("17-api-2.png", [
    {"type": "comment", "text": "Historical funding rates for stress baseline"},
    {"type": "prompt", "text": "curl -s https://api.pacifica.fi/api/v1/funding_rate/history?symbol=BTC"},
    {"type": "blank"},
    {"type": "output", "text": "[", "color": OUTPUT},
    {"type": "output", "text": '  { "timestamp": 1728518400000,', "color": GREEN},
    {"type": "output", "text": '    "rate": "0.000198",', "color": GREEN},
    {"type": "output", "text": '    "bid_impact": "74883.11",', "color": GREEN},
    {"type": "output", "text": '    "ask_impact": "74897.85" },', "color": GREEN},
    {"type": "output", "text": "  ...  4000 hourly records", "color": COMMENT},
    {"type": "output", "text": "]", "color": OUTPUT},
    {"type": "blank"},
    {"type": "comment", "text": "Orderbook depth for market impact model"},
    {"type": "prompt", "text": "curl -s https://api.pacifica.fi/api/v1/book?symbol=BTC"},
    {"type": "blank"},
    {"type": "output", "text": '{ "bids": [[74885, 0.32], [74880, 1.15], ...],', "color": RED},
    {"type": "output", "text": '  "asks": [[74895, 0.28], [74900, 0.94], ...] }', "color": RED},
])

print("All terminal frames generated.")
