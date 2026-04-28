"""Evidence chains - adapted from v6 ShadowTraceAgentUpgrade pattern.

Given corroborated claims, link them into directed evidence graphs where
each node is a claim and edges are shared-source / entity co-mentions.
Output is a ranked list of chains with chain-level confidence.
"""

from __future__ import annotations

import re
from typing import Any


def _shared_sources(a: dict, b: dict) -> list[str]:
    return sorted(set(a.get("sources", [])) & set(b.get("sources", [])))


def _entity_overlap(a: str, b: str) -> int:
    aw = set(w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", a))
    bw = set(w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", b))
    return len(aw & bw)


def build_chains(
    corroborated: list[dict[str, Any]], min_chain_len: int = 2, max_chains: int = 10
) -> list[dict[str, Any]]:
    verified = [c for c in corroborated if c.get("corroborated")]
    chains: list[dict[str, Any]] = []
    used: set[int] = set()

    for i, anchor in enumerate(verified):
        if i in used:
            continue
        chain = [anchor]
        used.add(i)
        for j, cand in enumerate(verified):
            if j in used:
                continue
            shared = _shared_sources(anchor, cand)
            overlap = _entity_overlap(anchor["claim"], cand["claim"])
            if shared and overlap >= 2:
                chain.append(cand)
                used.add(j)
        if len(chain) >= min_chain_len:
            confs = [c["combined_confidence"] for c in chain]
            chain_conf = 1.0
            for c in confs:
                chain_conf *= 1.0 - max(0.0, min(1.0, c))
            chain_conf = 1.0 - chain_conf
            all_sources: set[str] = set()
            for c in chain:
                all_sources.update(c.get("sources", []))
            chains.append(
                {
                    "length": len(chain),
                    "confidence": round(chain_conf, 3),
                    "sources": sorted(all_sources),
                    "claims": [c["claim"][:180] for c in chain],
                }
            )

    chains.sort(key=lambda c: (c["length"], c["confidence"]), reverse=True)
    return chains[:max_chains]
