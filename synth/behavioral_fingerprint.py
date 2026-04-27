"""Behavioral fingerprinting - writing style, posting rhythm, timezone inference.

Master-investigator technique: subtle patterns in HOW someone writes/acts
often identify them more reliably than WHAT they write. We extract:
  - lexical: avg sentence length, punctuation density, type/token ratio
  - stylistic: sentence openers, hedging markers, confidence markers
  - temporal: posting-time distribution (when timestamps available)
  - platform affinity: which sources over-index on this subject
"""
from __future__ import annotations
import re, statistics
from collections import Counter
from typing import List, Dict, Any
from ..sources.base import Record

HEDGES = ("might", "perhaps", "possibly", "arguably", "reportedly", "seems", "appears")
INTENSIFIERS = ("very", "extremely", "absolutely", "clearly", "obviously", "definitely")
OPENERS = ("I ", "We ", "The ", "This ", "That ", "In ", "On ", "At ", "When ", "If ")


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _timestamps(records: List[Record]) -> List[str]:
    """Pull ISO-like timestamps from record metadata."""
    out: List[str] = []
    for r in records:
        t = r.meta.get("timestamp") or r.meta.get("published") or r.meta.get("created_at")
        if t and isinstance(t, str):
            out.append(t)
    return out


def _hour_from_iso(iso: str) -> int | None:
    m = re.search(r"T(\d{2}):", iso)
    return int(m.group(1)) if m else None


def fingerprint(records: List[Record]) -> Dict[str, Any]:
    all_text = "\n\n".join(r.content for r in records if r.content)
    if not all_text.strip():
        return {"insufficient_data": True, "sample_size": 0}

    sents = _split_sentences(all_text)
    words = re.findall(r"[A-Za-z']+", all_text)
    word_lens = [len(w) for w in words] or [0]
    sent_lens = [len(s.split()) for s in sents] or [0]

    types = len({w.lower() for w in words})
    tokens = len(words) or 1
    ttr = round(types / tokens, 3)

    puncts = sum(1 for c in all_text if c in ".,;:!?—-()")
    punct_density = round(puncts / max(1, len(all_text)), 4)

    hedge_n = sum(1 for w in words if w.lower() in HEDGES)
    intens_n = sum(1 for w in words if w.lower() in INTENSIFIERS)

    opener_counts: Counter[str] = Counter()
    for s in sents:
        for op in OPENERS:
            if s.startswith(op.strip()):
                opener_counts[op.strip()] += 1
                break

    hours = [h for h in (_hour_from_iso(t) for t in _timestamps(records)) if h is not None]
    hour_hist: Dict[int, int] = {}
    for h in hours:
        hour_hist[h] = hour_hist.get(h, 0) + 1

    inferred_tz_offset = None
    if hour_hist:
        # assume peak activity between 09-21 local -> shift suggestion
        peak = max(hour_hist.items(), key=lambda kv: kv[1])[0]
        target_peak = 14  # 2pm local
        inferred_tz_offset = (target_peak - peak) % 24
        if inferred_tz_offset > 12:
            inferred_tz_offset -= 24

    source_affinity: Counter[str] = Counter()
    for r in records:
        key = r.source.split(":", 1)[-1]
        source_affinity[key] += 1

    return {
        "sample_size": len(records),
        "word_count": len(words),
        "sentence_count": len(sents),
        "lexical": {
            "avg_word_len": round(statistics.mean(word_lens), 2) if word_lens else 0,
            "avg_sentence_len": round(statistics.mean(sent_lens), 2) if sent_lens else 0,
            "type_token_ratio": ttr,
            "punct_density": punct_density,
        },
        "stylistic": {
            "hedge_rate_per_1k": round(hedge_n / max(1, tokens) * 1000, 2),
            "intensifier_rate_per_1k": round(intens_n / max(1, tokens) * 1000, 2),
            "top_sentence_openers": opener_counts.most_common(5),
        },
        "temporal": {
            "timestamp_samples": len(hours),
            "hour_histogram": hour_hist,
            "inferred_tz_offset_hours": inferred_tz_offset,
        },
        "platform_affinity": source_affinity.most_common(10),
    }
