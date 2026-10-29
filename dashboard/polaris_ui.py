from __future__ import annotations

import pandas as pd
import streamlit as st

from config.i18n import LANGUAGES, get_text
from dashboard.alerts_view import render_alerts_panel
from dashboard.charts import render_analytics_panel
from dashboard.layout import render_application_header
from dashboard.maps import render_map
from dashboard.metrics import render_kpis
from dashboard.modern_ui import render_modern_dashboard


def apply_i18n(lang: str = "en") -> None:
    st.session_state.setdefault("lang", lang)
    st.session_state["lang"] = lang
    st.set_page_config(page_title="PLEIADES — Wildfire Intelligence Platform", layout="wide")


def sidebar_nav(lang: str = "en") -> str:
    nav = [
        ("overview", get_text("overview", lang)),
        ("live_map", get_text("live_map", lang)),
        ("satellite", get_text("satellite", lang)),
        ("file_analysis", get_text("file_analysis", lang)),
        ("alerts", get_text("alerts", lang)),
        ("settings", get_text("settings", lang)),
    ]
    return st.sidebar.radio("", nav, index=0, horizontal=False, label_visibility="collapsed")


def render_header(lang: str = "en") -> None:
    render_application_header(page_title="Overview", lang=lang)


def render_alert_panel(df: pd.DataFrame, lang: str = "en") -> None:
    render_alerts_panel(df)


def render_file_analysis(df: pd.DataFrame, lang: str = "en") -> None:
    st.subheader(get_text("file_analysis", lang))
    if df.empty:
        st.info(get_text("empty_state", lang))
        return
    st.dataframe(df, use_container_width=True)


def render_settings(lang: str = "en") -> None:
    st.subheader(get_text("settings_title", lang))
    st.write(get_text("api_status", lang) + ": " + (get_text("api_ready", lang) if st.session_state.get("firms_key_available") else get_text("api_missing", lang)))


def render_demo_dashboard(df: pd.DataFrame | None = None, lang: str = "en") -> None:
    """Primary dashboard entry point that delegates to the modern UI presentation layer."""
    if df is None:
        df = pd.DataFrame()
    render_modern_dashboard(df, lang=lang)
