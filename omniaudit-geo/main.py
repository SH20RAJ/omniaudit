#!/usr/bin/env python3
"""
OmniAudit-GEO — Fast, Deterministic Web Control Plane & MCP API.
Powered by FastAPI & Streamlit. Shares the exact same canonical Python audit engine,
safe_fetch, and MCP server as the CLI and skills marketplace.
100% pure Python. Zero React, zero JavaScript build dependencies.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

# Add repository root and skill directories to sys.path to ensure unified source of truth
REPO_ROOT = Path(__file__).resolve().parent.parent
OMNIAUDIT_DIR = REPO_ROOT / "omniaudit-geo"
SKILLS_DIR = REPO_ROOT / "skills"
ORCHESTRATOR_SCRIPTS = SKILLS_DIR / "audit-orchestrator" / "scripts"
CRAWL_SCRIPTS = SKILLS_DIR / "crawl-render-audit" / "scripts"
ROOT_SCRIPTS = REPO_ROOT / "scripts"

for p in [str(OMNIAUDIT_DIR), str(ORCHESTRATOR_SCRIPTS), str(CRAWL_SCRIPTS), str(ROOT_SCRIPTS)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from eval_benchmarks import run_evals
    from schema_validator import validate_report
except ImportError:
    from scripts.eval_benchmarks import run_evals
    from scripts.schema_validator import validate_report

from audit_guard import check_rate_limit, execute_guarded_audit, execute_guarded_mcp
from audit_runner import (
    HTMLContentExtractor,
    audit_aeo_quotability,
    audit_crawl_render,
    audit_freshness_trust,
    audit_on_site_engagement,
    audit_structured_data,
    enrich_findings_actions,
    fetch_url,
)
from docs_manager import (
    build_documentation_portal_html,
    get_doc_by_id,
    get_docs_catalog,
)
from mcp_server import MCP_TOOLS
from safe_fetch import normalize_url
from seo_config import NOSCRIPT_SEMANTIC_BODY, SEO_HEAD_HTML

app = FastAPI(
    title="OmniAudit-GEO — Brand AI-Readiness & GEO Engine",
    description="Deterministic evaluation platform and Anthropic Model Context Protocol (MCP) server for website AI discoverability and visitor retention.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Hardened, environment-configurable CORS policy
allowed_origins_env = os.environ.get("OMNIAUDIT_ALLOWED_ORIGINS", "").strip()
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "https://omniaudit-geo.onrender.com",
        "http://localhost:8000",
        "http://localhost:7860",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:7860",
    ]

is_wildcard = "*" in allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=not is_wildcard,  # Standard CORS compliance: credentials cannot be true with wildcard
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

PUBLIC_DIR = Path(__file__).resolve().parent / "public"


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    # 1. Unified Rate Limiter for /api/ routes
    if request.url.path.startswith("/api/"):
        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
            request.client.host if request.client else "unknown"
        )
        allowed, retry_after = check_rate_limit(client_ip)
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate Limit Exceeded",
                    "error_code": "rate_limit_exceeded",
                    "message": "Maximum rate limit of 60 requests per minute exceeded.",
                },
                headers={"Retry-After": str(retry_after or 60)},
            )

    # 2. Process Request
    response: Response = await call_next(request)

    # 3. Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), microphone=(), payment=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------


@app.get("/api/health")
async def health_check():
    """Probe for service health and canonical Python engine readiness."""
    return {
        "status": "healthy",
        "service": "omniaudit-geo",
        "version": "1.0.0",
        "engine": "canonical-python-ast",
        "schema": "draft-07",
    }


@app.get("/api/audit")
async def audit_endpoint(
    request: Request, url: str = Query(..., description="Target website URL to audit (e.g. 'https://adobe.com')")
):
    """
    Executes the canonical brand AI-readiness and visitor engagement audit.
    Guarded against abuse, concurrency spikes, SSRF, and timeouts.
    Conforms strictly to skills/audit-orchestrator/references/audit_schema.json.
    """
    if not url or not url.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Bad Request",
                "error_code": "missing_url",
                "message": "Query parameter 'url' is required.",
            },
        )

    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    start_time = time.perf_counter()
    report = execute_guarded_audit(url, client_ip=client_ip)
    elapsed = time.perf_counter() - start_time

    if report.get("error"):
        status_code = report.get("status_code", status.HTTP_400_BAD_REQUEST)
        raise HTTPException(
            status_code=status_code,
            detail=report,
        )

    report["latency"] = f"{elapsed:.2f}s"

    # Recursive schema validation assertion
    is_valid, schema_errors = validate_report(report)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Schema Validation Error", "error_code": "schema_invalid", "details": schema_errors},
        )

    return report


@app.get("/api/audit/robots")
async def audit_robots_endpoint(url: str = Query(...)):
    """Specialist diagnostic: Crawl & robots.txt AI bot permissions."""
    clean_url = normalize_url(url.strip())
    fetch_res = fetch_url(clean_url)
    if fetch_res.get("error"):
        return {"site": clean_url, "error": fetch_res["error"], "findings": []}
    findings = audit_crawl_render(clean_url, fetch_res.get("html", ""), fetch_res.get("headers", {}))
    enrich_findings_actions(findings)
    return {
        "site": clean_url,
        "tool": "inspect_robots_and_rendering",
        "total_findings": len(findings),
        "findings": findings,
    }


@app.get("/api/audit/structured")
async def audit_structured_endpoint(url: str = Query(...)):
    """Specialist diagnostic: Schema.org JSON-LD and sameAs entity disambiguation."""
    clean_url = normalize_url(url.strip())
    fetch_res = fetch_url(clean_url)
    if fetch_res.get("error"):
        return {"site": clean_url, "error": fetch_res["error"], "findings": []}
    extractor = HTMLContentExtractor()
    extractor.feed(fetch_res.get("html", ""))
    findings = audit_structured_data(clean_url, extractor)
    enrich_findings_actions(findings)
    return {"site": clean_url, "tool": "inspect_structured_data", "total_findings": len(findings), "findings": findings}


@app.get("/api/audit/aeo")
async def audit_aeo_endpoint(url: str = Query(...)):
    """Specialist diagnostic: AEO Quotability, fact density, and non-text assets."""
    clean_url = normalize_url(url.strip())
    fetch_res = fetch_url(clean_url)
    if fetch_res.get("error"):
        return {"site": clean_url, "error": fetch_res["error"], "findings": []}
    extractor = HTMLContentExtractor()
    extractor.feed(fetch_res.get("html", ""))
    findings = audit_aeo_quotability(extractor)
    enrich_findings_actions(findings)
    return {"site": clean_url, "tool": "inspect_aeo_quotability", "total_findings": len(findings), "findings": findings}


@app.get("/api/audit/freshness")
async def audit_freshness_endpoint(url: str = Query(...)):
    """Specialist diagnostic: Freshness metadata and trust corroboration signals."""
    clean_url = normalize_url(url.strip())
    fetch_res = fetch_url(clean_url)
    if fetch_res.get("error"):
        return {"site": clean_url, "error": fetch_res["error"], "findings": []}
    html = fetch_res.get("html", "")
    extractor = HTMLContentExtractor()
    extractor.feed(html)
    findings = audit_freshness_trust(extractor, html, clean_url)
    enrich_findings_actions(findings)
    return {"site": clean_url, "tool": "inspect_freshness_trust", "total_findings": len(findings), "findings": findings}


@app.get("/api/audit/engagement")
async def audit_engagement_endpoint(url: str = Query(...)):
    """Specialist diagnostic: On-site retention, hero clarity, and CTA specificity."""
    clean_url = normalize_url(url.strip())
    fetch_res = fetch_url(clean_url)
    if fetch_res.get("error"):
        return {"site": clean_url, "error": fetch_res["error"], "findings": []}
    extractor = HTMLContentExtractor()
    extractor.feed(fetch_res.get("html", ""))
    findings = audit_on_site_engagement(extractor)
    enrich_findings_actions(findings)
    return {
        "site": clean_url,
        "tool": "inspect_on_site_retention",
        "total_findings": len(findings),
        "findings": findings,
    }


# -------------------------------------------------------------
# Anthropic Model Context Protocol (MCP) Endpoints
# -------------------------------------------------------------


@app.get("/mcp")
@app.get("/api/mcp")
async def mcp_info_endpoint():
    """Model Context Protocol (MCP) server capabilities and tool registry."""
    return {
        "name": "omniaudit-geo-mcp-server",
        "version": "1.0.0",
        "protocolVersion": "2024-11-05",
        "description": "OmniAudit-GEO: Brand AI-Readiness & GEO Audit MCP Server (FastAPI)",
        "endpoint": "/mcp",
        "tools": MCP_TOOLS,
    }


@app.post("/mcp")
@app.post("/api/mcp")
async def mcp_rpc_endpoint(request: Request):
    """
    JSON-RPC 2.0 handler for MCP tools/list, tools/call, and initialize.
    Guarded against abuse, concurrency spikes, SSRF, and timeouts.
    """
    try:
        raw_body = await request.body()
        body_str = raw_body.decode("utf-8")
        req_obj = json.loads(body_str) if isinstance(body_str, str) else body_str
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": f"Parse error: {str(exc)}"},
        }
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    rpc_response = execute_guarded_mcp(req_obj, client_ip=client_ip)
    return rpc_response


@app.get("/api/benchmarks")
async def benchmarks_endpoint():
    """Runs the 16 Golden Fixtures benchmark harness and returns statistical metrics."""
    results = run_evals(return_dict=True)
    return results


# -------------------------------------------------------------
# Web Navigation & Redirect Handlers (Frontend is Streamlit)
# -------------------------------------------------------------

REDIRECT_HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=https://omniaudit.streamlit.app/">
{SEO_HEAD_HTML}
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0b0f19;
      color: #f8fafc;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 1rem;
      box-sizing: border-box;
    }}
    .card {{
      text-align: center;
      padding: 2.5rem;
      background: #111827;
      border: 1px solid #1f2937;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      max-width: 480px;
      width: 100%;
    }}
    a {{
      color: #38bdf8;
      text-decoration: none;
      font-weight: 600;
    }}
    a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h2 style="margin-top:0; color:#ffffff;">OmniAudit<span style="color:#38bdf8;">.GEO</span></h2>
    <p style="color:#94a3b8; line-height:1.5;">Navigating to the unified Streamlit interface...</p>
    <p><a href="https://omniaudit.streamlit.app/">Click here to open OmniAudit-GEO on Streamlit</a></p>
  </div>
{NOSCRIPT_SEMANTIC_BODY}
  <script>window.location.replace('https://omniaudit.streamlit.app/');</script>
</body>
</html>
"""


