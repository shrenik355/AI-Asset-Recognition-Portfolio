"""Unit tests for the field-extraction module."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.extractor import classify_device, extract_fields  # noqa: E402

LABELLED_TEXT = """
ASSET LABEL (SAMPLE)
Manufacturer: Dell
Model: Latitude 5420
Serial Number: SAMPLE123456
Asset Tag: AT-009912
"""

PHONE_TEXT = """
DEVICE LABEL (SAMPLE)
Manufacturer: Apple
Model: iPhone 13
Serial Number: SAMPLEX98765
IMEI: 490154203237518
"""

UNLABELLED_TEXT = "Property of sample lab — Dell Latitude 5420 unit, do not remove."


class TestClassifyDevice:
    def test_laptop(self):
        assert classify_device("Latitude 5420") == "laptop"
        assert classify_device("ThinkPad X1") == "laptop"

    def test_smartphone(self):
        assert classify_device("iPhone 13") == "smartphone"
        assert classify_device("Galaxy S24") == "smartphone"

    def test_tablet(self):
        assert classify_device("iPad Pro") == "tablet"

    def test_unknown(self):
        assert classify_device("Mystery Device 9000") == "unknown"
        assert classify_device(None) == "unknown"


class TestExtractFields:
    def test_labelled_extraction(self):
        fields = extract_fields(LABELLED_TEXT)
        assert fields["brand"] == "Dell"
        assert fields["model"] == "Latitude 5420"
        assert fields["serial_number"] == "SAMPLE123456"
        assert fields["asset_tag"] == "AT-009912"
        assert fields["asset_type"] == "laptop"

    def test_imei_extraction(self):
        fields = extract_fields(PHONE_TEXT)
        assert fields["imei"] == "490154203237518"
        assert fields["asset_type"] == "smartphone"

    def test_flexible_fallback(self):
        fields = extract_fields(UNLABELLED_TEXT)
        assert fields["brand"] == "Dell"
        assert fields["model"] is not None
        assert "Latitude" in fields["model"]

    def test_empty_text(self):
        fields = extract_fields("")
        assert fields["brand"] is None
        assert fields["asset_type"] == "unknown"

    def test_no_false_imei(self):
        fields = extract_fields("Serial Number: ABC123 and some 1234 numbers")
        assert fields["imei"] is None
