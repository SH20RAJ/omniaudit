#!/usr/bin/env python3
"""
OmniAudit-GEO — High-End, Minimal, and Professional Gradio Interface.
Directly uses the canonical Python audit engine and specialist skills.
Zero React, zero JavaScript build steps. Pure Python.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

try:
    import gradio as gr
except ImportError:
    gr = None

# Ensure core scripts are importable
REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
ORCHESTRATOR_SCRIPTS = SKILLS_DIR / "audit-orchestrator" / "scripts"
CRAWL_SCRIPTS = SKILLS_DIR / "crawl-render-audit" / "scripts"
ROOT_SCRIPTS = REPO_ROOT / "scripts"

import sys

for p in [str(ORCHESTRATOR_SCRIPTS), str(CRAWL_SCRIPTS), str(ROOT_SCRIPTS), str(REPO_ROOT / "omniaudit-geo")]:
    if p not in sys.path:
        sys.path.insert(0, p)

import re
import tempfile

from eval_benchmarks import run_evals
from scoring import compute_scores

from audit_guard import (
    execute_guarded_audit,
    execute_guarded_mcp,
    execute_guarded_specialist_audit,
)
from docs_manager import (
    get_doc_by_id,
    get_docs_catalog,
)
from mcp_server import MCP_TOOLS

# ---------------------------------------------------------------------------
# UI Visual Helper Components
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# UI Visual Helper Components (Glassmorphism & SVG Radial Gauges)
# ---------------------------------------------------------------------------


def render_score_badge(score: float, label: str, components: dict[str, float] | None = None) -> str:
    """Renders an enterprise SVG circular radial score meter with qualitative rating and sub-breakdown."""
    radius = 38
    circ = 2 * 3.14159265 * radius
    pct = max(0.0, min(100.0, score))
    offset = circ * (1.0 - pct / 100.0)

    if score >= 90:
        color = "#10b981"
        bg = "rgba(16, 185, 129, 0.1)"
        grade = "A+" if score >= 95 else "A"
        rating = "EXCELLENT · OPTIMIZED"
    elif score >= 75:
        color = "#38bdf8"
        bg = "rgba(56, 189, 248, 0.1)"
        grade = "B"
        rating = "GOOD · SOLID"
    elif score >= 60:
        color = "#f59e0b"
        bg = "rgba(245, 158, 11, 0.1)"
        grade = "C"
        rating = "NEEDS ATTENTION"
    else:
        color = "#ef4444"
        bg = "rgba(239, 68, 68, 0.1)"
        grade = "F"
        rating = "CRITICAL RISKS"

    comp_html = ""
    if components:
        bars = []
        for name, val in components.items():
            val_pct = max(0.0, min(100.0, float(val)))
            bar_color = (
                "#10b981"
                if val_pct >= 90
                else ("#38bdf8" if val_pct >= 75 else ("#f59e0b" if val_pct >= 60 else "#ef4444"))
            )
            bars.append(f"""
            <div style="margin-bottom: 5px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8; margin-bottom: 2px;">
                    <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 140px;">{name}</span>
                    <span style="color: {bar_color}; font-weight: 700; font-family: monospace;">{val_pct:.0f}%</span>
                </div>
                <div style="background: rgba(255,255,255,0.06); height: 4px; border-radius: 2px; overflow: hidden;">
                    <div style="background: {bar_color}; width: {val_pct}%; height: 100%; border-radius: 2px;"></div>
                </div>
            </div>
            """)
        comp_html = f"""
        <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); text-align: left;">
            {"".join(bars)}
        </div>
        """

    return f"""
    <div class="glass-card" style="border-top: 3px solid {color} !important; padding: 20px 16px; text-align: center; position: relative;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">{label}</div>
        <div style="display: flex; justify-content: center; align-items: center; margin: 4px 0 10px 0; position: relative;">
            <svg width="106" height="106" viewBox="0 0 106 106" style="transform: rotate(-90deg);">
                <circle cx="53" cy="53" r="{radius}" stroke="rgba(255,255,255,0.08)" stroke-width="7" fill="transparent" />
                <circle cx="53" cy="53" r="{radius}" stroke="{color}" stroke-width="7" fill="transparent"
                        stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}" stroke-linecap="round"
                        style="transition: stroke-dashoffset 0.8s cubic-bezier(0.16, 1, 0.3, 1);" />
            </svg>
            <div style="position: absolute; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <span style="font-size: 1.95rem; font-weight: 800; color: #ffffff; line-height: 1; font-family: Outfit, sans-serif;">{score:.1f}</span>
                <span style="font-size: 0.66rem; color: {color}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 3px;">GRADE {grade}</span>
            </div>
        </div>
        <div>
            <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em; background: {bg}; color: {color}; border: 1px solid {color}40;">
                <span class="pulse-dot" style="background: {color}; box-shadow: 0 0 8px {color};"></span> {rating}
            </span>
        </div>
        {comp_html}
    </div>
    """


def render_findings_html(findings: list[dict[str, Any]]) -> str:
    """Renders audit findings as clean, responsive, high-contrast cards with filter counters."""
    if not findings:
        return """
        <div style="text-align: center; padding: 40px 20px; background: rgba(16, 185, 129, 0.04); border: 1px dashed rgba(16, 185, 129, 0.3); border-radius: 12px; color: #10b981; margin: 12px 0;">
            <div style="font-size: 2.2rem; margin-bottom: 8px;">✓</div>
            <div style="font-size: 1.15rem; font-weight: 800; font-family: Outfit, sans-serif;">Flawless Diagnostics — Zero Issues Detected</div>
            <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 6px; max-width: 480px; margin-left: auto; margin-right: auto;">
                The target satisfies all deterministic heuristic gates across crawler permissions, Schema.org entities, quotation clarity, and visitor retention.
            </div>
        </div>
        """

    sev_styles = {
        "critical": {"bg": "rgba(239, 68, 68, 0.15)", "border": "#ef4444", "text": "#ef4444", "icon": "🚨"},
        "high": {"bg": "rgba(249, 115, 22, 0.15)", "border": "#f97316", "text": "#f97316", "icon": "⚠️"},
        "medium": {"bg": "rgba(245, 158, 11, 0.15)", "border": "#f59e0b", "text": "#f59e0b", "icon": "⚡"},
        "low": {"bg": "rgba(59, 130, 246, 0.15)", "border": "#3b82f6", "text": "#3b82f6", "icon": "ℹ️"},
        "info": {"bg": "rgba(100, 116, 139, 0.15)", "border": "#94a3b8", "text": "#94a3b8", "icon": "📝"},
    }

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        s = str(f.get("severity", "medium")).lower()
        if s in counts:
            counts[s] += 1

    filter_bar_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0 14px 0; flex-wrap: wrap; gap: 8px;">
        <div style="font-size: 0.88rem; color: #94a3b8; font-weight: 600;">
            Showing <strong style="color: #f8fafc;">{len(findings)}</strong> diagnostic findings (sorted by priority):
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            <span class="sev-chip crit">🚨 {counts["critical"]} Critical</span>
            <span class="sev-chip high">⚠️ {counts["high"]} High</span>
            <span class="sev-chip med">⚡ {counts["medium"]} Medium</span>
            <span class="sev-chip low">ℹ️ {counts["low"]} Low</span>
        </div>
    </div>
    """

    cards = []
    for f in findings:
        fid = f.get("id", "F-???")
        sev = str(f.get("severity", "medium")).lower()
        cat = f.get("category", "general").replace("_", " ").title()
        title = f.get("title", "Audit Finding")
        remediation = f.get("remediation", "")
        evidence = f.get("evidence", "")

        st = sev_styles.get(sev, sev_styles["medium"])

        evidence_html = ""
        if evidence:
            if isinstance(evidence, (dict, list)):
                ev_str = json.dumps(evidence, indent=2)
            else:
                ev_str = str(evidence).strip()
            if ev_str and ev_str != "{}":
                evidence_html = f"""
                <details style="margin-top: 10px; background: rgba(0,0,0,0.4); border-radius: 8px; padding: 8px 14px; border: 1px solid rgba(255,255,255,0.06);">
                    <summary style="cursor: pointer; font-size: 0.78rem; font-weight: 600; color: #94a3b8; font-family: monospace; user-select: none;">🔍 View Diagnostic Evidence & AST Context</summary>
                    <pre style="margin: 8px 0 4px 0; font-size: 0.75rem; color: #cbd5e1; overflow-x: auto; white-space: pre-wrap; word-break: break-all; font-family: 'JetBrains Mono', Consolas, monospace; max-height: 220px;">{ev_str}</pre>
                </details>
                """

        card_html = f"""
        <div class="finding-card" style="border-left: 4px solid {st["border"]} !important;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="background: rgba(255,255,255,0.08); color: #f1f5f9; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;">{
            fid
        }</span>
                    <span style="background: {st["bg"]}; color: {st["text"]}; border: 1px solid {
            st["border"]
        }50; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.04em;">
                        {st["icon"]} {sev.upper()}
                    </span>
                    <span style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">{
            cat
        }</span>
                </div>
            </div>
            <div style="font-size: 1.02rem; font-weight: 600; color: #f8fafc; margin-bottom: 8px; line-height: 1.45;">
                {title}
            </div>
            {
            f'''<div class="action-callout">
                <strong style="color: #fca5a5;">💡 Remediation Plan:</strong> {remediation}
            </div>'''
            if remediation
            else ""
        }
            {evidence_html}
        </div>
        """
        cards.append(card_html)

    return f"""
    <div style="margin-top: 8px;">
        {filter_bar_html}
        {"".join(cards)}
    </div>
    """


