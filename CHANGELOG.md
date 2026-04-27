# Changelog

All notable changes to shadowtrace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [7.1.0] — 2026-04-19

First public release.

### Added
- Behavioral fingerprint synthesis (lexical / stylistic / temporal)
- Evidence-chain assembly across multi-claim corroboration
- Pivot-chain suggestions (depth-1, safety-bounded)
- Semantic deduplication of claim records
- Self-reference filter (drops noise from subject's own self-promotional surfaces)
- Adversarial red-team output (verification checklist)
- Telemetry module (local-only operator instrumentation)
- Wikipedia source module
- pytest suite with public-figure verification fixtures

### Changed
- License moved from proprietary-internal to MIT (this release)
- Resolver moved to probabilistic-then-deterministic two-stage approach
- Audit log format extended with structured `meta` field

### Verified
- Test suite passes 18/18 against Sophie Wilson public-figure fixture
- Manual verification on Eliot Higgins fixture: 6 corroborated claims, 0 hallucinations

## [7.0.1] — 2026-04-19

Initial private build. Internal-only.

### Added
- 19 modules / ~1400 LOC across `cli`, `engine`, `session`, `sources/`, `synth/`, `audit/`, `output/`
- Hard ethical rails: public-only default, audit-log append-only, GDPR-mode auto-detect, single-operator architecture, sensitive-category redaction
- CLI subcommands: research, enrich, report, recompile, audit
- Source modules: web search, GitHub, Wikipedia, memory, seed loader, MCP stub
- Output formats: markdown report, structured JSON, knowledge-base profile
