"""Benchmarks page — performance and accuracy charts with CSV export."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.theme import metric_card, page_setup, sidebar_brand  # noqa: E402

page_setup("Benchmarks")
sidebar_brand()

CSV_PATH = ROOT / "benchmark" / "benchmark_results.csv"

st.markdown('<div class="eyebrow">Performance &amp; Accuracy</div>', unsafe_allow_html=True)
st.markdown("# Benchmarks")
st.markdown(
    '<p class="muted">Reproducible metrics from the bundled harness '
    "(<code>python benchmark/run_benchmark.py</code>). Timings are single-thread on "
    "Linux with Tesseract 5.3; treat them as relative indicators, not production "
    "accuracy claims.</p>",
    unsafe_allow_html=True,
)

# Load benchmark results if present.
df = None
if CSV_PATH.exists():
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception:
        df = None

if df is None or df.empty:
    st.info("Run `python benchmark/run_benchmark.py` to generate benchmark_results.csv.")
    st.stop()

# Headline metrics
n = len(df)
avg_time = df["processing_seconds"].mean()
avg_conf = df["confidence_score"].mean()


def _rate(col: str) -> str:
    if col not in df.columns:
        return "—"
    hits = df[col].astype(str).str.lower().isin(["true", "1", "1.0"]).sum()
    return f"{hits}/{n}"


metrics = (
    metric_card("Images", str(n), "in sample set")
    + metric_card("Avg time", f"{avg_time:.2f}s", "per image")
    + metric_card("Avg confidence", f"{avg_conf:.2f}", "0–1 scale")
    + metric_card("IMEI valid", _rate("imei_valid"), "Luhn passed")
    + metric_card("Barcode valid", _rate("barcode_valid"), "check digit")
)
st.markdown(f'<div class="metric-grid">{metrics}</div>', unsafe_allow_html=True)

# Processing time chart
st.markdown('<div class="section-title">Processing time by image</div>', unsafe_allow_html=True)
time_df = df.set_index("file_name")["processing_seconds"]
st.bar_chart(time_df, color="#f5a623", height=260)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-title">Extraction success rate</div>', unsafe_allow_html=True)
    fields = {
        "Brand": "brand_found",
        "Model": "model_found",
        "Serial": "serial_found",
        "IMEI valid": "imei_valid",
        "Barcode valid": "barcode_valid",
    }
    rates = {}
    for label, col in fields.items():
        if col in df.columns:
            hits = df[col].astype(str).str.lower().isin(["true", "1", "1.0"]).sum()
            rates[label] = round(hits / n * 100)
    rate_df = pd.DataFrame.from_dict(rates, orient="index", columns=["percent"])
    st.bar_chart(rate_df, color="#45d483", height=260)

with col_b:
    st.markdown('<div class="section-title">Confidence distribution</div>', unsafe_allow_html=True)
    conf_df = df.set_index("file_name")["confidence_score"]
    st.bar_chart(conf_df, color="#5aa9f0", height=260)

# Raw table + export
st.markdown('<div class="section-title">Raw results</div>', unsafe_allow_html=True)
st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button(
    "Download benchmark CSV",
    df.to_csv(index=False),
    file_name="benchmark_results.csv",
    mime="text/csv",
)

st.markdown(
    '<p class="muted" style="margin-top:1rem;font-size:0.85rem;">'
    "A meaningful accuracy benchmark would need a larger labelled dataset spanning "
    "varied lighting, angle, font, and label damage. See the Documentation page for "
    "the methodology and the roadmap toward that.</p>",
    unsafe_allow_html=True,
)
