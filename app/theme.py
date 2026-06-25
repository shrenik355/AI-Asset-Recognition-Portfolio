"""Shared theme and reusable UI components for the Streamlit app.

Centralises the design system — colour tokens, typography, and HTML component
builders — so every page renders with one consistent, enterprise-grade look.
Import :func:`inject_theme` at the top of each page, then use the component
helpers to compose cards, badges, gauges, and chips.

Design language: calm slate canvas, a single warm amber accent, soft shadows,
hairline borders, generous spacing — closer to Linear/Vercel/Stripe than to a
default Streamlit dashboard.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# --------------------------------------------------------------------------- #
# Theme
# --------------------------------------------------------------------------- #
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:        #0c1116;
    --surface:   #161d26;
    --surface-2: #1d2734;
    --surface-3: #243041;
    --border:    #2a3543;
    --border-soft: #222c39;
    --text:      #eaf0f6;
    --muted:     #8b99a9;
    --faint:     #5c6776;
    --accent:    #f5a623;
    --accent-2:  #ffc560;
    --accent-dim:#6b4d16;
    --good:      #45d483;
    --warn:      #f5c043;
    --bad:       #f2706e;
    --info:      #5aa9f0;
    --shadow:    0 1px 2px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.28);
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.35);
    --radius:    14px;
}

.stApp { background: var(--bg); color: var(--text); }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1200px; }

h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.02em; color: var(--text); }

/* Sidebar */
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border-soft); }
section[data-testid="stSidebar"] * { color: var(--text); }

/* Eyebrow + section heads */
.eyebrow {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    letter-spacing: 0.22em; text-transform: uppercase; color: var(--accent);
    margin-bottom: 0.8rem;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 1.18rem; font-weight: 600;
    margin: 0.6rem 0 0.9rem 0; color: var(--text);
}
.muted { color: var(--muted); }

/* Hero */
.hero {
    border: 1px solid var(--border); border-radius: 20px; padding: 2.6rem 2.8rem;
    background:
        radial-gradient(130% 150% at 100% 0%, rgba(245,166,35,0.12) 0%, rgba(245,166,35,0) 48%),
        linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%);
    box-shadow: var(--shadow); margin-bottom: 1.4rem;
}
.hero-title {
    font-size: 2.9rem; font-weight: 700; line-height: 1.04; margin: 0 0 0.5rem 0;
}
.hero-title span { color: var(--accent); }
.hero-sub { font-size: 1.05rem; color: var(--text); font-weight: 500; margin-bottom: 0.3rem; }
.hero-tagline {
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: var(--muted);
    letter-spacing: 0.04em; margin-bottom: 1.5rem;
}

/* Status badges (animated) */
.badge-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.status-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.74rem;
    padding: 0.34rem 0.74rem; border-radius: 999px;
    background: var(--surface-2); border: 1px solid var(--border);
    color: var(--text);
}
.status-badge .dot {
    width: 7px; height: 7px; border-radius: 50%; background: var(--good);
    box-shadow: 0 0 0 0 rgba(69,212,131,0.6); animation: pulse 2.4s infinite;
}
.status-badge:nth-child(2) .dot { animation-delay: 0.3s; }
.status-badge:nth-child(3) .dot { animation-delay: 0.6s; }
.status-badge:nth-child(4) .dot { animation-delay: 0.9s; }
.status-badge:nth-child(5) .dot { animation-delay: 1.2s; }
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(69,212,131,0.55); }
    70%  { box-shadow: 0 0 0 6px rgba(69,212,131,0); }
    100% { box-shadow: 0 0 0 0 rgba(69,212,131,0); }
}

/* Cards */
.card {
    border: 1px solid var(--border); border-radius: var(--radius);
    background: var(--surface); padding: 1.3rem 1.45rem; box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}
.card-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 0.9rem;
}

/* Field cards grid */
.field-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.8rem; }
.field-card {
    border: 1px solid var(--border); border-radius: 12px; background: var(--surface-2);
    padding: 0.95rem 1.05rem; transition: border-color 0.15s ease, transform 0.15s ease;
}
.field-card:hover { border-color: var(--accent-dim); transform: translateY(-1px); }
.field-card .fc-name {
    font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 0.4rem;
}
.field-card .fc-value {
    font-size: 1.04rem; font-weight: 600; color: var(--text); word-break: break-all;
    margin-bottom: 0.55rem; font-family: 'Space Grotesk', sans-serif;
}
.field-card .fc-value.empty { color: var(--faint); font-style: italic; font-weight: 400; font-size: 0.9rem; }
.fc-foot { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.fc-conf { font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: var(--muted); }

/* Chips */
.chip {
    display: inline-flex; align-items: center; gap: 0.34rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 500;
    padding: 0.2rem 0.58rem; border-radius: 999px; border: 1px solid var(--border);
}
.chip.pass { color: var(--good); border-color: rgba(69,212,131,0.34); background: rgba(69,212,131,0.08); }
.chip.warn { color: var(--warn); border-color: rgba(245,192,67,0.34); background: rgba(245,192,67,0.08); }
.chip.fail { color: var(--bad);  border-color: rgba(242,112,110,0.34); background: rgba(242,112,110,0.08); }
.chip.info { color: var(--info); border-color: rgba(90,169,240,0.34); background: rgba(90,169,240,0.08); }

/* Breakdown rows */
.bd-row { margin-bottom: 0.85rem; }
.bd-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.35rem; }
.bd-label { font-size: 0.88rem; color: var(--text); }
.bd-val { font-family: 'JetBrains Mono', monospace; font-size: 0.84rem; color: var(--text); }
.bd-track { height: 7px; border-radius: 999px; background: var(--surface-3); overflow: hidden; }
.bd-fill { height: 100%; border-radius: 999px; }
.bd-detail { font-size: 0.76rem; color: var(--muted); margin-top: 0.28rem; }

/* Explanation cards */
.exp-card {
    display: flex; align-items: center; gap: 0.9rem;
    border: 1px solid var(--border); border-radius: 11px; background: var(--surface-2);
    padding: 0.75rem 0.95rem; margin-bottom: 0.55rem;
}
.exp-weight {
    font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.95rem;
    color: var(--accent); min-width: 44px; text-align: center;
    background: rgba(245,166,35,0.1); border: 1px solid var(--accent-dim);
    border-radius: 8px; padding: 0.3rem 0.2rem;
}
.exp-body { flex: 1; }
.exp-reason { font-size: 0.9rem; color: var(--text); font-weight: 500; }
.exp-impact { font-size: 0.76rem; color: var(--muted); margin-top: 0.1rem; }

/* Pipeline stepper */
.pipe-stage { display: flex; align-items: center; gap: 0.9rem; margin-bottom: 0.5rem; }
.pipe-name {
    font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; min-width: 110px; color: var(--text);
}
.pipe-track { flex: 1; height: 9px; border-radius: 999px; background: var(--surface-3); overflow: hidden; }
.pipe-fill { height: 100%; border-radius: 999px; background: var(--accent); }
.pipe-pct { font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: var(--muted); min-width: 40px; text-align: right; }

/* Buttons */
.stButton > button {
    background: var(--accent); color: #1a1206; border: none; border-radius: 11px;
    font-weight: 600; padding: 0.6rem 1.5rem; box-shadow: var(--shadow-sm);
    transition: filter 0.15s ease, transform 0.1s ease;
}
.stButton > button:hover { filter: brightness(1.08); color: #1a1206; }
.stButton > button:active { transform: scale(0.98); }
.stDownloadButton > button {
    background: var(--surface-2); color: var(--text); border: 1px solid var(--border);
    border-radius: 11px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted); padding: 0.45rem 0.9rem; }
.stTabs [aria-selected="true"] { color: var(--accent); }

/* Metric cards */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.8rem; margin-bottom: 1rem; }
.metric {
    border: 1px solid var(--border); border-radius: 12px; background: var(--surface);
    padding: 1.1rem 1.2rem; box-shadow: var(--shadow-sm);
}
.metric .m-label { font-size: 0.74rem; color: var(--muted); margin-bottom: 0.4rem; }
.metric .m-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.7rem; font-weight: 700; color: var(--text); }
.metric .m-sub { font-size: 0.74rem; color: var(--faint); margin-top: 0.25rem; }

/* Code block */
.codeblock {
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; line-height: 1.6;
    background: #0a0e13; border: 1px solid var(--border); border-radius: 12px;
    padding: 1rem 1.2rem; color: #cbd5e1; overflow-x: auto; white-space: pre;
}
.codeblock .k { color: #c792ea; }
.codeblock .s { color: #c3e88d; }
.codeblock .n { color: #f78c6c; }
.codeblock .key { color: #82aaff; }

/* Diagram */
.flow { display: flex; flex-direction: column; align-items: center; gap: 0.1rem; }
.flow-node {
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: var(--text);
    background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px;
    padding: 0.6rem 1.3rem; min-width: 200px; text-align: center;
}
.flow-node.accent { border-color: var(--accent-dim); background: rgba(245,166,35,0.08); color: var(--accent-2); }
.flow-arrow { color: var(--faint); font-size: 1.1rem; line-height: 1.2; }

/* Links / pills */
.pill {
    display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    padding: 0.22rem 0.62rem; border-radius: 8px; background: var(--surface-2);
    border: 1px solid var(--border); color: var(--text); margin: 0.15rem;
}
.method-get  { color: var(--good); border-color: rgba(69,212,131,0.4); }
.method-post { color: var(--accent); border-color: var(--accent-dim); }
</style>
"""


