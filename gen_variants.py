from pathlib import Path

root = Path(__file__).resolve().parent

R = {
    "R1": "Answer in the fewest words that answer. Line one is the answer.",
    "R2": "Add nothing unasked: no extra sections, examples, or next steps.",
    "R3": "Copy code, commands, paths, numbers, and errors exactly.",
    "R4": "Never drop a safety warning, an irreversible warning, a required step, or a requested field.",
    "R5": "A choice question names the pick, its one reason, and the rejected option.",
    "R6": "No greetings, closers, apology, narration, or hedging. Prose under three sentences unless the user asks for detail.",
    "D": "Tabular data goes in a table or CSV: one row per item, one column per field, no prose around it.",
    "E": "Never paste tool output back. Quote only the decisive line, with file:line when the log has one.",
    "S": "Code blocks do not count toward the sentence budget; the prose around them does.",
    "MT": "Answer only the current turn. Never recap earlier turns, and never re-derive a decision the user already accepted.",
}
base = ["R1", "R2", "R3", "R4", "R5", "R6"]
variants = {
    "dense_data": base + ["D"],
    "dense_echo": base + ["E"],
    "dense_seg": base + ["S"],
    "dense_v5": base + ["D", "E", "S"],
    "dense_data_echo": base + ["D", "E"],
    "dense_mt": base + ["MT"],
}
head = "---\nname: {name}\ndescription: dense variant\n---\n\n"
for name, keys in variants.items():
    d = root / "skill" / name
    d.mkdir(parents=True, exist_ok=True)
    text = "\n\n".join(R[k] for k in keys)
    (d / "SKILL.md").write_text(head.format(name=name) + text + "\n", encoding="utf-8")
    print(f"{name:18} {'+'.join(keys):28} ~{len(text)//4} tok")
