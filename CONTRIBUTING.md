# Contributing to shadowtrace

Thanks for considering a contribution. Three things to know first.

## 1. The ethical rails are non-negotiable

Shadowtrace exists because the closed broker-data market exists. The eight rails listed in the [README](README.md) are not configuration — they are the load-bearing reason this project ships under the MIT license without becoming part of the problem it was built against.

PRs that remove, weaken, or "make optional" any of the following will be closed without review:

- Public-sources-only default
- `robots.txt` respect
- Rate limiting (global + per-source)
- Append-only audit log
- EU subject GDPR mode
- Single-operator architecture (no multi-tenant mode)
- Sensitive-category auto-redact
- Two-source corroboration before evidence promotion

If you have a use case that you believe requires changing one of these, open an issue first to discuss. Don't open the PR.

## 2. Adding a source

New source modules go in `sources/` and must implement the contract in `sources/base.py`:

- `name: str` — short identifier
- `fetch(query, ctx) -> list[Record]` — returns structured records
- `rate_limit_per_minute: int` — your declared limit
- `respects_robots: bool = True` — must be True for public-internet sources
- `consent_tier: Literal["public", "deep"]` — `deep` requires explicit consent

Every fetch must call `audit.source_log.log(...)` with the query, source, outcome, and timestamp. The audit log is the contract with the subject.

Source modules must include unit tests in `tests/sources/test_<name>.py` that cover at minimum:
- A successful fetch (mocked)
- A rate-limited fetch (returns expected throttle behavior)
- A robots-blocked fetch (returns empty without error)

## 3. Tests must pass

```bash
pip install -e ".[dev]"
pytest tests/
```

Green CI on the PR is required for merge.

## Issues

Bug reports welcome. For security issues, see [SECURITY.md](SECURITY.md) — please don't open public issues for vulnerabilities.

Feature requests: include the use case, not just the feature. "I want to research a candidate before a sales call without violating LinkedIn's ToS" is a use case. "Add LinkedIn scraping" is not.

## Code style

- `black` for formatting (line length 100)
- `ruff` for linting
- Type hints on all public functions
- Docstrings on all public functions; inline comments only for non-obvious *why*

## License

By contributing, you agree your contribution is licensed under the MIT License (see [LICENSE](LICENSE)).
