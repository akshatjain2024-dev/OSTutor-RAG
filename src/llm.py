import json
import os
import random
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

import config
import prompts
from topics import STOPWORDS, tokenize

_status_cache = {"checked": 0.0, "provider": "offline", "model": "extractive", "available": False}


def get_active_provider(force=False) -> Dict[str, Any]:
    now = time.time()
    if not force and now - _status_cache["checked"] < 20:
        return {
            "provider": _status_cache["provider"],
            "model": _status_cache["model"],
            "available": _status_cache["available"],
        }

    if _check_ollama():
        installed = list_ollama_models()
        model = config.OLLAMA_MODEL
        if installed and model not in installed:
            model = installed[0]
        _status_cache.update({"checked": now, "provider": "ollama", "model": model, "available": True})
        return _status_cache

    _status_cache.update({"checked": now, "provider": "offline", "model": "extractive", "available": False})
    return _status_cache


def rag_available(force=False) -> bool:
    return get_active_provider(force)["available"]


def _check_ollama() -> bool:
    try:
        r = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


def list_ollama_models() -> List[str]:
    try:
        r = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2)
        if r.ok:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return []


def _chat_ollama(messages: List[Dict[str, str]], model: str = None, max_tokens: int = config.LLM_MAX_TOKENS,
                 temperature: float = 0.3) -> str:
    m = model or config.OLLAMA_MODEL
    url = f"{config.OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": m,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        }
    }
    r = requests.post(url, json=payload, timeout=config.LLM_TIMEOUT)
    r.raise_for_status()
    text = r.json().get("message", {}).get("content", "")
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def chat(messages: List[Dict[str, str]], provider: Optional[str] = None, model: Optional[str] = None,
         max_tokens: int = config.LLM_MAX_TOKENS, temperature: float = 0.3) -> str:
    info = get_active_provider()
    active_prov = (provider or info["provider"]).lower()
    active_mod = model or info["model"]

    if active_prov == "ollama":
        return _chat_ollama(messages, model=active_mod, max_tokens=max_tokens, temperature=temperature)
    else:
        raise RuntimeError(f"No active generative LLM provider available (current: {active_prov})")


def _parse_json_list(text: str) -> List[Any]:
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError("no JSON list in model output")
    return json.loads(m.group(0))


def answer(question: str, results: List[Dict[str, Any]], history: Optional[List[Dict[str, str]]] = None,
           provider: Optional[str] = None, model: Optional[str] = None) -> Tuple[str, str]:
    if not results:
        return ("I couldn't find anything about that in your OS notes. Try rephrasing, "
                "or use a keyword like 'deadlock', 'paging' or 'fork'."), "offline"

    notes_results = [r for r in results if r.get("doc_type") != "question_bank"] or results
    prov_info = get_active_provider()
    current_prov = provider or prov_info["provider"]
    current_mod = model or prov_info["model"]

    if prov_info["available"] or provider:
        try:
            msgs = [{"role": "system", "content": prompts.TUTOR_SYSTEM}]
            for m in (history or [])[-4:]:
                msgs.append({"role": m["role"], "content": m["content"][:600]})
            msgs.append({"role": "user", "content": prompts.ANSWER_TEMPLATE.format(
                context=prompts.build_context(notes_results), question=question)})
            text = chat(msgs, provider=current_prov, model=current_mod)
            return text, f"rag:{current_prov}:{current_mod}"
        except Exception as e:
            print(f"[rag] Generation with {current_prov} failed ({e}), falling back to extractive: {e}")

    return offline_answer(question, notes_results), "offline"


def _sentences(text: str) -> List[str]:
    text = " ".join(text.split())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\-])", text) if len(s.strip()) > 20]


def offline_answer(question: str, results: List[Dict[str, Any]], max_sents: int = 6) -> str:
    q = {t for t in tokenize(question) if t not in STOPWORDS and len(t) > 2}
    written = [r for r in results if r.get("doc_type") not in ("youtube", "past_paper", "question_bank")]
    if written:
        rank = {"notes": 0, "faculty": 1, "textbook": 2}
        ordered = sorted(enumerate(written), key=lambda x: (
            -len(q & set(tokenize(x[1].get("section") or ""))), rank.get(x[1].get("doc_type"), 3), x[0]))
        results = [r for _, r in ordered]
    picked, seen = [], set()
    top = results[0]
    for ci, r in enumerate(results[:3], 1):
        if ci > 1 and r["topic"] != top["topic"]:
            continue
        sents = [s for s in _sentences(r["text"]) if s[0].isupper() or s[0].isdigit() or s[0] == "-"]
        sents = [s for s in sents if not s.rstrip().endswith("?") and not s.startswith("Question:")
                 and len(s.split()) <= 60]
        scored = []
        for si, s in enumerate(sents):
            overlap = len(q & set(tokenize(s)))
            defines = any(re.match(rf"(?:an? |the )?{re.escape(t)}\w*\s+(?:is|are|means|occurs)\b", s.lower()) for t in q)
            scored.append((overlap + (0.5 if si == 0 else 0) + (1.5 if defines else 0) - 0.3 * ci, si, s))
        best = sorted(scored, reverse=True)[: (3 if ci == 1 else 2)]
        for sc, si, s in sorted(best, key=lambda x: x[1]):
            key = " ".join(s.lower().split())
            if key in seen:
                continue
            if ci == 1 or q & set(tokenize(s)):
                seen.add(key)
                picked.append((ci, s))
    picked = picked[:max_sents]
    paras, cur, buf = [], None, []
    for ci, s in picked:
        if ci != cur and buf:
            paras.append(" ".join(buf) + f" [{cur}]")
            buf = []
        cur = ci
        buf.append(s if s.endswith((".", "?", "!", ":")) else s + ".")
    if buf:
        paras.append(" ".join(buf) + f" [{cur}]")
    return "\n\n".join(paras)


