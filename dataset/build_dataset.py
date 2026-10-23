import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

import config
import gen_numericals
import prompts

SRC, OUT = HERE / "src", HERE / "out"
SYSTEM = prompts.TUTOR_SYSTEM.split("\n\nRULES:")[0]
rng = random.Random(7)


def parse_question_bank():
    items = []
    for ln, line in enumerate((SRC / "question_bank.txt").read_text().splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) not in (4, 5):
            raise ValueError(f"question_bank.txt line {ln}: expected 4 or 5 fields, got {len(parts)}")
        topic, marks, qtype, q = parts[:4]
        paper = parts[4] if len(parts) == 5 else None
        check_topic(topic, f"question_bank.txt:{ln}")
        items.append({"topic": topic, "marks": int(marks), "type": qtype, "question": q,
                      "source": paper or "practice (exam-style)", "real_paper": bool(paper)})
    for i, it in enumerate(items, 1):
        it["id"] = f"qb-{i:03d}"
    return items


def split_sections(text):
    for block in re.split(r"(?m)^## ", text)[1:]:
        topic, _, body = block.partition("\n")
        yield topic.strip(), body


def parse_viva():
    items = []
    for topic, body in split_sections((SRC / "viva.txt").read_text()):
        check_topic(topic, "viva.txt")
        for m in re.finditer(r"Q:\s*(.+?)\nA:\s*(.+?)(?=\n\s*\nQ:|\Z)", body.strip(), re.S):
            items.append({"topic": topic, "question": m.group(1).strip(), "answer": " ".join(m.group(2).split())})
    for i, it in enumerate(items, 1):
        it["id"] = f"viva-{i:03d}"
    return items


def parse_mcqs():
    items = []
    for topic, body in split_sections((SRC / "mcqs.txt").read_text()):
        check_topic(topic, "mcqs.txt")
        for blk in re.split(r"\n\s*\n", body.strip()):
            lines = [l.rstrip() for l in blk.strip().splitlines() if l.strip()]
            q = next(l[2:].strip() for l in lines if l.startswith("Q:"))
            opts = [(l[0] == "*", l[1:].strip()) for l in lines if l[:1] in "-*" and not l.startswith("Q")]
            exp = next((l[2:].strip() for l in lines if l.startswith("E:")), "")
            if len(opts) != 4 or sum(c for c, _ in opts) != 1:
                raise ValueError(f"mcqs.txt: bad options for '{q}'")
            items.append({"topic": topic, "question": q, "options": [o for _, o in opts],
                          "answer_index": [c for c, _ in opts].index(True), "explanation": exp,
                          "source": "concept"})
    for i, it in enumerate(items, 1):
        it["id"] = f"mcq-{i:03d}"
    return items


def parse_explanations():
    items = []
    for topic, body in split_sections((SRC / "explanations.txt").read_text()):
        check_topic(topic, "explanations.txt")
        for blk in re.split(r"(?m)^### ", body)[1:]:
            instr, _, ans = blk.partition("\n")
            items.append({"topic": topic, "instruction": instr.strip(), "answer": ans.strip()})
    for i, it in enumerate(items, 1):
        it["id"] = f"exp-{i:03d}"
    return items


def check_topic(t, where):
    if t not in config.TOPICS:
        raise ValueError(f"{where}: unknown topic '{t}'. Allowed: {config.TOPICS}")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def bucket(key):
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % 100


def chat(user, assistant, meta, system=SYSTEM):
    return {"messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user},
                         {"role": "assistant", "content": assistant}], "meta": meta}


LETTERS = "abcd"
REPHRASE = ["{q}", "Can you explain this? {q}", "I have my OS exam tomorrow. {q}",
            "Explain in simple words: {q}", "{q} Please keep it exam-oriented."]


