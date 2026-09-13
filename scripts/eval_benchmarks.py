#!/usr/bin/env python3
"""
eval_benchmarks.py — OmniAudit-GEO Evaluation Harness & Benchmark Suite
Mechanically computes precision, recall, false positive/negative rates,
per-fixture latency, and verifies recursive schema validity on every fixture.
"""

import pathlib
import sys
import time
from unittest.mock import patch

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT_DIR / "skills" / "audit-orchestrator" / "scripts"
FIXTURES_DIR = ROOT_DIR / "skills" / "audit-orchestrator" / "tests" / "fixtures" / "benchmark"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from schema_validator import validate_report

from audit_runner import run_full_audit

BENCHMARK_SPECS = [
    {
        "fixture": "crawler_blocked",
        "category": "Crawl & Robots",
        "robots": "User-agent: GPTBot\nDisallow: /\n",
        "expected_findings": {"F-001-GPTBot"},
        "expected_absences": {"F-002"},
        "desc": "Explicit GPTBot crawler block detected",
    },
    {
        "fixture": "hydration_spa",
        "category": "Hydration Gap",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": {"F-011"},
        "expected_absences": set(),
        "desc": "Client-only SPA empty DOM detected",
    },
    {
        "fixture": "partial_hydration",
        "category": "Hydration Gap",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": {"F-011"},
        "expected_absences": set(),
        "desc": "Partial hydration skeleton text detected",
    },
    {
        "fixture": "large_state_static",
        "category": "Hydration (FP Check)",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-011"},
        "desc": "No false-positive hydration gap on static state",
    },
    {
        "fixture": "app_router",
        "category": "Hydration (FP Check)",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-011"},
        "desc": "Next.js RSC static payload correctly classified",
    },
    {
        "fixture": "good_business",
        "category": "Production Brand",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-001-GPTBot", "F-002", "F-003b", "F-004"},
        "desc": "Clean production site produces 0 high/crit defects",
    },
    {
        "fixture": "good_structured",
        "category": "Structured Data",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-003", "F-004", "F-005"},
        "desc": "Valid JSON-LD @graph with sameAs authority",
    },
    {
        "fixture": "bad_structured",
        "category": "Structured Data",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": {"F-003", "F-012"},
        "expected_absences": set(),
        "desc": "Syntax error & missing sameAs flagged",
    },
    {
        "fixture": "strong_aeo",
        "category": "AEO & Quotability",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-015", "F-007"},
        "desc": "High atomic fact density & tabular quotability",
    },
    {
        "fixture": "weak_aeo",
        "category": "AEO & Quotability",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": {"F-006"},
        "expected_absences": set(),
        "desc": "Vague promotional fluff flagged for low fact density",
    },
    {
        "fixture": "stale_article",
        "category": "Freshness & Trust",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": {"F-009"},
        "expected_absences": set(),
        "desc": "Stale 2021 temporal decay flagged",
    },
    {
        "fixture": "current_article",
        "category": "Freshness & Trust",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-009"},
        "desc": "2026 timestamps + author byline verified fresh",
    },
    {
        "fixture": "strong_engagement",
        "category": "On-Site Engagement",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-019", "F-010"},
        "desc": "High readability + clear above-the-fold hero CTA",
    },
    {
        "fixture": "weak_engagement",
        "category": "On-Site Engagement",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": {"F-019"},
        "expected_absences": set(),
        "desc": "Wall of text / missing CTA flagged for bounce risk",
    },
    {
        "fixture": "documentation",
        "category": "On-Site Engagement",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": set(),
        "expected_absences": {"F-019"},
        "desc": "Technical API docs layout accurately scored",
    },
    {
        "fixture": "navigation_noise",
        "category": "On-Site Engagement",
        "robots": "User-agent: *\nAllow: /\n",
        "expected_findings": {"F-019"},
        "expected_absences": set(),
        "desc": "Bloated menu DOM vs low content ratio detected",
    },
]


