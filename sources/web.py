"""Public web fetch via urllib. robots.txt compliant.

Used for generic URL fetches the resolver / seed stage points at.
Respects robots.txt, times out at 10s, UA identifies the tool.
"""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
import urllib.robotparser

from .base import Record

UA = "shadowtrace/7.0 (+personal OSINT; solo-operator; contact=brayd@dominionlabs)"
TIMEOUT = 10
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _robots_ok(url: str) -> bool:
    try:
        parts = urllib.parse.urlparse(url)
        root = f"{parts.scheme}://{parts.netloc}"
        rp = _robots_cache.get(root)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{root}/robots.txt")
            try:
                rp.read()
            except Exception:
                return True  # if robots unreachable, default allow
            _robots_cache[root] = rp
        return rp.can_fetch(UA, url)
    except Exception:
        return True


def fetch(url: str) -> str | None:
    if not _robots_ok(url):
        return None
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read(2_000_000)
            try:
                return raw.decode("utf-8", errors="replace")
            except Exception:
                return raw.decode("latin-1", errors="replace")
    except Exception:
        return None


_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def strip_html(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.S | re.I)
    s = _TAG.sub(" ", s)
    s = html.unescape(s)
    return _WS.sub(" ", s).strip()


def harvest(url: str, subject_hint: str, authority: float = 0.4) -> list[Record]:
    body = fetch(url)
    if not body:
        return []
    text = strip_html(body)
    if not text:
        return []
    snippet = text[:1800]
    return [
        Record(
            source="web",
            kind="page",
            subject_hint=subject_hint,
            content=snippet,
            url=url,
            authority=authority,
            confidence=0.55,
            meta={"byte_len": len(body), "text_len": len(text)},
        )
    ]
