# Benchmark Report

This report describes how the pipeline is benchmarked and the results on the
bundled sample set. Reproduce it any time with:

```bash
python benchmark/run_benchmark.py
```

## Methodology

`benchmark/run_benchmark.py` runs every image in a directory through the full
pipeline (`src/pipeline.process_path`) and records, per image:

- **Processing time** — wall-clock seconds for the complete pipeline, measured
  with `time.perf_counter()`.
- **OCR volume** — number of characters Tesseract returned.
- **Extraction success** — whether brand, model, serial, and IMEI were found.
- **Validation success** — whether the IMEI passed Luhn and the barcode passed
  its check digit.
- **Confidence + recommendation** — the final score and review tier.

Results are written to `benchmark/benchmark_results.csv` and an aggregate
summary is printed to the console.

## Results (bundled sample set)

Measured on the four bundled sample images (Linux, Tesseract 5.3, single
thread). Absolute timings depend on hardware and image size; treat them as
relative indicators.

| Image                    | Time (s) | Confidence | Recommendation            |
|--------------------------|:--------:|:----------:|---------------------------|
| asset_label_full.png     | 0.50     | 0.90       | Auto-review eligible      |
| asset_label_phone.png    | 0.42     | 0.75       | Human review recommended  |
| asset_label_laptop.png   | 0.36     | 0.65       | Human review recommended  |
| barcode_upc.png          | 0.15     | 0.19       | Manual review required    |

**Aggregate**

| Metric                | Value          |
|-----------------------|----------------|
| Images processed      | 4              |
| Avg time / image      | ~0.36 s        |
| Avg confidence        | 0.62           |
| Brand extracted       | 3/4 (75%)      |
| Model extracted       | 3/4 (75%)      |
| Serial extracted      | 3/4 (75%)      |
| IMEI valid            | 2/4 (50%)      |
| Barcode valid         | 2/4 (50%)      |

## Reading the results

The numbers behave as designed. The combined label-plus-barcode image clears the
auto-review threshold because it satisfies nearly every signal, including two
validated identifiers. The single-modality images (label only, or barcode only)
land lower because fewer independent signals corroborate them — exactly the
behaviour you want from a triage score. The bare barcode scores lowest because a
barcode alone tells you very little about the asset.

## Scope and honesty

This is a small, clean sample set used to demonstrate the harness and the
scoring behaviour, not a claim of production accuracy. A meaningful accuracy
benchmark would require a larger, labelled dataset spanning varied lighting,
angles, fonts, and damaged labels. See `docs/limitations.md` for the path to
that.
