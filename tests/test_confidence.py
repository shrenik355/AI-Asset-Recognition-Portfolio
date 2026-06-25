"""Unit tests for the confidence-scoring module."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.confidence import (  # noqa: E402
    AUTO_REVIEW_THRESHOLD,
    HUMAN_REVIEW_THRESHOLD,
    calculate_confidence,
    recommend_review,
)

FULL_FIELDS = {
    "brand": "Apple",
    "model": "iPhone 13",
    "asset_type": "smartphone",
    "serial_number": "SAMPLEX98765",
    "asset_tag": "AT-0001",
    "imei": "490154203237518",
}

EMPTY_FIELDS = {
    "brand": None,
    "model": None,
    "asset_type": "unknown",
    "serial_number": None,
    "asset_tag": None,
    "imei": None,
}


class TestCalculateConfidence:
    def test_empty_is_zero(self):
        score, explanation = calculate_confidence(EMPTY_FIELDS)
        assert score == 0.0
        assert explanation  # non-empty, explains the absence

    def test_full_signal_is_high(self):
        score, explanation = calculate_confidence(
            FULL_FIELDS,
            imei_valid=True,
            barcode_valid=True,
            barcode_present=True,
            ocr_quality=1.0,
        )
        assert score >= AUTO_REVIEW_THRESHOLD
        assert any("Luhn" in line for line in explanation)

    def test_score_never_exceeds_one(self):
        score, _ = calculate_confidence(
            FULL_FIELDS,
            imei_valid=True,
            barcode_valid=True,
            barcode_present=True,
            ocr_quality=1.0,
        )
        assert score <= 1.0

    def test_valid_imei_beats_invalid(self):
        valid_score, _ = calculate_confidence(FULL_FIELDS, imei_valid=True)
        invalid_score, _ = calculate_confidence(FULL_FIELDS, imei_valid=False)
        assert valid_score > invalid_score

    def test_valid_barcode_beats_present_only(self):
        with_valid, _ = calculate_confidence(
            FULL_FIELDS, barcode_present=True, barcode_valid=True
        )
        present_only, _ = calculate_confidence(
            FULL_FIELDS, barcode_present=True, barcode_valid=False
        )
        assert with_valid > present_only

    def test_explanation_mentions_brand(self):
        _, explanation = calculate_confidence(FULL_FIELDS)
        assert any("Apple" in line for line in explanation)


class TestRecommendReview:
    def test_auto_review(self):
        assert recommend_review(0.9) == "Auto-review eligible"
        assert recommend_review(AUTO_REVIEW_THRESHOLD) == "Auto-review eligible"

    def test_human_review(self):
        assert recommend_review(0.7) == "Human review recommended"
        assert recommend_review(HUMAN_REVIEW_THRESHOLD) == "Human review recommended"

    def test_manual_review(self):
        assert recommend_review(0.2) == "Manual review required"
        assert recommend_review(0.0) == "Manual review required"
