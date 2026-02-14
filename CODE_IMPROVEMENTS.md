# Codebase improvement suggestions

This file collects suggestions for improving the codebase. They are non-blocking and can be addressed over time.

---

## Exceptions

- **`PDFProcessingError`**  
  Defined in `pdf_merger/utils/exceptions.py` and tested, but never raised in production. Consider either using it in PDF operations (e.g. `pdf_merger.py`, `streaming_pdf_merger.py`) when a PDF read/merge/write fails, or documenting it as a reserved type for future use.

---

## Result types and reporting

- **`ProcessingResult` and legacy API**  
  `ProcessingResult` is deprecated in favor of `MergeResult`, but the pipeline still returns/uses it internally (`merge_processor.process_job` builds `ProcessingResult`; `result_reporter` and `result_view` accept both). A full migration would have `process_job` return only `MergeResult` and remove `ProcessingResult` and `as_processing_result` from the public API (per `DEPRECATION.md`).

- **`format_result_detailed`**  
  Addressed: the UI uses it in the "View detailed log" action (`_show_detailed_report`), which opens a dialog showing `format_result_detailed(result)` after a merge.

---

## Constants and duplication

- **Serial number and CSV constants (addressed)**  
  Serial number format constants now live only in `utils.serial_number_parser`; they were removed from `CsvSerialConstants`. CSV/encoding constants (`UTF_8_ENCODING`, `CSV_SAMPLE_SIZE`, `DEFAULT_CSV_DELIMITER`) now have a single source in `utils/csv_constants.py`; `column_reader` and `CsvSerialConstants` use or re-export from there.

- **Example column name in UI**  
  The UI placeholder “e.g. serial_numbers or Document ID” uses a literal string. If you want a single canonical example name, consider a constant (e.g. in `ui_constants` or `defaults`) and use it in both placeholder and helper text.

---

## Deprecations and removal

- **`run_merge`**  
  Deprecated in favor of `run_merge_job`; still present for backward compatibility. Plan to remove in 2.0 as per `DEPRECATION.md`.

- **`process_file`**  
  Same as above; callers should use `load_job_from_file` + `process_job` and `as_processing_result` if needed.

---

## UI and structure

- **`pdf_merger/ui/app.py`**  
  The main app class is large. Consider extracting cohesive blocks into helpers or sub-modules (e.g. config loading, path application, validation state, run merge flow) to improve readability and testability.

- **Broad `except Exception`**  
  Several places catch `Exception` and log or show a generic message (e.g. `config_manager`, `handlers`, `row_pipeline`). Where possible, catch specific exceptions (`PDFMergerError`, `ValueError`, etc.) and re-raise or handle them explicitly so that unexpected errors are easier to diagnose.

---

## Tests and docs

- **`test_merge_processor.py`**  
  Comment at top references patching `utils.serial_number_parser` if merge_processor is refactored to import from utils; the processor already uses core’s re-export. You can update or remove that comment when touching this area.

- **ARCHITECTURE / IMPROVEMENT_ROADMAP**  
  If you remove or rename constants (e.g. `GOLDFARB_SERIAL_NUMBER_COLUMN`, `SOURCE_FILE_EXTENSIONS` from `FileConstants`), update any references in `docs/ARCHITECTURE.md` and `docs/IMPROVEMENT_ROADMAP.md`.

---

## Observability

- **Telemetry `endpoint`**  
  `TelemetryService.__init__` has an `endpoint` parameter “for future use”. Either implement sending events to that endpoint or document that it is reserved for a future backend.

- **MetricsCollector**  
  Metrics are recorded but not yet exported (e.g. to a file or external system). Consider adding a simple export hook (e.g. on shutdown or on demand) for debugging or future integration.