def run_evals(return_dict: bool = False):
    print("╔═══════════════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                 OmniAudit-GEO — Benchmark Evaluation Harness (ECC Spec)                      ║")
    print("║       Adobe University Hackathon 2026 (Round 3 CRP) — 16 Golden Fixtures Test Matrix          ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════════════════════╝\n")

    print(
        f"{'#':<3} {'Fixture Name':<20} {'Category':<20} {'ACPI':<6} {'CRS':<6} {'Schema':<8} {'Latency':<9} {'Status':<6}"
    )
    print("─" * 95)

    passed_fixtures = 0
    total_time = 0.0
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_tn = 0
    schema_failures = 0
    benchmark_details = []

    for idx, spec in enumerate(BENCHMARK_SPECS, 1):
        fixture_file = FIXTURES_DIR / f"{spec['fixture']}.html"
        if not fixture_file.exists():
            print(f"❌ Fixture missing: {fixture_file}")
            continue

        html_content = fixture_file.read_text(encoding="utf-8")
        robots_text = spec["robots"]

        def fake_fetch(url, *, _robots=robots_text, _html=html_content, **kwargs):
            if url.endswith("/robots.txt"):
                return {
                    "status": 200,
                    "headers": {"content-type": "text/plain"},
                    "body": _robots.encode(),
                    "html": _robots,
                    "url": url,
                    "error": None,
                    "error_code": None,
                }
            return {
                "status": 200,
                "headers": {"content-type": "text/html; charset=utf-8"},
                "body": _html.encode(),
                "html": _html,
                "url": url,
                "error": None,
                "error_code": None,
            }

        start_t = time.perf_counter()
        with patch("audit_runner.safe_fetch", side_effect=fake_fetch):
            report = run_full_audit("https://benchmark.test/")
        elapsed_ms = (time.perf_counter() - start_t) * 1000
        total_time += elapsed_ms

        # Recursive Schema Validation on every generated report
        is_schema_valid, schema_errors = validate_report(report)
        if not is_schema_valid:
            schema_failures += 1

        finding_ids = {f["id"] for f in report["findings"]}

        # Compute TP, FP, FN for this benchmark
        expected_findings = spec["expected_findings"]
        expected_absences = spec["expected_absences"]

        tp = len(finding_ids & expected_findings)
        fn = len(expected_findings - finding_ids)
        fp = len(finding_ids & expected_absences)
        tn = 1 if len(expected_findings) == 0 and fp == 0 else 0

        total_tp += tp
        total_fn += fn
        total_fp += fp
        total_tn += tn

        fixture_passed = (fn == 0) and (fp == 0) and is_schema_valid
        if fixture_passed:
            passed_fixtures += 1
            status = "✓ PASS"
        else:
            status = "✗ FAIL"

        acpi = report["metrics"]["acpi_score"]
        crs = report["metrics"]["crs_score"]
        schema_status = "PASS" if is_schema_valid else "FAIL"

        print(
            f"{idx:<3} {spec['fixture']:<20} {spec['category']:<20} {acpi:<6.1f} {crs:<6.1f} {schema_status:<8} {elapsed_ms:>6.2f}ms   {status}"
        )

        benchmark_details.append(
            {
                "fixture": spec["fixture"],
                "category": spec["category"],
                "passed": fixture_passed,
                "acpi_score": acpi,
                "crs_score": crs,
                "schema_valid": is_schema_valid,
                "latency_ms": round(elapsed_ms, 2),
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }
        )

    total_fixtures = len(BENCHMARK_SPECS)
    pass_rate = (passed_fixtures / total_fixtures) * 100 if total_fixtures > 0 else 0
    avg_latency = total_time / total_fixtures if total_fixtures > 0 else 0

    precision = (total_tp / (total_tp + total_fp)) * 100 if (total_tp + total_fp) > 0 else 100.0
    recall = (total_tp / (total_tp + total_fn)) * 100 if (total_tp + total_fn) > 0 else 100.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 100.0

    print("─" * 95)
    print("📊 Evaluation Metrics & Statistical Accuracy:")
    print(f"   • Total Benchmarks Evaluated : {total_fixtures}")
    print(f"   • Passed Benchmarks          : {passed_fixtures}/{total_fixtures} ({pass_rate:.1f}%)")
    print(f"   • True Positives (TP)        : {total_tp}")
    print(f"   • False Positives (FP)       : {total_fp}")
    print(f"   • False Negatives (FN)       : {total_fn}")
    print(f"   • Measured Precision         : {precision:.1f}%")
    print(f"   • Measured Recall            : {recall:.1f}%")
    print(f"   • F1-Score                   : {f1:.1f}%")
    print(f"   • Average Execution Latency  : {avg_latency:.2f} ms / site")
    print(f"   • Total Eval Run Time        : {total_time:.2f} ms")
    print(f"   • Schema Validation Failures : {schema_failures}/{total_fixtures}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    summary_result = {
        "status": "passed" if passed_fixtures == total_fixtures else "failed",
        "total": total_fixtures,
        "passed": passed_fixtures,
        "failed": total_fixtures - passed_fixtures,
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn,
        "precision_pct": round(precision, 2),
        "recall_pct": round(recall, 2),
        "f1_score": round(f1, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "total_time_ms": round(total_time, 2),
        "schema_failures": schema_failures,
        "fixtures": benchmark_details,
    }

    if return_dict:
        return summary_result

    return 0 if passed_fixtures == total_fixtures else 1


if __name__ == "__main__":
    code = run_evals(return_dict=False)
    sys.exit(int(code) if isinstance(code, int) else 0)
