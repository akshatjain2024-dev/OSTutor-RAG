# OSTutor – Operating Systems Tutor using RAG

**Team:** Akshat Jain (24BCE0380) · Vidit Basant Kumar (24BCE0388)

OSTutor answers Operating Systems questions from our own course material (textbook, faculty
slides, lecture transcripts, past CAT papers and our notes). It finds the right passages with a
hybrid search engine and then a local LLM (Qwen 2.5 through Ollama) writes the answer with
citations like [1], [2]. If Ollama is not running, the answer is taken straight from the notes.

---

## How to run (Windows)

| Double-click | What it does |
|---|---|
| `run.bat` | Starts the backend (port 8003) and opens the web page (port 8503) |
| `build_index.bat` | Rebuilds the search index after adding files to `data/` |
| `run_tests.bat` | Runs the accuracy test, the evaluation and the dataset checks (results in `logs/`) |

For LLM answers, keep Ollama running with the model installed: `ollama run qwen2.5:3b`.

---

## Project structure

```
OSTutorSearch/
├── run.bat, build_index.bat, run_tests.bat    one-click scripts
├── README.md                                  this file
├── requirements.txt                           Python packages
│
├── src/                  the application
├── data/                 study material + chat history
├── index/                search index built from data/
├── dataset/              question bank, MCQs, numericals, evaluation set
├── tests/                automated checks
├── docs/                 case study and project documents
└── venv/                 Python environment
```

### `src/` – the application, in the order a question flows through it

| File | Purpose |
|---|---|
| `config.py` | All settings in one place: folder paths, chunk size, search weights, Ollama model, ports |
| `ingest.py` | Builds the knowledge base: reads PDF / PPT / DOCX / notes, cleans them, labels each piece with a topic, cuts it into chunks and saves the search index |
| `embedder.py` | Turns text into vectors (BGE model, or TF-IDF + SVD when that model is not installed) |
| `topics.py` | The 17 OS topics with their keywords, abbreviation expansion (rr → round robin) and topic detection |
| `search.py` | Hybrid search: BM25 keyword search + FAISS vector search, topic boost, re-ranking, top 5 results |
| `prompts.py` | The instructions given to the LLM for answers, MCQs, viva questions and practice problems |
| `llm.py` | Talks to Ollama to write the answer; falls back to picking sentences from the notes when Ollama is off |
| `chat_store.py` | Saves conversations in SQLite so old chats appear in the sidebar |
| `app.py` | FastAPI backend: `/ask`, `/search`, `/mcq`, `/viva`, `/practice`, `/topics`, `/conversations` |
| `streamlit_app.py` | The web page students use (chat window + chat history) |

### `data/` – knowledge base

| Folder | Contents |
|---|---|
| `notes/` | Our cleaned topic notes (01–19), worked examples and solved papers |
| `questions/` | Question bank and viva questions |
| `raw/textbook/` | Silberschatz, Operating System Concepts (8th ed.) |
| `raw/faculty/` | Faculty slides, notes, OSTEP chapters, Linux commands, shell programming |
| `raw/question_papers/` | BACSE106 CAT papers |
| `raw/youtube/` | Lecture transcripts (Gate Smashers OS playlist) |
| `chat_history.db` | Saved conversations |

Each `raw/` folder has a `_sources.json` that gives the topic and source name of every file.

The textbook, faculty slides, lecture transcripts and CAT papers are not included in this
repository because they belong to their authors. Put them in the matching `data/raw/` folder
and run `build_index.bat` to create the `index/` folder.

### `index/` – built by `build_index.bat`

`chunks.db` (text + topic + source of every chunk), `bm25.pkl` (keyword index),
`faiss.index` (vector index), `embedder.pkl` (vectoriser), `cache/` (saved text extraction).

### `dataset/`

| File | Purpose |
|---|---|
| `src/` | Hand-written question bank, viva questions, MCQs and explanations |
| `out/` | Generated dataset files and the 71-question evaluation set |
| `build_dataset.py` | Builds everything in `out/` from `src/` |
| `solvers.py`, `gen_numericals.py` | Generate numericals (scheduling, page replacement, Banker's…) with checked answers |
| `validate.py` | Checks the generated dataset |
| `eval_rag.py` | Measures search and answer quality on the held-out questions |
| `finetune_qlora.py` | Optional QLoRA fine-tuning script (needs a GPU) |
| `DATASET.md` | Description of the dataset |

### `tests/`

| File | Purpose |
|---|---|
| `smoke_test.py` | Rebuilds the index and checks 76 student-style questions land on the right topic/source |
| `test_rag_pipeline.py` | Checks Ollama answers, MCQs and viva questions (needs Ollama running) |

---

## How it works

```
Student question
   │
Streamlit page (8503)  ──►  FastAPI backend (8003)
                                │
                     1. expand abbreviations, detect topic      (topics.py)
                     2. BM25 + FAISS search, fuse scores        (search.py)
                     3. topic boost, re-rank, keep top 5
                                │
                     Ollama qwen2.5:3b writes the answer        (llm.py + prompts.py)
                     or offline answer from the notes
                                │
                     answer + sources shown, chat saved         (chat_store.py)
```

## Results (71 held-out questions, laptop CPU)

| Measure | Result |
|---|---|
| Correct topic in the first result | 97.2% |
| Correct topic in the top 3 | 98.6% |
| Search time per question | about 20 ms |
| Knowledge base | 113 files, 3,539 chunks, 17 topics |