def _llm_json(template: str, topic: str, results: List[Dict[str, Any]], n: int,
              provider: Optional[str] = None, model: Optional[str] = None) -> Optional[List[Any]]:
    prov_info = get_active_provider()
    if not (prov_info["available"] or provider):
        return None
    try:
        out = chat([{"role": "user", "content": template.format(
            n=n, topic=topic, context=prompts.build_context(results, 900))}],
            provider=provider, model=model, max_tokens=1200, temperature=0.4)
        return _parse_json_list(out)[:n]
    except Exception as e:
        print(f"[rag] JSON generation failed: {e}")
        return None


def _definitions(results: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    defs = []
    for r in results:
        for line in r["text"].splitlines():
            m = re.match(r"^\s*[-*\d.]*\s*([A-Z][\w\s\-()/']{2,45}?):\s+(.{25,220})$", line.strip())
            if m and not m.group(1).lower().startswith(("q", "example", "note")):
                defs.append((m.group(1).strip(), m.group(2).strip()))
        for s in _sentences(r["text"]):
            m = re.match(r"^(?:An?|The)\s+([\w\s\-()]{3,40}?)\s+(?:is|are)\s+((?:a|an|the|when|where)\b.{20,})$", s)
            if m:
                defs.append((m.group(1).strip(), m.group(2).rstrip(".")))
    seen, out = set(), []
    for t, d in defs:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append((t[0].upper() + t[1:], d))
    return out


def mcqs(topic: str, results: List[Dict[str, Any]], n: int = 5, seed: Optional[int] = None,
         provider: Optional[str] = None, model: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
    got = _llm_json(prompts.MCQ_TEMPLATE, topic, results, n, provider=provider, model=model)
    if got:
        prov = provider or get_active_provider()["provider"]
        return got, f"rag:{prov}"
    rng = random.Random(seed)
    defs = _definitions([r for r in results if r.get("doc_type") == "notes"
                         and not r.get("file", "").startswith(("20_", "21_"))] or results)
    terms = [t for t, _ in defs]
    qs = []
    for term, d in defs:
        others = [t for t in terms if t.lower() != term.lower()]
        if len(others) < 3:
            continue
        d_clean = re.sub(re.escape(term), "____", d, flags=re.I)
        opts = rng.sample(others, 3) + [term]
        rng.shuffle(opts)
        qs.append({"question": f"Which term matches this description: \"{d_clean}\"",
                   "options": opts, "answer_index": opts.index(term),
                   "explanation": f"{term}: {d}"})
    rng.shuffle(qs)
    return qs[:n], "offline"


def _short_answer(question: str, lookup) -> str:
    hits = lookup(question) if lookup else []
    if not hits:
        return "(Check your notes)"
    q = {t for t in tokenize(question) if t not in STOPWORDS and len(t) > 2}
    sents = [s for s in _sentences(hits[0]["text"]) if s[0].isupper() or s[0].isdigit()]
    best = sorted(sents, key=lambda s: -len(q & set(tokenize(s))))[:2]
    return " ".join(s for s in sents if s in best) or "(Check your notes)"


def viva(topic: str, results: List[Dict[str, Any]], past_questions: List[Dict[str, Any]], n: int = 6,
         lookup=None, provider: Optional[str] = None, model: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
    got = _llm_json(prompts.VIVA_TEMPLATE, topic, results, n, provider=provider, model=model)
    if got:
        prov = provider or get_active_provider()["provider"]
        return got, f"rag:{prov}"
    out = []
    for q in past_questions:
        qt = q["text"].removeprefix("Q:").strip()
        out.append({"question": qt, "answer": _short_answer(qt, lookup), "source": "past paper"})
    for r in results:
        sents = _sentences(r["text"])
        if r["doc_type"] != "question_bank" and sents and r.get("section"):
            out.append({"question": f"Explain: {r['section']}", "answer": sents[0]})
    return out[:n], "offline"


def practice(topic: str, results: List[Dict[str, Any]], past_questions: List[Dict[str, Any]], n: int = 4,
             provider: Optional[str] = None, model: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
    got = _llm_json(prompts.PRACTICE_TEMPLATE, topic, results, n, provider=provider, model=model)
    if got:
        prov = provider or get_active_provider()["provider"]
        return got, f"rag:{prov}"
    numerical = [q for q in past_questions
                 if re.search(r"\b(compute|calculate|find|given|how many|solve)\b", q["text"], re.I)]
    worked = [r for r in results if "example" in r.get("section", "").lower()]
    out = [{"problem": q["text"].removeprefix("Q:").strip(),
            "solution": "Try it yourself, then compare with the worked example in your notes."}
           for q in numerical]
    out += [{"problem": f"Worked example from notes: {r['section']}", "solution": " ".join(r["text"].split())}
            for r in worked]
    return out[:n], "offline"
