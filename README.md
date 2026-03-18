# Files Unifeder — PDF Batch Merger

![Python](https://img.shields.io/badge/Python-A78BFA?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-7C3AED?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-7C3AED?style=for-the-badge)
![License](https://img.shields.io/badge/License-Commercial-6B7280?style=for-the-badge)

> Desktop GUI app for batch merging PDFs against a CSV/Excel manifest — match, merge, report.

---

## Overview

Files Unifeder is a desktop application built with Python and Tkinter that automates batch PDF merging. Given a CSV or Excel manifest and a folder of PDF files, it matches files by serial number, merges them in the configured order, and produces a detailed results report. Built for reliability — includes license management, crash reporting, metrics collection, and opt-in telemetry.

## Features

- Batch merge PDFs against a CSV/Excel manifest
- Serial number-based file matching
- Configurable merge order and page range control
- Detailed per-file and summary results report
- License management (valid/expired/error states)
- Crash reporting, metrics collection, and opt-in telemetry
- Packaged as a standalone executable (PyInstaller)

## Architecture

```
main.py
  └── Load config (config_manager)
  └── Launch PDFMergerApp (tkinter GUI)  ← window shown immediately
  └── Init observability (crash reporter, metrics, telemetry)
  └── Validate license (LicenseManager)
      └── On invalid → show error dialog, exit

PDFMergerApp (ui/app.py)
  └── MergeOrchestrator (core/merge_orchestrator.py)
      └── CSVExcelReader       → parse manifest
      └── SerialNumberParser   → extract IDs from filenames
      └── FileMatcher          → pair manifest rows to PDF files
      └── MergeProcessor       → execute PDF merges
      └── ResultReporter       → summarize output
```

> The GUI window is shown immediately on startup before license/observability I/O, giving faster perceived startup.

## Module Breakdown

| Module | Responsibility |
|--------|----------------|
| `pdf_merger/core/merge_orchestrator.py` | Coordinates the full merge pipeline |
| `pdf_merger/core/merge_processor.py` | Executes individual PDF merge operations |
| `pdf_merger/core/csv_excel_reader.py` | Parses CSV and Excel manifest files |
| `pdf_merger/core/serial_number_parser.py` | Extracts serial numbers from filenames |
| `pdf_merger/core/result_reporter.py` | Generates per-file and summary reports |
| `pdf_merger/core/enums.py` | Shared enums (merge status, file type, etc.) |
| `pdf_merger/matching/` | File-to-manifest matching logic |
| `pdf_merger/models/` | Data models (MergeJob, MergeResult, etc.) |
| `pdf_merger/config/config_manager.py` | Loads and saves user configuration |
| `pdf_merger/licensing/` | License validation and expiry management |
| `pdf_merger/observability/` | Crash reporter, metrics collector, telemetry |
| `pdf_merger/ui/app.py` | Tkinter GUI (PDFMergerApp) |
| `pdf_merger/utils/logging_utils.py` | Centralized logging setup |

## Getting Started

**Prerequisites:** Python 3.x, pip

```bash
git clone https://github.com/Yoavsb25/files_unifeder.git
cd files_unifeder
pip install -r requirements.txt
python main.py
```

## Project Structure

```
files_unifeder/
├── main.py                     # Entry point — launches GUI, observability, license check
├── pdf_merger/
│   ├── core/                   # Merge pipeline: orchestrator, processor, parsers, reporter
│   ├── config/                 # Configuration loading and persistence
│   ├── licensing/              # License management
│   ├── matching/               # Serial-number-to-file matching
│   ├── models/                 # Data models
│   ├── observability/          # Crash reporting, metrics, telemetry
│   ├── operations/             # High-level operation wrappers
│   ├── ui/                     # Tkinter GUI (PDFMergerApp)
│   └── utils/                  # Logging utilities
├── docs/                       # Documentation
├── tools/                      # Developer tooling
├── tests/                      # Test suite
├── build_config/               # PyInstaller build configuration
├── requirements.txt
└── pytest.ini
```

---

[![LinkedIn](https://img.shields.io/badge/Yoav_Sborovsky-LinkedIn-7C3AED?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yoav-sborovsky/)
&nbsp;
Part of [Yoav Sborovsky's GitHub portfolio](https://github.com/Yoavsb25)
