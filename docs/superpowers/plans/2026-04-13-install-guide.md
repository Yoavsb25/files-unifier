# Install Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add clear, non-technical Getting Started guides (txt + pdf + html) to the client delivery ZIP, covering Google Drive download, installation, OS security warnings, and first launch.

**Architecture:** A one-time generator script (`tools/generate_guides.py`) produces six static files under `docs/guides/{macos,windows}/`. The packaging script copies the right platform's folder into each delivery. A `copy_guide_files()` helper in `create_client_package.py` handles the copy and is unit-tested in isolation.

**Tech Stack:** Python 3, ReportLab (already a project dependency), pathlib, shutil

---

## File Map

| Action | Path |
|--------|------|
| Create | `tools/generate_guides.py` |
| Create (generated) | `docs/guides/macos/Getting_Started.txt` |
| Create (generated) | `docs/guides/macos/Getting_Started.html` |
| Create (generated) | `docs/guides/macos/Getting_Started.pdf` |
| Create (generated) | `docs/guides/windows/Getting_Started.txt` |
| Create (generated) | `docs/guides/windows/Getting_Started.html` |
| Create (generated) | `docs/guides/windows/Getting_Started.pdf` |
| Create | `tests/unit/test_tools/__init__.py` |
| Create | `tests/unit/test_tools/test_create_client_package.py` |
| Modify | `tools/create_client_package.py` — `create_delivery_package()` and new `copy_guide_files()` |

---

## Task 1: Write the guide content generator

**Files:**
- Create: `tools/generate_guides.py`

- [ ] **Step 1: Create `tools/generate_guides.py`**

