#!/usr/bin/env python3
"""dense — name index + on-demand inspect + fail-open reversible compression.

Commands
  index                      rebuild ~/.dense/index.json from installed skills
  resolve "<task>" [--k N]   top-N skills for a task (name, tokens, path)
  show <name>                print a skill's SKILL.md (inspect on demand)
  compress [--budget N]      stdin -> compressed text on stdout, handle on stderr
  recover <handle>           print the exact original bytes
  stats                      last operations from the journal

Every compression is fail-open: if it cannot shrink the input, or anything throws,
the original bytes go out unchanged and no handle is minted.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
SKILLS = HOME / ".agents" / "skills"
STORE = HOME / ".dense"
INDEX = STORE / "index.json"
CCR = STORE / "ccr"
JOURNAL = STORE / "journal.jsonl"


def ensure_store() -> None:
    CCR.mkdir(parents=True, exist_ok=True)


def frontmatter(text: str) -> tuple[str, str, str]:
    if not text.startswith("---"):
        return "", "", text
    end = text.find("\n---", 3)
    if end < 0:
        return "", "", text
    fm, body = text[3:end], text[end + 4:]
    name = re.search(r"(?m)^name:\s*(.+)$", fm)
    desc = re.search(r"(?ms)^description:\s*>?[|\-]?\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", fm)
    clean = lambda s: re.sub(r"\s+", " ", s or "").strip().strip("'\"")
    return clean(name.group(1) if name else ""), clean(desc.group(1) if desc else ""), body


ALIASES = {
    "知网": "cnki", "论文": "paper", "期刊": "journal", "收录": "index journal",
    "文献": "literature paper", "引用": "citation", "学术": "academic scholar",
    "测试": "test", "调试": "debug diagnose", "排查": "debug diagnose",
    "笔记": "note obsidian", "文章": "article write", "写作": "writing article",
    "浏览器": "browser scrape", "抓取": "scrape fetch", "网页": "page browser",
    "索引": "index graph", "代码库": "codebase graph",
    "审查": "review", "评审": "review", "规范": "standards review",
    "缺陷": "bug issue", "报告": "issue report", "问题单": "issue",
    "发布": "publish", "部署": "deploy", "表格": "spreadsheet xlsx",
    "文档": "docx document", "演示": "pptx slides", "截图": "screenshot image",
}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    words = re.findall(r"[a-z0-9_]+", text)
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    bigrams = ["".join(cjk[i:i + 2]) for i in range(len(cjk) - 1)]
    return words + bigrams


def expand(query: str) -> list[str]:
    """Add English task words for common Chinese terms (a lexicon, not a model call)."""
    extra = []
    for zh, en in ALIASES.items():
        if zh in query:
            extra.extend(en.split())
    return tokenize(query) + extra


def build_index() -> dict:
    items = []
    if SKILLS.exists():
        for d in sorted(SKILLS.iterdir()):
            p = d / "SKILL.md"
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            name, desc, body = frontmatter(text)
            if not name:
                continue
            items.append({
                "name": name,
                "desc": desc,
                "path": str(p),
                "body_tokens": len(body.strip()) // 4,
                "index_tokens": len((name + " " + desc)) // 4,
            })
    STORE.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({"built": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"), "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"items": items}


def load_index() -> dict:
    if not INDEX.exists():
        return build_index()
    return json.loads(INDEX.read_text(encoding="utf-8"))


def resolve(query: str, k: int = 3) -> int:
    data = load_index()
    items = data["items"]
    docs = [tokenize(i["name"] + " " + i["desc"]) for i in items]
    q = expand(query)
    if not q:
        print("no query terms", file=sys.stderr)
        return 2
    n = len(docs)
    avg = sum(len(d) for d in docs) / max(n, 1)
    df = Counter()
    for d in docs:
        df.update(set(d))
    idf = {t: math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)) for t in set(q)}
    scored = []
    for item, doc in zip(items, docs):
        tf = Counter(doc)
        s = 0.0
        for t in q:
            if t not in tf:
                continue
            denom = tf[t] + 1.2 * (1 - 0.75 + 0.75 * len(doc) / max(avg, 1))
            s += idf.get(t, 0.0) * tf[t] * 2.2 / denom
        name_bits = set(re.split(r"[-_]", item["name"].lower()))
        if name_bits & set(q):
            s *= 1.8
        if s > 0:
            scored.append((s, item))
    scored.sort(key=lambda x: -x[0])
    hits = [i for _, i in scored[:k]] or items[:k]
    print(f"# {len(hits)} of {len(items)} skills  (~{sum(h['index_tokens'] for h in hits)} tokens)")
    for h in hits:
        print(f"{h['name']}\t{h['body_tokens']}\t{h['path']}")
    return 0


def show(name: str) -> int:
    data = load_index()
    for i in data["items"]:
        if i["name"] == name:
            print(Path(i["path"]).read_text(encoding="utf-8", errors="replace"))
            return 0
    print(f"unknown skill: {name}", file=sys.stderr)
    return 2


KEEP = re.compile(
    r"(error|err!|fail|fatal|panic|exception|traceback|caused by|refused|timeout|timed out|"
    r"oom|killed|denied|not found|no such|undefined|cannot|unable|assert|warn|"
    r"错误|失败|异常|超时|拒绝|未找到)", re.I)
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
PROGRESS = re.compile(r"(\d+%|\bETA\b|\bprogress\b|\.\.\.\s*$|^\s*[#>\-=]{4,}\s*$)")


def compress_text(text: str, budget: int | None = None, context: int = 3) -> tuple[str, str | None]:
    raw = text
    body = ANSI.sub("", text.replace("\r\n", "\n").replace("\r", "\n")).split("\n")
    keep_idx = set()
    for idx, line in enumerate(body):
        if KEEP.search(line):
            for j in range(max(0, idx - context), min(len(body), idx + context + 1)):
                keep_idx.add(j)
    kept, seen = [], set()
    for idx in sorted(keep_idx):
        s = body[idx].strip()
        if not s or s in seen:
            continue
        # pure progress lines stay out unless they are the error line itself
        if PROGRESS.search(s) and not KEEP.search(s):
            continue
        seen.add(s)
        kept.append(s[:400])
    out = []
    for h in body[:2]:
        h = h.strip()
        if h and h not in out:
            out.append(h[:400])
    out.extend(kept)
    for t in body[-2:]:
        t = t.strip()
        if t and t not in out:
            out.append(t[:400])
    compressed = "\n".join(out)
    if budget:
        # keep at most `budget` approximate tokens, newest errors first
        while len(compressed) // 4 > budget and out:
            out.pop(1 if len(out) > 1 else 0)
            compressed = "\n".join(out)
    return compressed, (raw if compressed else raw)


def do_compress(budget: int | None) -> int:
    ensure_store()
    raw = sys.stdin.read()
    if not raw:
        return 0
    try:
        compressed, _ = compress_text(raw, budget)
    except Exception:  # noqa: BLE001  fail-open
        sys.stdout.write(raw)
        return 0
    before, after = len(raw), len(compressed)
    if after >= before * 0.9 or after < 40:
        sys.stdout.write(raw)
        print(f"[dense fail-open] no gain ({before}->{after} bytes)", file=sys.stderr)
        return 0
    handle = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:12]
    (CCR / f"{handle}.txt").write_text(raw, encoding="utf-8")
    with JOURNAL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"h": handle, "in": before, "out": after}) + "\n")
    sys.stdout.write(compressed)
    print(f"[dense handle={handle} {before}->{after} bytes −{100*(before-after)//max(before,1)}%]", file=sys.stderr)
    return 0


def recover(handle: str) -> int:
    p = CCR / f"{handle}.txt"
    if not p.is_file():
        print(f"unknown handle: {handle}", file=sys.stderr)
        return 2
    sys.stdout.write(p.read_text(encoding="utf-8"))
    return 0


def stats() -> int:
    if not JOURNAL.exists():
        print("no operations yet")
        return 0
    rows = [json.loads(l) for l in JOURNAL.read_text(encoding="utf-8").splitlines() if l.strip()]
    saved = sum(r["in"] - r["out"] for r in rows)
    print(f"operations={len(rows)} bytes_in={sum(r['in'] for r in rows)} bytes_out={sum(r['out'] for r in rows)} saved={saved}")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "index":
        data = build_index()
        total = sum(i["body_tokens"] for i in data["items"])
        print(f"indexed {len(data['items'])} skills, {total} body tokens, index itself ~{len(INDEX.read_text(encoding='utf-8'))//4} tokens")
        return 0
    if cmd == "resolve":
        k = 3
        if "--k" in rest:
            i = rest.index("--k")
            k = int(rest[i + 1])
            rest = rest[:i] + rest[i + 2:]
        return resolve(" ".join(rest), k)
    if cmd == "show":
        return show(rest[0]) if rest else 2
    if cmd == "compress":
        budget = None
        if "--budget" in rest:
            budget = int(rest[rest.index("--budget") + 1])
        return do_compress(budget)
    if cmd == "recover":
        return recover(rest[0]) if rest else 2
    if cmd == "stats":
        return stats()
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
