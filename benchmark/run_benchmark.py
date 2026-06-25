"""Benchmark harness for the asset-recognition pipeline.

Runs every image in a directory through the full pipeline, measures per-image
processing time, records which signals were successfully extracted/validated,
and writes a CSV summary plus a printed aggregate report.

Usage:
    python benchmark/run_benchmark.py
    python benchmark/run_benchmark.py --input data/sample_images --output benchmark/benchmark_results.csv
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import process_path  # noqa: E402

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}

FIELDNAMES = [
    "file_name",
    "processing_seconds",
    "ocr_chars",
    "brand_found",
    "model_found",
    "serial_found",
    "imei_found",
    "imei_valid",
    "barcode_found",
    "barcode_valid",
    "confidence_score",
    "review_recommendation",
]


def benchmark_directory(input_dir: Path, output_csv: Path) -> list[dict]:
    """Process every image in ``input_dir`` and write a CSV of results."""
    images = sorted(
        p for p in input_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not images:
        print(f"No images found in {input_dir}")
        return []

    rows: list[dict] = []
    for image_path in images:
        start = time.perf_counter()
        record = process_path(str(image_path))
        elapsed = time.perf_counter() - start

        rows.append(
            {
                "file_name": image_path.name,
                "processing_seconds": round(elapsed, 4),
                "ocr_chars": len(record.raw_ocr_text or ""),
                "brand_found": bool(record.brand),
                "model_found": bool(record.model),
                "serial_found": bool(record.serial_number),
                "imei_found": bool(record.imei),
                "imei_valid": record.imei_valid,
                "barcode_found": bool(record.barcode),
                "barcode_valid": record.barcode_valid,
                "confidence_score": record.confidence_score,
                "review_recommendation": record.review_recommendation,
            }
        )
        print(
            f"  {image_path.name:32s} "
            f"{elapsed:6.3f}s  conf={record.confidence_score:.2f}  "
            f"{record.review_recommendation}"
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return rows


def print_summary(rows: list[dict]) -> None:
    """Print aggregate metrics across the benchmark run."""
    if not rows:
        return
    n = len(rows)
    total_time = sum(r["processing_seconds"] for r in rows)
    avg_conf = sum(r["confidence_score"] for r in rows) / n

    def rate(key: str) -> str:
        hits = sum(1 for r in rows if r[key])
        return f"{hits}/{n} ({hits / n:.0%})"

    print("\nBenchmark summary")
    print("=" * 48)
    print(f"  Images processed     : {n}")
    print(f"  Total time           : {total_time:.3f}s")
    print(f"  Avg time / image     : {total_time / n:.3f}s")
    print(f"  Avg confidence       : {avg_conf:.2f}")
    print(f"  Brand extracted      : {rate('brand_found')}")
    print(f"  Model extracted      : {rate('model_found')}")
    print(f"  Serial extracted     : {rate('serial_found')}")
    print(f"  IMEI valid           : {rate('imei_valid')}")
    print(f"  Barcode valid        : {rate('barcode_valid')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the asset-recognition benchmark.")
    parser.add_argument("--input", default=str(ROOT / "data" / "sample_images"))
    parser.add_argument(
        "--output", default=str(ROOT / "benchmark" / "benchmark_results.csv")
    )
    args = parser.parse_args()

    print(f"Benchmarking images in {args.input}\n")
    rows = benchmark_directory(Path(args.input), Path(args.output))
    print_summary(rows)
    if rows:
        print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()