```python
#!/usr/bin/env python3
"""
One-time script to generate Getting_Started guides for Windows and macOS.

Run:    python tools/generate_guides.py
Output: docs/guides/macos/ and docs/guides/windows/

Re-run after editing content to regenerate all three formats.
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

GUIDES_DIR = Path(__file__).parent.parent / "docs" / "guides"


# ---------------------------------------------------------------------------
# Content definitions
# Each item is (tag, text). Tags: title | h2 | p | li | warning | spacer
# ---------------------------------------------------------------------------

def _content_macos():
    return [
        ("title",   "Getting Started with PDF Batch Merger"),
        ("h2",      "What's in this folder"),
        ("p",       "PDF Batch Merger.app   — The application"),
        ("p",       "license.json           — Your personal license (keep it next to the app)"),
        ("p",       "Getting_Started.*      — This guide (txt, pdf, html)"),
        ("h2",      "Step 1 — Download & extract"),
        ("li",      "Open the Google Drive link you received."),
        ("li",      "Click the file name, then click the download icon (↓) in the top-right corner."),
        ("li",      "Once downloaded, double-click the ZIP file to extract it. "
                    "A new folder will appear — open it to find your files."),
        ("h2",      "Step 2 — Place your files"),
        ("li",      'Drag "PDF Batch Merger.app" to your Applications folder.'),
        ("li",      'Copy "license.json" to the same Applications folder, next to the app.'),
        ("h2",      "Step 3 — Open the app"),
        ("li",      'Open your Applications folder.'),
        ("li",      'Right-click "PDF Batch Merger.app" and choose Open.'),
        ("warning", 'You may see a message saying "Apple cannot verify the developer." '
                    "This is normal for software not sold through the App Store. "
                    "Right-click the app \u2192 click Open \u2192 click Open again in the dialog."),
        ("h2",      "Step 4 — First launch"),
        ("p",       "A green checkmark at the top means your license is active. You are ready to go."),
        ("p",       "Use the three Browse buttons to select:"),
        ("li",      "Your input file (CSV or Excel with the list of files to merge)"),
        ("li",      "The folder containing your PDF files"),
        ("li",      "The folder where merged files should be saved"),
        ("p",       'Click "Run Merge" to start.'),
        ("h2",      "Need help?"),
        ("p",       "Contact your software provider for license or technical support."),
    ]


def _content_windows():
    return [
        ("title",   "Getting Started with PDF Batch Merger"),
        ("h2",      "What's in this folder"),
        ("p",       "PDF Batch Merger.exe   — The application"),
        ("p",       "license.json           — Your personal license (keep it next to the app)"),
        ("p",       "Getting_Started.*      — This guide (txt, pdf, html)"),
        ("h2",      "Step 1 — Download & extract"),
        ("li",      "Open the Google Drive link you received."),
        ("li",      "Click the file name, then click the download icon (↓) in the top-right corner."),
        ("li",      'Once downloaded, right-click the ZIP file and choose "Extract All", '
                    "then click Extract. A new folder will appear — open it to find your files."),
        ("h2",      "Step 2 — Place your files"),
        ("li",      '"PDF Batch Merger.exe" to any folder you like '
                    "(for example, your Desktop or Documents folder)."),
        ("li",      'Copy "license.json" to the same folder as the .exe file.'),
        ("h2",      "Step 3 — Open the app"),
        ("li",      'Double-click "PDF Batch Merger.exe" to launch.'),
        ("warning", '"Windows protected your PC" may appear. '
                    'This is normal for new software. Click "More info", then click "Run anyway".'),
        ("h2",      "Step 4 — First launch"),
        ("p",       "A green checkmark at the top means your license is active. You are ready to go."),
        ("p",       "Use the three Browse buttons to select:"),
        ("li",      "Your input file (CSV or Excel with the list of files to merge)"),
        ("li",      "The folder containing your PDF files"),
        ("li",      "The folder where merged files should be saved"),
        ("p",       'Click "Run Merge" to start.'),
        ("h2",      "Need help?"),
        ("p",       "Contact your software provider for license or technical support."),
    ]


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def _to_txt(items: list) -> str:
    lines = []
    counter = 0
    for tag, text in items:
        if tag == "title":
            lines += [text, "=" * len(text), ""]
            counter = 0
        elif tag == "h2":
            lines += ["", text, "-" * len(text)]
            counter = 0
        elif tag == "p":
            lines.append(text)
        elif tag == "li":
            counter += 1
            lines.append(f"{counter}. {text}")
        elif tag == "warning":
            lines += ["", "  \u26a0  " + text, ""]
        elif tag == "spacer":
            lines.append("")
    return "\n".join(lines) + "\n"


def _to_html(items: list) -> str:
    body_parts = []
    in_ol = False
    for tag, text in items:
        if tag != "li" and in_ol:
            body_parts.append("    </ol>")
            in_ol = False
        if tag == "li" and not in_ol:
            body_parts.append("    <ol>")
            in_ol = True

        if tag == "title":
            body_parts.append(f"    <h1>{text}</h1>")
        elif tag == "h2":
            body_parts.append(f"    <h2>{text}</h2>")
        elif tag == "p":
            body_parts.append(f"    <p>{text}</p>")
        elif tag == "li":
            body_parts.append(f"      <li>{text}</li>")
        elif tag == "warning":
            body_parts.append(
                f'    <div class="warning"><strong>\u26a0</strong> {text}</div>'
            )
    if in_ol:
        body_parts.append("    </ol>")

    body = "\n".join(body_parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Getting Started \u2014 PDF Batch Merger</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      max-width: 680px; margin: 40px auto; padding: 0 20px;
      color: #333; line-height: 1.7;
    }}
    h1 {{ color: #1a1a2e; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }}
    h2 {{ color: #16213e; margin-top: 28px; }}
    ol {{ padding-left: 22px; }}
    li {{ margin: 6px 0; }}
    .warning {{
      background: #fff8dc; border-left: 4px solid #f0c040;
      padding: 12px 16px; margin: 14px 0; border-radius: 4px;
    }}
    .warning strong {{ color: #856404; margin-right: 6px; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def _to_pdf(items: list, output_path: Path) -> None:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=inch, leftMargin=inch,
        topMargin=inch, bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    warning_style = ParagraphStyle(
        "Warning",
        parent=styles["Normal"],
        backColor=colors.HexColor("#FFF8DC"),
        leftIndent=12, rightIndent=12,
        spaceBefore=8, spaceAfter=8,
    )
    story = []
    counter = 0
    for tag, text in items:
        if tag == "title":
            story.append(Paragraph(text, styles["Title"]))
            story.append(Spacer(1, 0.15 * inch))
            counter = 0
        elif tag == "h2":
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(text, styles["Heading2"]))
            counter = 0
        elif tag == "p":
            story.append(Paragraph(text, styles["Normal"]))
        elif tag == "li":
            counter += 1
            story.append(Paragraph(f"{counter}. {text}", styles["Normal"]))
        elif tag == "warning":
            story.append(Paragraph(f"<b>\u26a0</b> {text}", warning_style))
        elif tag == "spacer":
            story.append(Spacer(1, 0.1 * inch))
    doc.build(story)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def generate(platform: str) -> None:
    """Generate all three guide formats for the given platform."""
    if platform not in ("macos", "windows"):
        raise ValueError(f"Unknown platform: {platform}")

    out_dir = GUIDES_DIR / platform
    out_dir.mkdir(parents=True, exist_ok=True)

    items = _content_macos() if platform == "macos" else _content_windows()

    txt_path = out_dir / "Getting_Started.txt"
    txt_path.write_text(_to_txt(items), encoding="utf-8")
    print(f"  Written: {txt_path}")

    html_path = out_dir / "Getting_Started.html"
    html_path.write_text(_to_html(items), encoding="utf-8")
    print(f"  Written: {html_path}")

    pdf_path = out_dir / "Getting_Started.pdf"
    _to_pdf(items, pdf_path)
    print(f"  Written: {pdf_path}")


if __name__ == "__main__":
    print("Generating macOS guides...")
    generate("macos")
    print("Generating Windows guides...")
    generate("windows")
    print("Done.")
```

