from __future__ import annotations

import streamlit as st
from config.i18n import LANGUAGES, get_text


def apply_pleiades_theme() -> None:
    """Inject the official PLEIADES dark Earth-observation visual design system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {
            --bg-main: #08111F;
            --bg-secondary: #0D1929;
            --surface: #122238;
            --surface-hover: #172B45;
            --border: #25374C;
            --border-focus: #38BDF8;
            --primary-accent: #38BDF8;
            --secondary-accent: #60A5FA;
            --fire-accent: #FF7A45;
            --critical-alert: #F04438;
            --text-primary: #F1F5F9;
            --text-secondary: #9FB0C5;
            --text-muted: #64748B;
            --success: #34D399;
            --warning: #FBBF24;
        }

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: var(--bg-main) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #091220 0%, #060D18 100%) !important;
            border-right: 1px solid var(--border) !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: var(--border) !important;
            margin: 1rem 0 !important;
        }

        /* Container padding */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1560px !important;
        }

        /* Cards and Panels */
        .pleiades-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .pleiades-card:hover {
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
        }

        /* Header Bar */
        .pleiades-header {
            background: linear-gradient(135deg, rgba(18, 34, 56, 0.95) 0%, rgba(13, 25, 41, 0.98) 100%);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        /* Form Controls */
        .stSelectbox, .stMultiselect, .stTextInput, .stNumberInput, .stDateInput {
            border-radius: 8px !important;
        }

        div[data-baseweb="select"] {
            border-radius: 8px !important;
            border-color: var(--border) !important;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            color: var(--text-primary) !important;
        }

        .stButton > button:hover {
            border-color: var(--primary-accent) !important;
            color: var(--primary-accent) !important;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.3) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
            border-color: #38BDF8 !important;
            color: #FFFFFF !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0369A1 0%, #075985 100%) !important;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.5) !important;
        }

        /* DataTables */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-main);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }

        /* Navigation Radio styling */
        [data-testid="stSidebar"] .stRadio > div {
            gap: 4px;
        }
        [data-testid="stSidebar"] .stRadio label {
            background: rgba(18, 34, 56, 0.4);
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 8px 12px;
            color: var(--text-secondary);
            font-size: 0.88rem;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(18, 34, 56, 0.8);
            color: var(--text-primary);
            border-color: var(--border);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_application_header(
    page_title: str = "Overview",
    data_source_mode: str = "Reference Sample Testbed",
    last_refresh_time: str = "Just now",
    alerts_count: int = 0,
    lang: str = "en",
) -> None:
    """Render the master PLEIADES application header bar."""
    is_live = "API" in data_source_mode
    is_upload = "Upload" in data_source_mode

    status_color = "#34D399" if is_live else "#38BDF8" if is_upload else "#F59E0B"
    status_icon = "🟢" if is_live else "📁" if is_upload else "🟡"

    st.markdown(
        f"""
        <div class="pleiades-header">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 10px;
                    background: linear-gradient(135deg, #0284C7 0%, #FF7A45 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.3rem;
                    box-shadow: 0 0 16px rgba(56, 189, 248, 0.4);
                ">
                    🛰️
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.25rem; font-weight: 800; letter-spacing: 0.06em; color: #F1F5F9;">PLEIADES</span>
                        <span style="
                            font-size: 0.68rem;
                            font-weight: 700;
                            letter-spacing: 0.08em;
                            text-transform: uppercase;
                            background: rgba(56, 189, 248, 0.15);
                            color: #38BDF8;
                            border: 1px solid rgba(56, 189, 248, 0.35);
                            padding: 2px 8px;
                            border-radius: 4px;
                        ">
                            NASA Space Apps Challenge
                        </span>
                    </div>
                    <div style="font-size: 0.78rem; color: #9FB0C5; display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                        <span>Earth Observation & Wildfire Geospatial Intelligence</span>
                        <span>·</span>
                        <span style="color: #38BDF8; font-weight: 600;">{page_title}</span>
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                <div style="
                    background: rgba(13, 25, 41, 0.8);
                    border: 1px solid #25374C;
                    border-radius: 8px;
                    padding: 6px 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 0.78rem;
                ">
                    <span>{status_icon}</span>
                    <span style="color: #9FB0C5;">Data Stream:</span>
                    <span style="color: {status_color}; font-weight: 600;">{data_source_mode}</span>
                </div>
                <div style="
                    background: rgba(13, 25, 41, 0.8);
                    border: 1px solid #25374C;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 0.78rem;
                    color: #9FB0C5;
                ">
                    <span>Synced: </span>
                    <span style="color: #F1F5F9; font-weight: 500;">{last_refresh_time}</span>
                </div>
                <div style="
                    background: {'rgba(240, 68, 56, 0.18)' if alerts_count > 0 else 'rgba(13, 25, 41, 0.8)'};
                    border: 1px solid {'rgba(240, 68, 56, 0.4)' if alerts_count > 0 else '#25374C'};
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 0.78rem;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                ">
                    <span>🔔</span>
                    <span style="color: {'#FCA5A5' if alerts_count > 0 else '#9FB0C5'}; font-weight: 600;">
                        {alerts_count} Active Threat Alerts
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
