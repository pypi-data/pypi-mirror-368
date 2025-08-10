#!/usr/bin/env python3
"""
Command Line Interface for Universal Printer v3.0
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

from . import DocumentPrinter, PrinterConfig, __version__


def print_file_command(args):
    """Handle print file command."""
    try:
        config = None
        if args.config:
            config = PrinterConfig(args.config)
        
        printer = DocumentPrinter(config=config)
        
        success, message, pdf_path = printer.print_file(
            args.file,
            printer_name=args.printer,
            fallback_to_pdf=not args.no_fallback,
            pdf_filename=args.output
        )
        
        if success:
            print(f"✅ Success: {message}")
            return 0
        elif pdf_path:
            print(f"🖨️  Printing failed, PDF fallback created: {pdf_path}")
            return 0
        else:
            print(f"❌ Failed: {message}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def generate_pdf_command(args):
    """Handle generate PDF command."""
    try:
        config = None
        if args.config:
            config = PrinterConfig(args.config)
        
        printer = DocumentPrinter(config=config)
        
        success, message, pdf_path = printer.generate_pdf(
            args.input,
            pdf_filename=args.output
        )
        
        if success:
            print(f"✅ PDF generated: {pdf_path}")
            return 0
        else:
            print(f"❌ Failed: {message}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def batch_print_command(args):
    """Handle batch print command."""
    try:
        config = None
        if args.config:
            config = PrinterConfig(args.config)
        
        printer = DocumentPrinter(config=config)
        
        # Read file list
        if args.file_list:
            with open(args.file_list, 'r') as f:
                files = [line.strip() for line in f if line.strip()]
        else:
            files = args.files
        
        results = printer.print_batch(
            files,
            printer_name=args.printer,
            fallback_to_pdf=not args.no_fallback
        )
        
        # Print summary
        print(f"📊 Batch Print Results:")
        print(f"   Total files: {results['total_files']}")
        print(f"   Successful prints: {results['successful_prints']}")
        print(f"   PDF fallbacks: {results['pdf_fallbacks']}")
        print(f"   Errors: {results['errors']}")
        print(f"   Duration: {results['duration']:.2f}s")
        
        # Save detailed results if requested
        if args.report:
            with open(args.report, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📄 Detailed report saved to: {args.report}")
        
        return 0 if results['errors'] == 0 else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def batch_pdf_command(args):
    """Handle batch PDF generation command."""
    try:
        config = None
        if args.config:
            config = PrinterConfig(args.config)
        
        printer = DocumentPrinter(config=config)
        
        # Read file list
        if args.file_list:
            with open(args.file_list, 'r') as f:
                files = [line.strip() for line in f if line.strip()]
        else:
            files = args.files
        
        results = printer.generate_batch_pdfs(files)
        
        # Print summary
        print(f"📊 Batch PDF Generation Results:")
        print(f"   Total files: {results['total_files']}")
        print(f"   Successful PDFs: {results['successful_pdfs']}")
        print(f"   Errors: {results['errors']}")
        print(f"   Duration: {results['duration']:.2f}s")
        
        # Save detailed results if requested
        if args.report:
            with open(args.report, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📄 Detailed report saved to: {args.report}")
        
        return 0 if results['errors'] == 0 else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def info_command(args):
    """Handle info command."""
    try:
        config = None
        if args.config:
            config = PrinterConfig(args.config)
        
        printer = DocumentPrinter(config=config)
        
        if args.file:
            # Show file information
            info = printer.get_file_info(args.file)
            print(f"📄 File Information: {args.file}")
            print(f"   Exists: {info.get('exists', False)}")
            if info.get('exists'):
                print(f"   Size: {info.get('size_human', 'Unknown')}")
                print(f"   Type: {info.get('mime_type', 'Unknown')}")
                print(f"   Is text: {info.get('is_text', False)}")
                print(f"   Is printable: {info.get('is_printable', False)}")
                print(f"   Supports enhanced PDF: {info.get('supports_enhanced_pdf', False)}")
                print(f"   Modified: {info.get('modified', 'Unknown')}")
        else:
            # Show general information
            stats = printer.get_statistics()
            formats = printer.get_supported_formats()
            
            print(f"🖨️  Universal Printer v{__version__}")
            print(f"📊 Statistics:")
            print(f"   Total prints: {stats['total_prints']}")
            print(f"   Success rate: {stats['success_rate']:.1f}%")
            print(f"   Uptime: {stats['uptime_seconds']:.1f}s")
            
            print(f"📋 Supported Formats:")
            print(f"   Printable: {len(formats['printable'])} types")
            print(f"   Enhanced PDF: {len(formats['enhanced_pdf'])} types")
            print(f"   Text files: {len(formats['text_files'])} types")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def config_command(args):
    """Handle config command."""
    try:
        if args.create:
            # Create default config
            config = PrinterConfig.create_default_config(args.create)
            print(f"✅ Default configuration created: {args.create}")
            return 0
        
        if args.show:
            # Show current config
            config = PrinterConfig(args.show) if args.show != "default" else PrinterConfig()
            config_dict = config.to_dict()
            print(json.dumps(config_dict, indent=2))
            return 0
        
        print("❌ No config action specified. Use --create or --show")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="universal-printer",
        description="Universal Printer v3.0 - Cross-platform document printing with enhanced PDF generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  universal-printer print document.txt
  universal-printer print --printer "HP LaserJet" document.pdf
  universal-printer pdf document.md --output formatted_doc
  universal-printer batch-print *.txt --no-fallback
  universal-printer batch-pdf *.md --report results.json
  universal-printer info --file document.txt
  universal-printer config --create config.json
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Universal Printer v{__version__}"
    )
    
    parser.add_argument(
        "--config", 
        help="Configuration file path"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Print command
    print_parser = subparsers.add_parser("print", help="Print a file")
    print_parser.add_argument("file", help="File to print")
    print_parser.add_argument("--printer", help="Printer name")
    print_parser.add_argument("--output", help="PDF filename if fallback is used")
    print_parser.add_argument("--no-fallback", action="store_true", help="Disable PDF fallback")
    print_parser.set_defaults(func=print_file_command)
    
    # PDF generation command
    pdf_parser = subparsers.add_parser("pdf", help="Generate PDF from file or text")
    pdf_parser.add_argument("input", help="Input file or text content")
    pdf_parser.add_argument("--output", help="Output PDF filename")
    pdf_parser.set_defaults(func=generate_pdf_command)
    
    # Batch print command
    batch_print_parser = subparsers.add_parser("batch-print", help="Print multiple files")
    batch_print_parser.add_argument("files", nargs="*", help="Files to print")
    batch_print_parser.add_argument("--file-list", help="File containing list of files to print")
    batch_print_parser.add_argument("--printer", help="Printer name")
    batch_print_parser.add_argument("--no-fallback", action="store_true", help="Disable PDF fallback")
    batch_print_parser.add_argument("--report", help="Save detailed report to file")
    batch_print_parser.set_defaults(func=batch_print_command)
    
    # Batch PDF command
    batch_pdf_parser = subparsers.add_parser("batch-pdf", help="Generate PDFs for multiple files")
    batch_pdf_parser.add_argument("files", nargs="*", help="Files to convert to PDF")
    batch_pdf_parser.add_argument("--file-list", help="File containing list of files to convert")
    batch_pdf_parser.add_argument("--report", help="Save detailed report to file")
    batch_pdf_parser.set_defaults(func=batch_pdf_command)
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information")
    info_parser.add_argument("--file", help="Show information about specific file")
    info_parser.set_defaults(func=info_command)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument("--create", help="Create default configuration file")
    config_parser.add_argument("--show", help="Show configuration (use 'default' for default config)")
    config_parser.set_defaults(func=config_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())