- [ ] **Step 2: Run the generator and verify output**

```bash
source .venv/bin/activate
python tools/generate_guides.py
```

Expected output:
```
Generating macOS guides...
  Written: docs/guides/macos/Getting_Started.txt
  Written: docs/guides/macos/Getting_Started.html
  Written: docs/guides/macos/Getting_Started.pdf
Generating Windows guides...
  Written: docs/guides/windows/Getting_Started.txt
  Written: docs/guides/windows/Getting_Started.html
  Written: docs/guides/windows/Getting_Started.pdf
Done.
```

Verify 6 files exist:
```bash
ls docs/guides/macos/ docs/guides/windows/
```

- [ ] **Step 3: Commit generator + generated files**

```bash
git add tools/generate_guides.py docs/guides/
git commit -m "feat: add Getting Started guides for macOS and Windows"
```

---

## Task 2: Write a failing test for `copy_guide_files`

**Files:**
- Create: `tests/unit/test_tools/__init__.py`
- Create: `tests/unit/test_tools/test_create_client_package.py`

- [ ] **Step 1: Create the test package init**

```bash
touch tests/unit/test_tools/__init__.py
```

- [ ] **Step 2: Write the failing tests**

Create `tests/unit/test_tools/test_create_client_package.py`:

```python
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
```

- [ ] **Step 3: Run tests — confirm they fail**

```bash
python -m pytest tests/unit/test_tools/test_create_client_package.py -v
```

Expected: `ImportError` or `TypeError` — `copy_guide_files` does not exist yet.

---

## Task 3: Add `copy_guide_files` to `create_client_package.py` and update `create_delivery_package`

**Files:**
- Modify: `tools/create_client_package.py`

- [ ] **Step 1: Add `copy_guide_files` function**

In `tools/create_client_package.py`, add this function after the existing `create_delivery_package` function (before `get_desktop_path`):

```python
def copy_guide_files(platform: str, dest_dir: Path, project_root: Path = None) -> bool:
    """Copy Getting_Started guide files for the given platform into dest_dir.

    Returns True if at least one file was copied, False if none were found.
    Accepts an optional project_root for testing with temp directories.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent
    guide_dir = project_root / "docs" / "guides" / platform
    copied = False
    for fmt in ("txt", "pdf", "html"):
        src = guide_dir / f"Getting_Started.{fmt}"
        if src.exists():
            shutil.copy2(src, dest_dir / f"Getting_Started.{fmt}")
            copied = True
        else:
            print_warning(f"Guide file not found: {src}")
    if copied:
        print_success("Getting Started guides copied")
    return copied
```