@app.get("/audit", response_class=HTMLResponse)
async def serve_audit(request: Request, url: str | None = None):
    return HTMLResponse(content=REDIRECT_HTML_CONTENT, status_code=200)


@app.get("/benchmarks", response_class=HTMLResponse)
async def serve_benchmarks(request: Request):
    return HTMLResponse(content=REDIRECT_HTML_CONTENT, status_code=200)


@app.get("/marketplace", response_class=HTMLResponse)
async def serve_marketplace(request: Request):
    return HTMLResponse(content=REDIRECT_HTML_CONTENT, status_code=200)


@app.get("/docs", response_class=HTMLResponse)
async def serve_docs(request: Request, doc: str | None = None):
    """Serves the rich, interactive standalone documentation website."""
    initial_slug = doc.strip() if doc and doc.strip() else "getting-started"
    html = build_documentation_portal_html(initial_doc_id=initial_slug)
    return HTMLResponse(content=html, status_code=200)


@app.get("/api/docs/list")
async def api_docs_list():
    """Returns catalog of all available documentation files and metadata."""
    return get_docs_catalog()


@app.get("/api/docs/content")
async def api_docs_content(
    doc: str = Query(..., description="Document ID slug (e.g. 'getting-started', 'architecture')"),
):
    """Returns raw markdown content and metadata for requested document."""
    data = get_doc_by_id(doc.strip())
    if not data:
        raise HTTPException(status_code=404, detail={"error": "Not Found", "message": f"Document '{doc}' not found."})
    return data


