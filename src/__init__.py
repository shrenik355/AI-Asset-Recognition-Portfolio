"""AI Asset Recognition — core processing package.

This package provides a modular pipeline for extracting and validating
hardware-asset information from images using OCR, barcode decoding, field
extraction, validation, and confidence scoring.

All code is original and operates on public/sample data only.
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = [
    "ocr",
    "barcode",
    "validation",
    "confidence",
    "extractor",
    "analytics",
    "pipeline",
    "utils",
]