def inject_theme() -> None:
    """Inject the global stylesheet. Call once at the top of every page."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def page_setup(title: str, icon: str = "◆") -> None:
    """Standard ``st.set_page_config`` + theme for a page."""
    st.set_page_config(
        page_title=f"{title} · AI Asset Recognition",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()


# --------------------------------------------------------------------------- #
# Component builders (return HTML strings)
# --------------------------------------------------------------------------- #
def eyebrow(text: str) -> str:
    return f'<div class="eyebrow">{text}</div>'


def section_title(text: str) -> str:
    return f'<div class="section-title">{text}</div>'


def metric_card(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="m-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="metric"><div class="m-label">{label}</div>'
        f'<div class="m-value">{value}</div>{sub_html}</div>'
    )


def chip(text: str, status: str) -> str:
    """status: pass | warn | fail | info"""
    icon = {"pass": "✓", "warn": "!", "fail": "✕", "info": "i"}.get(status, "")
    return f'<span class="chip {status}">{icon} {text}</span>'


def field_card(name: str, value, confidence: int, status: str) -> str:
    if value in (None, "", "unknown"):
        val_html = '<div class="fc-value empty">not found</div>'
        chip_html = chip("Missing", "fail")
        conf_html = ""
    else:
        val_html = f'<div class="fc-value">{value}</div>'
        chip_html = chip(
            {"pass": "Verified", "warn": "Review", "fail": "Failed"}.get(status, "—"),
            status,
        )
        conf_html = f'<span class="fc-conf">{confidence}%</span>'
    return (
        f'<div class="field-card"><div class="fc-name">{name}</div>{val_html}'
        f'<div class="fc-foot">{chip_html}{conf_html}</div></div>'
    )


def breakdown_row(label: str, score: int, detail: str, status: str) -> str:
    colour = {"pass": "var(--good)", "warn": "var(--warn)", "fail": "var(--bad)"}.get(
        status, "var(--accent)"
    )
    return (
        f'<div class="bd-row"><div class="bd-head">'
        f'<span class="bd-label">{label}</span><span class="bd-val">{score}%</span></div>'
        f'<div class="bd-track"><div class="bd-fill" style="width:{score}%;background:{colour};"></div></div>'
        f'<div class="bd-detail">{detail}</div></div>'
    )


def explanation_card(reason: str, weight: int, impact: str) -> str:
    return (
        f'<div class="exp-card"><div class="exp-weight">+{weight}</div>'
        f'<div class="exp-body"><div class="exp-reason">{reason}</div>'
        f'<div class="exp-impact">{impact}</div></div></div>'
    )


def confidence_gauge(pct: int, category: str, colour: str) -> str:
    """An SVG circular gauge for the headline confidence score."""
    radius = 56
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - pct / 100)
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;">
      <svg width="150" height="150" viewBox="0 0 150 150">
        <circle cx="75" cy="75" r="{radius}" fill="none" stroke="var(--surface-3)" stroke-width="12"/>
        <circle cx="75" cy="75" r="{radius}" fill="none" stroke="{colour}" stroke-width="12"
                stroke-linecap="round" stroke-dasharray="{circumference:.1f}"
                stroke-dashoffset="{offset:.1f}" transform="rotate(-90 75 75)"/>
        <text x="75" y="72" text-anchor="middle" font-family="Space Grotesk, sans-serif"
              font-size="34" font-weight="700" fill="var(--text)">{pct}</text>
        <text x="75" y="94" text-anchor="middle" font-family="JetBrains Mono, monospace"
              font-size="11" fill="var(--muted)">PERCENT</text>
      </svg>
      <div style="margin-top:0.4rem;font-family:'Space Grotesk',sans-serif;font-weight:600;
                  font-size:1rem;color:{colour};">{category}</div>
    </div>
    """


