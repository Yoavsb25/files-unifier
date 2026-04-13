"""Unit tests for copy_guide_files helper in create_client_package."""
import pytest
from pathlib import Path


class TestCopyGuideFiles:
    """Tests for copy_guide_files(platform, dest_dir, project_root)."""

    def _make_guide_files(self, tmp_path: Path, platform: str) -> None:
        """Create fake guide files for the given platform."""
        guide_dir = tmp_path / "docs" / "guides" / platform
        guide_dir.mkdir(parents=True)
        for fmt in ("txt", "pdf", "html"):
            (guide_dir / f"Getting_Started.{fmt}").write_bytes(b"content")

    def test_copies_all_three_formats_for_macos(self, tmp_path):
        self._make_guide_files(tmp_path, "macos")
        dest = tmp_path / "delivery"
        dest.mkdir()

        from tools.create_client_package import copy_guide_files
        result = copy_guide_files("macos", dest, project_root=tmp_path)

        assert result is True
        for fmt in ("txt", "pdf", "html"):
            assert (dest / f"Getting_Started.{fmt}").exists()

    def test_copies_all_three_formats_for_windows(self, tmp_path):
        self._make_guide_files(tmp_path, "windows")
        dest = tmp_path / "delivery"
        dest.mkdir()

        from tools.create_client_package import copy_guide_files
        result = copy_guide_files("windows", dest, project_root=tmp_path)

        assert result is True
        for fmt in ("txt", "pdf", "html"):
            assert (dest / f"Getting_Started.{fmt}").exists()

    def test_returns_false_when_guide_files_missing(self, tmp_path):
        dest = tmp_path / "delivery"
        dest.mkdir()

        from tools.create_client_package import copy_guide_files
        result = copy_guide_files("macos", dest, project_root=tmp_path)

        assert result is False
        assert list(dest.iterdir()) == []

    def test_does_not_mix_platform_files(self, tmp_path):
        self._make_guide_files(tmp_path, "windows")
        dest = tmp_path / "delivery"
        dest.mkdir()

        from tools.create_client_package import copy_guide_files
        # Request macos but only windows files exist
        result = copy_guide_files("macos", dest, project_root=tmp_path)

        assert result is False
