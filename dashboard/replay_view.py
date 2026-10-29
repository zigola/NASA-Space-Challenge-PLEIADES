from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.maps import render_map
from src.replay_engine import build_replay_index, generate_replay_window


def render_replay_view(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #F1F5F9; font-size: 1.25rem;">Spatiotemporal Fire Event Replay Engine</h3>
            <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px;">
                Simulate temporal fire progression by scrubbing through satellite observation chronologies.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty or "timestamp" not in df.columns:
        st.info("Replay requires observations with valid timestamp metadata.")
        return

    indexed_df = build_replay_index(df)
    if indexed_df.empty:
        st.info("No temporal records available for replay.")
        return

    total_records = len(indexed_df)
    st.caption(f"Chronological event sequence contains {total_records} ordered observation windows.")

    # Slider control
    step = st.slider(
        "Time Progression Window (Earliest ➔ Latest Observation)",
        min_value=1,
        max_value=total_records,
        value=total_records,
        help="Drag to view fire hotspots detected up to this point in time.",
    )

    window_records = generate_replay_window(indexed_df, start_idx=0, end_idx=step - 1)
    window_df = pd.DataFrame(window_records)

    if not window_df.empty:
        current_time = window_df["timestamp"].iloc[-1]
        st.markdown(
            f"""
            <div style="background: #122238; border: 1px solid #25374C; border-radius: 8px; padding: 8px 14px; margin-bottom: 12px; display: inline-flex; gap: 12px; align-items: center;">
                <span style="color: #38BDF8; font-weight: 700;">Active Replay Timestamp:</span>
                <span style="color: #F1F5F9; font-family: monospace;">{current_time}</span>
                <span style="color: #9FB0C5;">({len(window_df)} / {total_records} events accumulated)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_map(window_df, height=480, key="replay_map")


def render_replay(replay: pd.DataFrame) -> None:
    """Backward-compatible entry point."""
    render_replay_view(replay)
