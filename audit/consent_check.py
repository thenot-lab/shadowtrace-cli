"""GDPR / consent-tier enforcement.

Tiers:
  public_only        - anyone, public sources only
  manifestly_public  - EU subjects, Article 9(2)(e) spirit
  consented          - subject signed off, deep profile
"""
from __future__ import annotations
import re
from typing import Dict

EU_TLDS = {
    ".de", ".fr", ".it", ".es", ".nl", ".be", ".at", ".dk", ".se", ".fi",
    ".pl", ".cz", ".ie", ".pt", ".gr", ".hu", ".ro", ".bg", ".hr", ".sk",
    ".si", ".lt", ".lv", ".ee", ".lu", ".mt", ".cy", ".eu",
}
EU_COUNTRIES = {
    "germany", "france", "italy", "spain", "netherlands", "belgium",
    "austria", "denmark", "sweden", "finland", "poland", "czech", "ireland",
    "portugal", "greece", "hungary", "romania", "bulgaria", "croatia",
    "slovakia", "slovenia", "lithuania", "latvia", "estonia", "luxembourg",
    "malta", "cyprus", "uk", "united kingdom", "britain",
}
SENSITIVE_CATEGORY_PATTERNS = [
    re.compile(r"\b(religion|religious|christian|muslim|jewish|hindu|buddhist|atheist|catholic|protestant)\b", re.I),
    re.compile(r"\b(democrat|republican|liberal|conservative|left-wing|right-wing|communist|socialist)\b", re.I),
    re.compile(r"\b(hiv|cancer|diabetes|mental health|depression|anxiety|disability|medication)\b", re.I),
    re.compile(r"\b(gay|lesbian|bisexual|transgender|lgbtq)\b", re.I),
    re.compile(r"\b(trade union|union member)\b", re.I),
]


def detect_eu(subject_text: str) -> bool:
    s = (subject_text or "").lower()
    if any(tld in s for tld in EU_TLDS):
        return True
    return any(c in s for c in EU_COUNTRIES)


def classify_tier(subject_text: str, explicit_consent: bool = False) -> str:
    if explicit_consent:
        return "consented"
    if detect_eu(subject_text):
        return "manifestly_public"
    return "public_only"


def redact_sensitive(text: str, enabled: bool = True) -> tuple[str, list[str]]:
    if not enabled or not text:
        return text, []
    hits: list[str] = []
    out = text
    for pat in SENSITIVE_CATEGORY_PATTERNS:
        m = pat.search(out)
        if m:
            hits.append(m.group(0))
            out = pat.sub("[REDACTED:sensitive-category]", out)
    return out, hits


def evaluate(subject_text: str, cfg: Dict) -> Dict:
    consent = bool(cfg.get("consent", {}).get("explicit", False))
    tier = classify_tier(subject_text, consent)
    return {
        "tier": tier,
        "eu_subject": detect_eu(subject_text),
        "sensitive_redact": bool(cfg.get("consent", {}).get("sensitive_category_auto_redact", True)),
        "notes": "Article 9(2)(e) manifestly-public-only" if tier == "manifestly_public" else None,
    }
