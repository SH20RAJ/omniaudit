#!/usr/bin/env python3
"""
OmniAudit-GEO — Pure Gradio Frontend (Standalone Launcher)
Adobe University Hackathon 2026 (Round 3 CRP)

Run locally:
    python3 app.py
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
for p in [
    str(REPO_ROOT / "omniaudit-geo"),
    str(REPO_ROOT / "skills" / "audit-orchestrator" / "scripts"),
    str(REPO_ROOT / "skills" / "crawl-render-audit" / "scripts"),
    str(REPO_ROOT / "scripts"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

from gradio_ui import create_gradio_app

from seo_config import SEO_HEAD_HTML

demo = create_gradio_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 Starting OmniAudit-GEO Gradio UI on http://localhost:{port}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        head=SEO_HEAD_HTML,
        favicon_path=str(REPO_ROOT / "omniaudit-geo" / "public" / "favicon.ico"),
    )
