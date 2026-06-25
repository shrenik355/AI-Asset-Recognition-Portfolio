# Confidence Scoring

The confidence score answers one question: *how much should a human trust this
extraction without re-checking it?* It is a transparent weighted sum, not a
learned black box, so every point can be traced to a specific signal.

## Formula

The score is the sum of the weights of the signals that are satisfied:

```
score = Σ  weight(signal)   for each satisfied signal
        clamped to [0.0, 1.0]
```

Because the weights are chosen to sum to `1.0` when every signal fires, the raw
total is already a 0–1 score with no extra normalisation.

## Signal weights

| Signal              | Weight | Fires when…                                  |
|---------------------|:------:|----------------------------------------------|
| Brand               | 0.10   | a manufacturer is identified                 |
| Model               | 0.12   | a model string is identified                 |
| Asset type          | 0.08   | the device is classified (not `unknown`)     |
| Serial number       | 0.15   | a serial number is extracted                 |
| Asset tag           | 0.10   | an asset tag is extracted                    |
| IMEI present        | 0.05   | an IMEI-shaped value is found                |
| **IMEI valid**      | 0.15   | the IMEI passes Luhn validation              |
| Barcode present     | 0.05   | any barcode is decoded                       |
| **Barcode valid**   | 0.10   | the barcode passes its check digit           |
| OCR quality         | 0.10   | scaled by the OCR quality hint (0–1)         |

Two deliberate design points:

1. **Validation outweighs presence.** A *validated* IMEI (0.05 + 0.15 = 0.20)
   is worth far more than an IMEI that merely looks right (0.05). The same holds
   for barcodes. Passing a published checksum is strong evidence that OCR read
   the value correctly.
2. **OCR quality is a multiplier, not a flag.** Its contribution is
   `0.10 × ocr_quality`, so a thin or noisy capture is penalised proportionally.

## Review tiers

| Score range | Recommendation              |
|-------------|-----------------------------|
| 0.85 – 1.00 | Auto-review eligible        |
| 0.60 – 0.84 | Human review recommended    |
| 0.00 – 0.59 | Manual review required      |

## Worked example

A combined phone label + barcode sample produces:

```
brand (0.10) + model (0.12) + asset_type (0.08) + serial (0.15)
+ imei_present (0.05) + imei_valid (0.15)
+ barcode_present (0.05) + barcode_valid (0.10)
+ ocr_quality (0.10 × 1.0)
= 0.90  → Auto-review eligible
```

The same record carries the reasoning list, e.g. *"IMEI passed Luhn
validation"*, *"Barcode decoded and check digit is valid"*, so a reviewer sees
exactly which signals produced the score.

## Why explainable scoring

For asset intake, a number alone is not actionable — an operator needs to know
*which* field is shaky. Returning the reasons turns the score into a triage tool
rather than an opaque verdict, and makes the whole pipeline auditable.
