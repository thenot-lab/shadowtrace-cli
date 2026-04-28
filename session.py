"""Investigation session - adapted from v6 ShadowTraceAgentUpgrade.

Wraps a shadowtrace research bundle with a durable session ID, checkpoint
persistence, and a resume() path. Sessions live in cache/sessions/.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent / "cache" / "sessions"
BASE.mkdir(parents=True, exist_ok=True)


def _sid(query: str) -> str:
    return f"inv-{hashlib.sha1(query.lower().encode()).hexdigest()[:10]}-{int(time.time())}"


def start(query: str, target_info: dict[str, Any] | None = None) -> dict[str, Any]:
    sid = _sid(query)
    state = {
        "session_id": sid,
        "query": query,
        "target_info": target_info or {},
        "start_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "open",
        "findings": [],
        "evidence_chains": [],
        "leads": [],
        "telemetry_refs": [],
    }
    (BASE / f"{sid}.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def checkpoint(session: dict[str, Any], bundle: dict[str, Any]) -> None:
    sid = session["session_id"]
    session["last_checkpoint_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    session["findings"].append(
        {
            "records": bundle["meta"]["record_count"],
            "corroborated": sum(1 for c in bundle["corroborated_claims"] if c["corroborated"]),
            "subject_id": bundle["meta"]["subject_id"],
        }
    )
    session["evidence_chains"] = bundle.get("evidence_chains", [])
    (BASE / f"{sid}.json").write_text(json.dumps(session, indent=2), encoding="utf-8")


def resume(session_id: str) -> dict[str, Any] | None:
    p = BASE / f"{session_id}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def close(session_id: str) -> bool:
    p = BASE / f"{session_id}.json"
    if not p.exists():
        return False
    state = json.loads(p.read_text(encoding="utf-8"))
    state["status"] = "closed"
    state["closed_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    p.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return True
