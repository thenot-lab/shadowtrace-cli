"""v7.1 Sophie test - adapted from v6 ShadowTraceAgentUpgrade test pattern.

v6 test pattern (from outputs/agentic-framework/project-upgrades/shadowtrace/upgrade.ts):
  1. startInvestigation(targetId, targetInfo)
  2. gatherIntelligence(sessionId, targetId, agents[])  # parallel
  3. correlateFindings(sessionId, targetId)
  4. exportInvestigation(sessionId, format)

Adapted to v7.1 Python:
  1. session.start(query)  -> sess
  2. engine.research(query, ...)  -> bundle  (handles gather + correlate)
  3. assert invariants on bundle (records, sources, corroboration, chains)
  4. export is automatic (markdown + json + knowledge copy)

Target: Eli picks. Eli, given the option between any publicly-notable
'Sophie' figure, selected Sophie Wilson - British computer scientist,
co-designer of the BBC Micro and the ARM processor architecture. Rationale:
  - unambiguously public figure (books, Wikipedia, BBC, Fellow of Royal Society)
  - UK subject -> exercises the GDPR manifestly_public tier
  - technology-domain -> should surface cleanly on Wikipedia + web
  - ARM is foundational to modern computing -> high-authority cross-refs
  - NOT a private individual, not a minor, not a protected class subject
"""
from __future__ import annotations
import json
from pathlib import Path
from shadowtrace import engine
from shadowtrace import session as _session

SOPHIE_TARGET = "Sophie Wilson"
SOPHIE_SEEDS = Path(__file__).parent / "sophie_seeds.json"


def run() -> dict:
    """Full v7.1 test - returns assertion report."""
    results: dict = {"target": SOPHIE_TARGET, "assertions": [], "bundle_meta": None}

    bundle = engine.research(
        SOPHIE_TARGET,
        seeds_path=str(SOPHIE_SEEDS) if SOPHIE_SEEDS.exists() else None,
        enable_web=False,
        enable_github=True,
        enable_wikipedia=True,
        enable_memory=True,
        explicit_consent=False,
        pivot_depth=1,
    )
    meta = bundle["meta"]
    results["bundle_meta"] = meta

    def _assert(name: str, cond: bool, detail: str = "") -> None:
        results["assertions"].append({"name": name, "pass": bool(cond), "detail": detail})

    _assert("version_is_7_1", meta.get("version") == "7.1.0", f"got={meta.get('version')}")
    _assert("session_id_present", bool(meta.get("session_id", "").startswith("inv-")), meta.get("session_id", ""))
    _assert("records_gathered", meta["record_count"] >= 3, f"records={meta['record_count']}")
    _assert("multi_source", len(meta["sources_hit"]) >= 2, f"sources={meta['sources_hit']}")
    _assert("clusters_built", meta["cluster_count"] >= 1, f"clusters={meta['cluster_count']}")
    _assert("self_ref_filter_ran", "self_ref_dropped" in meta, str(meta.get("self_ref_dropped")))
    _assert("robots_compliant", meta["robots_compliant"] is True)

    corroborated = [c for c in bundle["corroborated_claims"] if c["corroborated"]]
    _assert("at_least_one_corroborated", len(corroborated) >= 1, f"n={len(corroborated)}")

    _assert("evidence_chains_field", "evidence_chains" in bundle)
    _assert("pivots_field", "pivots" in bundle)

    profile = bundle["profile"]
    _assert("profile_has_fingerprint", "fingerprint" in profile)
    _assert("profile_has_refined_orgs", "top_orgs_refined" in profile)

    fp = profile.get("fingerprint", {})
    if not fp.get("insufficient_data"):
        _assert("fingerprint_word_count", fp.get("word_count", 0) > 20, f"wc={fp.get('word_count')}")
        _assert("fingerprint_lexical", "lexical" in fp)
        _assert("fingerprint_platform_affinity", "platform_affinity" in fp)

    sess = _session.resume(meta["session_id"])
    _assert("session_persisted", sess is not None)
    _assert("session_has_checkpoint", sess is not None and len(sess.get("findings", [])) >= 1)

    refined = profile["top_orgs_refined"]
    bad_stopwords = [o for o in refined if o["name"].lower().strip(".") in ("news", "politics", "business")]
    _assert("no_stopword_orgs", len(bad_stopwords) == 0, f"bad={[o['name'] for o in bad_stopwords]}")

    passed = sum(1 for a in results["assertions"] if a["pass"])
    total = len(results["assertions"])
    results["summary"] = {"passed": passed, "total": total, "pct": round(100 * passed / total, 1)}
    return results


if __name__ == "__main__":
    r = run()
    print(json.dumps(r, indent=2, default=str))
