#!/usr/bin/env python3
"""Asset per il reskin acid/2026: dither 1-bit colorato + gradienti retinati Bayer."""
import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
LIME = (200, 255, 0)

BAYER8 = [
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]

def still(src, dst, width, ratio, contrast=2.4, brightness=0.95):
    """Dither 1-bit -> pixel accesi in lime su trasparente (si posa su qualsiasi fondo)."""
    img = Image.open(src).convert("L")
    w, h = img.size
    th = w / ratio
    if th <= h:
        top = (h - th) / 2
        img = img.crop((0, int(top), w, int(top + th)))
    else:
        tw = h * ratio
        left = (w - tw) / 2
        img = img.crop((int(left), 0, int(left + tw), h))
    img = img.resize((width, int(width / ratio)), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(0.35))
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageOps.autocontrast(img, cutoff=2)
    bw = img.convert("1")
    out = Image.new("RGBA", bw.size, (0, 0, 0, 0))
    px, src_px = out.load(), bw.load()
    for y in range(bw.size[1]):
        for x in range(bw.size[0]):
            if src_px[x, y]:
                px[x, y] = LIME + (255,)
    out.save(dst, optimize=True)
    return os.path.getsize(dst)

def dither_gradient(dst, w, h, c1, c2, vertical=False, levels=5):
    """Gradiente Bayer-ditherato tra due colori: la sfumatura si rompe in retino."""
    out = Image.new("RGB", (w, h))
    px = out.load()
    for y in range(h):
        for x in range(w):
            t = (y / h) if vertical else (x / w)
            thr = BAYER8[y % 8][x % 8] / 64.0
            q = min(levels - 1, int(t * levels + thr))  # quantizzazione con soglia ordinata
            f = q / (levels - 1)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * f) for i in range(3))
    out.save(dst, optimize=True)
    return os.path.getsize(dst)

def dither_glow(dst, size, color, levels=6):
    """Bagliore radiale ditherato su trasparente: sfondo 'digitale', non fotocopiato."""
    import math
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = out.load()
    c = size / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / c
            t = max(0.0, 1.0 - d)
            t = t * t
            thr = BAYER8[y % 8][x % 8] / 64.0
            q = int(t * levels + thr)
            if q > 0:
                px[x, y] = color + (min(255, int(q / levels * 255)),)
    out.save(dst, optimize=True)
    return os.path.getsize(dst)

jobs = [
    ("pUZReV7YXJM.jpg", "acid-streaming.png", 780, 16/9, 2.5, 0.92),
    ("zPLSSsIgv8I.jpg", "acid-show4health.png", 780, 16/9, 2.3, 0.94),
    ("A0UDOirbuhE.jpg", "acid-hifibasics.png", 780, 16/9, 2.4, 0.96),
]
for src, dst, w, r, c, b in jobs:
    print(f"{dst}: {still(os.path.join(BASE, src), os.path.join(BASE, dst), w, r, c, b)/1024:.1f} KB")

# piccoli + pochi livelli: ingranditi in pagina con image-rendering:pixelated il retino resta grosso
print(f"grad-text.png: {dither_gradient(os.path.join(BASE,'grad-text.png'), 260, 60, (200,255,0), (255,46,154), levels=4)/1024:.1f} KB")
print(f"grad-bar.png: {dither_gradient(os.path.join(BASE,'grad-bar.png'), 300, 10, (43,92,255), (200,255,0), levels=4)/1024:.1f} KB")
print(f"glow.png: {dither_glow(os.path.join(BASE,'glow.png'), 150, (200,255,0), levels=4)/1024:.1f} KB")
print(f"glow2.png: {dither_glow(os.path.join(BASE,'glow2.png'), 150, (255,46,154), levels=4)/1024:.1f} KB")
