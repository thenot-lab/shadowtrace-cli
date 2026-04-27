# Example 1: Public technical figure

**Subject pattern:** A publicly-credited technical leader with a Wikipedia page, talks-on-record, and a sparse but real GitHub footprint. Common-name disambiguation required.

## The command

```bash
shadowtrace research "Sophie Wilson computer scientist"
```

We include "computer scientist" in the query to anchor entity resolution. Without it, the resolver might cluster against the more common given-name "Sophie Wilson" patterns; with it, the cluster locks deterministically on the technical figure.

## The annotated output

```
======================================================================
shadowtrace v7  |  subject: Sophie Wilson computer scientist
subject_id: a1b2c3d4  tier: public  eu: True
sources hit: web, github, wikipedia, memory
records: 47  clusters: 3
```

`tier: public` means we did not pass `--consented`; only manifestly-public information is in scope. `eu: True` triggers GDPR mode (the subject is UK-based; UK still treated as EU-equivalent for GDPR-compatible defaults).

`clusters: 3` means three distinct same-name entities were detected; the engine selected the most evidence-rich cluster (the technical figure) and reports the others as ambiguity in the verification checklist.

```
TOP CORROBORATED CLAIMS:
  [0.94] Designed instruction set of the original ARM processor
        sources: wikipedia, web
  [0.91] Led BBC Micro BASIC interpreter design
        sources: wikipedia, web
  [0.86] Currently distinguished engineer at Broadcom
        sources: web, github
```

The `[0.94]` is combined-confidence: a function of source agreement, source weight, and recency. The thresholds are configurable in `v7_config.yaml`. Claims that didn't reach two-source corroboration are still in the underlying `cache/<id>.json` — they're just not surfaced as evidence.

```
COVERAGE GAPS  archetype=technical-leader-public
  gap: limited recent first-person commentary
  gap: sparse non-English-language sources
  interpretation: subject is press-public but interview-private
```

The "negative space" analysis is one of the more useful outputs for sales/research workflows: it tells you the *shape* of what you don't know. If the gap is "no recent press" you might be looking at a retired figure; if the gap is "no first-person commentary" you might be looking at someone who lets their work speak.

```
VERIFICATION CHECKLIST:
  - confirm current Broadcom role title before reaching out
  - cross-check Cambridge affiliation against college-specific page
  - distinguish Sophie Wilson (CS) from same-name namesakes (red-team count: 2)
```

This is the red-team output. **Treat the checklist as load-bearing**: every action you take based on the report should pass these checks first. Shadowtrace is a research aid, not a replacement for the 60 seconds of due-diligence before you press send.

## The audit excerpt

```
$ shadowtrace audit --tail 5
2026-04-27T14:22:18Z  wikipedia       ok=True   q=Sophie Wilson computer scientist  meta={'records': 11}
2026-04-27T14:22:21Z  web             ok=True   q=Sophie Wilson ARM Acorn  meta={'records': 22}
2026-04-27T14:22:24Z  github          ok=True   q=sophie-wilson  meta={'records': 4}
2026-04-27T14:22:24Z  memory          ok=True   q=cluster:sophie_wilson  meta={'records': 10}
2026-04-27T14:22:25Z  output          ok=True   q=write_profile:a1b2c3d4  meta={'bytes': 8421}
```

This is the contract with the subject: every fetch, every query, every outcome. If Sophie Wilson asked tomorrow what shadowtrace knows about her and how it knows, this log is the answer.
