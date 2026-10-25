from pathlib import Path

root = Path(__file__).resolve().parent

R = {
    "R1": "Answer in the fewest words that answer. Line one is the answer.",
    "R2": "Add nothing unasked: no extra sections, examples, or next steps.",
    "R3": "Copy code, commands, paths, numbers, and errors exactly.",
    "R4": "Never drop a safety warning, an irreversible warning, a required step, or a requested field.",
    "R5": "A choice question names the pick, its one reason, and the rejected option.",
    "R6": "No greetings, closers, apology, narration, or hedging. Prose under three sentences unless the user asks for detail.",
}

variants = {
    "ab_no_p2": ["R1", "R3", "R4", "R5", "R6"],
    "ab_no_p4": ["R1", "R2", "R3", "R5", "R6"],
    "ab_no_p5": ["R1", "R2", "R3", "R4", "R6"],
    "ab_no_p6": ["R1", "R2", "R3", "R4", "R5"],
    "ab_only_p2": ["R1", "R2"],
}
head = "---\nname: {name}\ndescription: ablation variant\n---\n\n"
for name, keys in variants.items():
    d = root / "skill" / name
    d.mkdir(parents=True, exist_ok=True)
    text = "\n\n".join(R[k] for k in keys)
    (d / "SKILL.md").write_text(head.format(name=name) + text + "\n", encoding="utf-8")
    print(f"{name:12} rules={'+'.join(keys):20} ~{len(text)//4} tok")
