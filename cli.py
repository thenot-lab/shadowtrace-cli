"""shadowtrace v7 CLI - Brayd's personal research assistant.

Usage:
  python -m shadowtrace research "<name or company>" [--seeds seeds.json] [--urls u1 u2] [--consented]
  python -m shadowtrace enrich <identifier>
  python -m shadowtrace report <subject_id>
  python -m shadowtrace recompile [--since YYYY-MM-DD]
  python -m shadowtrace audit [--tail N]

All queries use public sources only by default. Audit log is append-only.
Every run writes a human-readable profile into eli/knowledge/profiles/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def cmd_research(args: argparse.Namespace) -> int:
    from .engine import research

    bundle = research(
        query=args.query,
        seeds_path=args.seeds,
        urls_to_fetch=args.urls or [],
        enable_web=not args.no_web,
        enable_github=not args.no_github,
        enable_wikipedia=not args.no_wikipedia,
        enable_memory=not args.no_memory,
        explicit_consent=args.consented,
    )
    meta = bundle["meta"]
    print("=" * 70)
    print(f"shadowtrace v7  |  subject: {bundle['subject_query']}")
    print(
        f"subject_id: {meta['subject_id']}  tier: {meta['consent']['tier']}  eu: {meta['consent']['eu_subject']}"
    )
    print(f"sources hit: {', '.join(meta['sources_hit']) or '(none)'}")
    print(f"records: {meta['record_count']}  clusters: {meta['cluster_count']}")
    print("-" * 70)
    prof = bundle["profile"]
    if prof.get("bio_excerpt"):
        print("BIO (excerpt):")
        print("  " + prof["bio_excerpt"][:500].replace("\n", "\n  "))
        print()
    if prof.get("top_titles"):
        print("TOP TITLES: " + ", ".join(f"{t} ({c})" for t, c in prof["top_titles"]))
    if prof.get("top_orgs"):
        print("TOP ORGS:   " + ", ".join(f"{o} ({c})" for o, c in prof["top_orgs"]))
    if prof.get("top_locations"):
        print("LOCATIONS:  " + ", ".join(f"{loc} ({c})" for loc, c in prof["top_locations"]))
    print(f"SOURCE MIX: {dict(prof['source_breakdown'])}")
    print("-" * 70)
    print("TOP CORROBORATED CLAIMS:")
    corr = [c for c in bundle["corroborated_claims"] if c["corroborated"]][:8]
    if not corr:
        print("  (none crossed 2-source threshold)")
    for c in corr:
        print(f"  [{c['combined_confidence']:.2f}] {c['claim'][:120]}")
        print(f"        sources: {', '.join(c['sources'])}")
    print("-" * 70)
    ns = bundle["negative_space"]
    print(f"COVERAGE GAPS  archetype={ns['guessed_archetype']}")
    for g in ns["gaps"]:
        print(f"  gap: {g}")
    print(f"  interpretation: {ns['interpretation']}")
    print("-" * 70)
    print("VERIFICATION CHECKLIST (things to re-confirm before acting):")
    for r in bundle["adversarial"]["red_team"]:
        print(f"  - {r}")
    print("-" * 70)
    print("ENGAGEMENT GUIDE:")
    for g in bundle["interaction_guide"]:
        print(f"  - {g}")
    print("-" * 70)
    chains = bundle.get("evidence_chains", [])
    if chains:
        print(f"EVIDENCE CHAINS ({len(chains)}):")
        for ch in chains[:5]:
            print(
                f"  [{ch['confidence']:.2f}] len={ch['length']} sources={','.join(ch['sources'])}"
            )
            for cl in ch["claims"][:3]:
                print(f"      - {cl[:120]}")
        print("-" * 70)
    pivots = bundle.get("pivots", [])
    if pivots:
        print(f"PIVOT SUGGESTIONS (depth-1 safe, {len(pivots)} total):")
        for pv in pivots[:8]:
            print(f"  [{pv['type']}] {pv['query']} -- {pv['rationale']}")
        print("-" * 70)
    fp = bundle["profile"].get("fingerprint", {})
    if not fp.get("insufficient_data"):
        lex = fp.get("lexical", {})
        sty = fp.get("stylistic", {})
        print(
            f"BEHAVIORAL FINGERPRINT  wc={fp.get('word_count',0)} sents={fp.get('sentence_count',0)}"
        )
        print(
            f"  lexical: avg_sent_len={lex.get('avg_sentence_len')} ttr={lex.get('type_token_ratio')}"
        )
        print(
            f"  stylistic: hedge/1k={sty.get('hedge_rate_per_1k')} intens/1k={sty.get('intensifier_rate_per_1k')}"
        )
        tz = fp.get("temporal", {}).get("inferred_tz_offset_hours")
        if tz is not None:
            print(f"  inferred timezone offset (hours from UTC): {tz}")
        print("-" * 70)
    print(f"MARKDOWN: {meta['outputs']['markdown']}")
    print(f"JSON:     {meta['outputs']['json']}")
    print(f"KB COPY:  {meta['outputs']['knowledge_copy']}")
    print("=" * 70)
    return 0


def cmd_enrich(args: argparse.Namespace) -> int:
    args.query = args.identifier
    args.seeds = None
    args.urls = []
    args.no_web = True
    args.no_github = False
    args.no_wikipedia = True
    args.no_memory = False
    args.consented = False
    return cmd_research(args)


def cmd_report(args: argparse.Namespace) -> int:
    p = BASE / "cache" / f"{args.subject_id}.md"
    if not p.exists():
        print(f"No cached report for {args.subject_id}")
        return 1
    sys.stdout.write(p.read_text(encoding="utf-8"))
    return 0


def cmd_recompile(args: argparse.Namespace) -> int:
    from .engine import research

    cache = BASE / "cache"
    count = 0
    for jf in cache.glob("*.json"):
        try:
            bundle = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue
        q = bundle.get("subject_query")
        if not q:
            continue
        research(q)
        count += 1
    print(f"recompiled {count} profiles")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    from .audit import rate_limit, source_log

    tail = source_log.tail(args.tail)
    for r in tail:
        print(f"{r['iso']}  {r['source']:14}  ok={r['ok']}  q={r['query'][:60]}  meta={r['meta']}")
    print("-" * 70)
    print(f"rate-limit state: {rate_limit.status()}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="shadowtrace",
        description="Single-operator OSINT toolkit. Public sources only. Audit-logged. Cross-validated.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("research")
    r.add_argument("query")
    r.add_argument("--seeds", default=None, help="path to seed JSON of pre-fetched search results")
    r.add_argument("--urls", nargs="*", default=None, help="additional URLs to fetch")
    r.add_argument(
        "--consented", action="store_true", help="subject gave explicit consent (deep tier)"
    )
    r.add_argument("--no-web", action="store_true")
    r.add_argument("--no-github", action="store_true")
    r.add_argument("--no-wikipedia", action="store_true")
    r.add_argument("--no-memory", action="store_true")

    e = sub.add_parser("enrich")
    e.add_argument("identifier")
    rep = sub.add_parser("report")
    rep.add_argument("subject_id")
    rc = sub.add_parser("recompile")
    rc.add_argument("--since", default=None)
    au = sub.add_parser("audit")
    au.add_argument("--tail", type=int, default=20)

    args = p.parse_args(argv)
    fn = {
        "research": cmd_research,
        "enrich": cmd_enrich,
        "report": cmd_report,
        "recompile": cmd_recompile,
        "audit": cmd_audit,
    }[args.cmd]
    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
