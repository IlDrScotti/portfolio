#!/usr/bin/env python3
"""Ditherizza gli asset del portfolio in 1-bit stile fotocopia + texture di supporto."""
import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))

def xerox(src, dst, width, ratio, contrast=2.1, brightness=1.06, blur=0.4):
    """Grayscale -> contrasto spinto -> micro blur (ottica dello scanner) -> FS dither 1-bit."""
    img = Image.open(src).convert("L")
    # crop centrale al rapporto voluto
    w, h = img.size
    target_h = w / ratio
    if target_h <= h:
        top = (h - target_h) / 2
        img = img.crop((0, int(top), w, int(top + target_h)))
    else:
        target_w = h * ratio
        left = (w - target_w) / 2
        img = img.crop((int(left), 0, int(left + target_w), h))
    img = img.resize((width, int(width / ratio)), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(blur))
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.convert("1")  # Floyd-Steinberg di default in Pillow
    img.save(dst, optimize=True, bits=1)
    return os.path.getsize(dst)

# --- still dei progetti (16:9) ---
jobs = [
    ("pUZReV7YXJM.jpg", "still-streaming.png", 760, 16/9, 2.6, 0.80),
    ("zPLSSsIgv8I.jpg", "still-show4health.png", 760, 16/9, 2.4, 0.82),
    ("A0UDOirbuhE.jpg", "still-hifibasics.png", 760, 16/9, 2.5, 0.84),
    ("omnilan-social-web.mp4.png", "still-omnilan.png", 420, 9/16, 2.5, 0.86),
    ("reel-mr1mk3-web.mp4.png", "still-mr1mk3.png", 420, 9/16, 2.5, 0.86),
]
for src, dst, w, r, c, b in jobs:
    size = xerox(os.path.join(BASE, src), os.path.join(BASE, dst), w, r, c, b)
    print(f"{dst}: {size/1024:.1f} KB")

# --- tile Bayer 8x8 per l'overlay dei video (dither live in CSS) ---
BAYER8 = [
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]
tile = Image.new("L", (8, 8))
tile.putdata([int(BAYER8[y][x] / 63 * 255) for y in range(8) for x in range(8)])
tile.save(os.path.join(BASE, "bayer8.png"))
print("bayer8.png: tile 8x8")

# --- texture sporco/toner: puntini casuali su trasparente ---
import random
random.seed(11)
W = H = 380
dirt = Image.new("LA", (W, H), (0, 0))
px = dirt.load()
for _ in range(2600):
    x, y = random.randrange(W), random.randrange(H)
    a = random.choice([40, 60, 90, 130, 200])
    px[x, y] = (0, a)
for _ in range(120):  # granelli piu' grossi
    x, y = random.randrange(W - 2), random.randrange(H - 2)
    for dx in range(2):
        for dy in range(2):
            px[x + dx, y + dy] = (0, random.randrange(90, 220))
dirt.save(os.path.join(BASE, "dirt.png"), optimize=True)
print("dirt.png: texture sporco")
