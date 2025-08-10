#!/usr/bin/env python3
"""
Setup script for Universal Printer v3.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="universal-printer",
    version="3.0.0",
    author="Sharath Kumar Daroor",
    author_email="sharathkumardaroor@gmail.com",
    description="Cross-platform document printing with enhanced PDF generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sharathkumardaroor/universal-printer",
    project_urls={
        "Bug Reports": "https://github.com/sharathkumardaroor/universal-printer/issues",
        "Source": "https://github.com/sharathkumardaroor/universal-printer",
        "Documentation": "https://github.com/sharathkumardaroor/universal-printer/blob/main/README.md",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Printing",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    keywords=[
        "printing", "pdf", "cross-platform", "document", "markdown", 
        "csv", "json", "text", "fallback", "universal", "printer",
        "windows", "linux", "macos", "batch", "conversion"
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "twine>=3.0",
            "build>=0.7",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "universal-printer=universal_printer.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "universal_printer": [
            "*.md",
            "*.txt",
            "*.json",
        ],
    },
    zip_safe=False,
    license="MIT",
    platforms=["any"],
)