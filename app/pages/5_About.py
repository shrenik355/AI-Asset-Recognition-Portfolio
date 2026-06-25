"""About page — overview, features, roadmap, challenges, lessons."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.theme import page_setup, sidebar_brand  # noqa: E402

page_setup("About")
sidebar_brand()

st.markdown('<div class="eyebrow">Overview</div>', unsafe_allow_html=True)
st.markdown("# About this project")

st.markdown(
    '<div class="card"><p style="color:var(--text);line-height:1.7;margin:0;">'
    "AI Asset Recognition is an end-to-end computer-vision pipeline that turns a "
    "photo of a device label into structured, validated, confidence-scored asset "
    "data. It reads text, decodes barcodes, validates identifiers against their "
    "published checksums, and produces a single transparent score with the "
    "reasoning shown — so high-confidence records flow through and low-confidence "
    "ones get flagged for review.</p></div>",
    unsafe_allow_html=True,
)

col_feat, col_road = st.columns(2)

with col_feat:
    st.markdown('<div class="section-title">Features</div>', unsafe_allow_html=True)
    features = [
        "OCR text extraction (Tesseract)",
        "UPC-A / EAN-13 barcode decoding",
        "Labelled + fallback field extraction",
        "IMEI Luhn & barcode check-digit validation",
        "Rule-based device classification",
        "Explainable weighted confidence scoring",
        "OCR bounding-box overlay",
        "JSON & CSV structured export",
        "Benchmark harness, unit tests, CI",
    ]
    inner = "".join(
        f'<div style="padding:0.45rem 0;border-bottom:1px solid var(--border);'
        f'font-size:0.9rem;color:var(--text);">&#10003;&nbsp; {f}</div>'
        for f in features
    )
    st.markdown(f'<div class="card">{inner}</div>', unsafe_allow_html=True)

with col_road:
    st.markdown('<div class="section-title">Roadmap</div>', unsafe_allow_html=True)
    roadmap = [
        ("Image pre-processing", "Deskew, threshold, denoise ahead of OCR."),
        ("Hybrid extraction", "A learned extractor behind the deterministic rules."),
        ("Calibrated confidence", "Weights fit against a labelled ground-truth set."),
        ("Broader symbologies", "QR, Code-128, Data Matrix support."),
        ("REST API + container", "FastAPI surface for intake workflows."),
    ]
    inner = ""
    for name, desc in roadmap:
        inner += (
            f'<div style="padding:0.6rem 0;border-bottom:1px solid var(--border);">'
            f'<div style="font-family:Space Grotesk,sans-serif;font-weight:600;color:var(--text);">{name}</div>'
            f'<div class="muted" style="font-size:0.84rem;margin-top:0.15rem;">{desc}</div></div>'
        )
    st.markdown(f'<div class="card">{inner}</div>', unsafe_allow_html=True)

col_chal, col_less = st.columns(2)

with col_chal:
    st.markdown('<div class="section-title">Technical challenges</div>', unsafe_allow_html=True)
    challenges = [
        ("Portability", "Removed hard-coded OCR paths; configuration now comes from "
                        "the environment so the same code runs across OSes and CI."),
        ("Explainability", "Designed scoring as a transparent weighted sum that "
                          "returns its reasoning rather than an opaque number."),
        ("Graceful degradation", "Native dependencies are imported defensively so the "
                                "pure-logic stages stay importable and testable."),
    ]
    inner = ""
    for name, desc in challenges:
        inner += (
            f'<div style="padding:0.6rem 0;border-bottom:1px solid var(--border);">'
            f'<div style="font-weight:600;color:var(--text);">{name}</div>'
            f'<div class="muted" style="font-size:0.84rem;margin-top:0.15rem;">{desc}</div></div>'
        )
    st.markdown(f'<div class="card">{inner}</div>', unsafe_allow_html=True)

with col_less:
    st.markdown('<div class="section-title">Lessons learned</div>', unsafe_allow_html=True)
    lessons = [
        ("Validate, don't trust", "Checksums (Luhn, GS1) catch OCR errors cheaply and "
                                 "deserve more weight than mere field presence."),
        ("Triage beats accuracy alone", "A calibrated review recommendation is often "
                                       "more useful operationally than a raw accuracy figure."),
        ("Separation pays off", "Keeping core logic free of UI concerns made the whole "
                              "pipeline trivially testable and reusable across surfaces."),
    ]
    inner = ""
    for name, desc in lessons:
        inner += (
            f'<div style="padding:0.6rem 0;border-bottom:1px solid var(--border);">'
            f'<div style="font-weight:600;color:var(--text);">{name}</div>'
            f'<div class="muted" style="font-size:0.84rem;margin-top:0.15rem;">{desc}</div></div>'
        )
    st.markdown(f'<div class="card">{inner}</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="card" style="margin-top:1rem;"><div class="card-label">Disclaimer</div>'
    '<p class="muted" style="margin:0;font-size:0.86rem;line-height:1.6;">'
    "This is an independent portfolio project built with public/sample data and "
    "original code. It does not contain proprietary employer or client code.</p></div>",
    unsafe_allow_html=True,
)
