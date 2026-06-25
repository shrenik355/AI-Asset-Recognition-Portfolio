"""Architecture page — pipeline diagram, tech stack, and system components."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.theme import flow_diagram, page_setup, sidebar_brand  # noqa: E402

page_setup("Architecture")
sidebar_brand()

st.markdown('<div class="eyebrow">System Design</div>', unsafe_allow_html=True)
st.markdown("# Architecture")
st.markdown(
    '<p class="muted">A linear, stage-based pipeline. Each stage has one '
    "responsibility, a typed interface, and no hidden coupling — so any stage can "
    "be tested or swapped in isolation.</p>",
    unsafe_allow_html=True,
)

col_flow, col_desc = st.columns([1, 1.25])

with col_flow:
    st.markdown('<div class="section-title">Processing pipeline</div>', unsafe_allow_html=True)
    nodes = [
        ("Image input", False),
        ("Preprocessing", False),
        ("OCR · Tesseract", True),
        ("Barcode · pyzbar", True),
        ("Field extraction", True),
        ("Validation", True),
        ("Confidence scoring", True),
        ("Structured JSON", False),
        ("Dashboard", False),
    ]
    st.markdown('<div class="card">' + flow_diagram(nodes) + "</div>", unsafe_allow_html=True)

with col_desc:
    st.markdown('<div class="section-title">Stage responsibilities</div>', unsafe_allow_html=True)
    stages = [
        ("OCR", "Reads raw text via Tesseract. Binary path resolves from "
                "TESSERACT_CMD, so the same code runs on Linux CI, macOS, and Windows."),
        ("Barcode", "Decodes UPC-A / EAN-13 with pyzbar and normalises the result."),
        ("Field extraction", "Two-tier: labelled Key: Value patterns first, then a "
                             "keyword/pattern fallback for unstructured captures."),
        ("Validation", "Pure functions for the published checksums — IMEI Luhn, "
                       "UPC-A and EAN-13 GS1 check digits."),
        ("Confidence", "Transparent weighted sum over evidence signals; returns the "
                       "score plus the reasoning behind it."),
    ]
    inner = ""
    for name, desc in stages:
        inner += (
            f'<div style="padding:0.7rem 0;border-bottom:1px solid var(--border);">'
            f'<div style="font-family:Space Grotesk,sans-serif;font-weight:600;color:var(--text);">{name}</div>'
            f'<div class="muted" style="font-size:0.85rem;margin-top:0.2rem;">{desc}</div></div>'
        )
    st.markdown(f'<div class="card">{inner}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Technology stack</div>', unsafe_allow_html=True)
stack = [
    ("Language", "Python 3.10+"),
    ("OCR", "Tesseract · pytesseract"),
    ("Barcode", "pyzbar (zbar)"),
    ("Imaging", "Pillow"),
    ("Web app", "Streamlit (custom theme)"),
    ("Testing / CI", "pytest · GitHub Actions"),
]
cards = ""
for label, value in stack:
    cards += (
        f'<div class="metric"><div class="m-label">{label}</div>'
        f'<div class="m-value" style="font-size:1.05rem;">{value}</div></div>'
    )
st.markdown(f'<div class="metric-grid">{cards}</div>', unsafe_allow_html=True)

col_struct, col_comp = st.columns([1, 1])

with col_struct:
    st.markdown('<div class="section-title">Folder structure</div>', unsafe_allow_html=True)
    tree = """app/
  streamlit_app.py     Dashboard (entry)
  theme.py             Design system
  pages/               Architecture · Benchmarks
                       Documentation · API · About
src/
  ocr.py               OCR stage
  barcode.py           Barcode decoding
  extractor.py         Field extraction
  validation.py        Luhn · UPC-A · EAN-13
  confidence.py        Explainable scoring
  analytics.py         Derived UI views
  pipeline.py          Orchestration
  utils.py             Types + helpers
data/
  sample_images/       Original samples
  sample_outputs/      Example JSON
docs/                  Architecture · scoring
tests/                 40 unit tests
benchmark/             Timing harness"""
    st.markdown(f'<div class="codeblock">{tree}</div>', unsafe_allow_html=True)

with col_comp:
    st.markdown('<div class="section-title">System components</div>', unsafe_allow_html=True)
    comps = [
        ("Pipeline orchestrator", "Wires stages into one typed entry point shared by "
                                  "the UI and the benchmark harness."),
        ("AssetRecord", "Single structured output type; serialises cleanly to JSON/CSV."),
        ("Analytics layer", "Read-only enrichment — component sub-scores, weighted "
                            "explanations, OCR boxes — without touching core scoring."),
        ("Design system", "One theme module: colour tokens, typography, and component "
                          "builders for a consistent enterprise look."),
    ]
    inner = ""
    for name, desc in comps:
        inner += (
            f'<div style="padding:0.7rem 0;border-bottom:1px solid var(--border);">'
            f'<div style="font-family:Space Grotesk,sans-serif;font-weight:600;color:var(--text);">{name}</div>'
            f'<div class="muted" style="font-size:0.85rem;margin-top:0.2rem;">{desc}</div></div>'
        )
    st.markdown(f'<div class="card">{inner}</div>', unsafe_allow_html=True)
