"""Scout (Grok Bot -> free draft-only): thread draft + local signals scan.

Never posts anything. Signals come only from a local file the user provides.
"""
from __future__ import annotations
import os

DEFAULT_KEYWORDS = ["pricing", "pain", "need", "want", "stripe", "churn", "expensive", "slow"]


def generate_thread(product: str, goal: str, headline: str):
    return [
        f"1/ Built overnight with NightShift Free: {product}. Goal: {goal} — here's what actually happened, with real numbers only.",
        f"2/ {headline} Landing page generated, budget gate enforced ($0 spent), every step logged to a Markdown vault.",
        "3/ Signups so far: not connected, so I'm claiming 0. No auto-post, no fake metrics. Code is free and open source. (draft)",
    ]


def render_thread_draft(product, goal, headline):
    posts = generate_thread(product, goal, headline)
    body = "\n\n".join(posts)
    return ("# Social thread — DRAFT ONLY (never auto-posted)\n\n"
            f"{body}\n"), posts


def scan_signals(signals_path: str | None, keywords=None):
    kws = keywords or DEFAULT_KEYWORDS
    if not signals_path:
        return {"connected": False, "note": "no signals connected", "hits": []}
    if not os.path.isfile(signals_path):
        return {"connected": False, "note": f"signals file not found: {signals_path}", "hits": []}
    with open(signals_path, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    low = text.lower()
    hits = [{"keyword": k, "count": low.count(k.lower())} for k in kws if low.count(k.lower())]
    hits.sort(key=lambda h: -h["count"])
    return {"connected": True, "note": f"scanned local file {signals_path}", "hits": hits}
