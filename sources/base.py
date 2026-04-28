"""Source base contract.

Every source returns a list of Record dicts with a uniform shape so the
resolver and synth can merge across sources without ad-hoc glue.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Record:
    source: str  # "github", "wikipedia", "web_search", ...
    kind: str  # "bio", "employer", "link", "post", "commit", "mention"
    subject_hint: str  # raw name/email/handle that produced this record
    content: str  # human-readable chunk
    url: str | None = None
    ts_iso: str | None = None
    authority: float = 0.5  # 0-1, source credibility weight
    confidence: float = 0.5  # 0-1, how certain this record pertains to subject
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def empty() -> list[Record]:
    return []
