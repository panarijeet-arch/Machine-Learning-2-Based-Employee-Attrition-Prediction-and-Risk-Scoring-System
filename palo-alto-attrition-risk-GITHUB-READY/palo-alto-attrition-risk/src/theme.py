"""
theme.py
========
Dark, Palo Alto Networks-inspired enterprise palette (near-black
backgrounds, bold white type, orange-red accent) -- matched to
paloaltonetworks.com's actual visual language, checked directly against
the live site before writing this file.

Root-cause fix for the recurring contrast bug: `.streamlit/config.toml`
now sets `base = "dark"` explicitly, not just individual colors. Without
an explicit base, Streamlit partially auto-adapts built-in components
(like st.metric's value text) to each *viewer's own* browser/OS light-
or-dark preference, which is what caused text to go invisible twice
before -- the custom CSS assumed one background, the browser assumed
another. Locking `base = "dark"` makes every viewer see the same,
tested rendering, no matter their own system setting.

No copyrighted logo asset is embedded here -- `brand_header()` renders a
plain text wordmark in a similar visual weight/spacing to the real site,
not a reproduction of their actual logo graphic. If a legitimately-
licensed logo file is available, point LOGO_PATH at it and it will be
used automatically instead.
"""
from __future__ import annotations

import os

import streamlit as st

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")

COLORS = {
    "bg": "#0B0F19",
    "panel": "#141B2D",
    "panel_alt": "#1B2436",
    "border": "#26314A",
    "ink": "#F5F6F8",
    "muted": "#94A3B8",
    "orange": "#FA582D",
    "orange_light": "#FF8A65",
    "blue_accent": "#38BDF8",
    "low_risk": "#22C55E",
    "medium_risk": "#FBBF24",
    "high_risk": "#F87171",
}

RISK_COLOR_MAP = {
    "Low Risk": COLORS["low_risk"],
    "Medium Risk": COLORS["medium_risk"],
    "High Risk": COLORS["high_risk"],
}

PLOTLY_COLORWAY = [COLORS["orange"], COLORS["blue_accent"], COLORS["low_risk"], COLORS["medium_risk"], COLORS["high_risk"]]


def rgba(hex_color: str, alpha: float) -> str:
    """Convert '#RRGGBB' + 0-1 alpha into 'rgba(r,g,b,a)'. Plotly's color
    validator has rejected 8-digit hex-with-alpha strings on some
    versions in the past; rgba() is accepted by every version."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def style_fig(fig):
    """Apply consistent dark styling to any Plotly figure -- transparent
    plot area over the app's own dark background, light gridlines, white
    text. Call this on every figure right before st.plotly_chart()."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["ink"],
        colorway=PLOTLY_COLORWAY,
        legend=dict(font=dict(color=COLORS["ink"])),
    )
    fig.update_xaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"], color=COLORS["ink"])
    fig.update_yaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"], color=COLORS["ink"])
    return fig


def inject_global_css() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-top: 1.6rem;
            max-width: 1400px;
        }}

        /* --- KPI / metric cards --- */
        div[data-testid="stMetric"] {{
            background: {COLORS['panel']};
            border: 1px solid {COLORS['border']};
            border-left: 4px solid {COLORS['orange']};
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
        }}
        div[data-testid="stMetric"] * {{
            color: {COLORS['ink']} !important;
        }}
        div[data-testid="stMetricLabel"] * {{
            color: {COLORS['muted']} !important;
            font-weight: 600 !important;
        }}
        div[data-testid="stMetricValue"] * {{
            color: {COLORS['ink']} !important;
            font-weight: 700 !important;
        }}

        /* --- Right-rail control panel --- */
        .nc-rail {{
            background: {COLORS['panel']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 1rem 1.1rem;
        }}
        .nc-rail, .nc-rail * {{
            color: {COLORS['ink']} !important;
        }}
        .nc-rail-title {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {COLORS['muted']} !important;
            margin-bottom: 0.6rem;
        }}

        /* --- Badges --- */
        .nc-badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 100px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            background: {COLORS['panel_alt']};
            border: 1px solid {COLORS['border']};
            color: {COLORS['ink']} !important;
            margin-right: 6px;
        }}
        .nc-badge.accent {{
            background: {rgba(COLORS['orange'], 0.18)};
            border-color: {COLORS['orange']};
            color: {COLORS['orange_light']} !important;
        }}

        /* --- Risk badges --- */
        .risk-badge {{
            display: inline-block;
            padding: 3px 14px;
            border-radius: 100px;
            font-size: 0.78rem;
            font-weight: 700;
            color: #0B0F19 !important;
        }}

        /* --- Insight callout --- */
        .nc-insight {{
            background: {COLORS['panel']};
            border-left: 4px solid {COLORS['orange']};
            border-radius: 8px;
            padding: 0.9rem 1.2rem;
            margin-bottom: 0.6rem;
        }}
        .nc-insight, .nc-insight * {{
            color: {COLORS['ink']} !important;
        }}
        .nc-insight b {{
            color: {COLORS['orange_light']} !important;
        }}

        /* --- Brand header --- */
        .nc-brand-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 0.4rem;
        }}
        .nc-brand-mark {{
            width: 34px; height: 34px;
            background: {COLORS['orange']};
            border-radius: 7px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 800; color: #0B0F19; font-size: 1.05rem;
            flex-shrink: 0;
        }}
        .nc-brand-word {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {COLORS['ink']} !important;
            letter-spacing: -0.01em;
        }}
        .nc-brand-sub {{
            font-size: 0.72rem;
            color: {COLORS['muted']} !important;
            letter-spacing: 0.02em;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_header() -> None:
    """Text-based wordmark in the site's visual weight/spacing -- not a
    reproduction of the real logo graphic. Swaps in assets/logo.png
    automatically if that file exists (e.g. a legitimately-licensed
    logo you've added yourself)."""
    if os.path.exists(LOGO_PATH):
        c1, c2 = st.columns([1, 8])
        with c1:
            st.image(LOGO_PATH, width=40)
        with c2:
            st.markdown(
                f'<div class="nc-brand-word">Palo Alto Networks</div>'
                f'<div class="nc-brand-sub">HR ANALYTICS &middot; INTERNAL TOOL</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"""
            <div class="nc-brand-row">
                <div class="nc-brand-mark">P</div>
                <div>
                    <div class="nc-brand-word">Palo Alto Networks</div>
                    <div class="nc-brand-sub">HR ANALYTICS &middot; INTERNAL TOOL</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def risk_badge_html(category: str) -> str:
    color = RISK_COLOR_MAP.get(category, COLORS["muted"])
    return f'<span class="risk-badge" style="background:{color};">{category}</span>'


def badge_row_html(badges: list[str], accent_last: bool = True) -> str:
    spans = []
    for i, b in enumerate(badges):
        cls = "nc-badge accent" if (accent_last and i == len(badges) - 1) else "nc-badge"
        spans.append(f'<span class="{cls}">{b}</span>')
    return "".join(spans)


def insight_html(text: str) -> str:
    return f'<div class="nc-insight">{text}</div>'


def hero(title: str, subtitle: str, badges: list[str] | None = None) -> None:
    brand_header()
    st.title(title)
    st.caption(subtitle)
    if badges:
        st.markdown(badge_row_html(badges), unsafe_allow_html=True)
    st.divider()


def rail_start(title: str) -> None:
    st.markdown(f'<div class="nc-rail"><div class="nc-rail-title">{title}</div>', unsafe_allow_html=True)


def rail_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def chart_type_selector(key: str, options=("Bar", "Line"), label: str = "Chart type") -> str:
    return st.radio(label, options, horizontal=True, key=key)
