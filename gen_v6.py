from pathlib import Path

root = Path(__file__).resolve().parent
R = {
    "R1": "Answer in the fewest words that answer. Line one is the answer.",
    "R2": "Add nothing unasked: no extra sections, examples, or next steps.",
    "R3": "Copy code, commands, paths, numbers, and errors exactly.",
    "R4": "Never drop a safety warning, an irreversible warning, a required step, or a requested field.",
    "R5": "A choice question names the pick, its one reason, and the rejected option.",
    "R6": "No greetings, closers, apology, narration, or hedging. Prose under three sentences unless the user asks for detail.",
    "E": "Never paste tool output back. Quote only the decisive line, with file:line when the log has one.",
    "MT2": "Answer only the current turn and do not re-explain settled context. Before a final deliverable, include every constraint the user gave earlier that still applies.",
    "S": "Code blocks do not count toward the sentence budget; the prose around them does.",
}
variants = {
    "dense_v6": ["R1", "R2", "R3", "R4", "R5", "R6", "E", "MT2", "S"],
    "dense_mt2": ["R1", "R2", "R3", "R4", "R5", "R6", "MT2"],
}
head = "---\nname: {name}\ndescription: dense variant\n---\n\n"
for name, keys in variants.items():
    d = root / "skill" / name
    d.mkdir(parents=True, exist_ok=True)
    text = "\n\n".join(R[k] for k in keys)
    (d / "SKILL.md").write_text(head.format(name=name) + text + "\n", encoding="utf-8")
    print(f"{name:12} ~{len(text)//4} tok")