def write_kb(qbank, viva_kb, numericals):
    qdir, ndir = config.QUESTIONS_DIR, config.NOTES_DIR
    old = qdir / "viva_and_pyq.md"
    if old.exists():
        old.unlink()
    lines = ["---", "topic: auto", "source: Previous year style questions", "doc_type: question_bank", "---",
             "# Exam question bank", ""]
    by_t = defaultdict(list)
    for q in qbank:
        by_t[q["topic"]].append(q)
    for t in config.TOPICS:
        if by_t[t]:
            lines.append(f"## {t}")
            lines += [f"Q: {q['question']} ({q['marks']} marks" + (f", {q['source']})" if q["real_paper"] else ")")
                      for q in by_t[t]]
            lines.append("")
    (qdir / "question_bank.md").write_text("\n".join(lines))

    lines = ["---", "topic: auto", "source: Viva questions", "doc_type: question_bank", "---",
             "# Viva questions and answers", ""]
    by_t = defaultdict(list)
    for v in viva_kb:
        by_t[v["topic"]].append(v)
    for t in config.TOPICS:
        if by_t[t]:
            lines.append(f"## {t}")
            for v in by_t[t]:
                lines += [f"Q: {v['question']}", f"A: {v['answer']}"]
            lines.append("")
    (qdir / "viva.md").write_text("\n".join(lines))

    lines = ["---", "topic: auto", "source: Worked examples (solver-verified)", "---", "# Worked examples", ""]
    seen = Counter()
    for n in numericals:
        if seen[n["subtype"]] >= 2:
            continue
        seen[n["subtype"]] += 1
        title = n.get("algorithm") or n["subtype"].replace("_", " ")
        lines += [f"## Worked example: {title} ({n['topic']})", "", "Question: " + n["question"], "",
                  "Solution: " + n["solution"], ""]
    (ndir / "20_worked_examples.md").write_text("\n".join(lines))


def rag_pairs(viva_items):
    import ingest
    from search import OSSearch
    ingest.main()
    s = OSSearch()
    out = []
    for v in viva_items:
        res = s.search(v["question"], k=3, doc_type="notes")["results"]
        cite = next((i for i, r in enumerate(res, 1) if r["topic"] == v["topic"]), None)
        if not res or cite is None:
            continue
        user = prompts.ANSWER_TEMPLATE.format(context=prompts.build_context(res), question=v["question"])
        out.append({"messages": [{"role": "system", "content": prompts.TUTOR_SYSTEM},
                                 {"role": "user", "content": user},
                                 {"role": "assistant", "content": f"{v['answer']} [{cite}]"}],
                    "meta": {"kind": "rag_grounded", "topic": v["topic"], "source_id": v["id"]}})
    return out


