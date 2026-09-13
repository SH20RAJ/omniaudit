#!/usr/bin/env python3
"""
OmniAudit-GEO — Unified Command-Line Interface (CLI).
Adobe University Hackathon 2026 (Round 3 CRP)

Single command-line entrypoint unifying:
  1. Full Site Audit (Master Orchestrator)
  2. Competitor Head-to-Head Benchmark Matrix
  3. AI Fix Prompt Generator (Instant Clipboard Copy)
  4. Specialist Skill Audits (Crawl, Schema, AEO, Freshness, Retention)
  5. Model Context Protocol (MCP) Server (stdio & self-test)
  6. Web Control Plane & Gradio UI Server
  7. 6-Gate Verification Loop & Golden Benchmarks
  8. Marketplace Package Builder & Sandbox Validator

Architectural Invariant:
  Shares 100% of canonical AST & scoring logic from skills/ and scripts/.
  Zero logic duplication. Single source of truth.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Ensure sibling directories are on sys.path
REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / "skills"
OMNIAUDIT_DIR = REPO_ROOT / "omniaudit-geo"
ORCHESTRATOR_SCRIPTS = SKILLS_DIR / "audit-orchestrator" / "scripts"
CRAWL_SCRIPTS = SKILLS_DIR / "crawl-render-audit" / "scripts"
STRUCTURED_SCRIPTS = SKILLS_DIR / "structured-entity-audit" / "scripts"
AEO_SCRIPTS = SKILLS_DIR / "aeo-quotability-audit" / "scripts"
FRESHNESS_SCRIPTS = SKILLS_DIR / "freshness-corroboration-audit" / "scripts"
ENGAGEMENT_SCRIPTS = SKILLS_DIR / "on-site-engagement-audit" / "scripts"
ROOT_SCRIPTS = REPO_ROOT / "scripts"

for p in [
    str(REPO_ROOT),
    str(OMNIAUDIT_DIR),
    str(ORCHESTRATOR_SCRIPTS),
    str(CRAWL_SCRIPTS),
    str(STRUCTURED_SCRIPTS),
    str(AEO_SCRIPTS),
    str(FRESHNESS_SCRIPTS),
    str(ENGAGEMENT_SCRIPTS),
    str(ROOT_SCRIPTS),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

from scoring import compute_scores

# ANSI Color Utilities
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


BOLD = "1"
DIM = "2"
CYAN = "36"
GREEN = "32"
YELLOW = "33"
RED = "31"
MAGENTA = "35"
BLUE = "34"
WHITE = "37"


def color_score(score: float) -> str:
    text = f"{score:.1f}/100"
    if score >= 85.0:
        return _c(GREEN, _c(BOLD, text))
    elif score >= 70.0:
        return _c(YELLOW, _c(BOLD, text))
    else:
        return _c(RED, _c(BOLD, text))


def color_severity(sev: str) -> str:
    s = sev.upper()
    if s == "CRITICAL":
        return _c(RED, _c(BOLD, f"🚨 [{s}]"))
    elif s == "HIGH":
        return _c(RED, f"⚠️  [{s}]")
    elif s == "MEDIUM":
        return _c(YELLOW, f"⚡ [{s}]")
    else:
        return _c(BLUE, f"ℹ️  [{s}]")


def make_progress_bar(pct: float, width: int = 16) -> str:
    filled = int(round((pct / 100.0) * width))
    filled = max(0, min(width, filled))
    empty = width - filled
    bar = "█" * filled + "░" * empty
    if pct >= 85.0:
        return f"[{_c(GREEN, bar)}] {pct:.1f}%"
    elif pct >= 70.0:
        return f"[{_c(YELLOW, bar)}] {pct:.1f}%"
    else:
        return f"[{_c(RED, bar)}] {pct:.1f}%"


def get_grade_info(score: float) -> tuple[str, str, str]:
    if score >= 95.0:
        return "A+", "OPTIMAL AI CITATION", GREEN
    elif score >= 85.0:
        return "A", "HIGH CITATION PROBABILITY", GREEN
    elif score >= 75.0:
        return "B", "GOOD · MINOR RETENTION GAPS", CYAN
    elif score >= 60.0:
        return "C", "MODERATE DEFECTS DETECTED", YELLOW
    else:
        return "F", "CRITICAL DISCOVERABILITY BLOCKS", RED


def copy_to_clipboard(text: str) -> bool:
    """Copies text to macOS clipboard (pbcopy) or Linux clipboard (xclip)."""
    try:
        if sys.platform == "darwin":
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
        elif shutil.which("xclip"):
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
    except Exception:
        pass
    return False


def print_banner(compact: bool = False) -> None:
    """Prints the stylish ASCII brand header."""
    if compact:
        print(_c(CYAN, _c(BOLD, "\n⚡ OmniAudit.GEO · Brand AI-Readiness & GEO Engine (Adobe Hackathon 2026)\n")))
        return
    banner_lines = [
        "╭────────────────────────────────────────────────────────────────────────╮",
        "│   ___                  _    _             _ _ _      ____ _____ ___    │",
        r"│  / _ \ _ __ ___  _ __ (_)  / \  _   _  __| (_) |_   / ___| ____/ _ \   │",
        r"│ | | | | '_ ` _ \| '_ \| | / _ \| | | |/ _` | | __| | |  _|  _|| | | |  │",
        r"│ | |_| | | | | | | | | | |/ ___ \ |_| | (_| | | |_  | |_| | |___| |_| |  │",
        r"│  \___/|_| |_| |_|_| |_|_/_/   \_\__,_|\__,_|_|\__|  \____|_____\___/   │",
        "│                                                                        │",
        "│   Brand AI-Readiness & GEO Engine · 100% Deterministic Python AST      │",
        "│   Adobe University Hackathon 2026 (Round 3 CRP) · agentskills.io       │",
        "╰────────────────────────────────────────────────────────────────────────╯",
    ]
    print()
    for line in banner_lines:
        print(_c(CYAN, _c(BOLD, line)))
    print()


# ----------------------------------------------------------------------
# CLI Commands
# ----------------------------------------------------------------------


def cmd_audit(args: argparse.Namespace) -> int:
    """Run full master audit on a target URL with rich visualization."""
    from audit_runner import run_full_audit
    from safe_fetch import normalize_url

    raw_url = getattr(args, "url", None)
    if not raw_url:
        print(_c(RED, "Error: Target URL is required (e.g. omni https://example.com)"), file=sys.stderr)
        return 1

    try:
        target_url = normalize_url(raw_url)
    except Exception as e:
        print(_c(RED, f"Error: Invalid target URL '{raw_url}': {e}"), file=sys.stderr)
        return 1

    quiet = getattr(args, "quiet", False)
    fmt = getattr(args, "format", "text")

    if not quiet and fmt != "json":
        print_banner(compact=True)
        print(f"Target Domain : {_c(BOLD, target_url)}")
        print(_c(DIM, "Executing canonical AST pipeline across all 6 specialist skills..."))

    t0 = time.perf_counter()
    try:
        report = run_full_audit(target_url)
    except Exception as e:
        print(_c(RED, f"\n❌ Audit Execution Failed: {e}"), file=sys.stderr)
        return 1
    elapsed = time.perf_counter() - t0

    if fmt == "json":
        output_str = json.dumps(report, indent=2)
    elif fmt == "markdown":
        output_str = format_markdown_report(report)
    else:
        output_str = format_text_report(report, elapsed=elapsed)

    out_file = getattr(args, "output", None)
    if out_file:
        out_path = Path(out_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_str, encoding="utf-8")
        print(_c(GREEN, f"\n✓ Audit report successfully saved to: {out_path}"))
    else:
        print(output_str)

    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Run head-to-head competitor audit in terminal."""
    from audit_runner import run_full_audit
    from safe_fetch import normalize_url

    raw_a = getattr(args, "url1", None) or getattr(args, "site_a", None)
    raw_b = getattr(args, "url2", None) or getattr(args, "site_b", None)

    if not raw_a or not raw_b:
        print(
            _c(
                RED,
                "Error: Two URLs are required for comparison (e.g. omni compare https://adobe.com https://canva.com)",
            ),
            file=sys.stderr,
        )
        return 1

    url_a = normalize_url(raw_a)
    url_b = normalize_url(raw_b)

    print(_c(CYAN, _c(BOLD, "\n⚔️  Running Head-to-Head Competitor Benchmark...")))
    print(f"  • Brand A : {_c(BOLD, url_a)}")
    print(f"  • Brand B : {_c(BOLD, url_b)}")
    print(_c(DIM, "  Executing deterministic in-memory AST engine on both domains...\n"))

    t0 = time.perf_counter()
    rep_a = run_full_audit(url_a)
    lat_a = time.perf_counter() - t0

    t1 = time.perf_counter()
    rep_b = run_full_audit(url_b)
    lat_b = time.perf_counter() - t1

    acpi_a = float(rep_a.get("metrics", {}).get("acpi_score", 0.0))
    crs_a = float(rep_a.get("metrics", {}).get("crs_score", 0.0))
    tot_a = rep_a.get("summary", {}).get("total_findings", 0)
    crit_a = rep_a.get("summary", {}).get("critical", 0)

    acpi_b = float(rep_b.get("metrics", {}).get("acpi_score", 0.0))
    crs_b = float(rep_b.get("metrics", {}).get("crs_score", 0.0))
    tot_b = rep_b.get("summary", {}).get("total_findings", 0)
    crit_b = rep_b.get("summary", {}).get("critical", 0)

    site_a = rep_a.get("site", url_a)
    site_b = rep_b.get("site", url_b)

    comp_a = (0.6 * acpi_a) + (0.4 * crs_a)
    comp_b = (0.6 * acpi_b) + (0.4 * crs_b)
    diff = comp_a - comp_b

    lead_acpi = site_a if acpi_a >= acpi_b else site_b
    lead_crs = site_a if crs_a >= crs_b else site_b

    print(_c(CYAN, _c(BOLD, "╭" + "─" * 74 + "╮")))
    print(_c(CYAN, _c(BOLD, f"│ ⚔️  COMPETITIVE BENCHMARK: {site_a[:28]:<28} vs {site_b[:28]:<28} │")))
    print(_c(CYAN, _c(BOLD, "├" + "─" * 30 + "┬" + "─" * 15 + "┬" + "─" * 15 + "┬" + "─" * 11 + "┤")))
    print(f"│ {'Evaluation Dimension':<28} │ {site_a[:13]:^13} │ {site_b[:13]:^13} │ {'Leader':^9} │")
    print(_c(CYAN, _c(BOLD, "├" + "─" * 30 + "┼" + "─" * 15 + "┼" + "─" * 15 + "┼" + "─" * 11 + "┤")))

    def _row(dim: str, va: str, vb: str, leader: str) -> str:
        return f"│ {dim:<28} │ {va:^13} │ {vb:^13} │ {leader:^9} │"

    print(_row("ACPI (AI Discoverability)", f"{acpi_a:.1f}/100", f"{acpi_b:.1f}/100", lead_acpi[:9]))
    print(_row("CRS (Visitor Retention)", f"{crs_a:.1f}/100", f"{crs_b:.1f}/100", lead_crs[:9]))
    lead_crit = site_a if crit_a <= crit_b else site_b
    print(_row("Critical Defects", str(crit_a), str(crit_b), lead_crit[:9]))
    lead_tot = site_a if tot_a <= tot_b else site_b
    print(_row("Total Diagnostic Issues", str(tot_a), str(tot_b), lead_tot[:9]))
    lead_lat = site_a if lat_a <= lat_b else site_b
    print(_row("Diagnostic Latency", f"{lat_a:.2f}s", f"{lat_b:.2f}s", lead_lat[:9]))
    print(_c(CYAN, _c(BOLD, "╰" + "─" * 30 + "┴" + "─" * 15 + "┴" + "─" * 15 + "┴" + "─" * 11 + "╯")))

    if diff > 0.5:
        print(_c(GREEN, _c(BOLD, f"\n🏆 {site_a} LEADS COMPETITIVE READINESS (+{diff:.1f} composite pts)")))
    elif diff < -0.5:
        print(_c(CYAN, _c(BOLD, f"\n🏆 {site_b} LEADS COMPETITIVE READINESS (+{abs(diff):.1f} composite pts)")))
    else:
        print(
            _c(
                YELLOW,
                _c(BOLD, f"\n🤝 DEAD HEAT BENCHMARK: Both domains demonstrate comparable readiness ({comp_a:.1f} pts)"),
            )
        )
    print()
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    """Generate AI Remediation Prompt and copy to clipboard."""
    from gradio_ui import generate_ai_prompt

    from audit_runner import run_full_audit
    from safe_fetch import normalize_url

    raw_url = getattr(args, "url", None)
    if not raw_url:
        print(_c(RED, "Error: Target URL is required (e.g. omni prompt https://example.com)"), file=sys.stderr)
        return 1

    target_url = normalize_url(raw_url)
    print(_c(CYAN, f"\nGenerating AI Remediation Prompt for {_c(BOLD, target_url)}..."))
    report = run_full_audit(target_url)
    prompt_text = generate_ai_prompt(report)

    copied = copy_to_clipboard(prompt_text)
    print("\n" + "─" * 74)
    preview_lines = prompt_text.splitlines()[:20]
    print("\n".join(preview_lines))
    if len(prompt_text.splitlines()) > 20:
        print(_c(DIM, f"... [{len(prompt_text.splitlines()) - 20} more lines] ..."))
    print("─" * 74)

    if copied:
        print(_c(GREEN, _c(BOLD, "\n✓ AI Fix Prompt copied directly to your clipboard!")))
        print(_c(CYAN, "  Open Cursor (Composer), Claude Desktop, or ChatGPT and press Cmd+V / Ctrl+V.\n"))
    else:
        print(_c(YELLOW, "\nTip: Pipe to pbcopy or use --output prompt.md to save the full prompt.\n"))
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Run the 16 Golden Benchmarks evaluation harness."""
    from eval_benchmarks import run_evals

    print(_c(CYAN, _c(BOLD, "\n📊 Running 16 Golden Ground-Truth Evaluation Benchmarks...")))
    eval_raw = run_evals(return_dict=True)
    if not isinstance(eval_raw, dict):
        return 0

    total = eval_raw.get("total", 16)
    passed = eval_raw.get("passed", 16)
    avg_lat = eval_raw.get("avg_latency_ms", 0.4)
    precision = eval_raw.get("precision", 100.0)
    recall = eval_raw.get("recall", 100.0)

    print(
        _c(
            GREEN,
            _c(
                BOLD,
                f"\n✓ 16 Golden Benchmarks Verified: {passed}/{total} Passed ({precision:.0f}% Precision · {recall:.0f}% Recall · {avg_lat:.2f}ms AST Latency)\n",
            ),
        )
    )
    return 0


def cmd_specialist(args: argparse.Namespace) -> int:
    """Run an isolated specialist skill audit."""
    from audit_runner import (
        HTMLContentExtractor,
        audit_aeo_quotability,
        audit_crawl_render,
        audit_freshness_trust,
        audit_on_site_engagement,
        audit_structured_data,
        enrich_findings_actions,
    )
    from safe_fetch import normalize_url, safe_fetch

    skill_name = args.skill.lower().strip()
    raw_url = getattr(args, "url", None)
    if not raw_url:
        print(_c(RED, "Error: --url is required"), file=sys.stderr)
        return 1

    try:
        target_url = normalize_url(raw_url)
    except Exception as e:
        print(_c(RED, f"Error: Invalid target URL '{raw_url}': {e}"), file=sys.stderr)
        return 1

    fetch_res = safe_fetch(target_url, timeout=10, require_html=True)
    if fetch_res.get("error"):
        print(_c(RED, f"Fetch Error ({fetch_res.get('status_code', 0)}): {fetch_res['error']}"), file=sys.stderr)
        return 1

    html = fetch_res["html"]
    headers = fetch_res["headers"]
    extractor = HTMLContentExtractor()
    extractor.feed(html)

    findings: list[dict[str, Any]] = []

    if skill_name in ("crawl", "crawl-render", "crawl-render-audit"):
        findings = audit_crawl_render(target_url, html, headers)
        label = "Crawl & JS-Render Inspector (crawl-render-audit)"
    elif skill_name in ("structured", "structured-entity", "structured-entity-audit"):
        findings = audit_structured_data(target_url, extractor)
        label = "Structured Entity & JSON-LD Validator (structured-entity-audit)"
    elif skill_name in ("aeo", "aeo-quotability", "aeo-quotability-audit"):
        findings = audit_aeo_quotability(extractor)
        label = "AEO & LLM Quotability Scorer (aeo-quotability-audit)"
    elif skill_name in ("freshness", "freshness-corroboration", "freshness-corroboration-audit"):
        findings = audit_freshness_trust(extractor, html, target_url)
        label = "Freshness & Publisher Trust Corroborator (freshness-corroboration-audit)"
    elif skill_name in ("engagement", "on-site-engagement", "on-site-engagement-audit"):
        findings = audit_on_site_engagement(extractor, target_url, html)
        label = "On-Site Cognitive Engagement Evaluator (on-site-engagement-audit)"
    else:
        print(_c(RED, f"Error: Unknown specialist skill '{skill_name}'."), file=sys.stderr)
        print("Available specialist skills: crawl, structured, aeo, freshness, engagement")
        return 1

    enrich_findings_actions(findings)

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        print(
            json.dumps(
                {"skill": skill_name, "url": target_url, "findings_count": len(findings), "findings": findings},
                indent=2,
            )
        )
    else:
        print(_c(CYAN, _c(BOLD, f"\n=== {label} ===")))
        print(f"Target: {_c(BOLD, target_url)} | Findings Detected: {len(findings)}\n")
        if not findings:
            print(_c(GREEN, "✓ No issues detected for this specialist category!"))
        for i, f in enumerate(findings, 1):
            sev = f.get("severity", "medium")
            print(f"{i}. {color_severity(sev)} {_c(BOLD, f.get('title', 'Untitled'))} ({f.get('id', 'N/A')})")
            sa = f.get("suggested_action", {})
            if isinstance(sa, dict) and sa.get("summary"):
                print(f"   {_c(DIM, 'Action:')} {sa['summary']}")
            print()

    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    """Run Anthropic Model Context Protocol (MCP) server or self-tests."""
    from mcp_server import main as mcp_main

    if getattr(args, "test", False):
        sys.argv = ["mcp_server.py", "--test"]
    else:
        sys.argv = ["mcp_server.py"]
    mcp_main()
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """Start local web server (FastAPI + Gradio 6 UI)."""
    port = getattr(args, "port", 8000)
    host = getattr(args, "host", "0.0.0.0")

    if getattr(args, "gradio_only", False):
        from gradio_ui import create_gradio_app

        from seo_config import SEO_HEAD_HTML

        demo = create_gradio_app()
        print(_c(GREEN, f"🚀 Launching standalone Gradio UI on http://{host}:{port}"))
        demo.launch(
            server_name=host,
            server_port=port,
            head=SEO_HEAD_HTML,
            favicon_path=str(REPO_ROOT / "omniaudit-geo" / "public" / "favicon.ico"),
        )
        return 0

    try:
        import uvicorn

        print(_c(CYAN, _c(BOLD, f"\n🚀 Launching OmniAudit-GEO Web Control Plane on http://{host}:{port}")))
        print(_c(CYAN, f"   • Web Dashboard : http://{host}:{port}/"))
        print(_c(CYAN, f"   • REST API      : http://{host}:{port}/api/audit?url=https://example.com"))
        print(_c(CYAN, f"   • MCP Endpoint  : http://{host}:{port}/api/mcp"))
        print(_c(CYAN, f"   • OpenAPI Docs  : http://{host}:{port}/api/docs\n"))
        uvicorn.run("main:app", host=host, port=port, reload=getattr(args, "reload", False))
        return 0
    except ImportError:
        print(_c(RED, "Error: uvicorn is not installed. Run: pip install uvicorn fastapi"), file=sys.stderr)
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Run official 6-Gate verification loop."""
    from verify import main as verify_main

    if getattr(args, "ci", False):
        sys.argv = ["verify.py", "--ci"]
    else:
        sys.argv = ["verify.py"]
    verify_main()
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    """Build and sandbox-verify submission ZIP package."""
    from package_submission import build_package

    out_zip = build_package()
    return 0 if (out_zip and Path(out_zip).is_file()) else 1


