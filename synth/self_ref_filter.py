"""Self-reference filter - drop records that quote prior shadowtrace output.

Defect #1 from v7.0.1 Higgins test: shadowtrace re-finding its own prior
profile in eli/knowledge/profiles/*.md created false corroboration. This
filter strips any record whose URL or source-path lies inside the
shadowtrace cache or profiles tree, and any record whose content matches
the shadowtrace report signature.
"""
from __future__ import annotations
from pathlib import Path
from typing import List
from ..sources.base import Record

SIGNATURES = (
    "# shadowtrace profile",
    "## corroborated claims",
    "## negative space",
    "## adversarial",
    "subject_id:",
)

BAD_PATH_PARTS = ("shadowtrace/cache", "eli/knowledge/profiles", "shadowtrace\\cache", "eli\\knowledge\\profiles")


def _looks_like_self(content: str) -> bool:
    if not content:
        return False
    head = content[:400].lower()
    hits = sum(1 for sig in SIGNATURES if sig in head)
    return hits >= 2


def filter_records(records: List[Record]) -> tuple[List[Record], int]:
    """Return (kept, dropped_count)."""
    kept: List[Record] = []
    dropped = 0
    for r in records:
        url = (r.url or "").lower().replace("\\", "/")
        path_hit = any(p.lower().replace("\\", "/") in url for p in BAD_PATH_PARTS)
        content_hit = _looks_like_self(r.content)
        meta_path = str(r.meta.get("path", "")).lower().replace("\\", "/")
        meta_hit = any(p.lower().replace("\\", "/") in meta_path for p in BAD_PATH_PARTS)
        if path_hit or content_hit or meta_hit:
            dropped += 1
            continue
        kept.append(r)
    return kept, dropped
