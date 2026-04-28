"""Behavioral synthesis - rule-based profile assembly with LLM-swap hook.

If an ANTHROPIC_API_KEY is present in env, deep synthesis can upgrade to
Claude Opus 4.7 with Task Budgets (future). Default path is fully local:
no LLM dependency, deterministic, auditable.
"""

from __future__ import annotations

import os
import re
from collections import Counter
from typing import Any

from ..sources.base import Record

TITLES = re.compile(
    r"\b(CEO|CTO|CFO|COO|Founder|Co-founder|President|Director|Manager|Lead|Head|VP|Senior|Principal|Engineer|Researcher|Scientist|Analyst|Journalist|Editor|Professor|PhD|Author|Investigator)\b"
)
ORG_HINTS = re.compile(
    r"\b(?:at|of|@)\s+([A-Z][A-Za-z0-9&\- ]{2,40}?)(?=[.,;!?\n]|\s+(?:and|for|in|on|the|which|where|who|that|he|she|they|a |an )|$)"
)
YEAR = re.compile(r"\b(19|20)\d{2}\b")
LOCATION_HINTS = re.compile(r"\b(?:based in|lives in|from|located in)\s+([A-Z][A-Za-z ,.\-]{2,40})")


def _pick_top(items: list[str], n: int = 5) -> list[tuple[str, int]]:
    return Counter(items).most_common(n)


def assemble(records: list[Record], subject_query: str) -> dict[str, Any]:
    titles: list[str] = []
    orgs: list[str] = []
    years: list[str] = []
    locations: list[str] = []
    links: list[str] = []
    bio_chunks: list[str] = []

    for r in records:
        titles.extend(m.group(0) for m in TITLES.finditer(r.content))
        orgs.extend(m.group(1).strip(".,") for m in ORG_HINTS.finditer(r.content))
        years.extend(m.group(0) for m in YEAR.finditer(r.content))
        locations.extend(m.group(1).strip(".,") for m in LOCATION_HINTS.finditer(r.content))
        if r.url:
            links.append(r.url)
        if r.kind in {"bio", "profile", "page"} and len(r.content) > 60:
            bio_chunks.append(r.content[:600])

    # dedupe orgs - strip trailing connectors, collapse substring matches
    cleaned: list[str] = []
    for o in orgs:
        tok = o.strip(" .,:;")
        for stop in (" . ", ". ", "Writes on", "where", "which", "who"):
            if stop in tok:
                tok = tok.split(stop, 1)[0].strip(" .,:;")
        if len(tok) >= 3:
            cleaned.append(tok)
    # substring collapse: keep shortest canonical form when longer variants contain it
    cleaned.sort(key=len)
    dedup_orgs: list[str] = []
    seen_low: list[str] = []
    for o in cleaned:
        low = o.lower()
        if any(low == s or low.startswith(s + " ") or s in low for s in seen_low):
            continue
        seen_low.append(low)
        dedup_orgs.append(o)

    return {
        "subject_query": subject_query,
        "top_titles": _pick_top(titles, 5),
        "top_orgs": _pick_top(dedup_orgs, 8),
        "year_footprint": sorted(set(years)),
        "top_locations": _pick_top(locations, 3),
        "links": sorted(set(links)),
        "bio_excerpt": bio_chunks[0] if bio_chunks else "",
        "record_count": len(records),
        "source_breakdown": Counter(
            (r.source.split(":", 1)[1] if ":" in r.source else r.source) for r in records
        ),
        "llm_upgrade_available": bool(os.environ.get("ANTHROPIC_API_KEY")),
    }


def interaction_guide(profile: dict[str, Any], tier: str) -> list[str]:
    """Recommendations for engagement, tier-gated."""
    out: list[str] = []
    if profile["top_titles"]:
        top = profile["top_titles"][0][0]
        out.append(
            f"Lead title is {top}: frame first contact around peer-level value, not introduction."
        )
    if profile["top_orgs"]:
        org = profile["top_orgs"][0][0]
        out.append(
            f"Primary affiliation appears to be {org}: reference their current work, not past."
        )
    if profile["top_locations"]:
        loc = profile["top_locations"][0][0]
        out.append(f"Timezone / region hint: {loc}. Send outreach in their business hours.")
    if tier == "manifestly_public":
        out.append(
            "EU subject: GDPR manifestly-public tier - no sensitive categories in outbound messaging."
        )
    if not profile["top_orgs"] and not profile["top_titles"]:
        out.append(
            "Sparse signal: request explicit intro or warm connection before direct outreach."
        )
    return out
