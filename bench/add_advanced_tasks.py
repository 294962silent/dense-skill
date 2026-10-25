import json

p = "bench/tasks.json"
d = json.load(open(p, encoding="utf-8"))
existing = {t["id"] for t in d["tasks"]}

LOG_NGINX = """2026-10-24T08:12:01Z [error] 771#0: *8821 upstream timed out (110: Connection timed out) while reading response header from upstream, client: 10.2.1.9, server: api.example.com, request: "GET /v1/orders?page=2 HTTP/1.1", upstream: "http://10.0.4.11:8080/v1/orders?page=2", host: "api.example.com"
2026-10-24T08:12:01Z [error] 771#0: *8822 upstream timed out (110: Connection timed out) while reading response header from upstream, client: 10.2.1.9, server: api.example.com, request: "GET /v1/orders?page=3 HTTP/1.1", upstream: "http://10.0.4.11:8080/v1/orders?page=3"
2026-10-24T08:12:02Z [warn] 771#0: *8823 an upstream response is buffered to a temporary file /var/cache/nginx/1/23/0000000231 while reading upstream
2026-10-24T08:12:04Z [error] 771#0: *8824 upstream timed out (110: Connection timed out) while reading response header from upstream, upstream: "http://10.0.4.11:8080/v1/orders?page=4"
2026-10-24T08:12:05Z [notice] 771#0: *8825 client closed connection while waiting for request
2026-10-24T08:13:10Z [error] 771#0: *8901 upstream timed out (110: Connection timed out) while reading response header from upstream, upstream: "http://10.0.4.11:8080/v1/orders?page=2"
2026-10-24T08:14:22Z [error] 771#0: *8977 no live upstreams while connecting to upstream, upstream: "http://10.0.4.11:8080/v1/orders"
2026-10-24T08:14:23Z [error] 771#0: *8978 connect() failed (111: Connection refused) while connecting to upstream, upstream: "http://10.0.4.11:8080/v1/orders"
"""

LOG_PYTEST = """============================= test session starts =============================
platform linux -- Python 3.13.2, pytest-8.3.4, pluggy-1.5.0
rootdir: /srv/app
collected 42 items

tests/test_orders.py ........................F.....                       [ 69%]
tests/test_billing.py ..........                                          [ 93%]
tests/test_health.py ...                                                  [100%]

=================================== FAILURES ===================================
_________________________________ test_order_total _________________________________
    def test_order_total():
        order = build_order(lines=[Line(price=1999, qty=2), Line(price=500, qty=1)])
>       assert order.total == 4498
E       assert 4998 == 4498
E        +  where 4998 = build_order(...).total

tests/test_orders.py:88: AssertionError
=========================== short test summary info ============================
FAILED tests/test_orders.py::test_order_total - assert 4998 == 4498
========================= 1 failed, 41 passed in 3.42s ========================
"""

LOG_K8S = """Name:           checkout-7d9f8c6b5-x2lqp
Namespace:      prod
Node:           ip-10-0-3-77/10.0.3.77
Status:         Running
Restart Count:  7
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
  Started:      Mon, 24 Oct 2026 07:58:12 +0000
  Finished:     Mon, 24 Oct 2026 08:03:44 +0000
Limits:
  memory:  512Mi
Requests:
  memory:  256Mi
Events:
  Type     Reason     Age                   From     Message
  ----     ------     ----                  ----     -------
  Warning  BackOff    2m (x31 over 41m)     kubelet  Back-off restarting failed container
"""

LOG_NPM = """npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR! While resolving: web@0.1.0
npm ERR! Found: react@18.3.1
npm ERR! node_modules/react
npm ERR!   react@"18.3.1" from the root project
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^17.0.0" from react-beautiful-dnd@13.1.1
npm ERR! node_modules/react-beautiful-dnd
npm ERR!   react-beautiful-dnd@"*" from the root project
npm ERR! Fix the upstream dependency conflict, or retry
npm ERR! this command with --legacy-peer-deps
"""

