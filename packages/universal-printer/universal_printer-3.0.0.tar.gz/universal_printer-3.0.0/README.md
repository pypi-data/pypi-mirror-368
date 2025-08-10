# Universal Printer v3.0

🖨️ **A powerful, dependency-free Python library for cross-platform document printing with enhanced PDF generation**

[![PyPI version](https://badge.fury.io/py/universal-printer.svg)](https://badge.fury.io/py/universal-printer)
[![Python versions](https://img.shields.io/pypi/pyversions/universal-printer.svg)](https://pypi.org/project/universal-printer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/universal-printer)](https://pepy.tech/project/universal-printer)

Universal Printer is a comprehensive document printing and PDF generation library that works seamlessly across Windows, macOS, and Linux. Version 3.0 introduces powerful enhanced PDF generation with intelligent formatting for Markdown, CSV, JSON, and text files.

## ✨ Key Features

### 🖨️ Universal Printing
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Universal file support**: Print any file type (PDF, DOC, TXT, images, HTML, etc.)
- **Smart fallback**: Automatically creates PDF if printing fails
- **Batch processing**: Print multiple files at once

### 📄 Enhanced PDF Generation
- **Intelligent formatting**: Special handling for .txt, .md, .csv, .json files
- **Markdown conversion**: Headers, lists, code blocks, emphasis → formatted text
- **CSV table formatting**: Proper column alignment and table structure
- **JSON pretty printing**: Structured formatting with indentation
- **Professional output**: Clean, readable PDFs with metadata

### ⚙️ Advanced Features
- **Configuration system**: Customizable settings via JSON config files
- **Statistics tracking**: Monitor success rates and performance
- **CLI interface**: Command-line tool for all operations
- **Comprehensive logging**: Configurable file and console logging
- **File analysis**: Advanced file type detection and validation
- **Dependency-free**: Uses only Python standard library

## Installation

```bash
pip install universal-printer
```

## 🚀 Quick Start

### Basic Usage

```python
from universal_printer import DocumentPrinter

# Create printer instance
printer = DocumentPrinter()

# Print text content
success, message, pdf_path = printer.print_text(
    "Hello, World!\nThis is a test document.",
    fallback_to_pdf=True
)

# Print any file type
success, message, pdf_path = printer.print_file(
    "/path/to/document.pdf",  # or .docx, .jpg, .html, etc.
    fallback_to_pdf=True
)

# Generate PDF directly (NEW in v3.0)
success, message, pdf_path = printer.generate_pdf(
    "document.md",  # Supports .txt, .md, .csv, .json
    pdf_filename="formatted_document"
)
```

### Enhanced PDF Generation

```python
# Markdown with intelligent formatting
markdown_content = """
# My Document
## Introduction
This **bold text** and *italic text* will be properly formatted.

- Bullet points become • symbols
- Code blocks get special formatting
- Tables are properly aligned

```python
print("Code blocks are highlighted")
```
"""

success, message, pdf_path = printer.generate_pdf(
    markdown_content,
    pdf_filename="formatted_markdown"
)

# CSV with table formatting
csv_content = """Name,Age,City
John,30,New York
Jane,25,Los Angeles
Bob,35,Chicago"""

success, message, pdf_path = printer.generate_pdf(
    csv_content,
    pdf_filename="formatted_table"
)
```

### Batch Processing (NEW in v3.0)

```python
# Print multiple files
files = ["doc1.txt", "doc2.md", "doc3.csv"]
results = printer.print_batch(files, fallback_to_pdf=True)

print(f"Processed {results['total_files']} files")
print(f"Success rate: {results['successful_prints']}/{results['total_files']}")

# Generate PDFs for multiple files
results = printer.generate_batch_pdfs(files)
print(f"Generated {results['successful_pdfs']} PDFs")
```

### Configuration (NEW in v3.0)

```python
from universal_printer import DocumentPrinter, PrinterConfig

# Create custom configuration
config = PrinterConfig()
config.pdf.font_size = 12
config.pdf.margin_left = 60
config.logging.level = "DEBUG"

# Use custom configuration
printer = DocumentPrinter(config=config)

# Or load from file
printer = DocumentPrinter(config_file="my_config.json")
```

## 🖥️ Command Line Interface (NEW in v3.0)

Universal Printer now includes a powerful CLI for all operations:

```bash
# Print a file
universal-printer print document.txt
universal-printer print --printer "HP LaserJet" document.pdf

# Generate PDF
universal-printer pdf document.md --output formatted_doc
universal-printer pdf "Hello, World!" --output hello

# Batch operations
universal-printer batch-print *.txt --no-fallback
universal-printer batch-pdf *.md --report results.json

# Get information
universal-printer info --file document.txt
universal-printer info  # Show general info

# Configuration
universal-printer config --create config.json
universal-printer config --show default
```

## 📊 What's New in v3.0

### Enhanced PDF Generation
- **Markdown Support**: Full conversion of headers, lists, code blocks, emphasis
- **CSV Tables**: Automatic column alignment and table formatting  
- **JSON Formatting**: Pretty printing with proper indentation
- **Professional Output**: Clean, readable PDFs with metadata

### Advanced Features
- **Batch Processing**: Handle multiple files efficiently
- **Configuration System**: Customize behavior via JSON config files
- **Statistics Tracking**: Monitor performance and success rates
- **CLI Interface**: Complete command-line tool
- **Better Error Handling**: Detailed exceptions and error recovery

### Performance Improvements
- **Optimized PDF Generation**: Faster processing for large files
- **Memory Efficiency**: Better handling of large documents
- **Concurrent Processing**: Improved batch operation performance

## Supported File Types

The library can handle any file type, with optimized support for:

- **Documents**: `.pdf`, `.doc`, `.docx`, `.rtf`, `.odt`
- **Text files**: `.txt`, `.csv`, `.json`, `.xml`, `.html`, `.htm`, `.md`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`
- **Any other file type**: Will attempt to print or create PDF representation

## API Reference

### DocumentPrinter

#### `__init__()`
Creates a new DocumentPrinter instance with automatic file type detection.

#### `print_document(content_or_path, printer_name=None, fallback_to_pdf=True, pdf_filename=None)`
Universal method to print text content or any file type.

**Parameters:**
- `content_or_path` (str): Text content or path to any file type
- `printer_name` (str, optional): Name of printer to use, or "PDF" for print-to-PDF
- `fallback_to_pdf` (bool): Create PDF if printing fails (default: True)
- `pdf_filename` (str, optional): Custom filename for PDF fallback

**Returns:**
- `tuple`: (success: bool, message: str, pdf_path: str or None)

#### `print_text(text, printer_name=None, fallback_to_pdf=True, pdf_filename=None)`
Convenience method specifically for printing text content.

#### `print_file(file_path, printer_name=None, fallback_to_pdf=True, pdf_filename=None)`
Convenience method specifically for printing files.

#### `get_supported_file_types()`
Returns set of file extensions optimized for direct printing.

#### `is_file_printable(file_path)`
Check if a file type is directly supported for printing.

#### `generate_pdf(content_or_path, pdf_filename=None)`
Generate a PDF directly from text content or supported file types (.txt, .md, .csv, .json).
This method bypasses printing and creates a PDF directly with enhanced formatting.

**Parameters:**
- `content_or_path` (str): Text content or path to supported file type
- `pdf_filename` (str, optional): Custom filename for PDF output

**Returns:**
- `tuple`: (success: bool, message: str, pdf_path: str or None)

## Examples

### Print Text Content

```python
from universal_printer import DocumentPrinter

printer = DocumentPrinter()

# Simple text printing
success, msg, pdf = printer.print_text("Hello, World!")
print(f"Result: {success}, Message: {msg}")

# Multi-line text with custom PDF name
text_content = """
Invoice #12345
Date: 2024-01-01
Amount: $100.00
Thank you for your business!
"""
success, msg, pdf = printer.print_text(
    text_content,
    pdf_filename="invoice_12345.pdf"
)
```

### Print Various File Types

```python
# Print a PDF document
success, msg, pdf = printer.print_file("/path/to/document.pdf")

# Print a Word document
success, msg, pdf = printer.print_file("/path/to/report.docx")

# Print an image
success, msg, pdf = printer.print_file("/path/to/photo.jpg")

# Print HTML file
success, msg, pdf = printer.print_file("/path/to/webpage.html")

# Print CSV data
success, msg, pdf = printer.print_file("/path/to/data.csv")

# Print Markdown file
success, msg, pdf = printer.print_file("/path/to/document.md")
```

### Advanced Usage

```python
# Check if file type is supported
if printer.is_file_printable("/path/to/document.pdf"):
    print("PDF files are directly printable")

# Get all supported file types
supported_types = printer.get_supported_file_types()
print(f"Supported types: {supported_types}")

# Print to specific printer
success, msg, pdf = printer.print_document(
    "Important memo",
    printer_name="HP_LaserJet_Pro"
)

# Print to PDF (bypass physical printer)
success, msg, pdf = printer.print_document(
    "Save as PDF",
    printer_name="PDF",
    pdf_filename="saved_document.pdf"
)
```

### Error Handling and File Detection

```python
# The library automatically detects file types
success, msg, pdf = printer.print_file("unknown_file.xyz")
# Will attempt to print or create PDF representation

# Handle binary files gracefully
success, msg, pdf = printer.print_file("/path/to/program.exe")
# Creates PDF with file information for binary files

# Disable PDF fallback for testing
success, msg, pdf = printer.print_text(
    "Print or fail",
    fallback_to_pdf=False
)
if not success:
    print("Printing failed and no PDF was created")
```

### Enhanced PDF Generation

Generate PDFs directly from supported file types with enhanced formatting:

```python
# Generate PDF from text content
success, msg, pdf_path = printer.generate_pdf(
    "Hello, World!\nThis will be formatted nicely in the PDF.",
    pdf_filename="my_text_document"
)

# Generate PDF from Markdown file with enhanced formatting
success, msg, pdf_path = printer.generate_pdf(
    "/path/to/document.md",
    pdf_filename="formatted_markdown"
)

# Generate PDF from CSV with table formatting
success, msg, pdf_path = printer.generate_pdf(
    "/path/to/data.csv",
    pdf_filename="formatted_table"
)

# Generate PDF from JSON with pretty formatting
success, msg, pdf_path = printer.generate_pdf(
    "/path/to/config.json",
    pdf_filename="formatted_json"
)

if success:
    print(f"Enhanced PDF created: {pdf_path}")
else:
    print(f"PDF generation failed: {msg}")
```

## Platform-Specific Behavior

### Windows
- Uses `rundll32.exe` with shell print verb for all file types
- Falls back to Notepad for text files if needed
- Supports "Microsoft Print to PDF" printer
- Handles Office documents, images, and PDFs natively

### macOS/Linux
- Uses `lp` command (CUPS) for all file types
- Supports print-to-PDF with CUPS
- Handles various file formats through system print drivers
- Requires printer to be configured in system

## File Type Detection

The library includes intelligent file type detection:

- **MIME type detection**: Automatic detection using Python's `mimetypes`
- **Extension-based fallback**: Uses file extensions when MIME detection fails
- **Binary file handling**: Creates descriptive PDF for non-text binary files
- **Encoding detection**: Handles various text encodings (UTF-8, Latin-1)

## PDF Fallback Features

Enhanced PDF fallback system:

- **Smart content handling**: Different handling for text vs binary files
- **Enhanced formatting**: Special formatting for .txt, .md, .csv, and .json files
- **Markdown support**: Converts markdown syntax to formatted text in PDF
- **CSV table formatting**: Displays CSV data in properly aligned table format
- **JSON pretty printing**: Formats JSON with proper indentation and structure
- **File information**: Includes file metadata in PDF for binary files
- **Error recovery**: Multiple fallback levels for maximum reliability

## Requirements

- Python 3.7+
- No external dependencies
- Works on Windows, macOS, and Linux

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📈 API Reference (v3.0)

### DocumentPrinter Class

```python
from universal_printer import DocumentPrinter, PrinterConfig

# Initialize with optional configuration
printer = DocumentPrinter()
printer = DocumentPrinter(config=my_config)
printer = DocumentPrinter(config_file="config.json")
```

#### Core Methods

- `print_file(file_path, printer_name=None, fallback_to_pdf=True, pdf_filename=None)`
- `print_text(text, printer_name=None, fallback_to_pdf=True, pdf_filename=None)`
- `generate_pdf(content_or_path, pdf_filename=None)` - Direct PDF generation
- `print_batch(files, printer_name=None, fallback_to_pdf=True)` - Batch printing
- `generate_batch_pdfs(files, output_directory=None)` - Batch PDF generation

#### Utility Methods

- `get_statistics()` - Get performance statistics
- `get_file_info(file_path)` - Get comprehensive file information
- `validate_pdf(pdf_path)` - Validate PDF files
- `get_supported_formats()` - Get supported file formats by category
- `get_config()` - Get current configuration
- `update_config(**kwargs)` - Update configuration settings

### Configuration System

```python
from universal_printer import PrinterConfig

# Create and customize configuration
config = PrinterConfig()
config.pdf.font_size = 12
config.pdf.margin_left = 60
config.logging.level = "DEBUG"
config.print.enable_pdf_fallback = True

# Save/load configuration
config.save_to_file("my_config.json")
config = PrinterConfig("my_config.json")
```

## 🔧 Requirements

- **Python**: 3.7 or higher
- **Dependencies**: None (uses only Python standard library)
- **Operating Systems**: Windows, macOS, Linux
- **Permissions**: Read access to files, write access to output directory

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/sharathkumardaroor/universal-printer/issues)
- **Documentation**: [GitHub Wiki](https://github.com/sharathkumardaroor/universal-printer/wiki)
- **Email**: sharathkumardaroor@gmail.com

## 🏆 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### v3.0.0 Highlights
- Complete rewrite with enhanced PDF generation
- Configuration system and CLI interface
- Batch processing capabilities
- Advanced file type detection
- Professional PDF output with intelligent formatting