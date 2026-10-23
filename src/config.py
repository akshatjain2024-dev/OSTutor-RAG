import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
NOTES_DIR = DATA_DIR / "notes"
RAW_DIR = DATA_DIR / "raw"
QUESTIONS_DIR = DATA_DIR / "questions"
INDEX_DIR = BASE_DIR / "index"

FAISS_PATH = INDEX_DIR / "faiss.index"
BM25_PATH = INDEX_DIR / "bm25.pkl"
EMBEDDER_PATH = INDEX_DIR / "embedder.pkl"
META_DB = INDEX_DIR / "chunks.db"
CHAT_DB = DATA_DIR / "chat_history.db"

CHUNK_WORDS = int(os.getenv("CHUNK_WORDS", 220))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 40))

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-large-en-v1.5")
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "auto")

RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANK_BACKEND = os.getenv("RERANK_BACKEND", "auto")

BM25_K = 30
DENSE_K = 30
FINAL_K = 5
W_BM25 = 0.45
W_DENSE = 0.55

RAG_PROVIDER = os.getenv("RAG_PROVIDER", "ollama")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 850))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", 60))

API_PORT = int(os.getenv("API_PORT", 8003))
API_URL = os.getenv("API_URL", f"http://127.0.0.1:{API_PORT}")

TOPICS = [
    "Process Management", "Threads", "CPU Scheduling", "Process Synchronization",
    "Deadlocks", "Memory Management", "Virtual Memory", "File Systems",
    "Disk Scheduling", "System Calls", "Inter-Process Communication",
    "Linux Commands", "Shell Programming", "OS Basics",
    "I/O Systems", "Protection and Security", "Virtualization",
]
