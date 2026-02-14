# Deprecation notice

This document lists deprecated APIs and their removal status.

## Removed APIs (as of 2.0)

The following have been removed from the codebase:

- **`run_merge`** — Use `run_merge_job` from `pdf_merger` or `pdf_merger.core`.
- **`process_file`** — Use `load_job_from_file` (from `pdf_merger.core.job_loader`) then `process_job` (from `pdf_merger.core.merge_processor`).
- **`ProcessingResult`** and **`as_processing_result`** — The pipeline uses only `MergeResult`; use `MergeResult` from `pdf_merger.models` everywhere.

## Legacy removal (completed)

The following legacy/deprecated items have been removed (as of 2.0):

- **`find_pdf_file`** — Use `find_source_file` from `pdf_merger.operations.pdf_merger`.
- **`process_row`** (bool-returning) — Use `process_row_with_models(row, ...)` with `Row` and `RowResult` from `pdf_merger.core.merge_processor`.
- **`pdf_merger.core.serial_number_parser`** re-export — Import from `pdf_merger.utils.serial_number_parser` only.
- **Theme aliases** (`CARD_BG`, `BG_DARK`, `LOG_BG`, `GREEN_SUCCESS`, `RED_ERROR`, etc.) — Use the primary names: `CARD_BACKGROUND`, `APP_BACKGROUND`, `LOG_BACKGROUND`, `SUCCESS_GREEN`, `ERROR_RED`, etc., from `pdf_merger.ui.theme`.
- **`Footer.update_status`** — Removed (no-op); footer shows version only.

## Migration example

**Preferred entry point:**

```python
from pdf_merger import run_merge_job

result = run_merge_job(
    input_file=input_file,
    pdf_dir=pdf_dir,
    output_dir=output_dir,
    required_column="serial_numbers",
)
# result is MergeResult
```

**Building a job and processing manually:**

```python
from pdf_merger.core.job_loader import load_job_from_file
from pdf_merger.core.merge_processor import process_job

job = load_job_from_file(
    input_file=file_path,
    source_folder=source_folder,
    output_folder=output_folder,
    required_column=required_column,
    on_progress=...,
)
merge_result = process_job(job, on_progress=...)
```
