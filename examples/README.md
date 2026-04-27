# Examples

This directory contains walkthroughs of shadowtrace runs on public subjects with verifiable public footprints. They are illustrative — the exact output will vary because the underlying public sources change over time.

## What's here

- [`01_public_technical_figure.md`](01_public_technical_figure.md) — Researching a publicly-credited technical leader (e.g. an ARM-era computer scientist). Demonstrates entity resolution against same-name namesakes, two-source corroboration, behavioral fingerprint on a sparse data subject.

- [`02_company_research.md`](02_company_research.md) — Researching a small company before a sales call. Demonstrates org-level synthesis, gap detection ("press-public but interview-private"), and the verification checklist that should run before any outreach.

## How to read them

Each example has three sections:

1. **The command** — exactly what you'd type
2. **The annotated output** — what shadowtrace returns, with notes on what to trust and what to verify
3. **The audit excerpt** — what the append-only log captured during the run

The point isn't the specific subject. The point is the *shape* of the output — how shadowtrace surfaces what it knows, what it's unsure about, and what you must re-confirm before you act on it.

## Running your own

```bash
# After install:
shadowtrace research "<your subject>"
```

The first run takes ~10–30 seconds depending on enabled sources. Subsequent runs on the same subject reuse the cache; pass `--no-memory` to force a fresh fetch.

## A note on subject choice

The examples here use public technical figures whose data is genuinely public — they have Wikipedia pages, give public talks, have GitHub footprints. This is shadowtrace's intended use case.

Do not use shadowtrace for:
- Private individuals who haven't placed themselves in public discourse
- Profiling acquaintances, exes, or people you have personal history with
- Bulk profiling for a service or product

The architecture refuses to grow into those modes by design. Don't fight it.