- [ ] **Step 2: Replace the `INSTALLATION_INSTRUCTIONS.txt` block in `create_delivery_package`**

Find this block in `create_delivery_package` (around line 335):

```python
    # Create installation instructions
    instructions = delivery_dir / 'INSTALLATION_INSTRUCTIONS.txt'
    with open(instructions, 'w') as f:
        f.write("PDF Batch Merger - Installation Instructions\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Company: {company}\n")
        f.write(f"Version: {APP_VERSION}\n")
        f.write(f"Platform: {platform.upper()}\n\n")
        f.write("INSTALLATION:\n")
        f.write("-" * 50 + "\n\n")
        if platform == 'macos':
            f.write("1. Copy 'PDF Batch Merger.app' to your Applications folder\n")
            f.write("2. Copy 'license.json' to the same folder as the app\n")
            f.write("   (or to ~/.pdf_merger/ directory)\n")
            f.write("3. Double-click 'PDF Batch Merger.app' to launch\n\n")
        else:
            f.write("1. Copy 'PDF Batch Merger.exe' to your desired location\n")
            f.write("2. Copy 'license.json' to the same folder as the .exe\n")
            f.write("   (or to %USERPROFILE%\\.pdf_merger\\ directory)\n")
            f.write("3. Double-click 'PDF Batch Merger.exe' to launch\n\n")
        f.write("SUPPORT:\n")
        f.write("-" * 50 + "\n")
        f.write("For technical support or license renewal, contact your software provider.\n")
    
    print_success("Installation instructions created")
```

Replace it with:

```python
    # Copy getting started guides
    copy_guide_files(platform, delivery_dir)
```

- [ ] **Step 3: Run tests — confirm they pass**

```bash
python -m pytest tests/unit/test_tools/test_create_client_package.py -v
```

Expected output:
```
tests/unit/test_tools/test_create_client_package.py::TestCopyGuideFiles::test_copies_all_three_formats_for_macos PASSED
tests/unit/test_tools/test_create_client_package.py::TestCopyGuideFiles::test_copies_all_three_formats_for_windows PASSED
tests/unit/test_tools/test_create_client_package.py::TestCopyGuideFiles::test_returns_false_when_guide_files_missing PASSED
tests/unit/test_tools/test_create_client_package.py::TestCopyGuideFiles::test_does_not_mix_platform_files PASSED
```

- [ ] **Step 4: Run the full test suite to check for regressions**

```bash
python -m pytest
```

Expected: all existing tests still pass.

- [ ] **Step 5: Commit**

```bash
git add tools/create_client_package.py tests/unit/test_tools/
git commit -m "feat: replace INSTALLATION_INSTRUCTIONS.txt with Getting Started guides"
```

---

## Self-Review

**Spec coverage:**
- Download from Google Drive ✓ (Step 1 content in generator)
- Extract ZIP ✓ (Step 1, platform-specific: double-click vs Extract All)
- Install (place files) ✓ (Step 2)
- macOS Gatekeeper warning ✓ (inline warning callout in Step 3)
- Windows SmartScreen warning ✓ (inline warning callout in Step 3)
- First launch / quick start ✓ (Step 4)
- Three formats: txt, pdf, html ✓ (generator writes all three)
- Platform-specific guides ✓ (separate macos/ and windows/ folders)
- Static files, packaging just copies ✓ (copy_guide_files in Task 3)
- Old INSTALLATION_INSTRUCTIONS.txt removed ✓ (Task 3, Step 2)

**Placeholder scan:** None found. All code is complete.

**Type consistency:** `copy_guide_files(platform, dest_dir, project_root)` — same signature in implementation (Task 3 Step 1) and tests (Task 2 Step 2). ✓
