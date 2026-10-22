"""Brain (Opus 5.5 -> free): Gemini free tier if a key is in env, else offline template.

The key is read from the environment only, used in one HTTPS call, and never
stored, logged, or printed.
"""
from __future__ import annotations
import dataclasses, json, os, re, urllib.request, urllib.error


@dataclasses.dataclass
class BrainResult:
    mode: str                 # "gemini" | "offline-template"
    tokens: int
    cost_usd: float           # always 0.0 on the free tier / offline
    plan: dict

    def to_dict(self):
        return dataclasses.asdict(self)


def extract_product_name(goal: str) -> str:
    """Deterministic: prefer a capitalised product token, else a sensible default."""
    if not goal:
        return "Night Product"
    # 'for X' wins: in 'Build a page for ClipPay' the product is ClipPay, not Build.
    m = re.search(r"\bfor\s+([A-Z][A-Za-z0-9_-]{2,})", goal)
    if m:
        return m.group(1)
    stop = {"Build", "Make", "Create", "Design", "Write", "The", "This"}
    for m in re.finditer(r"\b([A-Z][A-Za-z0-9]{2,}(?:[A-Z][a-z]+)?)\b", goal):
        if m.group(1) not in stop:
            return m.group(1)
    m = re.search(r"for\s+([A-Za-z0-9_-]{2,})", goal, re.I)
    if m:
        return m.group(1)
    return "Night Product"


def offline_plan(goal: str) -> dict:
    product = extract_product_name(goal)
    return {
        "product_name": product,
        "goal": goal,
        "headline": f"{product} — built overnight, honestly.",
        "steps": ["research", "decide", "build landing page", "draft social thread", "log to vault"],
        "features": [
            "One goal in, one morning report out",
            "Hard budget gate: nothing over the cap, ever",
            "Every step and every cost logged",
        ],
        "proposed_spends": [{"item": "domain", "amount_usd": 49.0}],
    }


def _gemini_plan(goal: str, model: str, api_key: str):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent?key={api_key}")
    prompt = ("Return ONLY JSON with keys product_name, headline, features (3 short strings) "
              f"for this goal: {goal}")
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    tokens = int(data.get("usageMetadata", {}).get("totalTokenCount", 0))
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    m = re.search(r"\{.*\}", text, re.S)
    parsed = json.loads(m.group(0)) if m else {}
    plan = offline_plan(goal)
    for k in ("product_name", "headline", "features"):
        if parsed.get(k):
            plan[k] = parsed[k]
    return plan, tokens


def plan(goal: str, model: str = "gemini-2.5-flash") -> BrainResult:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        try:
            p, tokens = _gemini_plan(goal, model, key)
            return BrainResult("gemini", tokens, 0.0, p)
        except Exception:
            pass  # fall through to offline; never leak the key or the failing URL
    return BrainResult("offline-template", 0, 0.0, offline_plan(goal))
