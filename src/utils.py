"""Shared utilities, data types, and configuration helpers.

This module centralises the lightweight data structures and helper functions
used across the asset-recognition pipeline so that the individual stages
(OCR, barcode, extraction, validation, confidence) stay focused and testable.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

logger = logging.getLogger("asset_recognition")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


@dataclass
class AssetRecord:
    """Structured representation of a recognised asset.

    Attributes are intentionally optional because real-world labels are often
    partial or damaged. The pipeline records whatever it can identify and lets
    the confidence engine decide how trustworthy the overall result is.
    """

    asset_type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    asset_tag: Optional[str] = None
    imei: Optional[str] = None
    imei_valid: bool = False
    barcode: Optional[str] = None
    barcode_type: Optional[str] = None
    barcode_valid: bool = False
    confidence_score: float = 0.0
    review_recommendation: str = "Manual review required"
    explanation: list[str] = field(default_factory=list)
    raw_ocr_text: str = ""

    def to_dict(self, include_raw: bool = False) -> dict[str, Any]:
        """Return a JSON-serialisable dict.

        Args:
            include_raw: When ``False`` (default) the bulky raw OCR text is
                omitted to keep exported payloads clean.
        """
        data = asdict(self)
        if not include_raw:
            data.pop("raw_ocr_text", None)
        return data

    def to_json(self, include_raw: bool = False, indent: int = 2) -> str:
        """Serialise the record to a JSON string."""
        return json.dumps(self.to_dict(include_raw=include_raw), indent=indent)


def get_tesseract_cmd() -> Optional[str]:
    """Resolve the Tesseract binary path in a cross-platform way.

    Honors the ``TESSERACT_CMD`` environment variable first (useful on Windows
    where Tesseract is not on PATH), otherwise returns ``None`` so pytesseract
    falls back to the system PATH. This replaces the original hard-coded
    Windows path and makes the project portable across OSes and CI.
    """
    return os.environ.get("TESSERACT_CMD")


def clean_text(value: Optional[str]) -> Optional[str]:
    """Trim whitespace and collapse blank results to ``None``."""
    if value is None:
        return None
    cleaned = " ".join(value.split()).strip()
    return cleaned or None


def safe_first_line(value: Optional[str]) -> Optional[str]:
    """Return the first non-empty line of a multi-line capture group."""
    if not value:
        return None
    for line in value.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None
