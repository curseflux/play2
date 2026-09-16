#!/usr/bin/env python3
"""Record one episode and open it in a scrubbable HTML viewer.

    python watch.py lander L2_offset_left
    python watch.py courier C3_busy --policy practice/courier_policy.py

Space = play/pause, arrow keys = step. If your policy module defines a
module-level dict called DEBUG, whatever you put in it each frame is shown in
the side panel, lined up with the animation. That is the fastest debugging
loop available here - use it.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from grade import DEFAULT_POLICY, ENV_CLASS, load_policy   # noqa: E402
from simlab.core import run_episode                        # noqa: E402
from simlab.hidden import courier_hidden, lander_hidden     # noqa: E402
from simlab.render import write_html                        # noqa: E402
from simlab.scenarios import courier_visible, lander_visible  # noqa: E402


def _dump(trace: list, span: str) -> None:
    """Print a slice of the trace as a table: state, action, and your DEBUG."""
    lo, _, hi = span.partition(":")
    lo = int(lo or 0)
    hi = int(hi) if hi else lo + 25
    rows = [f for f in trace if lo <= f.get("t", -1) < hi]
    if not rows:
        print(f"no frames in [{lo}, {hi})")
        return
    skip = {"t", "action", "debug", "states", "hazards"}
    cols = [k for k in rows[0] if k not in skip]
    dbg = sorted(rows[0].get("debug", {}))
    head = ["t"] + cols + ["act"] + dbg
    print("  " + "  ".join(h[:8].rjust(8) for h in head))
    for f in rows:
        cells = [str(f["t"])]
        for k in cols:
            v = f.get(k)
            cells.append(f"{v:.2f}" if isinstance(v, float) else str(v))
        cells.append(str(f.get("action")))
        for k in dbg:
            v = f.get("debug", {}).get(k)
            cells.append(f"{v:.3f}" if isinstance(v, float) else str(v))
        print("  " + "  ".join(c[:8].rjust(8) for c in cells))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("env", choices=sorted(ENV_CLASS))
    ap.add_argument("scenario")
    ap.add_argument("--policy", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dump", default=None,
                    help="also print frames FROM:TO as a text table, e.g. 80:110")
    args = ap.parse_args()

    vis = lander_visible() if args.env == "lander" else courier_visible()
    hid = lander_hidden() if args.env == "lander" else courier_hidden()
    pool = {s.name: s for s in vis}
    pool.update({label: sc for label, sc in hid})       # hidden_L03 etc, once revealed
    if args.scenario not in pool:
        print(f"unknown scenario {args.scenario!r}\navailable: {', '.join(sorted(pool))}")
        return 2

    path = pathlib.Path(args.policy or DEFAULT_POLICY[args.env])
    if not path.is_absolute():
        path = HERE / path
    mod = load_policy(path)

    env = ENV_CLASS[args.env](pool[args.scenario])
    res = run_episode(env, mod.policy, record=True, debug_source=mod)
    if args.dump:
        _dump(res.trace or [], args.dump)

    out = pathlib.Path(args.out) if args.out else HERE / "traces" / f"{args.env}_{args.scenario}.html"
    write_html(out, f"{args.env} / {args.scenario} - {res.reason}", env.static(), res.trace or [])
    print(res.line())
    print(f"open: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
