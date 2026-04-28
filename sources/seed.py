"""Seed source - accepts pre-fetched results piped from outside the tool.

Eli (or any orchestrator) runs WebSearch outside shadowtrace, writes results
to a JSON file, passes --seeds path. Each seed becomes a Record directly.

Seed JSON shape:
[
  {"title": "...", "url": "...", "snippet": "...", "source_name": "search|twitter|..."},
  ...
]
"""

from __future__ import annotations

import json
from pathlib import Path

from .base import Record


def load(path: str, subject_hint: str) -> list[Record]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    out: list[Record] = []
    for d in data:
        if not isinstance(d, dict):
            continue
        src = (d.get("source_name") or "search").lower()
        authority = {
            "wikipedia": 0.9,
            "github": 0.75,
            "linkedin": 0.7,
            "news": 0.8,
            "academic": 0.85,
            "gov": 0.95,
            "twitter": 0.5,
            "blog": 0.5,
            "search": 0.6,
        }.get(src, 0.5)
        title = d.get("title") or ""
        snippet = d.get("snippet") or d.get("description") or ""
        content = f"{title}\n{snippet}".strip()
        if not content:
            continue
        out.append(
            Record(
                source=f"seed:{src}",
                kind="search_hit",
                subject_hint=subject_hint,
                content=content,
                url=d.get("url"),
                ts_iso=d.get("ts") or d.get("date"),
                authority=authority,
                confidence=float(d.get("confidence") or 0.6),
                meta={
                    k: v for k, v in d.items() if k not in {"title", "snippet", "url", "ts", "date"}
                },
            )
        )
    return out
