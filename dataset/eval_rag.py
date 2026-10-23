import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

import llm
import prompts
from search import OSSearch
from topics import STOPWORDS

EVAL = HERE / "out" / "eval" / "rag_eval.jsonl"


def toks(s):
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOPWORDS]


def f1(pred, gold):
    p, g = Counter(toks(pred)), Counter(toks(gold))
    common = sum((p & g).values())
    if not common:
        return 0.0
    prec, rec = common / sum(p.values()), common / sum(g.values())
    return round(2 * prec * rec / (prec + rec), 3)


def keyword_recall(pred, gold):
    keys = {t for t in toks(gold) if len(t) > 3}
    if not keys:
        return 0.0
    return round(len(keys & set(toks(pred))) / len(keys), 3)


def main(use_llm=False):
    rows = [json.loads(l) for l in open(EVAL)]
    s = OSSearch()
    llm_up = use_llm and llm.rag_available(force=True)
    if use_llm and not llm_up:
        print("RAG model not reachable — running without the LLM columns.")
    results = []
    for r in rows:
        res = s.search(r["question"], k=4)["results"]
        topics = [x["topic"] for x in res]
        out = {"id": r["id"], "type": r["type"], "topic": r["topic"], "question": r["question"],
               "hit@1": int(bool(topics) and topics[0] == r["topic"]), "hit@3": int(r["topic"] in topics[:3])}
        if r["type"] == "qa":
            gold = r["gold_answer"]
            notes = [x for x in res if x["doc_type"] != "question_bank"] or res
            off = llm.offline_answer(r["question"], notes) if notes else ""
            out |= {"offline_f1": f1(off, gold), "offline_kw": keyword_recall(off, gold)}
            if llm_up:
                with_rag = llm.chat([{"role": "system", "content": prompts.TUTOR_SYSTEM},
                                     {"role": "user", "content": prompts.ANSWER_TEMPLATE.format(
                                         context=prompts.build_context(notes), question=r["question"])}])
                no_rag = llm.chat([{"role": "system", "content": prompts.TUTOR_SYSTEM.split("\n\nRULES:")[0]},
                                   {"role": "user", "content": r["question"]}])
                out |= {"rag_f1": f1(with_rag, gold), "rag_kw": keyword_recall(with_rag, gold),
                        "norag_f1": f1(no_rag, gold), "norag_kw": keyword_recall(no_rag, gold),
                        "rag_answer": with_rag, "norag_answer": no_rag}
        results.append(out)

    path = HERE / "out" / "eval" / "results.csv"
    keys = sorted({k for r in results for k in r}, key=lambda k: list(results[-1]).index(k)
                  if k in results[-1] else 99)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(results)

    def avg(key, typ=None):
        vals = [r[key] for r in results if key in r and (typ is None or r["type"] == typ)]
        return round(sum(vals) / len(vals), 3) if vals else None

    print(f"\nRetrieval ({len(results)} questions): topic hit@1 = {avg('hit@1')}, hit@3 = {avg('hit@3')}")
    qa = [r for r in results if r["type"] == "qa"]
    print(f"Answers on {len(qa)} held-out viva questions (token F1 / keyword recall vs gold):")
    print(f"  RAG, offline extractive : F1 {avg('offline_f1')}  keywords {avg('offline_kw')}")
    if llm_up:
        print(f"  LLM + RAG               : F1 {avg('rag_f1')}  keywords {avg('rag_kw')}")
        print(f"  LLM without RAG         : F1 {avg('norag_f1')}  keywords {avg('norag_kw')}")
    worst = sorted(qa, key=lambda r: r["offline_f1"])[:3]
    print("Weakest offline answers:", [w["question"][:60] for w in worst])
    print(f"Saved per-question scores to {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true")
    main(ap.parse_args().llm)
