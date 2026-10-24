#!/usr/bin/env python3
"""A/B runner for output-compression skills.

Arms are built from real SKILL.md files so the comparison is honest:
the control is a plain "Answer concisely." prompt, and every skill arm is
that control plus the skill body (the delta is the skill, not generic terseness).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPOS = ROOT / "research" / "repos"
SKILL = ROOT / "skill" / "dense"
CRED = Path(os.path.expanduser("~/.dsh/.credentials.yaml"))

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://opencode.ai/inference/go/openai/v1").rstrip("/")
MODEL = os.environ.get("BENCH_MODEL", "deepseek-v4.1-flash")
TEMPERATURE = float(os.environ.get("BENCH_TEMP", "0.3"))
MAX_TOKENS = int(os.environ.get("BENCH_MAX_TOKENS", "1024"))

TERSE = "Answer concisely."

MICRO = """Respond like smart caveman. Cut all filler, keep technical substance.
- Drop articles (a, an, the), filler (just, really, basically, actually).
- Drop pleasantries (sure, certainly, happy to).
- No hedging. Fragments fine. Short synonyms.
- Technical terms stay exact. Code blocks unchanged.
- Pattern: [thing] [action] [reason]. [next step]."""


def api_key() -> str:
    for line in CRED.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("DEEPSEEK_API_KEY:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    raise SystemExit("DEEPSEEK_API_KEY not found in credentials")


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def build_arms(names: list[str]) -> dict[str, str]:
    arms: dict[str, str] = {}
    if "baseline" in names:
        arms["baseline"] = ""
    if "terse" in names:
        arms["terse"] = TERSE
    if "micro" in names:
        arms["micro"] = TERSE + "\n\n" + MICRO
    if "caveman" in names:
        body = strip_frontmatter((REPOS / "caveman" / "skills" / "caveman" / "SKILL.md").read_text(encoding="utf-8"))
        arms["caveman"] = TERSE + "\n\n" + body
    if "introvert" in names:
        body = strip_frontmatter((REPOS / "introvert" / "skills" / "introvert" / "SKILL.md").read_text(encoding="utf-8"))
        arms["introvert"] = TERSE + "\n\n" + body
    if "dense" in names:
        body = strip_frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
        arms["dense"] = TERSE + "\n\n" + body
    for name in names:
        if name in arms:
            continue
        path = ROOT / "skill" / name / "SKILL.md"
        if path.exists():
            arms[name] = TERSE + "\n\n" + strip_frontmatter(path.read_text(encoding="utf-8"))
    if "dense_ref" in names:
        body = strip_frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
        ref = (SKILL / "reference.md").read_text(encoding="utf-8")
        arms["dense_ref"] = TERSE + "\n\n" + body + "\n\n" + ref
    return arms


def call(system: str, user: str, key: str, retries: int = 3) -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    payload = json.dumps(
        {"model": MODEL, "messages": messages, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS, "stream": False}
    ).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "opencode/1.0",
        "Authorization": f"Bearer {key}",
        "x-opencode-session": str(uuid.uuid4()),
    }
    last = None
    for attempt in range(retries):
        started = time.time()
        try:
            req = urllib.request.Request(BASE_URL + "/chat/completions", data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return {
                "ok": True,
                "text": body["choices"][0]["message"].get("content") or "",
                "usage": body.get("usage", {}),
                "latency_ms": int((time.time() - started) * 1000),
                "attempt": attempt + 1,
            }
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * (attempt + 1))
    return {"ok": False, "error": last, "text": "", "usage": {}, "latency_ms": 0, "attempt": retries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--tasks", default="")
    ap.add_argument("--arms", default="baseline,terse,micro,caveman,introvert,dense")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    key = api_key()
    spec = json.loads((ROOT / "bench" / "tasks.json").read_text(encoding="utf-8"))
    tasks = spec["tasks"]
    if args.tasks:
        wanted = set(args.tasks.split(","))
        tasks = [t for t in tasks if t["id"] in wanted]
    arms = build_arms(args.arms.split(","))
    out_path = Path(args.out) if args.out else ROOT / "bench" / "results" / f"run-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    jobs = [(a, t, r) for a in arms for t in tasks for r in range(args.reps)]
    print(f"model={MODEL} arms={list(arms)} tasks={len(tasks)} reps={args.reps} calls={len(jobs)}", flush=True)

    lock = threading.Lock()
    done = 0
    with out_path.open("w", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(call, arms[a], t["prompt"], key): (a, t, r) for a, t, r in jobs}
        for fut in as_completed(futures):
            arm, task, rep = futures[fut]
            res = fut.result()
            rec = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "model": MODEL,
                "temperature": TEMPERATURE,
                "arm": arm,
                "task_id": task["id"],
                "lang": task["lang"],
                "category": task["category"],
                "rep": rep,
                "system_tokens_approx": len(arms[arm]) // 4,
                **res,
            }
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                done += 1
                if done % 20 == 0 or done == len(jobs):
                    print(f"  {done}/{len(jobs)}", flush=True)

    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
