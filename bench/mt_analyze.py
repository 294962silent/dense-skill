#!/usr/bin/env python3
"""Score multi-turn runs: total billed tokens, per-turn curve, final-answer fidelity."""
import json
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = json.loads((ROOT / "bench" / "multiturn_tasks.json").read_text(encoding="utf-8"))
checks = {t["id"]: t["checks"]["must_include"] for t in spec["tasks"]}

rows = [json.loads(l) for l in Path(ROOT / "bench" / "results" / "multiturn.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
by_arm = defaultdict(list)
for r in rows:
    if not r["ok"]:
        continue
    final = r["final_text"] or ""
    r["facts"] = sum(1 for p in checks[r["task_id"]] if re.search(p, final, re.I)) / len(checks[r["task_id"]])
    r["pass"] = r["facts"] == 1.0
    by_arm[r["arm"]].append(r)


def boot(vals, n=2000):
    if len(vals) < 2:
        return float("nan"), float("nan")
    rng = random.Random(11)
    s = sorted(st.mean(rng.choices(vals, k=len(vals))) for _ in range(n))
    return s[int(0.025 * n)], s[int(0.975 * n) - 1]


print("| arm | billed/会话 | 输入/会话 | 每轮 billed | pass | facts |")
print("|---|---:|---:|---|---:|---:|")
for arm, rs in by_arm.items():
    turns = [sum(t["usage"].get("completion_tokens", 0) for t in r["turns"]) for r in rs]
    curve = [st.mean(r["turns"][i]["usage"].get("completion_tokens", 0) for r in rs if len(r["turns"]) > i) for i in range(5)]
    print(
        f"| {arm} | {st.mean(turns):.0f} | {st.mean(r['input_total'] for r in rs):.0f} | "
        f"{' / '.join(f'{c:.0f}' for c in curve)} | {100*st.mean(r['pass'] for r in rs):.1f}% | "
        f"{100*st.mean(r['facts'] for r in rs):.1f}% |"
    )

base = by_arm.get("terse")
if base:
    print("\n相对 terse：")
    for arm, rs in by_arm.items():
        if arm == "terse":
            continue
        d = 100 * (st.mean(r["billed_total"] for r in rs) - st.mean(r["billed_total"] for r in base)) / st.mean(r["billed_total"] for r in base)
        print(f"  {arm}: billed {d:+.1f}%")
