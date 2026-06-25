"""Field extraction stage.

Turns raw OCR text into structured asset fields using a two-tier strategy:

1. **Labelled extraction** — looks for explicit ``Key: Value`` pairs that are
   common on asset/inventory labels (``Manufacturer:``, ``Model:``, ``Serial
   Number:``, ``Asset Tag:``, ``IMEI:``).
2. **Flexible fallback** — when labels are missing, scans for known brand
   keywords and model-name patterns so the pipeline still recovers useful data
   from unstructured captures.

All patterns operate on generic, public formatting conventions. No proprietary
label layouts or client-specific schemas are encoded here.
"""

from __future__ import annotations

import re
from typing import Optional

from .utils import safe_first_line

# Brand keyword -> canonical display name. Public manufacturer names only.
KNOWN_BRANDS: dict[str, str] = {
    "dell": "Dell",
    "hp": "HP",
    "hewlett": "HP",
    "lenovo": "Lenovo",
    "apple": "Apple",
    "samsung": "Samsung",
    "microsoft": "Microsoft",
    "google": "Google",
    "asus": "Asus",
    "acer": "Acer",
}

# Generic model-name patterns for common consumer/enterprise product lines.
MODEL_PATTERNS: tuple[str, ...] = (
    r"(Latitude\s+[A-Za-z0-9\-]+)",
    r"(ThinkPad\s+[A-Za-z0-9\s\-]+)",
    r"(EliteBook\s+[A-Za-z0-9\s\-]+)",
    r"(ProBook\s+[A-Za-z0-9\s\-]+)",
    r"(MacBook(?:\s+(?:Air|Pro))?\s*[A-Za-z0-9\s\-]*)",
    r"(iPhone\s+[A-Za-z0-9\s\-]+)",
    r"(iPad(?:\s+(?:Air|Pro|Mini))?\s*[A-Za-z0-9\s\-]*)",
    r"(Galaxy\s+[A-Za-z0-9\s\-]+)",
    r"(Pixel\s+[A-Za-z0-9\s\-]+)",
)

# Model keyword -> asset type. Mirrors the device-classification rules.
DEVICE_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("latitude", "thinkpad", "elitebook", "probook", "macbook"), "laptop"),
    (("iphone", "galaxy", "pixel"), "smartphone"),
    (("ipad", "tablet"), "tablet"),
)


def classify_device(model: Optional[str]) -> str:
    """Classify an asset type from a model string using rule-based matching.

    Returns one of ``"laptop"``, ``"smartphone"``, ``"tablet"`` or
    ``"unknown"``. The rules are simple and explainable by design.
    """
    if not model:
        return "unknown"
    model_lower = model.lower()
    for keywords, device_type in DEVICE_RULES:
        if any(keyword in model_lower for keyword in keywords):
            return device_type
    return "unknown"


def _flexible_extract(text: str) -> tuple[Optional[str], Optional[str]]:
    """Recover brand and model when explicit labels are absent."""
    text_lower = text.lower()

    brand: Optional[str] = None
    for keyword, canonical in KNOWN_BRANDS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            brand = canonical
            break

    model: Optional[str] = None
    for pattern in MODEL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            model = match.group(1).strip()
            break

    return brand, model


def extract_fields(text: str) -> dict[str, Optional[str]]:
    """Extract structured asset fields from raw OCR text.

    Args:
        text: Raw OCR output.

    Returns:
        A dict with keys ``brand``, ``model``, ``asset_type``,
        ``serial_number``, ``asset_tag`` and ``imei`` (values may be ``None``).
    """
    if not text:
        text = ""

    brand_match = re.search(r"Manufacturer[:\s]+(.+)", text, re.IGNORECASE)
    model_match = re.search(r"Model[:\s]+(.+)", text, re.IGNORECASE)
    serial_match = re.search(r"Serial\s*Number[:\s]+([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    asset_match = re.search(r"Asset\s*Tag[:\s]+([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    imei_match = re.search(r"IMEI[:\s]+(\d{15})", text, re.IGNORECASE)

    brand = safe_first_line(brand_match.group(1)) if brand_match else None
    model = safe_first_line(model_match.group(1)) if model_match else None

    # Fall back to keyword/pattern scanning for any missing high-value field.
    if not brand or not model:
        flex_brand, flex_model = _flexible_extract(text)
        brand = brand or flex_brand
        model = model or flex_model

    return {
        "brand": brand,
        "model": model,
        "asset_type": classify_device(model),
        "serial_number": serial_match.group(1) if serial_match else None,
        "asset_tag": asset_match.group(1) if asset_match else None,
        "imei": imei_match.group(1) if imei_match else None,
    }
