"""Field validation stage.

Pure, dependency-free validation functions for the identifiers the pipeline
extracts. Keeping these functions side-effect free makes them fast to unit test
and easy to reason about — important for portfolio review and for any reviewer
who wants to verify the algorithms independently.

Implemented checks:
    * IMEI       — Luhn checksum over 15 digits (GSMA standard).
    * UPC-A      — 12-digit check digit (weighted 3/1).
    * EAN-13     — 13-digit check digit (weighted 1/3).
    * Serial     — light structural heuristic, not a checksum.
"""

from __future__ import annotations

from typing import Optional


def validate_imei_luhn(imei: Optional[str]) -> bool:
    """Validate a 15-digit IMEI using the Luhn algorithm.

    The IMEI's final digit is a Luhn check digit. Starting from the rightmost
    digit and moving left, every second digit is doubled (subtracting 9 if the
    result exceeds 9); a valid number's digit sum is a multiple of 10. We
    implement the equivalent left-to-right form used by the GSMA specification.

    Args:
        imei: Candidate IMEI string.

    Returns:
        ``True`` if the value is exactly 15 numeric digits and passes Luhn.

    Examples:
        >>> validate_imei_luhn("490154203237518")
        True
        >>> validate_imei_luhn("490154203237519")
        False
    """
    if not imei or not imei.isdigit() or len(imei) != 15:
        return False

    total = 0
    for index, char in enumerate(imei):
        digit = int(char)
        # Double every second digit (0-indexed odd positions).
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def _ean_upc_check_digit_valid(code: str, length: int) -> bool:
    """Shared GS1 modulo-10 check-digit validation for UPC-A / EAN-13.

    GS1 numbering applies alternating weights of 3 and 1 to the digits
    preceding the check digit. The check digit is the amount needed to round
    the weighted sum up to the next multiple of 10.
    """
    if not code or not code.isdigit() or len(code) != length:
        return False

    body = code[:-1]
    expected_check = int(code[-1])

    total = 0
    # Weighting differs between UPC-A and EAN-13 by where the 3-weight starts.
    # We anchor the weights from the right so both schemes work with one rule:
    # rightmost body digit gets weight 3, then alternate 1, 3, 1, ...
    for offset, char in enumerate(reversed(body)):
        weight = 3 if offset % 2 == 0 else 1
        total += int(char) * weight

    computed_check = (10 - (total % 10)) % 10
    return computed_check == expected_check


def validate_upc_a(code: Optional[str]) -> bool:
    """Validate a 12-digit UPC-A barcode via its GS1 check digit.

    Examples:
        >>> validate_upc_a("012345678905")
        True
        >>> validate_upc_a("012345678900")
        False
    """
    if code is None:
        return False
    return _ean_upc_check_digit_valid(code, length=12)


def validate_ean_13(code: Optional[str]) -> bool:
    """Validate a 13-digit EAN-13 barcode via its GS1 check digit.

    Examples:
        >>> validate_ean_13("4006381333931")
        True
        >>> validate_ean_13("4006381333930")
        False
    """
    if code is None:
        return False
    return _ean_upc_check_digit_valid(code, length=13)


def validate_barcode(code: Optional[str]) -> tuple[bool, Optional[str]]:
    """Validate a barcode and infer its symbology from length.

    Returns:
        A ``(is_valid, symbology)`` tuple. ``symbology`` is one of
        ``"UPC-A"``, ``"EAN-13"`` or ``None`` when the format is unrecognised.
    """
    if not code or not code.isdigit():
        return False, None
    if len(code) == 12:
        return validate_upc_a(code), "UPC-A"
    if len(code) == 13:
        return validate_ean_13(code), "EAN-13"
    return False, None


def looks_like_serial(serial: Optional[str], min_length: int = 4) -> bool:
    """Heuristic structural check for a plausible serial number.

    Serial numbers have no universal checksum, so this only verifies that the
    value is alphanumeric and of a reasonable length. It is deliberately
    conservative and clearly documented as a heuristic, not a guarantee.
    """
    if not serial:
        return False
    candidate = serial.strip()
    return len(candidate) >= min_length and candidate.isalnum()
