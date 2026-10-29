from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from config.i18n import LANGUAGES, get_text
from dashboard.modern_ui import render_modern_dashboard
from src.ingest import get_reference_dataset, read_firms_file

st.set_page_config(
    page_title="PLEIADES — Wildfire Intelligence Platform",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
lang = st.session_state["lang"]

if "data_source_mode" not in st.session_state:
    st.session_state["data_source_mode"] = "Sample Reference Testbed"
if "is_sample_data" not in st.session_state:
    st.session_state["is_sample_data"] = True

api_key = os.getenv("NASA_FIRMS_MAP_KEY")
if api_key and "NASA_FIRMS_MAP_KEY" not in st.session_state:
    st.session_state["NASA_FIRMS_MAP_KEY"] = api_key

# Load active dataset
if "custom_data" in st.session_state and isinstance(st.session_state["custom_data"], pd.DataFrame) and not st.session_state["custom_data"].empty:
    all_data = st.session_state["custom_data"]
else:
    all_data = get_reference_dataset()
    st.session_state["custom_data"] = all_data
    st.session_state["is_sample_data"] = True
    st.session_state["data_source_mode"] = "Sample Reference Testbed"

# Render the complete reconstructed UI
render_modern_dashboard(all_data, lang=lang)
