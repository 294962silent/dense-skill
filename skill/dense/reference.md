# dense — reference (loaded on demand)

`SKILL.md` is the measured core. This file is the optional toolkit guide; loading it costs tokens and was **not** part of the output-compression benchmark.

## The `dense` CLI

`dense.py` lives next to this file. Three jobs: keep things **out** of the prompt, and never lose what was removed.

```bash
python dense.py index                     # scan ~/.agents/skills -> ~/.dense/index.json
python dense.py resolve "extract tables from a pdf" --k 3   # name, tokens, path
python dense.py show office-xlsx          # full SKILL.md, only when you picked it
python dense.py compress --budget 800 < build.log > build.min.log   # handle on stderr
python dense.py recover <handle>          # exact original bytes
python dense.py stats                     # operations, bytes in/out
```

**Name index, schema on demand.** Every installed skill's description costs tokens in every turn. `resolve` returns three candidates (~100 tokens) instead of the whole catalog; `show` fetches the one you picked. Measured on 68 installed skills: catalog ~3.4k tokens vs 3-line hit list ~104.

**Fail-open.** If compression cannot shrink the input (or anything throws), the original bytes are written out unchanged and no handle is minted. A broken compressor degrades to no compressor.

**Reversible.** A compressed log is lossy; the exact original is stored under `~/.dense/ccr/<handle>.txt` before the compressed text is emitted. Quote the handle; `recover` gets the bytes back. Never compress something you cannot recover.

## Long logs and tool output (measured)

Pasting a tool result back is the most expensive habit, but it only matters when the log is long. Quote the one decisive line and cite `file:line`; do not reproduce the rest. Measured on a 40-line k8s describe: 245 → 140 tokens for the same answer. On a short log the same rule changes nothing.

## Tables are not free (measured)

Forcing a table on a 2-3 item mapping adds headers and separators and came out longer than one line (211 → 328 tokens on a six-service list). Use a table only at ≥3 items × ≥3 fields, or when the user asks for one.

## Multi-turn

The saving in a long conversation comes from every turn being short, not from a running summary. A "don't repeat settled context" rule measured *worse* (−33% vs −42%) and lost final-answer accuracy, because the model spent the last turn re-checking what it might have dropped.

## Documents

Compression there is lossless on information: strip padding, keep every finding, number, and caveat. The conversational register does not apply to anything the user will send onward.

## Full sentences first

Security warning; irreversible or destructive action; ordered steps where a fragment could scramble the order; the user repeats the question (the compressed answer failed); you are asking the user a question. Resume after the risky part.

## Pre-send check

1. Does line one contain the answer?
2. Is every number, path, identifier, and error string byte-identical to the source?
3. Is there a sentence that can be deleted without changing what the reader does? Delete it.
4. Did a negation, condition, or required step disappear? Put it back.
