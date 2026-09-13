#!/usr/bin/env python3
"""
OmniAudit-GEO — Unified Command-Line Interface (CLI).
Adobe University Hackathon 2026 (Round 3 CRP)

Single command-line entrypoint unifying:
  1. Full Site Audit (Master Orchestrator)
  2. Specialist Skill Audits (Crawl/Render, Structured Entity, AEO Quotability, Freshness/Trust, Engagement)
  3. Model Context Protocol (MCP) Server (stdio & self-test)
  4. Web Control Plane & Gradio UI Server
  5. 6-Gate Verification Loop & Golden Benchmarks
  6. Marketplace Package Builder & Sandbox Validator

Architectural Invariant:
  Shares 100% of canonical AST & scoring logic from skills/ and scripts/.
  Zero logic duplication. Single source of truth.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
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

# ANSI Color Utilities
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


BOLD = "1"
CYAN = "36"
GREEN = "32"
YELLOW = "33"
RED = "31"
MAGENTA = "35"
BLUE = "34"
DIM = "2"


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
        return _c(RED, _c(BOLD, f"[{s}]"))
    elif s == "HIGH":
        return _c(RED, f"[{s}]")
    elif s == "MEDIUM":
        return _c(YELLOW, f"[{s}]")
    else:
        return _c(BLUE, f"[{s}]")


# ----------------------------------------------------------------------
# CLI Commands
# ----------------------------------------------------------------------


def cmd_audit(args: argparse.Namespace) -> int:
    """Run full master audit on a target URL."""
    from audit_runner import run_full_audit
    from safe_fetch import normalize_url

    raw_url = args.url
    if not raw_url:
        print(_c(RED, "Error: --url is required for audit command"), file=sys.stderr)
        return 1

    try:
        target_url = normalize_url(raw_url)
    except Exception as e:
        print(_c(RED, f"Error: Invalid target URL '{raw_url}': {e}"), file=sys.stderr)
        return 1

    if not args.quiet and args.format != "json":
        print(_c(CYAN, _c(BOLD, "╔═══════════════════════════════════════════════════════════════════════╗")))
        print(_c(CYAN, _c(BOLD, "║            OmniAudit-GEO — Brand AI-Readiness Audit Engine            ║")))
        print(_c(CYAN, _c(BOLD, "╚═══════════════════════════════════════════════════════════════════════╝")))
        print(f"Target URL : {_c(BOLD, target_url)}")
        print("Executing canonical pipeline across all 6 specialist skills...\n")

    try:
        report = run_full_audit(target_url)
    except Exception as e:
        print(_c(RED, f"Audit Execution Failed: {e}"), file=sys.stderr)
        return 1

    # Formatting output
    if args.format == "json":
        output_str = json.dumps(report, indent=2)
    elif args.format == "markdown":
        output_str = format_markdown_report(report)
    else:
        output_str = format_text_report(report)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_str, encoding="utf-8")
        print(_c(GREEN, f"\n✓ Audit report successfully written to: {out_path}"))
    else:
        print(output_str)

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
    raw_url = args.url
    if not raw_url:
        print(_c(RED, "Error: --url is required"), file=sys.stderr)
        return 1

    try:
        target_url = normalize_url(raw_url)
    except Exception as e:
        print(_c(RED, f"Error: Invalid target URL '{raw_url}': {e}"), file=sys.stderr)
        return 1

    # Fetch page
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

    if args.format == "json":
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
            if isinstance(sa, dict) and sa.get("implementation_code"):
                print(f"   {_c(DIM, 'Remediation snippet:')}")
                for line in sa["implementation_code"].splitlines()[:3]:
                    print(f"     {line}")
            print()

    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    """Run Anthropic Model Context Protocol (MCP) server or self-tests."""
    from mcp_server import main as mcp_main

    if args.test:
        sys.argv = ["mcp_server.py", "--test"]
    else:
        sys.argv = ["mcp_server.py"]
    mcp_main()
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """Start local web server (FastAPI + Gradio 6 UI)."""
    port = args.port
    host = args.host

    if args.gradio_only:
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

        print(_c(GREEN, f"🚀 Launching OmniAudit-GEO Web Control Plane & MCP Server on http://{host}:{port}"))
        print(_c(CYAN, f"   • Web UI       : http://{host}:{port}/"))
        print(_c(CYAN, f"   • REST API     : http://{host}:{port}/api/audit?url=https://example.com"))
        print(_c(CYAN, f"   • MCP Endpoint : http://{host}:{port}/api/mcp"))
        print(_c(CYAN, f"   • OpenAPI Docs : http://{host}:{port}/api/docs"))
        uvicorn.run("main:app", host=host, port=port, reload=args.reload)
        return 0
    except ImportError:
        print(_c(RED, "Error: uvicorn is not installed. Run: pip install uvicorn fastapi"), file=sys.stderr)
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Run official 6-Gate verification loop."""
    from verify import main as verify_main

    if args.ci:
        sys.argv = ["verify.py", "--ci"]
    else:
        sys.argv = ["verify.py"]
    verify_main()
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Run the 16 Golden Benchmarks evaluation harness."""
    from eval_benchmarks import run_evals

    return int(run_evals(return_dict=False))


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
            print(f"  • {_c(GREEN, doc['id']):<30} [{doc['category']}] {doc['title']}")
        return 0

    if getattr(args, "search", None):
        results = search_docs(args.search)
        print(_c(BOLD, _c(CYAN, f"\n🔍 Search results for '{args.search}': ({len(results)} found)")))
        for doc in results:
            print(f"  • {_c(GREEN, doc['id']):<30} {doc['title']}")
        return 0

    if getattr(args, "get", None):
        doc = get_doc_by_id(args.get)
        if not doc or not doc.get("exists"):
            print(_c(RED, f"Error: Document '{args.get}' not found."))
            return 1
        print(doc["content"])
        return 0

    print("Use --list, --search <query>, or --get <doc_id>")
    return 0


# ----------------------------------------------------------------------
# Text and Markdown Formatters
# ----------------------------------------------------------------------


def format_text_report(report: dict[str, Any]) -> str:
    lines = []
    site = report.get("site", "unknown")
    audited_at = report.get("audited_at", "N/A")
    metrics = report.get("metrics", {})
    summary = report.get("summary", {})
    findings = report.get("findings", [])
    proactive = report.get("proactive_recommendations", [])

    acpi = metrics.get("acpi_score", 0.0)
    crs = metrics.get("crs_score", 0.0)

    lines.append(_c(BOLD, f"\nSite: {site} | Audited At: {audited_at}"))
    lines.append("─" * 70)
    lines.append(f"• AI Citation Probability Index (ACPI) : {color_score(acpi)}")
    lines.append(f"• Cognitive Retention Score     (CRS)  : {color_score(crs)}")
    lines.append(
        f"• Total Findings Detected              : {summary.get('total_findings', len(findings))} ("
        f"{_c(RED, str(summary.get('critical', 0)) + ' critical')}, "
        f"{_c(RED, str(summary.get('high', 0)) + ' high')}, "
        f"{_c(YELLOW, str(summary.get('medium', 0)) + ' medium')}, "
        f"{_c(BLUE, str(summary.get('low', 0)) + ' low')})"
    )
    lines.append("─" * 70)

    if findings:
        lines.append(_c(BOLD, "\n[ FINDINGS & REMEDIATION ]"))
        for i, f in enumerate(findings, 1):
            sev = f.get("severity", "medium")
            title = f.get("title", "Untitled")
            f_id = f.get("id", "F-XXX")
            category = f.get("category", "")
            lines.append(f"\n{i}. {color_severity(sev)} {_c(BOLD, title)} [{f_id}]")
            lines.append(f"   Category: {category}")
            sa = f.get("suggested_action", {})
            if isinstance(sa, dict) and sa.get("summary"):
                lines.append(f"   Suggested Fix : {sa['summary']}")
            if isinstance(sa, dict) and sa.get("implementation_code"):
                lines.append("   Code snippet  :")
                for c_line in sa["implementation_code"].splitlines()[:3]:
                    lines.append(f"     {c_line}")
    else:
        lines.append(_c(GREEN, "\n✓ No discoverability or retention barriers detected!"))

    if proactive:
        lines.append(_c(BOLD, "\n[ PROACTIVE GEO RECOMMENDATIONS ]"))
        for p in proactive:
            lines.append(
                f"• {_c(BOLD, p.get('area', '').upper())} ({p.get('priority', '').upper()}): {p.get('recommendation', '')}"
            )
            if p.get("expected_impact"):
                lines.append(f"  {_c(DIM, 'Impact:')} {p['expected_impact']}")

    lines.append("")
    return "\n".join(lines)


def format_markdown_report(report: dict[str, Any]) -> str:
    site = report.get("site", "unknown")
    audited_at = report.get("audited_at", "N/A")
    metrics = report.get("metrics", {})
    summary = report.get("summary", {})
    findings = report.get("findings", [])
    proactive = report.get("proactive_recommendations", [])

    md = [
        f"# OmniAudit-GEO Audit Report for `{site}`",
        f"\n**Audited At:** `{audited_at}`\n",
        "## Composite Scores",
        f"- **AI Citation Probability Index (ACPI):** `{metrics.get('acpi_score', 0.0):.1f} / 100`",
        f"- **Cognitive Retention Score (CRS):** `{metrics.get('crs_score', 0.0):.1f} / 100`",
        "\n## Findings Summary",
        f"- **Total Findings:** {summary.get('total_findings', len(findings))}",
        f"- **Critical:** {summary.get('critical', 0)} | **High:** {summary.get('high', 0)} | **Medium:** {summary.get('medium', 0)} | **Low:** {summary.get('low', 0)}",
        "\n## Detailed Findings",
    ]

    for f in findings:
        sev = f.get("severity", "medium").upper()
        title = f.get("title", "Untitled")
        f_id = f.get("id", "F-XXX")
        sa = f.get("suggested_action", {})
        summary_text = sa.get("summary", "") if isinstance(sa, dict) else ""
        code = sa.get("implementation_code", "") if isinstance(sa, dict) else ""

        md.append(f"\n### `[{sev}]` {title} ({f_id})")
        md.append(f"**Category:** `{f.get('category', 'general')}`")
        if summary_text:
            md.append(f"\n**Action:** {summary_text}")
        if code:
            md.append(f"\n```html\n{code}\n```")

    if proactive:
        md.append("\n## Proactive GEO Opportunities")
        for p in proactive:
            md.append(
                f"- **{p.get('area', '').title()}** (`{p.get('priority', '').upper()}`): {p.get('recommendation', '')}"
            )
            if p.get("expected_impact"):
                md.append(f"  - *Expected Impact:* {p['expected_impact']}")

    return "\n".join(md)


# ----------------------------------------------------------------------
# CLI Argument Parser Setup
# ----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omniaudit",
        description="OmniAudit-GEO — Brand AI-Readiness & GEO Engine Unified CLI (Round 3 CRP)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cli.py --url https://example.com
  python3 cli.py audit --url https://example.com --format markdown --output report.md
  python3 cli.py specialist crawl --url https://example.com
  python3 cli.py specialist structured --url https://example.com
  python3 cli.py specialist aeo --url https://example.com
  python3 cli.py mcp --test
  python3 cli.py mcp
  python3 cli.py serve --port 8000
  python3 cli.py verify --ci
  python3 cli.py benchmark
  python3 cli.py package
        """,
    )

    # Allow top-level `--url` for immediate full audit shorthand
    parser.add_argument("--url", help="Target website URL to audit immediately")
    parser.add_argument(
        "--format", choices=["text", "json", "markdown"], default="text", help="Output format (default: text)"
    )
    parser.add_argument("--output", "-o", help="File path to save the output report")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress decorative banners")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. audit subcommand
    audit_parser = subparsers.add_parser("audit", help="Run full master audit across all 6 skills")
    audit_parser.add_argument("--url", "-u", required=True, help="Target website URL to audit")
    audit_parser.add_argument(
        "--format", "-f", choices=["text", "json", "markdown"], default="text", help="Output format (default: text)"
    )
    audit_parser.add_argument("--output", "-o", help="File path to save output report")
    audit_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress decorative banners")

    # 2. specialist subcommand
    spec_parser = subparsers.add_parser("specialist", help="Run an isolated specialist skill audit")
    spec_parser.add_argument(
        "skill", choices=["crawl", "structured", "aeo", "freshness", "engagement"], help="Specialist skill name"
    )
    spec_parser.add_argument("--url", "-u", required=True, help="Target website URL to audit")
    spec_parser.add_argument(
        "--format", "-f", choices=["text", "json"], default="text", help="Output format (default: text)"
    )

    # 3. mcp subcommand
    mcp_parser = subparsers.add_parser("mcp", help="Run Anthropic Model Context Protocol (MCP) server")
    mcp_parser.add_argument("--test", action="store_true", help="Run internal MCP self-test suite")

    # 4. serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Run local web control plane and Gradio UI")
    serve_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to bind (default: 8000)")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    serve_parser.add_argument("--gradio-only", action="store_true", help="Run standalone Gradio UI without FastAPI")

    # 5. verify subcommand
    verify_parser = subparsers.add_parser("verify", help="Run 6-Gate verification loop")
    verify_parser.add_argument("--ci", action="store_true", help="Enable strict CI mode")

    # 6. benchmark subcommand
    subparsers.add_parser("benchmark", help="Run the 16 Golden Benchmarks evaluation harness")

    # 7. package subcommand
    subparsers.add_parser("package", help="Build and sandbox-verify submission ZIP package")

    # 8. lint subcommand
    lint_parser = subparsers.add_parser("lint", help="Run Ruff linter and code formatting checks")
    lint_parser.add_argument("--fix", action="store_true", help="Automatically fix fixable lint and format issues")

    # 9. docs subcommand
    docs_parser = subparsers.add_parser("docs", help="Browse, search, or read canonical documentation")
    docs_parser.add_argument("--list", "-l", action="store_true", help="List all available documents in registry")
    docs_parser.add_argument("--search", "-s", help="Search documentation by keyword")
    docs_parser.add_argument("--get", "-g", help="Read full document content by slug ID (e.g. getting-started)")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # If invoked with top-level --url, route to cmd_audit
    if args.url and not args.command:
        return cmd_audit(args)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "audit":
        return cmd_audit(args)
    elif args.command == "specialist":
        return cmd_specialist(args)
    elif args.command == "mcp":
        return cmd_mcp(args)
    elif args.command == "serve":
        return cmd_serve(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "benchmark":
        return cmd_benchmark(args)
    elif args.command == "package":
        return cmd_package(args)
    elif args.command == "lint":
        return cmd_lint(args)
    elif args.command == "docs":
        return cmd_docs(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
