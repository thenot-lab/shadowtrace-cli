"""Pivot chains - depth-3 entity expansion from primary subject.

Given the primary cluster's extracted entities (orgs, people, domains),
propose next-hop search queries. Depth-3 only executes if user confirms,
because it expands the investigation surface exponentially.
"""

from __future__ import annotations

import re
from typing import Any

from ..sources.base import Record

PERSON = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b")
DOMAIN = re.compile(r"\b([a-z0-9\-]+\.(?:com|org|net|io|co|uk|ca|edu|gov|ai|dev))\b")


def extract_entities(records: list[Record]) -> dict[str, list[str]]:
    people: set[str] = set()
    domains: set[str] = set()
    for r in records:
        for m in PERSON.finditer(r.content):
            name = m.group(1)
            if len(name.split()) >= 2:
                people.add(name)
        for m in DOMAIN.finditer(r.content.lower()):
            domains.add(m.group(1))
    return {"people": sorted(people)[:25], "domains": sorted(domains)[:25]}


def propose_pivots(
    primary_query: str,
    records: list[Record],
    confirmed_orgs: list[str] | None = None,
    depth: int = 1,
) -> list[dict[str, Any]]:
    """Return list of pivot suggestions. depth=1 is always safe to display.
    depth >= 2 requires explicit operator confirmation before execution.
    """
    ents = extract_entities(records)
    confirmed_orgs = confirmed_orgs or []
    pivots: list[dict[str, Any]] = []

    for person in ents["people"][:10]:
        if person.lower() == primary_query.lower():
            continue
        pivots.append(
            {
                "type": "person",
                "query": person,
                "rationale": f"co-mentioned with {primary_query}",
                "depth": 1,
            }
        )
    for org in confirmed_orgs[:5]:
        pivots.append(
            {
                "type": "organization",
                "query": org,
                "rationale": f"affiliated with {primary_query}",
                "depth": 1,
            }
        )
    for dom in ents["domains"][:5]:
        pivots.append(
            {
                "type": "domain",
                "query": dom,
                "rationale": f"referenced from {primary_query} context",
                "depth": 1,
            }
        )

    if depth >= 2:
        for p in pivots[:]:
            pivots.append(
                {
                    "type": f"{p['type']}:depth2",
                    "query": p["query"],
                    "rationale": "depth-2 expansion (requires confirmation)",
                    "depth": 2,
                    "parent": primary_query,
                }
            )

    return pivots
