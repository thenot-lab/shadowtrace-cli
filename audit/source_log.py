"""Append-only provenance log. Every source hit writes a JSONL record."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

LOG_PATH = Path(__file__).resolve().parent.parent / "cache" / "audit.jsonl"


def log(source: str, query: str, ok: bool, meta: dict[str, Any] | None = None) -> str:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": source,
        "query": query,
        "ok": ok,
        "meta": meta or {},
    }
    record["id"] = hashlib.sha1(f"{record['ts']}{source}{query}".encode()).hexdigest()[:12]
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record["id"]


def tail(n: int = 20) -> list[dict]:
    if not LOG_PATH.exists():
        return []
    lines = LOG_PATH.read_text(encoding="utf-8").strip().split("\n")
    return [json.loads(line) for line in lines[-n:] if line.strip()]
