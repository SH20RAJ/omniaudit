#!/usr/bin/env python3
"""
Unit tests for Edge Cases, Multilingual Parsing, and Robustness Invariants.
Tests resilience against empty payloads, unicode/emojis, malformed JSON-LD,
skipped headings, nested schema @graph structures, and network error handling.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
REPO_ROOT = SKILL_ROOT.parent.parent

sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(1, str(REPO_ROOT / "skills/crawl-render-audit/scripts"))

from schema_validator import validate_report

from audit_runner import (
    HTMLContentExtractor,
    audit_aeo_quotability,
    audit_freshness_trust,
    audit_on_site_engagement,
    audit_structured_data,
    enrich_findings_actions,
    run_full_audit,
)
from safe_fetch import FetchValidationError, normalize_url


class TestEdgeCasesAndStress(unittest.TestCase):
    def test_empty_html_resilience(self):
        """Audit parser must gracefully handle empty or whitespace-only HTML."""
        for empty_payload in ["", "   \n\t  ", "<html></html>", "<html><body></body></html>"]:
            extractor = HTMLContentExtractor()
            extractor.feed(empty_payload)
            full_text = " ".join(extractor.text_chunks).strip()
            self.assertEqual(full_text, "")

            f_aeo = audit_aeo_quotability(extractor)
            f_struct = audit_structured_data("https://example.com", extractor)
            f_fresh = audit_freshness_trust(extractor, empty_payload, "https://example.com")
            f_eng = audit_on_site_engagement(extractor)

            enrich_findings_actions(f_aeo)
            enrich_findings_actions(f_struct)
            enrich_findings_actions(f_fresh)
            enrich_findings_actions(f_eng)

            self.assertIsInstance(f_aeo, list)
            self.assertIsInstance(f_struct, list)
            self.assertIsInstance(f_fresh, list)
            self.assertIsInstance(f_eng, list)

    def test_unicode_and_multilingual_html(self):
        """Ensure non-ASCII, UTF-8, Chinese, Arabic, Cyrillic, Hindi, and emoji text parse cleanly."""
        multilingual_html = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>全球创新科技 — 领先的智能解决方案 🚀</title>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "全球创新科技",
                "url": "https://example.cn",
                "description": "提供最前沿的分布式人工智能与云计算服务。"
            }
            </script>
        </head>
        <body>
            <h1>全球创新科技 🚀 人工智能平台</h1>
            <p>我们致力于为全球企业提供最高效的计算基础设施与智能模型服务。</p>
            <p>مرحبا بكم في منصتنا المتقدمة للذكاء الاصطناعي السحابي.</p>
            <p>Наша платформа обеспечивает высокую надежность и производительность.</p>
            <p>हम नवाचार और स्थिरता के लिए प्रतिबद्ध हैं।</p>
            <a href="/get-started">立即开始体验</a>
        </body>
        </html>
        """
        extractor = HTMLContentExtractor()
        extractor.feed(multilingual_html)
        full_text = " ".join(extractor.text_chunks)
        self.assertIn("全球创新科技", full_text)
        self.assertIn("🚀", full_text)

        f_struct = audit_structured_data("https://example.cn", extractor)
        f_aeo = audit_aeo_quotability(extractor)
        f_eng = audit_on_site_engagement(extractor)

        self.assertIsInstance(f_struct, list)
        self.assertIsInstance(f_aeo, list)
        self.assertIsInstance(f_eng, list)

    def test_malformed_html_tags(self):
        """Ensure resilient parsing of unclosed tags, nested comments, and messy markup."""
        messy_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Messy Test</title></head>
        <!-- messy comment -->
        <body>
            <div><div><p>Unclosed paragraph
            <span>Unclosed span
            <img src="test.jpg" alt="test">
            <script>var x = "<div>Not really a div</div>";</script>
            <a href="/buy">Click here to purchase now</a>
            <!-- comment 1 --> <!-- comment 2 -->
        </body>
        """
        extractor = HTMLContentExtractor()
        extractor.feed(messy_html)
        self.assertGreater(len(extractor.links), 0)

    def test_malformed_json_ld_blocks(self):
        """Malformed JSON-LD syntax must surface finding F-003 without crashing."""
        malformed_json_html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Unclosed string literal,
                "broken": true,
            }
            </script>
            <script type="application/ld+json">
            [{"valid": "but not a dict"}]
            </script>
        </head>
        <body><h1>Hello</h1></body>
        </html>
        """
        extractor = HTMLContentExtractor()
        extractor.feed(malformed_json_html)
        findings = audit_structured_data("https://example.com", extractor)
        syntax_errors = [f for f in findings if f.get("id") == "F-003"]
        self.assertEqual(len(syntax_errors), 1)
        self.assertEqual(syntax_errors[0]["severity"], "high")

    def test_extreme_heading_anomalies(self):
        """Sites with missing H1 or skipped levels (H1 -> H4) must be flagged cleanly."""
        skipped_levels_html = """
        <html>
        <body>
            <h4>Fourth Level Direct</h4>
            <p>Body text without preceding H1 or H2.</p>
        </body>
        </html>
        """
        extractor = HTMLContentExtractor()
        extractor.feed(skipped_levels_html)
        findings = audit_aeo_quotability(extractor)
        enrich_findings_actions(findings)
        heading_findings = [
            f for f in findings if "heading" in f.get("category", "") or "Heading" in f.get("title", "")
        ]
        self.assertGreaterEqual(len(heading_findings), 1)

    def test_schema_nested_graph(self):
        """Verify @graph nesting with complete Organization and WebSite emits 0 false positives."""
        nested_html = """
        <html><head><script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "Organization", "name": "DeepOrg", "url": "https://deeporg.com", "sameAs": ["https://wikidata.org/wiki/Q123"]},
                {"@type": "WebSite", "name": "DeepOrg Site", "url": "https://deeporg.com"}
            ]
        }
        </script></head><body><h1>Deep Graph</h1></body></html>
        """
        extractor = HTMLContentExtractor()
        extractor.feed(nested_html)
        findings = audit_structured_data("https://deeporg.com", extractor)
        self.assertEqual(len(findings), 0)

    def test_url_normalization_rules(self):
        """Verify URL normalizer handles tricky formats, ports, and schemes safely."""
        self.assertEqual(normalize_url("example.com"), "https://example.com/")
        self.assertEqual(normalize_url("http://example.com/path"), "http://example.com/path")
        self.assertEqual(normalize_url("https://example.com:443/test?q=1"), "https://example.com:443/test?q=1")

        invalid_urls = [
            "",
            "   ",
            "ftp://example.com",
            "file:///etc/passwd",
            "javascript:alert(1)",
            "data:text/html,<b>hi</b>",
            "http://user:pass@example.com",
            "http://example.com:8080",
            "http://127.0.0.1",
            "http://localhost",
            "http://169.254.169.254",
            "http://10.0.0.1",
            "http://192.168.1.1",
            "http://2130706433",
        ]
        for bad_url in invalid_urls:
            with self.assertRaises(FetchValidationError, msg=f"Should reject: {bad_url}"):
                normalize_url(bad_url)

    def test_nonexistent_domain_graceful_handling(self):
        """DNS failure on nonexistent domain must produce a valid structured report with F-000."""
        report = run_full_audit("https://this-domain-definitely-does-not-exist-9988776655.org")
        is_valid, errs = validate_report(report)
        self.assertTrue(is_valid, f"Report failed schema validation: {errs}")
        self.assertGreater(report["summary"]["critical"], 0)
        self.assertTrue(any(f.get("id") == "F-000" for f in report["findings"]))

    def test_proactive_recommendations_schema_integrity(self):
        """Verify that proactive recommendations adhere strictly to required schema format."""
        report = run_full_audit("https://example.com")
        is_valid, errs = validate_report(report)
        self.assertTrue(is_valid, f"Schema validation error: {errs}")
        self.assertIn("proactive_recommendations", report)
        recs = report["proactive_recommendations"]
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)
        for r in recs:
            self.assertIn("id", r)
            self.assertIn("area", r)
            self.assertIn("priority", r)
            self.assertIn("recommendation", r)
            self.assertIn("expected_impact", r)


if __name__ == "__main__":
    unittest.main()
