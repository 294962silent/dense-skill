import json

p = "bench/tasks.json"
d = json.load(open(p, encoding="utf-8"))
limits = {"T01": 60, "T02": 80, "T05": 40}
for t in d["tasks"]:
    if t["id"] in limits:
        t["max_words"] = limits[t["id"]]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok")
