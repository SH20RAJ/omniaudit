#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server Adapter for OmniAudit-GEO.
Enables Claude Desktop, Cursor, and Antigravity agents to discover and invoke
the Brand AI-Readiness Audit Marketplace natively via JSON-RPC 2.0.

Exposes all 6 agentskills.io modular tools:
1. audit_website (alias: audit_brand_ai_readiness) — Master Orchestrator
2. inspect_robots_and_rendering — Skill 1 (Crawl & Render)
3. inspect_structured_data — Skill 2 (Schema & Entity)
4. inspect_aeo_quotability — Skill 3 (Quotability & Facts)
5. inspect_freshness_trust — Skill 4 (Freshness & Corroboration)
6. inspect_on_site_retention — Skill 5 (On-site Retention)
"""

import json
import os
import sys
import urllib.parse

# Ensure audit_runner is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from audit_runner import (
    HTMLContentExtractor,
    audit_aeo_quotability,
    audit_crawl_render,
    audit_freshness_trust,
    audit_on_site_engagement,
    audit_structured_data,
    enrich_findings_actions,
    fetch_url,
    run_full_audit,
)

MCP_TOOLS = [
    {
        "name": "audit_website",
        "description": "Comprehensive master audit of website AI Discoverability (GEO/AEO, robots.txt, Schema.org JSON-LD, JS hydration) and On-site Retention (CRS).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The target website URL to audit (e.g. 'https://adobe.com').",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "audit_brand_ai_readiness",
        "description": "Alias for audit_website. Audits off-site AI Discoverability and on-site visitor retention.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The target website URL to audit.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "inspect_robots_and_rendering",
        "description": "Audits robots.txt AI bot directives (GPTBot, ClaudeBot, PerplexityBot) and detects client-side hydration gaps in JavaScript SPAs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target website URL.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "inspect_structured_data",
        "description": "Validates Schema.org JSON-LD graph, verifying sameAs Wikidata and entity disambiguation to prevent LLM hallucinations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target website URL.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "inspect_aeo_quotability",
        "description": "Evaluates sentence-level atomic fact density, interrogative Q&A headers, and tabular accessibility for answer engines.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target website URL.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "inspect_freshness_trust",
        "description": "Audits temporal freshness, copyright decay, author bylines, and citations for AI knowledge graph credibility.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target website URL.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "inspect_on_site_retention",
        "description": "Evaluates hero section orientation, H1 conciseness, Flesch-Kincaid reading ease, CTA contrast, and bounce risk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target website URL.",
                }
            },
            "required": ["url"],
        },
    },
]


def execute_tool(name: str, arguments: dict) -> dict:
    """
    Executes an audit tool according to official contract schemas:
    - 'audit_website' & 'audit_brand_ai_readiness' -> BrandAIReadinessAuditReport (audit_schema.json)
    - Specialist 'inspect_*' tools -> SpecialistAuditResult (specialist_audit_schema.json)
    """
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary")

    url = arguments.get("url")
    if not url or not isinstance(url, str) or not url.strip():
        raise ValueError("Missing or invalid 'url' parameter: must be a non-empty string")

    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if name in ("audit_website", "audit_brand_ai_readiness"):
        return run_full_audit(url)

    # Sub-audit execution: returns SpecialistAuditResult conforming payload
    fetch_result = fetch_url(url)
    if fetch_result.get("error"):
        return {
            "site": urllib.parse.urlparse(url).netloc or url,
            "tool": name,
            "error": fetch_result["error"],
            "total_findings": 0,
            "findings": [],
        }

    html = fetch_result.get("html", "")
    headers = fetch_result.get("headers", {})
    extractor = HTMLContentExtractor()
    extractor.feed(html)

    findings = []
    if name == "inspect_robots_and_rendering":
        findings = audit_crawl_render(url, html, headers)
    elif name == "inspect_structured_data":
        findings = audit_structured_data(url, extractor)
    elif name == "inspect_aeo_quotability":
        findings = audit_aeo_quotability(extractor)
    elif name == "inspect_freshness_trust":
        findings = audit_freshness_trust(extractor, html, url)
    elif name == "inspect_on_site_retention":
        findings = audit_on_site_engagement(extractor)
    else:
        raise ValueError(f"Unknown tool: {name}")

    enrich_findings_actions(findings)
    return {
        "site": urllib.parse.urlparse(url).netloc or url,
        "tool": name,
        "total_findings": len(findings),
        "findings": findings,
    }


def handle_json_rpc(request_input) -> dict:
    try:
        if isinstance(request_input, dict):
            req = request_input
        else:
            req = json.loads(request_input)
        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "omniaudit-geo-mcp-server",
                        "version": "1.0.0",
                    },
                },
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": MCP_TOOLS,
                },
            }

        elif method == "tools/call":
            params = req.get("params")
            if not isinstance(params, dict):
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": "Invalid params: 'params' must be an object"},
                }

            name = params.get("name")
            if not isinstance(name, str):
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": "Invalid params: 'name' must be a string"},
                }
            matched_tool = next((t for t in MCP_TOOLS if t["name"] == name), None)
            if not matched_tool:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Tool '{name}' not found"},
                }

            arguments = params.get("arguments")
            if not isinstance(arguments, dict):
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": "Invalid params: 'arguments' must be an object"},
                }

            url = arguments.get("url")
            if not url or not isinstance(url, str) or not url.strip():
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params: 'url' is required and must be a non-empty string",
                    },
                }

            try:
                result_data = execute_tool(name, arguments)
            except ValueError as ve:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": f"Invalid params: {ve}"},
                }
            except Exception as ex:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": f"Internal error during tool execution: {ex}"},
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result_data, indent=2),
                        }
                    ]
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not implemented"},
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": str(e)},
        }


def run_self_test():
    """Runs a self-test of the MCP server methods."""
    print("Testing MCP initialize...")
    init_res = handle_json_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}))
    assert init_res["result"]["serverInfo"]["name"] == "omniaudit-geo-mcp-server", "Initialize failed"
    print("✓ Initialize passed")

    print("Testing MCP tools/list...")
    tools_res = handle_json_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}))
    tools = tools_res["result"]["tools"]
    assert len(tools) == 7, f"Expected 7 tools, got {len(tools)}"
    tool_names = [t["name"] for t in tools]
    print(f"✓ tools/list passed ({len(tools)} tools: {', '.join(tool_names)})")

    print("All MCP self-tests passed successfully!")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_self_test()
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = handle_json_rpc(line)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
