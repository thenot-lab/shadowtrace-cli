"""Entity resolution - cluster records that refer to the same real subject.

Two-stage:
  1. Probabilistic: name/handle/email/domain similarity scoring
  2. Deterministic lock: email OR github-login exact match collapses cluster

Output: list of clusters, each with canonical_key, confidence, member records.
"""
from __future__ import annotations
import re, hashlib
from typing import List, Dict, Any
from difflib import SequenceMatcher
from ..sources.base import Record


EMAIL = re.compile(r"[\w.\-+]+@[\w\-]+\.[\w\-.]+")
HANDLE = re.compile(r"(?:^|\s|/)@?([a-zA-Z0-9][a-zA-Z0-9\-_]{1,38})")
URL_DOMAIN = re.compile(r"https?://(?:www\.)?([^/\s]+)")


def _extract_ids(r: Record) -> Dict[str, set]:
    blob = f"{r.subject_hint}\n{r.content}\n{r.url or ''}\n{r.meta}"
    return {
        "emails": set(m.group(0).lower() for m in EMAIL.finditer(blob)),
        "handles": set(m.group(1).lower() for m in HANDLE.finditer(blob) if len(m.group(1)) >= 3),
        "domains": set(m.group(1).lower() for m in URL_DOMAIN.finditer(blob)),
    }


def _name_sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def resolve(records: List[Record], primary_query: str) -> List[Dict[str, Any]]:
    clusters: list[dict] = []
    for r in records:
        ids = _extract_ids(r)
        # deterministic: match by email or github login
        matched = None
        for c in clusters:
            if ids["emails"] & c["ids"]["emails"]:
                matched = c; break
            gh_login = r.meta.get("login")
            if gh_login and gh_login.lower() in c["ids"]["handles"]:
                matched = c; break
            # name similarity > 0.85 and overlapping domain
            if _name_sim(primary_query, r.subject_hint) > 0.5:
                if _name_sim(c["canonical_name"], r.subject_hint) > 0.8 or (ids["domains"] & c["ids"]["domains"]):
                    matched = c; break
        if matched is None:
            clusters.append({
                "cluster_id": hashlib.sha1(r.subject_hint.encode()).hexdigest()[:10],
                "canonical_name": r.subject_hint,
                "ids": {k: set(v) for k, v in ids.items()},
                "records": [r],
            })
        else:
            for k, v in ids.items():
                matched["ids"][k] |= v
            matched["records"].append(r)

    # score each cluster by source diversity + authority
    for c in clusters:
        sources = set()
        for r in c["records"]:
            parts = r.source.split(":", 1)
            sources.add(parts[1] if len(parts) == 2 else parts[0])
        avg_auth = sum(r.authority for r in c["records"]) / max(1, len(c["records"]))
        c["source_diversity"] = len(sources)
        c["confidence"] = min(0.99, 0.3 + 0.1 * len(sources) + 0.4 * avg_auth)
        c["ids"] = {k: sorted(list(v)) for k, v in c["ids"].items()}

    clusters.sort(key=lambda c: (c["source_diversity"], len(c["records"])), reverse=True)
    return clusters
