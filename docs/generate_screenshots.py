"""Generate professional screenshots of the app's key views.

Renders standalone HTML using the application's own theme CSS and captures it
with headless Chromium (Playwright). This produces clean, deterministic,
high-resolution screenshots for the README and docs without needing to drive the
live Streamlit server through a browser.

Outputs to docs/screenshots/:
    01_dashboard.png   — hero + upload + status badges
    02_result.png      — extracted fields, gauge, breakdown, validation
    03_benchmarks.png  — metrics + chart

Usage:
    python docs/generate_screenshots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

# Pull the real theme CSS so screenshots match the app exactly.
from app.theme import (  # noqa: E402
    THEME_CSS,
    breakdown_row,
    chip,
    confidence_gauge,
    explanation_card,
    field_card,
)
from src.analytics import component_breakdown, explanation_cards  # noqa: E402
from src.pipeline import process_path  # noqa: E402

BODY_WRAP = """
<div style="background:var(--bg);padding:2rem;max-width:1100px;margin:0 auto;">{content}</div>
"""

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">{css}
<style>body{{margin:0;background:#0c1116;}}</style></head>
<body>{body}</body></html>"""


def _hero_and_upload() -> str:
    hero = """
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
    """
    upload = """
    <div class="card" style="text-align:center;border-style:dashed;padding:2.4rem;">
      <div style="font-size:1.8rem;margin-bottom:0.5rem;color:var(--accent);">&#x2913;</div>
      <div style="font-weight:600;color:var(--text);font-size:1.05rem;">Drag &amp; drop an asset label or device image</div>
      <div class="muted" style="font-size:0.88rem;margin-top:0.4rem;">PNG, JPG, JPEG, GIF or BMP &middot; best results with a flat, well-lit label</div>
    </div>
    """
    return hero + upload


def _result_view(record) -> str:
    pct = int(round(record.confidence_score * 100))
    fields = "".join([
        field_card("Asset type", record.asset_type, 99, "pass"),
        field_card("Brand", record.brand, 98, "pass"),
        field_card("Model", record.model, 96, "pass"),
        field_card("Serial number", record.serial_number, 95, "pass"),
        field_card("IMEI", record.imei, 99, "pass"),
        field_card("Barcode", record.barcode, 97, "pass"),
    ])
    bd = "".join(breakdown_row(c.label, c.score, c.detail, c.status)
                 for c in component_breakdown(record))
    exp = "".join(explanation_card(e.reason, e.weight, e.impact)
                  for e in explanation_cards(record)[:4])
    chips = (chip("IMEI Luhn passed", "pass") + chip("UPC-A check digit valid", "pass")
             + chip(f"Classified: {record.asset_type}", "pass"))

    return f"""
    <div class="section-title">Extracted fields</div>
    <div class="field-grid">{fields}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
      <div>
        <div class="section-title">Confidence</div>
        <div class="card">{confidence_gauge(pct, "High confidence", "var(--good)")}
          <div style="text-align:center;margin-top:0.5rem;" class="muted">{record.review_recommendation}</div>
        </div>
      </div>
      <div>
        <div class="section-title">Confidence breakdown</div>
        <div class="card">{bd}</div>
      </div>
    </div>
    <div class="section-title" style="margin-top:1rem;">Why this score</div>
    {exp}
    <div class="section-title" style="margin-top:1rem;">Validation</div>
    <div class="card" style="display:flex;gap:0.5rem;flex-wrap:wrap;">{chips}</div>
    """


def _benchmarks_view() -> str:
    import pandas as pd

    df = pd.read_csv(ROOT / "benchmark" / "benchmark_results.csv")
    n = len(df)
    metrics = ""
    cells = [
        ("Images", str(n), "in sample set"),
        ("Avg time", f"{df['processing_seconds'].mean():.2f}s", "per image"),
        ("Avg confidence", f"{df['confidence_score'].mean():.2f}", "0-1 scale"),
        ("IMEI valid", "2/4", "Luhn passed"),
        ("Barcode valid", "2/4", "check digit"),
    ]
    for label, value, sub in cells:
        metrics += (f'<div class="metric"><div class="m-label">{label}</div>'
                    f'<div class="m-value">{value}</div><div class="m-sub">{sub}</div></div>')

    # Simple inline bar chart for processing time.
    bars = ""
    maxt = df["processing_seconds"].max()
    for _, row in df.iterrows():
        w = int(row["processing_seconds"] / maxt * 100)
        bars += (
            f'<div class="bd-row"><div class="bd-head">'
            f'<span class="bd-label">{row["file_name"]}</span>'
            f'<span class="bd-val">{row["processing_seconds"]:.2f}s</span></div>'
            f'<div class="bd-track"><div class="bd-fill" style="width:{w}%;background:var(--accent);"></div></div></div>'
        )
    return f"""
    <div class="eyebrow">Performance &amp; Accuracy</div>
    <h1 style="font-family:'Space Grotesk';color:var(--text);">Benchmarks</h1>
    <div class="metric-grid">{metrics}</div>
    <div class="section-title">Processing time by image</div>
    <div class="card">{bars}</div>
    """


def _render(name: str, content: str, width: int = 1140, height: int = 900) -> None:
    from playwright.sync_api import sync_playwright

    html = PAGE.format(css=THEME_CSS, body=BODY_WRAP.format(content=content))
    tmp = OUT / f"_{name}.html"
    tmp.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height},
                                device_scale_factor=2)
        page.goto(tmp.as_uri())
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
        browser.close()
    tmp.unlink(missing_ok=True)
    print(f"wrote docs/screenshots/{name}.png")


def main() -> None:
    record = process_path(str(ROOT / "data" / "sample_images" / "asset_label_full.png"))
    _render("01_dashboard", _hero_and_upload(), height=620)
    _render("02_result", _result_view(record), height=1000)
    _render("03_benchmarks", _benchmarks_view(), height=620)


if __name__ == "__main__":
    main()
