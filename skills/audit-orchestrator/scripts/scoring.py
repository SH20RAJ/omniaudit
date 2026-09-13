"""
Deterministic, Component-Based Scoring Engine for OmniAudit-GEO.

Computes:
1. ACPI (AI Citation Probability Index, 0.0 - 100.0):
   Measures off-site search engine and generative assistant discoverability.
   Formula: ACPI = (0.30 * crawlability) + (0.15 * renderability) +
                   (0.20 * entity_clarity) + (0.20 * quotability) +
                   (0.15 * trust_freshness)

2. CRS (Cognitive Retention Score, 0.0 - 100.0):
   Measures on-site visitor orientation and conversion readiness post-referral.
   Formula: CRS = (0.35 * orientation) + (0.25 * intent_continuity) +
                  (0.20 * readability) + (0.20 * actionability)

Invariants:
- Clamped between 0.0 and 100.0 (baseline floor 5.0 for ACPI, 10.0 for CRS).
- Root-cause grouping prevents double-deductions for equivalent findings.
- Low confidence findings have proportionally reduced impact.
- Proactive recommendations have zero penalty impact.
"""

from typing import Any

ACPI_WEIGHTS = {
    "crawlability": 0.30,
    "renderability": 0.15,
    "entity_clarity": 0.20,
    "quotability": 0.20,
    "trust_freshness": 0.15,
}

CRS_WEIGHTS = {
    "orientation": 0.35,
    "intent_continuity": 0.25,
    "readability": 0.20,
    "actionability": 0.20,
}

CATEGORY_MAP = {
    # Crawl & Render
    "crawlability_ai_permissions": ("acpi", "crawlability", "robots"),
    "crawlability_headers": ("acpi", "crawlability", "headers"),
    "crawlability_network": ("acpi", "crawlability", "network"),
    "crawlability_hydration": ("acpi", "renderability", "hydration"),
    # Structured Entity
    "structured_data_entity": ("acpi", "entity_clarity", "schema_org"),
    "structured_data_syntax": ("acpi", "entity_clarity", "syntax"),
    "structured_data_disambiguation": ("acpi", "entity_clarity", "sameas"),
    "structured_data_corroboration": ("acpi", "entity_clarity", "sameas"),
    "structured_entity": ("acpi", "entity_clarity", "schema_org"),
    # AEO Quotability
    "quotability_atomic_facts": ("acpi", "quotability", "atomic_facts"),
    "quotability_headings": ("acpi", "quotability", "qa_headings"),
    "non_text_assets": ("acpi", "quotability", "non_text"),
    "aeo_non_text_facts": ("acpi", "quotability", "non_text"),
    "aeo_heading_structure": ("acpi", "quotability", "qa_headings"),
    "aeo_quotability": ("acpi", "quotability", "atomic_facts"),
    # Freshness & Trust
    "freshness_temporal": ("acpi", "trust_freshness", "timestamps"),
    "freshness_temporal_signals": ("acpi", "trust_freshness", "timestamps"),
    "authority_corroboration": ("acpi", "trust_freshness", "byline"),
    "freshness_trust": ("acpi", "trust_freshness", "timestamps"),
    # On-Site Engagement
    "engagement_orientation": ("crs", "orientation", "hero"),
    "engagement_intent": ("crs", "intent_continuity", "intent"),
    "paywall_gate": ("crs", "intent_continuity", "paywall"),
    "engagement_readability": ("crs", "readability", "flesch_kincaid"),
    "engagement_cognitive_load": ("crs", "readability", "cognitive_load"),
    "engagement_action_clarity": ("crs", "actionability", "cta"),
    "engagement_form_accessibility": ("crs", "actionability", "forms"),
    "on_site_retention": ("crs", "orientation", "hero"),
}

SEVERITY_DEDUCTION = {
    "critical": 30.0,
    "high": 15.0,
    "medium": 8.0,
    "low": 3.0,
}

CONFIDENCE_MULTIPLIER = {
    "high": 1.0,
    "medium": 0.7,
    "low": 0.4,
}

CATEGORY_MAX_DEDUCTION = {
    "crawlability": 70.0,
    "renderability": 70.0,
    "entity_clarity": 60.0,
    "quotability": 60.0,
    "trust_freshness": 55.0,
    "orientation": 60.0,
    "intent_continuity": 60.0,
    "readability": 50.0,
    "actionability": 50.0,
}


