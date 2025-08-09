"""
DocxMD Converter - A Python package for converting between .docx and .md files.

This package provides both CLI and GUI interfaces for converting documents
between Microsoft Word (.docx) and Markdown (.md) formats with support for
templates and recursive directory processing.
"""

__version__ = "2.0.1"
__author__ = "we256681"
__email__ = "we256681@gmail.com"
__description__ = (
    "Convert between .docx and .md files with template support "
    "and advanced document post-processing"
)

from .cli import main as cli_main
from .core import DocxMdConverter
from .gui import run as gui_run

__all__ = ["DocxMdConverter", "cli_main", "gui_run"]
