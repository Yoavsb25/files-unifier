"""
UI components for PDF Merger application.
"""

import customtkinter as ctk
from typing import Callable, Optional, Union

from pathlib import Path

from .. import APP_VERSION, APP_NAME
from ..core.enums import StatusColor
from ..utils.path_utils import open_path_in_explorer


class LogHandler:
    """Custom log handler that writes to GUI text widget."""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = []
    
    def write(self, message: str):
        """Write log message to buffer."""
        if message.strip():
            self.buffer.append(message.strip())
    
    def flush(self):
        """Flush buffer to text widget."""
        if self.buffer:
            text = "\n".join(self.buffer)
            self.text_widget.insert("end", text + "\n")
            self.text_widget.see("end")
            self.buffer.clear()


class FileSelector(ctk.CTkFrame):
    """Reusable file/directory selector component."""
    
    def __init__(
        self,
        parent,
        label_text: str,
        button_text: str = "Browse...",
        on_select: Optional[Callable] = None,
        helper_text: Optional[str] = None
    ):
        super().__init__(parent)
        
        self.on_select = on_select
        
        # Label (section header - larger, high contrast)
        ctk.CTkLabel(
            self,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Button frame
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x")
        
        # File/directory label (muted so labels stand out)
        self.path_label = ctk.CTkLabel(
            button_frame,
            text="No selection",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray55")
        )
        self.path_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Browse button (secondary / outline so Run Merge reads as primary)
        self.browse_button = ctk.CTkButton(
            button_frame,
            text=button_text,
            command=self._on_browse_clicked,
            width=100,
            fg_color="transparent",
            border_width=1,
            border_color=("#3B8ED0", "#1F6AA5")
        )
        self.browse_button.pack(side="right")
        
        # Optional helper text (muted, below button row)
        self._helper_label = None
        if helper_text:
            self._helper_label = ctk.CTkLabel(
                self,
                text=helper_text,
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray55"),
                anchor="w"
            )
            self._helper_label.pack(anchor="w", pady=(4, 0))
        
        # Inline error label (hidden until set_error is called)
        self._error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=("#CC0000", "#E57373"),
            anchor="w"
        )
        # Pack with 0 height so layout is stable; we'll update text and pady when showing
        self._error_label.pack(anchor="w", pady=(2, 0))
        self._error_label.pack_forget()
    
    def set_error(self, message: Optional[str]) -> None:
        """Show or hide inline error message below the field."""
        if message:
            self._error_label.configure(text=message)
            self._error_label.pack(anchor="w", pady=(2, 0))
        else:
            self._error_label.configure(text="")
            self._error_label.pack_forget()
    
    def _on_browse_clicked(self):
        """Handle browse button click."""
        if self.on_select:
            self.on_select()
    
    def set_path(self, path: str):
        """Update the displayed path."""
        self.path_label.configure(text=path)
    
    def get_path(self) -> str:
        """Get the currently displayed path."""
        return self.path_label.cget("text")


class LicenseFrame(ctk.CTkFrame):
    """License status display frame (pill/badge style)."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=("gray90", "gray20"), corner_radius=20)
        
        self.license_label = ctk.CTkLabel(
            self,
            text="Checking license...",
            font=ctk.CTkFont(size=12)
        )
        self.license_label.pack(padx=16, pady=8)
    
    def update_status(self, text: str, color: Union[str, StatusColor] = StatusColor.WHITE):
        """Update license status display.
        
        Args:
            text: Status text to display
            color: Color string or StatusColor enum (defaults to white)
        """
        color_value = color.value if isinstance(color, StatusColor) else color
        self.license_label.configure(text=text, text_color=color_value)


class CompletionSummaryFrame(ctk.CTkFrame):
    """Visual summary block shown after merge completes (rows processed, failed, open output)."""

    def __init__(self, parent):
        super().__init__(parent, fg_color=("gray92", "gray18"), corner_radius=8)
        self._rows_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color=("gray20", "gray90")
        )
        self._failed_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color=("gray20", "gray90")
        )
        self._output_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            anchor="w",
            text_color=("gray45", "gray55")
        )
        self._open_btn = ctk.CTkButton(
            self,
            text="Open output folder",
            command=self._on_open_output,
            width=140,
            fg_color="transparent",
            border_width=1,
            border_color=("#3B8ED0", "#1F6AA5")
        )
        self._output_path: Optional[Path] = None
        # Layout: rows and failed on first row or stacked; output path; button
        self._rows_label.pack(anchor="w", padx=12, pady=(10, 2))
        self._failed_label.pack(anchor="w", padx=12, pady=(0, 2))
        self._output_label.pack(anchor="w", padx=12, pady=(4, 2))
        self._open_btn.pack(anchor="w", padx=12, pady=(4, 10))

    def show_result(
        self,
        total_rows: int,
        successful_merges: int,
        failed_count: int,
        output_path: Path,
    ) -> None:
        """Populate and show the summary block."""
        self._rows_label.configure(text=f"\u2713 {total_rows} rows processed")
        self._failed_label.configure(text=f"\u2717 {failed_count} failed")
        self._output_label.configure(text=f"Output: {output_path}")
        self._output_path = output_path
        self.pack(fill="x", pady=(0, 10))

    def hide(self) -> None:
        """Clear and hide the summary block."""
        self._output_path = None
        self.pack_forget()

    def _on_open_output(self) -> None:
        if self._output_path is not None:
            open_path_in_explorer(self._output_path)


class LogArea(ctk.CTkFrame):
    """Log/output display area."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Label (section header - consistent with other sections)
        ctk.CTkLabel(
            self,
            text="Output Log:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Text widget
        self.log_text = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def log(self, message: str):
        """Add message to log area."""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
    
    def clear(self):
        """Clear the log area."""
        self.log_text.delete("1.0", "end")


class Footer(ctk.CTkFrame):
    """Application footer with version and status."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Version label
        version_label = ctk.CTkLabel(
            self,
            text=f"{APP_NAME} v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        version_label.pack(side="left", padx=10, pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=10),
            anchor="e"
        )
        self.status_label.pack(side="right", padx=10, pady=5)
    
    def update_status(self, text: str, color: Union[str, StatusColor] = StatusColor.WHITE):
        """Update status display.
        
        Args:
            text: Status text to display
            color: Color string or StatusColor enum (defaults to white)
        """
        color_value = color.value if isinstance(color, StatusColor) else color
        self.status_label.configure(text=text, text_color=color_value)
