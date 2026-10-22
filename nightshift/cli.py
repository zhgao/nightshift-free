"""One-command CLI: python3 -m nightshift run --goal "..." """
from __future__ import annotations
import argparse, os
from datetime import datetime
from .pipeline import load_config, run_pipeline


def main(argv=None):
    ap = argparse.ArgumentParser(prog="nightshift", description="NightShift Free v0.1")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--goal", required=True)
    r.add_argument("--out", default=None, help="output folder (default runs/<timestamp>)")
    r.add_argument("--config", default=None)
    r.add_argument("--target", default=".", help="local directory for REA-lite research")
    r.add_argument("--signals", default=None, help="local signals text/markdown file (optional)")
    args = ap.parse_args(argv)
    out = args.out or os.path.join("runs", datetime.now().strftime("%Y%m%d-%H%M%S"))
    summary = run_pipeline(args.goal, out, config=load_config(args.config),
                           target_dir=args.target, signals_file=args.signals)
    print(f"\n== Morning report: {summary['report']} | cost ${summary['total_cost']:.2f} "
          f"| {summary['duration_s']:.2f}s | signups 0 (not connected) ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
