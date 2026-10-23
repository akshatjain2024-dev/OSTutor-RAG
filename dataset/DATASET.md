# OSTutorLLM Dataset

Dataset for the OSTutorLLM case study (Akshat 24BCE0380, Vidit Basant Kumar 24BCE0388). It serves the
two parts of the design: the **RAG knowledge base** that the search system retrieves from, and the
optional **fine-tuning set** that teaches the model a teacher-like explaining style. It also includes an
**evaluation set** for the "RAG vs plain LLM" comparison planned in the conclusion.

Rebuild everything with one command (deterministic, same output every time):
```bash
python dataset/build_dataset.py     # build all files + refresh the knowledge base
python dataset/validate.py          # format, leakage and answer checks
python dataset/eval_rag.py          # retrieval + answer scores on the held-out set
```

## What's in it

| Part | Count | File | Used for |
|---|---|---|---|
| Faculty material (slides, OSTEP readings, lab sheets, Linux notes, problem sheets) | 40 files → 650 chunks | `data/raw/faculty/` | RAG knowledge base, ranked first |
| Textbook: Silberschatz, *Operating System Concepts* 8th ed. (syllabus chapters only) | 1865 chunks | `data/raw/textbook/` (you add the PDF) | RAG knowledge base |
| YouTube transcripts: Gate Smashers OS lectures Lec-0 and L-1.1 to L-5.5 (46 indexed, 4 Hindi ones skipped) | 545 chunks | `data/raw/youtube/` | RAG knowledge base |
| Past papers with answer keys (CAT-1 G2, CAT-2 G1, Winter 2025-26) | 36 chunks | `data/raw/question_papers/` | RAG knowledge base |
| Topic notes, worked examples and solved past-paper numericals | 22 files | `data/notes/*.md` | RAG knowledge base |
| Worked examples (2 per numerical type) | 14 sections | `data/notes/20_worked_examples.md` | RAG knowledge base |
| Exam question bank (topic, marks, type), incl. **34 real CAT questions** from 6 papers | 200 | `out/question_bank.jsonl`, `data/questions/question_bank.md` | search "past questions", practice tab |
| Viva Q&A with model answers | 133 (90 train, 43 held out) | `out/viva.jsonl`, `data/questions/viva.md` | KB, fine-tuning, evaluation |
| Concept MCQs with explanations | 90 | `out/mcqs.jsonl` | quiz, fine-tuning |
| Numerical MCQs (from solved problems) | 148 | `out/mcqs.jsonl` | quiz |
| Numericals with step-by-step solutions | 274 | `out/numericals.jsonl` | practice, fine-tuning |
| Teacher-style explanations | 46 | `out/explanations.jsonl` | fine-tuning (the target "voice") |
| Fine-tuning pairs | 621 train / 42 val | `out/finetune/*.jsonl` | QLoRA (`finetune_qlora.py`) |
| Evaluation rows | 71 (43 QA + 28 retrieval) | `out/eval/rag_eval.jsonl` | `eval_rag.py` |

Topics: Process Management, Threads, CPU Scheduling, Process Synchronization, Deadlocks, Memory
Management, Virtual Memory, File Systems, Disk Scheduling, System Calls, Inter-Process Communication,
Linux Commands, Shell Programming, OS Basics, I/O Systems, Protection and Security, Virtualization.

### Coverage per topic
| Topic | Exam Qs | Viva | MCQs | Numericals | Explanations |
|---|---|---|---|---|---|
| Process Management | 10 | 9 | 5 | 0 | 3 |
| Threads | 9 | 7 | 5 | 0 | 3 |
| CPU Scheduling | 13 | 10 | 67 | 75 | 4 |
| Process Synchronization | 12 | 10 | 7 | 0 | 4 |
| Deadlocks | 11 | 9 | 6 | 40 | 3 |
| Memory Management | 12 | 10 | 7 | 39 | 3 |
| Virtual Memory | 12 | 10 | 47 | 72 | 4 |
| File Systems | 12 | 9 | 6 | 0 | 3 |
| Disk Scheduling | 7 | 6 | 41 | 36 | 2 |
| System Calls | 10 | 10 | 18 | 12 | 2 |
| Inter-Process Communication | 8 | 7 | 5 | 0 | 2 |
| Linux Commands | 10 | 8 | 6 | 0 | 2 |
| Shell Programming | 10 | 7 | 5 | 0 | 2 |
| OS Basics | 12 | 8 | 5 | 0 | 3 |
| I/O Systems | 6 | 5 | 3 | 0 | 2 |
| Protection and Security | 7 | 5 | 3 | 0 | 2 |
| Virtualization | 5 | 3 | 2 | 0 | 2 |

