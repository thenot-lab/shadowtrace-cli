"""Local knowledge cache - eli/knowledge/ markdown files.

Grep-style scan so prior profiles + Brayd's notes surface as highest-authority hits.
"""

from __future__ import annotations

import re
from pathlib import Path

from .base import Record

KNOWLEDGE = Path(__file__).resolve().parent.parent.parent / "knowledge"


def scan(query: str, limit: int = 5) -> list[Record]:
    if not KNOWLEDGE.exists():
        return []
    needle = query.lower().strip()
    if not needle:
        return []
    # search both full query and individual tokens >= 4 chars
    tokens = [t for t in re.split(r"[\s,;]+", needle) if len(t) >= 4]
    patterns = [needle] + tokens
    out: list[Record] = []
    seen_paths: set[str] = set()
    for md in KNOWLEDGE.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        low = text.lower()
        hits = sum(1 for p in patterns if p in low)
        if hits == 0:
            continue
        # pick the most informative snippet
        idx = low.find(needle) if needle in low else low.find(tokens[0]) if tokens else -1
        start = max(0, idx - 200) if idx >= 0 else 0
        snippet = text[start : start + 900].strip()
        key = str(md)
        if key in seen_paths:
            continue
        seen_paths.add(key)
        out.append(
            Record(
                source="memory",
                kind="note",
                subject_hint=query,
                content=snippet,
                url=f"file://{md}",
                authority=0.95,
                confidence=min(0.95, 0.4 + 0.15 * hits),
                meta={"file": md.name, "hit_count": hits},
            )
        )
        if len(out) >= limit:
            break
    return out
