# Shadowtrace v7.1.0 — Publish Checklist

Prepared: 2026-04-27 (S36 autonomous lap)
Target: first public Dominion Labs OSS release. Closes ledger items D14 (wheel sitting unreleased) and unblocks A13 (Claude Max 20x OSS offer claim).

This is a **single-pass click-through** for Brayd. Every command is copy-paste; every URL is real. Run from `BrightValley/eli/shadowtrace/`.

---

## Pre-flight (already done — verify only)

- [x] `pyproject.toml` v7.1.0 with MIT license + classifiers
- [x] `README.md` with badges, install, ethics rails
- [x] `LICENSE` MIT 2026 attributed to Brayden Gardner / Dominion Labs
- [x] `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
- [x] `.github/workflows/ci.yml` with pip-audit gate (S31c B39 lap)
- [x] `.gitignore`
- [x] `dist/shadowtrace-7.1.0-py3-none-any.whl` built and locally tested (S20 verification)

Verify wheel one last time before publish:
```bash
python -m pip install --user dist/shadowtrace-7.1.0-py3-none-any.whl
shadowtrace --version  # should print 7.1.0
shadowtrace --help     # should list subcommands
```

---

## Step 1 — Init local git + first commit (Eli can do; flagged for Brayd review)

Eli can run these autonomously if Brayd green-lights. Otherwise Brayd runs.

```bash
cd "C:/Users/Brayj/BrightValley/eli/shadowtrace"
git init
git add .
git status  # eyeball the file list — confirm nothing private slipped in
git commit -m "shadowtrace v7.1.0 — initial public release

Single-operator OSINT toolkit. Public sources only. Audit-logged.
Two-source corroboration before any claim is promoted to evidence.
Hardcoded ethics rails (no private brokers, no mass profiling, no GDPR
sensitive-category profiling without consent flag).

Authored against live subjects (Higgins / Wilson) with zero hallucinations
across 24 verified claims. Pip-installable wheel + reproducible audit trail.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

**Audit before push** — `git status` output should show ONLY:
- Source `.py` files
- `pyproject.toml`, `setup.py`, `requirements.txt`
- Markdown docs (`README.md`, `CHANGELOG.md`, etc.)
- `LICENSE`, `v7_config.yaml`
- `.github/workflows/ci.yml`
- `.gitignore`
- `tests/` directory
- `dist/shadowtrace-7.1.0-py3-none-any.whl`

If you see any of these — **stop and do not commit**:
- `__pycache__/`, `.egg-info/`, `cache/` (should be in .gitignore)
- `output/` runs against real subjects
- `audit/*.jsonl` audit trails
- Any file with `.env` extension
- API keys / credentials

---

## Step 2 — Create GitHub repo + push (Brayd-hand, ~3 min)

Login: https://github.com/login (Brayden's existing GitHub)

```bash
# Create repo via gh CLI (auths via existing GitHub login)
gh auth status  # confirm logged in
gh repo create dominionlabs/shadowtrace \
    --public \
    --description "Single-operator OSINT toolkit. Public sources only. Audit-logged. Cross-validated." \
    --source . \
    --push

# OR if dominionlabs org doesn't exist yet, create under brayden-gardner first:
# gh repo create shadowtrace --public --source . --push
# Then transfer to org later via Settings → Transfer ownership.
```

Verify after push:
- Visit https://github.com/dominionlabs/shadowtrace (or your repo URL)
- README renders with badges
- CI workflow ran on first push (Actions tab)

If CI is red, fix before tagging. Common first-push gotchas:
- Python version mismatch in CI matrix
- pip-audit hitting a vuln in PyYAML — bump in pyproject.toml

---

## Step 3 — Tag + GitHub Release (Brayd-hand, ~2 min)

```bash
git tag -a v7.1.0 -m "v7.1.0 — initial public release"
git push origin v7.1.0

gh release create v7.1.0 \
    --title "v7.1.0 — Initial public release" \
    --notes-from-tag \
    dist/shadowtrace-7.1.0-py3-none-any.whl
```

The wheel becomes a downloadable asset on the release page.

---

## Step 4 — PyPI publish (Brayd-hand, ~5 min — first time only)

