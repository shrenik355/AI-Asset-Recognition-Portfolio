"""Unit tests for the validation module.

Covers IMEI Luhn validation and UPC-A / EAN-13 check-digit validation against
known-good and known-bad reference values.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.validation import (  # noqa: E402
    looks_like_serial,
    validate_barcode,
    validate_ean_13,
    validate_imei_luhn,
    validate_upc_a,
)


class TestImeiLuhn:
    def test_valid_imei(self):
        assert validate_imei_luhn("490154203237518") is True

    def test_invalid_check_digit(self):
        assert validate_imei_luhn("490154203237519") is False

    def test_wrong_length(self):
        assert validate_imei_luhn("12345") is False
        assert validate_imei_luhn("4901542032375180") is False

    def test_non_numeric(self):
        assert validate_imei_luhn("49015420323751A") is False

    def test_none_and_empty(self):
        assert validate_imei_luhn(None) is False
        assert validate_imei_luhn("") is False


class TestUpcA:
    def test_valid_upc(self):
        assert validate_upc_a("012345678905") is True
        assert validate_upc_a("036000291452") is True

    def test_invalid_check_digit(self):
        assert validate_upc_a("012345678900") is False

    def test_wrong_length(self):
        assert validate_upc_a("01234567890") is False

    def test_non_numeric(self):
        assert validate_upc_a("01234567890X") is False

    def test_none(self):
        assert validate_upc_a(None) is False


class TestEan13:
    def test_valid_ean(self):
        assert validate_ean_13("4006381333931") is True
        assert validate_ean_13("5901234123457") is True

    def test_invalid_check_digit(self):
        assert validate_ean_13("4006381333930") is False

    def test_wrong_length(self):
        assert validate_ean_13("400638133393") is False

    def test_none(self):
        assert validate_ean_13(None) is False


class TestValidateBarcode:
    def test_upc_inference(self):
        valid, symbology = validate_barcode("012345678905")
        assert valid is True
        assert symbology == "UPC-A"

    def test_ean_inference(self):
        valid, symbology = validate_barcode("4006381333931")
        assert valid is True
        assert symbology == "EAN-13"

    def test_unknown_length(self):
        valid, symbology = validate_barcode("12345")
        assert valid is False
        assert symbology is None

    def test_non_numeric(self):
        valid, symbology = validate_barcode("ABCDEFGHIJKL")
        assert valid is False


class TestSerialHeuristic:
    def test_plausible_serial(self):
        assert looks_like_serial("SAMPLE123456") is True

    def test_too_short(self):
        assert looks_like_serial("AB") is False

    def test_non_alnum(self):
        assert looks_like_serial("AB-12-CD") is False

    def test_none(self):
        assert looks_like_serial(None) is False
