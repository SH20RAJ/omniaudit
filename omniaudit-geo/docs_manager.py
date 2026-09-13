#!/usr/bin/env python3
"""
OmniAudit-GEO Documentation Manager.
Discovers, loads, searches, and serves documentation across:
1. Canonical Guides (docs/*.md)
2. Specialist Skill Specifications (skills/**/SKILL.md)
3. Root Protocols (README.md, AGENTS.md, CLAUDE.md, CONTRIBUTING.md, SECURITY.md, marketplace.json)
4. Historical Archive (docs/archive/*.md)

Shared by both the FastAPI control plane (/docs route) and Gradio 6 UI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

DOCS_REGISTRY: list[dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. Canonical Engineering Guides
    # -------------------------------------------------------------
    {
        "id": "beginners",
        "title": "Beginner's Guide (ELI5)",
        "icon": "📘",
        "category": "Canonical Guides",
        "rel_path": "beginners.md",
        "description": "High-clarity introductory guide to Generative Engine Optimization, ACPI & CRS scores, and how OmniAudit-GEO works.",
    },
    {
        "id": "getting-started",
        "title": "Getting Started",
        "icon": "🚀",
        "category": "Canonical Guides",
        "rel_path": "docs/getting-started.md",
        "description": "Prerequisites, instant 1-line curl install, pip editable setup, and first audit execution.",
    },
    {
        "id": "architecture",
        "title": "Master Architecture",
        "icon": "🏛️",
        "category": "Canonical Guides",
        "rel_path": "docs/architecture.md",
        "description": "System topology, AST parsing pipeline, core engine vs adapters, scoring formulas (ACPI & CRS).",
    },
    {
        "id": "marketplace",
        "title": "Marketplace & Submission",
        "icon": "📦",
        "category": "Canonical Guides",
        "rel_path": "docs/marketplace.md",
        "description": "Adobe Hackathon Round 3 submission boundary, marketplace.json manifest, and archive constraints.",
    },
    {
        "id": "skills",
        "title": "Specialist Skills Catalog",
        "icon": "🧰",
        "category": "Canonical Guides",
        "rel_path": "docs/skills.md",
        "description": "In-depth detection logic, algorithms, severity matrices, and failure behaviors for all 6 skills.",
    },
    {
        "id": "cli",
        "title": "CLI Reference",
        "icon": "💻",
        "category": "Canonical Guides",
        "rel_path": "docs/cli.md",
        "description": "Unified CLI commands, options, format flags, and Unix piping examples for omni / omniaudit.",
    },
    {
        "id": "api",
        "title": "REST API Reference",
        "icon": "🌐",
        "category": "Canonical Guides",
        "rel_path": "docs/api.md",
        "description": "FastAPI control plane: health probes, master & specialist audit endpoints, and rate limiting.",
    },
    {
        "id": "mcp",
        "title": "Model Context Protocol (MCP)",
        "icon": "🤖",
        "category": "Canonical Guides",
        "rel_path": "docs/mcp.md",
        "description": "Anthropic MCP server adapter: tool catalog, stdio & HTTP transports, and agent configs.",
    },
    {
        "id": "security",
        "title": "Security & Guardrails",
        "icon": "🛡️",
        "category": "Canonical Guides",
        "rel_path": "docs/security.md",
        "description": "SSRF defense, private RFC 1918 blocking, redirect validation, resource limits, and ReDoS immunity.",
    },
    {
        "id": "testing",
        "title": "Testing & Quality Gates",
        "icon": "🧪",
        "category": "Canonical Guides",
        "rel_path": "docs/testing.md",
        "description": "6-Gate verification loop, 167 unit and integration tests, offline execution, and CI workflows.",
    },
    {
        "id": "test-report",
        "title": "Comprehensive Test Report",
        "icon": "📋",
        "category": "Canonical Guides",
        "rel_path": "docs/test-report.md",
        "description": "Live automated test results, benchmark precision/recall, website audits, and security gate matrices.",
    },
    {
        "id": "benchmarking",
        "title": "16 Golden Benchmarks",
        "icon": "📊",
        "category": "Canonical Guides",
        "rel_path": "docs/benchmarking.md",
        "description": "16 Golden Fixtures matrix, precision/recall metrics, and local AST vs network latency.",
    },
    {
        "id": "deployment",
        "title": "Deployment & Operations",
        "icon": "☁️",
        "category": "Canonical Guides",
        "rel_path": "docs/deployment.md",
        "description": "Production Dockerfile, GHCR registry, Render webhook auto-deploy, and DigitalOcean config.",
    },
    {
        "id": "judging",
        "title": "Judge & Jury Defense",
        "icon": "⚖️",
        "category": "Canonical Guides",
        "rel_path": "docs/judging.md",
        "description": "90-second executive pitch, 15 comprehensive jury defenses, and team engineering ownership.",
    },
    {
        "id": "docs-index",
        "title": "Documentation Index",
        "icon": "🧭",
        "category": "Canonical Guides",
        "rel_path": "docs/README.md",
        "description": "Central routing table and navigation index for the entire documentation suite.",
    },
    # -------------------------------------------------------------
    # 2. Specialist Skill Specifications (SKILL.md)
    # -------------------------------------------------------------
    {
        "id": "skill-orchestrator",
        "title": "Skill: audit-orchestrator",
        "icon": "🎯",
        "category": "Skill Instructions",
        "rel_path": "skills/audit-orchestrator/SKILL.md",
        "description": "Master orchestrator instructions: entrypoint dispatching, scoring synthesis, and schema formatting.",
    },
    {
        "id": "skill-crawl",
        "title": "Skill: crawl-render-audit",
        "icon": "🕷️",
        "category": "Skill Instructions",
        "rel_path": "skills/crawl-render-audit/SKILL.md",
        "description": "Robots.txt AI bot policy analysis, response header checks, and client-side JS hydration gaps.",
    },
    {
        "id": "skill-structured",
        "title": "Skill: structured-entity-audit",
        "icon": "🏷️",
        "category": "Skill Instructions",
        "rel_path": "skills/structured-entity-audit/SKILL.md",
        "description": "Schema.org JSON-LD microdata validation and sameAs knowledge graph entity disambiguation.",
    },
    {
        "id": "skill-aeo",
        "title": "Skill: aeo-quotability-audit",
        "icon": "💬",
        "category": "Skill Instructions",
        "rel_path": "skills/aeo-quotability-audit/SKILL.md",
        "description": "Atomic fact density, interrogative Q&A heading trees, and non-text asset fact accessibility.",
    },
    {
        "id": "skill-freshness",
        "title": "Skill: freshness-corroboration-audit",
        "icon": "⏱️",
        "category": "Skill Instructions",
        "rel_path": "skills/freshness-corroboration-audit/SKILL.md",
        "description": "Publication date decay, footer copyright freshness, and publisher trust corroboration markers.",
    },
    {
        "id": "skill-engagement",
        "title": "Skill: on-site-engagement-audit",
        "icon": "🎯",
        "category": "Skill Instructions",
        "rel_path": "skills/on-site-engagement-audit/SKILL.md",
        "description": "Above-the-fold hero clarity, Flesch/ARI reading ease, and conversion-oriented CTA paths.",
    },
    # -------------------------------------------------------------
    # 3. Root Protocols & Community
    # -------------------------------------------------------------
    {
        "id": "readme",
        "title": "Project README",
        "icon": "📄",
        "category": "Root Protocols",
        "rel_path": "README.md",
        "description": "Main repository README: 90-second reader journey, badges, and quickstart commands.",
    },
    {
        "id": "agents",
        "title": "Agent Protocol (AGENTS.md)",
        "icon": "🤖",
        "category": "Root Protocols",
        "rel_path": "AGENTS.md",
        "description": "Repository-wide operating contract for autonomous AI coding agents (Antigravity, Claude, Cursor).",
    },
    {
        "id": "claude",
        "title": "Claude Code (CLAUDE.md)",
        "icon": "⚡",
        "category": "Root Protocols",
        "rel_path": "CLAUDE.md",
        "description": "Operational guidelines and primary verification commands for Claude Code.",
    },
    {
        "id": "contributing",
        "title": "Contributing Guide",
        "icon": "🤝",
        "category": "Root Protocols",
        "rel_path": "CONTRIBUTING.md",
        "description": "Guidelines for open-source contributors: development setup, invariants, and PR checklist.",
    },
    {
        "id": "security-policy",
        "title": "Security Policy",
        "icon": "🔒",
        "category": "Root Protocols",
        "rel_path": "SECURITY.md",
        "description": "Vulnerability reporting procedures and coordinated disclosure guidelines.",
    },
    {
        "id": "marketplace-manifest",
        "title": "marketplace.json",
        "icon": "📜",
        "category": "Root Protocols",
        "rel_path": "marketplace.json",
        "description": "Official agentskills.io marketplace manifest defining skills and entrypoint.",
    },
    {
        "id": "pitch",
        "title": "Jury Pitch & Defense Guide",
        "icon": "🏆",
        "category": "Root Protocols",
        "rel_path": "pitch.md",
        "description": "Executive 90-second speech, Adobe past hackathons criteria analysis, and 20+ technical jury defenses.",
    },
    # -------------------------------------------------------------
    # 4. Historical Archive
    # -------------------------------------------------------------
    {
        "id": "archive-index",
        "title": "Archive: Overview",
        "icon": "🗄️",
        "category": "Historical Archive",
        "rel_path": "docs/archive/README.md",
        "description": "Index of preserved early hackathon planning, ideation, and initial research documents.",
    },
    {
        "id": "archive-round3",
        "title": "Archive: Round 3 Deep Dive",
        "icon": "📑",
        "category": "Historical Archive",
        "rel_path": "docs/archive/01_ADOBE_HACKATHON_2026_ROUND3_DEEP_DIVE.md",
        "description": "Historical problem breakdown and initial challenge requirements analysis.",
    },
    {
        "id": "archive-winners",
        "title": "Archive: Benchmark Analysis",
        "icon": "🏆",
        "category": "Historical Archive",
        "rel_path": "docs/archive/02_PREVIOUS_WINNERS_AND_BENCHMARK_ANALYSIS.md",
        "description": "Historical research on past Adobe hackathon winners and key differentiators.",
    },
    {
        "id": "archive-ideas",
        "title": "Archive: 4 Winning Architectures",
        "icon": "💡",
        "category": "Historical Archive",
        "rel_path": "docs/archive/07_WINNING_PROJECT_IDEAS_AND_ARCHITECTURES.md",
        "description": "Early architectural trade-off analysis comparing 4 prospective designs.",
    },
]


def get_docs_catalog() -> list[dict[str, Any]]:
    """Returns metadata for all available documentation items."""
    return DOCS_REGISTRY


DOC_CONTENT_CACHE: dict[str, str] = {}


def get_doc_by_id(doc_id: str) -> dict[str, Any] | None:
    """Fetches a document by its unique ID and loads its content from disk with multi-path resolution and fallback."""
    for item in DOCS_REGISTRY:
        if item["id"] == doc_id:
            rel = item["rel_path"]

            # 1. Candidate file paths on disk
            candidate_paths = [
                REPO_ROOT / rel,
                Path.cwd() / rel,
                Path(__file__).resolve().parent.parent / rel,
                Path(__file__).resolve().parent / rel,
                Path("/app") / rel,
            ]

            for cp in candidate_paths:
                if cp.is_file():
                    try:
                        content = cp.read_text(encoding="utf-8")
                        DOC_CONTENT_CACHE[doc_id] = content
                        return {
                            **item,
                            "content": content,
                            "absolute_path": str(cp),
                            "exists": True,
                        }
                    except Exception:
                        pass

            # 2. Return from in-memory cache if available
            if doc_id in DOC_CONTENT_CACHE:
                return {
                    **item,
                    "content": DOC_CONTENT_CACHE[doc_id],
                    "absolute_path": f"cache://{rel}",
                    "exists": True,
                }

            # 3. Live fallback: Fetch raw markdown from GitHub repository
            try:
                import urllib.request

                raw_url = f"https://raw.githubusercontent.com/SH20RAJ/omniaudit/main/{rel}"
                req = urllib.request.Request(raw_url, headers={"User-Agent": "OmniAudit-GEO-DocsViewer/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        content = resp.read().decode("utf-8")
                        DOC_CONTENT_CACHE[doc_id] = content
                        return {
                            **item,
                            "content": content,
                            "absolute_path": raw_url,
                            "exists": True,
                        }
            except Exception:
                pass

            return {
                **item,
                "content": f"# Document Not Found\n\nFile does not exist at `{item['rel_path']}`.",
                "exists": False,
            }
    return None


def search_docs(query: str) -> list[dict[str, Any]]:
    """Searches documentation titles, descriptions, and file content."""
    clean_q = query.strip().lower()
    if not clean_q:
        return get_docs_catalog()

    results = []
    for item in DOCS_REGISTRY:
        score = 0
        title_lower = item["title"].lower()
        desc_lower = item["description"].lower()

        if clean_q in title_lower:
            score += 10
        if clean_q in desc_lower:
            score += 5
        if clean_q in item["id"].lower():
            score += 8

        # If not matched in metadata, search in content
        if score == 0:
            doc = get_doc_by_id(item["id"])
            if doc and clean_q in doc.get("content", "").lower():
                score += 2

        if score > 0:
            results.append({**item, "relevance": score})

    results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
    return results


def build_documentation_portal_html(initial_doc_id: str = "getting-started") -> str:
    """
    Renders an enterprise, standalone, client-side searchable documentation website.
    Inspired by VitePress, Docusaurus, and GitHub Pages with high-contrast Slate / Adobe tokens.
    """
    # Pre-embed all documents into JSON so client navigation is instant and 100% offline-capable
    docs_payload = []
    for item in DOCS_REGISTRY:
        doc = get_doc_by_id(item["id"])
        if doc:
            docs_payload.append(
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "icon": doc["icon"],
                    "category": doc["category"],
                    "description": doc["description"],
                    "rel_path": doc["rel_path"],
                    "content": doc.get("content", ""),
                }
            )

    docs_json = json.dumps(docs_payload).replace("</script>", "<\\/script>")

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OmniAudit-GEO Documentation Portal</title>
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <!-- Markdown & Syntax Highlighting -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/bash.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/python.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/json.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/yaml.min.js"></script>

  <style>
    :root {{
      --bg-main: #0b0f19;
      --bg-sidebar: #0f172a;
      --bg-card: #1e293b;
      --border-color: rgba(255, 255, 255, 0.08);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent-red: #eb1000;
      --accent-blue: #38bdf8;
      --accent-green: #10b981;
      --sidebar-width: 300px;
      --header-height: 64px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg-main);
      color: var(--text-main);
      line-height: 1.6;
      overflow-x: hidden;
    }}

    /* Top Navigation Header */
    header.top-nav {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: var(--header-height);
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.5rem;
      z-index: 50;
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: var(--text-main);
    }}
    .brand-logo {{
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, var(--accent-red), #ff4b4b);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.1rem;
      color: #fff;
    }}
    .brand-title {{
      font-size: 1.15rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .brand-badge {{
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 20px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent-blue);
      border: 1px solid rgba(56, 189, 248, 0.3);
      text-transform: uppercase;
    }}

    .nav-links {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}
    .nav-link {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 500;
      padding: 6px 12px;
      border-radius: 6px;
      transition: all 0.15s ease;
    }}
    .nav-link:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.05);
    }}
    .nav-link.primary {{
      background: rgba(235, 16, 0, 0.15);
      color: #ff6b6b;
      border: 1px solid rgba(235, 16, 0, 0.3);
      font-weight: 600;
    }}
    .nav-link.primary:hover {{
      background: rgba(235, 16, 0, 0.25);
    }}

    /* Main Container Layout */
    .app-container {{
      display: flex;
      margin-top: var(--header-height);
      min-height: calc(100vh - var(--header-height));
    }}

    /* Left Sidebar */
    aside.sidebar {{
      width: var(--sidebar-width);
      position: fixed;
      top: var(--header-height);
      bottom: 0;
      left: 0;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-color);
      overflow-y: auto;
      padding: 1.25rem 1rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      z-index: 40;
    }}

    /* Search Input */
    .search-box {{
      position: relative;
    }}
    .search-input {{
      width: 100%;
      padding: 9px 12px 9px 36px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: var(--text-main);
      font-size: 0.85rem;
      outline: none;
      transition: all 0.15s ease;
    }}
    .search-input:focus {{
      border-color: var(--accent-blue);
      background: rgba(56, 189, 248, 0.05);
      box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
    }}
    .search-icon {{
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 0.9rem;
      pointer-events: none;
    }}

    /* Navigation Sections */
    .nav-group-title {{
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
      margin-bottom: 0.5rem;
      padding-left: 0.5rem;
    }}
    .nav-item-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .nav-item-btn {{
      width: 100%;
      text-align: left;
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 0.86rem;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      transition: all 0.15s ease;
      text-decoration: none;
    }}
    .nav-item-btn:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }}
    .nav-item-btn.active {{
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.12);
      font-weight: 600;
      border-left: 3px solid #38bdf8;
      border-radius: 0 6px 6px 0;
    }}

    /* Content Area */
    main.content-pane {{
      margin-left: var(--sidebar-width);
      flex: 1;
      max-width: 960px;
      padding: 2.5rem 3rem 5rem 3rem;
    }}

    /* Breadcrumbs */
    .breadcrumbs {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-bottom: 1.5rem;
    }}
    .breadcrumbs span.separator {{
      opacity: 0.5;
    }}
    .breadcrumbs span.current {{
      color: var(--accent-blue);
      font-weight: 600;
    }}

    /* Markdown Styling */
    .markdown-body {{
      color: #e2e8f0;
      font-size: 1rem;
      line-height: 1.75;
    }}
    .markdown-body h1 {{
      font-size: 2.2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      color: #ffffff;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--border-color);
    }}
    .markdown-body h2 {{
      font-size: 1.5rem;
      font-weight: 700;
      color: #f1f5f9;
      margin-top: 2.2rem;
      margin-bottom: 0.75rem;
      letter-spacing: -0.02em;
    }}
    .markdown-body h3 {{
      font-size: 1.2rem;
      font-weight: 600;
      color: #cbd5e1;
      margin-top: 1.75rem;
      margin-bottom: 0.5rem;
    }}
    .markdown-body p {{
      margin-bottom: 1.2rem;
    }}
    .markdown-body a {{
      color: var(--accent-blue);
      text-decoration: none;
      font-weight: 500;
    }}
    .markdown-body a:hover {{
      text-decoration: underline;
    }}
    .markdown-body ul, .markdown-body ol {{
      margin-bottom: 1.2rem;
      padding-left: 1.5rem;
    }}
    .markdown-body li {{
      margin-bottom: 0.4rem;
    }}
    .markdown-body code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.88em;
      background: rgba(255, 255, 255, 0.08);
      padding: 2px 6px;
      border-radius: 4px;
      color: #38bdf8;
    }}
    .markdown-body pre {{
      background: #0d1117 !important;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 8px;
      padding: 1.2rem;
      margin-bottom: 1.5rem;
      overflow-x: auto;
      position: relative;
    }}
    .markdown-body pre code.hljs {{
      background: transparent !important;
      padding: 0;
      color: #e2e8f0;
      font-size: 0.86rem;
      line-height: 1.6;
      font-family: 'JetBrains Mono', monospace;
    }}
    .code-lang-badge {{
      position: absolute;
      top: 8px;
      right: 72px;
      font-size: 0.68rem;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 0.05em;
      pointer-events: none;
      user-select: none;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 2px 7px;
      border-radius: 4px;
    }}
    .markdown-body table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 1.5rem;
      font-size: 0.88rem;
    }}
    .markdown-body th, .markdown-body td {{
      padding: 10px 14px;
      border: 1px solid var(--border-color);
      text-align: left;
    }}
    .markdown-body th {{
      background: rgba(255, 255, 255, 0.04);
      font-weight: 600;
      color: #ffffff;
    }}
    .markdown-body tr:nth-child(even) {{
      background: rgba(255, 255, 255, 0.015);
    }}
    .markdown-body blockquote {{
      border-left: 4px solid var(--accent-blue);
      padding: 0.75rem 1rem;
      background: rgba(56, 189, 248, 0.05);
      border-radius: 0 8px 8px 0;
      margin-bottom: 1.5rem;
      color: #cbd5e1;
    }}
    .markdown-body hr {{
      border: none;
      border-top: 1px solid var(--border-color);
      margin: 2.5rem 0;
    }}

    /* Copy Code Button */
    .copy-btn {{
      position: absolute;
      top: 8px;
      right: 8px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #94a3b8;
      border-radius: 4px;
      font-size: 0.75rem;
      padding: 3px 8px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .copy-btn:hover {{
      background: rgba(255, 255, 255, 0.2);
      color: #fff;
    }}

    /* Page Navigation Footer */
    .doc-nav-footer {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      margin-top: 3.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border-color);
    }}
    .nav-arrow-btn {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      text-decoration: none;
      padding: 12px 18px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      min-width: 220px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .nav-arrow-btn:hover {{
      background: rgba(255, 255, 255, 0.06);
      border-color: var(--accent-blue);
    }}
    .nav-arrow-label {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }}
    .nav-arrow-title {{
      font-size: 0.92rem;
      color: var(--text-main);
      font-weight: 700;
    }}

    /* Mobile Drawer */
    .mobile-toggle {{
      display: none;
      background: transparent;
      border: none;
      color: #fff;
      font-size: 1.5rem;
      cursor: pointer;
    }}

    @media (max-width: 900px) {{
      .mobile-toggle {{ display: block; }}
      aside.sidebar {{
        transform: translateX(-100%);
        transition: transform 0.25s ease;
      }}
      aside.sidebar.open {{
        transform: translateX(0);
      }}
      main.content-pane {{
        margin-left: 0;
        padding: 1.5rem 1rem;
      }}
      .nav-links span.hide-mobile {{ display: none; }}
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header class="top-nav">
    <div style="display: flex; align-items: center; gap: 1rem;">
      <button class="mobile-toggle" onclick="toggleSidebar()">☰</button>
      <a href="/" class="brand-group">
        <img src="/brand/logo.png" alt="OmniAudit-GEO" style="height: 32px; width: auto; object-fit: contain; filter: drop-shadow(0 2px 6px rgba(56,189,248,0.25));" />
        <div class="brand-title">OmniAudit<span style="color: var(--accent-blue);">.GEO</span></div>
        <div class="brand-badge">Docs</div>
      </a>
    </div>
    <nav class="nav-links">
      <a href="/" class="nav-link primary">🔍 Launch Audit App</a>
      <a href="/api/docs" class="nav-link hide-mobile">📑 OpenAPI Swagger</a>
      <a href="/api/mcp" class="nav-link hide-mobile">🤖 MCP Endpoint</a>
      <a href="https://github.com/SH20RAJ/omniaudit" target="_blank" class="nav-link">⭐ GitHub</a>
    </nav>
  </header>

  <!-- Main Container -->
  <div class="app-container">
    <!-- Sidebar Navigation -->
    <aside class="sidebar" id="sidebar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="Search documentation..." oninput="handleSearch(this.value)">
      </div>

      <nav id="navGroups"></nav>
    </aside>

    <!-- Main Content Pane -->
    <main class="content-pane">
      <div class="breadcrumbs">
        <span>OmniAudit-GEO</span>
        <span class="separator">/</span>
        <span id="bcCategory">Documentation</span>
        <span class="separator">/</span>
        <span id="bcTitle" class="current">Getting Started</span>
      </div>

      <article id="markdownContent" class="markdown-body"></article>

      <div class="doc-nav-footer">
        <button id="prevBtn" class="nav-arrow-btn" style="visibility: hidden;" onclick="navigateDoc(-1)">
          <span class="nav-arrow-label">← Previous</span>
          <span id="prevTitle" class="nav-arrow-title"></span>
        </button>
        <button id="nextBtn" class="nav-arrow-btn" style="visibility: hidden; text-align: right;" onclick="navigateDoc(1)">
          <span class="nav-arrow-label">Next →</span>
          <span id="nextTitle" class="nav-arrow-title"></span>
        </button>
      </div>
    </main>
  </div>

  <script>
    // Embedded Registry of all documentation
    const DOCS_DATA = {docs_json};
    let currentDocId = "{initial_doc_id}";
    let activeFilterQuery = "";

    function init() {{
      // Read doc from URL params if present
      const urlParams = new URLSearchParams(window.location.search);
      const requestedDoc = urlParams.get('doc');
      if (requestedDoc && DOCS_DATA.some(d => d.id === requestedDoc)) {{
        currentDocId = requestedDoc;
      }}

      renderSidebar();
      loadDocument(currentDocId);

      // Handle popstate for back/forward browser buttons
      window.addEventListener('popstate', (event) => {{
        const params = new URLSearchParams(window.location.search);
        const docId = params.get('doc') || '{initial_doc_id}';
        loadDocument(docId, false);
      }});
    }}

    function renderSidebar() {{
      const navContainer = document.getElementById('navGroups');
      navContainer.innerHTML = '';

      // Group docs by category
      const categories = {{}};
      DOCS_DATA.forEach(doc => {{
        if (activeFilterQuery) {{
          const q = activeFilterQuery.toLowerCase();
          const match = doc.title.toLowerCase().includes(q) ||
                        doc.description.toLowerCase().includes(q) ||
                        doc.content.toLowerCase().includes(q);
          if (!match) return;
        }}
        if (!categories[doc.category]) {{
          categories[doc.category] = [];
        }}
        categories[doc.category].push(doc);
      }});

      for (const [catName, items] of Object.entries(categories)) {{
        const groupDiv = document.createElement('div');
        groupDiv.className = 'nav-group';

        const title = document.createElement('div');
        title.className = 'nav-group-title';
        title.textContent = catName;
        groupDiv.appendChild(title);

        const ul = document.createElement('ul');
        ul.className = 'nav-item-list';

        items.forEach(item => {{
          const li = document.createElement('li');
          const btn = document.createElement('button');
          btn.className = `nav-item-btn ${{item.id === currentDocId ? 'active' : ''}}`;
          btn.innerHTML = `<span>${{item.icon}}</span> <span>${{item.title}}</span>`;
          btn.onclick = () => selectDoc(item.id);
          li.appendChild(btn);
          ul.appendChild(li);
        }});

        groupDiv.appendChild(ul);
        navContainer.appendChild(groupDiv);
      }}
    }}

    function selectDoc(docId) {{
      loadDocument(docId, true);
      // Close mobile drawer if open
      document.getElementById('sidebar').classList.remove('open');
    }}

    function loadDocument(docId, updateHistory = true) {{
      const doc = DOCS_DATA.find(d => d.id === docId);
      if (!doc) return;

      currentDocId = docId;

      if (updateHistory) {{
        const newUrl = `${{window.location.pathname}}?doc=${{docId}}`;
        window.history.pushState({{ docId }}, '', newUrl);
      }}

      // Update breadcrumbs
      document.getElementById('bcCategory').textContent = doc.category;
      document.getElementById('bcTitle').textContent = doc.title;
      document.title = `${{doc.title}} — OmniAudit-GEO Documentation`;

      // Render Markdown
      marked.use({{
        gfm: true,
        breaks: true,
      }});

      // Rewrite relative markdown links in content
      let content = doc.content;
      // Convert relative links like [link](architecture.md) to [link](?doc=architecture)
      content = content.replace(/\\[([^\\]]+)\\]\\((?!http|#|mailto:)([^)]+)\\.md\\)/g, (match, text, file) => {{
        const cleanSlug = file.split('/').pop();
        return `[${{text}}](?doc=${{cleanSlug}})`;
      }});

      const parsedHtml = DOMPurify.sanitize(marked.parse(content));
      const contentEl = document.getElementById('markdownContent');
      contentEl.innerHTML = parsedHtml;

      // Run syntax highlighting & attach badges and copy buttons to all code blocks
      contentEl.querySelectorAll('pre').forEach(pre => {{
        const code = pre.querySelector('code');
        if (code) {{
          try {{
            hljs.highlightElement(code);
          }} catch (err) {{
            console.warn('highlight.js error:', err);
          }}

          let langName = '';
          code.classList.forEach(cls => {{
            if (cls.startsWith('language-')) {{
              langName = cls.replace('language-', '').toUpperCase();
            }}
          }});
          if (langName) {{
            const badge = document.createElement('span');
            badge.className = 'code-lang-badge';
            badge.textContent = langName;
            pre.appendChild(badge);
          }}
        }}

        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.textContent = 'Copy';
        btn.onclick = () => {{
          const textToCopy = code ? code.innerText : pre.innerText;
          navigator.clipboard.writeText(textToCopy);
          btn.textContent = 'Copied!';
          setTimeout(() => {{ btn.textContent = 'Copy'; }}, 2000);
        }};
        pre.appendChild(btn);
      }});

      // Update Sidebar Active Class
      document.querySelectorAll('.nav-item-btn').forEach(btn => {{
        btn.classList.remove('active');
        if (btn.innerText.includes(doc.title)) {{
          btn.classList.add('active');
        }}
      }});

      // Update Next / Prev buttons
      const currentIndex = DOCS_DATA.findIndex(d => d.id === docId);
      const prevDoc = currentIndex > 0 ? DOCS_DATA[currentIndex - 1] : null;
      const nextDoc = currentIndex < DOCS_DATA.length - 1 ? DOCS_DATA[currentIndex + 1] : null;

      const prevBtn = document.getElementById('prevBtn');
      const nextBtn = document.getElementById('nextBtn');

      if (prevDoc) {{
        prevBtn.style.visibility = 'visible';
        document.getElementById('prevTitle').textContent = `${{prevDoc.icon}} ${{prevDoc.title}}`;
      }} else {{
        prevBtn.style.visibility = 'hidden';
      }}

      if (nextDoc) {{
        nextBtn.style.visibility = 'visible';
        document.getElementById('nextTitle').textContent = `${{nextDoc.icon}} ${{nextDoc.title}}`;
      }} else {{
        nextBtn.style.visibility = 'hidden';
      }}

      window.scrollTo(0, 0);
    }}

    function navigateDoc(direction) {{
      const currentIndex = DOCS_DATA.findIndex(d => d.id === currentDocId);
      const newIndex = currentIndex + direction;
      if (newIndex >= 0 && newIndex < DOCS_DATA.length) {{
        selectDoc(DOCS_DATA[newIndex].id);
      }}
    }}

    function handleSearch(val) {{
      activeFilterQuery = val.trim();
      renderSidebar();
    }}

    function toggleSidebar() {{
      document.getElementById('sidebar').classList.toggle('open');
    }}

    window.onload = init;
  </script>
</body>
</html>
"""
