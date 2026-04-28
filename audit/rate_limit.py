"""Token-bucket rate limiter with JSON persistence.

Enforces global + per-source throttles from v7_config.yaml.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "cache" / "rate_state.json"


def _load() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"windows": {}}


def _save(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _parse_spec(spec: str) -> tuple[int, int]:
    # "30/hour" -> (30, 3600)
    n, unit = spec.split("/")
    secs = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}[unit.strip().lower()]
    return int(n), secs


def check(source: str, spec: str) -> tuple[bool, str]:
    """Returns (allowed, reason). If allowed, caller should call commit()."""
    limit, window = _parse_spec(spec)
    state = _load()
    w = state["windows"].setdefault(source, {"start": time.time(), "count": 0})
    now = time.time()
    if now - w["start"] > window:
        w["start"] = now
        w["count"] = 0
    if w["count"] >= limit:
        remaining = int(window - (now - w["start"]))
        return False, f"rate_limit_exceeded source={source} retry_in={remaining}s"
    _save(state)
    return True, "ok"


def commit(source: str) -> None:
    state = _load()
    w = state["windows"].setdefault(source, {"start": time.time(), "count": 0})
    w["count"] += 1
    _save(state)


def status() -> dict:
    return _load()
