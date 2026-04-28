# shadowtrace

**Single-operator OSINT toolkit. Public sources only. Audit-logged. Cross-validated.**

[![CI](https://github.com/thenot-lab/shadowtrace-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/thenot-lab/shadowtrace-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Shadowtrace is a personal investigative-research toolkit for sales, security due-diligence, customer discovery, and journalism. It runs on one machine, for one operator, against one subject at a time. It uses only public sources, logs every fetch, requires two-source corroboration before treating a claim as evidence, and writes a reproducible audit trail you can hand to a judge.

It is the open, auditable inverse of the closed broker-data tools — the ones that buy leaked personal data, sell deep profiles to anyone with a credit card, and leave no trail. That market exists. This is not part of it.

---

## What it does

Given a name, a company, or a public identifier, shadowtrace:

1. **Resolves** the entity across public sources (web search, GitHub, Wikipedia, prior cached profiles).
2. **Cross-validates** every claim against ≥2 independent sources before promoting it to evidence.
3. **Synthesizes** a structured profile: top affiliations, locations, behavioral fingerprint (lexical / stylistic / temporal), evidence chains, coverage gaps.
4. **Red-teams** itself: produces a verification checklist of things to re-confirm before acting on the report.
5. **Logs** every source hit with timestamp + query + outcome to an append-only audit trail.
6. **Caches** structured + markdown outputs for reproducibility and recompilation.

It is deterministic where it can be (resolution, deduplication, evidence-chain assembly) and clearly marked where it is not (behavioral synthesis is heuristic, not divination).

## What it explicitly does NOT do

- No private-data brokers. No leaked credentials. No dark-web scrapes.
- No mass profiling. The architecture is single-subject, single-operator by design.
- No social-media scraping that violates a platform's terms.
- No silent surveillance. The audit log is a feature; you can hand it to the subject.
- No bypassing of `robots.txt`. Allowlist per source.
- No EU subjects without GDPR mode (Article 9(2)(e) manifestly-public only by default).
- No sensitive-category profiling (religion, politics, health) without explicit consent flag.

If you wanted a tool to dox someone, this is not that tool. The hardcoded rails will fight you.

---

## Install

```bash
pip install shadowtrace
```

Or from source:

```bash
git clone https://github.com/thenot-lab/shadowtrace-cli.git
cd shadowtrace
pip install -e .
```

Requires Python 3.10+. Optional: an LLM API key (Anthropic / OpenAI) if you want to enable LLM-backed behavioral synthesis. The deterministic core runs without one.

## Quickstart

```bash
# Research a public subject (web + github + wikipedia + memory by default)
shadowtrace research "Sophie Wilson computer scientist"

# Look at the audit log of every source hit
shadowtrace audit --tail 20

# Re-run all cached profiles (e.g. after sources update)
shadowtrace recompile

# Print a previously cached report
shadowtrace report <subject_id>
```

A run produces three outputs:

- `cache/<subject_id>.md` — human-readable markdown report
- `cache/<subject_id>.json` — structured data + provenance + evidence chains
- `cache/<subject_id>.audit.jsonl` — append-only source log

See [`examples/`](examples/) for a full walkthrough on a public subject.

---

## The ethical rails (hardcoded)

These are not configuration. They are enforced in the code path:

1. **Public sources only** for arbitrary subjects; deep-tier requires `--consented` flag.
2. **No scraping against `robots.txt`** — explicit allowlist per source module.
3. **Rate limits** at the toolkit level, not just per-source. You cannot accidentally DoS a target.
4. **Audit log is append-only.** Every datapoint is traceable to its source query and timestamp.
5. **EU subjects auto-detected** → GDPR mode → manifestly-public-only by default.
6. **Single-operator guarantee.** No multi-tenant mode exists. The architecture refuses to grow into a service.
7. **Sensitive-category auto-redact.** Religion, politics, health are stripped from default reports.
8. **Two-source corroboration** required before a claim is promoted from "raw datapoint" to "evidence."

If you fork shadowtrace and remove these rails, you are no longer running shadowtrace. You are running something else with our name on it.

---

## Architecture

```
shadowtrace/
├── cli.py                     # entry: shadowtrace <cmd> [args]
├── engine.py                  # research orchestrator
├── session.py                 # session state + correlation
├── sources/                   # public-data adapters
│   ├── web.py                 # web search (DuckDuckGo by default)
│   ├── github.py              # public repos, issues, commits
│   ├── wikipedia.py           # public encyclopedic content
│   ├── memory.py              # local profile cache
│   ├── seed.py                # offline-mode seed loader
│   ├── mcp_stub.py            # Model Context Protocol adapter (optional)
│   └── base.py                # source contract
├── synth/                     # synthesis layer
│   ├── resolver.py            # probabilistic-then-deterministic entity resolution
│   ├── cross_validate.py      # ≥2-source corroboration
│   ├── semantic_dedup.py      # claim-level deduplication
│   ├── evidence_chain.py      # multi-claim evidence assembly
│   ├── pivot_chains.py        # safe depth-1 pivot suggestions
│   ├── behavioral.py          # behavioral inference (deterministic + optional LLM)
│   ├── behavioral_fingerprint.py  # lexical / stylistic / temporal fingerprint
│   ├── adversarial.py         # red-team verification checklist
│   └── self_ref_filter.py     # filters self-referential noise
├── audit/                     # provenance + safety
│   ├── source_log.py          # append-only fetch log
│   ├── consent_check.py       # GDPR / consent-tier detection
│   ├── rate_limit.py          # global + per-source throttle
│   └── telemetry.py           # local-only operator telemetry
├── output/                    # report rendering
│   ├── report.py              # markdown report
│   ├── json_export.py         # structured export
│   └── update_knowledge.py    # writes profile to local KB
├── tests/                     # pytest suite
└── v7_config.yaml             # priorities, rate limits, allowlists
```

## Output format (excerpt)

```
======================================================================
shadowtrace v7  |  subject: Sophie Wilson computer scientist
subject_id: a1b2c3d4  tier: public  eu: True
sources hit: web, github, wikipedia, memory
records: 47  clusters: 3
----------------------------------------------------------------------
TOP TITLES:    computer scientist (12), engineer (4), CBE (3)
TOP ORGS:      Acorn Computers (8), Broadcom (5), University of Cambridge (4)
LOCATIONS:     Cambridge UK (9), Roanoke VA (3)
SOURCE MIX:    {'wikipedia': 11, 'web': 22, 'github': 4, 'memory': 10}
----------------------------------------------------------------------
TOP CORROBORATED CLAIMS:
  [0.94] Designed instruction set of the original ARM processor
        sources: wikipedia, web
  [0.91] Led BBC Micro BASIC interpreter design
        sources: wikipedia, web
  [0.86] Currently distinguished engineer at Broadcom
        sources: web, github
----------------------------------------------------------------------
COVERAGE GAPS  archetype=technical-leader-public
  gap: limited recent first-person commentary
  gap: sparse non-English-language sources
  interpretation: subject is press-public but interview-private
----------------------------------------------------------------------
VERIFICATION CHECKLIST:
  - confirm current Broadcom role title before reaching out
  - cross-check Cambridge affiliation against college-specific page
  - distinguish Sophie Wilson (CS) from same-name namesakes (red-team count: 2)
----------------------------------------------------------------------
EVIDENCE CHAINS (3): ...
PIVOT SUGGESTIONS: ...
BEHAVIORAL FINGERPRINT  wc=2841 sents=164
  lexical: avg_sent_len=17.3 ttr=0.52
  stylistic: hedge/1k=8.2 intensifier/1k=2.1
======================================================================
```

---

## Roadmap

- [x] v7.0 — initial public-source synthesis, ethical rails, audit log
- [x] v7.1 — behavioral fingerprint, evidence chains, pivot chains, semantic dedup
- [ ] v7.2 — opt-in LLM synthesis adapter (Anthropic / OpenAI / local)
- [ ] v7.3 — additional source modules (proposed by community PR)
- [ ] v7.4 — desktop GUI wrapper

The single-subject single-operator architecture is a permanent design constraint, not a stage. shadowtrace will not become a service.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Three rules:

1. **Don't weaken the ethical rails.** PRs that remove or downgrade them will be closed without review.
2. **Add sources via the source contract** in `sources/base.py`. New sources must include rate limits, robots-respect, and audit-log integration.
3. **Tests pass.** `pytest tests/` must be green.

## License

[MIT](LICENSE). Use it. Fork it. Don't pretend the ethical rails away while keeping the name.

## Acknowledgments

Built by [Dominion Labs](https://dominionlabs.dev). The ethical-OSINT framing owes a debt to the open-investigation tradition (Bellingcat, OCCRP, CitizenLab) and stands in deliberate opposition to the closed broker-data market.

The verification approach — two-source corroboration, append-only audit, sensitivity redaction — is borrowed from journalism standards, not reinvented.
