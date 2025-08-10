"""
Universal Printer - Cross-platform document printing with enhanced PDF generation.

A powerful, dependency-free Python library that works across Windows, macOS, and Linux
to print documents and generate professional PDFs with intelligent formatting for
text, Markdown, CSV, and JSON files.

Version 3.0 Features:
- Enhanced PDF generation with intelligent formatting
- Advanced Markdown support with syntax conversion
- CSV table formatting with proper alignment
- JSON pretty printing with structure preservation
- Improved error handling and logging
- Professional PDF output with metadata
- Batch processing capabilities
- Configuration management
"""

from .document_printer import DocumentPrinter
from .exceptions import UniversalPrinterError, PrintingError, PDFGenerationError
from .config import PrinterConfig
from .utils import FileTypeDetector, PDFValidator

__version__ = "3.0.0"
__author__ = "Sharath Kumar Daroor"
__email__ = "sharathkumardaroor@gmail.com"
__description__ = "Cross-platform document printing with enhanced PDF generation"
__url__ = "https://github.com/sharathkumardaroor/universal-printer"
__license__ = "MIT"

__all__ = [
    "DocumentPrinter",
    "UniversalPrinterError", 
    "PrintingError",
    "PDFGenerationError",
    "PrinterConfig",
    "FileTypeDetector",
    "PDFValidator"
]