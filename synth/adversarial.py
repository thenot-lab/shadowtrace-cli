"""Adversarial verification + red-team inversion.

Master-investigator techniques:
  1. For every strong claim, generate "how is this wrong?" counter-hypotheses
  2. Red-team from subject's view: what would they want hidden? flag if absent.
  3. Negative-space analysis: what's NOT present that should be?
"""
from __future__ import annotations
import re
from typing import List, Dict, Any


SHOULD_EXIST = {
    "public_executive": ["wikipedia_presence", "news_coverage", "company_affiliation"],
    "academic": ["publications", "institution", "citation_trail"],
    "technical": ["github_or_equivalent", "talks_or_posts"],
    "general": ["any_primary_source", "temporal_footprint"],
}


def counter_hypothesize(claim: str) -> List[str]:
    """Given a claim, generate contradicting hypotheses to search for."""
    low = claim.lower()
    out: list[str] = []
    if " ceo " in f" {low} " or "founder" in low:
        out.append("Former role rather than current - check exit date")
        out.append("Co-founder or interim, not primary")
    if re.search(r"\b(19|20)\d{2}\b", low):
        out.append("Year refers to unrelated event in same subject's timeline")
    if "based in" in low or "lives in" in low:
        out.append("Past residence, not current")
    if "university of" in low or "school" in low:
        out.append("Visiting / affiliated, not faculty")
    if not out:
        out.append("Claim is a reference, not about this subject (homograph risk)")
    return out


def negative_space(profile: Dict[str, Any], claims: List[Dict[str, Any]], source_types_seen: set) -> Dict[str, Any]:
    """What's missing that should be present for this subject archetype."""
    archetype = _guess_archetype(profile, claims)
    expected = SHOULD_EXIST.get(archetype, SHOULD_EXIST["general"])
    gaps: list[str] = []
    have_wiki = "wikipedia" in source_types_seen
    have_gh = "github" in source_types_seen
    have_news = any("news" in s for s in source_types_seen) or any("news" in (c.get("claim","").lower()) for c in claims)

    if "wikipedia_presence" in expected and not have_wiki:
        gaps.append("No Wikipedia article surfaced for a subject archetype that usually has one.")
    if "github_or_equivalent" in expected and not have_gh:
        gaps.append("No GitHub footprint for a technical subject.")
    if "news_coverage" in expected and not have_news:
        gaps.append("No news coverage surfaced for a public-executive archetype.")
    if not profile.get("year_footprint"):
        gaps.append("Zero temporal anchors - no dates anywhere in record set.")
    if profile.get("record_count", 0) < 3:
        gaps.append("Record count under 3 - too sparse to triangulate.")

    return {
        "guessed_archetype": archetype,
        "expected_signals": expected,
        "gaps": gaps,
        "interpretation": _interpret(gaps),
    }


def _guess_archetype(profile: Dict[str, Any], claims: List[Dict[str, Any]]) -> str:
    blob = " ".join([c.get("claim", "") for c in claims]).lower()
    blob += " " + " ".join(t for t, _ in profile.get("top_titles", []))
    if any(w in blob for w in ("ceo", "founder", "president", "executive")):
        return "public_executive"
    if any(w in blob for w in ("professor", "phd", "researcher", "university")):
        return "academic"
    if any(w in blob for w in ("engineer", "developer", "architect", "technical")):
        return "technical"
    return "general"


def _interpret(gaps: list[str]) -> str:
    if not gaps:
        return "Record set is proportional to archetype expectation."
    if len(gaps) >= 3:
        return "Substantial negative space - either under-searched, wrong subject, or deliberately low-profile."
    return "Minor gaps - consider one more search pass on the missing surfaces before closing."


def red_team(profile: Dict[str, Any]) -> List[str]:
    """What would the subject want hidden that we should look for?"""
    out: list[str] = []
    if profile.get("top_orgs"):
        out.append("Prior employers during gap years - check LinkedIn-class sources.")
    if profile.get("top_titles"):
        out.append("Title inflation - cross-check with authoritative filings (SEC, company registry).")
    out.append("Address-of-record vs claimed location - public voter / property records.")
    out.append("Litigation or regulatory actions - court record and regulator databases.")
    out.append("Alternate handles / spellings - typosquat variants, prior names.")
    return out
