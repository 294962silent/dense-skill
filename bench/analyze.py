#!/usr/bin/env python3
"""Score a run: fidelity (deterministic regex checks) x output tokens."""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path: Path, spec: dict):
    checks = {t["id"]: t["checks"]["must_include"] for t in spec["tasks"]}
    limits = {t["id"]: t.get("max_words") for t in spec["tasks"]}
    ceremony = [re.compile(p) for p in spec["global_ceremony"]]
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if not rec.get("ok"):
            rec["pass"] = False
            rec["facts"] = 0.0
            rec["error_hit"] = True
            rows.append(rec)
            continue
        text = rec["text"]
        pats = checks[rec["task_id"]]
        matched = sum(1 for p in pats if re.search(p, text, re.I | re.M))
        ceremony_hit = any(p.search(text) for p in ceremony)
        limit = limits.get(rec["task_id"])
        over = bool(limit and len(text.split()) > limit)
        rec["facts"] = matched / len(pats)
        rec["pass"] = matched == len(pats) and not ceremony_hit
        rec["ceremony"] = ceremony_hit
        rec["over_length"] = over
        rec["words"] = len(text.split())
        rec["chars"] = len(text)
        rec["out_tokens"] = rec["usage"].get("completion_tokens", 0)
        rec["reasoning_tokens"] = (rec["usage"].get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
        rec["visible_tokens"] = len(text) // 4
        rec["in_tokens"] = rec["usage"].get("prompt_tokens", 0)
        rows.append(rec)
    return rows


def boot(vals, fn=st.mean, n=2000, alpha=0.05):
    if len(vals) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(7)
    stats = sorted(fn(rng.choices(vals, k=len(vals))) for _ in range(n))
    return stats[int(alpha / 2 * n)], stats[int((1 - alpha / 2) * n) - 1]


def fmt(x, nd=0):
    return "n/a" if x != x else f"{x:.{nd}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    spec = json.loads((ROOT / "bench" / "tasks.json").read_text(encoding="utf-8"))
    rows = load(Path(args.path), spec)

    arms = sorted({r["arm"] for r in rows})
    by_arm = defaultdict(list)
    for r in rows:
        by_arm[r["arm"]].append(r)

    lines = []
    lines.append(f"# Run report: {Path(args.path).name}\n")
    lines.append(f"model `{rows[0]['model']}` · temperature {rows[0]['temperature']} · n={len(rows)} calls\n")

    lines.append("## Arms (skill vs plain `Answer concisely.`)\n")
    lines.append("Billed = tokens charged (includes hidden reasoning). Visible = what the user reads.")
    lines.append("| arm | sys tok | pass % | facts % | billed out | visible out | reasoning | 95% CI (billed) | input tok | total tok | errors |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|")
    summary = {}
    for a in arms:
        rs = [r for r in by_arm[a] if not r.get("error_hit")]
        errs = sum(1 for r in by_arm[a] if r.get("error_hit"))
        if not rs:
            lines.append(f"| {a} | {by_arm[a][0]['system_tokens_approx']} | - | - | - | - | - | - | - | - | {errs} |")
            continue
        outs = [r["out_tokens"] for r in rs]
        passr = 100 * sum(r["pass"] for r in rs) / len(rs)
        facts = 100 * st.mean(r["facts"] for r in rs)
        lo, hi = boot(outs)
        summary[a] = {
            "sys_tokens": by_arm[a][0]["system_tokens_approx"],
            "pass": passr,
            "facts": facts,
            "out": st.mean(outs),
            "visible": st.mean(r["visible_tokens"] for r in rs),
            "reasoning": st.mean(r["reasoning_tokens"] for r in rs),
            "out_med": st.median(outs),
            "ci": (lo, hi),
            "inp": st.mean(r["in_tokens"] for r in rs),
            "total": st.mean(r["in_tokens"] + r["out_tokens"] for r in rs),
            "n": len(rs),
        }
        s = summary[a]
        lines.append(
            f"| {a} | {s['sys_tokens']} | {passr:.1f} | {facts:.1f} | {s['out']:.0f} | {s['visible']:.0f} | "
            f"{s['reasoning']:.0f} | {fmt(lo)}–{fmt(hi)} | {s['inp']:.0f} | {s['total']:.0f} | {errs} |"
        )

    lines.append("\n## Delta vs `terse`, paired by task (the honest comparison)\n")
    lines.append("| arm | billed change (95% CI over tasks) | visible change | pass-rate change (pp) | total-cost change |")
    lines.append("|---|---:|---:|---:|---:|")

    def per_task(arm, metric):
        d = defaultdict(list)
        for r in by_arm[arm]:
            if not r.get("error_hit"):
                d[r["task_id"]].append(r[metric])
        return {k: st.mean(v) for k, v in d.items()}

    base = summary.get("terse")
    for a in arms:
        s = summary.get(a)
        if not s or not base or a == "terse":
            continue
        ta, tt = per_task(a, "out_tokens"), per_task("terse", "out_tokens")
        common = sorted(set(ta) & set(tt))
        ratios = [100 * (ta[k] - tt[k]) / tt[k] for k in common if tt[k]]
        lo, hi = boot(ratios)
        point = 100 * (sum(ta[k] for k in common) - sum(tt[k] for k in common)) / sum(tt[k] for k in common)
        tp = per_task(a, "pass")
        tpb = per_task("terse", "pass")
        dpass = 100 * st.mean(tp[k] - tpb[k] for k in common)
        va, vt = per_task(a, "visible_tokens"), per_task("terse", "visible_tokens")
        vpoint = 100 * (sum(va[k] for k in common) - sum(vt[k] for k in common)) / sum(vt[k] for k in common)
        dtotal = 100 * (s["total"] - base["total"]) / base["total"]
        lines.append(
            f"| {a} | {point:+.1f}% ({lo:+.0f} … {hi:+.0f}) | {vpoint:+.1f}% | {dpass:+.1f} | {dtotal:+.1f}% |"
        )

    lines.append("\n## Dominance (pass rate ↑, output tokens ↓)\n")
    pts = [(a, summary[a]["out"], summary[a]["pass"]) for a in summary]
    front = []
    for a, out, p in pts:
        dominated = any((o <= out and pp >= p) and (o < out or pp > p) for b, o, pp in pts if b != a)
        if not dominated:
            front.append(a)
    lines.append("Non-dominated arms: " + ", ".join(sorted(front)) if front else "none")

    lines.append("\n## Per task\n")
    lines.append("| task | category | " + " | ".join(f"{a} pass/tok" for a in arms) + " |")
    lines.append("|---|---|" + "---|" * len(arms))
    for t in spec["tasks"]:
        cells = []
        for a in arms:
            rs = [r for r in by_arm[a] if r["task_id"] == t["id"] and not r.get("error_hit")]
            if not rs:
                cells.append("-")
                continue
            p = 100 * sum(r["pass"] for r in rs) / len(rs)
            tok = st.mean(r["out_tokens"] for r in rs)
            cells.append(f"{p:.0f}%/{tok:.0f}")
        lines.append(f"| {t['id']} | {t['category']} | " + " | ".join(cells) + " |")

    report = "\n".join(lines)
    out = Path(args.out) if args.out else Path(args.path).with_suffix(".report.md")
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
