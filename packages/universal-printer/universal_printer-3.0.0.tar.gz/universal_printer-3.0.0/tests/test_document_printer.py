import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from universal_printer import DocumentPrinter


class TestDocumentPrinter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.printer = DocumentPrinter()
        self.test_content = "This is a test document.\nWith multiple lines.\nFor testing purposes."
    
    def test_init(self):
        """Test DocumentPrinter initialization."""
        self.assertIsInstance(self.printer, DocumentPrinter)
        self.assertIsNotNone(self.printer.system)
        self.assertIsInstance(self.printer.downloads_path, Path)
        # Test new v2.0 attributes
        self.assertIsInstance(self.printer.printable_types, set)
        self.assertTrue(len(self.printer.printable_types) > 0)
    
    def test_write_temp_text(self):
        """Test temporary text file creation."""
        temp_path = self.printer._write_temp_text(self.test_content)
        
        # Check that file was created
        self.assertTrue(temp_path.exists())
        self.assertTrue(temp_path.suffix == '.txt')
        
        # Check content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, self.test_content)
        
        # Clean up
        temp_path.unlink()
    
    def test_write_minimal_pdf(self):
        """Test minimal PDF generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "test.pdf"
            
            success = self.printer._write_minimal_pdf(self.test_content, pdf_path)
            
            self.assertTrue(success)
            self.assertTrue(pdf_path.exists())
            
            # Check that it's a valid PDF (starts with PDF header)
            with open(pdf_path, 'rb') as f:
                header = f.read(8)
            self.assertTrue(header.startswith(b'%PDF-1.4'))
    
    def test_fallback_pdf_save(self):
        """Test PDF fallback functionality."""
        # Test with default filename
        pdf_path = self.printer._fallback_pdf_save(self.test_content)
        
        self.assertIsNotNone(pdf_path)
        self.assertTrue(Path(pdf_path).exists())
        self.assertTrue(str(pdf_path).endswith('.pdf'))
        
        # Clean up
        Path(pdf_path).unlink()
        
        # Test with custom filename
        custom_filename = "custom_test_file"
        pdf_path = self.printer._fallback_pdf_save(self.test_content, custom_filename)
        
        self.assertIsNotNone(pdf_path)
        self.assertTrue(Path(pdf_path).exists())
        self.assertTrue(str(pdf_path).endswith('.pdf'))
        self.assertIn('custom_test_file', str(pdf_path))
        
        # Clean up
        Path(pdf_path).unlink()
    
    def test_print_document_with_fallback(self):
        """Test print_document with PDF fallback enabled."""
        # This test will likely fail to print (no printer configured in test environment)
        # but should succeed with PDF fallback
        success, message, pdf_path = self.printer.print_document(
            self.test_content, 
            fallback_to_pdf=True,
            pdf_filename="test_fallback"
        )
        
        # In test environment, printing will likely fail but PDF should be created
        if not success and pdf_path:
            self.assertIsNotNone(pdf_path)
            self.assertTrue(Path(pdf_path).exists())
            # Clean up
            Path(pdf_path).unlink()
        
        # The test passes if either printing succeeded OR PDF fallback worked
        self.assertTrue(success or pdf_path is not None)
    
    def test_print_document_no_fallback(self):
        """Test print_document with PDF fallback disabled."""
        success, message, pdf_path = self.printer.print_document(
            self.test_content, 
            fallback_to_pdf=False
        )
        
        # With fallback disabled, pdf_path should be None if printing fails
        if not success:
            self.assertIsNone(pdf_path)
    
    def test_print_existing_file(self):
        """Test printing an existing file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_content)
            temp_file_path = f.name
        
        try:
            success, message, pdf_path = self.printer.print_document(
                temp_file_path, 
                fallback_to_pdf=True
            )
            
            # Should handle the file path correctly
            self.assertIsInstance(success, bool)
            self.assertIsInstance(message, str)
            
            # Clean up PDF if created
            if pdf_path and Path(pdf_path).exists():
                Path(pdf_path).unlink()
                
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
    
    def test_system_detection(self):
        """Test that system is properly detected."""
        system = self.printer.system
        self.assertIn(system, ['Windows', 'Darwin', 'Linux'])
    
    def test_downloads_path(self):
        """Test downloads path is set correctly."""
        downloads_path = self.printer.downloads_path
        self.assertIsInstance(downloads_path, Path)
        # Should be user's home directory + Downloads
        expected_path = Path.home() / "Downloads"
        self.assertEqual(downloads_path, expected_path)
    
    # New tests for version 2.0 features
    
    def test_detect_file_type(self):
        """Test file type detection."""
        # Create test files with different extensions
        with tempfile.TemporaryDirectory() as temp_dir:
            # Text file
            txt_file = Path(temp_dir) / "test.txt"
            txt_file.write_text("test content")
            mime_type, is_text, is_printable, supports_enhanced_pdf = self.printer._detect_file_type(txt_file)
            self.assertTrue(is_text)
            self.assertTrue(is_printable)
            
            # JSON file
            json_file = Path(temp_dir) / "test.json"
            json_file.write_text('{"test": "data"}')
            mime_type, is_text, is_printable, supports_enhanced_pdf = self.printer._detect_file_type(json_file)
            self.assertTrue(is_text)
            self.assertTrue(is_printable)
            
            # Unknown binary file
            bin_file = Path(temp_dir) / "test.xyz"
            bin_file.write_bytes(b'\x00\x01\x02\x03')
            mime_type, is_text, is_printable, supports_enhanced_pdf = self.printer._detect_file_type(bin_file)
            self.assertFalse(is_text)
            self.assertFalse(is_printable)
    
    def test_read_file_content(self):
        """Test reading file content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Text file
            txt_file = Path(temp_dir) / "test.txt"
            test_text = "Hello, World!\nThis is a test."
            txt_file.write_text(test_text)
            
            content = self.printer._read_file_content(txt_file)
            self.assertEqual(content, test_text)
            
            # Binary file
            bin_file = Path(temp_dir) / "test.bin"
            bin_file.write_bytes(b'\x00\x01\x02\x03')
            
            content = self.printer._read_file_content(bin_file)
            self.assertIn("This is a binary file", content)
            self.assertIn("test.bin", content)
    
    def test_prepare_file_for_printing(self):
        """Test file preparation for printing."""
        # Test with text content
        file_path, is_temp, original_content = self.printer._prepare_file_for_printing("Test content")
        self.assertTrue(is_temp)
        self.assertEqual(original_content, "Test content")
        self.assertTrue(file_path.exists())
        file_path.unlink()  # cleanup
        
        # Test with existing file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("File content")
            temp_file_path = f.name
        
        try:
            file_path, is_temp, original_content = self.printer._prepare_file_for_printing(temp_file_path)
            self.assertFalse(is_temp)
            self.assertEqual(original_content, "File content")
            self.assertEqual(file_path, Path(temp_file_path))
        finally:
            os.unlink(temp_file_path)
    
    def test_print_text_method(self):
        """Test the new print_text convenience method."""
        success, message, pdf_path = self.printer.print_text(
            "Test text content",
            fallback_to_pdf=True,
            pdf_filename="test_print_text"
        )
        
        # Should either succeed or create PDF fallback
        self.assertTrue(success or pdf_path is not None)
        
        # Clean up PDF if created
        if pdf_path and Path(pdf_path).exists():
            Path(pdf_path).unlink()
    
    def test_print_file_method(self):
        """Test the new print_file convenience method."""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file content")
            temp_file_path = f.name
        
        try:
            success, message, pdf_path = self.printer.print_file(
                temp_file_path,
                fallback_to_pdf=True,
                pdf_filename="test_print_file"
            )
            
            # Should either succeed or create PDF fallback
            self.assertTrue(success or pdf_path is not None)
            
            # Clean up PDF if created
            if pdf_path and Path(pdf_path).exists():
                Path(pdf_path).unlink()
                
        finally:
            os.unlink(temp_file_path)
    
    def test_print_file_not_found(self):
        """Test print_file with non-existent file."""
        success, message, pdf_path = self.printer.print_file("/nonexistent/file.txt")
        
        self.assertFalse(success)
        self.assertIn("File not found", message)
        self.assertIsNone(pdf_path)
    
    def test_get_supported_file_types(self):
        """Test getting supported file types."""
        supported_types = self.printer.get_supported_file_types()
        
        self.assertIsInstance(supported_types, set)
        self.assertIn('.txt', supported_types)
        self.assertIn('.pdf', supported_types)
        self.assertIn('.jpg', supported_types)
        self.assertTrue(len(supported_types) > 5)
    
    def test_is_file_printable(self):
        """Test file printability check."""
        # Test printable file types
        self.assertTrue(self.printer.is_file_printable("document.pdf"))
        self.assertTrue(self.printer.is_file_printable("text.txt"))
        self.assertTrue(self.printer.is_file_printable("image.jpg"))
        
        # Test non-printable file types
        self.assertFalse(self.printer.is_file_printable("program.exe"))
        self.assertFalse(self.printer.is_file_printable("data.bin"))
    
    def test_print_various_file_types(self):
        """Test printing various file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create different file types
            files_to_test = [
                ("test.txt", "Plain text content"),
                ("test.json", '{"key": "value", "number": 42}'),
                ("test.csv", "Name,Age,City\nJohn,30,NYC\nJane,25,LA"),
                ("test.html", "<html><body><h1>Test HTML</h1></body></html>"),
                ("test.xml", '<?xml version="1.0"?><root><item>test</item></root>')
            ]
            
            for filename, content in files_to_test:
                file_path = Path(temp_dir) / filename
                file_path.write_text(content)
                
                success, message, pdf_path = self.printer.print_file(
                    str(file_path),
                    fallback_to_pdf=True,
                    pdf_filename=f"test_{filename}"
                )
                
                # Should either succeed or create PDF fallback
                self.assertTrue(success or pdf_path is not None, 
                              f"Failed for file type: {filename}")
                
                # Clean up PDF if created
                if pdf_path and Path(pdf_path).exists():
                    Path(pdf_path).unlink()
    
    def test_enhanced_print_document(self):
        """Test enhanced print_document method with new parameters."""
        # Test with text content
        success, message, pdf_path = self.printer.print_document(
            "Enhanced test content",
            printer_name=None,
            fallback_to_pdf=True,
            pdf_filename="enhanced_test"
        )
        
        # Should either succeed or create PDF fallback
        self.assertTrue(success or pdf_path is not None)
        
        # Clean up PDF if created
        if pdf_path and Path(pdf_path).exists():
            Path(pdf_path).unlink()
    
    def test_generate_pdf_method(self):
        """Test the new generate_pdf method."""
        # Test with text content
        success, message, pdf_path = self.printer.generate_pdf(
            "This is test content for PDF generation.",
            pdf_filename="test_generated"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(pdf_path)
        self.assertTrue(Path(pdf_path).exists())
        self.assertIn("test_generated", str(pdf_path))
        
        # Clean up
        Path(pdf_path).unlink()
    
    def test_generate_pdf_from_files(self):
        """Test PDF generation from different file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test files with different formats
            test_files = [
                ("test.txt", "Simple text content\nWith multiple lines."),
                ("test.md", "# Markdown Title\n\n## Subtitle\n\n- Bullet point\n- Another point\n\n**Bold text**"),
                ("test.json", '{"name": "John", "age": 30, "city": "New York", "hobbies": ["reading", "coding"]}'),
                ("test.csv", "Name,Age,City\nJohn,30,NYC\nJane,25,LA\nBob,35,Chicago")
            ]
            
            for filename, content in test_files:
                file_path = Path(temp_dir) / filename
                file_path.write_text(content)
                
                success, message, pdf_path = self.printer.generate_pdf(
                    str(file_path),
                    pdf_filename=f"generated_{filename.replace('.', '_')}"
                )
                
                self.assertTrue(success, f"Failed to generate PDF for {filename}: {message}")
                self.assertIsNotNone(pdf_path)
                self.assertTrue(Path(pdf_path).exists())
                
                # Clean up
                Path(pdf_path).unlink()
    
    def test_generate_pdf_unsupported_type(self):
        """Test PDF generation with unsupported file type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an unsupported file type
            unsupported_file = Path(temp_dir) / "test.xyz"
            unsupported_file.write_text("Some content")
            
            success, message, pdf_path = self.printer.generate_pdf(str(unsupported_file))
            
            self.assertFalse(success)
            self.assertIn("not supported", message)
            self.assertIsNone(pdf_path)
    
    def test_enhanced_pdf_formatting(self):
        """Test enhanced PDF formatting for different file types."""
        # Test Markdown formatting
        md_content = """# Main Title
        
## Subtitle

This is a paragraph with **bold text** and *italic text*.

- First bullet point
- Second bullet point
- Third bullet point

### Code Example
```python
print("Hello, World!")
```

1. First numbered item
2. Second numbered item
"""
        
        success, message, pdf_path = self.printer.generate_pdf(
            md_content,
            pdf_filename="test_markdown_formatting"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(pdf_path)
        self.assertTrue(Path(pdf_path).exists())
        
        # Verify it's a valid PDF
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
        self.assertTrue(header.startswith(b'%PDF-1.4'))
        
        # Clean up
        Path(pdf_path).unlink()
    
    def test_markdown_file_support(self):
        """Test that .md files are now supported."""
        # Check that .md is in supported file types
        supported_types = self.printer.get_supported_file_types()
        self.assertIn('.md', supported_types)
        
        # Test that .md files are considered printable
        self.assertTrue(self.printer.is_file_printable("document.md"))
        
        # Test file type detection for .md files
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = Path(temp_dir) / "test.md"
            md_file.write_text("# Test Markdown")
            
            mime_type, is_text, is_printable, supports_enhanced_pdf = self.printer._detect_file_type(md_file)
            self.assertTrue(is_text)
            self.assertTrue(is_printable)


if __name__ == '__main__':
    unittest.main()