def flow_diagram(nodes: list[tuple[str, bool]]) -> str:
    """Vertical pipeline flow diagram. Each node: (label, is_accent)."""
    parts = ['<div class="flow">']
    for i, (label, accent) in enumerate(nodes):
        cls = "flow-node accent" if accent else "flow-node"
        parts.append(f'<div class="{cls}">{label}</div>')
        if i < len(nodes) - 1:
            parts.append('<div class="flow-arrow">↓</div>')
    parts.append("</div>")
    return "".join(parts)


def confidence_colour(pct: int) -> tuple[str, str]:
    """Return (hex-ish css var, category label) for a confidence percentage."""
    if pct >= 85:
        return "var(--good)", "High confidence"
    if pct >= 60:
        return "var(--warn)", "Medium confidence"
    return "var(--bad)", "Low confidence"


def sidebar_brand() -> None:
    """Consistent sidebar header across pages."""
    st.sidebar.markdown(
        """
        <div style="padding:0.4rem 0 1rem 0;border-bottom:1px solid var(--border-soft);margin-bottom:1rem;">
          <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.1rem;color:var(--text);">
            ◆ Asset<span style="color:var(--accent);">AI</span>
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;color:var(--muted);
                      letter-spacing:0.12em;margin-top:0.2rem;">ENTERPRISE CV PIPELINE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
