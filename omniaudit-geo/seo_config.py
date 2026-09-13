#!/usr/bin/env python3
"""
OmniAudit-GEO — Master SEO, Metadata & Structured Data Configuration.
Implements modern Search Engine Optimization (SEO), Generative Engine Optimization (GEO),
Answer Engine Optimization (AEO), Schema.org JSON-LD graphs, OpenGraph, and Twitter Card specifications.
"""

SEO_TITLE = "OmniAudit-GEO — Enterprise Brand AI-Readiness & GEO Engine"
SEO_DESCRIPTION = "Diagnose website AI discoverability barriers (robots.txt AI bot policies, hydration gaps, Schema.org entity graphs, AEO quotability) and on-site visitor retention. Local deterministic AST analysis executes in sub-millisecond benchmark conditions; real website audit latency depends on network and target response time."
SEO_CANONICAL_URL = "https://omniaudit-geo.onrender.com/"
SEO_OG_IMAGE = "https://omniaudit-geo.onrender.com/brand/og-image.png"

SCHEMA_JSON_LD = """{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      "@id": "https://omniaudit-geo.onrender.com/#software",
      "name": "OmniAudit-GEO",
      "applicationCategory": "DeveloperApplication",
      "operatingSystem": "All",
      "url": "https://omniaudit-geo.onrender.com/",
      "description": "Enterprise Brand AI-Readiness and Generative Engine Optimization (GEO) audit engine and Anthropic Model Context Protocol (MCP) server.",
      "image": "https://omniaudit-geo.onrender.com/brand/og-image.png",
      "softwareVersion": "1.0.0",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "author": [
        {
          "@type": "Person",
          "name": "Shaswat Raj",
          "url": "https://github.com/sh20raj",
          "sameAs": ["https://github.com/sh20raj", "https://twitter.com/sh20raj"]
        },
        {
          "@type": "Person",
          "name": "Prithvi",
          "url": "https://github.com/chikolavosaki-sys",
          "sameAs": ["https://github.com/chikolavosaki-sys"]
        }
      ]
    },
    {
      "@type": "Organization",
      "@id": "https://omniaudit-geo.onrender.com/#organization",
      "name": "OmniAudit-GEO",
      "url": "https://omniaudit-geo.onrender.com/",
      "logo": "https://omniaudit-geo.onrender.com/brand/logo.png",
      "sameAs": [
        "https://github.com/SH20RAJ/omniaudit"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://omniaudit-geo.onrender.com/#website",
      "url": "https://omniaudit-geo.onrender.com/",
      "name": "OmniAudit-GEO",
      "publisher": {
        "@id": "https://omniaudit-geo.onrender.com/#organization"
      }
    },
    {
      "@type": "FAQPage",
      "@id": "https://omniaudit-geo.onrender.com/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is OmniAudit-GEO?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "OmniAudit-GEO is an open-standard Agent Skill Marketplace adhering to agentskills.io and Model Context Protocol (MCP) for auditing website AI Discoverability (ACPI) and On-site Visitor Retention (CRS)."
          }
        },
        {
          "@type": "Question",
          "name": "What is the AI Citation Probability Index (ACPI)?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "ACPI is a deterministic, heuristic-weighted 0-100 score measuring crawlability, JavaScript hydration parity, Schema.org entity disambiguation, atomic fact density, and trust signals for AI search engines like ChatGPT, Perplexity, and Claude."
          }
        },
        {
          "@type": "Question",
          "name": "What is the Cognitive Retention Score (CRS)?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "CRS is a deterministic, heuristic-weighted 0-100 score measuring on-site visitor orientation, above-the-fold value proposition clarity, reading ease, and bounce resistance for visitors arriving from AI search referrals."
          }
        }
      ]
    }
  ]
}"""