def compute_scores(
    findings: list[dict[str, Any]],
    measurements: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Computes bounded, explainable ACPI and CRS scores.
    Derives baseline component scores from empirical AST/DOM measurements,
    and applies calibrated deductions with root-cause capping to prevent penalty accumulation.
    """
    component_deductions: dict[str, float] = {
        "crawlability": 0.0,
        "renderability": 0.0,
        "entity_clarity": 0.0,
        "quotability": 0.0,
        "trust_freshness": 0.0,
        "orientation": 0.0,
        "intent_continuity": 0.0,
        "readability": 0.0,
        "actionability": 0.0,
    }

    # Group deductions by root cause to prevent duplicate double-penalties
    seen_causes: dict[str, float] = {}

    for f in findings:
        severity = str(f.get("severity", "medium")).lower()
        if severity not in SEVERITY_DEDUCTION:
            continue  # info or unknown severity does not penalize score

        category = str(f.get("category", "")).lower()
        mapping = CATEGORY_MAP.get(category)
        if not mapping:
            # Default fallback mapping
            if "crawl" in category or "robot" in category:
                mapping = ("acpi", "crawlability", "crawl")
            elif "schema" in category or "entity" in category:
                mapping = ("acpi", "entity_clarity", "entity")
            elif "fresh" in category or "trust" in category:
                mapping = ("acpi", "trust_freshness", "freshness")
            elif "read" in category or "engage" in category or "hero" in category:
                mapping = ("crs", "orientation", "engagement")
            else:
                mapping = ("acpi", "quotability", "quotability")

        _, component, root_cause = mapping
        base_ded = SEVERITY_DEDUCTION[severity]
        conf = str(f.get("confidence", "high")).lower()
        conf_mult = CONFIDENCE_MULTIPLIER.get(conf, 1.0)
        net_ded = base_ded * conf_mult

        # Root cause capping: subsequent findings for same root cause have 50% diminishing impact
        cause_key = f"{component}:{root_cause}"
        if cause_key in seen_causes:
            effective_ded = net_ded * 0.5
        else:
            effective_ded = net_ded
            seen_causes[cause_key] = net_ded

        component_deductions[component] += effective_ded

    # Derive baseline component scores from empirical measurements if provided
    base_scores: dict[str, float] = {
        "crawlability": 100.0,
        "renderability": 100.0,
        "entity_clarity": 100.0,
        "quotability": 100.0,
        "trust_freshness": 100.0,
        "orientation": 100.0,
        "intent_continuity": 100.0,
        "readability": 100.0,
        "actionability": 100.0,
    }

    if measurements:
        # Entity Clarity: Schema.org richness, sameAs authority
        json_ld_count = measurements.get("json_ld_count", 0)
        has_sameas = measurements.get("has_sameas", False)
        base_entity = 75.0
        if json_ld_count > 0:
            base_entity += min(15.0, json_ld_count * 10.0)
        if has_sameas:
            base_entity += 10.0
        base_scores["entity_clarity"] = min(100.0, base_entity)

        # Quotability: factual density, direct Q&A blocks, table accessibility
        facts_count = measurements.get("facts_count", 0)
        words_count = max(1, measurements.get("words_count", 1))
        fact_density = facts_count / (words_count / 100.0)
        base_quotability = 70.0 + min(20.0, fact_density * 4.0)
        faq_pairs = measurements.get("faq_pairs", 0) or 0
        if faq_pairs > 0:
            base_quotability += min(10.0, faq_pairs * 5.0)
        base_scores["quotability"] = min(100.0, base_quotability)

        # Orientation: clear H1 structure, meta description presence
        base_orientation = 75.0
        if measurements.get("h1_count", 0) == 1:
            base_orientation += 15.0
        if measurements.get("has_meta_desc", False):
            base_orientation += 10.0
        base_scores["orientation"] = min(100.0, base_orientation)

        # Actionability: presence of usable forms, clear CTAs
        strong_ctas = measurements.get("strong_cta_count", 0)
        forms_count = measurements.get("form_count", 0)
        base_action = 75.0 + min(15.0, strong_ctas * 7.5) + min(10.0, forms_count * 5.0)
        base_scores["actionability"] = min(100.0, base_action)

    # Compute capped component scores
    component_scores: dict[str, float] = {}
    for comp, ded in component_deductions.items():
        base_val = base_scores.get(comp, 100.0)
        max_cap = CATEGORY_MAX_DEDUCTION.get(comp, 60.0)
        capped_ded = min(ded, max_cap)
        component_scores[comp] = round(max(0.0, base_val - capped_ded), 1)

    # Compute composite ACPI
    acpi_raw = sum(component_scores[comp] * weight for comp, weight in ACPI_WEIGHTS.items())
    acpi_score = round(max(5.0, min(100.0, acpi_raw)), 1)

    # Compute composite CRS
    crs_raw = sum(component_scores[comp] * weight for comp, weight in CRS_WEIGHTS.items())
    crs_score = round(max(10.0, min(100.0, crs_raw)), 1)

    return {
        "acpi_score": acpi_score,
        "crs_score": crs_score,
        "component_scores": component_scores,
    }