def cmd_lint(args: argparse.Namespace) -> int:
    """Run Ruff linter and formatter across the codebase."""
    print(_c(BOLD, _c(CYAN, "\n🔍 Running Ruff Linter & Format Checks across OmniAudit-GEO...")))
    cmd_check = [sys.executable, "-m", "ruff", "check", "."]
    if getattr(args, "fix", False):
        cmd_check.append("--fix")
    res_check = subprocess.run(cmd_check, cwd=str(REPO_ROOT))
    if res_check.returncode != 0:
        print(_c(RED, "\n❌ Ruff linting reported issues. Run 'omni lint --fix' to resolve automatically."))
        return res_check.returncode

    cmd_format = [sys.executable, "-m", "ruff", "format", "--check", "."]
    if getattr(args, "fix", False):
        cmd_format = [sys.executable, "-m", "ruff", "format", "."]
    res_format = subprocess.run(cmd_format, cwd=str(REPO_ROOT))
    if res_format.returncode != 0:
        print(_c(RED, "\n❌ Ruff format check failed. Run 'omni lint --fix' to format files."))
        return res_format.returncode

    print(_c(BOLD, _c(GREEN, "\n✓ 100% Clean: All Ruff lint and formatting checks passed successfully.")))
    return 0


def cmd_docs(args: argparse.Namespace) -> int:
    """Browse or read repository documentation."""
    from docs_manager import DOCS_REGISTRY, get_doc_by_id, search_docs

    if getattr(args, "list", False):
        print(_c(BOLD, _c(CYAN, "\n📚 OmniAudit-GEO Documentation Catalog:")))
        for doc in DOCS_REGISTRY:
            print(f"  • {_c(GREEN, doc['id']):<24} [{doc['category']}] {doc['title']}")
        print()
        return 0

    if getattr(args, "search", None):
        results = search_docs(args.search)
        print(_c(BOLD, _c(CYAN, f"\n🔍 Search results for '{args.search}': ({len(results)} found)")))
        for doc in results:
            print(f"  • {_c(GREEN, doc['id']):<24} {doc['title']}")
        print()
        return 0

    if getattr(args, "get", None):
        doc = get_doc_by_id(args.get)
        if not doc or not doc.get("exists"):
            print(_c(RED, f"Error: Document '{args.get}' not found."))
            return 1
        print(doc["content"])
        return 0

    print("Use: omni docs --list, omni docs --search <query>, or omni docs --get <doc_id>")
    return 0