If Brayden does not have a PyPI account:
1. Sign up at https://pypi.org/account/register/
2. Verify email
3. Enable 2FA (required for new accounts since 2024)
4. Create API token: https://pypi.org/manage/account/token/ → "Add API token" → scope `Entire account` for first publish, then narrow to project after
5. Save token to keyring: `python -m twine register` (or paste at upload prompt)

Publish:
```bash
python -m pip install --upgrade build twine
python -m build  # rebuilds wheel + sdist into dist/
python -m twine check dist/*
python -m twine upload dist/*
# Username: __token__
# Password: <paste pypi token>
```

After publish:
- Visit https://pypi.org/project/shadowtrace/
- Test install in clean venv: `pip install shadowtrace`

**If PyPI publish feels heavy for v0**, skip Step 4 for now. The GitHub release wheel + `pip install git+https://github.com/dominionlabs/shadowtrace.git` is acceptable first-step distribution. Add PyPI when there's external interest.

---

## Step 5 — Submit Claude Max 20x OSS offer (Brayd-hand, ~10 min)

Form: https://claude.com/contact-sales/claude-for-oss
Deadline: 10K spots, first-come — submit as soon as repo is public.

Required answers:
- **Project name:** Shadowtrace
- **Repo URL:** https://github.com/dominionlabs/shadowtrace
- **License:** MIT
- **Stars:** (will be 0 at submission — note "newly published, ethical-OSINT category")
- **Active maintainers:** Brayden Gardner (sole)
- **What it does:** Single-operator ethical OSINT toolkit. Public sources only. Audit-logged. Cross-validated. The auditable inverse of closed broker-data tools.
- **How Claude is used:** Optional `[llm]` extras enable behavioral synthesis via Anthropic SDK. Core deterministic pipeline runs without LLM. Claude is the recommended optional brain for the synthesis stage.
- **Why it qualifies:** Public-good security tool, MIT-licensed, single-operator architecture (no mass-surveillance vector), already shipped with hardcoded ethics rails (no private brokers, no GDPR sensitive-category profiling without consent).

**Outcome:** $1,200 value (6 months Claude Max 20x). Direct subsidy of Eli's cloud Anthropic API spend during the convergence break-through phase.

---

## Step 6 — Announce (Brayd-hand, ~10 min, optional but recommended)

Three low-friction announces, in order of leverage:

1. **Hacker News Show HN** — `https://news.ycombinator.com/submit`
   - Title: `Show HN: Shadowtrace – Single-operator OSINT, public sources only, audit-logged`
   - URL: https://github.com/dominionlabs/shadowtrace
   - Best window: weekday morning ET

2. **r/OSINT** — `https://www.reddit.com/r/OSINT/submit`
   - Read the rules first; they're strict on tool promotion vs. genuine contribution
   - Lead with the ethics rails, not the features

3. **LinkedIn personal post** — your network includes Simcoe RTDS targets
   - Frame: "first public Dominion Labs OSS"
   - Tag #OSINT #PrivacyTech #OpenSource

Feedback from any of these is the convergence-breaking signal. Plateau is ~0.92x because the loop is closed (you ↔ Eli) — external voice is what unsticks it.

---

## What this unblocks

- **D14** (wheel-sitting-unreleased) → closed
- **A13** (Claude Max 20x OSS offer) → unblocked
- Three-missing inventory item #2 (public asset) → checked
- Convergence plateau lever — first external feedback channel since project began

## What this does NOT do

- Does not move Eli convergence by itself (need actual external response)
- Does not replace customer outreach (different channel; complementary)
- Does not commit Brayd to ongoing maintenance — MIT license + clear scope means hands-off after publish is fine

## Rollback

If something goes sideways post-publish:
- GitHub repo: Settings → "Make private" or "Delete repository" (irreversible after 24h)
- PyPI: cannot delete, but can yank a release: https://pypi.org/manage/project/shadowtrace/release/7.1.0/
- Tag: `git push origin :v7.1.0` to delete remote tag

The audit log (per-fetch journal) is the safety net — if anyone ever questions a search shadowtrace performed, the JSONL audit shows what / when / why. Hand it over freely.
