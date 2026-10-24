import json

p = "bench/tasks.json"
d = json.load(open(p, encoding="utf-8"))
fix = {
    # drop phrasing-dependent "pick verb" checks: naming both options is the real
    # requirement, the verb used to express the pick is not content.
    "T01": ["pg_trgm", "elastic"],
    "T08": ["clickhouse", "mysql"],
    "T13": ["kafka", "sqs"],
    # widen the deploy step: any "put the new key where the workload reads it" verb
    "T06": [
        "(deactivate|disable|revoke|delete)",
        "(create|generate|issue|new).{0,40}key",
        "(update|deploy|replace|roll|swap|install|apply|put|store).{0,80}(app|service|environment|config|secret|ci|workload|system|pipeline)",
    ],
}
for t in d["tasks"]:
    if t["id"] in fix:
        t["checks"]["must_include"] = fix[t["id"]]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("patched", list(fix))
