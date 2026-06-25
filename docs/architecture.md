# Architecture

The system is a linear, stage-based pipeline. Each stage has a single
responsibility, a typed interface, and no hidden dependence on the others, so
any stage can be tested or replaced in isolation.

```
                ┌─────────────┐
   image  ───▶  │  1. OCR     │  raw text          (src/ocr.py)
                └─────────────┘
                      │
                ┌─────────────┐
        ───▶    │ 2. Barcode  │  decoded value     (src/barcode.py)
                └─────────────┘
                      │
                ┌─────────────┐
                │ 3. Extract  │  structured fields (src/extractor.py)
                └─────────────┘
                      │
                ┌─────────────┐
                │ 4. Validate │  IMEI / barcode    (src/validation.py)
                └─────────────┘
                      │
                ┌─────────────┐
                │ 5. Score    │  0–1 + reasons     (src/confidence.py)
                └─────────────┘
                      │
                ┌─────────────┐
                │ AssetRecord │  JSON / CSV        (src/utils.py)
                └─────────────┘
```

## Stage responsibilities

**1. OCR (`src/ocr.py`)**
Wraps Tesseract through `pytesseract`. The Tesseract binary path is resolved
from the `TESSERACT_CMD` environment variable, falling back to the system
`PATH` — this replaces the original hard-coded Windows path and lets the same
code run on Linux CI, macOS, and Windows. A coarse `ocr_quality_hint` feeds the
confidence engine.

**2. Barcode (`src/barcode.py`)**
Decodes 1D/2D barcodes via `pyzbar` and returns a normalised `BarcodeResult`
with the decoded value and reported symbology.

**3. Extraction (`src/extractor.py`)**
A two-tier strategy. First it looks for explicit `Key: Value` pairs common on
inventory labels. When labels are missing, it falls back to brand-keyword and
model-pattern scanning. Device classification is rule-based and explainable.

**4. Validation (`src/validation.py`)**
Pure functions implementing the published checksums: IMEI via the Luhn
algorithm, UPC-A and EAN-13 via their GS1 modulo-10 check digits. No external
dependencies, which keeps them fast and trivially unit-testable.

**5. Confidence (`src/confidence.py`)**
A transparent weighted sum over the available evidence signals. Validated
identifiers are weighted more heavily than merely present ones. The stage
returns both the score and an ordered list of the reasons behind it.

## Orchestration

`src/pipeline.py` wires the stages together and assembles the final
`AssetRecord` dataclass (`src/utils.py`), which serialises cleanly to JSON or
CSV. The Streamlit app and the benchmark harness both consume this single entry
point, so the UI and measurements always reflect identical logic.

## Design rationale

- **Explainability over opacity.** Every score carries its reasoning. This
  matters for asset-management trust and makes the project auditable on review.
- **Graceful degradation.** Native dependencies (Tesseract, zbar) are imported
  defensively so the package stays importable and the pure-logic stages remain
  testable even in minimal environments.
- **Portability.** No machine-specific paths; configuration comes from the
  environment.
