"""Barcode detection stage.

Decodes 1D/2D barcodes from images using ``pyzbar`` and exposes the result in a
normalised form. As with the OCR stage, the heavy native dependency is imported
defensively so the package remains importable in minimal environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .utils import logger

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore

try:
    from pyzbar.pyzbar import decode  # type: ignore
except Exception:  # pragma: no cover
    decode = None  # type: ignore


@dataclass
class BarcodeResult:
    """Normalised barcode decode result."""

    value: Optional[str] = None
    symbology: Optional[str] = None

    @property
    def found(self) -> bool:
        return self.value is not None


def detect_barcode(image: "Image.Image") -> BarcodeResult:
    """Decode the first barcode found in an image.

    Args:
        image: A ``PIL.Image.Image`` instance.

    Returns:
        A :class:`BarcodeResult`. If nothing is decoded (or pyzbar is missing),
        the result's ``found`` property is ``False``.
    """
    if decode is None:
        logger.warning("pyzbar is not installed; skipping barcode detection.")
        return BarcodeResult()

    try:
        barcodes = decode(image)
    except Exception as exc:  # pragma: no cover - depends on native zbar
        logger.error("Barcode decoding failed: %s", exc)
        return BarcodeResult()

    if not barcodes:
        return BarcodeResult()

    first = barcodes[0]
    try:
        value = first.data.decode("utf-8")
    except Exception:
        value = str(first.data)
    return BarcodeResult(value=value, symbology=getattr(first, "type", None))


def detect_barcode_from_path(image_path: str) -> BarcodeResult:
    """Open an image from disk and decode a barcode from it."""
    if Image is None:
        logger.warning("Pillow is not installed; cannot open %s.", image_path)
        return BarcodeResult()
    try:
        with Image.open(image_path) as img:
            return detect_barcode(img)
    except FileNotFoundError:
        logger.error("Image not found: %s", image_path)
        return BarcodeResult()
    except Exception as exc:  # pragma: no cover
        logger.error("Could not read image %s: %s", image_path, exc)
        return BarcodeResult()
