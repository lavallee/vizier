"""CLI: python -m vizier.gate <bundle_dir> [<bundle_dir> ...]

Each bundle gets a `draft/vizier-decision.json` written into it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vizier.gate import needs_charts, write_decision


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="vizier.gate")
    p.add_argument("bundle_dirs", nargs="+", type=Path)
    p.add_argument("--out-name", default="vizier-decision.json")
    args = p.parse_args(argv)

    rc = 0
    for bd in args.bundle_dirs:
        if not bd.exists():
            print(f"!! missing bundle: {bd}", file=sys.stderr)
            rc = 1
            continue
        decision = needs_charts(bd)
        out = bd / "draft" / args.out_name
        write_decision(decision, out)
        verdict_lines = []
        for v in decision.verdicts:
            mark = "KEEP" if v.keep else "drop"
            verdict_lines.append(f"    [{mark}] {v.candidate.get('title', '?')} — {v.reason[:80]}")
        print(
            f"{bd.name}: {'YES' if decision.needs_charts else 'no'} "
            f"({decision.n_kept}/{decision.n_candidates} kept) — {decision.summary[:120]}"
        )
        for line in verdict_lines:
            print(line)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
