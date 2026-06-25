"""Optical Character Recognition (OCR) stage.

Wraps Tesseract via ``pytesseract`` behind a small, typed interface and adds
graceful error handling so the rest of the pipeline can run (and be tested)
even when the OCR engine or its native dependencies are unavailable.
"""

from __future__ import annotations

from typing import Optional

from .utils import clean_text, get_tesseract_cmd, logger

try:  # Pillow and pytesseract are optional at import time for testability.
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - exercised only without Pillow
    Image = None  # type: ignore

try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover - exercised only without pytesseract
    pytesseract = None  # type: ignore


def _configure_tesseract() -> None:
    """Point pytesseract at a configured binary if one is provided."""
    if pytesseract is None:
        return
    cmd = get_tesseract_cmd()
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd


def extract_text(image: "Image.Image") -> str:
    """Run OCR on a PIL image and return the raw extracted text.

    Args:
        image: A ``PIL.Image.Image`` instance.

    Returns:
        The recognised text, or an empty string if OCR is unavailable or fails.
    """
    if pytesseract is None:
        logger.warning("pytesseract is not installed; returning empty OCR text.")
        return ""

    _configure_tesseract()
    try:
        return pytesseract.image_to_string(image)
    except Exception as exc:  # pragma: no cover - depends on native binary
        logger.error("OCR failed: %s", exc)
        return ""


def extract_text_from_path(image_path: str) -> str:
    """Open an image from disk and run OCR on it.

    Args:
        image_path: Path to a readable image file.

    Returns:
        Recognised text, or an empty string on any failure.
    """
    if Image is None:
        logger.warning("Pillow is not installed; cannot open %s.", image_path)
        return ""
    try:
        with Image.open(image_path) as img:
            return extract_text(img)
    except FileNotFoundError:
        logger.error("Image not found: %s", image_path)
        return ""
    except Exception as exc:  # pragma: no cover
        logger.error("Could not read image %s: %s", image_path, exc)
        return ""


def ocr_quality_hint(text: Optional[str]) -> float:
    """Return a coarse 0-1 hint of OCR quality based on output volume.

    This is a heuristic used by the confidence engine: very short or empty OCR
    output usually signals a poor capture. It is intentionally simple and
    explainable rather than a learned metric.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return 0.0
    length = len(cleaned)
    if length >= 60:
        return 1.0
    if length >= 25:
        return 0.7
    if length >= 10:
        return 0.4
    return 0.2
