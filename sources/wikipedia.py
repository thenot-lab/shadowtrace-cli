"""Wikipedia REST API - high-authority encyclopedia hits."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

from . import web as _web
from .base import Record

API = "https://en.wikipedia.org/w/api.php"
SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def _get_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": _web.UA, "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=_web.TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def search(query: str, limit: int = 3) -> list[Record]:
    q = urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json",
        }
    )
    data = _get_json(f"{API}?{q}") or {}
    results = (data.get("query") or {}).get("search") or []
    out: list[Record] = []
    for hit in results[:limit]:
        title = hit.get("title")
        if not title:
            continue
        slug = urllib.parse.quote(title.replace(" ", "_"))
        summary = _get_json(f"{SUMMARY}{slug}") or {}
        extract = summary.get("extract") or _web.strip_html(hit.get("snippet") or "")
        out.append(
            Record(
                source="wikipedia",
                kind="bio",
                subject_hint=query,
                content=f"{title}: {extract}",
                url=(summary.get("content_urls") or {}).get("desktop", {}).get("page")
                or f"https://en.wikipedia.org/wiki/{slug}",
                authority=0.9,
                confidence=0.75,
                meta={
                    "title": title,
                    "pageid": hit.get("pageid"),
                    "wordcount": hit.get("wordcount"),
                },
            )
        )
    return out
