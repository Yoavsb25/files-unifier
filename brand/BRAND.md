# Unifier — Brand Guide

The single source of truth for the Unifier brand. Masters live in this
folder as SVG; every raster asset in the product, on the web, and in
customer documents is generated from them. Never edit an export by hand.

## Naming

| Level | Name | Use |
|---|---|---|
| Company | **Unifier** | Nav, footer, legal, "by Unifier" |
| Product | **Files Unifier** | The desktop app, guides, reports, sales |
| Tagline | **Many files. One document.** | Always with the product or lockup, never alone as a headline substitute |

The shipped binary is `Files Unifier.app` / `Files Unifier.exe`, and
delivery packages are prefixed `Files_Unifier_`. Internal identifiers
that predate the brand (the macOS bundle ID `com.pdfmerger.batch`, the
`~/.pdf_merger/` config/license directory, the `pdf_merger` Python
package) are intentionally unchanged — renaming them would orphan
existing customers' licences and settings.

## Assets

Masters (edit these):

- `logo.svg` — app-icon artwork: gradient tile + white U. The primary mark.
- `mark.svg` — U only, gradient, transparent. For light backgrounds.
- `mark-reversed.svg` / `mark-mono-white.svg` — white U for dark backgrounds.
- `mark-mono-black.svg` — single-colour U for print and reports.
- `lockup-horizontal.svg` — tile + "Unifier" + tagline (primary lockup).
- `lockup-horizontal-reversed.svg` — lockup for navy/dark backgrounds.
- `lockup-stacked.svg` — centred lockup for square placements.
- `wordmark.svg` — "Unifier" text only.

Exports (generated, in `exports/`): app icons (`icon.icns`, `icon.ico`,
`logo-1024.png`), favicons, `og-image.png` (1200×630), `github-social.png`
(1280×640), lockup PNGs at 1x/2x, and a `contact-sheet.png` preview.

Regenerate everything after touching a master:

```bash
python tools/generate_brand_assets.py --contact-sheet
```

The script also syncs copies to `build_config/assets/` (PyInstaller),
`pdf_merger/assets/` (runtime window/sidebar icon), and `landing/assets/`
(favicons, social images). Commit masters, script output, and synced
copies together.

## Colour

| Token | Hex | Use |
|---|---|---|
| Gradient start | `#4338CA` | Logo tile, top-left |
| Gradient end | `#0EA5E9` | Logo tile, bottom-right |
| Navy | `#0F1B3D` | Headlines, nav, dark sections |
| Primary blue | `#2563EB` | Buttons, links, accents |
| Cream | `#F8F6F1` | Banner / social background |
| Slate | `#64748B` | Secondary text, tagline in lockups |
| App background | `#F0F4FF` | Desktop app background |
| Card border | `#C7D7F5` | Desktop app cards/inputs |

The gradient runs diagonally, top-left `#4338CA` to bottom-right
`#0EA5E9`. It is part of the artwork — never recolour, reverse, or flatten
it to a single colour except in the mono variants.

## Typography

- **Inter** for web and documents (weights 500/700/800), falling back to
  Helvetica Neue / Arial / system sans.
- Product name set in 800 weight, tight letter-spacing (-0.02em).
- Tagline in 500 weight, slate on light backgrounds, `#CBD5E1` on navy.

## Clearspace and minimum size

- Clearspace around the logo/lockup: at least the height of the U's left
  stem (roughly ¼ of the tile) on all sides. Nothing enters it — no text,
  edges, or other logos.
- Minimum sizes: tile logo 16px (favicon), mark 16px, horizontal lockup
  120px wide. Below that, use the tile alone.
- The U must stay legible: if the translucent left stem disappears at
  small sizes, the size is too small.

## Which variant where

| Surface | Asset |
|---|---|
| App icon (macOS/Windows) | `icon.icns` / `icon.ico` (tile) |
| App window + sidebar | `pdf_merger/assets/icon.png` (tile) |
| Website nav/footer (navy) | `logo.svg` tile (self-contained on dark) |
| Favicon | `favicon.svg`, PNG/ICO fallbacks |
| Link shares (LinkedIn/X) | `og-image.png` 1200×630, absolute URL |
| GitHub repo social preview | `github-social.png` 1280×640 (upload in repo Settings) |
| Wide banner placements | `landing/assets/banner.png` |
| PDF/print, single colour | `mark-mono-black.svg` |
| Merge reports (text) | "Files Unifier — Many files. One document." header |

## Do and don't

Do:
- Use the reversed/white variant on navy and photography.
- Keep the tagline with the lockup in customer-facing documents.
- Regenerate exports with the script and check `contact-sheet.png`.

Don't:
- Stretch, crop, rotate, or add shadows/outlines to the mark.
- Recolour the gradient or set the white U in another colour.
- Place the gradient mark (`mark.svg`) on navy — the tile or reversed
  variant belongs there.
- Typeset "Unifier" in a different font as a substitute logo.
- Use the old names ("PDF Batch Merger", "Files Unifeder") in copy.
