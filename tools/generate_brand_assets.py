#!/usr/bin/env python3
"""Generate every brand derivative from the masters in ``brand/``.

The canonical artwork is the SVG set in ``brand/`` (see ``brand/BRAND.md``).
This script rasterises the same geometry with Pillow (supersampled, so no
SVG rasteriser or extra dependency is needed), then copies each export to
its point of use:

- ``brand/exports/``          canonical exports
- ``build_config/assets/``    PyInstaller app icons (.icns / .ico)
- ``pdf_merger/assets/``      runtime window / sidebar icon
- ``landing/assets/``         favicons, touch icon, social images, logo

Usage:
    python tools/generate_brand_assets.py [--contact-sheet]

Regenerate after any change to the artwork and commit the results.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
EXPORTS = BRAND / "exports"

# Palette (brand/BRAND.md)
INDIGO = (67, 56, 202)       # #4338CA
SKY = (14, 165, 233)         # #0EA5E9
NAVY = (15, 27, 61)          # #0F1B3D
PRIMARY = (37, 99, 235)      # #2563EB
CREAM = (248, 246, 241)      # banner background
SLATE = (100, 116, 139)      # #64748B
WHITE = (255, 255, 255)

SS = 4  # supersample factor for anti-aliasing

# U geometry on a 1200 grid (mirrors brand/logo.svg)
STEM_L, STEM_R = 370, 830
TOP, SHOULDER, BOWL_Y = 375, 548, 660
STROKE = 150


def _gradient(size: int) -> Image.Image:
    """Diagonal indigo -> sky gradient."""
    small = 256
    img = Image.new("RGB", (small, small))
    px = img.load()
    for y in range(small):
        for x in range(small):
            t = (x + y) / (2 * (small - 1))
            px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(INDIGO, SKY))
    return img.resize((size, size), Image.BICUBIC)


def _draw_u(draw: ImageDraw.ImageDraw, scale: float, colour, light_opacity: float) -> None:
    """Draw the U (translucent upper left stem + solid body) at `scale`."""

    def s(v: float) -> float:
        return v * scale

    w = s(STROKE)
    # Solid body first: right stem, bowl, left stem up to the shoulder.
    draw.line([s(STEM_R), s(TOP), s(STEM_R), s(BOWL_Y)], fill=colour, width=int(w))
    draw.line([s(STEM_L), s(SHOULDER), s(STEM_L), s(BOWL_Y)], fill=colour, width=int(w))
    # Pillow draws an arc inside its bbox (the stroke extends inward), so
    # expand the bbox by half the stroke to land the centreline on the
    # same semicircle the SVG stroke follows.
    radius = (STEM_R - STEM_L) / 2
    half = STROKE / 2
    draw.arc(
        [s(STEM_L - half), s(BOWL_Y - radius - half),
         s(STEM_R + half), s(BOWL_Y + radius + half)],
        start=0, end=180, fill=colour, width=int(w),
    )
    for cx, cy in ((STEM_L, TOP), (STEM_R, TOP)):
        r = w / 2
        draw.ellipse([s(cx) - r, s(cy) - r, s(cx) + r, s(cy) + r], fill=colour)
    # Translucent upper left stem on its own layer so opacity composes.
    return w


def _u_overlay(size_px: int, colour, light_opacity: int) -> Image.Image:
    """U artwork on transparency, rendered at size_px (already supersampled)."""
    scale = size_px / 1200
    base = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    rgba = colour + (255,) if len(colour) == 3 else colour
    _draw_u(draw, scale, rgba, light_opacity)
    # Light segment: redraw over the top of the left stem with alpha.
    light = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    w = STROKE * scale
    ld.line([STEM_L * scale, TOP * scale, STEM_L * scale, SHOULDER * scale],
            fill=rgba[:3] + (light_opacity,), width=int(w))
    r = w / 2
    ld.ellipse([STEM_L * scale - r, TOP * scale - r, STEM_L * scale + r, TOP * scale + r],
               fill=rgba[:3] + (light_opacity,))
    return Image.alpha_composite(base, light)


def logo_image(px: int) -> Image.Image:
    """Rounded gradient tile + white U (the app-icon artwork)."""
    size = px * SS
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    tile = _gradient(size)
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    r = 264 * size / 1200
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    img.paste(tile, (0, 0), mask)
    img = Image.alpha_composite(img, _u_overlay(size, WHITE, 140))
    return img.resize((px, px), Image.LANCZOS)


def mark_image(px: int, variant: str) -> Image.Image:
    """U only, on transparency. variant: gradient | reversed | black | white."""
    size = px * SS
    if variant == "gradient":
        grad = _gradient(size).convert("RGBA")
        # Use the U as a mask over the gradient; keep the light segment lighter.
        solid = _u_overlay(size, WHITE, 115)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.paste(grad, (0, 0), solid)
        img = out
    elif variant == "reversed" or variant == "white":
        img = _u_overlay(size, WHITE, 140)
    elif variant == "black":
        img = _u_overlay(size, (0, 0, 0), 115)
    else:  # pragma: no cover
        raise ValueError(variant)
    return img.resize((px, px), Image.LANCZOS)


_FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]
_FONT_CANDIDATES_REG = [
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]


def _font(candidates, size: int) -> ImageFont.FreeTypeFont:
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def lockup_image(width_px: int, reversed_: bool = False) -> Image.Image:
    """Horizontal lockup: tile + 'Unifier' + tagline, transparent background."""
    scale = width_px / 2600
    height = int(640 * scale)
    img = Image.new("RGBA", (width_px, height), (0, 0, 0, 0))
    icon = logo_image(int(600 * scale))
    img.alpha_composite(icon, (int(20 * scale), int(20 * scale)))
    draw = ImageDraw.Draw(img)
    name_fill = WHITE + (255,) if reversed_ else NAVY + (255,)
    tag_fill = (203, 213, 225, 255) if reversed_ else SLATE + (255,)
    draw.text((700 * scale, 130 * scale), "Unifier",
              font=_font(_FONT_CANDIDATES_BOLD, int(215 * scale)), fill=name_fill)
    draw.text((706 * scale, 385 * scale), "Many files. One document.",
              font=_font(_FONT_CANDIDATES_REG, int(96 * scale)), fill=tag_fill)
    return img


def stacked_image(width_px: int) -> Image.Image:
    ratio = 1560 / 1400
    img = Image.new("RGBA", (width_px, int(width_px * ratio)), (0, 0, 0, 0))
    scale = width_px / 1400
    icon = logo_image(int(600 * scale))
    img.alpha_composite(icon, (int(400 * scale), int(20 * scale)))
    draw = ImageDraw.Draw(img)
    f_name = _font(_FONT_CANDIDATES_BOLD, int(215 * scale))
    f_tag = _font(_FONT_CANDIDATES_REG, int(96 * scale))
    draw.text((width_px / 2, 700 * scale), "Unifier", font=f_name,
              fill=NAVY + (255,), anchor="ma")
    draw.text((width_px / 2, 975 * scale), "Many files. One document.", font=f_tag,
              fill=SLATE + (255,), anchor="ma")
    return img


def social_image(w: int, h: int) -> Image.Image:
    """Share image at the exact crop platforms use: lockup on cream + rings."""
    img = Image.new("RGB", (w, h), CREAM)
    draw = ImageDraw.Draw(img)
    # Decorative concentric rings, top-right (echoes the banner artwork).
    cx, cy = int(w * 1.02), int(-h * 0.25)
    for i, r in enumerate((int(h * 0.95), int(h * 0.72), int(h * 0.5))):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=(165, 200, 240) if i % 2 == 0 else (140, 185, 235),
                     width=max(6, h // 60))
    lock = lockup_image(int(w * 0.62))
    img.paste(lock, (int(w * 0.07), (h - lock.height) // 2 - int(h * 0.06)), lock)
    draw = ImageDraw.Draw(img)
    sub = _font(_FONT_CANDIDATES_REG, int(h * 0.052))
    draw.text((int(w * 0.075), int(h * 0.80)),
              "Files Unifier — document assembly for operations teams",
              font=sub, fill=SLATE)
    return img


def _save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(f"  {path.relative_to(ROOT)}  ({img.width}x{img.height})")


def _make_icns(png1024: Path, dest: Path) -> bool:
    """Build .icns via iconutil (macOS) with a Pillow fallback."""
    if sys.platform == "darwin" and shutil.which("iconutil"):
        iconset = EXPORTS / "icon.iconset"
        if iconset.exists():
            shutil.rmtree(iconset)
        iconset.mkdir(parents=True)
        base = Image.open(png1024)
        for pts, name in [(16, "icon_16x16"), (32, "icon_16x16@2x"), (32, "icon_32x32"),
                          (64, "icon_32x32@2x"), (128, "icon_128x128"), (256, "icon_128x128@2x"),
                          (256, "icon_256x256"), (512, "icon_256x256@2x"),
                          (512, "icon_512x512"), (1024, "icon_512x512@2x")]:
            base.resize((pts, pts), Image.LANCZOS).save(iconset / f"{name}.png")
        result = subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(dest)])
        shutil.rmtree(iconset, ignore_errors=True)
        if result.returncode == 0 and dest.exists():
            return True
    try:
        Image.open(png1024).save(dest, format="ICNS")
        return True
    except Exception as exc:  # pragma: no cover
        print(f"  warning: could not build {dest.name}: {exc}")
        return False


def _contact_sheet(paths: list[Path], dest: Path) -> None:
    thumbs: list[Image.Image] = []
    for p in paths:
        if p.suffix.lower() != ".png" or not p.exists():
            continue
        im = Image.open(p).convert("RGBA")
        im.thumbnail((360, 240))
        thumbs.append((p.name, im))
    cols = 4
    cw, ch = 380, 280
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (240, 244, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * cw, (i // cols) * ch
        # Reversed / white artwork needs a dark cell to be visible.
        dark = "reversed" in name or "white" in name
        if dark:
            draw.rectangle([x, y, x + cw - 1, y + ch - 1], fill=NAVY + (255,))
        sheet.alpha_composite(im, (x + (cw - im.width) // 2, y + 8))
        draw.text((x + 10, y + ch - 28), name, font=_font(_FONT_CANDIDATES_REG, 20),
                  fill=WHITE if dark else (60, 60, 60))
    sheet.convert("RGB").save(dest)
    print(f"  {dest.relative_to(ROOT)}  ({sheet.width}x{sheet.height})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contact-sheet", action="store_true",
                        help="also render brand/exports/contact-sheet.png")
    args = parser.parse_args()

    EXPORTS.mkdir(parents=True, exist_ok=True)
    print("Generating brand assets...")

    logo1024 = EXPORTS / "logo-1024.png"
    _save(logo_image(1024), logo1024)
    _save(logo_image(512), EXPORTS / "logo-512.png")
    _save(mark_image(1024, "gradient"), EXPORTS / "mark-1024.png")
    _save(mark_image(1024, "reversed"), EXPORTS / "mark-reversed-1024.png")
    _save(mark_image(1024, "black"), EXPORTS / "mark-mono-black-1024.png")
    _save(mark_image(1024, "white"), EXPORTS / "mark-mono-white-1024.png")

    _save(lockup_image(2600), EXPORTS / "lockup-horizontal.png")
    _save(lockup_image(5200), EXPORTS / "lockup-horizontal@2x.png")
    _save(lockup_image(2600, reversed_=True), EXPORTS / "lockup-horizontal-reversed.png")
    _save(stacked_image(1400), EXPORTS / "lockup-stacked.png")

    og = EXPORTS / "og-image.png"
    _save(social_image(1200, 630), og)
    _save(social_image(1280, 640), EXPORTS / "github-social.png")

    # Favicons
    _save(logo_image(32), EXPORTS / "favicon-32.png")
    _save(logo_image(16), EXPORTS / "favicon-16.png")
    _save(logo_image(180), EXPORTS / "apple-touch-icon.png")
    ico_sizes = [(s, s) for s in (16, 20, 24, 32, 48, 64, 128, 256)]
    logo_image(256).save(EXPORTS / "favicon.ico", format="ICO", sizes=ico_sizes)
    print(f"  brand/exports/favicon.ico  {ico_sizes}")
    logo_image(256).save(EXPORTS / "icon.ico", format="ICO", sizes=ico_sizes)
    _make_icns(logo1024, EXPORTS / "icon.icns")

    # SVG masters travel with the exports for web use.
    for name in ("logo.svg", "mark.svg", "mark-reversed.svg",
                 "lockup-horizontal.svg", "lockup-horizontal-reversed.svg"):
        shutil.copy2(BRAND / name, EXPORTS / name)
    (EXPORTS / "favicon.svg").write_text((BRAND / "logo.svg").read_text())

    # ---- points of use -------------------------------------------------
    assets_cfg = ROOT / "build_config" / "assets"
    assets_cfg.mkdir(parents=True, exist_ok=True)
    shutil.copy2(EXPORTS / "icon.icns", assets_cfg / "icon.icns")
    shutil.copy2(EXPORTS / "icon.ico", assets_cfg / "icon.ico")
    shutil.copy2(logo1024, assets_cfg / "icon-1024.png")

    app_assets = ROOT / "pdf_merger" / "assets"
    app_assets.mkdir(parents=True, exist_ok=True)
    _save(logo_image(256), app_assets / "icon.png")

    landing_assets = ROOT / "landing" / "assets"
    landing_assets.mkdir(parents=True, exist_ok=True)
    for src, dst in [
        ("favicon.ico", "favicon.ico"), ("favicon-16.png", "favicon-16.png"),
        ("favicon-32.png", "favicon-32.png"), ("favicon.svg", "favicon.svg"),
        ("apple-touch-icon.png", "apple-touch-icon.png"),
        ("og-image.png", "og-image.png"), ("logo.svg", "logo.svg"),
        ("logo-512.png", "logo.png"),
    ]:
        shutil.copy2(EXPORTS / src, landing_assets / dst)
    print("  copied exports -> build_config/assets/, pdf_merger/assets/, landing/assets/")

    if args.contact_sheet:
        _contact_sheet(
            [p for p in sorted(EXPORTS.glob("*.png")) if p.name != "contact-sheet.png"],
            EXPORTS / "contact-sheet.png",
        )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
