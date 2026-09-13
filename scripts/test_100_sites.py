#!/usr/bin/env python3
"""
OmniAudit-GEO — 100 Diverse Live Websites Stress Test.
Audits 100 real-world websites across 10 distinct categories, verifying schema
validation, error resilience, ACPI/CRS score distributions, and latency benchmarks.
"""

from __future__ import annotations

import concurrent.futures
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

from audit_runner import run_full_audit

# 100 curated sites across 10 categories
SITES_100 = [
    # 1. Tech Giants & Dev Tools (10)
    ("https://google.com", "Tech Giants"),
    ("https://microsoft.com", "Tech Giants"),
    ("https://apple.com", "Tech Giants"),
    ("https://amazon.com", "Tech Giants"),
    ("https://github.com", "Tech Giants"),
    ("https://gitlab.com", "Tech Giants"),
    ("https://stackoverflow.com", "Tech Giants"),
    ("https://pypi.org", "Tech Giants"),
    ("https://openai.com", "Tech Giants"),
    ("https://anthropic.com", "Tech Giants"),
    # 2. News & Publishers (10)
    ("https://bbc.com", "News & Media"),
    ("https://nytimes.com", "News & Media"),
    ("https://cnn.com", "News & Media"),
    ("https://theverge.com", "News & Media"),
    ("https://techcrunch.com", "News & Media"),
    ("https://wired.com", "News & Media"),
    ("https://reuters.com", "News & Media"),
    ("https://bloomberg.com", "News & Media"),
    ("https://theguardian.com", "News & Media"),
    ("https://lemonde.fr", "News & Media"),
    # 3. E-Commerce & Retail (10)
    ("https://walmart.com", "E-Commerce"),
    ("https://target.com", "E-Commerce"),
    ("https://ebay.com", "E-Commerce"),
    ("https://etsy.com", "E-Commerce"),
    ("https://shopify.com", "E-Commerce"),
    ("https://bestbuy.com", "E-Commerce"),
    ("https://ikea.com", "E-Commerce"),
    ("https://zara.com", "E-Commerce"),
    ("https://nike.com", "E-Commerce"),
    ("https://adidas.com", "E-Commerce"),
    # 4. Universities & Academia (10)
    ("https://mit.edu", "Academia"),
    ("https://stanford.edu", "Academia"),
    ("https://harvard.edu", "Academia"),
    ("https://berkeley.edu", "Academia"),
    ("https://ox.ac.uk", "Academia"),
    ("https://cam.ac.uk", "Academia"),
    ("https://cmu.edu", "Academia"),
    ("https://caltech.edu", "Academia"),
    ("https://ethz.ch", "Academia"),
    ("https://iitb.ac.in", "Academia"),
    # 5. Non-Profits & Foundations (10)
    ("https://wikipedia.org", "Non-Profit"),
    ("https://mozilla.org", "Non-Profit"),
    ("https://apache.org", "Non-Profit"),
    ("https://linuxfoundation.org", "Non-Profit"),
    ("https://archive.org", "Non-Profit"),
    ("https://w3.org", "Non-Profit"),
    ("https://eff.org", "Non-Profit"),
    ("https://un.org", "Non-Profit"),
    ("https://who.int", "Non-Profit"),
    ("https://redcross.org", "Non-Profit"),
    # 6. Government & Public Services (10)
    ("https://nasa.gov", "Government"),
    ("https://cdc.gov", "Government"),
    ("https://noaa.gov", "Government"),
    ("https://whitehouse.gov", "Government"),
    ("https://gov.uk", "Government"),
    ("https://india.gov.in", "Government"),
    ("https://europa.eu", "Government"),
    ("https://canada.ca", "Government"),
    ("https://nih.gov", "Government"),
    ("https://usps.com", "Government"),
    # 7. SaaS & B2B Platforms (10)
    ("https://stripe.com", "SaaS & B2B"),
    ("https://slack.com", "SaaS & B2B"),
    ("https://zoom.us", "SaaS & B2B"),
    ("https://salesforce.com", "SaaS & B2B"),
    ("https://hubspot.com", "SaaS & B2B"),
    ("https://atlassian.com", "SaaS & B2B"),
    ("https://notion.so", "SaaS & B2B"),
    ("https://figma.com", "SaaS & B2B"),
    ("https://canva.com", "SaaS & B2B"),
    ("https://airtable.com", "SaaS & B2B"),
    # 8. Streaming, Media & Publishing (10)
    ("https://netflix.com", "Streaming & Media"),
    ("https://spotify.com", "Streaming & Media"),
    ("https://soundcloud.com", "Streaming & Media"),
    ("https://twitch.tv", "Streaming & Media"),
    ("https://vimeo.com", "Streaming & Media"),
    ("https://imdb.com", "Streaming & Media"),
    ("https://bandcamp.com", "Streaming & Media"),
    ("https://medium.com", "Streaming & Media"),
    ("https://substack.com", "Streaming & Media"),
    ("https://newsletter.pragmaticengineer.com", "Streaming & Media"),
    # 9. Modern Frameworks & Dev Docs (10)
    ("https://react.dev", "Developer Docs"),
    ("https://vuejs.org", "Developer Docs"),
    ("https://svelte.dev", "Developer Docs"),
    ("https://angular.dev", "Developer Docs"),
    ("https://nextjs.org", "Developer Docs"),
    ("https://fastapi.tiangolo.com", "Developer Docs"),
    ("https://expressjs.com", "Developer Docs"),
    ("https://tailwindcss.com", "Developer Docs"),
    ("https://rust-lang.org", "Developer Docs"),
    ("https://go.dev", "Developer Docs"),
    # 10. Free Hosting, Blogs & Mentioned Sites (10)
    ("https://sh20raj.github.io", "Free / Niche"),
    ("https://pages.github.com", "Free / Niche"),
    ("https://googleblog.blogspot.com", "Free / Niche"),
    ("https://wordpress.org", "Free / Niche"),
    ("https://ghost.org", "Free / Niche"),
    ("https://campusloop.space", "Free / Niche"),
    ("https://instagram.com", "Free / Niche"),
    ("https://rauchg.com", "Free / Niche"),
    ("https://news.ycombinator.com", "Free / Niche"),
    ("https://kith.com", "Free / Niche"),
]


