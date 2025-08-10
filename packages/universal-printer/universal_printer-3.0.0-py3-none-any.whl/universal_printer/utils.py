"""
Utility classes and functions for Universal Printer.

This module provides helper classes and functions for file type detection,
PDF validation, and other common operations.
"""

import os
import mimetypes
import re
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileTypeDetector:
    """Advanced file type detection and analysis."""
    
    # Enhanced file type mappings
    PRINTABLE_TYPES = {
        '.pdf', '.doc', '.docx', '.rtf', '.odt',  # Documents
        '.txt', '.csv', '.json', '.xml', '.html', '.htm', '.md',  # Text files
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'  # Images
    }
    
    ENHANCED_PDF_TYPES = {'.txt', '.md', '.csv', '.json'}
    
    TEXT_TYPES = {
        '.txt', '.csv', '.json', '.xml', '.html', '.htm', '.md',
        '.py', '.js', '.css', '.yaml', '.yml', '.ini', '.cfg',
        '.log', '.sql', '.sh', '.bat', '.ps1'
    }
    
    BINARY_TYPES = {
        '.pdf', '.doc', '.docx', '.rtf', '.odt',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.exe', '.dll', '.so', '.dylib'
    }
    
    @classmethod
    def detect_file_type(cls, file_path: Path) -> Tuple[str, bool, bool, bool]:
        """
        Detect file type and properties.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (mime_type, is_text, is_printable, supports_enhanced_pdf)
        """
        if not file_path.exists():
            return 'application/octet-stream', False, False, False
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        suffix = file_path.suffix.lower()
        
        # Determine properties
        is_text = (
            mime_type.startswith('text/') or 
            suffix in cls.TEXT_TYPES or
            cls._is_text_content(file_path)
        )
        
        is_printable = suffix in cls.PRINTABLE_TYPES
        supports_enhanced_pdf = suffix in cls.ENHANCED_PDF_TYPES
        
        return mime_type, is_text, is_printable, supports_enhanced_pdf
    
    @classmethod
    def _is_text_content(cls, file_path: Path, sample_size: int = 1024) -> bool:
        """
        Check if file contains text content by sampling.
        
        Args:
            file_path: Path to the file
            sample_size: Number of bytes to sample
            
        Returns:
            True if file appears to contain text
        """
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
            
            if not sample:
                return True  # Empty file is considered text
            
            # Check for null bytes (common in binary files)
            if b'\x00' in sample:
                return False
            
            # Try to decode as UTF-8
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                pass
            
            # Try other common encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    sample.decode(encoding)
                    return True
                except UnicodeDecodeError:
                    continue
            
            return False
            
        except Exception:
            return False
    
    @classmethod
    def get_file_info(cls, file_path: Path) -> Dict[str, Any]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        if not file_path.exists():
            return {'exists': False}
        
        stat = file_path.stat()
        mime_type, is_text, is_printable, supports_enhanced_pdf = cls.detect_file_type(file_path)
        
        return {
            'exists': True,
            'name': file_path.name,
            'stem': file_path.stem,
            'suffix': file_path.suffix,
            'size': stat.st_size,
            'size_human': cls._format_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'mime_type': mime_type,
            'is_text': is_text,
            'is_printable': is_printable,
            'supports_enhanced_pdf': supports_enhanced_pdf,
            'is_readable': os.access(file_path, os.R_OK),
            'is_writable': os.access(file_path, os.W_OK)
        }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


