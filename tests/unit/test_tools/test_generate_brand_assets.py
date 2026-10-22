"""Unit tests for the brand asset generator."""

from pathlib import Path

import pytest

from tools.generate_brand_assets import (
    EXPORTS,
    lockup_image,
    logo_image,
    mark_image,
    social_image,
)

ROOT = Path(__file__).resolve().parents[3]


class TestBrandImages:
    def test_logo_is_square_with_transparent_corners(self):
        img = logo_image(128)
        assert img.size == (128, 128)
        assert img.mode == "RGBA"
        # Rounded tile: corners transparent, centre opaque.
        assert img.getpixel((0, 0))[3] == 0
        assert img.getpixel((64, 64))[3] == 255

    @pytest.mark.parametrize("variant", ["gradient", "reversed", "black", "white"])
    def test_mark_variants_are_transparent(self, variant):
        img = mark_image(128, variant)
        assert img.size == (128, 128)
        assert img.getpixel((0, 0))[3] == 0

    def test_social_image_matches_platform_crop(self):
        assert social_image(1200, 630).size == (1200, 630)
        assert social_image(1280, 640).size == (1280, 640)

    def test_lockup_aspect(self):
        img = lockup_image(1300)
        assert img.width == 1300
        assert img.height == pytest.approx(320, abs=2)


class TestGeneratedExports:
    """Exports committed by running the generator (see brand/BRAND.md)."""

    @pytest.mark.parametrize(
        "rel",
        [
            "brand/logo.svg",
            "brand/mark.svg",
            "brand/mark-reversed.svg",
            "brand/BRAND.md",
            "brand/exports/icon.ico",
            "brand/exports/og-image.png",
            "brand/exports/github-social.png",
            "build_config/assets/icon.ico",
            "pdf_merger/assets/icon.png",
            "landing/assets/favicon.svg",
            "landing/assets/og-image.png",
        ],
    )
    def test_point_of_use_assets_exist(self, rel):
        assert (ROOT / rel).exists(), f"missing {rel} — run tools/generate_brand_assets.py"

    def test_exports_dir_is_canonical(self):
        assert EXPORTS.name == "exports"
        assert (EXPORTS / "logo-1024.png").exists()
