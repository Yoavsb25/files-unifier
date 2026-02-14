# Plan: Complete Removal of Old / Legacy / Deprecated Code

**Execution completed.** Removed items are listed in [docs/DEPRECATION.md](DEPRECATION.md) under "Legacy removal (completed)."

This document is a **concrete plan** to remove all remaining legacy, deprecated, and backward-compatibility code from the codebase. Each item lists **what** to remove, **where** it lives, **dependencies** (who uses it), and **steps** to remove it safely.

**Status key:** `[REMOVE]` = delete the code; `[MIGRATE]` = switch callers to the preferred API then delete; `[CLEANUP]` = remove comments/aliases only.

---

## 1. Legacy APIs (used only in tests or nowhere)

### 1.1 `find_pdf_file` — [REMOVE]

| Field | Detail |
|-------|--------|
| **Location** | `pdf_merger/operations/pdf_merger.py` (lines ~109–144) |
| **Current use** | Only in `tests/unit/operations/test_pdf_merger.py` (class `TestFindPdfFile` and one test in `TestMergePdfs`) |
| **Preferred API** | `find_source_file()` in the same module (finds PDF and Excel; uses matching rules) |
| **Steps** | 1. In `test_pdf_merger.py`, replace every `find_pdf_file(folder, name)` with `find_source_file(folder, name, fail_on_ambiguous=False)` and adjust assertions if needed (return type and behavior are compatible for PDF-only cases). 2. Remove the `TestFindPdfFile` class if its scenarios are fully covered by `find_source_file` tests; otherwise keep tests but call `find_source_file`. 3. Delete the `find_pdf_file` function from `pdf_merger.py`. 4. Update `docs/ARCHITECTURE.md` and `tests/README.md` to remove references to `find_pdf_file`. |

### 1.2 `process_row` (bool-returning) — [REMOVE]

| Field | Detail |
|-------|--------|
| **Location** | `pdf_merger/core/merge_processor.py` (lines ~39–82) |
| **Current use** | Only in `tests/unit/core/test_merge_processor.py` (classes `TestProcessRow`, `TestProcessRowWithExcelFile`, `TestProcessRowMixedPdfAndExcel`, etc.) |
| **Preferred API** | `process_row_with_models(row, source_folder, output_folder, ...)` with a `Row` and `RowResult` |
| **Steps** | 1. Refactor all tests that call `process_row(...)` to build a `Row` via `Row.from_raw_data(row_index, {"serial_numbers": "..."}, required_column)` and call `process_row_with_models(row, source_folder, output_folder, ...)`; assert on `RowResult` (e.g. `result.is_success()`, `result.is_failed()`, `result.status`). 2. Remove the `process_row` function from `merge_processor.py`. 3. Update module docstring and any ARCHITECTURE bullets that mention `process_row()` as a legacy API. |

---

## 2. Backward-compatibility re-exports and wrappers

### 2.1 `core/serial_number_parser` re-export — [REMOVE]

| Field | Detail |
|-------|--------|
| **Location** | `pdf_merger/core/serial_number_parser.py` (entire file: re-exports from `utils.serial_number_parser`) |
| **Current use** | `pdf_merger/core/merge_processor.py` imports from `.serial_number_parser`; `tests/unit/core/test_serial_number_parser.py` imports from `pdf_merger.core.serial_number_parser`. |
| **Preferred API** | Import from `pdf_merger.utils.serial_number_parser` everywhere. |
| **Steps** | 1. In `merge_processor.py`, change `from .serial_number_parser import (...)` to `from ..utils.serial_number_parser import (...)`. 2. In `tests/unit/core/test_serial_number_parser.py`, change imports to `from pdf_merger.utils.serial_number_parser import (...)`. 3. Update `test_merge_processor.py` patch target: change `patch('pdf_merger.core.merge_processor.split_serial_numbers')` to `patch('pdf_merger.core.merge_processor.split_serial_numbers')` — the module under test will now get it from utils, so patch `'pdf_merger.utils.serial_number_parser.split_serial_numbers'` and ensure merge_processor uses that (or keep patching at merge_processor’s namespace if it re-exports). Actually: after changing merge_processor to import from utils, patch `'pdf_merger.core.merge_processor.split_serial_numbers'` (the symbol where it’s used) so the test still works. 4. Delete `pdf_merger/core/serial_number_parser.py`. 5. Update `docs/ARCHITECTURE.md` directory tree: remove or reword the line that says `serial_number_parser.py  # Re-export from utils (backward compatibility)`. |

