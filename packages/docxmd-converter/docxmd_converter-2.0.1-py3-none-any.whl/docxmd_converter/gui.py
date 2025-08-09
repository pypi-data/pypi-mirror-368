"""
Graphical user interface for DocxMD Converter.
"""

import logging
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional

from .core import ConversionError, DocxMdConverter


class LogHandler(logging.Handler):
    """Custom logging handler to redirect logs to GUI."""

    def __init__(self, text_widget: tk.Text) -> None:
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        # Use after() to ensure thread safety
        self.text_widget.after(0, self._append_text, msg + "\n")

    def _append_text(self, text: str) -> None:
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)


class DocxMdConverterGUI:
    """GUI application for DocxMD Converter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("DocxMD Converter")
        self.root.geometry("800x600")

        # Variables
        self.src_dir = tk.StringVar()
        self.dst_dir = tk.StringVar()
        self.template_path = tk.StringVar()
        self.format = tk.StringVar(value="docx2md")

        self.verbose = tk.BooleanVar()

        # Post-processing variables
        self.post_process = tk.BooleanVar()
        self.processor_type = tk.StringVar(value="basic")
        self.report_format = tk.StringVar(value="console")
        self.report_update = tk.BooleanVar()
        self.force_process = tk.BooleanVar()
        self.dry_run_process = tk.BooleanVar()

        self.converter: Optional[DocxMdConverter] = None
        self.conversion_thread: Optional[threading.Thread] = None

        self._create_widgets()
        self._setup_layout()
        self._setup_logging()

        # Center window on screen
        self.root.after(100, self._center_window)

    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")

        # Title
        self.title_label = ttk.Label(
            self.main_frame, text="DocxMD Converter", font=("Arial", 16, "bold")
        )

        # Source directory
        self.src_frame = ttk.LabelFrame(
            self.main_frame, text="Source Directory", padding="5"
        )
        self.src_entry = ttk.Entry(self.src_frame, textvariable=self.src_dir, width=60)
        self.src_button = ttk.Button(
            self.src_frame, text="Browse...", command=self._browse_source_dir
        )

        # Destination directory
        self.dst_frame = ttk.LabelFrame(
            self.main_frame, text="Destination Directory", padding="5"
        )
        self.dst_entry = ttk.Entry(self.dst_frame, textvariable=self.dst_dir, width=60)
        self.dst_button = ttk.Button(
            self.dst_frame, text="Browse...", command=self._browse_dest_dir
        )

        # Template
        self.template_frame = ttk.LabelFrame(
            self.main_frame, text="Template (Optional)", padding="5"
        )
        self.template_entry = ttk.Entry(
            self.template_frame, textvariable=self.template_path, width=60
        )
        self.template_button = ttk.Button(
            self.template_frame, text="Browse...", command=self._browse_template
        )

        # Conversion format
        self.format_frame = ttk.LabelFrame(
            self.main_frame, text="Conversion Format", padding="5"
        )
        self.format_docx2md = ttk.Radiobutton(
            self.format_frame,
            text="DOCX → Markdown",
            variable=self.format,
            value="docx2md",
            command=self._on_format_change,
        )
        self.format_md2docx = ttk.Radiobutton(
            self.format_frame,
            text="Markdown → DOCX",
            variable=self.format,
            value="md2docx",
            command=self._on_format_change,
        )

        # Options
        self.options_frame = ttk.LabelFrame(
            self.main_frame, text="Options", padding="5"
        )
        self.verbose_check = ttk.Checkbutton(
            self.options_frame, text="Verbose logging", variable=self.verbose
        )

        # Post-processing frame
        self.postprocess_frame = ttk.LabelFrame(
            self.main_frame, text="Post-Processing Options", padding="5"
        )

        self.postprocess_check = ttk.Checkbutton(
            self.postprocess_frame,
            text="Apply document processing after conversion",
            variable=self.post_process,
            command=self._on_postprocess_toggle,
        )

        # Processor type selection
        self.processor_frame = ttk.Frame(self.postprocess_frame)
        self.processor_basic = ttk.Radiobutton(
            self.processor_frame,
            text="Basic processor",
            variable=self.processor_type,
            value="basic",
            state="disabled",
        )
        self.processor_advanced = ttk.Radiobutton(
            self.processor_frame,
            text="Advanced processor",
            variable=self.processor_type,
            value="advanced",
            state="disabled",
        )

        # Report options
        self.report_frame = ttk.Frame(self.postprocess_frame)
        self.report_console = ttk.Radiobutton(
            self.report_frame,
            text="Console report",
            variable=self.report_format,
            value="console",
            state="disabled",
        )
        self.report_file = ttk.Radiobutton(
            self.report_frame,
            text="File report",
            variable=self.report_format,
            value="file",
            state="disabled",
        )

        # Processing options
        self.processing_options_frame = ttk.Frame(self.postprocess_frame)
        self.force_process_check = ttk.Checkbutton(
            self.processing_options_frame,
            text="Force process already processed files",
            variable=self.force_process,
            state="disabled",
        )
        self.dry_run_process_check = ttk.Checkbutton(
            self.processing_options_frame,
            text="Dry run (show what would be processed)",
            variable=self.dry_run_process,
            state="disabled",
        )
        self.report_update_check = ttk.Checkbutton(
            self.processing_options_frame,
            text="Update existing report file",
            variable=self.report_update,
            state="disabled",
        )

        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.convert_button = ttk.Button(
            self.button_frame,
            text="Start Conversion",
            command=self._start_conversion,
            style="Accent.TButton",
        )
        self.clear_button = ttk.Button(
            self.button_frame, text="Clear Log", command=self._clear_log
        )

        # Log output
        self.log_frame = ttk.LabelFrame(
            self.main_frame, text="Conversion Log", padding="5"
        )
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame, height=15, width=80, state=tk.DISABLED
        )

        # Progress bar
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress = ttk.Progressbar(self.progress_frame, mode="indeterminate")
        self.status_label = ttk.Label(self.progress_frame, text="Ready")

    def _setup_layout(self) -> None:
        """Setup widget layout."""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        self.title_label.pack(pady=(0, 20))

        # Source directory
        self.src_frame.pack(fill=tk.X, pady=5)
        self.src_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.src_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Destination directory
        self.dst_frame.pack(fill=tk.X, pady=5)
        self.dst_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dst_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Template
        self.template_frame.pack(fill=tk.X, pady=5)
        self.template_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.template_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Format
        self.format_frame.pack(fill=tk.X, pady=5)
        self.format_docx2md.pack(side=tk.LEFT, padx=(0, 20))
        self.format_md2docx.pack(side=tk.LEFT)

        # Options
        self.options_frame.pack(fill=tk.X, pady=5)
        self.verbose_check.pack(side=tk.LEFT)

        # Post-processing
        self.postprocess_frame.pack(fill=tk.X, pady=5)
        self.postprocess_check.pack(anchor=tk.W)

        self.processor_frame.pack(fill=tk.X, pady=2)
        self.processor_basic.pack(side=tk.LEFT, padx=(20, 10))
        self.processor_advanced.pack(side=tk.LEFT)

        self.report_frame.pack(fill=tk.X, pady=2)
        self.report_console.pack(side=tk.LEFT, padx=(20, 10))
        self.report_file.pack(side=tk.LEFT)

        self.processing_options_frame.pack(fill=tk.X, pady=2)
        self.force_process_check.pack(anchor=tk.W, padx=(20, 0))
        self.dry_run_process_check.pack(anchor=tk.W, padx=(20, 0))
        self.report_update_check.pack(anchor=tk.W, padx=(20, 0))

        # Buttons
        self.button_frame.pack(fill=tk.X, pady=10)
        self.convert_button.pack(side=tk.LEFT)
        self.clear_button.pack(side=tk.LEFT, padx=(10, 0))

        # Progress
        self.progress_frame.pack(fill=tk.X, pady=5)
        self.progress.pack(fill=tk.X)
        self.status_label.pack(pady=5)

        # Log
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Initially disable template and post-processing controls
        self._on_format_change()
        self._on_postprocess_toggle()

    def _setup_logging(self) -> None:
        """Setup logging to display in GUI."""
        # Create a custom handler that writes to our text widget
        self.log_handler = LogHandler(self.log_text)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.log_handler.setFormatter(formatter)

        # Initially setup with INFO level
        self._update_logging()

    def _update_logging(self) -> None:
        """Update logging configuration based on verbose setting."""
        # Remove existing handler if present
        logger = logging.getLogger("docxmd_converter.core")
        logger.handlers = [h for h in logger.handlers if not isinstance(h, LogHandler)]

        # Set level and add handler
        level = logging.DEBUG if self.verbose.get() else logging.INFO
        logger.setLevel(level)
        self.log_handler.setLevel(level)
        logger.addHandler(self.log_handler)

    def _browse_source_dir(self) -> None:
        """Browse for source directory."""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.src_dir.set(directory)

    def _browse_dest_dir(self) -> None:
        """Browse for destination directory."""
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.dst_dir.set(directory)

    def _browse_template(self) -> None:
        """Browse for template file."""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")],
        )
        if filename:
            self.template_path.set(filename)

    def _on_format_change(self) -> None:
        """Handle format change."""
        if self.format.get() == "md2docx":
            # Enable template controls
            self.template_entry.config(state="normal")
            self.template_button.config(state="normal")
        else:
            # Disable template controls
            self.template_entry.config(state="disabled")
            self.template_button.config(state="disabled")
            self.template_path.set("")

    def _on_postprocess_toggle(self) -> None:
        """Handle post-processing toggle."""
        state = "normal" if self.post_process.get() else "disabled"

        # Update processor type controls
        self.processor_basic.config(state=state)
        self.processor_advanced.config(state=state)

        # Update report format controls
        self.report_console.config(state=state)
        self.report_file.config(state=state)

        # Update processing options
        self.force_process_check.config(state=state)
        self.dry_run_process_check.config(state=state)
        self.report_update_check.config(state=state)

    def _clear_log(self) -> None:
        """Clear the log text."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_message(self, message: str, level: str = "INFO") -> None:
        """Add a message to the log."""
        self.log_text.config(state=tk.NORMAL)
        timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _validate_inputs(self) -> None:
        """Validate user inputs."""
        if not self.src_dir.get():
            raise ConversionError("Please select a source directory")

        if not self.dst_dir.get():
            raise ConversionError("Please select a destination directory")

        src_path = Path(self.src_dir.get())
        if not src_path.exists() or not src_path.is_dir():
            raise ConversionError(
                f"Source directory does not exist: {self.src_dir.get()}"
            )

        # Validate template if provided
        template = self.template_path.get().strip()
        if template:
            if self.format.get() != "md2docx":
                raise ConversionError(
                    "Template can only be used with Markdown → DOCX conversion"
                )

            template_path = Path(template)
            if not template_path.exists():
                raise ConversionError(f"Template file does not exist: {template}")

            if template_path.suffix.lower() != ".docx":
                raise ConversionError("Template must be a .docx file")

    def _start_conversion(self) -> None:
        """Start the conversion process in a separate thread."""
        if self.conversion_thread and self.conversion_thread.is_alive():
            messagebox.showwarning("Warning", "Conversion is already in progress!")
            return

        try:
            self._validate_inputs()
        except ConversionError as e:
            messagebox.showerror("Validation Error", str(e))
            return

        # Update UI state
        self.convert_button.config(state="disabled", text="Converting...")
        self.progress.start(10)
        self.status_label.config(text="Converting files...")

        # Clear log and update logging
        self._clear_log()
        self._update_logging()

        # Start conversion in separate thread
        self.conversion_thread = threading.Thread(target=self._run_conversion)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def _run_conversion(self) -> None:
        """Run the actual conversion (in separate thread)."""
        try:
            # Initialize converter
            log_level = "DEBUG" if self.verbose.get() else "INFO"
            self.converter = DocxMdConverter(log_level=log_level)

            # Get template path
            template = (
                self.template_path.get().strip()
                if self.template_path.get().strip()
                else None
            )

            # Run conversion
            successful, total, processing_results = self.converter.convert_directory(
                src_dir=self.src_dir.get(),
                dst_dir=self.dst_dir.get(),
                format=self.format.get(),
                template_path=template,
                post_process=self.post_process.get(),
                processor_type=self.processor_type.get(),
                force_process=self.force_process.get(),
                dry_run_process=self.dry_run_process.get(),
                report_format=self.report_format.get(),
                report_update=self.report_update.get(),
            )

            # Update UI in main thread
            self.root.after(
                0,
                self._conversion_complete,
                successful,
                total,
                processing_results,
                None,
            )

        except Exception as e:
            # Update UI in main thread
            self.root.after(0, self._conversion_complete, 0, 0, None, str(e))

    def _conversion_complete(
        self,
        successful: int,
        total: int,
        processing_results: Optional[dict],
        error: Optional[str],
    ) -> None:
        """Handle conversion completion (runs in main thread)."""
        # Update UI state
        self.convert_button.config(state="normal", text="Start Conversion")
        self.progress.stop()

        if error:
            self.status_label.config(text=f"Error: {error}")
            self._log_message(f"Conversion failed: {error}", "ERROR")
            messagebox.showerror("Conversion Error", error)
        else:
            if successful == total:
                status_msg = f"✅ Successfully converted all {total} files"
                log_msg = f"Successfully converted all {total} files"

                # Add post-processing info if applicable
                if processing_results and self.post_process.get():
                    if "error" not in processing_results:
                        processed = processing_results.get("processed", 0)
                        total_processed = processing_results.get("total", 0)
                        status_msg += (
                            f" | Post-processed: {processed}/{total_processed}"
                        )
                        log_msg += f" | Post-processed: {processed}/{total_processed}"

                self.status_label.config(text=status_msg)
                self._log_message(log_msg, "INFO")
                messagebox.showinfo("Success", status_msg)
            else:
                status_msg = f"⚠️ Done {successful}/{total} files"
                log_msg = f"Converted {successful}/{total} files (some errors occurred)"

                # Add post-processing info if applicable
                if processing_results and self.post_process.get():
                    if "error" not in processing_results:
                        processed = processing_results.get("processed", 0)
                        total_processed = processing_results.get("total", 0)
                        status_msg += (
                            f" | Post-processed: {processed}/{total_processed}"
                        )
                        log_msg += f" | Post-processed: {processed}/{total_processed}"

                self.status_label.config(text=status_msg)
                self._log_message(log_msg, "WARNING")
                messagebox.showwarning(
                    "Partial Success", f"{status_msg}. Check log for details."
                )

    def run(self) -> None:
        """Start the GUI application."""
        try:
            # Check if pandoc is available
            DocxMdConverter()._check_pandoc()
        except ConversionError as e:
            messagebox.showerror("Dependency Error", str(e))
            return

        self.root.mainloop()


def run() -> None:
    """Entry point for GUI application."""
    try:
        app = DocxMdConverterGUI()
        app.run()
    except Exception as e:
        try:
            messagebox.showerror("Error", f"Failed to start application: {e}")
        except Exception:
            print(f"Failed to start GUI application: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    run()
