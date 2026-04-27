# Security Policy

## Reporting a Vulnerability

If you find a vulnerability in shadowtrace — particularly one that could:

- Bypass the audit log
- Bypass the ethical rails (rate limits, robots respect, consent tier)
- Leak operator credentials or subject data
- Enable mass-profiling that the architecture is designed to prevent

…please report it privately rather than opening a public issue.

**Email:** security@dominionlabs.dev (or the contact on dominionlabs.dev if that route is unavailable).

Include:
- The vulnerability and its impact
- Reproduction steps
- Affected version(s)
- Any suggested mitigation

You should expect:
- Acknowledgment within 72 hours
- A coordinated disclosure window discussion
- Credit in the changelog if you want it

## Scope

Shadowtrace is a single-operator local toolkit. The threat model is:

1. **In scope:** vulnerabilities in the shadowtrace code path itself — anything that lets a user circumvent the rails described in the README, leaks the audit log, or breaks the consent-tier enforcement.

2. **Out of scope:** the security posture of the public sources shadowtrace queries (web search engines, Wikipedia, GitHub, etc.). Their security is theirs.

3. **Out of scope:** misuse by an operator with legitimate access to a machine running shadowtrace. The tool is designed to be auditable by the *subject* of an investigation, not by the operator's adversaries.

## Hardening recommendations for operators

- Run shadowtrace under a dedicated user account, not your daily-driver account
- Keep the audit log on a separate disk or replicate it off-machine
- Rotate any LLM API keys (if you've enabled the optional LLM adapter) on a defined cadence
- Treat `cache/` as sensitive — it is the materialized form of every subject you've researched
