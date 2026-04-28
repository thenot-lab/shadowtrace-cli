"""Drop the human report into eli/knowledge/profiles/ for next-session recall."""

from __future__ import annotations

from pathlib import Path

KNOWLEDGE_PROFILES = Path(__file__).resolve().parent.parent.parent / "knowledge" / "profiles"


def persist(subject_id: str, markdown: str) -> Path:
    KNOWLEDGE_PROFILES.mkdir(parents=True, exist_ok=True)
    out = KNOWLEDGE_PROFILES / f"{subject_id}.md"
    out.write_text(markdown, encoding="utf-8")
    return out
