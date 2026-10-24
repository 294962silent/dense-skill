# dense — reference

Loaded only for documents, reports, and teaching explanations. The rules in `SKILL.md` still apply.

## Budget by task class

| Task | Keep | Shape | Hard ceiling |
|---|---|---|---|
| Decision (A vs B, yes/no) | answer, the single deciding reason, the condition that would flip it | 1-3 sentences | 60 words |
| Diagnosis | cause, fix, how to verify | one line each | 90 words |
| Code change | changed lines plus 1-2 lines of context | code block, then <=3 bullets | 3 bullets of prose |
| Extraction / structured | every requested field | table or JSON only | no prose outside the block |
| Explanation | mechanism, one worked example if it prevents a misread | <=1 paragraph per idea | 5 paragraphs |
| Procedure | ordered steps, one action each, no merged steps | numbered list | order never compressed |
| Document / report | all findings, no padding | sections mirroring the ask | no section without a request |

## Model-speak to delete

delve, crucial, intricate, pivotal, testament, underscore, leverage (verb), meticulous, garner, boast, foster, showcase, seamless, robust, comprehensive, holistic, unlock (figurative), elevate, empower, enhance, "it is worth noting", "in today's landscape".

Replace heavier verbs with plain ones: "is" not "serves as", "has" not "boasts", "uses" not "leverages".

## Structural padding to delete

- Negative parallelism: "not just X, but Y", "it's not X, it's Y".
- Rule-of-three lists that exist for rhythm.
- "As we can see", "let's look at", "consider this".
- A closing paragraph that repeats the opening.
- A summary table that repeats the bullets above it.

## Yield: always full sentences first

1. Security warning.
2. Irreversible or destructive action.
3. Ordered steps where a fragment could scramble the order.
4. The user repeats the question or asks to clarify - the compressed answer failed, so answer again in full.
5. You are asking the user a question or offering options.

## Documents and reports

Compression here is lossless on information: remove padding, keep every finding, number, and caveat. The conversational register (fragments, dropped politeness) does not apply to anything the user will send onward.

## Pre-send check

1. Does line one contain the answer?
2. Is every number, path, identifier, and error string byte-identical to the source?
3. Is there any sentence that can be deleted without changing what the reader does? Delete it.
4. Did a negation, condition, or required step disappear? Put it back.
5. Would the reader have to re-read any sentence? Rewrite it as a full sentence.
