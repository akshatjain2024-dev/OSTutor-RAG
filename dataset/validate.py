import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE))
import config
import solvers as S

OUT = HERE / "out"
errors = []


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def check(cond, msg):
    if not cond:
        errors.append(msg)


ft = load(OUT / "finetune/train.jsonl") + load(OUT / "finetune/val.jsonl")
for i, row in enumerate(ft):
    m = row["messages"]
    check([x["role"] for x in m] == ["system", "user", "assistant"], f"ft row {i}: bad roles")
    check(all(x["content"].strip() for x in m), f"ft row {i}: empty message")
    if row["meta"]["kind"].endswith("_generation"):
        try:
            json.loads(m[2]["content"])
        except Exception:
            errors.append(f"ft row {i}: generation target is not valid JSON")

evalq = {r["question"] for r in load(OUT / "eval/rag_eval.jsonl") if r["type"] == "qa"}
train_text = "\n".join(x["content"] for row in ft for x in row["messages"][1:])
kb_text = "\n".join(p.read_text() for d in (config.NOTES_DIR, config.QUESTIONS_DIR) for p in d.glob("*.md"))
leak_ft = [q for q in evalq if f"Viva question: {q}" in train_text or f"STUDENT QUESTION: {q}" in train_text]
leak_kb = [q for q in evalq if f"Q: {q}\nA:" in kb_text]
check(not leak_ft, f"eval questions leaked into fine-tuning data: {leak_ft[:3]}")
check(not leak_kb, f"eval viva answers leaked into the knowledge base: {leak_kb[:3]}")

nums = load(OUT / "numericals.jsonl")
for n in nums:
    st, d, a = n["subtype"], n.get("data", {}), n["answer"]
    if st == "scheduling":
        name = n["algorithm"]
        if name.startswith("Round Robin"):
            q = int(name.split("=")[1].strip(" )"))
            r = S.round_robin(d["processes"], q)
        else:
            r = S.SCHEDULERS[name](d["processes"])
        check(r["avg"]["wt"] == a["avg_wt"], f"{n['id']}: avg WT mismatch")
    elif st == "page_replacement":
        check(S.page_replacement(d["refs"], d["frames"], n["algorithm"])["faults"] == a["faults"], f"{n['id']}: faults")
    elif st == "disk_scheduling":
        check(S.disk(d["requests"], d["head"], n["algorithm"], d["direction"], d["size"])["total"] == a["total"],
              f"{n['id']}: head movement")
    elif st == "bankers_safety":
        check(S.bankers(d["available"], d["max"], d["allocation"])["safe"] == a["safe"], f"{n['id']}: safety")
    elif st == "bankers_request":
        check(S.bankers_request(d["available"], d["max"], d["allocation"], d["pid"], d["request"])["granted"]
              == a["granted"], f"{n['id']}: request")

for m in load(OUT / "mcqs.jsonl"):
    check(len(m["options"]) == 4 and len(set(m["options"])) == 4, f"{m['id']}: options not 4 distinct")
    check(0 <= m["answer_index"] < 4, f"{m['id']}: bad answer index")
    check(m["topic"] in config.TOPICS, f"{m['id']}: unknown topic")

print(f"Checked {len(ft)} fine-tuning rows, {len(nums)} numericals, {len(evalq)} held-out questions.")
if errors:
    print(f"{len(errors)} problem(s):")
    for e in errors[:30]:
        print("  -", e)
    sys.exit(1)
print("All dataset checks passed.")
