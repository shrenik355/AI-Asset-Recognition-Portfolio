"""Confidence scoring stage.

Produces a single normalised confidence score (0.0-1.0) plus a human-readable
explanation and a review recommendation. The score is a transparent weighted
sum of evidence signals rather than a black-box model, which makes results
auditable — a property that matters both for asset-management trust and for
technical review.

Design principles:
    * Every signal has a fixed, documented weight.
    * Validated identifiers (IMEI Luhn, barcode check digit) are worth more
      than merely *present* identifiers.
    * The function returns the reasoning, not just the number.
"""

from __future__ import annotations

from typing import Optional

# Signal weights. These sum to 1.0 when every signal is satisfied, so the raw
# weighted total is already a 0-1 score with no extra normalisation needed.
WEIGHTS: dict[str, float] = {
    "brand": 0.10,
    "model": 0.12,
    "asset_type": 0.08,
    "serial_number": 0.15,
    "asset_tag": 0.10,
    "imei_present": 0.05,
    "imei_valid": 0.15,
    "barcode_present": 0.05,
    "barcode_valid": 0.10,
    "ocr_quality": 0.10,
}

# Score thresholds for the review recommendation.
AUTO_REVIEW_THRESHOLD = 0.85
HUMAN_REVIEW_THRESHOLD = 0.60


def calculate_confidence(
    fields: dict[str, Optional[str]],
    imei_valid: bool = False,
    barcode_valid: bool = False,
    barcode_present: bool = False,
    ocr_quality: float = 0.0,
) -> tuple[float, list[str]]:
    """Compute a 0-1 confidence score and an explanation list.

    Args:
        fields: Extracted-field dict (see :func:`src.extractor.extract_fields`).
        imei_valid: Whether the IMEI passed Luhn validation.
        barcode_valid: Whether the barcode passed check-digit validation.
        barcode_present: Whether any barcode was decoded.
        ocr_quality: 0-1 OCR-quality hint (see :func:`src.ocr.ocr_quality_hint`).

    Returns:
        ``(score, explanation)`` where ``score`` is rounded to two decimals and
        ``explanation`` is an ordered list of the reasons that contributed.
    """
    score = 0.0
    explanation: list[str] = []

    if fields.get("brand"):
        score += WEIGHTS["brand"]
        explanation.append(f"Brand identified ({fields['brand']}).")

    if fields.get("model"):
        score += WEIGHTS["model"]
        explanation.append(f"Model identified ({fields['model']}).")

    if fields.get("asset_type") and fields["asset_type"] != "unknown":
        score += WEIGHTS["asset_type"]
        explanation.append(f"Asset type classified as {fields['asset_type']}.")

    if fields.get("serial_number"):
        score += WEIGHTS["serial_number"]
        explanation.append("Serial number extracted.")

    if fields.get("asset_tag"):
        score += WEIGHTS["asset_tag"]
        explanation.append("Asset tag extracted.")

    if fields.get("imei"):
        score += WEIGHTS["imei_present"]
        if imei_valid:
            score += WEIGHTS["imei_valid"]
            explanation.append("IMEI passed Luhn validation.")
        else:
            explanation.append("IMEI present but failed Luhn validation.")

    if barcode_present:
        score += WEIGHTS["barcode_present"]
        if barcode_valid:
            score += WEIGHTS["barcode_valid"]
            explanation.append("Barcode decoded and check digit is valid.")
        else:
            explanation.append("Barcode decoded but check digit could not be confirmed.")

    if ocr_quality > 0:
        contribution = WEIGHTS["ocr_quality"] * ocr_quality
        score += contribution
        if ocr_quality >= 0.7:
            explanation.append("OCR returned a high volume of legible text.")

    score = round(min(score, 1.0), 2)
    if not explanation:
        explanation.append("No reliable signals were extracted from the image.")
    return score, explanation


def recommend_review(score: float) -> str:
    """Map a confidence score to a review recommendation."""
    if score >= AUTO_REVIEW_THRESHOLD:
        return "Auto-review eligible"
    if score >= HUMAN_REVIEW_THRESHOLD:
        return "Human review recommended"
    return "Manual review required"
