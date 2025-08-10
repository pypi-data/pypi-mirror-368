"""
Custom exceptions for Universal Printer.

This module defines custom exception classes for better error handling
and debugging in the Universal Printer library.
"""


class UniversalPrinterError(Exception):
    """Base exception class for Universal Printer."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} (Code: {self.error_code}, Details: {self.details})"
        return f"{self.message} (Code: {self.error_code})"


class PrintingError(UniversalPrinterError):
    """Exception raised when printing operations fail."""
    
    def __init__(self, message: str, printer_name: str = None, file_path: str = None, 
                 system_error: str = None):
        details = {}
        if printer_name:
            details['printer_name'] = printer_name
        if file_path:
            details['file_path'] = file_path
        if system_error:
            details['system_error'] = system_error
            
        super().__init__(message, "PRINTING_ERROR", details)
        self.printer_name = printer_name
        self.file_path = file_path
        self.system_error = system_error


class PDFGenerationError(UniversalPrinterError):
    """Exception raised when PDF generation fails."""
    
    def __init__(self, message: str, file_type: str = None, content_length: int = None,
                 output_path: str = None):
        details = {}
        if file_type:
            details['file_type'] = file_type
        if content_length is not None:
            details['content_length'] = content_length
        if output_path:
            details['output_path'] = output_path
            
        super().__init__(message, "PDF_GENERATION_ERROR", details)
        self.file_type = file_type
        self.content_length = content_length
        self.output_path = output_path


class FileNotFoundError(UniversalPrinterError):
    """Exception raised when a file is not found."""
    
    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"
        details = {'file_path': file_path}
        super().__init__(message, "FILE_NOT_FOUND", details)
        self.file_path = file_path


class UnsupportedFileTypeError(UniversalPrinterError):
    """Exception raised when a file type is not supported."""
    
    def __init__(self, file_type: str, supported_types: list = None):
        message = f"Unsupported file type: {file_type}"
        details = {'file_type': file_type}
        if supported_types:
            details['supported_types'] = supported_types
            message += f". Supported types: {', '.join(supported_types)}"
            
        super().__init__(message, "UNSUPPORTED_FILE_TYPE", details)
        self.file_type = file_type
        self.supported_types = supported_types


class ConfigurationError(UniversalPrinterError):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, config_value = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        if config_value is not None:
            details['config_value'] = str(config_value)
            
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key
        self.config_value = config_value


class PermissionError(UniversalPrinterError):
    """Exception raised when permission is denied."""
    
    def __init__(self, message: str, path: str = None, operation: str = None):
        details = {}
        if path:
            details['path'] = path
        if operation:
            details['operation'] = operation
            
        super().__init__(message, "PERMISSION_ERROR", details)
        self.path = path
        self.operation = operation