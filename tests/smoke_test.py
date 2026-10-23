import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ingest
import llm
from search import OSSearch

EVAL = [
    ("belady anomaly", "Virtual Memory"),
    ("rr time quantum too small", "CPU Scheduling"),
    ("convoy effect", "CPU Scheduling"),
    ("four conditions for deadlock", "Deadlocks"),
    ("bankers algorithm safe sequence", "Deadlocks"),
    ("difference between paging and segmentation", "Memory Management"),
    ("what is a TLB", "Memory Management"),
    ("page fault effective access time", "Virtual Memory"),
    ("what is thrashing", "Virtual Memory"),
    ("producer consumer using semaphores", "Process Synchronization"),
    ("race condition counter++", "Process Synchronization"),
    ("what does fork return in child", "System Calls"),
    ("code after exec never runs", "System Calls"),
    ("zombie process", "Process Management"),
    ("what is in a PCB", "Process Management"),
    ("pthread_create", "Threads"),
    ("one-to-one threading model", "Threads"),
    ("inode direct and indirect pointers", "File Systems"),
    ("linked vs indexed allocation", "File Systems"),
    ("sstf vs scan", "Disk Scheduling"),
    ("pipe read end write end", "Inter-Process Communication"),
    ("shared memory shmget", "Inter-Process Communication"),
    ("chmod 755", "Linux Commands"),
    ("grep -v", "Linux Commands"),
    ("what does $# mean in shell script", "Shell Programming"),
    ("case statement in bash", "Shell Programming"),
    ("kernel mode vs user mode", "OS Basics"),
    ("microkernel vs monolithic", "OS Basics"),
]


FACULTY_EVAL = [
    "why check the condition in a while loop before cond_wait",
    "missed wakeup when lock not held while calling wait",
    "producer consumer with two condition variables",
    "hybrid approach paging and segments",
    "multi-level page table page directory",
    "evaluating locks fairness performance",
    "building a spin lock with test and set",
    "ticket lock fetch and add",
    "semaphores as condition variables",
    "dining philosophers third attempt using mutex",
    "shared memory server client program shmget",
    "atomicity violation and order violation bugs",
    "deadlock problem P0 P1 P2 P3 R1 R2 R3 R4 safe sequence",
    "first fit best fit worst fit memory allocation",
    "limited direct execution trap table",
    "what does the OS do on a timer interrupt context switch",
    "fork exec wait example program output",
    "pthread_create and pthread_join arguments",
    "why do threads need locks shared counter race",
    "covering conditions broadcast",
    "how does OS create a process load program into memory",
    "reader writer problem with semaphore wrmutex",
    "lottery scheduling tickets",
    "multi-level feedback queue rules priority boost",
    "dup system call file descriptor",
    "shell script to check palindrome exercise",
]

BOOK_PAPER_EVAL = [
    ("bakery algorithm", "textbook"),
    ("swap space management", "textbook"),
    ("RAID levels structure", "textbook"),
    ("thrashing working-set model", "textbook"),
    ("hashed page tables", "textbook"),
    ("Linux kernel modules", "textbook"),
    ("ML_Training GPU banker's request", "past_paper"),
    ("chef delivery agent producer consumer", "past_paper"),
    ("if fork and fork how many times hello printed", "youtube"),
    ("how to count context switches in round robin", "youtube"),
    ("suspend ready suspend wait medium term scheduler", "youtube"),
    ("lseek SEEK_CUR SEEK_SET read write head position", "youtube"),
    ("multilevel feedback queue starvation upgrade lower queue", "youtube"),
    ("printer spooler problem in variable race condition", "youtube"),
    ("readers writers semaphore rc mutex db first reader", "youtube"),
    ("dining philosophers deadlock fifth philosopher reverse order", "youtube"),
    ("multi instance resource allocation graph available need deadlock", "youtube"),
    ("deadlock ignorance ostrich method windows linux restart", "youtube"),
    ("gate 2018 three processes four instances largest value of k", "youtube"),
    ("fixed partitioning internal fragmentation limit on process size", "youtube"),
    ("first fit next fit best fit worst fit hole leftover space", "youtube"),
    ("each process uses cpu then shifts to input output device then comes back to cpu completion time", "youtube"),
]


def main():
    ingest.main()
    s = OSSearch()
    print(f"\nembedder={s.embedder.backend} reranker={s.reranker.kind} chunks={s.n}\n")

    top1 = top3 = 0
    for q, want in EVAL:
        res = s.search(q, k=3)["results"]
        got = [r["topic"] for r in res]
        top1 += bool(got) and got[0] == want
        top3 += want in got
        mark = "OK " if got and got[0] == want else ("~3 " if want in got else "XX ")
        print(f"  {mark} {q:<45} -> {got[0] if got else '-':<28} ({res[0]['section'] if res else ''})")
    print(f"\nTop-1 topic accuracy: {top1}/{len(EVAL)} = {top1 / len(EVAL):.0%}")
    print(f"Top-3 topic accuracy: {top3}/{len(EVAL)} = {top3 / len(EVAL):.0%}")

    fac_hits = 0
    print("\nFaculty-material queries (a faculty source in the top 3?):")
    for q in FACULTY_EVAL:
        res = s.search(q, k=3)["results"]
        hit = any(r["doc_type"] == "faculty" or "faculty" in r["source"].lower() for r in res)
        fac_hits += hit
        print(f"  {'OK ' if hit else 'XX '} {q:<55} -> {res[0]['source'] if res else '-'}")
    print(f"Faculty top-3 hit rate: {fac_hits}/{len(FACULTY_EVAL)}")

    bp = 0
    print("\nTextbook / past-paper / YouTube queries:")
    for q, kind in BOOK_PAPER_EVAL:
        res = s.search(q, k=5)["results"]
        hit = any(r["doc_type"] == kind or (kind == "past_paper" and "CAT" in r["text"]) for r in res)
        bp += hit
        print(f"  {'OK ' if hit else 'XX '} {q:<45} -> {res[0]['source'][:50] if res else '-'}")
    print(f"Textbook/past-paper/YouTube top-5 hit rate: {bp}/{len(BOOK_PAPER_EVAL)}")

    print("\n--- Answer ---")
    res = s.search("what is the convoy effect", k=4)["results"]
    text, mode = llm.answer("what is the convoy effect", res)
    print(f"[{mode}]\n{text}")

    notes = [c for c in s.chunks if c["topic"] == "Virtual Memory" and c["doc_type"] != "question_bank"]
    past = [c for c in s.chunks if c["topic"] == "Virtual Memory" and c["doc_type"] == "question_bank"]
    qs, mode = llm.mcqs("Virtual Memory", notes, 3, seed=1)
    print(f"\n--- MCQs [{mode}] ---")
    for q in qs:
        print(f"  {q['question']}\n    options={q['options']} answer={q['options'][q['answer_index']]}")
    assert qs, "MCQ generator returned nothing"
    lookup = lambda q: s.search(q, k=1, doc_type="notes")["results"]
    vq, mode = llm.viva("Virtual Memory", notes, past, 3, lookup=lookup)
    print(f"\n--- Viva [{mode}] ---")
    for q in vq:
        print(f"  Q: {q['question']}\n  A: {q['answer']}")
    pq, mode = llm.practice("Virtual Memory", notes, past, 2)
    print(f"\n--- Practice [{mode}] ---")
    for p in pq:
        print(f"  {p['problem'][:120]}")

    assert top3 / len(EVAL) >= 0.85, "retrieval quality dropped"
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