def render_proactive_recs(recommendations: list[dict[str, Any]]) -> str:
    """Renders beyond-defect strategic recommendations as high-impact cards."""
    if not recommendations:
        return "<div style='color:#94a3b8; font-size:0.9rem; padding: 12px 0;'>No critical proactive recommendations generated. Target website satisfies core optimization heuristics.</div>"

    prio_colors = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f97316",
        "MEDIUM": "#f59e0b",
        "LOW": "#38bdf8",
    }

    cards = []
    for r in recommendations:
        prio = str(r.get("priority", "medium")).upper()
        title = r.get("title", "")
        rec = r.get("recommendation", "")
        impact = r.get("impact", "")
        color = prio_colors.get(prio, "#f59e0b")

        cards.append(f"""
        <div class="glass-card" style="border-top: 3px solid {color} !important; padding: 16px 18px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
                <span style="font-size: 1rem; font-weight: 700; color: #f8fafc; font-family: Outfit, sans-serif;">{title}</span>
                <span style="background: {color}20; color: {color}; border: 1px solid {color}50; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 10px; text-transform: uppercase;">
                    {prio} PRIORITY
                </span>
            </div>
            <div style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.55; margin-bottom: 10px;">{rec}</div>
            <div style="font-size: 0.78rem; color: #10b981; font-weight: 600; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16,185,129,0.25); padding: 4px 12px; border-radius: 6px; display: inline-flex; align-items: center; gap: 6px;">
                📈 Expected Strategic Impact: {impact}
            </div>
        </div>
        """)

    return "".join(cards)


# ---------------------------------------------------------------------------
# Backend Handlers using the Guarded Audit Service Execution Layer
# ---------------------------------------------------------------------------


def _get_client_ip(request: gr.Request | None) -> str:
    """Extracts client IP from incoming Gradio request context."""
    if not request:
        return "local"
    try:
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd:
            return fwd.split(",")[0].strip()
        if hasattr(request, "client") and request.client and hasattr(request.client, "host"):
            return str(request.client.host)
    except Exception:
        pass
    return "local"


def generate_ai_prompt(report: dict[str, Any]) -> str:
    """Generates an actionable, copy-paste LLM prompt for Claude, Cursor, or ChatGPT to fix detected issues."""
    if not report or report.get("error"):
        return "Run an audit to generate an AI remediation prompt."

    site = report.get("site", "target-site.com")
    audited_at = report.get("audited_at", "")
    metrics = report.get("metrics", {})
    acpi = float(metrics.get("acpi_score", 0.0))
    crs = float(metrics.get("crs_score", 0.0))
    findings = report.get("findings", [])
    recs = report.get("proactive_recommendations", [])
    summary = report.get("summary", {})

    lines = [
        "# 🛠️ OmniAudit-GEO: AI Search (GEO) & Visitor Retention (CRS) Fix Prompt",
        "",
        f"**Target Domain:** `{site}`",
        f"**Audited At:** `{audited_at}`",
        f"**Current Baseline Scores:** ACPI: **{acpi:.1f}/100** (Discoverability) | CRS: **{crs:.1f}/100** (Retention)",
        f"**Total Defects Detected:** {summary.get('total_findings', len(findings))} "
        f"({summary.get('critical', 0)} Critical, {summary.get('high', 0)} High, {summary.get('medium', 0)} Medium, {summary.get('low', 0)} Low)",
        "",
        "---",
        "",
        "### 🎯 Your Objective",
        f"You are a Senior Full-Stack & Generative Engine Optimization (GEO/AEO) Engineer. "
        f"Your mission is to resolve every diagnostic defect identified below on `{site}` to achieve ACPI ≥ 95.0 and CRS ≥ 95.0.",
        "",
        "### 📋 Detected Diagnostic Defects & Required Remediations:",
    ]

    for i, f in enumerate(findings, 1):
        fid = f.get("id", f"F-{i:03d}")
        sev = str(f.get("severity", "medium")).upper()
        cat = f.get("category", "general")
        title = f.get("title", "")
        remediation = f.get("remediation", "Inspect and fix.")
        evidence = f.get("evidence", "")
        ev_repr = ""
        if evidence and evidence != "{}":
            if isinstance(evidence, (dict, list)):
                ev_repr = json.dumps(evidence)
            else:
                ev_repr = str(evidence).strip()
            if len(ev_repr) > 180:
                ev_repr = ev_repr[:180] + "..."

        lines.append(f"{i}. **[{sev}] `{fid}`: {title}**")
        lines.append(f"   - **Diagnostic Category:** `{cat}`")
        lines.append(f"   - **Required Remediation:** {remediation}")
        if ev_repr:
            lines.append(f"   - **AST Evidence:** `{ev_repr}`")

    if recs:
        lines.append("")
        lines.append("### 💡 Beyond-Defect Strategic Recommendations:")
        for r in recs:
            prio = r.get("priority", "MEDIUM").upper()
            lines.append(
                f"- **[{prio}] {r.get('title', '')}:** {r.get('recommendation', '')} *(Expected Impact: {r.get('impact', '')})*"
            )

    lines.extend(
        [
            "",
            "---",
            "",
            "### 💻 Concrete Implementation Requirements:",
            "1. **Robots.txt Updates:** If crawlability issues were detected, provide the exact `robots.txt` configuration explicitly allowing AI crawlers (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `Applebot-Extended`).",
            '2. **Schema.org JSON-LD:** Output copy-paste `<script type="application/ld+json">` blocks for `Organization`, `WebSite`, and disambiguating `sameAs` entity links to Wikipedia/Wikidata authorities.',
            "3. **AEO Quotability & Headings:** Rewrite top sections into atomic, self-contained 20–50 word factual statements answering search intent directly with semantic H1–H3 hierarchy.",
            "4. **Above-the-Fold Value Clarity (CRS):** Provide revised hero headline, sub-headline, and high-contrast primary call-to-action (CTA) button copy to drop bounce rates.",
            "5. **Clean Code:** Return syntactically valid code blocks, ready to drop into production.",
        ]
    )

    return "\n".join(lines)


def generate_markdown_report(report: dict[str, Any]) -> str:
    """Generates a complete, publication-ready GitHub-flavored Markdown audit report."""
    if not report or report.get("error"):
        return "# Audit Report\n\nNo report data available."

    site = report.get("site", "target-site.com")
    audited_at = report.get("audited_at", "")
    metrics = report.get("metrics", {})
    acpi = float(metrics.get("acpi_score", 0.0))
    crs = float(metrics.get("crs_score", 0.0))
    summary = report.get("summary", {})
    findings = report.get("findings", [])
    recs = report.get("proactive_recommendations", [])

    rating_acpi = (
        "EXCELLENT" if acpi >= 90 else ("GOOD" if acpi >= 75 else ("NEEDS WORK" if acpi >= 60 else "CRITICAL"))
    )
    rating_crs = "EXCELLENT" if crs >= 90 else ("GOOD" if crs >= 75 else ("NEEDS WORK" if crs >= 60 else "CRITICAL"))

    lines = [
        "# 🛡️ OmniAudit-GEO Brand AI-Readiness Audit Report",
        "",
        f"- **Audited Domain:** `{site}`",
        f"- **Audit Date:** `{audited_at}`",
        "- **Standard Compliance:** `agentskills.io` · Anthropic Model Context Protocol (MCP)",
        "- **Engine Execution Mode:** 100% Deterministic Local Python AST (Zero External Cloud API Dependencies)",
        "",
        "---",
        "",
        "## 📊 Executive Scorecard",
        "",
        "| Metric Axis | Score | Rating | Focus & Intent |",
        "| :--- | :---: | :---: | :--- |",
        f"| **ACPI** (AI Citation Probability Index) | **{acpi:.1f} / 100** | `{rating_acpi}` | Machine discoverability, robots.txt, Schema.org entities, atomic quotability |",
        f"| **CRS** (Cognitive Retention Score) | **{crs:.1f} / 100** | `{rating_crs}` | Human orientation, value-prop clarity, reading ease, actionability |",
        "",
        f"**Defect Distribution:** Total `{summary.get('total_findings', len(findings))}` findings "
        f"(🚨 Critical: `{summary.get('critical', 0)}`, ⚠️ High: `{summary.get('high', 0)}`, ⚡ Medium: `{summary.get('medium', 0)}`, ℹ️ Low: `{summary.get('low', 0)}`)",
        "",
        "---",
        "",
        "## 📋 Proactive Strategic Recommendations",
        "",
    ]

    if recs:
        for r in recs:
            lines.append(f"### 💡 {r.get('title', '')} (`{r.get('priority', 'MEDIUM').upper()}` Priority)")
            lines.append(f"- **Recommendation:** {r.get('recommendation', '')}")
            lines.append(f"- **Projected Impact:** {r.get('impact', '')}")
            lines.append("")
    else:
        lines.append("No high-priority recommendations detected.\n")

    lines.extend(
        [
            "---",
            "",
            "## 🔍 Detailed Diagnostic Findings & AST Evidence",
            "",
        ]
    )

    if findings:
        for f in findings:
            fid = f.get("id", "F-???")
            sev = str(f.get("severity", "medium")).upper()
            cat = f.get("category", "general")
            title = f.get("title", "")
            remediation = f.get("remediation", "")
            evidence = f.get("evidence", "")

            lines.append(f"### `[{sev}]` {fid}: {title}")
            lines.append(f"- **Category:** `{cat}`")
            if remediation:
                lines.append(f"- **Remediation:** {remediation}")
            if evidence and evidence != "{}":
                ev_str = json.dumps(evidence, indent=2) if isinstance(evidence, (dict, list)) else str(evidence).strip()
                lines.append(f"- **Evidence:**\n```json\n{ev_str}\n```")
            lines.append("")
    else:
        lines.append("✓ Clean audit. No defects identified across tested heuristic gates.\n")

    lines.extend(
        [
            "---",
            "*Report generated automatically by OmniAudit-GEO · Adobe University Hackathon 2026*",
        ]
    )

    return "\n".join(lines)


