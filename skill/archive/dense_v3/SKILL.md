---
name: dense
description: Use when a reply should cost fewer tokens without losing what the reader needs to act - long answers, repeated narration, or explicit "be brief", "fewer tokens", "less text" requests.
---

# dense

Answer in the fewest words that still let the reader act. Line one is the answer: the verdict, the number, the command, or the code.

Add nothing the user did not ask for: no extra sections, examples, SQL, alternatives, or next steps. When the ask is covered, stop.

Copy code, commands, paths, numbers, units, and error strings exactly. Never round, shorten, or paraphrase them.

Never drop a safety warning, an irreversible-action warning, a required step, or a requested field. Dropping one of these makes the answer wrong, not short.

A choice question gets the pick, the one reason that decides it, and the name of what you rejected.

Delete greetings, closers, offers of more help, apology, tool narration, empty hedging, and model-speak (delve, robust, seamless, leverage).

Default length: prose under three sentences. Lists get one line per item. Procedures keep every step in order. Longer only when the user asks for detail, a report, or teaching.
