"""AI Asset Recognition — Dashboard (main entry point).

The primary workspace: upload or pick a sample, watch the pipeline run stage by
stage, then review extracted fields, a confidence gauge with a component
breakdown, weighted explanation cards, validation chips, an OCR overlay, and
structured exports.

Run the whole app with:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
import time
from io import StringIO
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.theme import (  # noqa: E402
    breakdown_row,
    chip,
    confidence_colour,
    confidence_gauge,
    explanation_card,
    field_card,
    page_setup,
    sidebar_brand,
)
from src.analytics import (  # noqa: E402
    component_breakdown,
    explanation_cards,
    ocr_word_boxes,
)
from src.pipeline import process_image  # noqa: E402
from src.utils import AssetRecord  # noqa: E402

try:
    from PIL import Image, ImageDraw  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore

SAMPLE_DIR = ROOT / "data" / "sample_images"

page_setup("Dashboard")
sidebar_brand()

if "history" not in st.session_state:
    st.session_state.history = []

st.sidebar.markdown("### Settings")
show_overlay = st.sidebar.toggle("OCR bounding-box overlay", value=True)
animate = st.sidebar.toggle("Animated pipeline progress", value=True)
min_conf = st.sidebar.slider("OCR overlay min confidence", 0, 100, 40, step=5)

st.sidebar.markdown("### Recent scans")
if st.session_state.history:
    for h in reversed(st.session_state.history[-5:]):
        st.sidebar.markdown(
            f'<div style="font-family:JetBrains Mono,monospace;font-size:0.72rem;'
            f'color:var(--muted);padding:0.2rem 0;">{h["name"]} · '
            f'<span style="color:var(--accent);">{int(h["score"]*100)}%</span></div>',
            unsafe_allow_html=True,
        )
    if st.sidebar.button("Clear history"):
        st.session_state.history = []
        st.rerun()
else:
    st.sidebar.caption("No scans yet this session.")


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Enterprise Computer Vision Pipeline</div>
      <div class="hero-title">AI Asset <span>Recognition</span></div>
      <div class="hero-sub">Enterprise Computer Vision Pipeline</div>
      <div class="hero-tagline">OCR &bull; Barcode &bull; Validation &bull; Confidence Scoring &bull; Structured AI Extraction</div>
      <div class="badge-row">
        <span class="status-badge"><span class="dot"></span>OCR</span>
        <span class="status-badge"><span class="dot"></span>Barcode</span>
        <span class="status-badge"><span class="dot"></span>Validation</span>
        <span class="status-badge"><span class="dot"></span>Confidence</span>
        <span class="status-badge"><span class="dot"></span>JSON Export</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def _field_confidence(value, valid: bool, ocr_q: float):
    if value in (None, "", "unknown"):
        return 0, "fail"
    base = 80 + int(ocr_q * 18)
    if valid:
        return min(99, base + 1), "pass"
    return min(96, base), "pass"


def _draw_overlay(image, boxes):
    if ImageDraw is None or not boxes:
        return image
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img, "RGBA")
    for b in boxes:
        draw.rectangle(
            [b.left, b.top, b.left + b.width, b.top + b.height],
            outline=(245, 166, 35, 255),
            width=2,
        )
    return img


def _result_to_csv(record: AssetRecord) -> str:
    import csv

    buf = StringIO()
    data = record.to_dict()
    data["explanation"] = " | ".join(record.explanation)
    writer = csv.DictWriter(buf, fieldnames=list(data.keys()))
    writer.writeheader()
    writer.writerow(data)
    return buf.getvalue()


def _json_highlight(record: AssetRecord) -> str:
    import html
    import json
    import re

    raw = json.dumps(record.to_dict(), indent=2)
    out_lines = []
    for line in raw.splitlines():
        esc = html.escape(line)
        esc = re.sub(r'(&quot;.*?&quot;)(\s*:)', r'<span class="key">\1</span>\2', esc, count=1)
        esc = re.sub(r'(:\s*)(&quot;.*?&quot;)', r'\1<span class="s">\2</span>', esc)
        esc = re.sub(r'(:\s*)(-?\d+\.?\d*|true|false|null)', r'\1<span class="n">\2</span>', esc)
        out_lines.append(esc)
    return '<div class="codeblock">' + "\n".join(out_lines) + "</div>"


def run_pipeline_animated(image) -> AssetRecord:
    stages = ["Uploading", "OCR", "Barcode", "Validation", "Confidence", "Finished"]
    if not animate:
        return process_image(image)

    holder = st.empty()
    record = process_image(image)
    fills = [18, 45, 68, 84, 96, 100]
    for i, stage in enumerate(stages):
        rows = []
        for j, s in enumerate(stages[:-1]):
            pct = 100 if j < i else (fills[i] if j == i else 0)
            rows.append(
                f'<div class="pipe-stage"><span class="pipe-name">{s}</span>'
                f'<span class="pipe-track"><span class="pipe-fill" style="width:{pct}%;"></span></span>'
                f'<span class="pipe-pct">{pct}%</span></div>'
            )
        label = "Finished" if stage == "Finished" else f"Running &middot; {stage}"
        holder.markdown(
            f'<div class="card"><div class="card-label">{label}</div>'
            + "".join(rows) + "</div>",
            unsafe_allow_html=True,
        )
        time.sleep(0.18)
    holder.empty()
    return record


def render_results(record: AssetRecord, image) -> None:
    ocr_q = (component_breakdown(record)[0].score) / 100.0
    pct = int(round(record.confidence_score * 100))
    colour, category = confidence_colour(pct)

    col_img, col_score = st.columns([1.25, 1])
    with col_img:
        st.markdown('<div class="section-title">Source image</div>', unsafe_allow_html=True)
        boxes = ocr_word_boxes(image, min_conf=float(min_conf)) if show_overlay else []
        display_img = _draw_overlay(image, boxes) if (show_overlay and boxes) else image
        st.image(display_img, use_container_width=True)
        if show_overlay and boxes:
            st.caption(f"OCR overlay &middot; {len(boxes)} words detected (>={min_conf}% conf)")
    with col_score:
        st.markdown('<div class="section-title">Confidence</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card">' + confidence_gauge(pct, category, colour)
            + f'<div style="text-align:center;margin-top:0.6rem;" class="muted">'
            f'{record.review_recommendation}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Extracted fields</div>', unsafe_allow_html=True)
    brand_c = _field_confidence(record.brand, False, ocr_q)
    model_c = _field_confidence(record.model, False, ocr_q)
    serial_c = _field_confidence(record.serial_number, False, ocr_q)
    tag_c = _field_confidence(record.asset_tag, False, ocr_q)
    imei_c = _field_confidence(record.imei, record.imei_valid, ocr_q)
    bc_c = _field_confidence(record.barcode, record.barcode_valid, ocr_q)
    type_c = (99, "pass") if record.asset_type not in (None, "", "unknown") else (0, "fail")

    cards = [
        field_card("Asset type", record.asset_type, *type_c),
        field_card("Brand", record.brand, *brand_c),
        field_card("Model", record.model, *model_c),
        field_card("Serial number", record.serial_number, *serial_c),
        field_card("Asset tag", record.asset_tag, *tag_c),
        field_card("IMEI", record.imei, *imei_c),
        field_card("Barcode", record.barcode, *bc_c),
        field_card("Barcode type", record.barcode_type, *((90, "pass") if record.barcode_type else (0, "fail"))),
    ]
    st.markdown('<div class="field-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)

    col_bd, col_exp = st.columns([1, 1])
    with col_bd:
        st.markdown('<div class="section-title">Confidence breakdown</div>', unsafe_allow_html=True)
        rows = [breakdown_row(c.label, c.score, c.detail, c.status) for c in component_breakdown(record)]
        final_row = breakdown_row("Final score", pct, record.review_recommendation,
                                  "pass" if pct >= 85 else "warn" if pct >= 60 else "fail")
        st.markdown('<div class="card">' + "".join(rows) + final_row + "</div>", unsafe_allow_html=True)
    with col_exp:
        st.markdown('<div class="section-title">Why this score</div>', unsafe_allow_html=True)
        exp = explanation_cards(record)
        if exp:
            st.markdown("".join(explanation_card(e.reason, e.weight, e.impact) for e in exp),
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="card muted">No positive signals were extracted.</div>',
                        unsafe_allow_html=True)

    st.markdown('<div class="section-title">Validation</div>', unsafe_allow_html=True)
    chips = []
    if record.imei:
        chips.append(chip("IMEI " + ("Luhn passed" if record.imei_valid else "Luhn failed"),
                          "pass" if record.imei_valid else "fail"))
    else:
        chips.append(chip("No IMEI present", "warn"))
    if record.barcode:
        chips.append(chip(f"{record.barcode_type or 'Barcode'} " +
                          ("check digit valid" if record.barcode_valid else "unconfirmed"),
                          "pass" if record.barcode_valid else "warn"))
    else:
        chips.append(chip("No barcode detected", "warn"))
    chips.append(chip(f"Classified: {record.asset_type}",
                      "pass" if record.asset_type not in (None, "", "unknown") else "fail"))
    st.markdown(
        '<div class="card" style="display:flex;gap:0.5rem;flex-wrap:wrap;">'
        + "".join(chips) + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)
    st.markdown(_json_highlight(record), unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        st.download_button("Download JSON", record.to_json(),
                           file_name="asset_result.json", mime="application/json",
                           use_container_width=True)
    with c2:
        st.download_button("Download CSV", _result_to_csv(record),
                           file_name="asset_result.csv", mime="text/csv",
                           use_container_width=True)
    with st.expander("Raw OCR text"):
        st.text(record.raw_ocr_text or "(no text extracted)")


tab_upload, tab_demo = st.tabs(["  Upload  ", "  Demo mode  "])

with tab_upload:
    if Image is None:
        st.error("Pillow is not installed in this environment.")
    else:
        st.markdown(
            '<div class="card" style="text-align:center;border-style:dashed;padding:1.6rem;">'
            '<div style="font-size:1.4rem;margin-bottom:0.4rem;">&#x2913;</div>'
            '<div style="font-weight:600;color:var(--text);">Drag &amp; drop an asset label or device image</div>'
            '<div class="muted" style="font-size:0.85rem;margin-top:0.3rem;">'
            'PNG, JPG, JPEG, GIF or BMP &middot; best results with a flat, well-lit label</div></div>',
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Upload", type=["png", "jpg", "jpeg", "gif", "bmp"], label_visibility="collapsed"
        )
        if uploaded is not None:
            image = Image.open(uploaded)
            prev, ctrl = st.columns([1, 1])
            with prev:
                st.image(image, caption="Preview", use_container_width=True)
            with ctrl:
                st.markdown('<div class="muted" style="margin:0.4rem 0 0.8rem;">'
                            'Ready to analyze. The pipeline will run OCR, barcode decoding, '
                            'field extraction, validation, and confidence scoring.</div>',
                            unsafe_allow_html=True)
                go = st.button("Analyze asset", type="primary")
            if go:
                record = run_pipeline_animated(image)
                st.session_state.history.append({"name": uploaded.name, "score": record.confidence_score})
                render_results(record, image)

with tab_demo:
    st.markdown('<div class="section-title">Run a bundled sample</div>', unsafe_allow_html=True)
    samples = []
    if SAMPLE_DIR.exists():
        samples = sorted(p for p in SAMPLE_DIR.iterdir()
                         if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp"})
    if not samples:
        st.info("No sample images found in data/sample_images/.")
    elif Image is None:
        st.error("Pillow is not installed.")
    else:
        cols = st.columns(len(samples))
        for col, p in zip(cols, samples):
            with col:
                st.image(str(p), caption=p.name, use_container_width=True)
        choice = st.selectbox("Sample image", samples, format_func=lambda p: p.name)
        if st.button("Run sample", type="primary"):
            image = Image.open(choice)
            record = run_pipeline_animated(image)
            st.session_state.history.append({"name": choice.name, "score": record.confidence_score})
            render_results(record, image)
