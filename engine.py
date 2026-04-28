"""shadowtrace v7.1 engine - orchestrates sources -> resolver -> synth -> output.

v7.1 upgrades over v7.0.1:
  - self-reference filter (drops shadowtrace's own prior profiles)
  - semantic org dedup (collapses common-noun false-positives)
  - behavioral fingerprint (writing-style + posting-rhythm + timezone)
  - pivot chains (depth-1 safe, depth-2 requires confirmation)
  - evidence chains adapted from v6 agent pattern
  - investigation session with checkpoint + resume
  - span-based telemetry alongside audit log
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import yaml

from . import session as _session
from .audit import consent_check, rate_limit, source_log, telemetry
from .output import json_export, update_knowledge
from .output import report as _report
from .sources import base as _base
from .sources import github, mcp_stub, memory, seed, web, wikipedia
from .synth import (
    adversarial,
    behavioral,
    behavioral_fingerprint,
    cross_validate,
    evidence_chain,
    pivot_chains,
    resolver,
    self_ref_filter,
    semantic_dedup,
)

BASE = Path(__file__).resolve().parent
CACHE = BASE / "cache"
VERSION = "7.1.0"


def _load_cfg() -> dict[str, Any]:
    p = BASE / "v7_config.yaml"
    if not p.exists():
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _subject_id(query: str) -> str:
    return hashlib.sha1(query.strip().lower().encode()).hexdigest()[:12]


def research(
    query: str,
    seeds_path: str | None = None,
    enable_web: bool = True,
    enable_github: bool = True,
    enable_wikipedia: bool = True,
    enable_memory: bool = True,
    urls_to_fetch: list[str] | None = None,
    explicit_consent: bool = False,
    session_resume_id: str | None = None,
    pivot_depth: int = 1,
) -> dict[str, Any]:
    run_span = telemetry.span("research.full", query=query[:80], version=VERSION)
    cfg = _load_cfg()
    cfg.setdefault("consent", {})["explicit"] = explicit_consent
    consent = consent_check.evaluate(query, cfg)

    subject_id = _subject_id(query)
    run_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if session_resume_id:
        sess = _session.resume(session_resume_id)
        if sess is None:
            sess = _session.start(query)
    else:
        sess = _session.start(query, {"subject_id": subject_id})

    records: list[_base.Record] = []
    sources_hit: set[str] = set()

    def _call(name: str, spec: str, fn, *args):
        s = telemetry.span("source." + name)
        if spec:
            ok, reason = rate_limit.check(name, spec)
            if not ok:
                source_log.log(name, query, False, {"reason": reason})
                s.add_event("rate_limited", {"reason": reason})
                s.end("rate_limited")
                return []
        try:
            res = fn(*args) or []
        except Exception as e:
            source_log.log(name, query, False, {"error": str(e)[:200]})
            s.add_event("error", {"msg": str(e)[:200]})
            s.end("error")
            return []
        if spec:
            rate_limit.commit(name)
        source_log.log(name, query, True, {"records": len(res)})
        if res:
            sources_hit.add(name)
        s.add_event("ok", {"records": len(res)})
        s.end("ok")
        return res

    if enable_memory:
        records.extend(_call("memory", "", memory.scan, query))
    if enable_wikipedia:
        records.extend(_call("wikipedia", "30/hour", wikipedia.search, query, 3))
    if enable_github:
        gh_hits = _call("github", "30/hour", github.search_user, query, 3)
        records.extend(gh_hits)
        for r in gh_hits[:2]:
            login = r.meta.get("login")
            if login:
                records.extend(_call("github", "30/hour", github.list_repos, login, 5))
    if seeds_path:
        records.extend(_call("seed", "", seed.load, seeds_path, query))
    if enable_web and urls_to_fetch:
        for u in urls_to_fetch[:5]:
            records.extend(_call("web", "30/hour", web.harvest, u, query, 0.55))

    # MCP stubs always logged honestly even when empty
    for s in ("gmail", "common_room", "apollo", "stripe_crm"):
        source_log.log(s, query, False, {"reason": mcp_stub.REASON})

    # v7.1: drop self-references BEFORE resolver sees them
    filter_span = telemetry.span("filter.self_reference")
    records, self_ref_dropped = self_ref_filter.filter_records(records)
    filter_span.add_event("filtered", {"dropped": self_ref_dropped})
    filter_span.end("ok")

    # re-evaluate consent tier against record content for EU/UK detection
    try:
        _combined = query + chr(10) + chr(10).join((r.content or "")[:400] for r in records[:20])
        _promoted = consent_check.evaluate(_combined, cfg)
        if isinstance(_promoted, dict) and (
            _promoted.get("tier") != "public_only" or _promoted.get("eu_subject")
        ):
            consent = _promoted
    except Exception:
        pass

    # apply sensitive-category redaction if requested
    if consent.get("sensitive_redact"):
        for r in records:
            r.content, hits = consent_check.redact_sensitive(r.content, True)
            if hits:
                r.meta["redacted"] = hits

    resolver_span = telemetry.span("synth.resolver")
    clusters = resolver.resolve(records, query)
    resolver_span.add_event("resolved", {"clusters": len(clusters)})
    resolver_span.end("ok")
    primary_cluster_records = clusters[0]["records"] if clusters else records

    cv_span = telemetry.span("synth.cross_validate")
    claims = cross_validate.extract_claims(primary_cluster_records)
    corroborated = cross_validate.corroborate(claims)
    cv_span.add_event(
        "validated",
        {"claims": len(claims), "corroborated": sum(1 for c in corroborated if c["corroborated"])},
    )
    cv_span.end("ok")

    profile_span = telemetry.span("synth.profile")
    profile = behavioral.assemble(primary_cluster_records, query)
    raw_org_names = [
        o[0] if isinstance(o, (list, tuple)) else o for o in profile.get("top_orgs", [])
    ]
    profile["top_orgs_refined"] = semantic_dedup.normalize_orgs(raw_org_names)
    profile["fingerprint"] = behavioral_fingerprint.fingerprint(primary_cluster_records)
    guide = behavioral.interaction_guide(profile, consent["tier"])
    profile_span.end("ok")

    sources_seen = set()
    for r in primary_cluster_records:
        parts = r.source.split(":", 1)
        sources_seen.add(parts[1] if len(parts) == 2 else parts[0])
    adv_span = telemetry.span("synth.adversarial")
    ns = adversarial.negative_space(profile, corroborated, sources_seen)
    rt = adversarial.red_team(profile)
    counter = []
    for cl in [c for c in corroborated if c["corroborated"]][:6]:
        counter.append(
            {"claim": cl["claim"], "hypotheses": adversarial.counter_hypothesize(cl["claim"])}
        )
    adv_span.end("ok")

    chain_span = telemetry.span("synth.evidence_chain")
    chains = evidence_chain.build_chains(corroborated)
    chain_span.add_event("chains", {"count": len(chains)})
    chain_span.end("ok")

    pivot_span = telemetry.span("synth.pivot_chains")
    confirmed_orgs = [o["name"] for o in profile["top_orgs_refined"][:5]]
    pivots = pivot_chains.propose_pivots(
        query, primary_cluster_records, confirmed_orgs, depth=pivot_depth
    )
    pivot_span.add_event("pivots", {"count": len(pivots)})
    pivot_span.end("ok")

    bundle: dict[str, Any] = {
        "subject_query": query,
        "meta": {
            "version": VERSION,
            "subject_id": subject_id,
            "session_id": sess["session_id"],
            "run_iso": run_iso,
            "operator": "brayd",
            "consent": consent,
            "sources_hit": sorted(sources_hit),
            "record_count": len(records),
            "self_ref_dropped": self_ref_dropped,
            "cluster_count": len(clusters),
            "robots_compliant": True,
            "audit_log": "cache/audit.jsonl",
            "telemetry_log": "cache/telemetry.jsonl",
        },
        "profile": profile,
        "evidence_chains": chains,
        "pivots": pivots,
        "corroborated_claims": corroborated,
        "negative_space": ns,
        "adversarial": {"counter_hypotheses": counter, "red_team": rt},
        "interaction_guide": guide,
        "clusters_summary": [
            {
                "cluster_id": c["cluster_id"],
                "canonical_name": c["canonical_name"],
                "confidence": c["confidence"],
                "source_diversity": c["source_diversity"],
                "record_count": len(c["records"]),
                "ids": c["ids"],
            }
            for c in clusters
        ],
        "records": [r.to_dict() for r in records],
    }

    md = _report.render(bundle)
    md_path = CACHE / f"{subject_id}.md"
    json_path = CACHE / f"{subject_id}.json"
    _report.write(md_path, md)
    json_export.write(json_path, bundle)
    knowledge_path = update_knowledge.persist(subject_id, md)

    bundle["meta"]["outputs"] = {
        "markdown": str(md_path),
        "json": str(json_path),
        "knowledge_copy": str(knowledge_path),
    }

    _session.checkpoint(sess, bundle)
    run_span.add_event(
        "complete",
        {
            "records": len(records),
            "corroborated": sum(1 for c in corroborated if c["corroborated"]),
            "chains": len(chains),
        },
    )
    run_span.end("ok")
    return bundle