class PDFValidator:
    """PDF file validation and analysis."""
    
    PDF_HEADER = b'%PDF-'
    PDF_FOOTER = b'%%EOF'
    
    @classmethod
    def is_valid_pdf(cls, file_path: Path) -> bool:
        """
        Check if file is a valid PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            True if file is a valid PDF
        """
        try:
            if not file_path.exists() or file_path.stat().st_size == 0:
                return False
            
            with open(file_path, 'rb') as f:
                # Check header
                header = f.read(8)
                if not header.startswith(cls.PDF_HEADER):
                    return False
                
                # Check footer (last 1024 bytes)
                f.seek(max(0, file_path.stat().st_size - 1024))
                footer_content = f.read()
                if cls.PDF_FOOTER not in footer_content:
                    return False
                
                return True
                
        except Exception as e:
            logger.debug(f"PDF validation error: {e}")
            return False
    
    @classmethod
    def get_pdf_info(cls, file_path: Path) -> Dict[str, Any]:
        """
        Get PDF file information.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        info = {
            'is_valid': False,
            'version': None,
            'size': 0,
            'pages': None,
            'encrypted': False
        }
        
        try:
            if not file_path.exists():
                return info
            
            info['size'] = file_path.stat().st_size
            
            with open(file_path, 'rb') as f:
                # Read first 1024 bytes for analysis
                header_content = f.read(1024)
                
                # Check if valid PDF
                if not header_content.startswith(cls.PDF_HEADER):
                    return info
                
                info['is_valid'] = True
                
                # Extract version
                version_match = re.search(rb'%PDF-(\d+\.\d+)', header_content)
                if version_match:
                    info['version'] = version_match.group(1).decode('ascii')
                
                # Check for encryption
                if b'/Encrypt' in header_content:
                    info['encrypted'] = True
                
                # Try to count pages (basic method)
                f.seek(0)
                content = f.read()
                page_matches = re.findall(rb'/Type\s*/Page[^s]', content)
                if page_matches:
                    info['pages'] = len(page_matches)
                
        except Exception as e:
            logger.debug(f"PDF info extraction error: {e}")
        
        return info


class ContentFormatter:
    """Advanced content formatting for different file types."""
    
    @staticmethod
    def format_markdown(content: str) -> str:
        """
        Format Markdown content for PDF generation.
        
        Args:
            content: Raw Markdown content
            
        Returns:
            Formatted content for PDF
        """
        lines = content.splitlines()
        formatted_lines = []
        in_code_block = False
        
        for line in lines:
            line = line.rstrip()
            
            # Handle code blocks
            if line.startswith('```'):
                in_code_block = not in_code_block
                if in_code_block:
                    formatted_lines.append("┌─ CODE BLOCK ─────────────────────────────────────────┐")
                else:
                    formatted_lines.append("└──────────────────────────────────────────────────────┘")
                continue
            
            if in_code_block:
                formatted_lines.append(f"│ {line:<52} │")
                continue
            
            # Headers
            if line.startswith('# '):
                title = line[2:].strip()
                formatted_lines.append(f"\n{title.upper()}")
                formatted_lines.append("=" * len(title))
            elif line.startswith('## '):
                title = line[3:].strip()
                formatted_lines.append(f"\n{title}")
                formatted_lines.append("-" * len(title))
            elif line.startswith('### '):
                title = line[4:].strip()
                formatted_lines.append(f"\n{title}")
                formatted_lines.append("·" * len(title))
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                formatted_lines.append(f"  • {line[2:]}")
            elif re.match(r'^\d+\.\s', line):
                formatted_lines.append(f"  {line}")
            
            # Emphasis
            elif line.startswith('> '):
                formatted_lines.append(f"┃ {line[2:]}")
            
            # Regular text with inline formatting
            else:
                # Bold text
                line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove ** but keep content
                # Italic text  
                line = re.sub(r'\*(.*?)\*', r'\1', line)  # Remove * but keep content
                # Inline code
                line = re.sub(r'`(.*?)`', r'[\1]', line)  # Convert `code` to [code]
                
                if line.strip():
                    formatted_lines.append(line)
                else:
                    formatted_lines.append("")
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_csv(content: str, max_rows: int = 100) -> str:
        """
        Format CSV content for PDF generation.
        
        Args:
            content: Raw CSV content
            max_rows: Maximum number of rows to include
            
        Returns:
            Formatted content for PDF
        """
        lines = content.splitlines()
        if not lines:
            return content
        
        # Detect delimiter
        first_line = lines[0]
        delimiter = ','
        for delim in [',', ';', '\t', '|']:
            if delim in first_line:
                delimiter = delim
                break
        
        # Parse CSV
        rows = []
        for line in lines[:max_rows]:
            # Simple CSV parsing (doesn't handle quoted fields with delimiters)
            row = [cell.strip().strip('"\'') for cell in line.split(delimiter)]
            rows.append(row)
        
        if not rows:
            return content
        
        # Calculate column widths
        max_widths = []
        for row in rows:
            for i, cell in enumerate(row):
                if i >= len(max_widths):
                    max_widths.append(0)
                max_widths[i] = max(max_widths[i], len(str(cell)))
        
        # Format as table
        formatted_lines = []
        
        # Header
        if rows:
            header_row = []
            for i, cell in enumerate(rows[0]):
                width = max_widths[i] if i < len(max_widths) else 10
                header_row.append(str(cell).ljust(width))
            formatted_lines.append(" │ ".join(header_row))
            
            # Separator
            separator = []
            for i in range(len(rows[0])):
                width = max_widths[i] if i < len(max_widths) else 10
                separator.append("─" * width)
            formatted_lines.append("─┼─".join(separator))
        
        # Data rows
        for row in rows[1:]:
            data_row = []
            for i, cell in enumerate(row):
                width = max_widths[i] if i < len(max_widths) else 10
                data_row.append(str(cell).ljust(width))
            formatted_lines.append(" │ ".join(data_row))
        
        # Add truncation notice if needed
        if len(lines) > max_rows:
            formatted_lines.append("")
            formatted_lines.append(f"... ({len(lines) - max_rows} more rows truncated)")
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_json(content: str) -> str:
        """
        Format JSON content for PDF generation.
        
        Args:
            content: Raw JSON content
            
        Returns:
            Formatted content for PDF
        """
        try:
            import json
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
        except json.JSONDecodeError:
            # If JSON is invalid, return original content
            return content
    
    @staticmethod
    def format_text(content: str) -> str:
        """
        Format plain text content for PDF generation.
        
        Args:
            content: Raw text content
            
        Returns:
            Formatted content for PDF
        """
        # Simple text formatting - preserve original but clean up
        lines = content.splitlines()
        formatted_lines = []
        
        for line in lines:
            # Remove excessive whitespace but preserve intentional spacing
            cleaned_line = re.sub(r'[ \t]+', ' ', line.rstrip())
            formatted_lines.append(cleaned_line)
        
        return '\n'.join(formatted_lines)