def audit_single_site(item: tuple[str, str]) -> dict:
    url, category = item
    start = time.perf_counter()
    try:
        report = run_full_audit(url)
        elapsed_ms = (time.perf_counter() - start) * 1000
        is_valid, errors = validate_report(report)
        acpi = report.get("metrics", {}).get("acpi_score", 0.0)
        crs = report.get("metrics", {}).get("crs_score", 0.0)
        findings_count = len(report.get("findings", []))
        critical_count = report.get("summary", {}).get("critical", 0)
        proactive_count = len(report.get("proactive_recommendations", []))

        return {
            "url": url,
            "category": category,
            "status": "PASS" if is_valid else "SCHEMA_ERROR",
            "errors": errors,
            "acpi": acpi,
            "crs": crs,
            "findings": findings_count,
            "critical": critical_count,
            "proactive": proactive_count,
            "latency_ms": elapsed_ms,
            "exception": None,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "url": url,
            "category": category,
            "status": "EXCEPTION",
            "errors": [str(exc)],
            "acpi": 0.0,
            "crs": 0.0,
            "findings": 0,
            "critical": 0,
            "proactive": 0,
            "latency_ms": elapsed_ms,
            "exception": str(exc),
        }


def main():
    print(f"Starting 100-site evaluation across {len(SITES_100)} unique domains...")
    start_total = time.perf_counter()

    results = []
    # Run with 8 worker threads for fast execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(audit_single_site, site): site for site in SITES_100}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results.append(res)
            symbol = "✓" if res["status"] == "PASS" else "✗"
            print(
                f"[{len(results):>3}/100] {symbol} {res['url']:<38} | ACPI: {res['acpi']:5.1f} | CRS: {res['crs']:5.1f} | Findings: {res['findings']:2d} | {res['latency_ms']:6.0f}ms | {res['status']}"
            )

    total_time = time.perf_counter() - start_total
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] != "PASS")
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)
    avg_acpi = sum(r["acpi"] for r in results if r["status"] == "PASS") / max(1, passed)
    avg_crs = sum(r["crs"] for r in results if r["status"] == "PASS") / max(1, passed)

    print("\n" + "=" * 80)
    print("📊 100-SITE RIGOROUS STRESS TEST RESULTS")
    print("=" * 80)
    print(f"Total Sites Audited       : {len(results)}/100")
    print(f"Passed Schema Validation  : {passed}/{len(results)} ({passed / len(results) * 100:.1f}%)")
    print(f"Failures / Schema Errors  : {failed}")
    print(f"Average Execution Latency : {avg_latency:.1f} ms / website")
    print(f"Total Test Run Time       : {total_time:.2f} seconds")
    print(f"Average ACPI Score        : {avg_acpi:.1f} / 100.0")
    print(f"Average CRS Score         : {avg_crs:.1f} / 100.0")
    print("=" * 80)

    if failed > 0:
        print("\nFailure breakdown:")
        for r in results:
            if r["status"] != "PASS":
                print(f" - {r['url']}: {r['status']} -> {r['errors']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
