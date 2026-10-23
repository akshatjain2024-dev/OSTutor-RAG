import re
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import chat_store
import config
import llm
from search import get_search

app = FastAPI(title="OSTutor Search & RAG", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup_event():
    try:
        get_search()
        llm.get_active_provider(force=True)
    except Exception as e:
        print(f"[startup] Warmup notice: {e}")


class SearchReq(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    k: int = Field(config.FINAL_K, ge=1, le=20)
    topic: Optional[str] = None
    doc_type: Optional[str] = None


class AskReq(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: str = "default"
    conv_id: Optional[str] = None
    topic: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class GenReq(BaseModel):
    topic: str
    n: int = Field(5, ge=1, le=15)
    provider: Optional[str] = None
    model: Optional[str] = None


def _source_cards(results):
    return [{k: r[k] for k in ("id", "topic", "section", "source", "file", "page",
                               "doc_type", "score", "snippet")} for r in results]


FOLLOWUP = re.compile(r"\b(it|its|that|this|they|them|those|these|above|same|more|example)\b", re.I)


def _search_query(question, history):
    if history and len(question.split()) <= 7 and FOLLOWUP.search(question):
        prev = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        return f"{prev} {question}"
    return question


def _topic_material(topic):
    s = get_search()
    if topic not in s.topics():
        raise HTTPException(404, f"Unknown topic '{topic}'. See /topics.")
    notes = [c for c in s.chunks if c["topic"] == topic and c["doc_type"] != "question_bank"]
    past = [c for c in s.chunks if c["topic"] == topic and c["doc_type"] == "question_bank"]
    return notes, past


@app.get("/health")
def health():
    s = get_search()
    prov = llm.get_active_provider(force=True)
    return {
        "status": "ok",
        "chunks": s.n,
        "embedder": s.embedder.backend,
        "reranker": s.reranker.kind,
        "rag_available": prov["available"],
        "rag_provider": prov["provider"],
        "rag_model": prov["model"],
        "llm": prov["provider"],
        "llm_model": prov["model"],
    }


@app.get("/providers")
def providers():
    return {
        "active": llm.get_active_provider(),
        "ollama_models": llm.list_ollama_models(),
        "supported_providers": ["ollama", "offline"],
    }


@app.get("/topics")
def topics():
    return get_search().topics()


@app.post("/search")
def search(req: SearchReq):
    out = get_search().search(req.query, k=req.k, topic=req.topic, doc_type=req.doc_type)
    out["results"] = _source_cards(out["results"])
    return out


@app.post("/ask")
def ask(req: AskReq):
    conv_id = req.conv_id or chat_store.new_conversation(req.session_id)
    history = chat_store.get_messages(conv_id)
    q = _search_query(req.question, history)
    found = get_search().search(q, k=4, topic=req.topic)
    found["results"].sort(key=lambda r: r["doc_type"] == "question_bank")
    text, mode = llm.answer(req.question, found["results"], history,
                            provider=req.provider, model=req.model)
    sources = _source_cards(found["results"])
    chat_store.add_message(conv_id, "user", req.question)
    chat_store.add_message(conv_id, "assistant", text, sources)
    return {
        "answer": text, "mode": mode, "sources": sources, "conv_id": conv_id,
        "detected_topics": found["detected_topics"], "search_query": q,
        "rag_provider": req.provider or llm.get_active_provider()["provider"],
        "rag_model": req.model or llm.get_active_provider()["model"],
    }


@app.post("/mcq")
def mcq(req: GenReq):
    notes, _ = _topic_material(req.topic)
    qs, mode = llm.mcqs(req.topic, notes, req.n, provider=req.provider, model=req.model)
    return {"topic": req.topic, "mode": mode, "questions": qs}


@app.post("/viva")
def viva(req: GenReq):
    notes, past = _topic_material(req.topic)
    lookup = lambda q: get_search().search(q, k=1, topic=req.topic, doc_type="notes")["results"]
    qs, mode = llm.viva(req.topic, notes, past, req.n, lookup=lookup,
                        provider=req.provider, model=req.model)
    return {"topic": req.topic, "mode": mode, "questions": qs}


@app.post("/practice")
def practice(req: GenReq):
    notes, past = _topic_material(req.topic)
    qs, mode = llm.practice(req.topic, notes, past, req.n,
                            provider=req.provider, model=req.model)
    return {"topic": req.topic, "mode": mode, "problems": qs}


@app.get("/conversations")
def conversations(session_id: str):
    return chat_store.list_conversations(session_id)


@app.post("/conversations")
def new_conv(session_id: str):
    return {"conv_id": chat_store.new_conversation(session_id)}


@app.get("/conversations/{conv_id}")
def conversation(conv_id: str):
    return chat_store.get_messages(conv_id)


@app.delete("/conversations")
def clear_conversations(session_id: str):
    chat_store.clear_all(session_id)
    return {"cleared": session_id}


@app.delete("/conversations/{conv_id}")
def delete_conv(conv_id: str):
    chat_store.delete_conversation(conv_id)
    return {"deleted": conv_id}
