'''Utility to ensure Streamlit can read/write its credentials file without permission errors.
This module overwrites (or creates) a minimal credentials.toml file in the user's
~/.streamlit directory. It is called at application start‑up before any Streamlit
API is used.
'''
import os
from pathlib import Path

def ensure_streamlit_credentials() -> None:
    """Create or overwrite ``~/.streamlit/credentials.toml`` with minimal content.
    The file must be readable and writable by the current process; Streamlit
    attempts to delete the file on first run, which fails on Windows when the
    existing file has restrictive ACLs. Overwriting avoids the delete step.
    """
    cred_path = Path.home() / ".streamlit" / "credentials.toml"
    # Ensure the parent directory exists
    cred_path.parent.mkdir(parents=True, exist_ok=True)
    # Minimal valid TOML content – empty email disables onboarding prompts
    minimal_content = "[general]\nemail = \"\"\n"
    try:
        cred_path.write_text(minimal_content, encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(
            f"Failed to write Streamlit credentials file at {cred_path!s}: {exc}"
        ) from exc