---

## 3. Theme and UI aliases

### 3.1 Theme aliases (CARD_BG, BG_DARK, etc.) — [MIGRATE then REMOVE]

| Field | Detail |
|-------|--------|
| **Location** | `pdf_merger/ui/theme.py` (lines ~30–40: `BG_DARK`, `CARD_BG`, `INPUT_CONTAINER_BG`, `INPUT_BG`, `LOG_BG`, `FOCUS_BLUE`, `INPUT_HOVER_BG`, `GREEN_SUCCESS`, `RED_ERROR`, `YELLOW_WARNING`, `BLUE_INFO`) |
| **Current use** | `app.py`: `CARD_BG`. `components.py`: `CARD_BG`, `METRIC_CARD_BG`. |
| **Preferred names** | `APP_BACKGROUND`, `CARD_BACKGROUND`, `INPUT_BACKGROUND`, etc. (already defined above the aliases). |
| **Steps** | 1. In `app.py`, replace `CARD_BG` with `CARD_BACKGROUND`. 2. In `components.py`, replace `CARD_BG` with `CARD_BACKGROUND` and keep `METRIC_CARD_BG` as-is (it’s a distinct constant, not an alias). 3. In `theme.py`, remove the alias block (lines 30–40) and the comment "Aliases for backward compatibility". 4. Grep for any remaining use of `BG_DARK`, `INPUT_CONTAINER_BG`, `INPUT_BG`, `LOG_BG`, `FOCUS_BLUE`, `INPUT_HOVER_BG`, `GREEN_SUCCESS`, `RED_ERROR`, `YELLOW_WARNING`, `BLUE_INFO`; replace with the preferred name or leave if it’s the only name (e.g. `LOG_BG`). |

### 3.2 `Footer.update_status` no-op — [REMOVE]

| Field | Detail |
|-------|--------|
| **Location** | `pdf_merger/ui/components.py` — `Footer.update_status(self, text, color)` (no-op body). |
| **Current use** | No production code calls it. Only `tests/unit/ui/test_components.py` has `test_footer_update_status_no_op` which asserts the method exists and can be called. |
| **Steps** | 1. Remove the `update_status` method from the `Footer` class. 2. In `test_components.py`, remove `test_footer_update_status_no_op` or replace it with a test that the footer still builds and has no `update_status` (e.g. assert `not hasattr(footer, 'update_status')` or simply delete the test). |

---

## 4. Comments and docstrings (no behavioral legacy)

### 4.1 PDFMergerError.message — [CLEANUP]

| Field | Detail |
|-------|--------|
| **Location** | `pdf_merger/utils/exceptions.py`: `self.message = message  # Keep for backward compatibility; same as args[0].` |
| **Action** | If no external or internal code relies on `e.message` (only `str(e)` or `e.args[0]`), remove the `.message` attribute and the comment. Grep for `\.message` on exception objects first; if only in tests or docs, remove the attribute and update any reference to use `str(e)`. |

### 4.2 config/__init__.py "Re-export for backward compatibility"

| Field | Detail |
| **Action** | This is the normal public API of the config package. Either remove the comment or reword to "Public API of the config package." No code removal. |

### 4.3 core/constants.py "backward compatibility"

| Field | Detail |
| **Action** | Comment says "import Constants from here for backward compatibility." Reword to "Composes domain-specific constant classes; import Constants from here." No code removal. |

### 4.4 license_ui.py "Constants for backward compatibility and convenience"

