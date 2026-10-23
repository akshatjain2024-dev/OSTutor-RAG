import pickle
import re
import sqlite3
from functools import lru_cache

import faiss
import numpy as np

import config
from embedder import Embedder
from topics import STOPWORDS, detect_topics, expand_query, tokenize


class Reranker:
    def __init__(self):
        self.model, self.kind = None, config.RERANK_BACKEND
        if self.kind in ("auto", "ce"):
            try:
                from sentence_transformers import CrossEncoder
                self.model = CrossEncoder(config.RERANK_MODEL)
                self.kind = "cross-encoder"
            except Exception:
                if self.kind == "ce":
                    raise
                self.kind = "lexical"

    def score(self, query, texts):
        if self.kind == "off":
            return np.zeros(len(texts))
        if self.model is not None:
            return np.asarray(self.model.predict([(query, t) for t in texts]), dtype=float)
        q_terms = [t for t in tokenize(query) if t not in STOPWORDS and len(t) > 1]
        if not q_terms:
            return np.zeros(len(texts))
        out = []
        ql = query.lower()
        bigrams = [" ".join(p) for p in zip(q_terms, q_terms[1:])]
        for t in texts:
            tl = t.lower()
            toks = set(tokenize(t))
            cover = sum(1 for q in set(q_terms) if q in toks) / len(set(q_terms))
            phrase = sum(1 for b in bigrams if b in tl) / max(1, len(bigrams))
            exact = 1.0 if len(ql) > 8 and ql.strip("? ") in tl else 0.0
            out.append(cover + 0.6 * phrase + 0.5 * exact)
        return np.asarray(out)


class OSSearch:
    def __init__(self):
        self.index = faiss.read_index(str(config.FAISS_PATH))
        with open(config.BM25_PATH, "rb") as f:
            self.bm25 = pickle.load(f)
        self.embedder = Embedder.load()
        self.reranker = Reranker()
        con = sqlite3.connect(config.META_DB)
        con.row_factory = sqlite3.Row
        self.chunks = [dict(r) for r in con.execute("SELECT * FROM chunks ORDER BY id")]
        con.close()
        n = min(self.index.ntotal, len(self.chunks))
        if self.index.ntotal != len(self.chunks):
            print(f"[search] warning: index={self.index.ntotal} meta={len(self.chunks)}; using {n}")
        self.n = n

    @staticmethod
    def _minmax(x):
        x = np.asarray(x, dtype=float)
        if x.size == 0 or x.max() == x.min():
            return np.zeros_like(x)
        return (x - x.min()) / (x.max() - x.min())

    @staticmethod
    def _snippet(text, query, width=260):
        text = " ".join(text.split())
        terms = [t for t in tokenize(query) if t not in STOPWORDS and len(t) > 2]
        pos = min((m.start() for t in terms
                   for m in [re.search(re.escape(t), text, re.I)] if m), default=0)
        start = max(0, pos - 60)
        s = text[start:start + width]
        if start > 0:
            s = "..." + s[s.find(" ") + 1:]
        if start + width < len(text):
            s = s[:s.rfind(" ")] + "..."
        return s

    def topics(self):
        from collections import Counter
        return dict(Counter(c["topic"] for c in self.chunks).most_common())

    def search(self, query, k=config.FINAL_K, topic=None, doc_type=None, rerank=True):
        query = query.strip()
        if not query:
            return {"query": query, "results": [], "detected_topics": []}
        expanded = expand_query(query)
        detected = detect_topics(expanded, top_n=2)

        bm = np.zeros(self.n)
        bm[:] = self.bm25.get_scores(tokenize(expanded))[: self.n]
        dense = np.zeros(self.n)
        qv = self.embedder.encode_query(expanded)
        D, I = self.index.search(qv, min(config.DENSE_K * 3, self.n))
        for d, i in zip(D[0], I[0]):
            if 0 <= i < self.n:
                dense[i] = d

        fused = config.W_BM25 * self._minmax(bm) + config.W_DENSE * self._minmax(dense)

        mask = np.ones(self.n, dtype=bool)
        for i, c in enumerate(self.chunks[: self.n]):
            if topic and c["topic"] != topic:
                mask[i] = False
            if doc_type and c["doc_type"] != doc_type:
                mask[i] = False
            if not topic and detected and c["topic"] in detected:
                fused[i] += 0.25 if c["topic"] == detected[0] else 0.1
        fused[~mask] = -1

        cand = [i for i in np.argsort(-fused)[:20] if fused[i] > 0]
        if not cand:
            return {"query": query, "expanded": expanded, "detected_topics": detected,
                    "results": [], "reranker": self.reranker.kind}

        final = fused[cand]
        if rerank and self.reranker.kind != "off":
            rr = self._minmax(self.reranker.score(
                expanded, [f"{self.chunks[i]['section']}. {self.chunks[i]['text']}" for i in cand]))
            final = 0.5 * self._minmax(fused[cand]) + 0.5 * rr

        is_num = bool(re.search(
            r"\b(calculate|compute|solve|numerical|gantt|matrix|available\s*=|given\s+allocation)\b",
            query, re.I
        ))

        q_terms = {t for t in tokenize(expanded) if t not in STOPWORDS and len(t) > 2}
        adjs = []
        for i in cand:
            c = self.chunks[i]
            w = 1.0
            dt = c.get("doc_type", "")
            fn = c.get("file", "").lower()
            sn = c.get("section", "").lower()
            th = c.get("text", "")[:160].lower()

            base_weights = {"question_bank": 0.5, "past_paper": 0.7, "textbook": 1.05, "faculty": 1.1}
            w *= base_weights.get(dt, 1.0)

            if not is_num:
                if any(p in fn for p in ("worked_example", "faculty_problem", "past_paper_sol", "solution")):
                    w *= 0.6
                if fn.endswith(".md") and re.match(r"^\d{2}_", fn) and not fn.startswith(("20_", "21_", "22_")):
                    w *= 1.35

            sec_tokens = set(tokenize(sn))
            overlap = len(q_terms & sec_tokens)
            if overlap >= 2 or (len(q_terms) == 1 and overlap == 1):
                w *= 1.25

            if any(term in th for term in q_terms):
                if any(kw in th for kw in (": a ", " is a ", " are ", " defined as ", " algorithm: ")):
                    w *= 1.15

            adjs.append(w)

        final = final * np.array(adjs)
        order = [cand[j] for j in np.argsort(-final)]
        score_of = {cand[j]: float(final[j]) for j in range(len(cand))}

        results, seen = [], set()
        for i in order:
            c = self.chunks[i]
            key = c["id"] if c["doc_type"] == "question_bank" else (c["file"], c["section"])
            if key in seen:
                continue
            seen.add(key)
            results.append({
                **c, "score": round(score_of[i], 4),
                "bm25": round(float(bm[i]), 3), "dense": round(float(dense[i]), 3),
                "snippet": self._snippet(c["text"], query),
            })
            if len(results) >= k:
                break
        return {"query": query, "expanded": expanded, "detected_topics": detected,
                "results": results, "reranker": self.reranker.kind,
                "embedder": self.embedder.backend}


@lru_cache(maxsize=1)
def get_search():
    return OSSearch()


if __name__ == "__main__":
    import sys
    s = get_search()
    q = " ".join(sys.argv[1:]) or "what is belady's anomaly"
    out = s.search(q)
    print(f"Q: {q}\nexpanded: {out['expanded']}\ntopics: {out['detected_topics']}\n")
    for r in out["results"]:
        print(f"[{r['score']:.3f}] {r['topic']} > {r['section']} ({r['file']})\n   {r['snippet']}\n")