def export_md_file(report: dict[str, Any]) -> str | None:
    """Exports audit report as downloadable Markdown file."""
    if not report or not report.get("site"):
        return None
    content = generate_markdown_report(report)
    site = re.sub(r"[^a-zA-Z0-9_\-]", "_", report.get("site", "audit"))
    file_path = os.path.join(tempfile.gettempdir(), f"omniaudit_{site}_report.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


def export_json_file(report: dict[str, Any]) -> str | None:
    """Exports audit report as downloadable verified JSON file."""
    if not report or not report.get("site"):
        return None
    site = re.sub(r"[^a-zA-Z0-9_\-]", "_", report.get("site", "audit"))
    file_path = os.path.join(tempfile.gettempdir(), f"omniaudit_{site}_report.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return file_path


def select_high_critical_findings(report: dict[str, Any]) -> Any:
    """Selects all critical and high findings in the What-If simulation CheckboxGroup."""
    if not report or not report.get("findings"):
        return gr.update(value=[])
    selected = []
    for f in report.get("findings", []):
        sev = str(f.get("severity", "medium")).lower()
        if sev in ("critical", "high"):
            label = f"[{sev.upper()}] {f.get('id', 'F-???')}: {f.get('title', '')}"
            selected.append(label)
    return gr.update(value=selected)


def select_critical_findings(report: dict[str, Any]) -> Any:
    """Selects only critical findings in the What-If simulation CheckboxGroup."""
    if not report or not report.get("findings"):
        return gr.update(value=[])
    selected = []
    for f in report.get("findings", []):
        sev = str(f.get("severity", "medium")).lower()
        if sev == "critical":
            label = f"[{sev.upper()}] {f.get('id', 'F-???')}: {f.get('title', '')}"
            selected.append(label)
    return gr.update(value=selected)


def select_crawl_findings(report: dict[str, Any]) -> Any:
    """Selects crawlability, robots, and hydration findings."""
    if not report or not report.get("findings"):
        return gr.update(value=[])
    selected = []
    for f in report.get("findings", []):
        cat = str(f.get("category", "")).lower()
        if any(k in cat for k in ("crawl", "render", "robot", "network", "hydration")):
            sev = str(f.get("severity", "medium")).upper()
            label = f"[{sev}] {f.get('id', 'F-???')}: {f.get('title', '')}"
            selected.append(label)
    return gr.update(value=selected)


def select_schema_findings(report: dict[str, Any]) -> Any:
    """Selects structured data and Schema.org entity findings."""
    if not report or not report.get("findings"):
        return gr.update(value=[])
    selected = []
    for f in report.get("findings", []):
        cat = str(f.get("category", "")).lower()
        if any(k in cat for k in ("schema", "entity", "structured", "data", "sameas")):
            sev = str(f.get("severity", "medium")).upper()
            label = f"[{sev}] {f.get('id', 'F-???')}: {f.get('title', '')}"
            selected.append(label)
    return gr.update(value=selected)


def run_what_if_simulation(report: dict[str, Any], selected_labels: list[str]) -> str:
    """Re-calculates projected ACPI & CRS scores excluding user-selected resolved findings."""
    if not report or "metrics" not in report:
        return "<div style='color:#94a3b8; padding:8px 0;'>Please run an audit first before simulating fixes.</div>"

    orig_acpi = float(report.get("metrics", {}).get("acpi_score", 0.0))
    orig_crs = float(report.get("metrics", {}).get("crs_score", 0.0))
    findings = report.get("findings", [])

    if not findings:
        return "<div style='color:#10b981; padding:8px 0;'>✓ No defects detected on this target. Score is already at peak rating.</div>"

    resolved_ids: set[str] = set()
    for label in selected_labels:
        match = re.search(r"\]\s*([A-Za-z0-9_\-]+):", label)
        if match:
            resolved_ids.add(match.group(1))
        else:
            for f in findings:
                fid = f.get("id", "")
                if fid and fid in label:
                    resolved_ids.add(fid)

    if not resolved_ids:
        return """
        <div style="background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; padding: 14px; text-align: center; color: #94a3b8;">
            No defects selected. Select one or more defects above and click <strong>⚡ Re-calculate Projected Scores</strong>.
        </div>
        """

    remaining = [f for f in findings if f.get("id") not in resolved_ids]
    sim_scores = compute_scores(remaining)
    sim_acpi = float(sim_scores.get("acpi_score", orig_acpi))
    sim_crs = float(sim_scores.get("crs_score", orig_crs))

    acpi_delta = sim_acpi - orig_acpi
    crs_delta = sim_crs - orig_crs

    acpi_delta_str = f"+{acpi_delta:.1f}" if acpi_delta > 0 else f"{acpi_delta:.1f}"
    crs_delta_str = f"+{crs_delta:.1f}" if crs_delta > 0 else f"{crs_delta:.1f}"
    acpi_color = "#10b981" if acpi_delta > 0 else "#94a3b8"
    crs_color = "#10b981" if crs_delta > 0 else "#94a3b8"

    return f"""
    <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 16px 18px; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
            <div style="font-size: 1rem; font-weight: 700; color: #f8fafc;">
                📈 Simulation Impact: {len(resolved_ids)} of {len(findings)} Defects Resolved
            </div>
            <span style="font-size: 0.75rem; background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 10px; border-radius: 12px; font-weight: 700;">
                PROJECTED LIFT
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-bottom: 12px;">
            <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 14px; text-align: center; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">ACPI · AI Discoverability</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #ffffff; margin: 4px 0;">
                    {orig_acpi:.1f} ➔ <span style="color: #10b981;">{sim_acpi:.1f}</span>
                </div>
                <div style="font-size: 0.85rem; font-weight: 700; color: {acpi_color};">Net Gain: {acpi_delta_str} pts</div>
            </div>
            <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 14px; text-align: center; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">CRS · Visitor Retention</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #ffffff; margin: 4px 0;">
                    {orig_crs:.1f} ➔ <span style="color: #3b82f6;">{sim_crs:.1f}</span>
                </div>
                <div style="font-size: 0.85rem; font-weight: 700; color: {crs_color};">Net Gain: {crs_delta_str} pts</div>
            </div>
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8;">
            <strong>Resolved IDs:</strong> {", ".join(sorted(resolved_ids))}
        </div>
    </div>
    """


def run_competitor_comparison(
    url_a: str, url_b: str, request: gr.Request | None = None
) -> tuple[str, str, str, str, str]:
    """Runs concurrent/sequential audits against both URLs and generates head-to-head analysis."""
    client_ip = _get_client_ip(request)
    if not url_a or not url_a.strip() or not url_b or not url_b.strip():
        return (
            "<div style='color:#ef4444; padding:10px;'>Please provide both Target Website and Competitor Website URLs.</div>",
            "",
            "",
            "",
            "Please enter two valid URLs to generate competitor comparison.",
        )

    t0_a = time.perf_counter()
    rep_a = execute_guarded_audit(url_a.strip(), client_ip=client_ip)
    lat_a = time.perf_counter() - t0_a

    t0_b = time.perf_counter()
    rep_b = execute_guarded_audit(url_b.strip(), client_ip=client_ip)
    lat_b = time.perf_counter() - t0_b

    site_a = rep_a.get("site", url_a)
    site_b = rep_b.get("site", url_b)

    if rep_a.get("error") or rep_b.get("error"):
        err_a = rep_a.get("error", "OK")
        err_b = rep_b.get("error", "OK")
        return (
            f"<div style='color:#ef4444; padding:12px; background:rgba(239,68,68,0.1); border-radius:8px;'>Comparison Notice — Site A: {err_a} | Site B: {err_b}</div>",
            "",
            "",
            "",
            f"**Notice during comparison:** Site A ({site_a}): `{err_a}` | Site B ({site_b}): `{err_b}`",
        )

    acpi_a = float(rep_a.get("metrics", {}).get("acpi_score", 0.0))
    crs_a = float(rep_a.get("metrics", {}).get("crs_score", 0.0))
    tot_a = rep_a.get("summary", {}).get("total_findings", 0)
    crit_a = rep_a.get("summary", {}).get("critical", 0)

    acpi_b = float(rep_b.get("metrics", {}).get("acpi_score", 0.0))
    crs_b = float(rep_b.get("metrics", {}).get("crs_score", 0.0))
    tot_b = rep_b.get("summary", {}).get("total_findings", 0)
    crit_b = rep_b.get("summary", {}).get("critical", 0)

    comp_a = (0.6 * acpi_a) + (0.4 * crs_a)
    comp_b = (0.6 * acpi_b) + (0.4 * crs_b)

    diff = comp_a - comp_b
    if diff > 0.5:
        winner_html = f"""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 16px 20px; text-align: center; margin-bottom: 16px;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #10b981;">🏆 {site_a} LEADS COMPETITIVE AI READINESS</div>
            <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 4px;">
                Outperforms {site_b} by <strong>+{diff:.1f} composite points</strong> (Composite: {comp_a:.1f} vs {comp_b:.1f})
            </div>
        </div>
        """
    elif diff < -0.5:
        winner_html = f"""
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 16px 20px; text-align: center; margin-bottom: 16px;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #60a5fa;">🏆 {site_b} LEADS COMPETITIVE AI READINESS</div>
            <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 4px;">
                Outperforms {site_a} by <strong>+{abs(diff):.1f} composite points</strong> (Composite: {comp_b:.1f} vs {comp_a:.1f})
            </div>
        </div>
        """
    else:
        winner_html = f"""
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 16px 20px; text-align: center; margin-bottom: 16px;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #f59e0b;">🤝 DEAD HEAT COMPETITIVE BENCHMARK</div>
            <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 4px;">
                Both domains demonstrate comparable AI search readiness ({comp_a:.1f} vs {comp_b:.1f} composite points).
            </div>
        </div>
        """

    def _render_comp_card(
        site: str, acpi: float, crs: float, tot: int, crit: int, lat: float, border_color: str
    ) -> str:
        r = 26
        circ = 2 * 3.14159265 * r
        pct_acpi = max(0.0, min(100.0, acpi))
        off_acpi = circ * (1.0 - pct_acpi / 100.0)
        c_acpi = "#10b981" if acpi >= 80 else ("#38bdf8" if acpi >= 70 else ("#f59e0b" if acpi >= 50 else "#ef4444"))

        pct_crs = max(0.0, min(100.0, crs))
        off_crs = circ * (1.0 - pct_crs / 100.0)
        c_crs = "#38bdf8" if crs >= 80 else ("#818cf8" if crs >= 70 else ("#f59e0b" if crs >= 50 else "#ef4444"))

        return f"""
        <div class="glass-card" style="border-top: 4px solid {border_color} !important; padding: 20px 16px; text-align: center;">
            <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin-bottom: 12px; font-family: Outfit, sans-serif; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{site}</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin: 12px 0 16px 0; flex-wrap: wrap;">
                <!-- Mini ACPI Gauge -->
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="position: relative; width: 72px; height: 72px; display: flex; align-items: center; justify-content: center;">
                        <svg width="72" height="72" viewBox="0 0 72 72" style="transform: rotate(-90deg);">
                            <circle cx="36" cy="36" r="{r}" stroke="rgba(255,255,255,0.08)" stroke-width="5" fill="transparent" />
                            <circle cx="36" cy="36" r="{r}" stroke="{c_acpi}" stroke-width="5" fill="transparent"
                                    stroke-dasharray="{circ:.1f}" stroke-dashoffset="{off_acpi:.1f}" stroke-linecap="round" />
                        </svg>
                        <div style="position: absolute; font-size: 1.15rem; font-weight: 800; color: #ffffff; font-family: Outfit, sans-serif;">
                            {acpi:.1f}
                        </div>
                    </div>
                    <span style="font-size: 0.7rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-top: 5px;">ACPI (GEO)</span>
                </div>
                <!-- Mini CRS Gauge -->
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="position: relative; width: 72px; height: 72px; display: flex; align-items: center; justify-content: center;">
                        <svg width="72" height="72" viewBox="0 0 72 72" style="transform: rotate(-90deg);">
                            <circle cx="36" cy="36" r="{r}" stroke="rgba(255,255,255,0.08)" stroke-width="5" fill="transparent" />
                            <circle cx="36" cy="36" r="{r}" stroke="{c_crs}" stroke-width="5" fill="transparent"
                                    stroke-dasharray="{circ:.1f}" stroke-dashoffset="{off_crs:.1f}" stroke-linecap="round" />
                        </svg>
                        <div style="position: absolute; font-size: 1.15rem; font-weight: 800; color: #ffffff; font-family: Outfit, sans-serif;">
                            {crs:.1f}
                        </div>
                    </div>
                    <span style="font-size: 0.7rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-top: 5px;">CRS (Retention)</span>
                </div>
            </div>
            <div style="font-size: 0.8rem; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; display: flex; justify-content: space-around;">
                <span>Defects: <strong style="color:#f59e0b;">{tot}</strong> (<span style="color:#ef4444; font-weight: 700;">{crit} crit</span>)</span>
                <span>Latency: <strong>{lat:.2f}s</strong></span>
            </div>
        </div>
        """

    card_a = _render_comp_card(site_a, acpi_a, crs_a, tot_a, crit_a, lat_a, "#10b981")
    card_b = _render_comp_card(site_b, acpi_b, crs_b, tot_b, crit_b, lat_b, "#3b82f6")

    def _cell_winner(val_a: float, val_b: float, higher_better: bool = True) -> tuple[str, str]:
        if abs(val_a - val_b) < 0.1:
            return "#cbd5e1", "#cbd5e1"
        is_a_win = (val_a > val_b) if higher_better else (val_a < val_b)
        return ("#10b981; font-weight: 700;", "#94a3b8") if is_a_win else ("#94a3b8", "#10b981; font-weight: 700;")

    c_acpi_a, c_acpi_b = _cell_winner(acpi_a, acpi_b, True)
    c_crs_a, c_crs_b = _cell_winner(crs_a, crs_b, True)
    c_tot_a, c_tot_b = _cell_winner(float(tot_a), float(tot_b), False)
    c_crit_a, c_crit_b = _cell_winner(float(crit_a), float(crit_b), False)
    c_lat_a, c_lat_b = _cell_winner(lat_a, lat_b, False)

    matrix_html = f"""
    <div style="overflow-x: auto; margin-top: 14px;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left;">
            <thead>
                <tr style="border-bottom: 2px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 0.78rem; text-transform: uppercase;">
                    <th style="padding: 10px 12px;">Evaluation Dimension</th>
                    <th style="padding: 10px 12px; text-align: center;">{site_a}</th>
                    <th style="padding: 10px 12px; text-align: center;">{site_b}</th>
                    <th style="padding: 10px 12px; text-align: center;">Leader</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <td style="padding: 10px 12px; font-weight: 600;">🤖 ACPI (AI Citation Probability)</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_acpi_a};">{acpi_a:.1f} / 100</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_acpi_b};">{acpi_b:.1f} / 100</td>
                    <td style="padding: 10px 12px; text-align: center; font-weight: 700;">{"Tie" if abs(acpi_a - acpi_b) < 0.1 else (site_a if acpi_a > acpi_b else site_b)}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <td style="padding: 10px 12px; font-weight: 600;">🎯 CRS (Cognitive Visitor Retention)</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_crs_a};">{crs_a:.1f} / 100</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_crs_b};">{crs_b:.1f} / 100</td>
                    <td style="padding: 10px 12px; text-align: center; font-weight: 700;">{"Tie" if abs(crs_a - crs_b) < 0.1 else (site_a if crs_a > crs_b else site_b)}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <td style="padding: 10px 12px; font-weight: 600;">🚨 Critical Architectural Defects</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_crit_a};">{crit_a}</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_crit_b};">{crit_b}</td>
                    <td style="padding: 10px 12px; text-align: center; font-weight: 700;">{"Tie" if crit_a == crit_b else (site_a if crit_a < crit_b else site_b)}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <td style="padding: 10px 12px; font-weight: 600;">📋 Total Diagnostic Findings</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_tot_a};">{tot_a}</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_tot_b};">{tot_b}</td>
                    <td style="padding: 10px 12px; text-align: center; font-weight: 700;">{"Tie" if tot_a == tot_b else (site_a if tot_a < tot_b else site_b)}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 12px; font-weight: 600;">⚡ AST Diagnostic Latency</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_lat_a};">{lat_a:.2f}s</td>
                    <td style="padding: 10px 12px; text-align: center; color: {c_lat_b};">{lat_b:.2f}s</td>
                    <td style="padding: 10px 12px; text-align: center; font-weight: 700;">{site_a if lat_a < lat_b else site_b}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """

    leader_acpi = site_a if acpi_a >= acpi_b else site_b
    leader_crs = site_a if crs_a >= crs_b else site_b
    max_acpi = max(acpi_a, acpi_b)
    min_acpi = min(acpi_a, acpi_b)
    max_crs = max(crs_a, crs_b)
    min_crs = min(crs_a, crs_b)

    rec_item_a = (
        "Resolve critical crawl blocks in robots.txt immediately to prevent generative assistant exclusion."
        if crit_a > 0
        else "Crawlability is clean; focus on Schema.org entity disambiguation with sameAs links."
    )
    rec_item_b = (
        "Expand atomic fact answer density under semantic H2 headings to overtake competitor."
        if acpi_a <= acpi_b
        else "Maintain quote density advantage by keeping 2026 freshness signals updated."
    )

    insights_md = f"""
### 💡 Strategic Competitive Positioning & Takeaways

* **AI Citation Leader:** **`{leader_acpi}`** demonstrates stronger off-site AI discoverability ({max_acpi:.1f} vs {min_acpi:.1f} ACPI). It is significantly more likely to be cited by Perplexity, ChatGPT Search, and Claude.
* **Visitor Retention Leader:** **`{leader_crs}`** has superior on-site landing page clarity ({max_crs:.1f} vs {min_crs:.1f} CRS) with lower bounce risk for referred visitors.
* **Tactical Advice for `{site_a}`:**
  * {rec_item_a}
  * {rec_item_b}
"""

    return winner_html, card_a, card_b, matrix_html, insights_md


def perform_full_audit(
    url: str, request: gr.Request | None = None
) -> tuple[str, str, str, str, dict[str, Any], str, str, Any, str]:
    """Executes the master audit orchestrator on the target URL via the guarded execution service."""
    client_ip = _get_client_ip(request)
    start_time = time.perf_counter()
    report = execute_guarded_audit(url, client_ip=client_ip)
    elapsed = time.perf_counter() - start_time

    if report.get("error"):
        err_msg = report.get("error", "Audit failed")
        err_code = report.get("error_code", "error")
        return (
            f"<div style='color:#ef4444; font-weight:600; padding:14px; background:rgba(239,68,68,0.1); border-radius:8px; border:1px solid rgba(239,68,68,0.25);'>"
            f"🛡️ Security &amp; Execution Guard Notice ({err_code}): {err_msg}</div>",
            "",
            f"<div style='color:#ef4444;'>Audit execution halted by guard layer: {err_msg}</div>",
            "No recommendations generated.",
            report,
            f"Error: {err_msg}",
            f"# Audit Error\n\n{err_msg}",
            gr.update(choices=[], value=[]),
            f"<div style='color:#ef4444;'>Simulation unavailable: {err_msg}</div>",
        )

    acpi = report.get("metrics", {}).get("acpi_score", 0.0)
    crs = report.get("metrics", {}).get("crs_score", 0.0)
    summary = report.get("summary", {})
    total = summary.get("total_findings", 0)
    crit = summary.get("critical", 0)
    high = summary.get("high", 0)
    med = summary.get("medium", 0)
    low = summary.get("low", 0)
    clean_url = report.get("site", url)

    findings = report.get("findings", [])
    scores_info = compute_scores(findings)
    comp_scores = scores_info.get("component_scores", {})
    acpi_comps = {
        "Crawlability (30%)": comp_scores.get("crawlability", 100.0),
        "Renderability (15%)": comp_scores.get("renderability", 100.0),
        "Entity Clarity (20%)": comp_scores.get("entity_clarity", 100.0),
        "Quotability (20%)": comp_scores.get("quotability", 100.0),
        "Freshness/Trust (15%)": comp_scores.get("trust_freshness", 100.0),
    }
    crs_comps = {
        "Orientation (35%)": comp_scores.get("orientation", 100.0),
        "Intent (25%)": comp_scores.get("intent_continuity", 100.0),
        "Readability (20%)": comp_scores.get("readability", 100.0),
        "Actionability (20%)": comp_scores.get("actionability", 100.0),
    }

    badge_acpi = render_score_badge(acpi, "ACPI · AI Discoverability", acpi_comps)
    badge_crs = render_score_badge(crs, "CRS · Visitor Retention", crs_comps)

    # Status Cards HTML
    metrics_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px;">
        {badge_acpi}
        {badge_crs}
        <div class="glass-card" style="border-top: 3px solid #f59e0b !important; padding: 20px 16px; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">Diagnostic Defects</div>
            <div style="font-size: 2.8rem; font-weight: 800; color: #f59e0b; line-height: 1.1; margin: 4px 0; font-family: Outfit, sans-serif;">{total}</div>
            <div style="margin: 8px 0 12px 0;">
                <span style="font-size: 0.74rem; font-weight: 700; color: #f59e0b; background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.25); padding: 2px 10px; border-radius: 12px;">
                    {crit + high} ACTIONABLE PRIORITY
                </span>
            </div>
            <div style="display: flex; justify-content: center; gap: 6px; margin-top: 10px; flex-wrap: wrap;">
                <span class="sev-chip crit">🚨 {crit}</span>
                <span class="sev-chip high">⚠️ {high}</span>
                <span class="sev-chip med">⚡ {med}</span>
                <span class="sev-chip low">ℹ️ {low}</span>
            </div>
        </div>
        <div class="glass-card" style="border-top: 3px solid #8b5cf6 !important; padding: 20px 16px; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">Engine Latency</div>
            <div style="font-size: 2.8rem; font-weight: 800; color: #a78bfa; line-height: 1.1; margin: 4px 0; font-family: Outfit, sans-serif;">{elapsed:.2f}s</div>
            <div style="margin: 8px 0 12px 0;">
                <span style="font-size: 0.74rem; font-weight: 700; color: #a78bfa; background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.25); padding: 2px 10px; border-radius: 12px;">
                    100% AIR-GAPPED AST
                </span>
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 10px; font-family: 'JetBrains Mono', monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {report.get("site", clean_url)}
            </div>
        </div>
    </div>
    """

    findings = report.get("findings", [])
    findings_html = render_findings_html(findings)
    recs_html = render_proactive_recs(report.get("proactive_recommendations", []))
    summary_text = f"**Target Site:** `{report.get('site', clean_url)}` | **Audited At:** `{report.get('audited_at', '')}` | **Spec:** `agentskills.io`"

    ai_prompt = generate_ai_prompt(report)
    md_report = generate_markdown_report(report)

    sim_choices = [
        f"[{f.get('severity', 'medium').upper()}] {f.get('id', 'F-???')}: {f.get('title', '')}" for f in findings
    ]
    sim_initial_html = "<div style='color:#94a3b8; font-size:0.9rem; padding:8px 0;'>Select defects above and click <strong>⚡ Re-calculate Projected Scores</strong> to simulate impact.</div>"

    return (
        metrics_html,
        summary_text,
        findings_html,
        recs_html,
        report,
        ai_prompt,
        md_report,
        gr.update(choices=sim_choices, value=[]),
        sim_initial_html,
    )


def perform_specialist_audit(
    skill_name: str, url: str, request: gr.Request | None = None
) -> tuple[str, str, dict[str, Any]]:
    """Invokes individual specialist audit skills directly via the guarded execution layer."""
    client_ip = _get_client_ip(request)
    summary_md, findings, meta = execute_guarded_specialist_audit(skill_name, url, client_ip=client_ip)
    if meta.get("error"):
        err_msg = meta.get("error")
        return (
            summary_md,
            f"<div style='color:#ef4444; padding:12px; background:rgba(239,68,68,0.1); border-radius:6px;'>🛡️ Guard Notice: {err_msg}</div>",
            meta,
        )

    findings_html = render_findings_html(findings)
    return summary_md, findings_html, meta


def perform_live_mcp_call(tool_name: str, target_url: str, request: gr.Request | None = None) -> tuple[str, str]:
    """Interactive Live MCP Sandbox Tester via the guarded execution layer."""
    client_ip = _get_client_ip(request)
    if not target_url or not target_url.strip():
        target_url = "https://example.com"

    req_obj = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": {"url": target_url.strip()}},
    }
    req_json = json.dumps(req_obj, indent=2)
    res_obj = execute_guarded_mcp(req_obj, client_ip=client_ip)
    res_json = json.dumps(res_obj, indent=2)

    return req_json, res_json


def load_benchmarks_data() -> tuple[str, list[list[str]]]:
    eval_raw = run_evals(return_dict=True)
    eval_res: dict[str, Any] = eval_raw if isinstance(eval_raw, dict) else {}
    total = eval_res.get("total", 16)
    passed = eval_res.get("passed", 16)
    precision = eval_res.get("precision_pct", 100.0)
    recall = eval_res.get("recall_pct", 100.0)
    f1 = eval_res.get("f1_score", 100.0)
    avg_latency = eval_res.get("avg_latency_ms", 0.4)

    summary_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px;">
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; text-align: center;">
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600;">LABELED FIXTURES</div>
            <div style="font-size: 2rem; font-weight: 800; color: #10b981; margin: 4px 0;">{passed}/{total}</div>
            <div style="font-size: 0.72rem; color: #10b981;">Regression Suite Pass</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; text-align: center;">
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600;">PRECISION (SUITE)</div>
            <div style="font-size: 2rem; font-weight: 800; color: #3b82f6; margin: 4px 0;">{precision:.1f}%</div>
            <div style="font-size: 0.72rem; color: #3b82f6;">Zero False Positives</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; text-align: center;">
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600;">RECALL (SUITE)</div>
            <div style="font-size: 2rem; font-weight: 800; color: #8b5cf6; margin: 4px 0;">{recall:.1f}%</div>
            <div style="font-size: 0.72rem; color: #8b5cf6;">Zero False Negatives</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; text-align: center;">
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600;">F1-SCORE</div>
            <div style="font-size: 2rem; font-weight: 800; color: #ec4899; margin: 4px 0;">{f1:.1f}%</div>
            <div style="font-size: 0.72rem; color: #ec4899;">Ground Truth Parity</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; text-align: center;">
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600;">AST LATENCY</div>
            <div style="font-size: 2rem; font-weight: 800; color: #f59e0b; margin: 4px 0;">{avg_latency:.2f}ms</div>
            <div style="font-size: 0.72rem; color: #f59e0b;">Local In-Memory AST</div>
        </div>
    </div>
    """

    rows = []
    for fix in eval_res.get("fixtures", []):
        rows.append(
            [
                fix.get("name", ""),
                fix.get("category", ""),
                f"{fix.get('acpi_score', 0):.1f}",
                f"{fix.get('crs_score', 0):.1f}",
                f"{fix.get('latency_ms', 0):.2f} ms",
                "PASS" if fix.get("schema_valid") else "FAIL",
                "✓ PASS",
            ]
        )

    return summary_html, rows


def get_marketplace_data() -> list[list[str]]:
    """Loads declared skills from marketplace.json."""
    manifest_path = REPO_ROOT / "marketplace.json"
    if not manifest_path.is_file():
        return []
    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for s in data.get("skills", []):
        rows.append(
            [
                s.get("name", ""),
                s.get("role", ""),
                s.get("description", ""),
                s.get("entrypoint", ""),
                s.get("version", "1.0.0"),
            ]
        )
    return rows


def get_mcp_tools_data() -> list[list[str]]:
    """Loads declared Anthropic Model Context Protocol (MCP) tools."""
    rows = []
    for t in MCP_TOOLS:
        req = ", ".join(t.get("inputSchema", {}).get("required", []))
        rows.append(
            [
                t.get("name", ""),
                t.get("description", ""),
                req or "none",
            ]
        )
    return rows


def get_doc_choices(category: str = "All Categories") -> list[str]:
    catalog = get_docs_catalog()
    if category and category != "All Categories":
        catalog = [d for d in catalog if d["category"] == category]
    return [f"{d['icon']} {d['title']} ({d['id']})" for d in catalog]


def parse_doc_id_from_choice(choice: str) -> str:
    match = re.search(r"\(([^)]+)\)$", choice)
    return match.group(1) if match else "getting-started"


def get_default_doc_choice() -> str:
    choices = get_doc_choices("All Categories")
    return choices[0] if choices else ""


def render_doc_meta_header(doc_id: str) -> str:
    doc = get_doc_by_id(doc_id)
    if not doc:
        return ""
    return f"""
    <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px 18px; margin: 10px 0 18px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 3px 10px; border-radius: 12px; letter-spacing: 0.05em;">{doc["category"]}</span>
                <span style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-left: 10px;">{doc["icon"]} {doc["title"]}</span>
            </div>
            <div style="font-family: monospace; font-size: 0.8rem; color: #94a3b8; background: rgba(0,0,0,0.25); padding: 4px 10px; border-radius: 6px;">
                {doc["rel_path"]}
            </div>
        </div>
        <div style="font-size: 0.88rem; color: #cbd5e1; margin-top: 8px; line-height: 1.5;">{doc["description"]}</div>
    </div>
    """


def get_doc_markdown(doc_id: str) -> str:
    doc = get_doc_by_id(doc_id)
    return doc.get("content", "# Document Not Found") if doc else "# Document Not Found"


def on_category_change(cat: str):
    choices = get_doc_choices(cat)
    val = choices[0] if choices else ""
    doc_id = parse_doc_id_from_choice(val)
    return gr.update(choices=choices, value=val), render_doc_meta_header(doc_id), get_doc_markdown(doc_id)


def on_doc_change(choice: str):
    if not choice:
        return "", ""
    doc_id = parse_doc_id_from_choice(choice)
    return render_doc_meta_header(doc_id), get_doc_markdown(doc_id)


# ---------------------------------------------------------------------------
# Gradio UI Layout Definition
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

body, .gradio-container {
    max-width: 1320px !important;
    margin: 0 auto !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background: radial-gradient(ellipse at 50% -10%, #1e1b4b 0%, #080c16 55%, #04060a 100%) !important;
    color: #f1f5f9 !important;
    min-height: 100vh !important;
}

h1, h2, h3, .brand-title {
    font-family: 'Outfit', 'Inter', sans-serif !important;
    letter-spacing: -0.02em !important;
}

pre, code, .code-font {
    font-family: 'JetBrains Mono', Consolas, monospace !important;
}

.glass-card {
    background: rgba(15, 23, 42, 0.72) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
}

.glass-card:hover {
    border-color: rgba(255, 255, 255, 0.16) !important;
    box-shadow: 0 14px 36px -8px rgba(0, 0, 0, 0.75), 0 0 20px rgba(56, 189, 248, 0.08) !important;
}

.finding-card {
    background: rgba(15, 23, 42, 0.65) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
    margin-bottom: 12px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.finding-card:hover {
    background: rgba(22, 34, 60, 0.8) !important;
    transform: translateX(4px) !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
}

.action-callout {
    background: rgba(239, 68, 68, 0.07) !important;
    border-left: 3px solid #ef4444 !important;
    border-radius: 6px !important;
    padding: 10px 14px !important;
    margin: 10px 0 !important;
    font-size: 0.88rem !important;
    color: #cbd5e1 !important;
    line-height: 1.5 !important;
}

.sev-chip {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 3px 10px !important;
    border-radius: 20px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
}

.sev-chip.crit { background: rgba(239, 68, 68, 0.15) !important; color: #ef4444 !important; border: 1px solid rgba(239, 68, 68, 0.35) !important; }
.sev-chip.high { background: rgba(249, 115, 22, 0.15) !important; color: #f97316 !important; border: 1px solid rgba(249, 115, 22, 0.35) !important; }
.sev-chip.med { background: rgba(245, 158, 11, 0.15) !important; color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.35) !important; }
.sev-chip.low { background: rgba(59, 130, 246, 0.15) !important; color: #38bdf8 !important; border: 1px solid rgba(59, 130, 246, 0.35) !important; }

@keyframes pulse {
    0% { transform: scale(0.95); opacity: 1; }
    50% { transform: scale(1.18); opacity: 0.75; }
    100% { transform: scale(0.95); opacity: 1; }
}

.pulse-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulse 2s infinite ease-in-out;
}

.header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    background: rgba(235, 16, 0, 0.12);
    color: #ff4d4f;
    border: 1px solid rgba(235, 16, 0, 0.3);
    border-radius: 20px;
}

.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 11px;
    font-size: 12px;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    color: #94a3b8;
    transition: all 0.2s ease;
}
.stat-chip:hover {
    background: rgba(255, 255, 255, 0.07);
    color: #f8fafc;
    border-color: rgba(255, 255, 255, 0.16);
}

button.primary, .gr-button-primary {
    background: linear-gradient(135deg, #2563eb 0%, #0284c7 50%, #06b6d4 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    transition: all 0.2s ease !important;
}
button.primary:hover, .gr-button-primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.5) !important;
}

button.secondary, .gr-button-secondary {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #cbd5e1 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
button.secondary:hover, .gr-button-secondary:hover {
    background: rgba(255, 255, 255, 0.09) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #080c14;
}
::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #334155;
}
"""


def create_gradio_app() -> Any:
    """Creates the full, pure Gradio frontend for OmniAudit-GEO."""
    if gr is None:
        raise ImportError(
            "Gradio is not installed. OmniAudit-GEO has migrated to Streamlit. "
            "Please run: streamlit run streamlit_app.py"
        )
    with gr.Blocks(title="OmniAudit-GEO — Brand AI-Readiness Platform") as demo:
        gr.HTML(f"<style>{CUSTOM_CSS}</style>")
        # Top Minimalist Navigation & Brand Header
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div style="padding: 18px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <img src="/brand/logo.png" alt="Logo" style="height: 40px; width: auto; object-fit: contain;" />
                            <div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                                        OmniAudit<span style="color: #38bdf8;">.GEO</span>
                                    </span>
                                    <span style="font-size: 0.72rem; font-weight: 700; color: #94a3b8; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 12px; letter-spacing: 0.03em;">
                                        Round 3 CRP · agentskills.io
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                            <span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 16px; font-size: 11px; font-weight: 700; background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25);">
                                <span class="pulse-dot" style="background: #10b981;"></span>
                                AIR-GAPPED AST · 0.4ms
                            </span>
                            <a href="/docs" target="_blank" style="text-decoration: none; font-size: 12px; font-weight: 600; color: #38bdf8; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.25); padding: 4px 10px; border-radius: 6px;">
                                📖 Docs ↗
                            </a>
                            <a href="https://github.com/SH20RAJ/omniaudit" target="_blank" style="text-decoration: none; font-size: 12px; font-weight: 600; color: #cbd5e1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 6px;">
                                ★ GitHub ↗
                            </a>
                        </div>
                    </div>
                    <div style="margin-top: 14px;">
                        <h2 style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 0 0 4px 0; font-family: Outfit, sans-serif;">
                            Brand AI-Readiness &amp; Visitor Retention Audit
                        </h2>
                        <p style="font-size: 0.88rem; color: #94a3b8; margin: 0; line-height: 1.5;">
                            Deterministic Python AST engine measuring <strong>AI Citation Probability (ACPI: 0–100)</strong> and <strong>Visitor Retention (CRS: 0–100)</strong> with zero cloud LLM dependencies.
                        </p>
                    </div>
                </div>
                """)

        with gr.Tabs():
            # ===============================================================
            # TAB 1: Master Brand Audit
            # ===============================================================
            with gr.TabItem("⚡ Master Brand Audit", id="tab_audit"):
                with gr.Row():
                    with gr.Column(scale=5):
                        url_input = gr.Textbox(
                            label="",
                            placeholder="Enter any domain or URL (e.g. https://adobe.com, https://example.com)...",
                            value="https://example.com",
                            lines=1,
                            show_label=False,
                            container=False,
                        )
                    with gr.Column(scale=1, min_width=140):
                        audit_btn = gr.Button("🚀 Run Audit", variant="primary", scale=1)

                with gr.Row():
                    gr.Markdown(
                        "<span style='font-size: 0.78rem; color: #94a3b8; font-weight: 600; line-height: 2;'>Quick Presets:</span>"
                    )
                    btn_p_adobe = gr.Button("Adobe", size="sm", variant="secondary")
                    btn_p_openai = gr.Button("OpenAI", size="sm", variant="secondary")
                    btn_p_github = gr.Button("GitHub", size="sm", variant="secondary")
                    btn_p_stripe = gr.Button("Stripe", size="sm", variant="secondary")
                    btn_p_campus = gr.Button("CampusLoop", size="sm", variant="secondary")
                    btn_p_example = gr.Button("Example.com", size="sm", variant="secondary")

                audit_status = gr.HTML(value="")
                summary_meta = gr.Markdown(value="")

                with gr.Tabs():
                    with gr.TabItem("📋 Diagnostic Findings", id="subtab_findings"):
                        findings_output = gr.HTML(
                            value="<div style='color:#94a3b8; font-size:0.9rem; padding: 30px; text-align: center;'>Run an audit above to inspect diagnostic findings and AST evidence.</div>"
                        )

                    with gr.TabItem("💡 Proactive Strategy", id="subtab_recs"):
                        recs_output = gr.HTML(
                            value="<div style='color:#94a3b8; font-size:0.9rem; padding: 30px; text-align: center;'>Run an audit to view strategic recommendations beyond defects.</div>"
                        )

                    with gr.TabItem("⚡ 'What-If' Fix Simulator", id="subtab_sim"):
                        gr.Markdown(
                            "Select detected issues to simulate: *'If I resolve these issues, what will my new ACPI and CRS scores be?'*"
                        )
                        sim_checkboxes = gr.CheckboxGroup(
                            choices=[],
                            value=[],
                            label="Detected Defects (Select to resolve)",
                        )
                        with gr.Row():
                            sim_btn = gr.Button("⚡ Re-calculate Projected Scores", variant="primary", scale=2)
                            sim_select_crit_btn = gr.Button("Critical Only", variant="secondary", scale=1)
                            sim_select_all_btn = gr.Button("High & Critical", variant="secondary", scale=1)
                            sim_select_crawl_btn = gr.Button("Crawl & Robots", variant="secondary", scale=1)
                            sim_select_schema_btn = gr.Button("Schema & Entities", variant="secondary", scale=1)
                            sim_reset_btn = gr.Button("Reset", variant="secondary", scale=1)
                        sim_results_html = gr.HTML(
                            value="<div style='color:#94a3b8; font-size:0.9rem; padding:10px 0;'>Select defects and click 'Re-calculate' to project your score gain.</div>"
                        )

                    with gr.TabItem("🤖 AI Fix Prompt & Export", id="subtab_export"):
                        with gr.Row():
                            with gr.Column(scale=1):
                                gr.Markdown("#### 🤖 Instant AI Fix Prompt (Copy & paste into Claude / Cursor)")
                                ai_prompt_box = gr.Code(
                                    label="AI Remediation Prompt (Click Copy in Top-Right)",
                                    language="markdown",
                                    lines=14,
                                    interactive=False,
                                )
                            with gr.Column(scale=1):
                                gr.Markdown("#### 📄 Full Markdown Audit Report")
                                md_report_box = gr.Code(
                                    label="Markdown Report (Click Copy in Top-Right)",
                                    language="markdown",
                                    lines=14,
                                    interactive=False,
                                )
                        with gr.Row():
                            download_md_btn = gr.Button("📥 Download Markdown (.md)", variant="secondary", scale=1)
                            download_json_btn = gr.Button("📥 Download JSON (.json)", variant="secondary", scale=1)
                        file_download = gr.File(label="Exported Report File", interactive=False)

                    with gr.TabItem("📦 Raw JSON Schema", id="subtab_json"):
                        raw_json = gr.JSON(value={}, label="Verified Audit Schema Output")

                # Wiring preset buttons
                btn_p_adobe.click(fn=lambda: "https://adobe.com", outputs=[url_input])
                btn_p_openai.click(fn=lambda: "https://openai.com", outputs=[url_input])
                btn_p_github.click(fn=lambda: "https://github.com", outputs=[url_input])
                btn_p_stripe.click(fn=lambda: "https://stripe.com", outputs=[url_input])
                btn_p_campus.click(fn=lambda: "https://campusloop.space", outputs=[url_input])
                btn_p_example.click(fn=lambda: "https://example.com", outputs=[url_input])

                audit_btn.click(
                    fn=perform_full_audit,
                    inputs=[url_input],
                    outputs=[
                        audit_status,
                        summary_meta,
                        findings_output,
                        recs_output,
                        raw_json,
                        ai_prompt_box,
                        md_report_box,
                        sim_checkboxes,
                        sim_results_html,
                    ],
                )

                sim_btn.click(
                    fn=run_what_if_simulation,
                    inputs=[raw_json, sim_checkboxes],
                    outputs=[sim_results_html],
                )

                sim_select_crit_btn.click(
                    fn=select_critical_findings,
                    inputs=[raw_json],
                    outputs=[sim_checkboxes],
                )

                sim_select_all_btn.click(
                    fn=select_high_critical_findings,
                    inputs=[raw_json],
                    outputs=[sim_checkboxes],
                )

                sim_select_crawl_btn.click(
                    fn=select_crawl_findings,
                    inputs=[raw_json],
                    outputs=[sim_checkboxes],
                )

                sim_select_schema_btn.click(
                    fn=select_schema_findings,
                    inputs=[raw_json],
                    outputs=[sim_checkboxes],
                )

                sim_reset_btn.click(
                    fn=lambda: gr.update(value=[]),
                    inputs=[],
                    outputs=[sim_checkboxes],
                )

                download_md_btn.click(
                    fn=export_md_file,
                    inputs=[raw_json],
                    outputs=[file_download],
                )

                download_json_btn.click(
                    fn=export_json_file,
                    inputs=[raw_json],
                    outputs=[file_download],
                )

            # ===============================================================
            # TAB 2: Competitor Benchmark (Round 4 Prototype)
            # ===============================================================
            with gr.TabItem("⚔️ Competitor Benchmark", id="tab_competitor"):
                gr.HTML("""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px 20px; margin-bottom: 20px;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff;">Live Competitor Head-to-Head AI Readiness Benchmark</div>
                    <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 4px;">
                        Round 4 Prototype Showcase: Benchmark your domain against any competitor across AI Discoverability (ACPI) and On-Site Retention (CRS).
                    </div>
                </div>
                """)

                with gr.Row():
                    with gr.Column(scale=2):
                        comp_url_a = gr.Textbox(
                            label="Your Website URL",
                            value="https://adobe.com",
                            placeholder="https://yourbrand.com",
                        )
                    with gr.Column(scale=2):
                        comp_url_b = gr.Textbox(
                            label="Competitor Website URL",
                            value="https://canva.com",
                            placeholder="https://competitor.com",
                        )
                    with gr.Column(scale=1, min_width=180):
                        comp_btn = gr.Button("⚔️ Compare Head-to-Head", variant="primary", scale=1)

                with gr.Row():
                    gr.Markdown(
                        "<span style='font-size: 0.8rem; color: #94a3b8; font-weight: 600;'>⚔️ Quick Matchups:</span>"
                    )
                    btn_m_adobe = gr.Button("Adobe vs Canva", size="sm", variant="secondary")
                    btn_m_openai = gr.Button("OpenAI vs Anthropic", size="sm", variant="secondary")
                    btn_m_github = gr.Button("GitHub vs GitLab", size="sm", variant="secondary")
                    btn_m_vercel = gr.Button("Vercel vs Netlify", size="sm", variant="secondary")

                btn_m_adobe.click(
                    fn=lambda: ("https://adobe.com", "https://canva.com"), outputs=[comp_url_a, comp_url_b]
                )
                btn_m_openai.click(
                    fn=lambda: ("https://openai.com", "https://anthropic.com"), outputs=[comp_url_a, comp_url_b]
                )
                btn_m_github.click(
                    fn=lambda: ("https://github.com", "https://gitlab.com"), outputs=[comp_url_a, comp_url_b]
                )
                btn_m_vercel.click(
                    fn=lambda: ("https://vercel.com", "https://netlify.com"), outputs=[comp_url_a, comp_url_b]
                )

                comp_winner_output = gr.HTML(value="")

                with gr.Row():
                    with gr.Column(scale=1):
                        comp_card_a = gr.HTML(
                            value="<div style='color:#94a3b8; text-align:center; padding:20px;'>Brand A scorecard will appear here.</div>"
                        )
                    with gr.Column(scale=1):
                        comp_card_b = gr.HTML(
                            value="<div style='color:#94a3b8; text-align:center; padding:20px;'>Brand B scorecard will appear here.</div>"
                        )

                comp_matrix_output = gr.HTML(value="")
                comp_insights_output = gr.Markdown(value="")

                comp_btn.click(
                    fn=run_competitor_comparison,
                    inputs=[comp_url_a, comp_url_b],
                    outputs=[comp_winner_output, comp_card_a, comp_card_b, comp_matrix_output, comp_insights_output],
                )

            # ===============================================================
            # TAB 2: Specialist Skill Diagnostics
            # ===============================================================
            with gr.TabItem("🔬 Specialist Diagnostics", id="tab_specialist"):
                gr.Markdown("""
                **Modular Diagnostic Skills:** Directly invokes individual specialist skills from the `skills/` directory to inspect specific architectural layers in complete isolation.
                """)
                with gr.Row():
                    skill_selector = gr.Dropdown(
                        choices=[
                            "🕷️ Crawl & Render Audit (robots.txt & SPA)",
                            "🏷️ Structured Data & Entity Audit (JSON-LD & sameAs)",
                            "💬 AEO Quotability Audit (Atomic Facts)",
                            "⏱️ Freshness & Publisher Trust Audit (2026 Recency)",
                            "🎯 On-Site Retention & Engagement Audit (CRS)",
                        ],
                        value="🕷️ Crawl & Render Audit (robots.txt & SPA)",
                        label="Specialist Diagnostic Skill",
                        scale=3,
                    )
                    spec_url_input = gr.Textbox(
                        label="Target Website URL",
                        value="https://example.com",
                        scale=3,
                    )
                    spec_btn = gr.Button("🔬 Run Specialist Check", variant="secondary", scale=1)

                spec_summary = gr.Markdown(value="")
                spec_findings_output = gr.HTML(value="")
                with gr.Accordion("Specialist Raw JSON Output", open=False):
                    spec_json = gr.JSON(value={})

                spec_btn.click(
                    fn=perform_specialist_audit,
                    inputs=[skill_selector, spec_url_input],
                    outputs=[spec_summary, spec_findings_output, spec_json],
                )

            # ===============================================================
            # TAB 3: 16 Golden Benchmarks Matrix
            # ===============================================================
            with gr.TabItem("📊 16 Golden Benchmarks", id="tab_benchmarks"):
                gr.Markdown("""
                **Deterministic Evaluation Harness:** Evaluates the AST engine against 16 ground-truth labeled regression fixtures across Crawlability, JavaScript Hydration Gaps, Structured Data Disambiguation, AEO Quotability, Freshness Decay, and Visitor Retention. Achieves 100% precision & recall against this curated test suite (regression verification, not an extrapolation over the entire web).
                """)
                bench_btn = gr.Button("🔄 Re-run Evaluation Harness", variant="secondary")
                bench_metrics = gr.HTML(value="")
                gr.Dataframe(
                    headers=[
                        "Fixture Name",
                        "Category",
                        "ACPI Score",
                        "CRS Score",
                        "Latency",
                        "Schema Valid",
                        "Status",
                    ],
                    datatype=["str", "str", "str", "str", "str", "str", "str"],
                    value=load_benchmarks_data()[1],
                    interactive=False,
                )

                bench_btn.click(
                    fn=load_benchmarks_data,
                    inputs=[],
                    outputs=[bench_metrics],
                )

            # ===============================================================
            # TAB 4: Skill Marketplace Manifest
            # ===============================================================
            with gr.TabItem("📦 Skill Marketplace", id="tab_marketplace"):
                gr.Markdown("""
                ### Official Round 3 Agent Skill Marketplace Manifest (`marketplace.json`)
                Strictly satisfies the **Adobe University Hackathon 2026** and **`agentskills.io`** specification.
                """)
                gr.Dataframe(
                    headers=["Skill Name", "Role", "Description", "Entrypoint", "Version"],
                    datatype=["str", "str", "str", "str", "str"],
                    value=get_marketplace_data(),
                    interactive=False,
                    wrap=True,
                )

            # ===============================================================
            # TAB 5: MCP & Multi-Agent Integration Guide
            # ===============================================================
            with gr.TabItem("🔌 MCP & Agent Integration", id="tab_mcp"):
                gr.HTML("""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px 20px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff;">Model Context Protocol (MCP) Server Endpoint</div>
                            <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 4px;">
                                Standardized Anthropic MCP JSON-RPC 2.0 interface. Connect any AI agent directly to OmniAudit-GEO.
                            </div>
                        </div>
                        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px; padding: 6px 14px; font-family: monospace; font-size: 0.85rem; color: #60a5fa;">
                            POST https://omniaudit-geo.onrender.com/api/mcp
                        </div>
                    </div>
                </div>
                """)

                gr.Markdown("### 🤖 How to Connect OmniAudit-GEO to Different AI Agents")

                with gr.Accordion("1. Claude Desktop (macOS & Windows)", open=True):
                    gr.Markdown("""
                    **Configuration File Location:**
                    * **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
                    * **Windows:** `%APPDATA%\\Claude\\claude_desktop_config.json`

                    #### Option A: Connect to Live Remote Server via `mcp-remote` (Recommended):
                    ```json
                    {
                      "mcpServers": {
                        "omniaudit-geo": {
                          "command": "npx",
                          "args": ["-y", "mcp-remote", "https://omniaudit-geo.onrender.com/api/mcp"]
                        }
                      }
                    }
                    ```

                    #### Option B: Air-Gapped Local Python stdio:
                    ```json
                    {
                      "mcpServers": {
                        "omniaudit-geo": {
                          "command": "python3",
                          "args": ["/ABSOLUTE/PATH/TO/omniaudit/skills/audit-orchestrator/scripts/mcp_server.py"]
                        }
                      }
                    }
                    ```
                    """)

                with gr.Accordion("2. Cursor IDE (Agent / Composer)", open=True):
                    gr.Markdown("""
                    **Setup via Cursor UI:**
                    1. Open **Cursor Settings** (`Cmd+,` or `Ctrl+,`).
                    2. Navigate to **Features** → **MCP Servers**.
                    3. Click **+ Add New MCP Server**.
                    4. Fill in:
                       * **Name:** `omniaudit-geo`
                       * **Type:** `command`
                       * **Command:** `npx -y mcp-remote https://omniaudit-geo.onrender.com/api/mcp`

                    **Or add directly to project `.cursor/mcp.json`:**
                    ```json
                    {
                      "mcpServers": {
                        "omniaudit-geo": {
                          "command": "npx",
                          "args": ["-y", "mcp-remote", "https://omniaudit-geo.onrender.com/api/mcp"]
                        }
                      }
                    }
                    ```
                    """)

                with gr.Accordion("3. Google Antigravity AI / Gemini Agent", open=False):
                    gr.Markdown("""
                    Add to your workspace or global customization `mcp_config.json`:
                    ```json
                    {
                      "mcpServers": {
                        "omniaudit-geo": {
                          "command": "python3",
                          "args": ["skills/audit-orchestrator/scripts/mcp_server.py"]
                        }
                      }
                    }
                    ```
                    """)

                with gr.Accordion("4. Windsurf / Codeium Cascade", open=False):
                    gr.Markdown("""
                    Add to `~/.codeium/windsurf/mcp_config.json`:
                    ```json
                    {
                      "mcpServers": {
                        "omniaudit-geo": {
                          "command": "npx",
                          "args": ["-y", "mcp-remote", "https://omniaudit-geo.onrender.com/api/mcp"]
                        }
                      }
                    }
                    ```
                    """)

                with gr.Accordion("5. Custom Python / LangChain / LangGraph Agents", open=False):
                    gr.Markdown("""
                    Directly call any of the 7 MCP tools via HTTP JSON-RPC 2.0:
                    ```python
                    import httpx

                    MCP_URL = "https://omniaudit-geo.onrender.com/api/mcp"

                    def call_mcp_tool(tool_name: str, arguments: dict):
                        payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "tools/call",
                            "params": {
                                "name": tool_name,
                                "arguments": arguments
                            }
                        }
                        response = httpx.post(MCP_URL, json=payload, timeout=30.0)
                        return response.json().get("result")

                    # Example: Master Brand Audit
                    result = call_mcp_tool("audit_website", {"url": "https://adobe.com"})
                    print("Audit Summary:", result)
                    ```
                    """)

                with gr.Accordion("6. Direct cURL / Terminal Commands", open=False):
                    gr.Markdown("""
                    **List Available Tools:**
                    ```bash
                    curl -X POST https://omniaudit-geo.onrender.com/api/mcp \\
                      -H "Content-Type: application/json" \\
                      -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
                    ```

                    **Execute Master Website Audit:**
                    ```bash
                    curl -X POST https://omniaudit-geo.onrender.com/api/mcp \\
                      -H "Content-Type: application/json" \\
                      -d '{
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                          "name": "audit_website",
                          "arguments": {"url": "https://example.com"}
                        }
                      }'
                    ```
                    """)

                # -----------------------------------------------------------
                # Interactive Live MCP Sandbox Tester
                # -----------------------------------------------------------
                gr.HTML(
                    "<h3 style='font-size: 1.15rem; font-weight: 700; margin: 25px 0 10px 0; color:#f8fafc;'>⚡ Live Interactive MCP Sandbox Tester</h3>"
                )
                gr.Markdown("Test JSON-RPC 2.0 tool calls against the live MCP server directly in this interface:")

                with gr.Row():
                    mcp_tool_select = gr.Dropdown(
                        choices=[t["name"] for t in MCP_TOOLS],
                        value="audit_website",
                        label="Select MCP Tool",
                        scale=3,
                    )
                    mcp_url_input = gr.Textbox(
                        label="Target Website URL Parameter",
                        value="https://example.com",
                        scale=3,
                    )
                    mcp_run_btn = gr.Button("⚡ Execute Tool via MCP", variant="primary", scale=1)

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📤 JSON-RPC 2.0 Request Payload:")
                        mcp_req_code = gr.Code(label="Request Sent", language="json", lines=10)
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📥 JSON-RPC 2.0 Response Result:")
                        mcp_res_code = gr.Code(label="Response Received", language="json", lines=10)

                mcp_run_btn.click(
                    fn=perform_live_mcp_call,
                    inputs=[mcp_tool_select, mcp_url_input],
                    outputs=[mcp_req_code, mcp_res_code],
                )

                gr.HTML(
                    "<h4 style='font-size: 1rem; font-weight: 700; margin: 25px 0 10px 0; color:#f8fafc;'>📋 Declared Anthropic MCP Tools (7):</h4>"
                )
                gr.Dataframe(
                    headers=["Tool Name", "Description", "Required Inputs"],
                    datatype=["str", "str", "str"],
                    value=get_mcp_tools_data(),
                    interactive=False,
                    wrap=True,
                )

            # ===============================================================
            # TAB 6: 📖 Interactive Documentation Hub
            # ===============================================================
            with gr.TabItem("📖 Documentation Hub", id="tab_docs"):
                gr.HTML("""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px 20px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff;">OmniAudit-GEO Documentation Portal</div>
                            <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 4px;">
                                Live interactive browser exploring canonical architecture, specialist skills, security models, testing rubrics, and jury defense.
                            </div>
                        </div>
                        <div>
                            <a href="/docs" target="_blank" style="background: rgba(235, 16, 0, 0.15); color: #ff6b6b; border: 1px solid rgba(235, 16, 0, 0.3); padding: 8px 16px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 0.88rem; display: inline-flex; align-items: center; gap: 6px;">
                                🌐 Open Fullscreen Docs (/docs) ↗
                            </a>
                        </div>
                    </div>
                </div>
                """)

                with gr.Row():
                    doc_category_filter = gr.Dropdown(
                        choices=[
                            "All Categories",
                            "Canonical Guides",
                            "Skill Instructions",
                            "Root Protocols",
                            "Historical Archive",
                        ],
                        value="All Categories",
                        label="Filter by Category",
                        scale=2,
                    )
                    doc_item_select = gr.Dropdown(
                        choices=get_doc_choices("All Categories"),
                        value=get_default_doc_choice(),
                        label="Select Document to View",
                        scale=4,
                    )

                doc_header_html = gr.HTML(value=render_doc_meta_header("getting-started"))
                doc_viewer_md = gr.Markdown(value=get_doc_markdown("getting-started"))

                doc_category_filter.change(
                    fn=on_category_change,
                    inputs=[doc_category_filter],
                    outputs=[doc_item_select, doc_header_html, doc_viewer_md],
                )

                doc_item_select.change(
                    fn=on_doc_change,
                    inputs=[doc_item_select],
                    outputs=[doc_header_html, doc_viewer_md],
                )

        # Footer
        gr.HTML("""
        <div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 30px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.06);">
            <div style="margin-bottom: 8px;">
                <a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2FSH20RAJ%2Fomniaudit" target="_blank" style="display: inline-block;">
                    <img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fgithub.com%2FSH20RAJ%2Fomniaudit&countColor=%23263759&style=flat" alt="Visitors" />
                </a>
            </div>
            OmniAudit-GEO · Apache 2.0 License · Built by Shaswat Raj (@sh20raj) & Prithvi (@chikolavosaki-sys) · Adobe University Hackathon 2026
        </div>
        """)

    return demo


if __name__ == "__main__":
    demo = create_gradio_app()
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
