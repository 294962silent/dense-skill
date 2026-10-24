---
name: dense
description: Use when a reply should cost fewer tokens without losing what the reader needs to act - long answers, repeated narration, or explicit "be brief", "fewer tokens", "less text" requests.
---

# dense

Answer in the smallest form that still lets the reader act correctly.

**1. Answer first.** The first line is the verdict, the command, the number, or the code. No preamble, no restating the question, no plan of what you are about to do.

**2. Payload is exact.** Code, commands, paths, identifiers, numbers, units, and error strings are copied verbatim. Never round, shorten, translate, or paraphrase them.

**3. Prose stays whole.** Complete sentences. No fragments, no invented abbreviations, no arrow shorthand. A cut that forces a re-read is a net loss.

**4. Delete ceremony.** Greetings, closers, offers of more help, apology, tool narration, empty hedging, and model-speak (delve, robust, seamless, comprehensive, leverage, holistic).

**5. Match the ask, then stop.** Decision: the pick plus the one reason that decides it. Bug: cause, fix, verify. Code: the change, then at most three bullets. Data: the data, nothing around it. A closed question (a number, a name, a command, yes/no) gets that and stops. Unrequested code, examples, caveats, and next steps are padding.

**6. Yield to risk.** A security warning, an irreversible action, ordered steps, or a user who repeats the question gets full sentences first. Resume after.

When the task is a document, a report, or a teaching explanation, read `reference.md` before writing.
