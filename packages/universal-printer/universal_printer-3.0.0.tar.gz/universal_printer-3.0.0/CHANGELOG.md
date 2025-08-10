# Changelog

All notable changes to Universal Printer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-08-09

### 🎉 Major Release - Complete Rewrite

#### Added
- **Enhanced PDF Generation**: Intelligent formatting for .txt, .md, .csv, and .json files
- **Advanced Markdown Support**: Full syntax conversion including headers, lists, code blocks, emphasis
- **CSV Table Formatting**: Proper column alignment and table structure in PDFs
- **JSON Pretty Printing**: Structured formatting with proper indentation
- **Configuration System**: Comprehensive configuration management with JSON support
- **Custom Exceptions**: Detailed error handling with specific exception types
- **Batch Processing**: Print or generate PDFs for multiple files at once
- **Statistics Tracking**: Monitor printing success rates and performance
- **CLI Interface**: Command-line tool for all operations
- **File Type Detection**: Advanced file analysis and validation
- **PDF Validation**: Verify PDF integrity and extract metadata
- **Logging System**: Configurable logging with file and console output
- **Professional PDF Output**: Enhanced PDF structure with metadata

#### Enhanced
- **Cross-platform Compatibility**: Improved support for Windows, macOS, and Linux
- **Error Handling**: Robust error recovery with detailed error messages
- **API Design**: Clean, intuitive API with comprehensive documentation
- **Performance**: Optimized PDF generation and file processing
- **Code Quality**: Type hints, comprehensive testing, and documentation

#### New Methods
- `print_batch()`: Print multiple files in one operation
- `generate_batch_pdfs()`: Generate PDFs for multiple files
- `get_statistics()`: Get printing and performance statistics
- `get_file_info()`: Get comprehensive file information
- `validate_pdf()`: Validate PDF files and extract metadata
- `get_config()`: Get current configuration
- `update_config()`: Update configuration settings
- `save_config()`: Save configuration to file
- `get_supported_formats()`: Get categorized supported file formats

#### New Classes
- `PrinterConfig`: Configuration management
- `FileTypeDetector`: Advanced file type detection
- `PDFValidator`: PDF validation and analysis
- `ContentFormatter`: Content formatting for different file types
- Custom exception classes for better error handling

#### CLI Commands
- `universal-printer print <file>`: Print a file
- `universal-printer pdf <input>`: Generate PDF
- `universal-printer batch-print <files>`: Batch printing
- `universal-printer batch-pdf <files>`: Batch PDF generation
- `universal-printer info`: Show system and file information
- `universal-printer config`: Configuration management

### Changed
- **Minimum Python Version**: Now requires Python 3.7+
- **Package Structure**: Reorganized for better maintainability
- **API**: Some method signatures updated for consistency
- **Dependencies**: Still dependency-free, uses only Python standard library

### Fixed
- **PDF Generation**: Improved reliability and error handling
- **File Encoding**: Better handling of different text encodings
- **Memory Usage**: Optimized for large file processing
- **Cross-platform Issues**: Resolved platform-specific printing problems

## [2.0.0] - 2024-08-04

### Added
- Universal file type support (PDF, DOC, images, etc.)
- Enhanced PDF fallback with better formatting
- New convenience methods: `print_text()`, `print_file()`
- `generate_pdf()` method for direct PDF creation
- Enhanced PDF formatting for .txt, .md, .csv, .json files
- Markdown support with syntax conversion
- CSV table formatting with proper alignment
- JSON pretty printing with indentation
- Automatic file type detection and MIME type handling
- Improved error handling and binary file support
- Better cross-platform compatibility
- File type checking utilities

### Changed
- Improved PDF generation with better formatting
- Enhanced error messages and logging
- Better file type detection

### Fixed
- Cross-platform printing issues
- PDF generation reliability
- File encoding problems

## [1.0.0] - 2024-07-15

### Added
- Initial release
- Basic cross-platform printing support
- Simple PDF fallback functionality
- Support for text files and basic document types
- Windows, macOS, and Linux compatibility
- Basic error handling

### Features
- Print text content directly
- Print common file types
- PDF fallback when printing fails
- Cross-platform support

---

## Migration Guide

### From v2.x to v3.0

#### Breaking Changes
1. **Constructor**: Now accepts optional `config` parameter
   ```python
   # Old
   printer = DocumentPrinter()
   
   # New
   printer = DocumentPrinter()  # Still works
   printer = DocumentPrinter(config=my_config)  # New option
   ```

2. **File Type Detection**: Returns additional information
   ```python
   # Old: (mime_type, is_text, is_printable)
   # New: (mime_type, is_text, is_printable, supports_enhanced_pdf)
   ```

#### New Features to Adopt
1. **Configuration System**:
   ```python
   from universal_printer import PrinterConfig
   config = PrinterConfig()
   config.pdf.font_size = 12
   printer = DocumentPrinter(config=config)
   ```

2. **Batch Processing**:
   ```python
   results = printer.print_batch(['file1.txt', 'file2.md'])
   ```

3. **Statistics**:
   ```python
   stats = printer.get_statistics()
   print(f"Success rate: {stats['success_rate']:.1f}%")
   ```

### From v1.x to v3.0

Version 3.0 is a complete rewrite with many new features. Consider it a new library with backward compatibility for basic operations.

Key improvements:
- Enhanced PDF generation
- Configuration system
- Batch processing
- Better error handling
- CLI interface
- Professional output quality