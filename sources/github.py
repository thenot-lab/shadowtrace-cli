"""GitHub public API source - no auth for unauth rate-limited endpoints.

Search users, fetch profile, list repos. Authority 0.75 (structured, authoritative).
"""
from __future__ import annotations
import json, urllib.request, urllib.parse
from typing import List
from .base import Record
from . import web as _web  # reuse UA / timeout

API = "https://api.github.com"


def _get(path: str) -> dict | list | None:
    url = API + path
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": _web.UA,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        with urllib.request.urlopen(req, timeout=_web.TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def search_user(name_or_email: str, limit: int = 3) -> List[Record]:
    q = urllib.parse.quote(name_or_email)
    data = _get(f"/search/users?q={q}&per_page={limit}")
    out: list[Record] = []
    if not isinstance(data, dict):
        return out
    for u in (data.get("items") or [])[:limit]:
        login = u.get("login")
        if not login:
            continue
        profile = _get(f"/users/{login}") or {}
        bio = profile.get("bio") or ""
        content = " | ".join(x for x in [
            f"login={login}",
            f"name={profile.get('name') or ''}",
            f"company={profile.get('company') or ''}",
            f"blog={profile.get('blog') or ''}",
            f"location={profile.get('location') or ''}",
            f"followers={profile.get('followers', 0)}",
            f"public_repos={profile.get('public_repos', 0)}",
            f"bio={bio}",
        ] if x)
        out.append(Record(
            source="github",
            kind="profile",
            subject_hint=name_or_email,
            content=content,
            url=profile.get("html_url") or u.get("html_url"),
            ts_iso=profile.get("created_at"),
            authority=0.75,
            confidence=0.4 if (profile.get("followers") or 0) < 5 else 0.7,
            meta={
                "login": login,
                "followers": profile.get("followers"),
                "public_repos": profile.get("public_repos"),
                "company": profile.get("company"),
                "location": profile.get("location"),
            },
        ))
    return out


def list_repos(login: str, limit: int = 5) -> List[Record]:
    data = _get(f"/users/{login}/repos?sort=updated&per_page={limit}")
    if not isinstance(data, list):
        return []
    out: list[Record] = []
    for r in data[:limit]:
        out.append(Record(
            source="github",
            kind="repo",
            subject_hint=login,
            content=f"{r.get('full_name')} stars={r.get('stargazers_count',0)} lang={r.get('language')} desc={r.get('description') or ''}",
            url=r.get("html_url"),
            ts_iso=r.get("updated_at"),
            authority=0.7,
            confidence=0.9,
            meta={"stars": r.get("stargazers_count"), "language": r.get("language")},
        ))
    return out
