#!/usr/bin/env python3
"""E2: long tool output — paste it all vs compress with fail-open + recovery handle."""
from __future__ import annotations

import json
import random
import re
import statistics as st
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, api_key, call  # noqa: E402

DENSE = ROOT / "skill" / "dense" / "dense.py"


def noise(n, rng):
    kinds = ["INFO request id={} handled in {}ms status=200",
             "DEBUG cache hit key=user:{} ttl={}s",
             "INFO worker {} picked job {}"]
    return [rng.choice(kinds).format(rng.randint(1, 9999), rng.randint(1, 900)) for _ in range(n)]


def make_cases():
    rng = random.Random(42)
    cases = []

    nginx = noise(120, rng) + [
        "2026-10-25T08:12:01Z [error] 771#0: *8821 upstream timed out (110: Connection timed out) while reading response header from upstream, upstream: \"http://10.0.4.11:8080/v1/orders?page=2\"",
        "2026-10-25T08:12:02Z [warn] an upstream response is buffered to a temporary file",
    ] + noise(60, rng)
    cases.append(("L1", "\n".join(nginx), "这个日志里哪个 upstream 超时了？端口号是多少？", ["8080", "10\\.0\\.4\\.11"]))

    pytest = noise(100, rng) + [
        "=========================== FAILURES ===========================",
        "    def test_order_total():",
        ">       assert order.total == 4498",
        "E       assert 4998 == 4498",
        "tests/test_orders.py:88: AssertionError",
        "========================= 1 failed, 41 passed in 3.42s =========================",
    ] + noise(80, rng)
    cases.append(("L2", "\n".join(pytest), "断言里的期望值和实际值分别是多少？", ["4998", "4498"]))

    k8s = noise(110, rng) + [
        "Last State:     Terminated",
        "  Reason:       OOMKilled",
        "  Exit Code:    137",
        "Limits:",
        "  memory:  512Mi",
        "Events:",
        "  Warning  BackOff  2m (x31 over 41m)  kubelet  Back-off restarting failed container",
    ] + noise(70, rng)
    cases.append(("L3", "\n".join(k8s), "容器为什么被杀？内存上限是多少？", ["oom", "512"]))

    npm = noise(90, rng) + [
        "npm ERR! code ERESOLVE",
        "npm ERR! Found: react@18.3.1",
        "npm ERR! peer react@\"^17.0.0\" from react-beautiful-dnd@13.1.1",
        "npm ERR! Fix the upstream dependency conflict, or retry",
    ] + noise(90, rng)
    cases.append(("L4", "\n".join(npm), "冲突的是哪两个 react 版本？", ["17", "18"]))

    java = noise(100, rng) + [
        "Exception in thread \"main\" java.lang.NullPointerException",
        "\tat com.acme.OrderService.computeTotal(OrderService.java:42)",
        "\tat com.acme.Main.main(Main.java:11)",
    ] + noise(70, rng)
    cases.append(("L5", "\n".join(java), "抛的是什么异常？在哪个文件第几行？", ["nullpointerexception", "42"]))

    return cases


def compress(text):
    out = subprocess.run([sys.executable, str(DENSE), "compress"], input=text,
                         capture_output=True, text=True, encoding="utf-8")
    return out.stdout, out.stderr.strip()


def main():
    key = api_key()
    cases = make_cases()
    rows = []
    for cid, text, question, checks in cases:
        packed, note = compress(text)
        handle = re.search(r"handle=([0-9a-f]+)", note)
        for arm in ("raw", "dense"):
            body = text if arm == "raw" else packed
            if arm == "dense" and handle:
                body += f"\n\n[compressed by dense; original bytes: dense recover {handle.group(1)}]"
            system = "Answer from the log. Cite the exact values."
            user = f"LOG:\n{body}\n\nQUESTION: {question}"
            for rep in range(3):
                res = call(system, user, key)
                ans = res.get("text") or ""
                hit = all(re.search(p, ans, re.I) for p in checks)
                rows.append({"case": cid, "arm": arm, "rep": rep, "ok": res["ok"], "answer": ans,
                             "correct": hit, "log_chars": len(text), "sent_chars": len(body),
                             "input_tokens": res["usage"].get("prompt_tokens", 0),
                             "output_tokens": res["usage"].get("completion_tokens", 0),
                             "handle": handle.group(1) if handle else None})
    out = ROOT / "bench" / "results" / "exp_longctx.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")

    print("| arm | 平均输入 token | 正确率 |")
    print("|---|---:|---:|")
    for arm in ("raw", "dense"):
        rs = [r for r in rows if r["arm"] == arm and r["ok"]]
        print(f"| {arm} | {st.mean(r['input_tokens'] for r in rs):.0f} | {100*st.mean(r['correct'] for r in rs):.0f}% |")
    for cid, text, _, _ in cases:
        packed, note = compress(text)
        print(f"  {cid}: {len(text)//4} tok -> {len(packed)//4} tok  {note.split(']')[0]}]")
    print("\nwrong answers:")
    for r in rows:
        if not r["correct"]:
            print(f"  {r['case']} {r['arm']}: {r['answer'][:120]}")


if __name__ == "__main__":
    main()
