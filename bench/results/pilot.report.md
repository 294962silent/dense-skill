# Run report: pilot.jsonl

model `deepseek-v4.1-flash` · temperature 0.3 · n=4 calls

## Arms (skill vs plain `Answer concisely.`)

| arm | system tokens (approx) | pass % | facts % | output tok (mean) | 95% CI | input tok | total tok | errors |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| dense | 304 | 100.0 | 100.0 | 206 | 68–343 | 342 | 547 | 0 |
| terse | 4 | 50.0 | 66.7 | 82 | 53–112 | 64 | 147 | 0 |

## Delta vs `terse` (the honest comparison)

| arm | output tok change | pass-rate change (pp) | facts change (pp) | total-cost change |
|---|---:|---:|---:|---:|
| dense | +149.1% | +50.0 | +33.3 | +272.1% |

## Dominance (pass rate ↑, output tokens ↓)

Non-dominated arms: dense, terse

## Per task

| task | category | dense pass/tok | terse pass/tok |
|---|---|---|---|
| T01 | decision | 100%/343 | 0%/112 |
| T02 | code_fix | - | - |
| T03 | diagnosis | - | - |
| T04 | extraction | - | - |
| T05 | numeric | 100%/68 | 100%/53 |
| T06 | ordered_steps | - | - |
| T07 | safety | - | - |
| T08 | decision | - | - |
| T09 | explain | - | - |
| T10 | code_fix | - | - |
| T11 | extraction | - | - |
| T12 | enumeration | - | - |