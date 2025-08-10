"""
Configuration management for Universal Printer.

This module provides configuration classes and utilities for customizing
the behavior of the Universal Printer library.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from .exceptions import ConfigurationError


@dataclass
class PDFConfig:
    """Configuration for PDF generation."""
    
    # Page settings
    page_width: int = 612  # Letter size width in points
    page_height: int = 792  # Letter size height in points
    margin_left: int = 50
    margin_right: int = 50
    margin_top: int = 50
    margin_bottom: int = 50
    
    # Font settings
    font_name: str = "Helvetica"
    font_size: int = 10
    title_font_size: int = 16
    header_font_size: int = 14
    line_height: int = 14
    
    # Content settings
    max_lines_per_page: int = 50
    word_wrap_length: int = 80
    table_column_padding: int = 2
    
    # Metadata
    include_metadata: bool = True
    creator: str = "Universal Printer v3.0"
    producer: str = "Universal Printer"
    
    def validate(self) -> None:
        """Validate configuration values."""
        if self.page_width <= 0 or self.page_height <= 0:
            raise ConfigurationError("Page dimensions must be positive")
        
        if any(margin < 0 for margin in [self.margin_left, self.margin_right, 
                                        self.margin_top, self.margin_bottom]):
            raise ConfigurationError("Margins cannot be negative")
        
        if self.font_size <= 0 or self.title_font_size <= 0 or self.header_font_size <= 0:
            raise ConfigurationError("Font sizes must be positive")
        
        if self.line_height <= 0:
            raise ConfigurationError("Line height must be positive")


@dataclass
class PrintConfig:
    """Configuration for printing operations."""
    
    # Printer settings
    default_printer: Optional[str] = None
    print_command_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Fallback settings
    enable_pdf_fallback: bool = True
    fallback_directory: Optional[str] = None
    auto_open_fallback: bool = False
    
    # Platform-specific settings
    windows_print_method: str = "shell"  # "shell" or "win32print"
    unix_print_command: str = "lp"  # "lp" or "lpr"
    macos_print_options: List[str] = None
    
    def __post_init__(self):
        if self.macos_print_options is None:
            self.macos_print_options = ["-o", "media=Letter"]
    
    def validate(self) -> None:
        """Validate configuration values."""
        if self.print_command_timeout <= 0:
            raise ConfigurationError("Print command timeout must be positive")
        
        if self.retry_attempts < 0:
            raise ConfigurationError("Retry attempts cannot be negative")
        
        if self.retry_delay < 0:
            raise ConfigurationError("Retry delay cannot be negative")
        
        if self.windows_print_method not in ["shell", "win32print"]:
            raise ConfigurationError("Invalid Windows print method")
        
        if self.unix_print_command not in ["lp", "lpr"]:
            raise ConfigurationError("Invalid Unix print command")


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    
    def validate(self) -> None:
        """Validate configuration values."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ConfigurationError(f"Invalid log level. Must be one of: {valid_levels}")
        
        if self.max_file_size <= 0:
            raise ConfigurationError("Max file size must be positive")
        
        if self.backup_count < 0:
            raise ConfigurationError("Backup count cannot be negative")


class PrinterConfig:
    """Main configuration class for Universal Printer."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (JSON format)
        """
        self.pdf = PDFConfig()
        self.print = PrintConfig()
        self.logging = LoggingConfig()
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
        
        # Load from environment variables
        self._load_from_env()
        
        # Validate all configurations
        self.validate()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # PDF settings
        if os.getenv("UP_PDF_FONT_SIZE"):
            try:
                self.pdf.font_size = int(os.getenv("UP_PDF_FONT_SIZE"))
            except ValueError:
                pass
        
        if os.getenv("UP_PDF_MARGIN"):
            try:
                margin = int(os.getenv("UP_PDF_MARGIN"))
                self.pdf.margin_left = margin
                self.pdf.margin_right = margin
                self.pdf.margin_top = margin
                self.pdf.margin_bottom = margin
            except ValueError:
                pass
        
        # Print settings
        if os.getenv("UP_DEFAULT_PRINTER"):
            self.print.default_printer = os.getenv("UP_DEFAULT_PRINTER")
        
        if os.getenv("UP_FALLBACK_DIR"):
            self.print.fallback_directory = os.getenv("UP_FALLBACK_DIR")
        
        if os.getenv("UP_ENABLE_FALLBACK"):
            self.print.enable_pdf_fallback = os.getenv("UP_ENABLE_FALLBACK").lower() == "true"
        
        # Logging settings
        if os.getenv("UP_LOG_LEVEL"):
            self.logging.level = os.getenv("UP_LOG_LEVEL").upper()
        
        if os.getenv("UP_LOG_FILE"):
            self.logging.file_path = os.getenv("UP_LOG_FILE")
    
    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_file}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update PDF config
            if 'pdf' in config_data:
                for key, value in config_data['pdf'].items():
                    if hasattr(self.pdf, key):
                        setattr(self.pdf, key, value)
            
            # Update print config
            if 'print' in config_data:
                for key, value in config_data['print'].items():
                    if hasattr(self.print, key):
                        setattr(self.print, key, value)
            
            # Update logging config
            if 'logging' in config_data:
                for key, value in config_data['logging'].items():
                    if hasattr(self.logging, key):
                        setattr(self.logging, key, value)
                        
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration file: {e}")
    
    def save_to_file(self, config_file: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config_file: Path to save configuration file
        """
        try:
            config_data = {
                'pdf': asdict(self.pdf),
                'print': asdict(self.print),
                'logging': asdict(self.logging)
            }
            
            config_path = Path(config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration file: {e}")
    
    def validate(self) -> None:
        """Validate all configuration sections."""
        self.pdf.validate()
        self.print.validate()
        self.logging.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'pdf': asdict(self.pdf),
            'print': asdict(self.print),
            'logging': asdict(self.logging)
        }
    
    def get_downloads_path(self) -> Path:
        """Get the downloads directory path."""
        if self.print.fallback_directory:
            return Path(self.print.fallback_directory)
        
        # Default downloads path based on OS
        home = Path.home()
        if os.name == 'nt':  # Windows
            return home / "Downloads"
        else:  # Unix-like systems
            return home / "Downloads"
    
    @classmethod
    def create_default_config(cls, config_file: str) -> 'PrinterConfig':
        """
        Create a default configuration file.
        
        Args:
            config_file: Path to create configuration file
            
        Returns:
            PrinterConfig instance
        """
        config = cls()
        config.save_to_file(config_file)
        return config