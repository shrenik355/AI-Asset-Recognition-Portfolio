"""API page — documentation for a proposed REST surface over the pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.theme import page_setup, sidebar_brand  # noqa: E402

page_setup("API")
sidebar_brand()

st.markdown('<div class="eyebrow">Integration</div>', unsafe_allow_html=True)
st.markdown("# API reference")
st.markdown(
    '<p class="muted">A proposed REST surface that wraps the same pipeline. '
    "The endpoints below describe the planned contract — a thin FastAPI layer over "
    "<code>src.pipeline</code> — included as design documentation, not a running "
    "server.</p>",
    unsafe_allow_html=True,
)

endpoints = [
    ("POST", "/analyze", "Run the full pipeline on a single image."),
    ("POST", "/batch", "Run the pipeline over multiple images in one request."),
    ("GET", "/health", "Liveness probe for orchestration."),
    ("GET", "/version", "Return the deployed model/pipeline version."),
]

st.markdown('<div class="section-title">Endpoints</div>', unsafe_allow_html=True)
rows = ""
for method, path, desc in endpoints:
    mcls = "method-get" if method == "GET" else "method-post"
    rows += (
        f'<div style="display:flex;align-items:center;gap:1rem;padding:0.7rem 0;'
        f'border-bottom:1px solid var(--border);">'
        f'<span class="pill {mcls}" style="min-width:54px;text-align:center;">{method}</span>'
        f'<span style="font-family:JetBrains Mono,monospace;color:var(--text);min-width:120px;">{path}</span>'
        f'<span class="muted" style="font-size:0.86rem;">{desc}</span></div>'
    )
st.markdown(f'<div class="card">{rows}</div>', unsafe_allow_html=True)

col_req, col_res = st.columns(2)

with col_req:
    st.markdown('<div class="section-title">Sample request</div>', unsafe_allow_html=True)
    req = """POST /analyze HTTP/1.1
Host: api.assetai.example
Content-Type: multipart/form-data

file=@asset_label.png"""
    st.markdown(f'<div class="codeblock">{req}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:1rem;">cURL</div>', unsafe_allow_html=True)
    curl = """curl -X POST \\
  https://api.assetai.example/analyze \\
  -F "file=@asset_label.png" """
    st.markdown(f'<div class="codeblock">{curl}</div>', unsafe_allow_html=True)

with col_res:
    st.markdown('<div class="section-title">Sample response</div>', unsafe_allow_html=True)
    res = """{
  "asset_type": "smartphone",
  "brand": "Apple",
  "model": "iPhone 13",
  "serial_number": "SN-PH-774120",
  "asset_tag": null,
  "imei": "490154203237518",
  "imei_valid": true,
  "barcode": "012345678905",
  "barcode_type": "UPC-A",
  "barcode_valid": true,
  "confidence_score": 0.9,
  "review_recommendation": "Auto-review eligible",
  "explanation": [
    "IMEI passed Luhn validation",
    "Barcode check digit is valid",
    "Brand, model, serial extracted"
  ]
}"""
    st.markdown(f'<div class="codeblock">{res}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Status codes</div>', unsafe_allow_html=True)
codes = [
    ("200", "Analysis completed", "pass"),
    ("400", "Invalid or missing image", "warn"),
    ("422", "Unsupported file type", "warn"),
    ("500", "Pipeline error", "fail"),
]
chips = ""
for code, desc, status in codes:
    cls = {"pass": "pass", "warn": "warn", "fail": "fail"}[status]
    chips += (
        f'<span class="chip {cls}" style="margin:0.2rem 0.3rem;">'
        f'{code} &middot; {desc}</span>'
    )
st.markdown(f'<div class="card">{chips}</div>', unsafe_allow_html=True)
