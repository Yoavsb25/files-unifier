"""
Apply application config to UI fields.
Pure helper for loading config (paths, column name) into selectors and path attributes;
used by the main app so config-into-UI logic is testable and keeps app.py short.
"""

from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

from ..utils.exceptions import PDFMergerError


def apply_config_to_ui(
    config: Any,
    *,
    column_entry: Any,
    path_applyments: List[Tuple[Optional[str], str, Any, Callable[[Path], None], str]],
    set_path_attr: Callable[[str, Path], None],
    log_info: Callable[[str], None],
    log_warning: Callable[[str], None],
    on_update_state: Callable[[], None],
) -> None:
    """
    Load configuration into UI: set column name and apply each path to selector and path attribute.

    For each (path_str, path_attr, selector, validator, log_label) in path_applyments,
    if path_str is set, validates the path, sets the path attribute via set_path_attr,
    updates the selector display, and logs. On validation or path error, logs a warning
    and continues. Finally calls on_update_state().

    Args:
        config: AppConfig-like with required_column and path fields.
        column_entry: Entry widget for column name; will have config.required_column inserted at 0.
        path_applyments: List of (path_str, path_attr, selector, validator, log_label).
        set_path_attr: Called as set_path_attr(path_attr, path) to store the path on the app.
        log_info: Info logger (e.g. logger.info).
        log_warning: Warning logger (e.g. logger.warning).
        on_update_state: Called once after applying all paths (e.g. app._update_ui_state).
    """
    column_entry.insert(0, config.required_column)
    for path_str, path_attr, selector, validator, log_label in path_applyments:
        if not path_str:
            continue
        try:
            path = Path(path_str)
            validator(path)
            set_path_attr(path_attr, path)
            selector.set_path(str(path))
            log_info(f"Loaded {log_label} from config: {path}")
        except (OSError, ValueError, PDFMergerError) as e:
            log_warning(f"Could not load {log_label} from config: {e}")
    on_update_state()