def main():
    qbank, viva, mcqs, expl = parse_question_bank(), parse_viva(), parse_mcqs(), parse_explanations()
    numericals = gen_numericals.main()
    num_mcqs = [json.loads(l) for l in open(OUT / "numerical_mcqs.jsonl")]

    eval_ids = set()
    by_t = defaultdict(list)
    for v in viva:
        by_t[v["topic"]].append(v)
    for t, vs in by_t.items():
        k = max(1, round(len(vs) / 3))
        eval_ids |= {v["id"] for v in sorted(vs, key=lambda v: bucket(v["id"]))[:k]}
    viva_train = [v for v in viva if v["id"] not in eval_ids]
    viva_eval = [v for v in viva if v["id"] in eval_ids]

    write_kb(qbank, viva_train, numericals)

    pairs = []
    for e in expl:
        pairs.append(chat(e["instruction"], e["answer"], {"kind": "explanation", "topic": e["topic"], "source_id": e["id"]}))
        alt = rng.choice(REPHRASE[1:]).format(q=e["instruction"])
        pairs.append(chat(alt, e["answer"], {"kind": "explanation_rephrased", "topic": e["topic"], "source_id": e["id"]}))
    for v in viva_train:
        pairs.append(chat(f"Viva question: {v['question']} Answer briefly.", v["answer"],
                          {"kind": "viva", "topic": v["topic"], "source_id": v["id"]}))
    for n in numericals:
        pairs.append(chat(n["question"], n["solution"],
                          {"kind": "numerical", "topic": n["topic"], "subtype": n["subtype"], "source_id": n["id"]}))
    for m in mcqs:
        opts = "\n".join(f"({LETTERS[i]}) {o}" for i, o in enumerate(m["options"]))
        ans = (f"**Answer: ({LETTERS[m['answer_index']]}) {m['options'][m['answer_index']]}**\n\n{m['explanation']}")
        pairs.append(chat(f"{m['question']}\n{opts}\nChoose the correct option and explain.", ans,
                          {"kind": "mcq", "topic": m["topic"], "source_id": m["id"]}))
    pairs += rag_pairs(viva_train)

    for t in config.TOPICS:
        tm = [m for m in mcqs if m["topic"] == t]
        if len(tm) >= 3:
            sample = rng.sample(tm, 3)
            out = json.dumps([{k: m[k] for k in ("question", "options", "answer_index", "explanation")}
                              for m in sample], ensure_ascii=False)
            pairs.append(chat(f'Write 3 multiple-choice questions on "{t}" for an OS exam. Return ONLY valid JSON: '
                              '[{"question": "...", "options": ["A","B","C","D"], "answer_index": 0, "explanation": "..."}]',
                              out, {"kind": "mcq_generation", "topic": t}))
        tv = [v for v in viva_train if v["topic"] == t]
        if len(tv) >= 3:
            sample = rng.sample(tv, 3)
            out = json.dumps([{"question": v["question"], "answer": v["answer"]} for v in sample], ensure_ascii=False)
            pairs.append(chat(f'Write 3 short viva questions on "{t}" with 1-2 line model answers. Return ONLY valid JSON: '
                              '[{"question": "...", "answer": "..."}]', out, {"kind": "viva_generation", "topic": t}))

    train, val = [], []
    for p in pairs:
        key = p["meta"].get("source_id") or p["messages"][1]["content"]
        (val if bucket(key) < 8 else train).append(p)
    rng.shuffle(train)
    write_jsonl(OUT / "finetune" / "train.jsonl", train)
    write_jsonl(OUT / "finetune" / "val.jsonl", val)
    to_alpaca = lambda p: {"instruction": p["messages"][1]["content"], "input": "",
                           "output": p["messages"][2]["content"], "system": p["messages"][0]["content"]}
    write_jsonl(OUT / "finetune" / "train_alpaca.jsonl", [to_alpaca(p) for p in train])
    write_jsonl(OUT / "finetune" / "val_alpaca.jsonl", [to_alpaca(p) for p in val])

    from tests.smoke_test import EVAL as SEARCH_EVAL
    eval_rows = [{"id": v["id"], "type": "qa", "topic": v["topic"], "question": v["question"],
                  "gold_answer": v["answer"]} for v in viva_eval]
    eval_rows += [{"id": f"search-{i:03d}", "type": "retrieval", "topic": t, "question": q}
                  for i, (q, t) in enumerate(SEARCH_EVAL, 1)]
    write_jsonl(OUT / "eval" / "rag_eval.jsonl", eval_rows)

    write_jsonl(OUT / "question_bank.jsonl", qbank)
    write_jsonl(OUT / "viva.jsonl", [v | {"split": "eval" if v["id"] in eval_ids else "train"} for v in viva])
    write_jsonl(OUT / "mcqs.jsonl", mcqs + num_mcqs)
    write_jsonl(OUT / "explanations.jsonl", expl)

    kinds = Counter(p["meta"]["kind"] for p in train + val)
    stats = {
        "knowledge_base_notes": len(list(config.NOTES_DIR.glob("*.md"))),
        "question_bank": len(qbank), "question_bank_real_past_papers": sum(q["real_paper"] for q in qbank), "viva_total": len(viva), "viva_heldout_for_eval": len(viva_eval),
        "mcqs_concept": len(mcqs), "mcqs_numerical": len(num_mcqs), "numericals": len(numericals),
        "explanations": len(expl), "finetune_train": len(train), "finetune_val": len(val),
        "finetune_by_kind": dict(kinds), "eval_rows": len(eval_rows),
        "numericals_by_type": dict(Counter(n["subtype"] for n in numericals)),
        "topic_coverage": {t: {"questions": sum(q["topic"] == t for q in qbank),
                               "viva": sum(v["topic"] == t for v in viva),
                               "mcqs": sum(m["topic"] == t for m in mcqs + num_mcqs),
                               "numericals": sum(n["topic"] == t for n in numericals),
                               "explanations": sum(e["topic"] == t for e in expl)} for t in config.TOPICS},
    }
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps({k: v for k, v in stats.items() if k != "topic_coverage"}, indent=2))
    return stats


if __name__ == "__main__":
    main()
