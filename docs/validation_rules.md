# Validation Rules

All validators live in `src/validation.py` as pure functions with no external
dependencies. Each implements a published standard so results can be verified
independently.

## IMEI — Luhn checksum

An IMEI (International Mobile Equipment Identity) is 15 digits; the final digit
is a Luhn check digit defined by the GSMA.

**Algorithm**
1. Reject anything that is not exactly 15 numeric digits.
2. Walking the digits, double every second digit; if a doubled value exceeds 9,
   subtract 9.
3. Sum all resulting digits.
4. The IMEI is valid if the sum is a multiple of 10.

```
490154203237518  → valid
490154203237519  → invalid (check digit off by one)
```

## UPC-A — 12-digit GS1 check digit

UPC-A barcodes are 12 digits with a modulo-10 check digit.

**Algorithm**
1. Reject anything that is not exactly 12 numeric digits.
2. Apply alternating weights of 3 and 1 to the first 11 digits (anchored from
   the right so UPC-A and EAN-13 share one implementation).
3. The check digit is the amount needed to round the weighted sum up to the next
   multiple of 10.
4. Valid if the computed check digit equals the 12th digit.

```
012345678905  → valid
012345678900  → invalid
```

## EAN-13 — 13-digit GS1 check digit

EAN-13 uses the same GS1 modulo-10 scheme over 13 digits.

```
4006381333931  → valid
4006381333930  → invalid
```

The combined helper `validate_barcode` infers the symbology from length
(12 → UPC-A, 13 → EAN-13) and returns `(is_valid, symbology)`.

> **Note on zbar output:** `pyzbar` often reports UPC-A codes as a 13-digit
> EAN-13 with a leading zero. This is expected and standards-compliant — a
> UPC-A code *is* an EAN-13 with a leading zero — and both forms validate
> correctly.

## Serial number — structural heuristic

Serial numbers have no universal checksum, so `looks_like_serial` only performs
a conservative structural check: the value must be alphanumeric and at least a
minimum length. This is explicitly a heuristic and is **not** treated as a
validation guarantee anywhere in the scoring.

## Testing

Every rule above is covered by `tests/test_validation.py` against both
known-good and known-bad reference values, including length, non-numeric, and
`None` edge cases.
