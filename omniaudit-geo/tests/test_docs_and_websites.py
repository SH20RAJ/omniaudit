#!/usr/bin/env python3
"""
Comprehensive tests for OmniAudit-GEO:
1. Documentation Engine (all 29 documents, search, fallback resolution, cache)
2. FastAPI Documentation Endpoints (/docs, /api/docs/list, /api/docs/content)
3. Gradio UI Documentation Hub Functions (choices, headers, change callbacks)
4. Dockerfile & Container Packaging Contract (docs/ and protocols copied)
5. Full Website Auditing & Specialist Diagnostics (ACPI, CRS, MCP execution)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
WEBAPP_DIR = Path(__file__).resolve().parents[1]
ORCHESTRATOR_DIR = REPO_ROOT / "skills" / "audit-orchestrator" / "scripts"

for p in [str(REPO_ROOT), str(WEBAPP_DIR), str(ORCHESTRATOR_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from gradio_ui import (
    get_default_doc_choice,
    get_doc_choices,
    get_doc_markdown,
    on_category_change,
    on_doc_change,
    parse_doc_id_from_choice,
    render_doc_meta_header,
)
from main import app
from schema_validator import validate_report

from docs_manager import (
    DOCS_REGISTRY,
    build_documentation_portal_html,
    get_doc_by_id,
    search_docs,
)


class TestDocumentationSystem(unittest.TestCase):
    """Verifies that all documentation files exist, load correctly, and are searchable."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_all_29_docs_in_registry_exist_and_load(self):
        """Every registered doc must exist on disk, have content, and be non-empty."""
        self.assertGreaterEqual(len(DOCS_REGISTRY), 29, "DOCS_REGISTRY must contain at least 29 documents")
        for item in DOCS_REGISTRY:
            doc_id = item["id"]
            doc = get_doc_by_id(doc_id)
            self.assertIsNotNone(doc, f"Doc {doc_id} returned None")
            assert doc is not None
            self.assertTrue(doc["exists"], f"Doc {doc_id} marked as not existing at {doc['rel_path']}")
            self.assertGreater(len(doc["content"]), 50, f"Doc {doc_id} content too short")
            self.assertNotIn("Document Not Found", doc["content"], f"Doc {doc_id} returned Document Not Found error")
            self.assertTrue(doc["title"], f"Doc {doc_id} missing title")
            self.assertTrue(doc["category"], f"Doc {doc_id} missing category")

    def test_search_docs_returns_relevant_results(self):
        """search_docs should find relevant docs by keyword."""
        res_arch = search_docs("architecture")
        self.assertTrue(any(d["id"] == "architecture" for d in res_arch))

        res_robots = search_docs("robots")
        self.assertTrue(len(res_robots) >= 1)

        res_getting = search_docs("getting-started")
        self.assertTrue(any(d["id"] == "getting-started" for d in res_getting))

        res_empty = search_docs("")
        self.assertEqual(len(res_empty), len(DOCS_REGISTRY))

        res_bogus = search_docs("xyznonexistentterm99999")
        self.assertEqual(len(res_bogus), 0)

    def test_build_documentation_portal_html(self):
        """Standalone portal HTML generator must generate valid HTML with search and marked.js."""
        html = build_documentation_portal_html(initial_doc_id="getting-started")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("OmniAudit", html)
        self.assertIn("marked.min.js", html)
        self.assertIn('id="searchInput"', html)
        self.assertIn("Getting Started", html)

    def test_api_docs_endpoints(self):
        """All 29 docs must be retrievable via FastAPI /api/docs/content?doc=<id>."""
        # 1. /docs portal endpoint
        res = self.client.get("/docs?doc=getting-started")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers["content-type"])
        self.assertIn("Getting Started", res.text)

        # 2. /api/docs/list
        res_list = self.client.get("/api/docs/list")
        self.assertEqual(res_list.status_code, 200)
        catalog = res_list.json()
        self.assertEqual(len(catalog), len(DOCS_REGISTRY))

        # 3. /api/docs/content for all items
        for item in DOCS_REGISTRY:
            slug = item["id"]
            res_item = self.client.get(f"/api/docs/content?doc={slug}")
            self.assertEqual(res_item.status_code, 200, f"Failed to fetch /api/docs/content?doc={slug}")
            data = res_item.json()
            self.assertEqual(data["id"], slug)
            self.assertTrue(data["exists"])
            self.assertGreater(len(data["content"]), 50)

    def test_dockerfile_contains_docs_and_protocols(self):
        """Ensures Dockerfile explicitly copies docs/ and root markdown protocols."""
        dockerfile_path = REPO_ROOT / "Dockerfile"
        self.assertTrue(dockerfile_path.exists(), "Dockerfile missing")
        content = dockerfile_path.read_text(encoding="utf-8")

        self.assertIn("COPY docs/ ./docs/", content, "Dockerfile must copy docs/ into container")
        self.assertIn("COPY README.md ./README.md", content)
        self.assertIn("COPY AGENTS.md ./AGENTS.md", content)
        self.assertIn("COPY CLAUDE.md ./CLAUDE.md", content)
        self.assertIn("COPY CONTRIBUTING.md ./CONTRIBUTING.md", content)
        self.assertIn("COPY SECURITY.md ./SECURITY.md", content)
        self.assertIn("COPY pyproject.toml ./pyproject.toml", content)
        self.assertIn("COPY setup.py ./setup.py", content)

    def test_gradio_ui_docs_helpers(self):
        """Verifies Tab 6 Gradio helper functions."""
        choices_all = get_doc_choices("All Categories")
        self.assertEqual(len(choices_all), len(DOCS_REGISTRY))

        choices_canon = get_doc_choices("Canonical Guides")
        self.assertGreaterEqual(len(choices_canon), 10)

        default_choice = get_default_doc_choice()
        self.assertTrue(default_choice)

        doc_id = parse_doc_id_from_choice(choices_all[0])
        self.assertTrue(doc_id)

        header_html = render_doc_meta_header("getting-started")
        self.assertIn("Getting Started", header_html)
        self.assertIn("docs/getting-started.md", header_html)

        md = get_doc_markdown("getting-started")
        self.assertGreater(len(md), 100)
        self.assertNotIn("Document Not Found", md)

        # Change callbacks
        new_choices, new_header, new_md = on_category_change("Skill Instructions")
        self.assertIn("audit-orchestrator", new_header)

        h2, md2 = on_doc_change(choices_all[1])
        self.assertTrue(h2)
        self.assertTrue(md2)