# Public static root files (brand assets, favicons, manifests, SEO robots & sitemaps)
@app.get("/brand/{file_name}")
async def serve_brand_asset(file_name: str):
    f = PUBLIC_DIR / "brand" / file_name
    if not f.is_file() or not f.resolve().is_relative_to((PUBLIC_DIR / "brand").resolve()):
        raise HTTPException(status_code=404, detail="Brand asset not found")
    media_type = "image/png" if file_name.endswith(".png") else "application/octet-stream"
    return FileResponse(f, media_type=media_type)


@app.get("/favicon.ico")
async def serve_favicon():
    f = PUBLIC_DIR / "favicon.ico"
    return FileResponse(f, media_type="image/x-icon") if f.is_file() else Response(status_code=404)


@app.get("/favicon-16x16.png")
async def serve_favicon_16():
    f = PUBLIC_DIR / "favicon-16x16.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/favicon-32x32.png")
async def serve_favicon_32():
    f = PUBLIC_DIR / "favicon-32x32.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/favicon-48x48.png")
async def serve_favicon_48():
    f = PUBLIC_DIR / "favicon-48x48.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/favicon.svg")
async def serve_favicon_svg():
    f = PUBLIC_DIR / "favicon-32x32.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/logo.svg")
async def serve_logo():
    f = PUBLIC_DIR / "brand" / "logo.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/og-image.png")
async def serve_og():
    f = PUBLIC_DIR / "brand" / "og-image.png"
    if not f.is_file():
        f = PUBLIC_DIR / "og-image.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/site.webmanifest")
@app.get("/manifest.json")
async def serve_manifest():
    f = PUBLIC_DIR / "site.webmanifest"
    if not f.is_file():
        f = PUBLIC_DIR / "manifest.json"
    return FileResponse(f, media_type="application/manifest+json") if f.is_file() else Response(status_code=404)


