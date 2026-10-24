"""Connector/Orchestrator (Dots -> local): 6-step runner with checkpoints.

state.json is written after every step so a failed run can resume: steps
already marked done are skipped on the next run with the same output folder.
"""
from __future__ import annotations
import json, os, time
from datetime import datetime

from . import brain as brain_mod
from . import decider as decider_mod
from . import researcher, scout, vault
from .builder import landing_html, report_html

DEFAULT_CONFIG = {"budget_cap_usd": 10.0, "domain_proposed_usd": 49.0,
                  "gemini_model": "gemini-3.5-flash-lite", "keywords": scout.DEFAULT_KEYWORDS}


def load_config(path=None):
    cfg = dict(DEFAULT_CONFIG)
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    return cfg


class Logger:
    def __init__(self, path):
        self.path = path

    def log(self, msg):
        line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
        print(line, flush=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def run_pipeline(goal, out_dir, config=None, target_dir=".", signals_file=None):
    cfg = config or dict(DEFAULT_CONFIG)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "build"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "vault"), exist_ok=True)
    log = Logger(os.path.join(out_dir, "night-shift.log"))
    state_path = os.path.join(out_dir, "state.json")
    state = {"completed": [], "artifacts": {}}
    if os.path.isfile(state_path):
        try:
            with open(state_path, encoding="utf-8") as fh:
                state = json.load(fh)
            log.log(f"resume: {len(state['completed'])} step(s) already done, skipping them")
        except (OSError, json.JSONDecodeError):
            state = {"completed": [], "artifacts": {}}
    steps_summary, start = [], time.time()

    def checkpoint(name, status, detail, artifact=None):
        steps_summary.append({"name": name, "status": status, "detail": detail})
        if name not in state["completed"]:
            state["completed"].append(name)
        if artifact:
            state["artifacts"][name] = artifact
        with open(state_path, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)
        log.log(f"[{name}] {status} — {detail}")

    def done(name):
        return name in state["completed"]

    # 1 Brain
    brain_file = os.path.join(out_dir, "plan.json")
    if done("brain") and os.path.isfile(brain_file):
        with open(brain_file, encoding="utf-8") as fh:
            saved = json.load(fh)
        plan, brain_mode, tokens = saved["plan"], saved["mode"], saved["tokens"]
        steps_summary.append({"name": "brain", "status": "done (resumed)", "detail": brain_mode})
    else:
        br = brain_mod.plan(goal, model=cfg.get("gemini_model", "gemini-3.5-flash-lite"))
        plan, brain_mode, tokens = br.plan, br.mode, br.tokens
        with open(brain_file, "w", encoding="utf-8") as fh:
            json.dump({"mode": brain_mode, "tokens": tokens, "cost_usd": 0.0, "plan": plan}, fh, indent=2, ensure_ascii=False)
        checkpoint("brain", "done", f"mode={brain_mode} tokens={tokens} cost=$0.00", "plan.json")
    product = plan.get("product_name", "Night Product")

    for _name in ("researcher", "decider", "builder", "scout"):
        if done(_name):
            steps_summary.append({"name": _name, "status": "done (resumed)",
                                  "detail": "checkpoint in state.json"})

    # 2 Researcher (REA-lite)
    if not done("researcher"):
        ev = researcher.analyze(target_dir, goal)
        with open(os.path.join(out_dir, "research.md"), "w", encoding="utf-8") as fh:
            fh.write(researcher.render_markdown(ev))
        checkpoint("researcher", "done",
                   f"REA-lite: {ev['total_files']} files, {len(ev['todos'])} TODOs", "research.md")

    # 3 Decider
    if not done("decider"):
        decisions = decider_mod.run_all_decisions(
            goal, product, float(cfg["budget_cap_usd"]), float(cfg["domain_proposed_usd"]))
        with open(os.path.join(out_dir, "decisions.json"), "w", encoding="utf-8") as fh:
            json.dump([d.to_dict() for d in decisions], fh, indent=2)
        dom = decisions[1]
        checkpoint("decider", "done",
                   f"budget gate cap=${float(cfg['budget_cap_usd']):.0f}; domain -> {dom.answer} (draft, $0 spent)",
                   "decisions.json")

    # 4 Builder
    landing_path = os.path.join(out_dir, "build", "index.html")
    if not done("builder"):
        with open(landing_path, "w", encoding="utf-8") as fh:
            fh.write(landing_html(plan))
        checkpoint("builder", "done", "landing page build/index.html", "build/index.html")

    # 5 Scout (draft only)
    if not done("scout"):
        draft, _posts = scout.render_thread_draft(product, goal, plan.get("headline", product))
        with open(os.path.join(out_dir, "social_draft.md"), "w", encoding="utf-8") as fh:
            fh.write(draft)
        sig = scout.scan_signals(signals_file, cfg.get("keywords"))
        with open(os.path.join(out_dir, "signals.json"), "w", encoding="utf-8") as fh:
            json.dump(sig, fh, indent=2)
        checkpoint("scout", "done",
                   f"3-post draft written, nothing posted; signals: {sig['note']}", "social_draft.md")

    duration = round(time.time() - start, 2)
    entries = [{"step": "brain", "item": f"LLM ({brain_mode})", "cost_usd": 0.0},
               {"step": "decider", "item": "domain/purchase (gated, not bought)", "cost_usd": 0.0},
               {"step": "hosting", "item": "static landing page (local build)", "cost_usd": 0.0}]
    summary = {"product": product, "goal": goal, "steps": steps_summary,
               "duration_s": duration, "tokens": tokens, "brain_mode": brain_mode,
               "total_cost": 0.0, "signups": 0, "revenue_usd": 0}

    # 6 Logger (vault + ledger + report)
    vault.write_ledger(out_dir, entries, 0.0)
    vault_path = vault.write_vault_note(os.path.join(out_dir, "vault"),
                                        datetime.now().strftime("%Y-%m-%d"), summary)
    with open(os.path.join(out_dir, "report.html"), "w", encoding="utf-8") as fh:
        fh.write(report_html(summary))
    checkpoint("logger", "done", f"vault note + ledger total $0.00; {os.path.basename(vault_path)}",
               "report.html")
    summary["vault_note"] = vault_path
    summary["report"] = os.path.join(out_dir, "report.html")
    log.log(f"done in {duration:.2f}s — total cost $0.00 — report: {summary['report']}")
    return summary
