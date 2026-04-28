"""Cross-validation - every claim needs >=2 independent sources.

Bayesian weak-signal chaining: 3 weak corroborations (0.3 each) combine
to ~0.66, matching master-investigator heuristics.
"""

from __future__ import annotations

import re
from typing import Any

from ..sources.base import Record


def _combine(confidences: list[float]) -> float:
    # complement-product: 1 - prod(1 - c_i)
    p = 1.0
    for c in confidences:
        p *= 1.0 - max(0.0, min(1.0, c))
    return 1.0 - p


def extract_claims(records: list[Record]) -> list[dict[str, Any]]:
    """Heuristic claim extraction: tokenized noun-phrase-ish shingles.

    For each record we generate claim candidates by splitting on sentence-ish
    delimiters and keeping 4-12 word chunks that look assertive.
    """
    claims: list[dict] = []
    for r in records:
        for chunk in re.split(r"(?<=[.!?])\s+|\s\|\s|\n+", r.content):
            chunk = chunk.strip(" ·-\t")
            words = chunk.split()
            if not (4 <= len(words) <= 35):
                continue
            claims.append(
                {
                    "text": chunk,
                    "source": r.source,
                    "authority": r.authority,
                    "confidence": r.confidence,
                    "url": r.url,
                }
            )
    return claims


def _similar(a: str, b: str) -> float:
    aw = set(w.lower() for w in re.findall(r"[a-zA-Z0-9]{3,}", a))
    bw = set(w.lower() for w in re.findall(r"[a-zA-Z0-9]{3,}", b))
    if not aw or not bw:
        return 0.0
    return len(aw & bw) / len(aw | bw)


def _source_key(s: str) -> str:
    # "seed:wikipedia" -> "wikipedia"; "wikipedia" -> "wikipedia"; "web" -> "web"
    parts = s.split(":", 1)
    return (parts[1] if len(parts) == 2 else parts[0]).strip().lower()


def corroborate(claims: list[dict[str, Any]], threshold: float = 0.35) -> list[dict[str, Any]]:
    """Cluster similar claims across sources, produce combined confidence."""
    clusters: list[dict] = []
    for cl in claims:
        placed = False
        for c in clusters:
            if _similar(cl["text"], c["representative"]) >= threshold:
                c["variants"].append(cl)
                c["sources"].add(_source_key(cl["source"]))
                placed = True
                break
        if not placed:
            clusters.append(
                {
                    "representative": cl["text"],
                    "variants": [cl],
                    "sources": {_source_key(cl["source"])},
                }
            )
    out: list[dict] = []
    for c in clusters:
        confs = [v["confidence"] * (0.5 + 0.5 * v["authority"]) for v in c["variants"]]
        combined = _combine(confs)
        out.append(
            {
                "claim": c["representative"],
                "source_count": len(c["sources"]),
                "sources": sorted(c["sources"]),
                "combined_confidence": round(combined, 3),
                "corroborated": len(c["sources"]) >= 2,
                "urls": list({v["url"] for v in c["variants"] if v.get("url")}),
            }
        )
    out.sort(key=lambda x: (x["corroborated"], x["combined_confidence"]), reverse=True)
    return out
