"""Structured JSON export - source of truth for recompile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _safe(o: Any) -> Any:
    if isinstance(o, set):
        return sorted(list(o))
    if hasattr(o, "to_dict"):
        return o.to_dict()
    raise TypeError(f"unserializable: {type(o).__name__}")


def write(path: Path, bundle: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, indent=2, default=_safe), encoding="utf-8")
    return path