class TestWebsiteAuditingEngine(unittest.TestCase):
    """Verifies end-to-end website auditing and specialist skill diagnostics."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_audit_website_simulated_production_brand(self):
        """Audits a complete modern production brand website."""
        mock_html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Acme AI Cloud Platform | Enterprise Intelligent Systems</title>
            <meta name="description" content="Acme AI Cloud empowers enterprises to optimize AI discoverability and customer retention.">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Corporation",
                "name": "Acme AI",
                "url": "https://acme.test",
                "sameAs": ["https://www.wikidata.org/wiki/Q123456", "https://en.wikipedia.org/wiki/Acme_AI"]
            }
            </script>
        </head>
        <body>
            <header>
                <nav><a href="/">Home</a><a href="/pricing">Pricing</a><a href="/docs">Docs</a></nav>
            </header>
            <main>
                <section class="hero">
                    <h1>Enterprise AI Discoverability & Retention Intelligence</h1>
                    <p>Acme AI analyzes your digital presence across Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO).</p>
                    <a href="/start" class="btn">Start Your Free Audit Today</a>
                </section>
                <section class="facts">
                    <h2>What is Generative Engine Optimization?</h2>
                    <p>Generative Engine Optimization is the systematic discipline of making digital content discoverable, verifiable, and quotable by autonomous generative AI engines.</p>
                    <h2>How does Acme AI improve brand retention?</h2>
                    <p>Acme AI improves brand retention by evaluating above-the-fold value proposition clarity and measuring reading ease across target audiences.</p>
                </section>
            </main>
            <footer>
                <p>&copy; 2026 Acme AI Inc. All rights reserved. Last updated: 2026-03-01.</p>
                <p>Published by Senior Technology Editor Dr. Shaswat Raj.</p>
            </footer>
        </body>
        </html>
        """

        mock_robots = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /
"""

        def mock_fetch(url, **kwargs):
            if url.endswith("/robots.txt"):
                return {
                    "status": 200,
                    "headers": {"content-type": "text/plain"},
                    "body": mock_robots.encode(),
                    "html": mock_robots,
                    "url": url,
                    "error": None,
                    "error_code": None,
                }
            return {
                "status": 200,
                "headers": {"content-type": "text/html; charset=utf-8"},
                "body": mock_html.encode(),
                "html": mock_html,
                "url": url,
                "error": None,
                "error_code": None,
            }

        with patch("audit_runner.safe_fetch", side_effect=mock_fetch):
            res = self.client.get("/api/audit?url=https://acme.example.com")
            self.assertEqual(res.status_code, 200)
            report = res.json()

            # Validate against schema
            is_valid, errs = validate_report(report)
            self.assertTrue(is_valid, f"Report schema validation failed: {errs}")

            # Verify metrics & scores
            metrics = report["metrics"]
            self.assertGreaterEqual(metrics["acpi_score"], 80.0)
            self.assertGreaterEqual(metrics["crs_score"], 80.0)
            self.assertEqual(report["site"], "acme.example.com")

    def test_audit_website_crawler_blocked(self):
        """Audits a website that blocks AI crawlers in robots.txt."""
        mock_html = "<html><body><h1>Welcome</h1><p>Test</p></body></html>"
        mock_robots = """User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /
"""

        def mock_fetch(url, **kwargs):
            if url.endswith("/robots.txt"):
                return {
                    "status": 200,
                    "headers": {"content-type": "text/plain"},
                    "body": mock_robots.encode(),
                    "html": mock_robots,
                    "url": url,
                    "error": None,
                    "error_code": None,
                }
            return {
                "status": 200,
                "headers": {"content-type": "text/html"},
                "body": mock_html.encode(),
                "html": mock_html,
                "url": url,
                "error": None,
                "error_code": None,
            }

        with patch("audit_runner.safe_fetch", side_effect=mock_fetch):
            res = self.client.get("/api/audit?url=https://blocked.example.com")
            self.assertEqual(res.status_code, 200)
            report = res.json()
            findings = [f["id"] for f in report["findings"]]
            self.assertIn("F-001-GPTBot", findings)
            self.assertIn("F-001-ClaudeBot", findings)

    def test_mcp_execute_audit_website_tool(self):
        """Verifies calling the audit_website tool over JSON-RPC 2.0 MCP."""

        def mock_fetch(url, **kwargs):
            return {
                "status": 200,
                "headers": {"content-type": "text/html"},
                "body": b"<html><body><h1>Hello World</h1><p>Sample audit content</p></body></html>",
                "html": "<html><body><h1>Hello World</h1><p>Sample audit content</p></body></html>",
                "url": url,
                "error": None,
                "error_code": None,
            }

        with patch("audit_runner.safe_fetch", side_effect=mock_fetch):
            rpc_req = {
                "jsonrpc": "2.0",
                "id": 42,
                "method": "tools/call",
                "params": {
                    "name": "audit_website",
                    "arguments": {"url": "https://mcp-test.com"},
                },
            }
            res = self.client.post("/api/mcp", json=rpc_req)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["id"], 42)
            self.assertIn("result", data)
            content = data["result"]["content"]
            self.assertTrue(len(content) > 0)
            self.assertIn("acpi_score", content[0]["text"])

    def test_audit_website_ecommerce_product_page(self):
        """Audits an e-commerce retail product page with JSON-LD Product schema."""
        mock_ecom_html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <title>NovaPro ANC Wireless Headphones | Ultra Acoustics</title>
            <meta name="description" content="Shop the NovaPro ANC Wireless Headphones with 45-hour battery life and spatial audio.">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "NovaPro ANC Wireless Headphones",
                "description": "High-fidelity active noise cancelling wireless headphones with 45-hour battery life.",
                "brand": {"@type": "Brand", "name": "Ultra Acoustics"},
                "offers": {
                    "@type": "Offer",
                    "price": "249.99",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock"
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.8",
                    "reviewCount": "1240"
                }
            }
            </script>
        </head>
        <body>
            <header><nav><a href="/">Store</a><a href="/cart">Cart (0)</a></nav></header>
            <main>
                <article>
                    <h1>NovaPro Active Noise Cancelling Headphones</h1>
                    <p class="price">$249.99 USD — Free 2-Day Shipping</p>
                    <button class="buy-now">Add to Cart</button>
                    <section class="specs">
                        <h2>Product Specifications</h2>
                        <p>The NovaPro headphones deliver 45 hours of continuous playback with rapid USB-C fast charging.</p>
                        <p>Engineered with custom 40mm beryllium drivers, active hybrid noise cancellation reduces ambient noise by up to 38dB.</p>
                    </section>
                </article>
            </main>
            <footer><p>&copy; 2026 Ultra Acoustics Inc.</p></footer>
        </body>
        </html>
        """

        def mock_fetch(url, **kwargs):
            return {
                "status": 200,
                "headers": {"content-type": "text/html; charset=utf-8"},
                "body": mock_ecom_html.encode(),
                "html": mock_ecom_html,
                "url": url,
                "error": None,
                "error_code": None,
            }

        with patch("audit_runner.safe_fetch", side_effect=mock_fetch):
            res = self.client.get("/api/audit?url=https://store.example.com/products/novapro")
            self.assertEqual(res.status_code, 200)
            report = res.json()
            is_valid, errs = validate_report(report)
            self.assertTrue(is_valid, f"E-commerce report schema invalid: {errs}")
            self.assertGreater(report["metrics"]["acpi_score"], 80.0)
            self.assertGreater(report["metrics"]["crs_score"], 80.0)

    def test_audit_website_news_media(self):
        """Audits an authoritative editorial news article with NewsArticle schema and freshness signals."""
        mock_news_html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Global AI Readiness Standards Announced for 2026 | TechObserver</title>
            <meta name="description" content="International consortium announces new Generative Engine Optimization benchmarks.">
            <meta name="author" content="Dr. Sarah Jenkins">
            <meta property="article:published_time" content="2026-02-15T09:00:00Z">
            <meta property="article:modified_time" content="2026-03-01T14:30:00Z">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                "headline": "Global AI Readiness Standards Announced for 2026",
                "datePublished": "2026-02-15T09:00:00Z",
                "dateModified": "2026-03-01T14:30:00Z",
                "author": [{"@type": "Person", "name": "Dr. Sarah Jenkins"}],
                "publisher": {"@type": "Organization", "name": "TechObserver Media"}
            }
            </script>
        </head>
        <body>
            <article>
                <header>
                    <h1>Global AI Readiness Standards Announced for 2026</h1>
                    <p>By Dr. Sarah Jenkins | Published February 15, 2026 | Updated March 1, 2026</p>
                </header>
                <section>
                    <p>According to the International Web Consortium report published today, over 74 percent of commercial web traffic will interact with generative AI synthesis agents by the end of 2026.</p>
                    <p>The standard establishes that machine crawlers require explicit semantic structure and clear attribution markers to cite external sources accurately.</p>
                </section>
            </article>
        </body>
        </html>
        """

        def mock_fetch(url, **kwargs):
            return {
                "status": 200,
                "headers": {"content-type": "text/html; charset=utf-8"},
                "body": mock_news_html.encode(),
                "html": mock_news_html,
                "url": url,
                "error": None,
                "error_code": None,
            }

        with patch("audit_runner.safe_fetch", side_effect=mock_fetch):
            res = self.client.get("/api/audit?url=https://techobserver.example.com/articles/ai-readiness-2026")
            self.assertEqual(res.status_code, 200)
            report = res.json()
            is_valid, errs = validate_report(report)
            self.assertTrue(is_valid, f"News report schema invalid: {errs}")
            self.assertGreater(report["metrics"]["acpi_score"], 80.0)

    def test_audit_website_spa_hydration_gap(self):
        """Audits a pure client-side SPA with minimal static markup triggering hydration gap finding F-002."""
        mock_spa_html = """<!DOCTYPE html>
        <html>
        <head><title>Modern Single Page App</title></head>
        <body>
            <div id="root"></div>
            <noscript>You need JavaScript to run this app.</noscript>
            <script>
                const root = createRoot(document.getElementById('root'));
                root.render(null);
            </script>
        </body>
        </html>
        """

        def mock_fetch(url, **kwargs):
            return {
                "status": 200,
                "headers": {"content-type": "text/html; charset=utf-8"},
                "body": mock_spa_html.encode(),
                "html": mock_spa_html,
                "url": url,
                "error": None,
                "error_code": None,
            }

        with patch("audit_runner.safe_fetch", side_effect=mock_fetch):
            res = self.client.get("/api/audit?url=https://spa.example.com")
            self.assertEqual(res.status_code, 200)
            report = res.json()
            finding_ids = [f["id"] for f in report["findings"]]
            self.assertIn("F-011", finding_ids, "F-011 hydration gap finding must be emitted for client-only SPA")

    def test_audit_website_live_public_domain_if_connected(self):
        """Performs a live audit against a public domain (https://example.com) if network is reachable."""
        try:
            res = self.client.get("/api/audit?url=https://example.com")
            if res.status_code == 200:
                report = res.json()
                is_valid, errs = validate_report(report)
                self.assertTrue(is_valid, f"Live audit report schema failed: {errs}")
                self.assertEqual(report["site"], "example.com")
            elif res.status_code in (408, 502, 504):
                self.skipTest("Public network timeout reaching example.com")
        except Exception as e:
            self.skipTest(f"Live network test skipped due to connectivity: {e}")


class TestCommandLineInterface(unittest.TestCase):
    """Verifies that unified CLI commands execute without error."""

    def test_cli_docs_list(self):
        """Verifies 'omni docs --list' prints document inventory."""
        import subprocess

        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "cli.py"), "docs", "--list"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("getting-started", res.stdout)
        self.assertIn("architecture", res.stdout)

    def test_cli_docs_get(self):
        """Verifies 'omni docs --get getting-started' prints markdown content."""
        import subprocess

        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "cli.py"), "docs", "--get", "getting-started"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Getting Started", res.stdout)

    def test_cli_version_and_help(self):
        """Verifies CLI help flags output help text cleanly."""
        import subprocess

        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "cli.py"), "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("OmniAudit-GEO", res.stdout)


if __name__ == "__main__":
    unittest.main()
