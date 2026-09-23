#!/usr/bin/env python3
"""
Fon rasmlarini tayyorlash skripti.

Ishlatilishi:
    python3 scripts/build_wallpapers.py <manba_rasm> <slot_raqami>

Masalan:
    python3 scripts/build_wallpapers.py ~/Downloads/beach.jpg 1

Skript rasmni 16:9 ga kesadi va public/wallpapers/ ichiga
4 xil o'lchamda saqlaydi: wp-01-640.jpg, wp-01-1280.jpg,
wp-01-1920.jpg, wp-01-2560.jpg

Talab: pip install pillow
Tavsiya: manba rasm kamida 1920px kenglikda bo'lsin (16:9 kesilgandan keyin).
"""

import sys
import os
from PIL import Image, ImageFilter

WIDTHS = [640, 1280, 1920, 2560]
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'public', 'wallpapers')
TARGET_RATIO = 16 / 9


def crop_16x9(im, vertical_focus=0.40):
    """Markazdan 16:9 kesadi. vertical_focus: 0 = tepa, 1 = past."""
    w, h = im.size
    if w / h > TARGET_RATIO:
        nw = int(h * TARGET_RATIO)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = int(w / TARGET_RATIO)
    top = int((h - nh) * vertical_focus)
    return im.crop((0, top, w, top + nh))


def resize_to(im, width):
    """Kichraytirish — to'g'ridan-to'g'ri Lanczos (sifat yo'qolmaydi).
    Kattalashtirish — bosqichma-bosqich + yengil unsharp."""
    height = round(width * 9 / 16)
    if im.width >= width:
        return im.resize((width, height), Image.LANCZOS)

    out = im
    while out.width * 2 <= width:
        out = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
        out = out.filter(ImageFilter.UnsharpMask(radius=1.3, percent=50, threshold=4))
    return out.resize((width, height), Image.LANCZOS)


def build(src_path, slot):
    im = Image.open(src_path).convert('RGB')
    src_w = im.size[0]
    im = crop_16x9(im)

    os.makedirs(OUT_DIR, exist_ok=True)
    for w in WIDTHS:
        out = resize_to(im, w)
        quality = 82 if w <= 640 else (88 if w <= 1280 else 90)
        path = os.path.join(OUT_DIR, f'wp-{slot:02d}-{w}.jpg')
        out.save(path, quality=quality, subsampling=0, optimize=True, progressive=True)

    usable = im.size[0]
    status = 'ajoyib' if usable >= 2560 else ('yaxshi' if usable >= 1920 else 'past')
    print(f'wp-{slot:02d}: {src_w}px manba -> 16:9 {im.size[0]}x{im.size[1]} ({status})')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1], int(sys.argv[2]))
