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
