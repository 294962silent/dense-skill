#!/usr/bin/env python3
"""Regression test for dense's name index.

Two properties:
  1. SELF   - a skill's own description must retrieve that skill (top-3 always, top-1 mostly).
  2. ZH     - short Chinese task phrasings must land on an acceptable skill.

Run:  python bench/test_resolve.py        (exit 0 = pass, 1 = fail)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skill" / "dense"))

import dense  # noqa: E402

# accepted answers per Chinese query; more than one skill can be legitimate
ZH_CASES: list[tuple[str, set[str]]] = [
    ("把这个日志压缩一下", {"dense"}),
    ("回答短一点，少放点 token", {"dense"}),
    ("帮我省点 token", {"dense"}),
    ("输出太啰嗦了", {"dense"}),
    ("调试这个报错", {"diagnosing-bugs", "systematic-debugging"}),
    ("审查我的 PR", {"review", "requesting-code-review", "receiving-code-review"}),
    ("查知网的论文", {"cnki-search", "cnki-paper-detail", "cnki-journal-index"}),
    ("存进 obsidian", {"obsidian-vault"}),
    ("合并冲突了", {"resolving-merge-conflicts"}),
    ("用浏览器抓页面", {"browser-skill"}),
    ("给仓库建索引", {"graphify"}),
    ("先写测试再实现", {"test-driven-development", "tdd"}),
]


def main() -> int:
    items = dense.build_index()["items"]
    failures: list[str] = []

    # 1. self-retrieval
    top1 = top3 = 0
    for it in items:
        hits = [h["name"] for h in dense.rank(it["desc"][:200] or it["name"], 3, items)]
        if hits[:1] == [it["name"]]:
            top1 += 1
        if it["name"] in hits:
            top3 += 1
        else:
            failures.append(f"SELF  {it['name']} -> {hits}")
    n = len(items)
    print(f"SELF  {n} skills   hit@1 {100*top1/n:.0f}%   hit@3 {100*top3/n:.0f}%")
    if 100 * top3 / n < 100:
        failures.append(f"SELF  hit@3 is {100*top3/n:.0f}%, required 100%")
    if 100 * top1 / n < 95:
        failures.append(f"SELF  hit@1 is {100*top1/n:.0f}%, required >=95%")

    # 2. Chinese task phrasing
    zh_hits = 0
    for query, accepted in ZH_CASES:
        hits = [h["name"] for h in dense.rank(query, 3, items)]
        ok = bool(set(hits) & accepted)
        zh_hits += ok
        print(f"{'PASS' if ok else 'FAIL'}  {query}  ->  {', '.join(hits)}")
        if not ok:
            failures.append(f"ZH    {query} -> {hits} (want one of {sorted(accepted)})")
    print(f"ZH    {zh_hits}/{len(ZH_CASES)} queries resolved")

    if failures:
        print("\nFAILURES")
        for f in failures:
            print("  " + f)
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
