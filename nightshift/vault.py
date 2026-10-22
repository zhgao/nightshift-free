"""Logger (Obsidian -> Markdown vault): vault note + honest cost ledger."""
from __future__ import annotations
import json, os


def write_vault_note(vault_dir: str, date_str: str, summary: dict) -> str:
    os.makedirs(vault_dir, exist_ok=True)
    path = os.path.join(vault_dir, f"{date_str}-night-shift.md")
    steps = "\n".join(
        f"- [[{s['name']}]] — {s['status']}: {s.get('detail','')}" for s in summary["steps"])
    note = f"""---
product: {summary['product']}
cost_usd: {summary['total_cost']:.2f}
tokens: {summary['tokens']}
---
# Night Shift — {date_str} — {summary['product']}

Goal: {summary['goal']}

## Steps
{steps}

## Costs
- Total (actual): **${summary['total_cost']:.2f}**
- Brain mode: {summary['brain_mode']} (free tier / offline = $0)
- Domain/purchase: gated by [[decider]] — nothing bought

## Honest metrics
- Signups: 0 — not connected, no fabricated numbers
- Revenue: $0 — not connected, no fabricated numbers

## Links
[[research]] · [[decisions]] · [[social_draft]] · [[report]]
"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(note)
    return path


def write_ledger(out_dir: str, entries: list, total: float) -> str:
    path = os.path.join(out_dir, "cost_ledger.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"entries": entries, "total_usd": round(total, 2)}, fh, indent=2)
    return path
