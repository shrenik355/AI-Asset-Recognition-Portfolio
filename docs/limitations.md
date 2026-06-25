# Limitations and Future Improvements

A portfolio project is more credible when it is honest about what it does *not*
yet do. This document states the current limits and a realistic path forward.

## Current limitations

**OCR is only as good as the capture.** Tesseract handles clean, high-contrast
labels well but degrades on skew, glare, low resolution, unusual fonts, and
physically damaged labels. There is no pre-processing (deskew, threshold,
denoise) stage yet.

**Extraction is rule-based.** Field extraction relies on labelled `Key: Value`
patterns plus a keyword fallback. It will miss layouts that do not follow those
conventions and brands not in the keyword list. It does not understand free-form
or multi-language labels.

**Classification is a small ruleset.** Device classification covers common
laptop, smartphone, and tablet product lines. Anything outside the rules returns
`unknown`.

**Confidence weights are hand-tuned.** The scoring weights are sensible and
explainable but are expert-set, not learned from labelled outcomes. They have
not been calibrated against a ground-truth dataset.

**Benchmark set is small.** The bundled benchmark demonstrates the harness and
scoring behaviour; it is not a statistically meaningful accuracy measurement.

## Future improvements

**Image pre-processing.** Add a configurable OpenCV stage (grayscale, adaptive
threshold, deskew, denoise) ahead of OCR to lift accuracy on poor captures.

**Learned or hybrid extraction.** Layer a model-based extractor (e.g. a small
fine-tuned token classifier, or an LLM with structured output) behind the
rule-based one, falling back gracefully so the deterministic path always works.

**Calibrated confidence.** Collect a labelled dataset, then fit the confidence
weights (or a light classifier) so the score reflects measured
precision/recall, and publish a calibration curve.

**Broader barcode and identifier support.** Add QR, Code-128, Data Matrix, and
additional identifier checksums; expand the brand/model dictionaries.

**Real accuracy benchmark.** Build a larger, labelled sample set spanning
lighting, angle, font, and damage variation, and report precision/recall per
field alongside timing.

**Deployment surface.** Add a small REST API (FastAPI) and container image so
the pipeline can be embedded in an intake workflow, plus batch processing with
result persistence.

## Scope guardrails

This project deliberately uses only original code and public/sample data. It
contains no proprietary employer or client code, label layouts, datasets, or
business logic, and any future extension is expected to hold that line.
