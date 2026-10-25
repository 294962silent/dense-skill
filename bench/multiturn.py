#!/usr/bin/env python3
"""Multi-turn runner: same task, scripted turns, per-turn token accounting."""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, api_key, build_arms, call, MODEL, TEMPERATURE  # noqa: E402


def converse(system: str, turns: list[str], key: str) -> dict:
    messages = [{"role": "system", "content": system}] if system else []
    per_turn = []
    for text in turns:
        messages.append({"role": "user", "content": text})
        res = call_simple(messages, key)
        per_turn.append(res)
        if not res["ok"]:
            break
        messages.append({"role": "assistant", "content": res["text"]})
    return {"ok": all(t["ok"] for t in per_turn), "turns": per_turn}


def call_simple(messages, key):
    import urllib.request

    payload = json.dumps(
        {"model": MODEL, "messages": messages, "temperature": TEMPERATURE, "max_tokens": 1024, "stream": False}
    ).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "opencode/1.0",
        "Authorization": f"Bearer {key}",
        "x-opencode-session": str(uuid.uuid4()),
    }
    last = None
    for attempt in range(3):
        started = time.time()
        try:
            req = urllib.request.Request("https://opencode.ai/inference/go/openai/v1/chat/completions", data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return {
                "ok": True,
                "text": body["choices"][0]["message"].get("content") or "",
                "usage": body.get("usage", {}),
                "latency_ms": int((time.time() - started) * 1000),
            }
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * (attempt + 1))
    return {"ok": False, "error": last, "text": "", "usage": {}, "latency_ms": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=4)
    ap.add_argument("--arms", default="terse,dense,dense_mt")
    ap.add_argument("--out", default="bench/results/multiturn.jsonl")
    args = ap.parse_args()

    key = api_key()
    tasks = json.loads((ROOT / "bench" / "multiturn_tasks.json").read_text(encoding="utf-8"))["tasks"]
    arms = build_arms(args.arms.split(","))
    jobs = [(a, t, r) for a in arms for t in tasks for r in range(args.reps)]
    print(f"arms={list(arms)} tasks={len(tasks)} reps={args.reps} conversations={len(jobs)}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(converse, arms[a], t["turns"], key): (a, t, r) for a, t, r in jobs}
        done = 0
        for fut in as_completed(futures):
            arm, task, rep = futures[fut]
            res = fut.result()
            rec = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "model": MODEL,
                "arm": arm,
                "task_id": task["id"],
                "rep": rep,
                "ok": res["ok"],
                "turns": res["turns"],
                "billed_total": sum(t["usage"].get("completion_tokens", 0) for t in res["turns"] if t["ok"]),
                "input_total": sum(t["usage"].get("prompt_tokens", 0) for t in res["turns"] if t["ok"]),
                "final_text": res["turns"][-1]["text"] if res["turns"] else "",
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            done += 1
            if done % 5 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)}", flush=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
