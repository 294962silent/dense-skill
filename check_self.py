import json, subprocess, sys
from pathlib import Path
DENSE = Path("skill/dense/dense.py")
data = json.loads((Path.home()/".dense"/"index.json").read_text(encoding="utf-8"))["items"]
top1 = top3 = 0; miss = []
for it in data:
    q = it["desc"][:160] or it["name"]
    out = subprocess.run([sys.executable, str(DENSE), "resolve", q, "--k", "3"],
                         capture_output=True, text=True, encoding="utf-8")
    names = [l.split("\t")[0] for l in out.stdout.splitlines() if l and not l.startswith("#")]
    if names[:1] == [it["name"]]: top1 += 1
    if it["name"] in names: top3 += 1
    else: miss.append(it["name"])
n = len(data)
print(f"skills={n}  self-hit@1={100*top1/n:.0f}%  self-hit@3={100*top3/n:.0f}%")
print("misses:", ", ".join(miss[:12]))
