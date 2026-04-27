# Example 2: Pre-call company research

**Subject pattern:** A small or mid-size company you're about to call. You want context — what they do, who's there, what's been said about them publicly — without burning two hours.

## The command

```bash
shadowtrace research "Acme Innovation Centre Barrie Ontario"
```

Including the city/region helps disambiguate against same-named entities and biases the web-source results toward locally-relevant content.

## The annotated output (illustrative)

```
======================================================================
shadowtrace v7  |  subject: Acme Innovation Centre Barrie Ontario
subject_id: c5d6e7f8  tier: public  eu: False
sources hit: web, wikipedia, memory
records: 31  clusters: 1
----------------------------------------------------------------------
TOP TITLES:    executive director (3), program manager (2), founder (1)
TOP ORGS:      Acme Innovation Centre (15), County of Simcoe (4), Georgian College (3)
LOCATIONS:     Barrie ON (12), Simcoe County (5)
SOURCE MIX:    {'web': 22, 'wikipedia': 1, 'memory': 8}
----------------------------------------------------------------------
TOP CORROBORATED CLAIMS:
  [0.89] Operates a co-working and accelerator space in downtown Barrie
        sources: web, web
  [0.84] Partners with County of Simcoe and Georgian College on workforce programming
        sources: web, web
  [0.71] Hosted a regional manufacturing-tech summit in late 2025
        sources: web, web
----------------------------------------------------------------------
COVERAGE GAPS  archetype=regional-innovation-org
  gap: limited program-outcome reporting
  gap: no public financial disclosures (private nonprofit, expected)
  interpretation: org is locally visible but does not publish program metrics — ask in the call
----------------------------------------------------------------------
VERIFICATION CHECKLIST:
  - confirm executive director name and current term before naming them in outreach
  - check whether the 2025 summit had follow-on programming you could reference
  - distinguish from any similarly-named US-based innovation centres
----------------------------------------------------------------------
PIVOT SUGGESTIONS (depth-1 safe, 4 total):
  [adjacent_org] Sandbox Centre Barrie — same-region peer, often co-programmed
  [funder] Simcoe County economic development — likely funder/partner
  [adjacent_org] Henry Bernick Entrepreneurship Centre — Georgian College sister org
  [event] Barrie ON innovation ecosystem 2026 — recent event mentions
======================================================================
```

## How to use this output for an actual sales call

1. **Read the corroborated claims, not the underlying records.** The two-source filter exists because single-source web claims are often outdated, opinion, or wrong.

2. **Read the coverage gaps.** "Org does not publish program metrics" is not a deficit in shadowtrace — it's a fact about the org you can use in the call ("I noticed you don't publish program outcomes publicly — is there a private report you'd be willing to share?").

3. **Read the verification checklist before drafting outreach.** Especially "confirm executive director name and current term." Public bios go stale.

4. **Read the pivot suggestions for second-call context.** Mentioning a peer org or funder in a first call is a strong signal you've done homework — but only if you've actually verified those connections.

5. **Don't paste the report into your CRM verbatim.** It's research scaffolding, not a customer record. Pull the verified facts; leave the heuristic synthesis behind.

## What shadowtrace will NOT tell you

- The decision-maker's personal contact info — that's broker-data territory.
- Who's about to leave the org — speculation that the rails refuse.
- What the executive director thinks of you — that's not knowable from public sources.

If a sales-research tool is selling you certainty about any of those, ask harder questions about where their data comes from.
