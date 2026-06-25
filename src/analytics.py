"""Presentation-layer analytics derived from pipeline output.

This module adds *derived* views on top of an :class:`~src.utils.AssetRecord`
without changing any core scoring logic. It exists so the UI can show a
component-level confidence breakdown, word-level OCR bounding boxes, and
weighted explanation cards while the authoritative score in ``src.confidence``
remains the single source of truth.

Nothing here feeds back into the pipeline — it is read-only enrichment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .confidence import WEIGHTS
from .ocr import ocr_quality_hint
from .utils import AssetRecord

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore

try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore


# Human-readable labels and the explanation weight contributed by each signal.
EXPLANATION_WEIGHTS: dict[str, int] = {
    "brand": 10,
    "model": 12,
    "asset_type": 8,
    "serial_number": 15,
    "asset_tag": 10,
    "imei_valid": 20,   # present (5) + valid (15)
    "imei_present": 5,
    "barcode_valid": 15,  # present (5) + valid (10)
    "barcode_present": 5,
    "ocr_quality": 10,
}


@dataclass
class ComponentScore:
    """One row of the confidence breakdown."""

    label: str
    score: int          # 0-100
    detail: str
    status: str         # "pass" | "warn" | "fail"


def component_breakdown(record: AssetRecord) -> list[ComponentScore]:
    """Derive a per-component confidence breakdown for display.

    The components mirror the pipeline stages: OCR quality, field extraction,
    classification, barcode, and validation. Each is computed from data already
    present on the record, so the breakdown is consistent with the headline
    score without duplicating the scoring rules.
    """
    rows: list[ComponentScore] = []

    # OCR quality — reuse the same heuristic the scorer uses.
    ocr_q = int(round(ocr_quality_hint(record.raw_ocr_text) * 100))
    rows.append(
        ComponentScore(
            "OCR quality",
            ocr_q,
            "Volume and legibility of recognised text",
            _status(ocr_q),
        )
    )

    # Field extraction — fraction of the four primary fields recovered.
    primary = [record.brand, record.model, record.serial_number, record.asset_tag]
    found = sum(1 for v in primary if v)
    extraction = int(round(found / len(primary) * 100))
    rows.append(
        ComponentScore(
            "Field extraction",
            extraction,
            f"{found} of {len(primary)} primary fields recovered",
            _status(extraction),
        )
    )

    # Classification — confident when a concrete type was assigned.
    classified = record.asset_type not in (None, "", "unknown")
    rows.append(
        ComponentScore(
            "Classification",
            99 if classified else 0,
            f"Device classified as {record.asset_type}" if classified
            else "Device type could not be determined",
            "pass" if classified else "fail",
        )
    )

    # Barcode — decoded and check-digit validated.
    if record.barcode:
        bc = 95 if record.barcode_valid else 55
        detail = (
            f"{record.barcode_type or 'Barcode'} check digit valid"
            if record.barcode_valid
            else "Decoded but check digit unconfirmed"
        )
        rows.append(ComponentScore("Barcode", bc, detail, _status(bc)))
    else:
        rows.append(
            ComponentScore("Barcode", 0, "No barcode detected", "fail")
        )

    # Validation — IMEI Luhn outcome.
    if record.imei:
        val = 98 if record.imei_valid else 20
        detail = "IMEI passed Luhn validation" if record.imei_valid \
            else "IMEI failed Luhn validation"
        rows.append(ComponentScore("Validation", val, detail, _status(val)))
    else:
        rows.append(
            ComponentScore(
                "Validation",
                70 if classified else 40,
                "No IMEI to validate (expected for this asset type)"
                if classified else "No identifiers available to validate",
                "warn",
            )
        )

    return rows


def _status(score: int) -> str:
    if score >= 85:
        return "pass"
    if score >= 60:
        return "warn"
    return "fail"


@dataclass
class ExplanationCard:
    """A weighted explanation entry for the 'Why this score' panel."""

    reason: str
    weight: int
    impact: str


def explanation_cards(record: AssetRecord) -> list[ExplanationCard]:
    """Turn the record's flat explanation list into weighted cards.

    Each card pairs a reason with the points it contributed and a plain-language
    impact statement, matching the weights documented in
    ``docs/confidence_scoring.md``.
    """
    cards: list[ExplanationCard] = []

    def add(condition: bool, reason: str, weight: int, impact: str) -> None:
        if condition:
            cards.append(ExplanationCard(reason, weight, impact))

    add(bool(record.brand), f"Brand detected ({record.brand})",
        EXPLANATION_WEIGHTS["brand"], "Increased confidence")
    add(bool(record.model), f"Model detected ({record.model})",
        EXPLANATION_WEIGHTS["model"], "Increased confidence")
    add(record.asset_type not in (None, "", "unknown"),
        f"Classified as {record.asset_type}",
        EXPLANATION_WEIGHTS["asset_type"], "Increased confidence")
    add(bool(record.serial_number), "Serial number extracted",
        EXPLANATION_WEIGHTS["serial_number"], "Strong identifier signal")
    add(bool(record.asset_tag), "Asset tag extracted",
        EXPLANATION_WEIGHTS["asset_tag"], "Strong identifier signal")
    if record.imei and record.imei_valid:
        add(True, "IMEI passed Luhn validation",
            EXPLANATION_WEIGHTS["imei_valid"], "High-trust validated identifier")
    elif record.imei:
        add(True, "IMEI present but failed Luhn",
            EXPLANATION_WEIGHTS["imei_present"], "Weak signal — needs review")
    if record.barcode and record.barcode_valid:
        add(True, "Barcode check digit valid",
            EXPLANATION_WEIGHTS["barcode_valid"], "High-trust validated identifier")
    elif record.barcode:
        add(True, "Barcode decoded, check digit unconfirmed",
            EXPLANATION_WEIGHTS["barcode_present"], "Weak signal — needs review")

    cards.sort(key=lambda c: c.weight, reverse=True)
    return cards


@dataclass
class WordBox:
    """A single OCR word with its bounding box (image pixel coordinates)."""

    text: str
    left: int
    top: int
    width: int
    height: int
    conf: float


def ocr_word_boxes(image: "Image.Image", min_conf: float = 40.0) -> list[WordBox]:
    """Return word-level OCR bounding boxes for an overlay.

    Uses Tesseract's ``image_to_data``. Returns an empty list if OCR is
    unavailable, so callers can degrade gracefully.

    Args:
        image: A ``PIL.Image.Image``.
        min_conf: Minimum per-word confidence (0-100) to include.
    """
    if pytesseract is None:
        return []
    try:
        from .ocr import _configure_tesseract

        _configure_tesseract()
        data = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DICT
        )
    except Exception:  # pragma: no cover - depends on native binary
        return []

    boxes: list[WordBox] = []
    n = len(data.get("text", []))
    for i in range(n):
        text = (data["text"][i] or "").strip()
        try:
            conf = float(data["conf"][i])
        except (ValueError, TypeError):
            conf = -1.0
        if text and conf >= min_conf:
            boxes.append(
                WordBox(
                    text=text,
                    left=int(data["left"][i]),
                    top=int(data["top"][i]),
                    width=int(data["width"][i]),
                    height=int(data["height"][i]),
                    conf=conf,
                )
            )
    return boxes
