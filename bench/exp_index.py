#!/usr/bin/env python3
"""E1: skill routing — whole catalog in context vs a 3-line name index.

Ground truth is a SET of acceptable skills per task (several skills are legitimate
answers: qa vs to-issues, review vs requesting-code-review), so scoring does not
punish a defensible choice.
"""
from __future__ import annotations

import json
import subprocess
import sys
import statistics as st
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, api_key, call  # noqa: E402

DENSE = ROOT / "skill" / "dense" / "dense.py"
INDEX = Path.home() / ".dense" / "index.json"

CASES = [
    ("帮我查一下知网上关于数字经济的论文", {"cnki-search", "cnki-paper-detail", "cnki-journal-index"}),
    ("这本期刊是不是 CSSCI 收录", {"cnki-journal-index"}),
    ("在 Google Scholar 上找这个主题高引的论文", {"gs-search"}),
    ("审查我这个 PR 的改动是否符合规范", {"review", "requesting-code-review", "receiving-code-review"}),
    ("这个测试单独跑能过，跑全量就挂", {"systematic-debugging", "diagnosing-bugs", "test-driven-development"}),
    ("先写测试再实现这个功能", {"test-driven-development", "tdd"}),
    ("把这段内容存进我的 Obsidian 笔记", {"obsidian-vault"}),
    ("用我登录着的浏览器抓一下这个页面的数据", {"browser-skill"}),
    ("给这个仓库建一个结构化代码索引", {"graphify"}),
    ("把我这堆笔记写成一篇可发布的文章", {"writing-shape", "writing-beats", "writing-fragments", "edit-article"}),
    ("盯着这个 PR 直到 CI 全绿", {"babysit", "autopilot"}),
    ("把这些 bug 报告整理成 GitHub issue", {"qa", "to-issues", "triage"}),
]

HOLDOUT = [
    ("给这个模块补几个单元测试", {"test-driven-development", "tdd", "setup-pre-commit"}),
    ("把我上周的会议记录整理进笔记库", {"obsidian-vault"}),
    ("这个 PR 的 CI 一直红，帮我盯到绿", {"babysit", "autopilot"}),
    ("在知网上查这本期刊的影响因子", {"cnki-journal-index"}),
    ("帮我在 Google Scholar 上查这篇的引用数", {"gs-search"}),
    ("这个模块的接口设计得太浅，怎么加深", {"codebase-design", "domain-modeling"}),
    ("这个报错到底根因是什么", {"diagnosing-bugs", "systematic-debugging"}),
    ("用浏览器登录后把页面表格抓下来", {"browser-skill"}),
    ("把这些 bug 描述拆成 issue", {"qa", "to-issues", "triage"}),
    ("帮我把这份 Word 文档转成 PDF", {"office-export-pdf", "office-docx", "office"}),
]

SYS_FULL = "You are a routing table. Pick exactly one skill for the task. Reply with the skill name only.\n\nAvailable skills:\n{cat}"
SYS_INDEX = "You are a routing table. Pick exactly one skill for the task. Reply with the skill name only.\n\nCandidates:\n{cand}"


def catalog_text(items):
    return "\n".join(f"- {i['name']}: {i['desc'][:90]}" for i in items)


def resolve_names(query, k=3):
    out = subprocess.run([sys.executable, str(DENSE), "resolve", query, "--k", str(k)],
                         capture_output=True, text=True, encoding="utf-8")
    names = [l.split("\t")[0] for l in out.stdout.splitlines() if l and not l.startswith("#")]
    return names


def main():
    key = api_key()
    cases = HOLDOUT if "holdout" in sys.argv else CASES
    items = json.loads(INDEX.read_text(encoding="utf-8"))["items"]
    cat = catalog_text(items)
    rows = []
    for q, expect in cases:
        names = resolve_names(q, 3)
        recall = bool(set(names) & expect)
        cand = "\n".join(f"- {n}" for n in names)
        for arm, system in (("full", SYS_FULL.format(cat=cat)), ("index", SYS_INDEX.format(cand=cand))):
            for rep in range(3):
                res = call(system, q, key)
                ans = (res.get("text") or "").strip().split("\n")[-1].strip().strip("`\"' ")
                hit = any(e in ans.lower() for e in expect)
                rows.append({
                    "query": q, "expected": sorted(expect), "arm": arm, "rep": rep, "ok": res["ok"],
                    "answer": ans, "hit": hit, "resolve_recall": recall, "candidates": names,
                    "input_tokens": res["usage"].get("prompt_tokens", 0),
                    "output_tokens": res["usage"].get("completion_tokens", 0),
                })
    out = ROOT / "bench" / "results" / "exp_index.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")

    print("| arm | 输入 token | 路由正确率 |")
    print("|---|---:|---:|")
    for arm in ("full", "index"):
        rs = [r for r in rows if r["arm"] == arm and r["ok"]]
        print(f"| {arm} | {st.mean(r['input_tokens'] for r in rs):.0f} | {100*st.mean(r['hit'] for r in rs):.2f}% |")
    recall = st.mean(r["resolve_recall"] for r in rows if r["arm"] == "index")
    print(f"\nresolve recall@3: {100*recall:.0f}%")
    print("index-arm misses:")
    for r in rows:
        if r["arm"] == "index" and not r["hit"]:
            print(f"  {r['query'][:24]} -> {r['answer']}  (want one of {r['expected']}, got {r['candidates']})")


if __name__ == "__main__":
    main()