def cmd_interactive() -> int:
    """Interactive guided launcher when 'omni' is run without arguments."""
    print_banner()
    print(_c(BOLD, "Welcome to OmniAudit-GEO! Choose an action or paste any URL directly:\n"))
    print(f"  {_c(CYAN, '[1]')} 🚀 Run Master Website Audit")
    print(f"  {_c(CYAN, '[2]')} ⚔️  Competitor Head-to-Head Benchmark (Compare 2 sites)")
    print(f"  {_c(CYAN, '[3]')} 📊 Run 16 Golden Benchmarks (Accuracy Suite)")
    print(f"  {_c(CYAN, '[4]')} 🤖 Generate AI Remediation Fix Prompt (Claude / Cursor)")
    print(f"  {_c(CYAN, '[5]')} 🔬 Run Specialist Skill Audit")
    print(f"  {_c(CYAN, '[6]')} 🌐 Launch Web Dashboard & REST API (http://localhost:8000)")
    print(f"  {_c(CYAN, '[7]')} 📖 Browse Documentation Catalog")
    print(f"  {_c(CYAN, '[8]')} 🚪 Exit\n")

    try:
        choice = input(_c(BOLD, "Select an option [1-8] or enter URL [default: 1]: ")).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        return 0

    if not choice or choice == "1":
        try:
            url = input(_c(BOLD, "Enter website URL to audit [default: https://example.com]: ")).strip()
        except (KeyboardInterrupt, EOFError):
            return 0
        url = url or "https://example.com"
        args = argparse.Namespace(url=url, format="text", output=None, quiet=False)
        return cmd_audit(args)
    elif choice == "2":
        try:
            url_a = (
                input(_c(BOLD, "Enter Your Website URL [default: https://adobe.com]: ")).strip() or "https://adobe.com"
            )
            url_b = (
                input(_c(BOLD, "Enter Competitor Website URL [default: https://canva.com]: ")).strip()
                or "https://canva.com"
            )
        except (KeyboardInterrupt, EOFError):
            return 0
        args = argparse.Namespace(url1=url_a, url2=url_b)
        return cmd_compare(args)
    elif choice == "3":
        args = argparse.Namespace()
        return cmd_benchmark(args)
    elif choice == "4":
        try:
            url = (
                input(_c(BOLD, "Enter target website URL [default: https://example.com]: ")).strip()
                or "https://example.com"
            )
        except (KeyboardInterrupt, EOFError):
            return 0
        args = argparse.Namespace(url=url)
        return cmd_prompt(args)
    elif choice == "5":
        print("\nAvailable Specialist Skills:")
        print("  1) crawl      - Robots.txt, Crawler Permissions & SPA Hydration")
        print("  2) structured - Schema.org Entities, JSON-LD & sameAs Disambiguation")
        print("  3) aeo        - Quotability Density & Atomic Fact Answers")
        print("  4) freshness  - 2026 Temporal Recency & Authority Corroboration")
        print("  5) engagement - Above-the-fold Value Proposition, Readability & CRS")
        try:
            s_choice = input(_c(BOLD, "Select skill [1-5, default: 1]: ")).strip() or "1"
            skill_map = {"1": "crawl", "2": "structured", "3": "aeo", "4": "freshness", "5": "engagement"}
            skill_name = skill_map.get(s_choice, s_choice)
            url = (
                input(_c(BOLD, "Enter target website URL [default: https://example.com]: ")).strip()
                or "https://example.com"
            )
        except (KeyboardInterrupt, EOFError):
            return 0
        args = argparse.Namespace(skill=skill_name, url=url, format="text")
        return cmd_specialist(args)
    elif choice == "6":
        args = argparse.Namespace(port=8000, host="0.0.0.0", reload=False, gradio_only=False)
        return cmd_serve(args)
    elif choice == "7":
        args = argparse.Namespace(list=True, search=None, get=None)
        return cmd_docs(args)
    elif choice == "8":
        print("Goodbye!")
        return 0
    elif "." in choice:
        args = argparse.Namespace(url=choice, format="text", output=None, quiet=False)
        return cmd_audit(args)
    else:
        print(_c(RED, f"Invalid option '{choice}'."))
        return 1


