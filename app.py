#!/usr/bin/env python3
"""
OmniAudit-GEO — Streamlit Web Application Launcher
Adobe University Hackathon 2026 (Round 3 CRP)

Run locally:
    python3 app.py
    or:
    streamlit run streamlit_app.py
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    port = os.environ.get("PORT", "8501")
    print(f"🚀 Starting OmniAudit-GEO Streamlit UI on http://localhost:{port}")
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(REPO_ROOT / "streamlit_app.py"),
        "--server.port",
        str(port),
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",
    ]
    sys.exit(subprocess.call(cmd))
