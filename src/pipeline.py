"""End-to-end asset-recognition pipeline.

Orchestrates the individual stages into a single, well-typed entry point that
both the Streamlit UI and the benchmark script consume. Each stage remains
independently testable; this module only wires them together and assembles the
final :class:`~src.utils.AssetRecord`.
"""

from __future__ import annotations

from typing import Optional

from .barcode import BarcodeResult, detect_barcode, detect_barcode_from_path
from .confidence import calculate_confidence, recommend_review
from .extractor import extract_fields
from .ocr import extract_text, extract_text_from_path, ocr_quality_hint
from .utils import AssetRecord
from .validation import validate_barcode, validate_imei_luhn

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore


def _assemble(
    ocr_text: str,
    barcode: BarcodeResult,
) -> AssetRecord:
    """Build an :class:`AssetRecord` from OCR text and a barcode result."""
    fields = extract_fields(ocr_text)

    imei_valid = validate_imei_luhn(fields.get("imei"))
    barcode_valid, inferred_symbology = validate_barcode(barcode.value)
    ocr_quality = ocr_quality_hint(ocr_text)

    score, explanation = calculate_confidence(
        fields,
        imei_valid=imei_valid,
        barcode_valid=barcode_valid,
        barcode_present=barcode.found,
        ocr_quality=ocr_quality,
    )

    return AssetRecord(
        asset_type=fields.get("asset_type"),
        brand=fields.get("brand"),
        model=fields.get("model"),
        serial_number=fields.get("serial_number"),
        asset_tag=fields.get("asset_tag"),
        imei=fields.get("imei"),
        imei_valid=imei_valid,
        barcode=barcode.value,
        barcode_type=barcode.symbology or inferred_symbology,
        barcode_valid=barcode_valid,
        confidence_score=score,
        review_recommendation=recommend_review(score),
        explanation=explanation,
        raw_ocr_text=ocr_text,
    )


def process_image(image: "Image.Image") -> AssetRecord:
    """Run the full pipeline on an in-memory PIL image."""
    ocr_text = extract_text(image)
    barcode = detect_barcode(image)
    return _assemble(ocr_text, barcode)


def process_path(image_path: str) -> AssetRecord:
    """Run the full pipeline on an image file path."""
    ocr_text = extract_text_from_path(image_path)
    barcode = detect_barcode_from_path(image_path)
    return _assemble(ocr_text, barcode)
