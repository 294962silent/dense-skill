# Run report: main.jsonl

model `deepseek-v4.1-flash` · temperature 0.3 · n=360 calls

## Arms (skill vs plain `Answer concisely.`)

Billed = tokens charged (includes hidden reasoning). Visible = what the user reads.
| arm | sys tok | pass % | facts % | billed out | visible out | reasoning | 95% CI (billed) | input tok | total tok | errors |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| baseline | 0 | 76.7 | 81.8 | 516 | 88 | 405 | 430–606 | 55 | 571 | 0 |
| caveman | 1112 | 96.7 | 98.1 | 284 | 104 | 144 | 240–330 | 1156 | 1440 | 0 |
| dense | 342 | 90.0 | 93.9 | 427 | 102 | 287 | 354–497 | 377 | 804 | 0 |
| introvert | 1686 | 91.7 | 96.1 | 260 | 68 | 169 | 221–303 | 1609 | 1869 | 0 |
| micro | 90 | 85.0 | 90.6 | 272 | 76 | 160 | 210–341 | 144 | 416 | 0 |
| terse | 4 | 93.3 | 96.3 | 333 | 88 | 211 | 275–395 | 60 | 393 | 0 |

## Delta vs `terse`, paired by task (the honest comparison)

| arm | billed change (95% CI over tasks) | visible change | pass-rate change (pp) | total-cost change |
|---|---:|---:|---:|---:|
| baseline | +54.7% (+32 … +65) | +0.5% | -16.7 | +45.1% |
| caveman | -14.7% (-27 … +3) | +17.8% | +3.3 | +266.2% |
| dense | +28.0% (+5 … +53) | +16.5% | -3.3 | +104.4% |
| introvert | -22.1% (-30 … +9) | -22.2% | -1.7 | +375.1% |
| micro | -18.3% (-41 … -4) | -13.9% | -8.3 | +5.8% |

## Dominance (pass rate ↑, output tokens ↓)

Non-dominated arms: caveman, introvert

## Per task

| task | category | baseline pass/tok | caveman pass/tok | dense pass/tok | introvert pass/tok | micro pass/tok | terse pass/tok |
|---|---|---|---|---|---|---|---|
| T01 | decision | 100%/211 | 80%/214 | 60%/365 | 60%/163 | 20%/92 | 100%/154 |
| T02 | code_fix | 100%/207 | 100%/169 | 100%/186 | 80%/212 | 60%/60 | 100%/223 |
| T03 | diagnosis | 80%/1017 | 100%/331 | 100%/492 | 100%/172 | 100%/297 | 100%/513 |
| T04 | extraction | 100%/191 | 100%/123 | 100%/177 | 100%/165 | 100%/194 | 100%/151 |
| T05 | numeric | 100%/119 | 100%/41 | 100%/57 | 100%/48 | 100%/67 | 100%/88 |
| T06 | ordered_steps | 60%/962 | 100%/516 | 40%/1021 | 60%/583 | 40%/852 | 80%/732 |
| T07 | safety | 20%/902 | 100%/329 | 100%/481 | 100%/333 | 100%/255 | 60%/495 |
| T08 | decision | 100%/374 | 100%/351 | 100%/369 | 100%/296 | 100%/343 | 100%/266 |
| T09 | explain | 20%/1024 | 80%/628 | 80%/861 | 100%/273 | 100%/635 | 100%/612 |
| T10 | code_fix | 80%/474 | 100%/202 | 100%/332 | 100%/206 | 100%/111 | 100%/252 |
| T11 | extraction | 60%/251 | 100%/173 | 100%/213 | 100%/288 | 100%/103 | 80%/169 |
| T12 | enumeration | 100%/454 | 100%/335 | 100%/569 | 100%/377 | 100%/259 | 100%/346 |
| T13 | decision | - | - | - | - | - | - |
| T14 | numeric | - | - | - | - | - | - |
| T15 | explain | - | - | - | - | - | - |
| T16 | code_fix | - | - | - | - | - | - |