# Run report: adv1.jsonl

model `deepseek-v4.1-flash` · temperature 0.3 · n=240 calls

## Arms (skill vs plain `Answer concisely.`)

Billed = tokens charged (includes hidden reasoning). Visible = what the user reads.
| arm | sys tok | pass % | facts % | billed out | visible out | reasoning | 95% CI (billed) | input tok | total tok | errors |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| dense | 123 | 86.7 | 88.9 | 285 | 50 | 217 | 238–335 | 291 | 576 | 0 |
| dense_data | 147 | 86.7 | 89.8 | 278 | 55 | 203 | 235–325 | 316 | 594 | 0 |
| dense_echo | 147 | 88.3 | 89.8 | 281 | 53 | 208 | 240–326 | 313 | 593 | 0 |
| terse | 4 | 73.3 | 77.6 | 487 | 133 | 323 | 408–570 | 188 | 674 | 0 |

## Delta vs `terse`, paired by task (the honest comparison)

| arm | billed change (95% CI over tasks) | visible change | pass-rate change (pp) | total-cost change |
|---|---:|---:|---:|---:|
| dense | -41.4% (-47 … -13) | -62.2% | +13.3 | -14.6% |
| dense_data | -42.8% (-48 … -1) | -58.7% | +13.3 | -11.9% |
| dense_echo | -42.3% (-47 … -13) | -60.6% | +15.0 | -12.0% |

## Dominance (pass rate ↑, output tokens ↓)

Non-dominated arms: dense_data, dense_echo

## Per task

| task | category | dense pass/tok | dense_data pass/tok | dense_echo pass/tok | terse pass/tok |
|---|---|---|---|---|---|
| T01 | decision | - | - | - | - |
| T02 | code_fix | - | - | - | - |
| T03 | diagnosis | - | - | - | - |
| T04 | extraction | - | - | - | - |
| T05 | numeric | - | - | - | - |
| T06 | ordered_steps | - | - | - | - |
| T07 | safety | - | - | - | - |
| T08 | decision | - | - | - | - |
| T09 | explain | - | - | - | - |
| T10 | code_fix | - | - | - | - |
| T11 | extraction | - | - | - | - |
| T12 | enumeration | - | - | - | - |
| T13 | decision | - | - | - | - |
| T14 | numeric | - | - | - | - |
| T15 | explain | - | - | - | - |
| T16 | code_fix | - | - | - | - |
| T17 | data | 100%/315 | 100%/211 | 100%/328 | 100%/332 |
| T18 | data | 0%/159 | 0%/178 | 0%/153 | 0%/184 |
| T19 | data | 100%/122 | 100%/171 | 100%/115 | 100%/94 |
| T20 | data | 100%/342 | 100%/272 | 100%/311 | 67%/498 |
| T21 | data | 100%/176 | 100%/191 | 100%/155 | 100%/263 |
| T22 | data | 100%/169 | 100%/93 | 100%/222 | 100%/233 |
| T23 | tool_echo | 100%/516 | 100%/500 | 100%/514 | 67%/1017 |
| T24 | tool_echo | 67%/636 | 67%/568 | 83%/498 | 0%/1024 |
| T25 | tool_echo | 100%/169 | 100%/245 | 100%/140 | 100%/569 |
| T26 | tool_echo | 100%/250 | 100%/356 | 100%/372 | 100%/652 |