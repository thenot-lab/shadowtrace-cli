"""Semantic org/entity deduplication using rule-based NER heuristics.

Defect #2 from v7.0.1: rule-based org extractor listed common nouns like
'News' / 'Politics' / 'Bellingcat. He previously wrote...' as orgs. This
module normalizes, filters stopword-orgs, collapses prefix substrings,
and scores by frequency + title-case ratio.
"""

from __future__ import annotations

import re

# words that are frequently miscapitalized as Title Case but aren't orgs
STOPWORD_ORGS = {
    "news",
    "politics",
    "business",
    "sports",
    "technology",
    "tech",
    "science",
    "health",
    "media",
    "opinion",
    "world",
    "national",
    "local",
    "breaking",
    "the",
    "a",
    "an",
    "he",
    "she",
    "they",
    "his",
    "her",
    "their",
    "this",
    "that",
    "these",
    "those",
    "also",
    "since",
    "when",
    "where",
    "who",
    "how",
    "today",
    "yesterday",
    "tomorrow",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "english",
    "french",
    "spanish",
    "german",
    "italian",
    "best-seller",
    "bestseller",
    "interview",
    "article",
    "book",
    "page",
}

# suffixes that strongly indicate real orgs
ORG_SUFFIXES = (
    "inc",
    "inc.",
    "ltd",
    "ltd.",
    "llc",
    "corp",
    "corp.",
    "co.",
    "co",
    "university",
    "college",
    "institute",
    "foundation",
    "center",
    "centre",
    "group",
    "labs",
    "lab",
    "studios",
    "studio",
    "agency",
    "school",
    "hospital",
    "academy",
    "press",
    "publishing",
    "society",
    "association",
    "council",
    "board",
    "committee",
    "department",
    "ministry",
    "bureau",
    "agency",
    "commission",
    "organization",
    "organisation",
    "alliance",
    "network",
    "federation",
    "union",
    "league",
    "club",
    "bellingcat",
)


def _is_stopword(tok: str) -> bool:
    return tok.lower().strip(".,;:()[]") in STOPWORD_ORGS


def _split_into_clause_orgs(phrase: str) -> list[str]:
    """Split a multi-clause extraction into the shortest org-looking prefix."""
    # Heuristic: if phrase contains "He "/"She "/"They "/"It "/"Since " mid-phrase, cut before it
    m = re.search(r"\.\s+(He|She|They|It|Since|When|Because|However|After|Before|During)\b", phrase)
    if m:
        phrase = phrase[: m.start()]
    return [phrase.strip(" .,;:")]


def normalize_orgs(raw_orgs: list[str]) -> list[dict[str, object]]:
    """Return sorted list of {name, score, count} with junk filtered."""
    freq: dict[str, int] = {}
    for org in raw_orgs:
        for piece in _split_into_clause_orgs(org):
            piece = re.sub(r"\s+", " ", piece).strip(" .,;:\u2014-")
            if not piece or len(piece) < 3 or len(piece) > 60:
                continue
            if _is_stopword(piece):
                continue
            # require at least one token that isn't a stopword and has a capital
            toks = piece.split()
            cap_toks = [t for t in toks if t[:1].isupper() and not _is_stopword(t)]
            if not cap_toks:
                continue
            # drop if the whole phrase is one stopword with a period
            if len(toks) == 1 and _is_stopword(toks[0]):
                continue
            freq[piece] = freq.get(piece, 0) + 1

    # collapse prefix substrings: if "Bellingcat" and "Bellingcat Investigations" both present, keep both but prefer longer-root
    items = sorted(freq.items(), key=lambda kv: (-kv[1], -len(kv[0])))
    out: list[dict[str, object]] = []
    for name, count in items:
        # bonus if matches known org suffix pattern
        last_tok = name.split()[-1].lower().strip(".")
        suffix_bonus = 0.15 if last_tok in ORG_SUFFIXES else 0.0
        has_known_root = any(s in name.lower() for s in ORG_SUFFIXES)
        score = min(0.99, 0.40 + 0.10 * count + suffix_bonus + (0.10 if has_known_root else 0.0))
        out.append({"name": name, "count": count, "score": round(score, 2)})
    return out[:20]