@app.get("/robots.txt", response_class=FileResponse)
async def serve_robots():
    f = PUBLIC_DIR / "robots.txt"
    return FileResponse(f, media_type="text/plain; charset=utf-8") if f.is_file() else Response(status_code=404)


@app.get("/sitemap.xml", response_class=FileResponse)
async def serve_sitemap():
    f = PUBLIC_DIR / "sitemap.xml"
    return FileResponse(f, media_type="application/xml; charset=utf-8") if f.is_file() else Response(status_code=404)


@app.get("/llms.txt", response_class=FileResponse)
async def serve_llms():
    f = PUBLIC_DIR / "llms.txt"
    return FileResponse(f, media_type="text/markdown; charset=utf-8") if f.is_file() else Response(status_code=404)


@app.get("/apple-touch-icon.png")
@app.get("/apple-touch-icon-precomposed.png")
async def serve_apple_touch_icon():
    f = PUBLIC_DIR / "apple-touch-icon.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/icon-192.png")
async def serve_icon_192():
    f = PUBLIC_DIR / "icon-192.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


@app.get("/icon-512.png")
async def serve_icon_512():
    f = PUBLIC_DIR / "icon-512.png"
    return FileResponse(f, media_type="image/png") if f.is_file() else Response(status_code=404)


# -------------------------------------------------------------
# Root Landing Portal & Unified Streamlit Bridge (Pure Python)
# -------------------------------------------------------------
ROOT_LANDING_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OmniAudit-GEO — Dual-Engine Brand AI Discoverability &amp; Visitor Retention</title>
  <meta http-equiv="refresh" content="2; url=https://omniaudit.streamlit.app/">
  {SEO_HEAD_HTML}
  <style>
    :root {{
      --bg: #090d16;
      --card: #0f172a;
      --border: #1e293b;
      --accent: #38bdf8;
      --text: #f8fafc;
      --muted: #94a3b8;
    }}
    body {{
      margin: 0;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      box-sizing: border-box;
    }}
    .portal-card {{
      max-width: 680px;
      width: 100%;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 40px;
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6);
      text-align: center;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 14px;
      border-radius: 9999px;
      background: rgba(56, 189, 248, 0.1);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.25);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.05em;
      margin-bottom: 20px;
    }}
    h1 {{
      font-size: 32px;
      font-weight: 800;
      margin: 0 0 12px 0;
      letter-spacing: -0.02em;
    }}
    p.lead {{
      color: var(--muted);
      font-size: 16px;
      line-height: 1.6;
      margin: 0 0 32px 0;
    }}
    .actions {{
      display: flex;
      gap: 12px;
      justify-content: center;
      flex-wrap: wrap;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 12px 22px;
      border-radius: 8px;
      text-decoration: none;
      font-size: 14px;
      font-weight: 600;
      transition: all 0.15s ease;
    }}
    .btn-primary {{
      background: var(--accent);
      color: #090d16;
    }}
    .btn-primary:hover {{
      background: #7dd3fc;
      transform: translateY(-1px);
    }}
    .btn-secondary {{
      background: #1e293b;
      color: var(--text);
      border: 1px solid #334155;
    }}
    .btn-secondary:hover {{
      background: #334155;
      transform: translateY(-1px);
    }}
    .footer-meta {{
      margin-top: 36px;
      padding-top: 20px;
      border-top: 1px solid var(--border);
      font-size: 12px;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
    }}
  </style>
</head>
<body>
  <div class="portal-card">
    <div class="badge">⚡ Streamlit UI &amp; FastAPI Control Plane</div>
    <h1>OmniAudit<span style="color: var(--accent);">.GEO</span></h1>
    <p class="lead">Dual-Engine Brand AI Discoverability (ACPI) &amp; Visitor Retention (CRS) Audit Platform. Auditing machine crawlers and human readability with zero cloud dependencies.</p>
    <div class="actions">
      <a href="https://omniaudit.streamlit.app/" target="_blank" class="btn btn-primary">⚡ Launch Live Streamlit App</a>
      <a href="/docs" class="btn btn-secondary">📖 Documentation Portal</a>
      <a href="/api/docs" class="btn btn-secondary">🔌 OpenAPI REST Docs</a>
    </div>
    <div class="footer-meta">
      <span>Standard: <code>agentskills.io v1.0.0</code></span>
      <span>Engine: Pure Local Python AST</span>
      <span>Status: All 6 Gates Active</span>
    </div>
  </div>
  {NOSCRIPT_SEMANTIC_BODY}
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def serve_root_portal():
    return HTMLResponse(content=ROOT_LANDING_HTML, status_code=200)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting OmniAudit-GEO FastAPI Server on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