## How each part was made

**Faculty material** (`data/raw/faculty/`, described in `_sources.json`): 36 uploaded files in two batches. In the first batch of 20, 3
were exact duplicates (Segmentation, Paging, Advanced Page Tables were uploaded twice) and one was the
same notes in two formats (dining philosophers .docx and .pdf, detected automatically by text overlap),
leaving 16 indexed. The second batch of 16 added 13 new files (threads-locks, threads-sema and Virtual_memory were already in, and the reader-writer notes came as both .docx and .pdf), so 28 faculty files are indexed in total (30 including the two skipped same-content copies). Old `.ppt` files are converted with LibreOffice; slides whose content is a picture
(code screenshots, diagrams) are read with OCR and marked "[Text read from slide image]", so expect
small OCR errors there. Running headers, slide-number placeholders and template notes are stripped,
and the OSTEP readings keep their numbered section titles (e.g. "28.11 Fetch-And-Add"). Faculty
chunks get a small ranking boost because they define what is taught. The faculty deadlock problem
sheet is solved step by step in `data/notes/21_faculty_problem_solutions.md` (safe sequence
<P2, P0, P1, P3>, checked with the solver).

**Notes, viva, MCQs, question bank, explanations** are written by hand in plain-text source files under
`dataset/src/` (easy to edit; the build script converts them to JSON). They're original summaries in
our own words, organised by the syllabus, not copied from the textbook.

**Numericals are generated, not written.** `solvers.py` implements FCFS, SJF, SRTF, priority (both),
Round Robin, FIFO/LRU/OPT page replacement, all six disk algorithms, Banker's safety and request
algorithms, fork counting, first/best/worst fit, paging address translation and EAT. The solvers are
checked against the textbook's own worked examples (`python dataset/solvers.py`), and `gen_numericals.py`
uses them to make random problems with exact step-by-step solutions (Gantt charts, frame tables, Need
matrices). Conventions are stated inside every solution (tie-breaking, RR queue order, whether C-SCAN
counts the return jump), since textbooks differ on these.

| Numerical type | Count |
|---|---|
| CPU scheduling (6 algorithms) | 60 |
| Scheduling comparison (FCFS vs SJF vs RR) | 15 |
| Page replacement (FIFO / LRU / OPT) | 40 |
| Page replacement comparison | 15 |
| Belady's anomaly check | 8 |
| Disk scheduling (6 algorithms) | 36 |
| Banker's safety | 25 |
| Banker's resource request | 15 |
| Paging bits / address translation | 20 |
| Effective access time (TLB / page fault) | 16 |
| fork() counting | 12 |
| First / best / worst fit | 12 |

**Real past papers.** Six BACSE106 CAT papers (CAT-1 C1, C2 Fall 2026-27; CAT-1 G1, G2 and CAT-2 G1, G2 Winter 2025-26). Two were phone photos and the others had OCR errors and missing table values, so all 34 questions were transcribed by hand into `dataset/src/question_bank.txt` with the paper name as a fifth field. The two papers that include faculty answer keys are also indexed as documents. The numericals without keys are solved step by step in `data/notes/22_past_paper_solutions.md`, computed with the solvers. One finding: the official key for CAT-1 G2 Q4 gives a Round Robin average waiting time of 37.83, but its per-process values don't satisfy waiting = turnaround − burst; the consistent value is 39.83.

**Textbook.** Only the syllabus chapters are indexed (1–15 plus the real-time and Linux chapters, page ranges in `data/raw/textbook/_sources.json`); distributed systems, multimedia, Windows XP, bibliography and index are skipped. Each chunk is labelled from its chapter, and numbered headings such as "6.3 Peterson's Solution" become section names (end-of-chapter exercise sentences are not mistaken for headings). The PDF is copyrighted, so it is not included in the project zip: put your own copy at `data/raw/textbook/Operating_System_Concepts_8th_Edition.pdf`.

