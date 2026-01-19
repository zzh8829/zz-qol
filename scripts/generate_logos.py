#!/usr/bin/env python3
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont
import argparse
import os
from pathlib import Path

SIZE = 512
MARGIN = 28
PACKS = {
    "qol-1-lite": ("Lite", "1", ((20, 60, 70), (10, 30, 35))),
    "qol-2-plus": ("Plus", "2", ((20, 40, 100), (10, 20, 60))),
    "qol-3-max": ("Max", "3", ((60, 30, 90), (30, 10, 50))),
    "qol-4-editor": ("Editor", "4", ((120, 90, 20), (70, 40, 10))),
}


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    # Try a few common fonts, fall back to default
    preferred = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in preferred:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def gradient_bg(colors: tuple[tuple[int, int, int], tuple[int, int, int]]) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), colors[0])
    top, bottom = colors
    draw = ImageDraw.Draw(img)
    for y in range(SIZE):
        t = y / (SIZE - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))
    return img


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def draw_header(draw: ImageDraw.ImageDraw, title: str, sub: str):
    title_font = load_font(72)
    sub_font = load_font(40)
    # Title: ZZ QOL
    w, h = _text_size(draw, title, title_font)
    x = (SIZE - w) // 2
    y = MARGIN
    # shadow
    draw.text((x + 2, y + 2), title, font=title_font, fill=(0, 0, 0, 120))
    draw.text((x, y), title, font=title_font, fill=(240, 240, 240))

    # Sub-title (level)
    w2, h2 = _text_size(draw, sub, sub_font)
    x2 = (SIZE - w2) // 2
    y2 = y + h + 6
    draw.text((x2 + 1, y2 + 1), sub, font=sub_font, fill=(0, 0, 0, 120))
    draw.text((x2, y2), sub, font=sub_font, fill=(230, 230, 230))


def draw_badge(draw: ImageDraw.ImageDraw, text: str, color: tuple[int, int, int]):
    # Corner badge with a number or symbol
    pad = 12
    radius = 16
    badge_w, badge_h = 88, 52
    x0, y0 = SIZE - badge_w - pad, pad
    x1, y1 = SIZE - pad, pad + badge_h
    # rounded rect
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=color)
    font = load_font(36)
    tw, th = _text_size(draw, text, font)
    tx = x0 + (badge_w - tw) // 2
    ty = y0 + (badge_h - th) // 2 - 2
    draw.text((tx, ty), text, font=font, fill=(10, 10, 10))


def overlay_lite(draw: ImageDraw.ImageDraw):
    # Simple monitor with a bar chart
    x, y, w, h = 90, 200, 332, 190
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=(230, 230, 230), width=4, fill=(20, 30, 35, 50))
    # bars
    bx = x + 30
    for i, bh in enumerate([40, 80, 120, 90, 140]):
        draw.rectangle([bx + i * 55, y + h - 20 - bh, bx + i * 55 + 30, y + h - 20], fill=(140, 220, 220))
    # stand
    draw.rectangle([x + w // 2 - 30, y + h + 10, x + w // 2 + 30, y + h + 28], fill=(200, 200, 200))


def overlay_plus(draw: ImageDraw.ImageDraw):
    # Mosaic of plus symbols
    font = load_font(60)
    cols = 4
    rows = 3
    start_x, start_y = 80, 220
    step_x, step_y = 100, 86
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * step_x
            y = start_y + r * step_y
            draw.text((x + 2, y + 2), "+", font=font, fill=(0, 0, 0, 100))
            draw.text((x, y), "+", font=font, fill=(220, 240, 255))


def overlay_max(draw: ImageDraw.ImageDraw):
    # Lightning bolt over blueprint grid
    # Grid
    for i in range(0, SIZE, 24):
        draw.line([(i, 170), (i, SIZE - 60)], fill=(70, 90, 140))
    for j in range(170, SIZE - 60, 24):
        draw.line([(50, j), (SIZE - 50, j)], fill=(70, 90, 140))
    # Bolt polygon
    bolt = [(220, 190), (340, 190), (270, 300), (360, 300), (180, 480), (240, 340), (150, 340)]
    draw.polygon(bolt, fill=(255, 230, 120), outline=(60, 50, 10))


def overlay_editor(draw: ImageDraw.ImageDraw):
    # Crown + water drop to signal creator/waterfill
    # Crown
    base_y = 340
    crown = [(120, base_y), (180, 240), (240, 340), (300, 240), (360, 340), (420, 240), (440, base_y)]
    draw.polygon(crown, fill=(255, 210, 110), outline=(80, 60, 10))
    draw.rectangle([120, base_y, 440, base_y + 24], fill=(255, 210, 110), outline=(80, 60, 10))
    # Water drop
    drop = [(310, 250), (340, 210), (370, 250), (360, 300), (340, 320), (320, 300)]
    draw.polygon(drop, fill=(120, 200, 255), outline=(20, 60, 90))


def make_logo(level: str, number: str, colors: tuple[tuple[int, int, int], tuple[int, int, int]], out_path: str):
    img = gradient_bg(colors)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "ZZ QOL", level)
    draw_badge(draw, number, (255, 255, 255))

    if level.lower() == "lite":
        overlay_lite(draw)
    elif level.lower() == "plus":
        overlay_plus(draw)
    elif level.lower() == "max":
        overlay_max(draw)
    else:
        overlay_editor(draw)

    img.save(out_path, format="PNG")
    return out_path


def resolve_pack(path: Path) -> tuple[str, str, tuple[tuple[int, int, int], tuple[int, int, int]]]:
    folder = path.name
    if folder not in PACKS:
        raise SystemExit(f"Unknown pack folder {folder!r}; expected one of: {', '.join(sorted(PACKS))}")
    label, num, colors = PACKS[folder]
    return label, num, colors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a pack thumbnail for one mod folder")
    ap.add_argument("--path", default=".", help="Path to a mod folder containing info.json")
    args = ap.parse_args(argv)

    mod_dir = Path(args.path).resolve()
    info_path = mod_dir / "info.json"
    if not info_path.exists():
        raise SystemExit(f"Missing info.json in {mod_dir}")

    label, num, colors = resolve_pack(mod_dir)
    os.makedirs(mod_dir, exist_ok=True)
    out_path = mod_dir / "thumbnail.png"
    make_logo(label, num, colors, str(out_path))
    print(f"Generated {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
