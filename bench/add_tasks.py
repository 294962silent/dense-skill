import json

p = "bench/tasks.json"
d = json.load(open(p, encoding="utf-8"))
new = [
    {
        "id": "T13",
        "lang": "en",
        "category": "decision",
        "prompt": "Kafka or SQS? 5k events/s, at-least-once delivery, 3 consumer groups, already AWS-native.",
        "checks": {"must_include": ["kafka", "sqs", "\\b(pick|use|choose|go with|stick with)\\b"]},
        "max_words": 80,
        "held_out": True,
    },
    {
        "id": "T14",
        "lang": "en",
        "category": "numeric",
        "prompt": "SQL: `SELECT COUNT(*) FROM t WHERE a > 1 AND b IS NULL`. Rows: (2,NULL), (3,1), (NULL,NULL), (5,NULL). What is the result?",
        "checks": {"must_include": ["\\b2\\b"]},
        "max_words": 40,
        "held_out": True,
    },
    {
        "id": "T15",
        "lang": "zh",
        "category": "explain",
        "prompt": "为什么 Redis 单线程还这么快？",
        "checks": {"must_include": ["(内存|memory)", "(单线程|单核|无锁|锁|epoll|多路复用|io 多路)", "(切换|竞争|锁|开销|序列化)"]},
        "held_out": True,
    },
    {
        "id": "T16",
        "lang": "zh",
        "category": "code_fix",
        "prompt": "写 SQL：查每个用户最近一次订单。表 orders(user_id, id, created_at)。",
        "checks": {"must_include": ["(row_number|distinct on|max\\()", "order by", "created_at"]},
        "held_out": True,
    },
]
existing = {t["id"] for t in d["tasks"]}
for t in new:
    if t["id"] not in existing:
        d["tasks"].append(t)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("tasks:", len(d["tasks"]))
