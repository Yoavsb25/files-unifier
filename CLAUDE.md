# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Run the app
python main.py

# Run all tests
python -m pytest

# Run a single test file
python -m pytest tests/unit/test_core/test_merge_orchestrator.py -v

# Run tests with coverage
python -m pytest --cov=pdf_merger

# Build macOS executable
bash build_config/build.sh

# Build Windows executable
build_config/build.bat

# Generate a customer license
python tools/license_generator.py

# Create a client delivery package
python tools/create_client_package.py
```

## Architecture

**Entry point:** `main.py` — starts the GUI, initializes observability, validates the license, then enters the Tkinter event loop.

**Core merge pipeline** (`pdf_merger/core/`):
- `merge_orchestrator.py` — top-level coordinator; `run_merge()` and `run_merge_job()` drive the full pipeline
- `merge_processor.py` — row-by-row merge execution; calls into `matching/rules.py` for file resolution
- `csv_excel_reader.py` — parses the input manifest (CSV or Excel) via pandas
- `serial_number_parser.py` — extracts serial/ID tokens from PDF filenames
- `result_reporter.py` — writes per-file and summary reports (ReportLab PDF output)

**Matching** (`pdf_merger/matching/rules.py`): confidence-scored matching of manifest rows to PDF files; detects and handles ambiguous matches.

**GUI** (`pdf_merger/ui/`):
- `app.py` — `PDFMergerApp` (CustomTkinter); owns the window and delegates to handlers
- `handlers.py` — `FileSelectionHandler`, `MergeHandler` for UI events
- `components.py` — reusable UI widgets (cards, log area, results frame)
- `theme.py` — all colors, fonts, and spacing constants (dark-blue theme)

**Domain models** (`pdf_merger/models/`): `MergeJob`, `MergeResult`, `RowResult`, `Row`.

**Configuration** (`pdf_merger/config/`): four-level precedence — env vars → `~/.pdf_merger/config.json` → `.pdf_merger_config.json` → built-in defaults. Key fields: `input_file`, `pdf_dir`, `output_dir`, `required_column`, `output_name_column`, `fail_on_ambiguous_matches`.

**Licensing** (`pdf_merger/licensing/`): RSA-signed licenses stored at `~/.pdf_merger/license.json`. States: `VALID`, `EXPIRED`, `INVALID_SIGNATURE`, `NOT_FOUND`, etc. License generation and customer packaging live in `tools/`.

**Observability** (`pdf_merger/observability/`): crash reporting (exception hook), metrics (JSON export), and opt-in telemetry. All initialized in `main.py` before the GUI loop.

**Operations** (`pdf_merger/operations/`): low-level PDF merge (`pypdf`), streaming merge for large files, and Excel-to-PDF conversion (`reportlab`).

## Brand

Company is **Unifier**, product is **Files Unifier**, tagline "Many files. One document." — `brand/BRAND.md` is the source of truth for names, colours and asset usage. Never use the old names ("PDF Batch Merger", "Files Unifeder") in user-facing copy. Edit SVG masters in `brand/`, then run `python tools/generate_brand_assets.py --contact-sheet` to regenerate exports and sync them to `build_config/assets/`, `pdf_merger/assets/` and `landing/assets/`.

`landing/index.html` is the static marketing site (no build step); preview with `python -m http.server 8000 --directory landing`.

## Tests

Tests live in `tests/unit/` organized by module (mirrors `pdf_merger/` structure). `pytest.ini` configures discovery. There are no integration tests — the test suite is unit-only (~30 tests).

## CI/CD

`.github/workflows/build-client-package.yml` — manually triggered; accepts `company_name`, `expiry_date`, platform. Generates a signed license, builds a PyInstaller executable, packages it, and uploads the ZIP to Google Drive via `tools/upload_to_drive.py`.