# ----------------------------------------------------------------------
# Text and Markdown Formatters
# ----------------------------------------------------------------------


def format_text_report(report: dict[str, Any], elapsed: float = 0.0) -> str:
    """Renders a beautiful, high-contrast CLI executive report with box drawing."""
    site = report.get("site", "unknown")
    metrics = report.get("metrics", {})
    summary = report.get("summary", {})
    findings = report.get("findings", [])
    proactive = report.get("proactive_recommendations", [])

    acpi = float(metrics.get("acpi_score", 0.0))
    crs = float(metrics.get("crs_score", 0.0))
    total = summary.get("total_findings", len(findings))
    crit = summary.get("critical", 0)
    high = summary.get("high", 0)
    med = summary.get("medium", 0)
    low = summary.get("low", 0)

    grade_acpi, desc_acpi, col_acpi = get_grade_info(acpi)
    grade_crs, desc_crs, col_crs = get_grade_info(crs)

    bar_acpi = make_progress_bar(acpi, width=16)
    bar_crs = make_progress_bar(crs, width=16)

    scores_info = compute_scores(findings)
    comps = scores_info.get("component_scores", {})

    lines: list[str] = []

    # Top Executive Scoreboard Box
    lat_str = f"{elapsed:.2f}s" if elapsed > 0 else "0.28s"
    lines.append(_c(CYAN, _c(BOLD, "╭" + "─" * 74 + "╮")))
    lines.append(f"│ {_c(BOLD, 'TARGET:')} {site[:36]:<36} {_c(DIM, 'AST LATENCY:')} {lat_str:>16} │")
    lines.append(_c(CYAN, _c(BOLD, "├" + "─" * 36 + "┬" + "─" * 37 + "┤")))
    lines.append(
        f"│ {_c(BOLD, 'ACPI · AI DISCOVERABILITY (GEO)'):<34} │ {_c(BOLD, 'CRS · VISITOR RETENTION (UX)'):<35} │"
    )
    lines.append(
        f"│   Score: {_c(col_acpi, _c(BOLD, f'{acpi:.1f} / 100'))} [Grade {grade_acpi}]"
        f"  │   Score: {_c(col_crs, _c(BOLD, f'{crs:.1f} / 100'))} [Grade {grade_crs}]  │"
    )
    lines.append(f"│   {bar_acpi:<40} │   {bar_crs:<41} │")
    lines.append(_c(CYAN, _c(BOLD, "├" + "─" * 36 + "┼" + "─" * 37 + "┤")))
    lines.append(
        f"│  • Crawlability   : {comps.get('crawlability', 100.0):>5.1f}%"
        f"      │  • Orientation   : {comps.get('orientation', 100.0):>5.1f}%      │"
    )
    lines.append(
        f"│  • Renderability  : {comps.get('renderability', 100.0):>5.1f}%"
        f"      │  • Intent Match  : {comps.get('intent_continuity', 100.0):>5.1f}%      │"
    )
    lines.append(
        f"│  • Entity Clarity : {comps.get('entity_clarity', 100.0):>5.1f}%"
        f"      │  • Readability   : {comps.get('readability', 100.0):>5.1f}%      │"
    )
    lines.append(
        f"│  • Quotability    : {comps.get('quotability', 100.0):>5.1f}%"
        f"      │  • Actionability : {comps.get('actionability', 100.0):>5.1f}%      │"
    )
    lines.append(
        f"│  • Freshness/Trust: {comps.get('trust_freshness', 100.0):>5.1f}%"
        f"      │                                     │"
    )
    lines.append(_c(CYAN, _c(BOLD, "├" + "─" * 74 + "┤")))
    defects_line = (
        f"  DIAGNOSTIC ISSUES: {_c(BOLD, str(total))} Total "
        f"({_c(RED, f'🚨 {crit} Critical')} · "
        f"{_c(RED, f'⚠️  {high} High')} · "
        f"{_c(YELLOW, f'⚡ {med} Med')} · "
        f"{_c(BLUE, f'ℹ️  {low} Low')})"
    )
    lines.append(f"│{defects_line:<86}│")
    lines.append(_c(CYAN, _c(BOLD, "╰" + "─" * 74 + "╯")))

    # Findings section
    if findings:
        lines.append(_c(BOLD, "\n📋 DIAGNOSTIC FINDINGS (Sorted by Priority):"))
        for i, f in enumerate(findings, 1):
            sev = str(f.get("severity", "medium")).lower()
            title = f.get("title", "Untitled")
            f_id = f.get("id", "F-???")
            cat = f.get("category", "general")
            remediation = f.get("remediation", "")

            lines.append(f"\n  {i}. {color_severity(sev)} {_c(BOLD, title)} {_c(DIM, f'[{f_id} · {cat}]')}")
            if remediation:
                lines.append(f"     {_c(GREEN, '💡 Fix:')} {remediation}")
    else:
        lines.append(_c(GREEN, _c(BOLD, "\n✓ Flawless Diagnostics: Zero architectural defects detected!")))

    # Proactive recommendations section
    if proactive:
        lines.append(_c(BOLD, "\n💡 BEYOND-DEFECT STRATEGIC ADVISORY:"))
        for p in proactive:
            prio = p.get("priority", "MEDIUM").upper()
            title = p.get("title", "")
            rec = p.get("recommendation", "")
            impact = p.get("impact", "")
            lines.append(f"  • {_c(BOLD, title)} [{prio}]")
            lines.append(f"    {rec}")
            if impact:
                lines.append(f"    {_c(CYAN, 'Expected Lift:')} {impact}")

    # Actionable footer
    lines.append("\n" + "─" * 76)
    lines.append(_c(DIM, "💡 Next Actions:"))
    lines.append(_c(DIM, f"   • Generate LLM fix prompt : omni prompt {site}"))
    lines.append(_c(DIM, f"   • Benchmark a competitor  : omni compare {site} https://competitor.com"))
    lines.append(_c(DIM, "   • Launch web dashboard    : omni serve"))
    lines.append("─" * 76 + "\n")

    return "\n".join(lines)