**YouTube transcripts.** 50 Gate Smashers lecture transcripts covering the syllabus overview, OS introduction and types, process states, Linux commands, system calls, fork, user/kernel mode, threads, all the scheduling algorithms (including mixed CPU/IO bursts, multilevel queue and MLFQ), process synchronization (race condition, producer-consumer, printer spooler, critical section, semaphores, readers-writers, dining philosophers) deadlocks (necessary conditions, resource allocation graphs, handling methods and prevention, Banker's algorithm, the GATE 2018 questions and the minimum-resources formula R + n > total demand) and memory management (degree of multiprogramming, contiguous vs non-contiguous, fixed and variable partitioning, fragmentation, first/next/best/worst fit). The L-5.1 video gets its CPU-utilization numbers wrong (it quotes 76% and 93% for 1 - 0.7^2 and 1 - 0.7^4; the right values are 51% and 76%), so the corrected calculation was added to `data/notes/07_memory_management.md`. Notes always rank above transcripts, so the tutor gives the right figures. Four videos (L-3.5 lock variable, L-3.6 test-and-set, L-3.7 turn variable, L-3.10 binary semaphore practice) only had Hindi auto-generated subtitles. Those were too garbled to be useful and the English embeddings can't read Devanagari, so they're marked `skip` in `_sources.json`. Their topics are already covered in `data/notes/05_synchronization.md`. Timestamps and channel filler ("subscribe", "press the bell button", "welcome to ...") are removed per subtitle cue, the text is regrouped into ~60-word paragraphs, and each video is tagged with its topic in `data/raw/youtube/_sources.json`. Spoken lectures are less precise than notes (the subtitles have no punctuation and occasionally misspeak), so these chunks rank slightly below notes, faculty material and the textbook. Keep them local; they are the channel's content.

## Fine-tuning set

Chat format (works with TRL `SFTTrainer`, Unsloth, Axolotl, LLaMA-Factory), one JSON per line:
```json
{"messages": [{"role": "system", "content": "You are OSTutor..."},
              {"role": "user", "content": "Explain Round Robin scheduling with an example."},
              {"role": "assistant", "content": "**In short:** every process gets the CPU for..."}],
 "meta": {"kind": "explanation", "topic": "CPU Scheduling", "source_id": "exp-007"}}
```
The same pairs are also in Alpaca format (`train_alpaca.jsonl`: instruction / input / output / system).

| Kind | Rows | What it teaches |
|---|---|---|
| explanation (+ rephrased) | 92 | teacher voice: one-line answer → steps → example → exam tip |
| viva | 90 | short, precise viva answers |
| numerical | 274 | step-by-step solving with correct arithmetic |
| mcq | 90 | pick the option and justify it |
| rag_grounded | 85 | answer **from the retrieved notes** and cite them `[n]` — the exact prompt the app sends |
| mcq_generation / viva_generation | 32 | produce the JSON the Practice tab expects |

The train/val split is by source item, so a question and its rephrased copy are always on the same side.

## Evaluation set

43 viva questions (about a third of each topic) are **held out**: they're not in the fine-tuning data and
their answers are not in the knowledge base, so the tutor can't just look them up. Plus 28 student-style
search queries ("rr time quantum too small", "sstf vs scan") with the expected topic.

Current results (offline mode, TF-IDF embeddings, no LLM, with faculty material indexed):
- Retrieval: topic hit@1 = 0.94, hit@3 = 0.97 over 71 questions
- Faculty-specific questions (`tests/smoke_test.py`): a faculty source in the top 3 for 22/22
- Extractive answers vs gold: token F1 0.17, keyword recall 0.41 (low by design — it's sentence
  extraction, not generation; this is the baseline the LLM should beat)

With the RAG model running, `python dataset/eval_rag.py --llm` adds **LLM + RAG** and **LLM without RAG**
columns, which is the comparison the case study's conclusion asks for.

## Adding your real class material
1. Lecture PPT/PPTX, PDFs, DOCX, lab manuals → `data/raw/faculty/` (or any folder under `data/raw/`),
   and add a line for each file in that folder's `_sources.json` with its topic and a readable source
   name. Files without an entry still work; their topic is detected automatically. Keep copyrighted
   readings (like the OSTEP chapters) local and don't redistribute them.
2. Real previous-year questions → append to `dataset/src/question_bank.txt` (`topic | marks | type | question`).
3. More viva / MCQs / explanations → same format in `dataset/src/`.
4. Run `python dataset/build_dataset.py`, then `python dataset/validate.py`, then restart the app.
A topic name that isn't in `config.TOPICS` stops the build with a clear message.

## Known limitations
- Numericals are 44% of the fine-tuning set. If the fine-tuned model starts answering theory questions
  like a worked problem, sample fewer numerical rows (filter by `meta.kind`).
- 46 teacher-style explanations is enough to show the style but small; more (especially written by
  faculty) would help the most.
- Linux man pages from the original plan aren't included; they can be dropped
  into `data/raw/` as .txt files.
- The model answers in `viva.txt` and `explanations.txt` should be reviewed by a faculty member before
  being used for grading.
