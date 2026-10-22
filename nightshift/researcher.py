"""Researcher (REA -> REA-lite): evidence from a local target directory only.

This is NOT full reverse engineering. It reads file names/types, a README
excerpt, and TODO/FIXME markers, and reports exactly what it found.
"""
from __future__ import annotations
import collections, os

MAX_FILES = 2000
TEXT_EXTS = {".py", ".md", ".txt", ".js", ".ts", ".json", ".html", ".css", ".java"}


def analyze(target_dir: str, goal: str = "") -> dict:
    target = target_dir or "."
    files, by_ext, todos = [], collections.Counter(), []
    readme_excerpt = ""
    if os.path.isdir(target):
        for root, dirs, names in os.walk(target):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules"}]
            for n in sorted(names):
                path = os.path.join(root, n)
                rel = os.path.relpath(path, target)
                files.append(rel)
                by_ext[os.path.splitext(n)[1].lower() or "(none)"] += 1
                if len(files) >= MAX_FILES:
                    break
                if os.path.splitext(n)[1].lower() in TEXT_EXTS:
                    try:
                        with open(path, encoding="utf-8", errors="ignore") as fh:
                            for i, line in enumerate(fh, 1):
                                if "TODO" in line or "FIXME" in line:
                                    todos.append(f"{rel}:{i}: {line.strip()[:120]}")
                                if n.lower().startswith("readme") and i <= 20:
                                    readme_excerpt += line
                    except OSError:
                        pass
            if len(files) >= MAX_FILES:
                break
    return {"target_dir": target, "goal": goal, "total_files": len(files),
            "by_ext": dict(by_ext.most_common()), "files_sample": files[:50],
            "todos": todos[:50], "readme_excerpt": readme_excerpt.strip()[:800]}


def render_markdown(ev: dict) -> str:
    lines = ["# Research (REA-lite)", "",
             "> Local evidence only — file tree, types, README, TODOs. "
             "Not full reverse engineering.", "",
             f"- Target: `{ev['target_dir']}`", f"- Goal: {ev['goal'] or '(none)'}",
             f"- Files found: **{ev['total_files']}**", "", "## File types"]
    for ext, n in ev["by_ext"].items():
        lines.append(f"- `{ext}`: {n}")
    lines += ["", "## Files (sample)"]
    lines += [f"- `{f}`" for f in ev["files_sample"]] or ["- (none)"]
    lines += ["", "## TODO / FIXME"]
    lines += [f"- {t}" for t in ev["todos"]] or ["- (none found)"]
    lines += ["", "## README excerpt", ev["readme_excerpt"] or "(no README found)"]
    return "\n".join(lines) + "\n"