new = [
    {
        "id": "T17",
        "lang": "en",
        "category": "data",
        "prompt": "Summarize these services in one view: api-gateway p99 12ms uptime 99.95%, auth 8ms 99.99%, search 240ms 99.5%, billing 31ms 99.9%, notify 55ms 99.0%, media 180ms 98.7%.",
        "checks": {"must_include": ["api-gateway", "auth", "search", "billing", "notify", "media", "12", "240", "180"]},
        "max_words": 120,
    },
    {
        "id": "T18",
        "lang": "en",
        "category": "data",
        "prompt": "Inventory: SKU-1001 x4 at 12.50, SKU-1002 x0 at 8.00, SKU-1003 x17 at 4.25, SKU-1004 x2 at 99.00, SKU-1005 x9 at 15.75. Which SKUs are out of stock and what is the total value?",
        "checks": {"must_include": ["SKU-1002", "1001", "1003", "1004", "1005", "12\\.50", "99\\.00"]},
        "max_words": 100,
    },
    {
        "id": "T19",
        "lang": "en",
        "category": "data",
        "prompt": "Map these errors to their fixes: E401 token expired -> refresh token; E403 role missing -> add role; E429 rate limited -> backoff; E500 upstream crash -> restart pod.",
        "checks": {"must_include": ["E401", "E403", "E429", "E500", "refresh", "role", "backoff", "restart"]},
        "max_words": 90,
    },
    {
        "id": "T20",
        "lang": "en",
        "category": "data",
        "prompt": "Compare vendors: Acme 99.9% SLA, $0.004/req, EU region; Bolt 99.5% SLA, $0.002/req, US only; Corvus 99.99% SLA, $0.007/req, EU+US.",
        "checks": {"must_include": ["Acme", "Bolt", "Corvus", "99\\.9", "0\\.004", "EU", "US"]},
        "max_words": 100,
    },
    {
        "id": "T21",
        "lang": "zh",
        "category": "data",
        "prompt": "整理事故时间线：07:58 部署 v2.3.1；08:03 错误率升至 12%；08:07 回滚开始；08:12 错误率回落到 0.2%；08:20 确认恢复。",
        "checks": {"must_include": ["07:58", "08:03", "08:07", "08:12", "08:20", "v2\\.3\\.1"]},
    },
    {
        "id": "T22",
        "lang": "zh",
        "category": "data",
        "prompt": "把这些配置项整理清楚：timeout 默认 30s，retries 默认 3，backoff 默认 200ms，max_conns 默认 100，keepalive 默认 60s。",
        "checks": {"must_include": ["timeout", "retries", "backoff", "max_conns", "keepalive", "30s", "200ms", "100", "60s"]},
    },
    {
        "id": "T23",
        "lang": "en",
        "category": "tool_echo",
        "prompt": "Root cause and fix, from this nginx log:\n" + LOG_NGINX,
        "checks": {"must_include": ["upstream|8080", "timeout|timed out|refused|live upstreams"]},
    },
    {
        "id": "T24",
        "lang": "en",
        "category": "tool_echo",
        "prompt": "Why does this test fail, and what is the fix?\n" + LOG_PYTEST,
        "checks": {"must_include": ["4998", "4498"]},
    },
    {
        "id": "T25",
        "lang": "en",
        "category": "tool_echo",
        "prompt": "What killed this pod, and what should change?\n" + LOG_K8S,
        "checks": {"must_include": ["OOMKilled|oom", "512Mi|memory limit|limit"]},
    },
    {
        "id": "T26",
        "lang": "en",
        "category": "tool_echo",
        "prompt": "Explain this install failure and the correct fix:\n" + LOG_NPM,
        "checks": {"must_include": ["ERESOLVE|peer", "react", "17|18"]},
    },
]
for t in new:
    if t["id"] not in existing:
        d["tasks"].append(t)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("tasks:", len(d["tasks"]))
