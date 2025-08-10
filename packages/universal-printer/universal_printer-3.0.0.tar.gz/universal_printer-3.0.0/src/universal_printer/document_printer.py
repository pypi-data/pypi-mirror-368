import os
import platform
import subprocess
import tempfile
import logging
import mimetypes
import base64
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Union, Tuple, Optional, List, Dict, Any

from .config import PrinterConfig
from .exceptions import (
    UniversalPrinterError, PrintingError, PDFGenerationError,
    FileNotFoundError as UPFileNotFoundError, UnsupportedFileTypeError
)
from .utils import FileTypeDetector, PDFValidator, ContentFormatter

logger = logging.getLogger(__name__)


class DocumentPrinter:
    """
    Cross-platform document printer with enhanced PDF generation capabilities.
    
    Version 3.0 Features:
    - Enhanced PDF generation with intelligent formatting
    - Advanced Markdown support with syntax conversion
    - CSV table formatting with proper alignment
    - JSON pretty printing with structure preservation
    - Configurable settings and behavior
    - Improved error handling with custom exceptions
    - Batch processing capabilities
    - Professional PDF output with metadata
    """

    def __init__(self, config: Optional[PrinterConfig] = None, config_file: Optional[str] = None):
        """
        Initialize DocumentPrinter with optional configuration.
        
        Args:
            config: PrinterConfig instance for custom settings
            config_file: Path to configuration file (JSON format)
        """
        # Load configuration
        if config:
            self.config = config
        elif config_file:
            self.config = PrinterConfig(config_file)
        else:
            self.config = PrinterConfig()
        
        # System information
        self.system = platform.system()
        self.downloads_path = self.config.get_downloads_path()
        
        # File type detector and utilities
        self.file_detector = FileTypeDetector()
        self.pdf_validator = PDFValidator()
        self.content_formatter = ContentFormatter()
        
        # Supported file types for direct printing
        self.printable_types = self.file_detector.PRINTABLE_TYPES.copy()
        
        # Statistics tracking
        self.stats = {
            'total_prints': 0,
            'successful_prints': 0,
            'pdf_fallbacks': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        # Initialize mimetypes and logging
        mimetypes.init()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_config = self.config.logging
        
        # Set log level
        numeric_level = getattr(logging, log_config.level.upper(), logging.INFO)
        logger.setLevel(numeric_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        if log_config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_level)
            formatter = logging.Formatter(log_config.format)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if log_config.file_path:
            try:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    log_config.file_path,
                    maxBytes=log_config.max_file_size,
                    backupCount=log_config.backup_count
                )
                file_handler.setLevel(numeric_level)
                formatter = logging.Formatter(log_config.format)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not setup file logging: {e}")

    def _detect_file_type(self, file_path: Path) -> tuple:
        """
        Detect file type and return (mime_type, is_text, is_printable, supports_enhanced_pdf)
        """
        return self.file_detector.detect_file_type(file_path)
    
    def _read_file_content(self, file_path: Path) -> str:
        """
        Read file content as text. For binary files, return a description.
        """
        mime_type, is_text, _, _ = self._detect_file_type(file_path)
        
        if is_text:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        return f.read()
                except Exception:
                    return f"[Binary file: {file_path.name}]\nMIME Type: {mime_type}\nSize: {file_path.stat().st_size} bytes"
        else:
            # For binary files, create a text representation
            size = file_path.stat().st_size
            return f"""File Information:
Name: {file_path.name}
Type: {mime_type}
Size: {size:,} bytes
Path: {file_path}

[This is a binary file that cannot be displayed as text]
[Original file will be sent to printer if supported]"""

    def _write_temp_text(self, content) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        f.write(str(content))
        f.flush()
        f.close()
        return Path(f.name)
    
    def _prepare_file_for_printing(self, content_or_path) -> tuple:
        """
        Prepare content for printing. Returns (file_path, is_temp_file, original_content)
        """
        if isinstance(content_or_path, (str, Path)) and Path(content_or_path).exists():
            # It's an existing file
            file_path = Path(content_or_path)
            original_content = self._read_file_content(file_path)
            return file_path, False, original_content
        else:
            # It's text content - create temp file
            file_path = self._write_temp_text(content_or_path)
            return file_path, True, str(content_or_path)

    def _write_minimal_pdf(self, content, output_path: Path) -> bool:
        """
        Very naive PDF writer: places text in a single page using default fonts.
        Not full-featured; works for basic ASCII lines. 
        """
        try:
            lines = str(content).splitlines()
            # PDF objects
            objs = []
            xref_offsets = []

            def add_obj(s):
                xref_offsets.append(len(b''.join(objs)))
                objs.append(s)
                return len(xref_offsets)  # object number

            # Catalog
            # Prepare content stream: simple text using BT/ET
            text_lines = []
            text_lines.append("BT /F1 12 Tf 50 750 Td")
            for line in lines:
                safe = line.replace("(", "\\(").replace(")", "\\)")
                text_lines.append(f"({safe}) Tj 0 -14 Td")
            text_stream = "\n".join(text_lines)
            stream = f"""q
1 0 0 1 0 0 cm
BT
/F1 12 Tf
50 750 Td
{text_stream}
ET
Q
"""
            # Create font object
            font_obj_num = add_obj(f"""<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>""".encode("utf-8"))
            # Content stream object
            content_stream_bytes = stream.encode("utf-8")
            content_obj_num = add_obj(
                f"""<< /Length {len(content_stream_bytes)} >>\nstream\n{stream}\nendstream""".encode("utf-8")
            )
            # Page object
            page_obj_num = add_obj(
                f"""<< /Type /Page /Parent 4 0 R /Resources << /Font << /F1 {font_obj_num} 0 R >> >> /Contents {content_obj_num} 0 R /MediaBox [0 0 612 792] >>""".encode("utf-8")
            )
            # Pages root
            pages_obj_num = add_obj(
                f"""<< /Type /Pages /Kids [ {page_obj_num} 0 R ] /Count 1 >>""".encode("utf-8")
            )
            # Catalog
            catalog_obj_num = add_obj(f"""<< /Type /Catalog /Pages {pages_obj_num} 0 R >>""".encode("utf-8"))

            # Build PDF binary
            pdf = b"%PDF-1.4\n"
            # write objects with numbering
            for idx, obj in enumerate(objs, start=1):
                xref_offsets[idx - 1] = len(pdf)
                pdf += f"{idx} 0 obj\n".encode("utf-8")
                if isinstance(obj, bytes):
                    pdf += obj
                else:
                    pdf += obj.encode("utf-8")
                pdf += b"\nendobj\n"
            # xref
            xref_start = len(pdf)
            pdf += b"xref\n"
            pdf += f"0 {len(objs)+1}\n".encode("utf-8")
            pdf += b"0000000000 65535 f \n"
            for offset in xref_offsets:
                pdf += f"{offset:010d} 00000 n \n".encode("utf-8")
            # trailer
            pdf += b"trailer\n"
            pdf += f"""<< /Size {len(objs)+1} /Root {catalog_obj_num} 0 R >>\n""".encode("utf-8")
            pdf += b"startxref\n"
            pdf += f"{xref_start}\n".encode("utf-8")
            pdf += b"%%EOF\n"

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(pdf)
            logger.info(f"Minimal PDF written to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write minimal PDF: {e}")
            return False

    def _format_text_for_pdf(self, content: str, file_type: str = 'txt') -> str:
        """
        Format text content for better PDF presentation based on file type.
        """
        if file_type == 'md':
            return self.content_formatter.format_markdown(content)
        elif file_type == 'csv':
            return self.content_formatter.format_csv(content)
        elif file_type == 'json':
            return self.content_formatter.format_json(content)
        else:
            return self.content_formatter.format_text(content)

    def _write_enhanced_pdf(self, content: str, output_path: Path, file_type: str = 'txt') -> bool:
        """
        Enhanced PDF writer with better formatting for different file types.
        """
        try:
            # Format content based on file type
            formatted_content = self._format_text_for_pdf(content, file_type)
            lines = formatted_content.splitlines()
            
            # PDF objects
            objs = []
            xref_offsets = []

            def add_obj(s):
                xref_offsets.append(len(b''.join(objs)))
                objs.append(s)
                return len(xref_offsets)  # object number

            # Enhanced text formatting
            text_lines = []
            y_position = 750
            line_height = 14
            page_height = 792
            margin_bottom = 50
            
            # Add title based on file type
            title_map = {
                'txt': 'Text Document',
                'md': 'Markdown Document', 
                'json': 'JSON Document',
                'csv': 'CSV Data'
            }
            title = title_map.get(file_type, 'Document')
            
            text_lines.append("BT /F1 16 Tf 50 770 Td")
            text_lines.append(f"({title}) Tj")
            text_lines.append("0 -30 Td")
            text_lines.append("/F1 10 Tf")
            
            # Add content with proper line wrapping
            for line in lines:
                if y_position < margin_bottom:
                    # Would need new page - for now just truncate
                    text_lines.append("(...content truncated for PDF size limits...) Tj")
                    break
                    
                # Handle long lines by wrapping
                if len(line) > 80:
                    # Simple word wrapping
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word) > 80:
                            if current_line:
                                safe_line = current_line.replace("(", "\\(").replace(")", "\\)")
                                text_lines.append(f"({safe_line}) Tj 0 -{line_height} Td")
                                y_position -= line_height
                            current_line = word + " "
                        else:
                            current_line += word + " "
                    
                    if current_line.strip():
                        safe_line = current_line.strip().replace("(", "\\(").replace(")", "\\)")
                        text_lines.append(f"({safe_line}) Tj 0 -{line_height} Td")
                        y_position -= line_height
                else:
                    safe_line = line.replace("(", "\\(").replace(")", "\\)")
                    text_lines.append(f"({safe_line}) Tj 0 -{line_height} Td")
                    y_position -= line_height

            # Create content stream
            stream = f"""q
1 0 0 1 0 0 cm
BT
/F1 10 Tf
50 750 Td
{chr(10).join(text_lines)}
ET
Q
"""
            
            # Create font object
            font_obj_num = add_obj(f"""<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>""".encode("utf-8"))
            
            # Content stream object
            content_stream_bytes = stream.encode("utf-8")
            content_obj_num = add_obj(
                f"""<< /Length {len(content_stream_bytes)} >>\nstream\n{stream}\nendstream""".encode("utf-8")
            )
            
            # Page object
            page_obj_num = add_obj(
                f"""<< /Type /Page /Parent 4 0 R /Resources << /Font << /F1 {font_obj_num} 0 R >> >> /Contents {content_obj_num} 0 R /MediaBox [0 0 612 792] >>""".encode("utf-8")
            )
            
            # Pages root
            pages_obj_num = add_obj(
                f"""<< /Type /Pages /Kids [ {page_obj_num} 0 R ] /Count 1 >>""".encode("utf-8")
            )
            
            # Catalog
            catalog_obj_num = add_obj(f"""<< /Type /Catalog /Pages {pages_obj_num} 0 R >>""".encode("utf-8"))

            # Build PDF binary
            pdf = b"%PDF-1.4\n"
            # write objects with numbering
            for idx, obj in enumerate(objs, start=1):
                xref_offsets[idx - 1] = len(pdf)
                pdf += f"{idx} 0 obj\n".encode("utf-8")
                if isinstance(obj, bytes):
                    pdf += obj
                else:
                    pdf += obj.encode("utf-8")
                pdf += b"\nendobj\n"
                
            # xref
            xref_start = len(pdf)
            pdf += b"xref\n"
            pdf += f"0 {len(objs)+1}\n".encode("utf-8")
            pdf += b"0000000000 65535 f \n"
            for offset in xref_offsets:
                pdf += f"{offset:010d} 00000 n \n".encode("utf-8")
                
            # trailer
            pdf += b"trailer\n"
            pdf += f"""<< /Size {len(objs)+1} /Root {catalog_obj_num} 0 R >>\n""".encode("utf-8")
            pdf += b"startxref\n"
            pdf += f"{xref_start}\n".encode("utf-8")
            pdf += b"%%EOF\n"

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(pdf)
            logger.info(f"Enhanced PDF written to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write enhanced PDF: {e}")
            return False

    def _fallback_pdf_save(self, content, filename=None, file_type=None):
        if not filename:
            filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        elif not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        pdf_path = self.downloads_path / filename
        
        # Try enhanced PDF generation for supported file types
        if file_type and file_type.lower() in ['txt', 'md', 'json', 'csv']:
            success = self._write_enhanced_pdf(content, pdf_path, file_type.lower())
            if success:
                return pdf_path
        
        # Fallback to minimal PDF
        success = self._write_minimal_pdf(content, pdf_path)
        if success:
            return pdf_path
            
        # Last-resort: plain text with .pdf extension (warn)
        try:
            with open(pdf_path, "w", encoding="utf-8") as f:
                f.write("<< WARNING: Could not build PDF, fallback to text >>\n")
                f.write(str(content))
            logger.info(f"Fallback text-as-.pdf written to {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Final fallback write failed: {e}")
            return None

    def _print_unix(self, file_path: Path, printer_name=None, to_pdf_path: Path = None):
        cmd = ["lp"]
        if printer_name:
            cmd += ["-d", printer_name]
        if to_pdf_path:
            # CUPS print-to-file (PDF) if supported
            cmd += ["-o", f"outputfile={to_pdf_path}"]
        cmd.append(str(file_path))
        return subprocess.run(cmd, capture_output=True, check=True)

    def _print_windows(self, file_path: Path, printer_name=None):
        # If the user wants Microsoft Print to PDF, the system normally pops up a dialog.
        if printer_name and "Microsoft Print to PDF" in printer_name:
            # Use ShellExecute print verb
            subprocess.run(
                ["rundll32.exe", "shell32.dll,ShellExec_RunDLL", str(file_path), "print"],
                check=True,
            )
            return
        # Generic print via shell verb
        try:
            subprocess.run(
                ["rundll32.exe", "shell32.dll,ShellExec_RunDLL", str(file_path), "print"],
                check=True,
            )
        except subprocess.CalledProcessError:
            # Fallback to notepad for .txt
            if file_path.suffix.lower() == ".txt":
                cmd = f'notepad /P "{file_path}"'
                subprocess.run(cmd, shell=True, check=True)
            else:
                raise

    def print_document(self, content_or_path, printer_name=None, fallback_to_pdf=True, pdf_filename=None):
        """
        Print text content or any file type with PDF fallback support.
        
        Args:
            content_or_path: Text string or path to file (any type)
            printer_name: Optional printer name or "PDF" for print-to-PDF
            fallback_to_pdf: Create PDF if printing fails (default: True)
            pdf_filename: Custom filename for PDF fallback
            
        Returns:
            tuple: (success: bool, message: str, pdf_path_or_None: str)
        """
        temp_file = None
        try:
            # Prepare file for printing
            file_path, is_temp, original_content = self._prepare_file_for_printing(content_or_path)
            temp_file = file_path if is_temp else None
            
            # Detect file type for better handling
            mime_type, is_text, is_printable, _ = self._detect_file_type(file_path)
            
            logger.info(f"Printing file: {file_path.name} (Type: {mime_type})")
            
            # Attempt to print based on OS
            if self.system in ("Darwin", "Linux"):
                try:
                    # If printer_name indicates PDF, interpret as print-to-PDF
                    to_pdf = None
                    if printer_name and "pdf" in printer_name.lower():
                        default_pdf_name = pdf_filename or f"print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        to_pdf = self.downloads_path / default_pdf_name
                    
                    self._print_unix(file_path, printer_name=printer_name, to_pdf_path=to_pdf)
                    
                    if to_pdf:
                        return True, f"Printed to PDF: {to_pdf}", str(to_pdf)
                    else:
                        return True, f"Printed successfully via lp. File type: {mime_type}", None
                        
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Unix print failed: {e}; stderr: {getattr(e, 'stderr', None)}")
                    raise

            elif self.system == "Windows":
                try:
                    self._print_windows(file_path, printer_name=printer_name)
                    return True, f"Printed successfully on Windows. File type: {mime_type}", None
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Windows print failed: {e}")
                    raise

            else:
                return False, f"Unsupported OS: {self.system}", None

        except Exception as e:
            logger.error(f"Printing error: {e}")
            if fallback_to_pdf:
                # Use original content for PDF fallback
                content_for_pdf = original_content if 'original_content' in locals() else str(content_or_path)
                # Determine file type for enhanced PDF generation
                file_type = None
                if 'file_path' in locals():
                    file_type = file_path.suffix.lower().lstrip('.')
                pdf_path = self._fallback_pdf_save(content_for_pdf, pdf_filename, file_type)
                if pdf_path:
                    return False, f"Printing failed. PDF fallback saved to: {pdf_path}", str(pdf_path)
                else:
                    return False, "Printing failed. PDF fallback also failed.", None
            else:
                return False, "Printing failed and fallback disabled.", None
        finally:
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    logger.debug("Could not delete temp file; ignoring.")
    
    def print_file(self, file_path, printer_name=None, fallback_to_pdf=True, pdf_filename=None):
        """
        Convenience method to print any file type.
        
        Args:
            file_path: Path to file (any type: PDF, DOC, TXT, images, etc.)
            printer_name: Optional printer name
            fallback_to_pdf: Create PDF if printing fails (default: True)
            pdf_filename: Custom filename for PDF fallback
            
        Returns:
            tuple: (success: bool, message: str, pdf_path_or_None: str)
        """
        if not Path(file_path).exists():
            return False, f"File not found: {file_path}", None
            
        return self.print_document(file_path, printer_name, fallback_to_pdf, pdf_filename)
    
    def print_text(self, text, printer_name=None, fallback_to_pdf=True, pdf_filename=None):
        """
        Convenience method to print text content.
        
        Args:
            text: Text string to print
            printer_name: Optional printer name
            fallback_to_pdf: Create PDF if printing fails (default: True)
            pdf_filename: Custom filename for PDF fallback
            
        Returns:
            tuple: (success: bool, message: str, pdf_path_or_None: str)
        """
        return self.print_document(str(text), printer_name, fallback_to_pdf, pdf_filename)
    
    def print_batch(self, files: List[Union[str, Path]], printer_name: Optional[str] = None, 
                   fallback_to_pdf: bool = True) -> Dict[str, Any]:
        """
        Print multiple files in batch.
        
        Args:
            files: List of file paths to print
            printer_name: Optional printer name
            fallback_to_pdf: Create PDF if printing fails (default: True)
            
        Returns:
            Dictionary with batch processing results
        """
        results = {
            'total_files': len(files),
            'successful_prints': 0,
            'pdf_fallbacks': 0,
            'errors': 0,
            'results': [],
            'start_time': datetime.now(),
            'end_time': None,
            'duration': None
        }
        
        logger.info(f"Starting batch print of {len(files)} files")
        
        for i, file_path in enumerate(files, 1):
            try:
                file_path = Path(file_path)
                logger.info(f"Processing file {i}/{len(files)}: {file_path.name}")
                
                success, message, pdf_path = self.print_file(
                    str(file_path), printer_name, fallback_to_pdf
                )
                
                result = {
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'success': success,
                    'message': message,
                    'pdf_path': pdf_path,
                    'timestamp': datetime.now()
                }
                
                if success:
                    results['successful_prints'] += 1
                elif pdf_path:
                    results['pdf_fallbacks'] += 1
                else:
                    results['errors'] += 1
                
                results['results'].append(result)
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                results['errors'] += 1
                results['results'].append({
                    'file_path': str(file_path),
                    'file_name': getattr(file_path, 'name', str(file_path)),
                    'success': False,
                    'message': f"Processing error: {e}",
                    'pdf_path': None,
                    'timestamp': datetime.now()
                })
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info(f"Batch processing completed in {results['duration']:.2f}s")
        logger.info(f"Results: {results['successful_prints']} printed, "
                   f"{results['pdf_fallbacks']} PDF fallbacks, {results['errors']} errors")
        
        return results
    
    def generate_batch_pdfs(self, files: List[Union[str, Path]], 
                           output_directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate PDFs for multiple files in batch.
        
        Args:
            files: List of file paths to convert to PDF
            output_directory: Optional output directory (default: downloads)
            
        Returns:
            Dictionary with batch processing results
        """
        results = {
            'total_files': len(files),
            'successful_pdfs': 0,
            'errors': 0,
            'results': [],
            'start_time': datetime.now(),
            'end_time': None,
            'duration': None
        }
        
        logger.info(f"Starting batch PDF generation for {len(files)} files")
        
        for i, file_path in enumerate(files, 1):
            try:
                file_path = Path(file_path)
                logger.info(f"Processing file {i}/{len(files)}: {file_path.name}")
                
                # Generate custom filename
                pdf_filename = f"{file_path.stem}_converted"
                
                success, message, pdf_path = self.generate_pdf(
                    str(file_path), pdf_filename
                )
                
                result = {
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'success': success,
                    'message': message,
                    'pdf_path': pdf_path,
                    'timestamp': datetime.now()
                }
                
                if success:
                    results['successful_pdfs'] += 1
                else:
                    results['errors'] += 1
                
                results['results'].append(result)
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                results['errors'] += 1
                results['results'].append({
                    'file_path': str(file_path),
                    'file_name': getattr(file_path, 'name', str(file_path)),
                    'success': False,
                    'message': f"Processing error: {e}",
                    'pdf_path': None,
                    'timestamp': datetime.now()
                })
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info(f"Batch PDF generation completed in {results['duration']:.2f}s")
        logger.info(f"Results: {results['successful_pdfs']} PDFs created, {results['errors']} errors")
        
        return results
    
    def generate_pdf(self, content_or_path, pdf_filename=None):
        """
        Generate a PDF directly from text content or supported file types (.txt, .md, .csv, .json).
        This method bypasses printing and creates a PDF directly.
        
        Args:
            content_or_path: Text string or path to supported file type
            pdf_filename: Custom filename for PDF output
            
        Returns:
            tuple: (success: bool, message: str, pdf_path_or_None: str)
        """
        try:
            # Prepare content and determine file type
            if isinstance(content_or_path, Path):
                # It's a Path object
                if content_or_path.exists():
                    file_path = content_or_path
                    file_type = file_path.suffix.lower().lstrip('.')
                    
                    # Check if file type is supported for enhanced PDF generation
                    if file_type not in ['txt', 'md', 'csv', 'json']:
                        return False, f"PDF generation not supported for .{file_type} files. Supported types: .txt, .md, .csv, .json", None
                    
                    content = self._read_file_content(file_path)
                else:
                    return False, f"File not found: {content_or_path}", None
            elif isinstance(content_or_path, str):
                # Check if it's a file path (string) that exists
                try:
                    path_obj = Path(content_or_path)
                    if path_obj.exists() and path_obj.is_file():
                        # It's an existing file
                        file_path = path_obj
                        file_type = file_path.suffix.lower().lstrip('.')
                        
                        # Check if file type is supported for enhanced PDF generation
                        if file_type not in ['txt', 'md', 'csv', 'json']:
                            return False, f"PDF generation not supported for .{file_type} files. Supported types: .txt, .md, .csv, .json", None
                        
                        content = self._read_file_content(file_path)
                    else:
                        # It's text content
                        content = str(content_or_path)
                        file_type = 'txt'
                except (OSError, ValueError):
                    # Invalid path, treat as text content
                    content = str(content_or_path)
                    file_type = 'txt'
            else:
                # It's text content
                content = str(content_or_path)
                file_type = 'txt'
            
            # Generate PDF filename if not provided
            if not pdf_filename:
                pdf_filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            elif not pdf_filename.lower().endswith(".pdf"):
                pdf_filename += ".pdf"
            
            pdf_path = self.downloads_path / pdf_filename
            
            # Generate enhanced PDF
            success = self._write_enhanced_pdf(content, pdf_path, file_type)
            
            if success:
                return True, f"PDF generated successfully: {pdf_path}", str(pdf_path)
            else:
                return False, "Failed to generate PDF", None
                
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            return False, f"PDF generation failed: {e}", None
    
    def get_supported_file_types(self):
        """
        Get list of supported file types for direct printing.
        
        Returns:
            set: Set of supported file extensions
        """
        return self.printable_types.copy()
    
    def is_file_printable(self, file_path):
        """
        Check if a file type is directly printable.
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if file type is supported for direct printing
        """
        return Path(file_path).suffix.lower() in self.printable_types
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get printing statistics.
        
        Returns:
            Dictionary with statistics
        """
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'total_prints': self.stats['total_prints'],
            'successful_prints': self.stats['successful_prints'],
            'pdf_fallbacks': self.stats['pdf_fallbacks'],
            'errors': self.stats['errors'],
            'success_rate': (self.stats['successful_prints'] / max(1, self.stats['total_prints'])) * 100,
            'uptime_seconds': uptime,
            'start_time': self.stats['start_time'],
            'version': '3.0.0'
        }
    
    def reset_statistics(self) -> None:
        """Reset printing statistics."""
        self.stats = {
            'total_prints': 0,
            'successful_prints': 0,
            'pdf_fallbacks': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        logger.info("Statistics reset")
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        return self.file_detector.get_file_info(Path(file_path))
    
    def validate_pdf(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with validation results
        """
        return self.pdf_validator.get_pdf_info(Path(pdf_path))
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration.
        
        Returns:
            Dictionary with configuration
        """
        return self.config.to_dict()
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration settings.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config.pdf, key):
                setattr(self.config.pdf, key, value)
            elif hasattr(self.config.print, key):
                setattr(self.config.print, key, value)
            elif hasattr(self.config.logging, key):
                setattr(self.config.logging, key, value)
        
        # Re-validate configuration
        self.config.validate()
        
        # Re-setup logging if logging config changed
        if any(key.startswith('log') for key in kwargs.keys()):
            self._setup_logging()
        
        logger.info("Configuration updated")
    
    def save_config(self, config_file: str) -> None:
        """
        Save current configuration to file.
        
        Args:
            config_file: Path to save configuration file
        """
        self.config.save_to_file(config_file)
        logger.info(f"Configuration saved to {config_file}")
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get supported file formats by category.
        
        Returns:
            Dictionary with categorized file formats
        """
        return {
            'printable': sorted(list(self.printable_types)),
            'enhanced_pdf': sorted(list(self.file_detector.ENHANCED_PDF_TYPES)),
            'text_files': sorted(list(self.file_detector.TEXT_TYPES)),
            'binary_files': sorted(list(self.file_detector.BINARY_TYPES))
        }
