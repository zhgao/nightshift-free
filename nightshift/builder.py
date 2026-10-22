"""Builder: static landing page + morning report card. Self-contained, offline."""
from __future__ import annotations
import html


def _esc(s):
    return html.escape(str(s))


def landing_html(plan: dict) -> str:
    p = plan.get("product_name", "Night Product")
    feats = "".join(f"<li>{_esc(f)}</li>" for f in plan.get("features", []))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(p)}</title>
<style>body{{background:#0b0e1a;color:#eef;font-family:system-ui,sans-serif;margin:0}}
main{{max-width:720px;margin:12vh auto;padding:0 20px}}h1{{font-size:44px;line-height:1.1}}
.accent{{color:#ff5fa2}}p{{color:#aab;font-size:18px}}ul{{line-height:1.9}}
.cta{{display:inline-block;background:#ff5fa2;color:#111;padding:12px 22px;border-radius:10px;
font-weight:700;text-decoration:none}}footer{{color:#778;margin-top:48px;font-size:13px}}</style>
</head><body><main>
<h1>{_esc(plan.get('headline', p))}</h1>
<p>Goal: {_esc(plan.get('goal',''))}</p>
<ul>{feats}</ul>
<a class="cta" href="#">Join the waitlist (draft — not connected)</a>
<footer>Built by NightShift Free v0.1 overnight. No payment connected. No signups claimed.</footer>
</main></body></html>
"""


def report_html(summary: dict) -> str:
    steps = "".join(
        f"<tr><td>{_esc(s['name'])}</td><td>{_esc(s['status'])}</td><td>{_esc(s.get('detail',''))}</td></tr>"
        for s in summary["steps"])
    dur = summary["duration_s"]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>NightShift Free — Morning Report</title>
<style>body{{background:#07070f;color:#eef;font-family:system-ui,sans-serif;margin:0}}
.card{{max-width:820px;margin:40px auto;background:#10101f;border:1px solid #2a2a44;
border-radius:16px;padding:28px}}h1{{margin:0 0 4px}}.sub{{color:#9cf}}
.grid{{display:flex;gap:14px;flex-wrap:wrap;margin:20px 0}}
.stat{{background:#17172b;border-radius:12px;padding:14px 18px;min-width:130px}}
.stat b{{font-size:24px;display:block}}.pink{{color:#ff5fa2}}table{{width:100%;border-collapse:collapse}}
td{{padding:7px 6px;border-bottom:1px solid #262640;color:#ccd}}footer{{color:#778;margin-top:18px}}</style>
</head><body><div class="card">
<div class="sub">NIGHTSHIFT FREE &middot; MERGED AI SETUP (FREE EDITION)</div>
<h1>Morning report — {_esc(summary['product'])}</h1>
<div>Goal: {_esc(summary['goal'])}</div>
<div class="grid">
<div class="stat">NIGHT SHIFT<b>{int(dur//60)}m {dur%60:.0f}s</b></div>
<div class="stat">COST<b class="pink">$0.00</b></div>
<div class="stat">TOKENS<b>{summary['tokens']}</b></div>
<div class="stat">SIGNUPS<b>0</b>not connected — no fabricated numbers</div>
<div class="stat">REVENUE<b>$0</b>not connected — no fabricated numbers</div>
</div>
<table>{steps}</table>
<footer>Mode: {_esc(summary['brain_mode'])} &middot; Cost ledger total: ${summary['total_cost']:.2f}
&middot; Social: draft only, nothing auto-posted &middot; Purchases: gated, nothing bought.</footer>
</div></body></html>
"""