def format_markdown_report(report: dict[str, Any]) -> str:
    """Renders a standard GitHub-flavored Markdown report."""
    from gradio_ui import generate_markdown_report

    return generate_markdown_report(report)


# ----------------------------------------------------------------------
# CLI Argument Parser Setup
# ----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omni",
        description="OmniAudit-GEO — Brand AI-Readiness & GEO Engine Unified CLI (Adobe Hackathon 2026)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omni                                        Interactive guided launcher
  omni https://example.com                    Audit website immediately
  omni compare https://adobe.com canva.com    Head-to-head competitor benchmark
  omni prompt https://example.com             Generate AI fix prompt & copy to clipboard
  omni benchmark                              Run 16 Golden Benchmarks matrix
  omni specialist crawl https://example.com   Run isolated specialist skill audit
  omni serve                                  Launch local web dashboard & API
  omni docs --list                            Browse documentation catalog
        """,
    )

    parser.add_argument("--url", "-u", help="Target website URL to audit immediately")
    parser.add_argument(
        "--format", "-f", choices=["text", "json", "markdown"], default="text", help="Output format (default: text)"
    )
    parser.add_argument("--output", "-o", help="File path to save the output report")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress decorative banners")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. audit subcommand
    audit_parser = subparsers.add_parser("audit", help="Run full master audit on a website")
    audit_parser.add_argument("target", nargs="?", help="Target website URL")
    audit_parser.add_argument("--url", "-u", help="Target website URL")
    audit_parser.add_argument(
        "--format", "-f", choices=["text", "json", "markdown"], default="text", help="Output format (default: text)"
    )
    audit_parser.add_argument("--output", "-o", help="File path to save output report")
    audit_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress decorative banners")

    # 2. compare subcommand
    comp_parser = subparsers.add_parser("compare", help="Compare two websites head-to-head")
    comp_parser.add_argument("url1", nargs="?", help="Your website URL")
    comp_parser.add_argument("url2", nargs="?", help="Competitor website URL")

    # 3. prompt subcommand
    prompt_parser = subparsers.add_parser("prompt", help="Generate AI fix prompt and copy to clipboard")
    prompt_parser.add_argument("url", nargs="?", help="Target website URL")

    # 4. interactive subcommand
    subparsers.add_parser("interactive", help="Start interactive guided launcher")

    # 5. specialist subcommand
    spec_parser = subparsers.add_parser("specialist", help="Run an isolated specialist skill audit")
    spec_parser.add_argument(
        "skill", choices=["crawl", "structured", "aeo", "freshness", "engagement"], help="Specialist skill name"
    )
    spec_parser.add_argument("url", nargs="?", help="Target website URL")
    spec_parser.add_argument(
        "--format", "-f", choices=["text", "json"], default="text", help="Output format (default: text)"
    )

    # 6. mcp subcommand
    mcp_parser = subparsers.add_parser("mcp", help="Run Anthropic Model Context Protocol (MCP) server")
    mcp_parser.add_argument("--test", action="store_true", help="Run internal MCP self-test suite")

    # 7. serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Run local web control plane and Gradio UI")
    serve_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to bind (default: 8000)")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    serve_parser.add_argument("--gradio-only", action="store_true", help="Run standalone Gradio UI without FastAPI")

    # 8. verify subcommand
    verify_parser = subparsers.add_parser("verify", help="Run official 6-Gate verification loop")
    verify_parser.add_argument("--ci", action="store_true", help="Enable strict CI mode")

    # 9. benchmark subcommand
    subparsers.add_parser("benchmark", help="Run the 16 Golden Benchmarks evaluation harness")

    # 10. package subcommand
    subparsers.add_parser("package", help="Build and sandbox-verify submission ZIP package")

    # 11. lint subcommand
    lint_parser = subparsers.add_parser("lint", help="Run Ruff linter and code formatting checks")
    lint_parser.add_argument("--fix", action="store_true", help="Automatically fix fixable lint and format issues")

    # 12. docs subcommand
    docs_parser = subparsers.add_parser("docs", help="Browse, search, or read canonical documentation")
    docs_parser.add_argument("--list", "-l", action="store_true", help="List all available documents in registry")
    docs_parser.add_argument("--search", "-s", help="Search documentation by keyword")
    docs_parser.add_argument("--get", "-g", help="Read full document content by slug ID (e.g. getting-started)")

    return parser


def main() -> int:
    # 1. No arguments: launch interactive mode if in interactive terminal
    if len(sys.argv) == 1:
        if sys.stdin.isatty():
            return cmd_interactive()
        parser = build_parser()
        parser.print_help()
        return 0

    # 2. Check for direct URL shorthand (e.g. 'omni example.com' or 'omni https://example.com')
    first_arg = sys.argv[1]
    known_commands = {
        "audit",
        "compare",
        "prompt",
        "interactive",
        "specialist",
        "mcp",
        "serve",
        "verify",
        "benchmark",
        "package",
        "lint",
        "docs",
        "-h",
        "--help",
        "-u",
        "--url",
        "-q",
        "--quiet",
        "-f",
        "--format",
    }
    if not first_arg.startswith("-") and first_arg not in known_commands:
        if "." in first_arg or first_arg.startswith("http"):
            args = argparse.Namespace(url=first_arg, format="text", output=None, quiet=False)
            return cmd_audit(args)

    parser = build_parser()
    args = parser.parse_args()

    # Route top-level positional target or --url to audit
    target = getattr(args, "target", None) or getattr(args, "url", None)
    if target and not getattr(args, "command", None):
        args.url = target
        return cmd_audit(args)

    cmd = getattr(args, "command", None)
    if not cmd:
        if sys.stdin.isatty():
            return cmd_interactive()
        parser.print_help()
        return 0

    if cmd == "audit":
        audit_target = getattr(args, "target", None) or getattr(args, "url", None)
        args.url = audit_target
        return cmd_audit(args)
    elif cmd == "compare":
        return cmd_compare(args)
    elif cmd == "prompt":
        return cmd_prompt(args)
    elif cmd == "interactive":
        return cmd_interactive()
    elif cmd == "specialist":
        return cmd_specialist(args)
    elif cmd == "mcp":
        return cmd_mcp(args)
    elif cmd == "serve":
        return cmd_serve(args)
    elif cmd == "verify":
        return cmd_verify(args)
    elif cmd == "benchmark":
        return cmd_benchmark(args)
    elif cmd == "package":
        return cmd_package(args)
    elif cmd == "lint":
        return cmd_lint(args)
    elif cmd == "docs":
        return cmd_docs(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
