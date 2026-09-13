# 🏆 OmniAudit-GEO: Round 4 Prototype Showcase & Jury Defense Masterplan

> **Adobe University Hackathon 2026 (CRP) — Round 4 Prototype Showcase (21–27 September 2026)**  
> **Project:** OmniAudit-GEO (`brand-ai-readiness-audit`)  
> **Standard:** `agentskills.io` Agent Skill Marketplace Standard & Anthropic Model Context Protocol (MCP)  
> **Team:** Shaswat Raj ([@sh20raj](https://github.com/sh20raj)) & Prithvi ([@chikolavosaki-sys](https://github.com/chikolavosaki-sys))  
> **Live Production Platform:** [https://omniaudit-geo.onrender.com/](https://omniaudit-geo.onrender.com/)  
> **Interactive Documentation Portal:** [https://omniaudit-geo.onrender.com/docs](https://omniaudit-geo.onrender.com/docs)  
> **GitHub Repository:** [https://github.com/SH20RAJ/omniaudit](https://github.com/SH20RAJ/omniaudit)  
> **Verified Package:** `omniaudit-geo-marketplace.zip` (0.09 MB / 69 verified files)

---

## 📌 Executive Summary

For 25 years, digital brand visibility was governed by traditional search engines and 10 blue links. In 2026, user discovery has fundamentally shifted to **Generative Answer Engines** (ChatGPT Search, Perplexity, Claude, Google AI Overviews).

Yet enterprise brands face a critical, multi-million dollar blindspot:
1. **Silent Exclusion from AI Citations:** Due to client-side hydration gaps, restrictive robots.txt policies, missing Schema.org disambiguation, and unquotable prose, AI models cannot accurately extract or cite brand facts.
2. **Post-Referral Drop-Off:** When generative search engines do refer visitors, poor above-the-fold value proposition clarity causes immediate bounce rates exceeding 70%.

**OmniAudit-GEO** is the industry's first open-standard, dual-axis brand audit engine evaluating:
* **ACPI (AI Citation Probability Index, 0–100):** Machine crawler accessibility, Schema.org entities, and atomic fact quotability.
* **CRS (Cognitive Retention Score, 0–100):** Above-the-fold value proposition clarity, reading ease, and conversion orientation.

Built from first principles with **100% Python standard library AST parsing**, OmniAudit-GEO requires **zero cloud LLM API keys**, runs locally in **0.4 ms**, enforces hardened **anti-SSRF security**, and integrates natively with **Adobe Experience Cloud** and modern AI agent IDEs (Cursor, Claude Desktop) via **Anthropic's Model Context Protocol (MCP)**.

---

## ⏱️ The 3-Minute Live Showcase Demo Script

*(This is the word-for-word, click-by-click live demonstration playbook for Round 4 jury evaluations).*

### [0:00 – 0:35] The Hook & Multibillion-Dollar Shift
* **Presenter 1 (Voice):**  
  *"Good morning, judges. In 2026, web traffic no longer starts with Google blue links—it starts with conversational answers from Perplexity, ChatGPT Search, and Claude.*  
  *Here is the dilemma: Brands spend millions on stunning digital presences, yet AI assistants routinely fail to cite them or hallucinate their products. And when referred users do land on the page, they bounce in under four seconds.*  
  *We built **OmniAudit-GEO** to solve both halves of this equation: **ACPI** for machine discoverability, and **CRS** for human visitor retention. Everything you are about to see is running live, open-source, and powered by a 100% deterministic local Python AST engine with zero paid cloud API dependencies."*

### [0:35 – 1:15] Demo 1: Master Brand Audit & 0.4ms Local AST
* **Presenter 2 (Screen Action):**  
  1. Open [https://omniaudit-geo.onrender.com](https://omniaudit-geo.onrender.com).
  2. In **Tab 1: ⚡ Master Brand Audit**, select preset `https://adobe.com` and click **🚀 Run Master Audit**.
  3. Show the instant metric cards: ACPI Score (89.4), CRS Score (92.0), Total Findings, and Engine Latency.
* **Presenter 1 (Voice):**  
  *"Notice the execution speed: in under a second over the live network, our streaming AST extractor parses HTML hierarchy, robots.txt bot rules, JSON-LD knowledge graph entities, and Flesch readability scores. When run offline on local fixtures, this engine executes in **0.4 milliseconds** per site.*  
  *Scroll down: the engine doesn't just output high-level scores; it isolates concrete diagnostic evidence—for example, missing `sameAs` Wikidata authority links, non-text asset quotation gaps, and semantic heading structure."*

### [1:15 – 1:50] Demo 2: Showstopper — The Interactive "What-If" Fix Simulator
* **Presenter 2 (Screen Action):**  
  1. Scroll down to **🔧 Interactive 'What-If' Fix Simulator (Impact Predictor)**.
  2. Check off 2 high/critical findings (e.g. `[HIGH] ENT-001` and `[MEDIUM] CRAWL-002`).
  3. Click **⚡ Re-calculate Projected Scores**.
  4. Show the visual comparison banner jumping: ACPI 89.4 ➔ 96.2 (+6.8 pts gain!).
* **Presenter 1 (Voice):**  
  *"Every audit tool tells you what's broken; OmniAudit-GEO predicts the exact mathematical ROI of fixing it.*  
  *Using our interactive **What-If Fix Simulator**, enterprise engineering teams and CMOs can simulate resolving individual defects. With one click, our scoring engine recalculates projected score lifts and grade transitions, giving developers an unambiguous roadmap of what will move the needle most."*

### [1:50 – 2:25] Demo 3: Live Competitor Head-to-Head Benchmark
* **Presenter 2 (Screen Action):**  
  1. Switch to **Tab 2: ⚔️ Competitor Benchmark**.
  2. Select preset `https://adobe.com` vs `https://canva.com`.
  3. Click **⚔️ Compare Head-to-Head**.
  4. Display the dynamic Winner Banner, side-by-side Scorecards, and comparative Dimension Matrix.
* **Presenter 1 (Voice):**  
  *"New for Round 4, our **Competitor Benchmark** lets brands compare their AI visibility directly against rivals.*  
  *Here we benchmark Adobe against Canva: the system evaluates AI Crawler permissions, Schema.org disambiguation, and visitor retention side-by-side, crowning a leader and generating automated tactical takeaways on where each brand has an advantage."*

### [2:25 – 2:50] Demo 4: Instant AI Remediation Prompt & MCP Agent Connectivity
* **Presenter 2 (Screen Action):**  
  1. Switch to **Tab 1: 🚀 AI Action Prompt & Export Center**.
  2. Show the **AI Remediation Prompt** box with its copy icon, and click **📥 Download Markdown Report**.
  3. Briefly open **Tab 6: 🔌 MCP & Agent Integration** showing the live JSON-RPC 2.0 endpoint (`/api/mcp`).
* **Presenter 1 (Voice):**  
  *"To close the loop from audit to remediation, we generate a structured **AI Fix Prompt** that engineers can copy directly into Cursor or Claude to automatically generate compliant robots.txt rules and Schema.org JSON-LD scripts.*  
  *Furthermore, through our Anthropic Model Context Protocol (MCP) server, autonomous AI coding agents can call OmniAudit-GEO tools natively via standard JSON-RPC 2.0."*

### [2:50 – 3:00] Wrap-up & Adobe Ecosystem Vision
* **Presenter 1 (Voice):**  
  *"OmniAudit-GEO is designed as a native pre-publish quality gate for **Adobe Experience Manager (AEM)** and an automated catalog enrichment engine for **Adobe Commerce**.*  
  *193 automated tests passing across 6 verification gates, 100% ground-truth precision on our 16 Golden Benchmarks, and zero external API dependencies. Thank you, and we welcome your questions!"*

---

## 🎯 5 Live Demonstration Scenarios for Round 4 Evaluators

| # | Demo Scenario | URL / Command | What Evaluators See | Key Technical Takeaway |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Master Brand Audit** | `https://adobe.com` in Tab 1 | Live ACPI & CRS badges, priority findings, AST evidence accordion. | Sub-second latency, zero LLM hallucinations, deterministic mathematical scores. |
| **2** | **"What-If" Impact Simulator** | Checkboxes in Tab 1 | Live recalculation card: Baseline ➔ Projected score with net gain. | Demonstrates business ROI before spending engineering hours on fixes. |
| **3** | **Competitor Head-to-Head** | `adobe.com` vs `canva.com` in Tab 2 | Winner banner, side-by-side scorecards, 5-dimension evaluation matrix. | Competitive positioning & enterprise CMO strategic intelligence. |
| **4** | **Anthropic MCP Tool Call** | Tab 6 Sandbox or Cursor | Live JSON-RPC 2.0 request & response payload for `audit_website`. | Drop-in AI agent interoperability complying with open standards. |
| **5** | **Offline Sandboxed CI Gate** | `python3 scripts/verify.py --ci` | 193 unit tests, 16 Golden Fixtures (100% precision), 0.4ms parser. | Fully air-gapped, zero cloud dependencies, verifiable in CI/CD pipelines. |

---

## 🏗️ Technical Architecture & Competitive Differentiation

### Architectural Topology

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 OmniAudit-GEO Web UI                   │
                  │   Gradio 6 Dark-Mode Interface + FastAPI 0.115 API      │
                  └───────────────────────────┬────────────────────────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              ▼                               ▼                               ▼
    ┌────────────────────┐          ┌────────────────────┐          ┌────────────────────┐
    │  ⚡ Master Audit   │          │  ⚔️ Competitor     │          │  🔌 Model Context  │
    │  Orchestrator      │          │  Benchmark Matchup │          │  Protocol (MCP)    │
    └─────────┬──────────┘          └─────────┬──────────┘          └─────────┬──────────┘
              │                               │                               │
              └───────────────────────────────┼───────────────────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │  🛡️ Guard Layer (audit_guard.py) │
                             │  Anti-SSRF · Rate Limiting · AST│
                             └────────────────┬────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
┌──────────────────┐                ┌──────────────────┐                 ┌──────────────────┐
│ crawl-render     │                │ structured-entity│                 │ aeo-quotability  │
│ (robots.txt, SPA)│                │ (JSON-LD, sameAs)│                 │ (atomic facts)   │
└──────────────────┘                └──────────────────┘                 └──────────────────┘
         │                                    │                                    │
         ▼                                    ▼                                    ▼
┌──────────────────┐                ┌──────────────────┐                 ┌──────────────────┐
│ freshness-trust  │                │ on-site-retention│                 │ scoring engine   │
│ (recency, byline)│                │ (CRS, readability│                 │ (ACPI/CRS bounds)│
└──────────────────┘                └──────────────────┘                 └──────────────────┘
```

### Feature Comparison Matrix

| Feature Dimension | Google Lighthouse | SEMrush / Ahrefs | Generic LLM Wrappers | **OmniAudit-GEO** |
| :--- | :---: | :---: | :---: | :---: |
| **Focus Axis** | Web Vitals / Performance | 10 Blue Links SEO | Unbounded Text Summary | **Dual: ACPI (GEO) + CRS (Retention)** |
| **Execution Engine** | Heavy Headless Chrome | Cloud Crawler Farm | OpenAI API Prompt | **Pure Python Local Streaming AST** |
| **Execution Latency** | 15,000 – 30,000 ms | Hours / Background | 5,000 – 15,000 ms | **0.4 ms (local) / 1,500 ms (network)** |
| **Cloud API Cost** | Free | $130 – $500/month | ~$0.05 per audit | **$0.00 (Zero external dependencies)** |
| **SSRF Security** | N/A (Client-side) | Proprietary cloud | Vulnerable to fetch injection | **Hardened (Blocks RFC 1918 & Cloud Metadata)** |
| **What-If Fix Simulator** | ❌ No | ❌ No | ❌ No | **✅ Yes (Live AST recalculation)** |
| **Competitor Matchup** | ❌ No | Partial (SEO only) | ❌ No | **✅ Yes (Side-by-side ACPI/CRS Matrix)** |
| **Agent Protocol (MCP)** | ❌ No | ❌ No | ❌ No | **✅ Yes (JSON-RPC 2.0 / 7 tools)** |
| **Marketplace Standard** | ❌ No | ❌ No | ❌ No | **✅ Yes (`agentskills.io` compliant)** |

---

## 💼 Adobe Product Ecosystem Integration Blueprint

```
                      ┌──────────────────────────────────────────────┐
                      │        Adobe Experience Cloud Ecosystem      │
                      └──────────────────────┬───────────────────────┘
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             ▼                               ▼                               ▼
   ┌────────────────────┐          ┌────────────────────┐          ┌────────────────────┐
   │  Adobe Experience  │          │   Adobe Commerce   │          │    Adobe Target    │
   │   Manager (AEM)    │          │  (Magento Catalog) │          │  (Personalization) │
   └─────────┬──────────┘          └─────────┬──────────┘          └─────────┬──────────┘
             │                               │                               │
             ▼                               ▼                               ▼
    Pre-Publish Gate                Catalog Schema Audit            Retention Optimizer
   Blocks publishing of            Validates Product JSON-LD,      Uses CRS heuristics to
   pages with robots crawl         Wikidata sameAs links, and      A/B test hero value props
   blocks or missing schema        atomic product specifications   and reduce referral bounce
```

### 1. Adobe Experience Manager (AEM) — Pre-Publish Quality Gate
* **Problem:** Marketing teams publish landing pages with broken client-side hydration, missing OpenGraph cards, or accidental `Disallow: /` directives that take weeks to detect.
* **OmniAudit-GEO Solution:** Implemented as an automated Cloud Manager pipeline build step or pre-publish workflow hook. If ACPI < 80.0 or critical crawl blocks are present, the deployment triggers an alert with the exact AST remediation before publication.

### 2. Adobe Commerce (Magento) — AI Merchant Discovery
* **Problem:** In conversational commerce (e.g. asking ChatGPT "Where can I buy eco-friendly running shoes under $150?"), stores without rich `Product` Schema.org microdata and structured attributes are completely omitted.
* **OmniAudit-GEO Solution:** Automated background crawler scanning merchant product catalogs, verifying `PriceSpecification`, `availability`, and `sameAs` brand entities to maximize conversational search conversion.

### 3. Adobe Target — Automated Hero Fold Personalization
* **Problem:** Visitors arriving from generative search referrals expect immediate answer continuity, but traditional landing pages present generic corporate slogans.
* **OmniAudit-GEO Solution:** Feeds CRS orientation and readability scores into Adobe Target to automatically A/B test hero headlines, high-contrast CTAs, and semantic introductory summaries tailored for AI-referred cohorts.

---

## 🛡️ Round 4 Tough Questions & Jury Defense Playbook

### Q1: "Why did you build your own AST heuristic engine instead of just asking GPT-4 to audit the website?"
* **Defense:**
  1. **Determinism & Reproducibility:** LLM prompts produce variable outputs across runs, hallucinate non-existent issues, and cannot guarantee mathematical bounds. Our AST engine evaluates exact DOM nodes, heading depth trees, and JSON-LD schemas deterministically.
  2. **Sub-Millisecond Latency:** Our local AST parser processes a full page in **0.4 milliseconds**, compared to 8–15 seconds for an LLM API roundtrip.
  3. **Air-Gapped Privacy & Zero Cost:** Enterprise brands cannot transmit proprietary intranet or staging HTML to public LLM endpoints. Our engine executes 100% offline with zero cloud API costs.
  4. **The LLM is the Target, Not the Auditor:** In GEO, our goal is to measure how generative engines perceive the page. Using an LLM to evaluate itself introduces circular bias.

### Q2: "How does your What-If Fix Simulator work mathematically without running a whole new audit?"
* **Defense:**
  * Core diagnostic findings are decoupled from raw HTML fetching. When the user checks off resolved items, the simulator dynamically filters the finding list and invokes canonical `compute_scores(remaining_findings)`.
  * The scoring engine re-applies category-specific deduplication damping (50% damping for shared root causes) and mathematical bounds ($\text{ACPI} \in [5, 100], \text{CRS} \in [10, 100]$), computing exact projected score lifts instantly with zero network overhead.

### Q3: "What prevents malicious actors from using your tool for SSRF attacks against internal infrastructure?"
* **Defense:**
  * Our `safe_fetch.py` and `audit_guard.py` layers implement a multi-tiered security perimeter:
    1. **DNS Pre-Flight Resolution:** Resolves the hostname before issuing HTTP requests.
    2. **Private IP & Loopback Blacklist:** Strictly blocks RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), link-local (`169.254.0.0/16`), and IPv6 equivalents.
    3. **Cloud Metadata Defense:** Explicitly blocks AWS/GCP/Azure instance metadata endpoints (`169.254.169.254`).
    4. **Hop-by-Hop Redirect Validation:** Every HTTP redirect (max 5 hops) is re-validated against the IP blacklist before following.
    5. **Hard Payload Capping:** Enforces a 5 MB payload limit and 10-second timeout to mitigate memory exhaustion and Slowloris attacks.

### Q4: "How do you avoid penalizing modern Single Page Applications (SPAs) like React or Next.js that have valid client-side hydration?"
* **Defense:**
  * We built dedicated **False Positive Guards** (verified in Golden Fixtures #4 `large_state_static` and #5 `app_router`):
    * The engine inspects inline server-rendered state (`__NEXT_DATA__`, `window.__INITIAL_STATE__`, `<script type="application/json">`).
    * If meaningful text content or state payloads are present, the page is recognized as server-rendered or pre-rendered, avoiding false hydration penalties.
    * Only empty shell templates (e.g. `<div id="root"></div>` with under 50 words of static content) trigger the `CRAWL-HYDRATION-GAP` finding.

### Q5: "How does the Model Context Protocol (MCP) benefit an AI coding agent?"
* **Defense:**
  * MCP is the open standard created by Anthropic to connect AI models with external tools.
  * Rather than copying and pasting website URLs into web browsers, an agent in Cursor or Claude Desktop can directly invoke `audit_website(url="https://example.com")`.
  * The agent receives structured JSON findings and can immediately write code to fix the detected issues (e.g. creating the missing JSON-LD schema or editing `robots.txt`) in a single autonomous feedback loop.

---

## 🛟 Emergency Demo Fallback Runbook

| Scenario | Primary Cause | Instant Recovery Action |
| :--- | :--- | :--- |
| **Wi-Fi / Internet Outage on Stage** | Venue network failure | Run the CLI offline demo: `python3 cli.py benchmark` (demonstrates all 16 golden fixtures in 8ms with zero internet connection). |
| **Target Website Blocks Bot (403/Cloudflare)** | Aggressive WAF on live URL | Immediately switch to fallback preset: `https://example.com` or `https://httpbin.org`. |
| **Render Container Cold Start** | Render free tier spin-up delay | Platform is pre-warmed via automated health-check pingers; keep a local instance running on `localhost:7860` (`python3 omniaudit-geo/main.py`) as hot backup. |
| **Judge Asks for Arbitrary Website** | Live unplanned test | Run the live audit on the judge's chosen URL; our guarded fetch handles any public website safely in ~1.5 seconds. |

---

*Authored by Shaswat Raj & Prithvi · Adobe University Hackathon 2026*
