"""Documentation page — renders the project docs in-app."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.theme import page_setup, sidebar_brand  # noqa: E402

page_setup("Documentation")
sidebar_brand()

DOCS = ROOT / "docs"

st.markdown('<div class="eyebrow">Reference</div>', unsafe_allow_html=True)
st.markdown("# Documentation")
st.markdown(
    '<p class="muted">The same documents that ship in the repo under '
    "<code>docs/</code>, rendered here for convenience.</p>",
    unsafe_allow_html=True,
)

DOC_FILES = {
    "Architecture": "architecture.md",
    "Confidence scoring": "confidence_scoring.md",
    "Validation rules": "validation_rules.md",
    "Benchmark methodology": "benchmark_report.md",
    "Limitations & future work": "limitations.md",
}

choice = st.selectbox("Select a document", list(DOC_FILES.keys()))
path = DOCS / DOC_FILES[choice]

if path.exists():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(path.read_text(encoding="utf-8"))
    st.markdown("</div>", unsafe_allow_html=True)
    st.download_button(
        f"Download {DOC_FILES[choice]}",
        path.read_text(encoding="utf-8"),
        file_name=DOC_FILES[choice],
        mime="text/markdown",
    )
else:
    st.warning(f"{DOC_FILES[choice]} not found in docs/.")
