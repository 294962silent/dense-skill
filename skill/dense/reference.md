# dense — reference (optional, not part of the measured arm)

`SKILL.md` is the whole measured skill: 123 tokens, the body that won the benchmark. This file is extra guidance for cases the five rules leave ambiguous. Loading it costs tokens and was **not** part of the experiment, so read it only when you need it.

## Budget by task class

| Task | Keep | Shape | Ceiling |
|---|---|---|---|
| Decision (A vs B, yes/no) | pick, one deciding reason, rejected option | 1-3 sentences | 60 words |
| Diagnosis | cause, fix, verify | one line each | 90 words |
| Code change | changed lines plus 1-2 context lines | code block, then ≤3 bullets | 3 bullets |
| Extraction | every requested field | table or JSON | no prose around it |
| Explanation | mechanism, one example only if it prevents a misread | ≤1 paragraph per idea | 5 paragraphs |
| Procedure | ordered steps, one action each | numbered list | order never compressed |
| Document / report | every finding, no padding | sections mirroring the ask | no unrequested section |

## Model-speak to delete

delve, crucial, intricate, pivotal, testament, underscore, leverage (verb), meticulous, garner, boast, foster, showcase, seamless, robust, comprehensive, holistic, unlock (figurative), elevate, empower, enhance, "it is worth noting", "in today's landscape".

Plain verbs instead: "is" not "serves as", "has" not "boasts", "uses" not "leverages".

## Structural padding

Negative parallelism ("not just X, but Y"). Rule-of-three lists written for rhythm. "As we can see" / "let's look at". A closing paragraph that repeats the opening. A summary table that repeats the bullets above it.

## Full sentences first

Security warning; irreversible or destructive action; ordered steps where a fragment could scramble the order; the user repeats the question (the compressed answer failed); you are asking the user a question. Resume after the risky part.

## Documents

Compression there is lossless on information: strip padding, keep every finding, number, and caveat. The conversational register does not apply to anything the user will send onward.

## Long logs and tool output (measured)

Pasting a tool result back is the most expensive habit, but it only matters when the log is long. Quote the one decisive line and cite `file:line`; do not reproduce the rest. Measured on a 40-line k8s describe: 245 → 140 tokens for the same answer. On a short log the same rule changes nothing.

## Tables are not free (measured)

Forcing a table on a 2-3 item mapping adds headers and separators and came out longer than one line (211 → 328 tokens on a six-service list). Use a table only at ≥3 items × ≥3 fields, or when the user asks for one.

## Multi-turn

The saving in a long conversation comes from every turn being short, not from a running summary. A "don't repeat settled context" rule measured *worse* (−33% vs −42%) and lost final-answer accuracy, because the model spent the last turn re-checking what it might have dropped.

## Pre-send check

1. Does line one contain the answer?
2. Is every number, path, identifier, and error string byte-identical to the source?
3. Is there a sentence that can be deleted without changing what the reader does? Delete it.
4. Did a negation, condition, or required step disappear? Put it back.
