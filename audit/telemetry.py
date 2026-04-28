"""Telemetry - span-based observability adapted from v6 TelemetryCollector.

Every source call and synth step creates a span with duration + outcome.
Spans flush to cache/telemetry.jsonl alongside audit.jsonl.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent.parent / "cache"
BASE.mkdir(parents=True, exist_ok=True)
LOG = BASE / "telemetry.jsonl"
_LOCK = threading.Lock()
_ACTIVE: dict[str, dict[str, Any]] = {}


class Span:
    def __init__(self, name: str, attrs: dict[str, Any] | None = None):
        self.name = name
        self.attrs = attrs or {}
        self.events: list[dict[str, Any]] = []
        self.start = time.time()
        self.id = f"{name}-{int(self.start*1000)}"
        _ACTIVE[self.id] = {"name": name, "start": self.start, "attrs": self.attrs}

    def add_event(self, event: str, data: dict[str, Any] | None = None) -> None:
        self.events.append({"event": event, "data": data or {}, "t": time.time() - self.start})

    def end(self, outcome: str = "ok") -> None:
        dur = time.time() - self.start
        record = {
            "span": self.name,
            "id": self.id,
            "start_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.start)),
            "duration_s": round(dur, 4),
            "outcome": outcome,
            "attrs": self.attrs,
            "events": self.events,
        }
        _ACTIVE.pop(self.id, None)
        with _LOCK:
            with LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")


def span(name: str, **attrs: Any) -> Span:
    return Span(name, attrs)


def active_spans() -> list[dict[str, Any]]:
    return list(_ACTIVE.values())


def summary() -> dict[str, Any]:
    if not LOG.exists():
        return {"total": 0}
    n, errs, total_dur = 0, 0, 0.0
    names: dict[str, int] = {}
    try:
        for line in LOG.read_text(encoding="utf-8").splitlines()[-500:]:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            n += 1
            total_dur += rec.get("duration_s", 0)
            names[rec["span"]] = names.get(rec["span"], 0) + 1
            if rec.get("outcome") != "ok":
                errs += 1
    except Exception:
        return {"total": 0, "error": "log read failed"}
    return {
        "total": n,
        "errors": errs,
        "total_duration_s": round(total_dur, 3),
        "by_span": sorted(names.items(), key=lambda kv: -kv[1])[:20],
    }