SEO_HEAD_HTML = f"""  <title>{SEO_TITLE}</title>
  <meta name="description" content="{SEO_DESCRIPTION}" />
  <meta name="keywords" content="GEO, Generative Engine Optimization, AEO, Answer Engine Optimization, AI SEO, Brand AI Readiness, agentskills.io, MCP, Model Context Protocol, ChatGPT Search, Perplexity SEO, Claude AI, AI Crawler Audit, robots.txt AI, Schema.org JSON-LD" />
  <meta name="author" content="Shaswat Raj &amp; Prithvi" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
  <meta name="bingbot" content="index, follow, max-snippet:-1, max-image-preview:large" />
  <link rel="canonical" href="{SEO_CANONICAL_URL}" />

  <!-- OpenGraph Metadata -->
  <meta property="og:locale" content="en_US" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{SEO_TITLE}" />
  <meta property="og:description" content="{SEO_DESCRIPTION}" />
  <meta property="og:url" content="{SEO_CANONICAL_URL}" />
  <meta property="og:site_name" content="OmniAudit-GEO" />
  <meta property="og:image" content="{SEO_OG_IMAGE}" />
  <meta property="og:image:secure_url" content="{SEO_OG_IMAGE}" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="OmniAudit-GEO Platform Overview &amp; AI Readiness Metrics" />

  <!-- Twitter Card Metadata -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@sh20raj" />
  <meta name="twitter:creator" content="@sh20raj" />
  <meta name="twitter:title" content="{SEO_TITLE}" />
  <meta name="twitter:description" content="{SEO_DESCRIPTION}" />
  <meta name="twitter:image" content="{SEO_OG_IMAGE}" />

  <!-- Icons & Web App Manifest -->
  <link rel="icon" type="image/x-icon" href="/favicon.ico" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <meta name="theme-color" content="#0b0f19" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
{SCHEMA_JSON_LD}
  </script>
"""

NOSCRIPT_SEMANTIC_BODY = """
<noscript>
  <div style="background: #0b0f19; color: #f8fafc; font-family: sans-serif; padding: 2rem; max-width: 800px; margin: 0 auto;">
    <h1>OmniAudit-GEO — Enterprise Brand AI-Readiness & GEO Engine</h1>
    <p>OmniAudit-GEO is an open-standard Agent Skill Marketplace compliant with the <code>agentskills.io</code> specification and Anthropic Model Context Protocol (MCP). It equips AI assistants with tools to diagnose why web properties are ignored or distorted by AI search engines (Perplexity, ChatGPT Search, Claude, Google AI Overviews) and why referred visitors bounce.</p>

    <h2>Core Skills in Marketplace:</h2>
    <ul>
      <li><strong>crawl-render-audit:</strong> Analyzes robots.txt AI policies and detects client-side JavaScript hydration gaps.</li>
      <li><strong>structured-entity-audit:</strong> Validates Schema.org JSON-LD and authoritative sameAs entity disambiguation.</li>
      <li><strong>aeo-quotability-audit:</strong> Measures Answer Engine Optimization (AEO) and atomic fact density.</li>
      <li><strong>freshness-corroboration-audit:</strong> Scans copyright year 2026, timestamps, and publisher trust signals.</li>
      <li><strong>on-site-engagement-audit:</strong> Assesses above-the-fold value proposition clarity and bounce resistance.</li>
    </ul>

    <h2>Scoring Indices:</h2>
    <ul>
      <li><strong>ACPI (AI Citation Probability Index):</strong> 0 to 100 severity-weighted discoverability score.</li>
      <li><strong>CRS (Cognitive Retention Score):</strong> 0 to 100 on-site visitor orientation score.</li>
    </ul>

    <h2>API & Integrations:</h2>
    <p>Audit API: <code>GET /api/audit?url=&lt;target&gt;</code> | Remote MCP Endpoint: <code>POST /api/mcp</code></p>
    <p>Explore full interactive console by enabling JavaScript or visiting <a href="/api/docs" style="color:#38bdf8;">API Documentation</a>.</p>
    <p>&copy; 2026 Shaswat Raj &amp; Prithvi &middot; Adobe University Hackathon 2026 (Round 3 CRP)</p>
  </div>
</noscript>
"""
