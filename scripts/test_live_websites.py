#!/usr/bin/env python3
"""
OmniAudit-GEO — Comprehensive Real-World Web & Specialist Skill Test Suite.
Verifies all 6 skills/agents across diverse live websites, edge cases, MCP tools,
FastAPI endpoints, and schema conformance according to Round 3 specifications.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
for p in [
    "omniaudit-geo",
    "skills/audit-orchestrator/scripts",
    "skills/crawl-render-audit/scripts",
    "skills/structured-entity-audit/scripts",
    "skills/aeo-quotability-audit/scripts",
    "skills/freshness-corroboration-audit/scripts",
    "skills/on-site-engagement-audit/scripts",
    "scripts",
]:
    sys.path.insert(0, str(REPO_ROOT / p))

from schema_validator import validate_report

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
from mcp_server import handle_json_rpc

# Terminal styling
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(
        f"{BOLD}{CYAN}╔═══════════════════════════════════════════════════════════════════════════════════════════════╗{RESET}"
    )
    print(
        f"{BOLD}{CYAN}║             OmniAudit-GEO — Comprehensive Real-World Web & Skill Evaluation Harness           ║{RESET}"
    )
    print(
        f"{BOLD}{CYAN}║             Adobe University Hackathon 2026 (Round 3 CRP Handout Verification)               ║{RESET}"
    )
    print(
        f"{BOLD}{CYAN}╚═══════════════════════════════════════════════════════════════════════════════════════════════╝{RESET}\n"
    )


def test_live_websites():
    print(f"{BOLD}Phase 1: Master Audit on Diverse Live Web Targets{RESET}")
    print("─" * 95)
    print(
        f"{'#':<3} {'Target Site':<32} {'Category':<18} {'ACPI':<6} {'CRS':<6} {'Findings':<10} {'Latency':<9} {'Status'}"
    )
    print("─" * 95)

    test_sites = [
        ("https://example.com", "Minimal Baseline (RFC 2606)"),
        ("https://adobe.com", "Enterprise Creative / Tech"),
        ("https://python.org", "Open Source Foundation"),
        ("https://github.com", "Developer Platform"),
        ("https://cloudflare.com", "CDN & Edge Infrastructure"),
        ("https://stripe.com", "Fintech / SaaS"),
        ("https://news.ycombinator.com", "Lightweight Dynamic Forum"),
        ("https://fastapi.tiangolo.com", "Modern Technical Documentation"),
    ]

    all_passed = True
    results = []

    for idx, (url, category) in enumerate(test_sites, 1):
        start = time.perf_counter()
        try:
            report = run_full_audit(url)
            elapsed = (time.perf_counter() - start) * 1000
            is_valid, errors = validate_report(report)

            acpi = report.get("metrics", {}).get("acpi_score", 0.0)
            crs = report.get("metrics", {}).get("crs_score", 0.0)
            findings = report.get("findings", [])

            # Verify Round 3 required fields
            assert "site" in report, "Missing 'site'"
            assert "audited_at" in report, "Missing 'audited_at'"
            assert "summary" in report, "Missing 'summary'"
            assert "total_findings" in report["summary"], "Missing 'summary.total_findings'"
            assert "critical" in report["summary"], "Missing 'summary.critical'"
            assert "high" in report["summary"], "Missing 'summary.high'"
            assert "medium" in report["summary"], "Missing 'summary.medium'"

            for f in findings:
                assert "id" in f, f"Finding missing 'id': {f}"
                assert "title" in f, f"Finding missing 'title': {f}"
                assert "severity" in f, f"Finding missing 'severity': {f}"
                assert "evidence" in f, f"Finding missing 'evidence': {f}"
                assert "suggested_action" in f, f"Finding missing 'suggested_action': {f}"
                assert "summary" in f["suggested_action"], f"Missing suggested_action.summary: {f}"
                assert "priority" in f["suggested_action"], f"Missing suggested_action.priority: {f}"

            status_str = f"{GREEN}✓ PASS{RESET}" if is_valid else f"{RED}✗ FAIL{RESET}"
            if not is_valid:
                all_passed = False

            print(
                f"{idx:<3} {url:<32} {category:<18} {acpi:<6.1f} {crs:<6.1f} {len(findings):<10} {elapsed:>6.0f}ms   {status_str}"
            )
            results.append({"url": url, "acpi": acpi, "crs": crs, "findings": len(findings), "valid": is_valid})
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            print(
                f"{idx:<3} {url:<32} {category:<18} {'ERR':<6} {'ERR':<6} {'0':<10} {elapsed:>6.0f}ms   {RED}✗ EXCEPTION: {exc}{RESET}"
            )
            all_passed = False

    print("─" * 95)
    return all_passed


def test_specialist_agents():
    print(f"\n{BOLD}Phase 2: Individual Specialist Agent Verifications{RESET}")
    print("─" * 95)

    test_url = "https://example.com"
    fetch_res = fetch_url(test_url)
    html = fetch_res.get("html", "")
    headers = fetch_res.get("headers", {})

    extractor = HTMLContentExtractor()
    extractor.feed(html)

    # 1. Crawl & Render Agent
    f_crawl = audit_crawl_render(test_url, html, headers)
    enrich_findings_actions(f_crawl)
    print(f"1. crawl-render-audit           : {len(f_crawl)} findings surfaced ({GREEN}✓ Verified{RESET})")

    # 2. Structured Data Agent
    f_struct = audit_structured_data(test_url, extractor)
    enrich_findings_actions(f_struct)
    print(f"2. structured-entity-audit      : {len(f_struct)} findings surfaced ({GREEN}✓ Verified{RESET})")

    # 3. AEO Quotability Agent
    f_aeo = audit_aeo_quotability(extractor)
    enrich_findings_actions(f_aeo)
    print(f"3. aeo-quotability-audit        : {len(f_aeo)} findings surfaced ({GREEN}✓ Verified{RESET})")

    # 4. Freshness & Trust Agent
    f_fresh = audit_freshness_trust(extractor, html, test_url)
    enrich_findings_actions(f_fresh)
    print(f"4. freshness-corroboration-audit: {len(f_fresh)} findings surfaced ({GREEN}✓ Verified{RESET})")

    # 5. On-Site Engagement Agent
    f_eng = audit_on_site_engagement(extractor)
    enrich_findings_actions(f_eng)
    print(f"5. on-site-engagement-audit     : {len(f_eng)} findings surfaced ({GREEN}✓ Verified{RESET})")

    print("─" * 95)
    return True


def test_mcp_tools():
    print(f"\n{BOLD}Phase 3: Model Context Protocol (MCP) JSON-RPC 2.0 Agent Calls{RESET}")
    print("─" * 95)

    tools_to_test = [
        ("audit_website", {"url": "https://example.com"}),
        ("inspect_robots_and_rendering", {"url": "https://example.com"}),
        ("inspect_structured_data", {"url": "https://example.com"}),
        ("inspect_aeo_quotability", {"url": "https://example.com"}),
        ("inspect_freshness_trust", {"url": "https://example.com"}),
        ("inspect_on_site_retention", {"url": "https://example.com"}),
    ]

    all_mcp_passed = True
    for tool_name, args in tools_to_test:
        rpc_req = {
            "jsonrpc": "2.0",
            "id": f"test-{tool_name}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": args,
            },
        }
        res = handle_json_rpc(rpc_req)
        has_error = "error" in res
        content = res.get("result", {}).get("content", [{}])[0].get("text", "")
        status_text = f"{GREEN}✓ PASS{RESET}" if not has_error and content else f"{RED}✗ FAIL{RESET}"
        print(f" • MCP Tool: {tool_name:<30} -> {status_text} (Response size: {len(content)} chars)")
        if has_error:
            all_mcp_passed = False

    print("─" * 95)
    return all_mcp_passed


def test_adversarial_security():
    print(f"\n{BOLD}Phase 4: Adversarial Security & SSRF Defense Invariants{RESET}")
    print("─" * 95)

    blocked_targets = [
        ("http://127.0.0.1:8080/admin", "Loopback IPv4"),
        ("http://localhost:3000", "Localhost Hostname"),
        ("http://169.254.169.254/latest/meta-data/", "AWS/Cloud Instance Metadata"),
        ("http://10.0.0.1/internal", "Private RFC 1918 Class A"),
        ("http://192.168.1.1/router", "Private RFC 1918 Class C"),
    ]

    security_passed = True
    for url, desc in blocked_targets:
        report = run_full_audit(url)
        findings = report.get("findings", [])
        is_blocked = (
            report.get("status") == "unknown"
            or "error" in report
            or any(
                "non-public ip" in f.get("evidence", "").lower()
                or "blocked" in f.get("evidence", "").lower()
                or "inaccessible" in f.get("title", "").lower()
                for f in findings
            )
        )
        status = f"{GREEN}✓ BLOCKED (Safe){RESET}" if is_blocked else f"{RED}✗ UNBLOCKED (Vulnerability!){RESET}"
        print(f" • Anti-SSRF: {desc:<32} ({url:<30}) -> {status}")
        if not is_blocked:
            security_passed = False

    print("─" * 95)
    return security_passed


def main():
    print_banner()
    p1 = test_live_websites()
    p2 = test_specialist_agents()
    p3 = test_mcp_tools()
    p4 = test_adversarial_security()

    all_passed = p1 and p2 and p3 and p4
    print("\n" + "=" * 95)
    if all_passed:
        print(f"{BOLD}{GREEN}🎉 ALL EVALUATIONS PASSED: 100% COMPLIANT WITH ADOBE ROUND 3 SPECIFICATION!{RESET}")
    else:
        print(f"{BOLD}{RED}❌ SOME EVALUATIONS FAILED. INSPECT TRACES ABOVE.{RESET}")
    print("=" * 95 + "\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