| Field | Detail |
| **Action** | `GREEN_COLOR`, `RED_COLOR`, etc. are used only inside `license_ui.py`. They are convenience, not legacy. Reword the comment to "Convenience constants mapping LicenseColor to theme hex." No removal required unless you want to inline `LicenseColor.GREEN.value` everywhere. |

---

## 5. Documentation cleanup (stale legacy references)

### 5.1 tests/README.md

| Location | Current text | Action |
|----------|--------------|--------|
| ~225 | `find_pdf_file` - Finding PDF files (backward compatibility) | Remove the line or update to "find_source_file - Finding source files (PDF/Excel)". |
| ~259 | `ProcessingResult` - Result dataclass | Remove or replace with "MergeResult - Result of a merge run." |

### 5.2 docs/TESTING.md

| Location | Current text | Action |
|----------|--------------|--------|
| ~302 | `result = process_file(...)` | Replace with example using `run_merge_job` or `load_job_from_file` + `process_job`. |
| ~416–417 | `ProcessingResult(total_rows=5, ...)` example | Replace with `MergeResult(total_rows=5, successful_merges=4, ...)`. |

### 5.3 docs/ENGINEERING_AUDIT.md

| Location | Current text | Action |
|----------|--------------|--------|
| References to "legacy run_merge/process_file" | Several bullets | Update to state they are removed; no "deprecated with timeline" anymore. |

### 5.4 docs/IMPROVEMENT_ROADMAP.md

| Location | Current text | Action |
|----------|--------------|--------|
| References to `as_processing_result`, legacy entry points | Several lines | Update to "Legacy APIs removed as of 2.0." No code changes. |

### 5.5 CODE_IMPROVEMENTS.md

| Location | Current text | Action |
|----------|--------------|--------|
| "Legacy APIs kept (documented): find_pdf_file and process_row" | In Code Cleanup section | After removal, update to "Legacy APIs find_pdf_file and process_row have been removed. Use find_source_file and process_row_with_models + MergeResult." |

---

## 6. Execution order (recommended)

1. **Docs only (low risk):** 4.1–4.4 (comment/attribute cleanup), 5.1–5.5 (doc updates). Optionally do 4.1 after checking for `.message` usage.
2. **Test-only legacy:** 1.1 `find_pdf_file` (refactor tests, then delete function), then 1.2 `process_row` (refactor tests, then delete function). Run full test suite after each.
3. **Re-exports:** 2.1 `core/serial_number_parser` (switch imports, delete file). Run tests again.
4. **UI:** 3.1 theme aliases (migrate app + components to preferred names, remove aliases), 3.2 `Footer.update_status` (remove method and adjust test).

---

## 7. Verification

- Run `pytest` and ensure all tests pass.
- Run `ruff check pdf_merger` (or your lint step).
- Grep for: `find_pdf_file`, `process_row(`, `from.*core.serial_number_parser`, `CARD_BG`, `BG_DARK`, `update_status` (in Footer context), and confirm no remaining unintended uses.
- Update `docs/DEPRECATION.md` to add a short "Legacy removal (completed)" section listing removed items: `find_pdf_file`, `process_row` (bool), `core.serial_number_parser` re-export, theme aliases, `Footer.update_status`.

---

## 8. Summary table

| Item | Type | Remove? | Dependencies to update |
|------|------|---------|-------------------------|
| `find_pdf_file` | Function | Yes | test_pdf_merger.py, ARCHITECTURE, tests/README |
| `process_row` (bool) | Function | Yes | test_merge_processor.py, ARCHITECTURE |
| `core/serial_number_parser` | Module | Yes | merge_processor.py, test_serial_number_parser.py, test_merge_processor patches, ARCHITECTURE |
| Theme aliases (CARD_BG etc.) | Constants | Yes (after migrate) | app.py, components.py |
| `Footer.update_status` | Method | Yes | test_components.py |
| `PDFMergerError.message` | Attribute | Optional | Grep; if unused, remove |
| Config/core/license_ui comments | Comments | Cleanup only | None |
| Docs (TESTING, README, etc.) | Text | Update | None |
