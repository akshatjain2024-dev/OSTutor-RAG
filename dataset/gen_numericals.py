import json
import random
from pathlib import Path

import solvers as S

OUT = Path(__file__).parent / "out"
rng = random.Random(2026)


def fmt_gantt(g):
    s = f"{g[0][1]}"
    for pid, a, b in g:
        s += f" [{pid if pid != 'idle' else 'idle'}] {b}"
    return s


def fmt_procs(procs, with_pr=False):
    head = "| Process | Arrival | Burst |" + (" Priority |" if with_pr else "")
    sep = "|---|---|---|" + ("---|" if with_pr else "")
    rows = [f"| {p['pid']} | {p['at']} | {p['bt']} |" + (f" {p['pr']} |" if with_pr else "") for p in procs]
    return "\n".join([head, sep] + rows)


def fmt_result_table(res):
    lines = ["| Process | AT | BT | CT | TAT = CT-AT | WT = TAT-BT | RT |", "|---|---|---|---|---|---|---|"]
    for pid, r in res["table"].items():
        lines.append(f"| {pid} | {r['at']} | {r['bt']} | {r['ct']} | {r['tat']} | {r['wt']} | {r['rt']} |")
    return "\n".join(lines)


def rand_procs(n, with_pr=False, zero_arrival=False):
    ats = [0] * n if zero_arrival else sorted([0] + [rng.randint(0, 8) for _ in range(n - 1)])
    prs = rng.sample(range(1, n + 3), n)
    return [{"pid": f"P{i+1}", "at": ats[i], "bt": rng.randint(1, 10),
             **({"pr": prs[i]} if with_pr else {})} for i in range(n)]


ALGO_NOTES = {
    "FCFS": "processes run strictly in arrival order and nobody is interrupted.",
    "SJF (non-preemptive)": "whenever the CPU becomes free, pick the arrived process with the smallest burst; it then runs to completion.",
    "SRTF (preemptive SJF)": "at every time unit, run the arrived process with the smallest REMAINING time; a new short process can preempt the running one.",
    "Priority (non-preemptive)": "when the CPU becomes free, pick the arrived process with the highest priority (smaller number = higher priority).",
    "Priority (preemptive)": "at every instant, the highest-priority arrived process runs (smaller number = higher priority); a higher-priority arrival preempts.",
}


def gen_scheduling(i):
    algo = rng.choice(list(S.SCHEDULERS) + ["Round Robin"] * 2)
    n = rng.randint(4, 5)
    with_pr = algo.startswith("Priority")
    procs = rand_procs(n, with_pr, zero_arrival=rng.random() < 0.25)
    if algo == "Round Robin":
        q = rng.randint(2, 4)
        res = S.round_robin(procs, q)
        rule = (f"each process gets at most {q} time units, then goes to the back of the ready queue. "
                "A process arriving at the same moment a quantum ends joins the queue before the preempted one.")
        name = f"Round Robin (time quantum = {q})"
    else:
        res = S.SCHEDULERS[algo](procs)
        rule = ALGO_NOTES[algo]
        name = algo
    question = (f"Consider the following processes:\n\n{fmt_procs(procs, with_pr)}\n\n"
                f"Draw the Gantt chart using {name} scheduling and find the average waiting time "
                f"and average turnaround time.")
    idle = any(g[0] == "idle" for g in res["gantt"])
    solution = "\n".join([
        f"**Rule for {name}:** {rule}" + (" Ties are broken by earlier arrival, then lower process number." if "Round" not in name else ""),
        "",
        "**Gantt chart** (times between the brackets):",
        f"`{fmt_gantt(res['gantt'])}`" + ("  — the CPU is idle when no process has arrived yet." if idle else ""),
        "",
        "**Table:** completion time (CT) comes from the Gantt chart, then TAT = CT − AT, WT = TAT − BT, "
        "RT = first time on CPU − AT.",
        "",
        fmt_result_table(res),
        "",
        f"Average waiting time = {sum(r['wt'] for r in res['table'].values())}/{n} = **{res['avg']['wt']}**",
        f"Average turnaround time = {sum(r['tat'] for r in res['table'].values())}/{n} = **{res['avg']['tat']}**",
        f"Average response time = {res['avg']['rt']}",
    ])
    return {"id": f"num-sched-{i:03d}", "topic": "CPU Scheduling", "subtype": "scheduling",
            "algorithm": name, "question": question, "solution": solution,
            "answer": {"avg_wt": res["avg"]["wt"], "avg_tat": res["avg"]["tat"], "avg_rt": res["avg"]["rt"],
                       "gantt": res["gantt"]},
            "data": {"processes": procs}, "difficulty": "medium" if algo in ("FCFS", "SJF (non-preemptive)") else "hard"}


def gen_sched_compare(i):
    procs = rand_procs(4, zero_arrival=True)
    q = rng.randint(2, 4)
    results = {"FCFS": S.fcfs(procs), "SJF": S.sjf(procs), f"RR (q={q})": S.round_robin(procs, q)}
    best = min(results, key=lambda k: results[k]["avg"]["wt"])
    lines = [f"- **{k}:** Gantt `{fmt_gantt(v['gantt'])}` → average WT = {v['avg']['wt']}, "
             f"average TAT = {v['avg']['tat']}" for k, v in results.items()]
    question = (f"Four processes arrive at time 0 with burst times "
                f"{', '.join(f'{p['pid']} = {p['bt']}' for p in procs)}. Compare FCFS, SJF and Round Robin "
                f"(q = {q}) by average waiting time. Which is best?")
    solution = "\n".join(["All processes arrive at 0, so we only need the order each algorithm runs them in.", ""]
                         + lines + ["", f"**{best}** gives the lowest average waiting time. "
                                    "SJF is provably optimal for average waiting time when all jobs are known in advance; "
                                    "RR trades some waiting time for better response time."])
    return {"id": f"num-schedcmp-{i:03d}", "topic": "CPU Scheduling", "subtype": "scheduling_compare",
            "question": question, "solution": solution,
            "answer": {k: v["avg"]["wt"] for k, v in results.items()} | {"best": best},
            "data": {"processes": procs, "q": q}, "difficulty": "medium"}


def fmt_steps(res, nframes):
    hdr = "| Ref | " + " | ".join(f"F{k+1}" for k in range(nframes)) + " | Result |"
    sep = "|---|" + "---|" * nframes + "---|"
    rows = []
    for s in res["steps"]:
        fr = s["frames"] + ["-"] * (nframes - len(s["frames"]))
        r = "hit" if s["hit"] else ("fault" + (f" (replace {s['victim']})" if s["victim"] is not None else ""))
        rows.append(f"| {s['ref']} | " + " | ".join(str(x) for x in fr) + f" | {r} |")
    return "\n".join([hdr, sep] + rows)


PR_RULE = {
    "FIFO": "replace the page that has been in memory the longest.",
    "LRU": "replace the page that was used least recently (look backwards in the string).",
    "OPT": "replace the page whose next use is farthest in the future (look forwards); a page never used again goes first.",
}


def gen_page(i):
    algo = rng.choice(["FIFO", "LRU", "OPT"])
    n = rng.randint(12, 18)
    pages = rng.randint(5, 7)
    refs = [rng.randint(0, pages - 1) for _ in range(n)]
    nf = rng.choice([3, 3, 4])
    res = S.page_replacement(refs, nf, algo)
    question = (f"For the reference string {', '.join(map(str, refs))} with {nf} frames (initially empty), "
                f"find the number of page faults using {algo} page replacement.")
    solution = "\n".join([
        f"**Rule for {algo}:** {PR_RULE[algo]} The first {nf} distinct pages fill empty frames and each is a fault.",
        "", fmt_steps(res, nf), "",
        f"Total page faults = **{res['faults']}**, hits = {res['hits']}, "
        f"fault rate = {res['faults']}/{n} = {res['fault_rate']}"])
    return {"id": f"num-page-{i:03d}", "topic": "Virtual Memory", "subtype": "page_replacement",
            "algorithm": algo, "question": question, "solution": solution,
            "answer": {"faults": res["faults"], "hits": res["hits"]},
            "data": {"refs": refs, "frames": nf}, "difficulty": "medium"}


def gen_page_compare(i):
    refs = [rng.randint(0, 5) for _ in range(rng.randint(12, 16))]
    nf = 3
    r = {a: S.page_replacement(refs, nf, a)["faults"] for a in ("FIFO", "LRU", "OPT")}
    question = (f"Reference string: {', '.join(map(str, refs))}. With {nf} frames, compare the number of page "
                f"faults for FIFO, LRU and Optimal replacement.")
    solution = (f"Simulating each algorithm frame by frame:\n\n- FIFO: **{r['FIFO']}** faults\n- LRU: **{r['LRU']}** faults\n"
                f"- OPT: **{r['OPT']}** faults\n\nOPT is always the lowest because it uses future knowledge; it can't be "
                f"implemented in practice and is used as a benchmark. LRU is the practical approximation of OPT.")
    return {"id": f"num-pagecmp-{i:03d}", "topic": "Virtual Memory", "subtype": "page_compare",
            "question": question, "solution": solution, "answer": r,
            "data": {"refs": refs, "frames": nf}, "difficulty": "medium"}


def gen_belady(i):
    while True:
        refs = [rng.randint(1, 5) for _ in range(12)]
        f3, f4 = (S.page_replacement(refs, k, "FIFO")["faults"] for k in (3, 4))
        want = i % 2 == 0
        if (f4 > f3) == want:
            break
    question = (f"Using FIFO on the reference string {', '.join(map(str, refs))}, find the page faults with 3 frames "
                f"and with 4 frames. Does this string show Belady's anomaly?")
    yes = f4 > f3
    solution = (f"FIFO with 3 frames gives **{f3}** faults and with 4 frames gives **{f4}** faults. "
                + ("Adding a frame INCREASED the faults, so **yes, this is Belady's anomaly**. It happens with FIFO "
                   "because the set of pages kept with 3 frames is not always a subset of the set kept with 4 frames."
                   if yes else
                   "More frames did not increase the faults, so **this string does not show Belady's anomaly**. "
                   "(The anomaly is possible with FIFO but only for particular strings; LRU and OPT never show it.)"))
    return {"id": f"num-belady-{i:03d}", "topic": "Virtual Memory", "subtype": "belady",
            "question": question, "solution": solution,
            "answer": {"faults_3": f3, "faults_4": f4, "anomaly": yes},
            "data": {"refs": refs}, "difficulty": "hard"}


DISK_RULE = {
    "FCFS": "serve requests in the order given.",
    "SSTF": "always go to the pending request closest to the current head position.",
    "SCAN": "move in the given direction serving requests until the END of the disk, then reverse.",
    "LOOK": "like SCAN, but only go as far as the last request in each direction, then reverse.",
    "C-SCAN": "move in the given direction to the end of the disk, jump to the other end, and continue in the same direction (the jump is counted).",
    "C-LOOK": "go up to the last request in the direction, jump to the farthest request at the other side, continue the same direction (the jump is counted).",
}


def gen_disk(i):
    algo = rng.choice(list(DISK_RULE))
    size = 200
    reqs = rng.sample(range(0, size), rng.randint(6, 9))
    head = rng.randint(20, 180)
    direction = rng.choice(["up", "down"])
    res = S.disk(reqs, head, algo, direction, size)
    dir_text = "towards higher cylinder numbers" if direction == "up" else "towards cylinder 0"
    steps = " → ".join(map(str, res["path"]))
    moves = " + ".join(f"|{b}−{a}|" for a, b in zip(res["path"], res["path"][1:]))
    question = (f"A disk has {size} cylinders (0–{size-1}). The request queue is {', '.join(map(str, reqs))} and the "
                f"head is at {head}" + (f", moving {dir_text}" if algo not in ("FCFS", "SSTF") else "")
                + f". Find the total head movement using {algo}.")
    solution = "\n".join([f"**Rule for {algo}:** {DISK_RULE[algo]}", "",
                          f"Head path: {steps}", "", f"Total head movement = {moves} = **{res['total']} cylinders**"])
    return {"id": f"num-disk-{i:03d}", "topic": "Disk Scheduling", "subtype": "disk_scheduling",
            "algorithm": algo, "question": question, "solution": solution,
            "answer": {"total": res["total"], "order": res["service_order"]},
            "data": {"requests": reqs, "head": head, "direction": direction, "size": size}, "difficulty": "medium"}


def fmt_matrix(name, rows, labels):
    return "\n".join([f"| {name} | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
                     + [f"| P{i} | " + " | ".join(map(str, r)) + " |" for i, r in enumerate(rows)])


def rand_bank(want_safe):
    while True:
        n, m = rng.randint(4, 5), 3
        maxm = [[rng.randint(1, 9) for _ in range(m)] for _ in range(n)]
        alloc = [[rng.randint(0, x) for x in row] for row in maxm]
        avail = [rng.randint(0, 4) for _ in range(m)]
        r = S.bankers(avail, maxm, alloc)
        if r["safe"] == want_safe and (want_safe or len(r["sequence"]) >= 1):
            return n, maxm, alloc, avail, r


def gen_bankers(i):
    n, maxm, alloc, avail, r = rand_bank(want_safe=rng.random() < 0.7)
    L = ["A", "B", "C"]
    question = ("Using the Banker's algorithm, determine whether the system is in a safe state. "
                "If it is, give a safe sequence.\n\n" + fmt_matrix("Allocation", alloc, L) + "\n\n"
                + fmt_matrix("Max", maxm, L) + f"\n\nAvailable = ({', '.join(map(str, avail))})")
    steps = [f"- P{t['p']}: Need {tuple(t['need'])} ≤ Work {tuple(t['work_before'])} ✓ → it finishes, "
             f"Work = {tuple(t['work_before'])} + Alloc {tuple(alloc[t['p']])} = {tuple(t['work_after'])}"
             for t in r["trace"]]
    stuck = [f"P{k}" for k in range(n) if k not in r["sequence"]]
    solution = "\n".join(
        ["**Step 1: Need = Max − Allocation**", "", fmt_matrix("Need", r["need"], L), "",
         f"**Step 2: Safety algorithm.** Start with Work = Available = {tuple(avail)}. Scan P0, P1, ... "
         "repeatedly; any process whose Need ≤ Work can finish and release its allocation.", ""] + steps + [""]
        + ([f"All processes finish, so the system is **SAFE**. Safe sequence: "
            f"**<{', '.join(f'P{k}' for k in r['sequence'])}>** (other safe sequences may also exist)."]
           if r["safe"] else
           [f"No remaining process ({', '.join(stuck)}) has Need ≤ Work = {tuple(r['trace'][-1]['work_after']) if r['trace'] else tuple(avail)}, "
            "so the system is **NOT SAFE** (unsafe state — a deadlock may occur)."]))
    return {"id": f"num-bank-{i:03d}", "topic": "Deadlocks", "subtype": "bankers_safety",
            "question": question, "solution": solution,
            "answer": {"safe": r["safe"], "sequence": [f"P{k}" for k in r["sequence"]] if r["safe"] else None,
                       "need": r["need"]},
            "data": {"allocation": alloc, "max": maxm, "available": avail}, "difficulty": "hard"}


def gen_bank_request(i):
    n, maxm, alloc, avail, r = rand_bank(True)
    pid = rng.randrange(n)
    need = r["need"][pid]
    req = [rng.randint(0, max(0, min(need[j], avail[j] + 1))) for j in range(3)]
    if not any(req):
        req[rng.randrange(3)] = 1
    res = S.bankers_request(avail, maxm, alloc, pid, req)
    L = ["A", "B", "C"]
    question = (f"For the system below, process P{pid} requests ({', '.join(map(str, req))}). "
                f"Can the request be granted immediately?\n\n" + fmt_matrix("Allocation", alloc, L) + "\n\n"
                + fmt_matrix("Max", maxm, L) + f"\n\nAvailable = ({', '.join(map(str, avail))})")
    lines = [f"Need of P{pid} = Max − Allocation = {tuple(need)}.",
             f"1. Request ≤ Need? {tuple(req)} ≤ {tuple(need)} → {'yes' if all(req[j] <= need[j] for j in range(3)) else 'NO'}"]
    if all(req[j] <= need[j] for j in range(3)):
        lines.append(f"2. Request ≤ Available? {tuple(req)} ≤ {tuple(avail)} → "
                     f"{'yes' if all(req[j] <= avail[j] for j in range(3)) else 'NO'}")
    if "after" in res:
        a = res["after"]
        lines += [f"3. Pretend to allocate: Available becomes {tuple(res['avail_after'])}, then run the safety algorithm.",
                  ("   Safe sequence found: <" + ", ".join(f"P{k}" for k in a["sequence"]) + ">")
                  if a["safe"] else "   No safe sequence exists."]
    lines.append(f"\n**{'Grant' if res['granted'] else 'Do not grant'} the request** — {res['reason']}.")
    return {"id": f"num-bankreq-{i:03d}", "topic": "Deadlocks", "subtype": "bankers_request",
            "question": question, "solution": "\n".join(lines),
            "answer": {"granted": res["granted"], "reason": res["reason"]},
            "data": {"allocation": alloc, "max": maxm, "available": avail, "pid": pid, "request": req},
            "difficulty": "hard"}


def gen_paging(i):
    page_kb = rng.choice([1, 2, 4, 8])
    page = page_kb * 1024
    off_bits = page.bit_length() - 1
    la_bits = rng.choice([16, 20, 24, 32])
    pn_bits = la_bits - off_bits
    kind = rng.choice(["bits", "translate"])
    if kind == "bits":
        question = (f"A system uses a {la_bits}-bit logical address and a page size of {page_kb} KB. "
                    "How many bits are used for the page number and the offset, and how many entries can the page table have?")
        solution = (f"Page size = {page_kb} KB = {page} bytes = 2^{off_bits}, so the **offset needs {off_bits} bits**.\n"
                    f"Page number bits = {la_bits} − {off_bits} = **{pn_bits} bits**, so the page table can have "
                    f"2^{pn_bits} = **{2 ** pn_bits:,} entries**.")
        ans = {"offset_bits": off_bits, "page_bits": pn_bits, "entries": 2 ** pn_bits}
    else:
        la_bits = 16
        pn_bits = la_bits - off_bits
        npages = 2 ** pn_bits
        p = rng.randrange(0, min(npages, 8))
        d = rng.randrange(0, page)
        addr = p * page + d
        frames = rng.sample(range(0, 32), min(npages, 8))
        table = {k: frames[k] for k in range(min(npages, 8))}
        phys = table[p] * page + d
        question = (f"Page size is {page} bytes. The page table is {table} (page → frame). "
                    f"Translate the logical address {addr} to a physical address.")
        solution = (f"Page number p = {addr} ÷ {page} = **{p}**, offset d = {addr} mod {page} = **{d}**.\n"
                    f"Page {p} is in frame {table[p]}, so physical address = frame × page size + offset = "
                    f"{table[p]} × {page} + {d} = **{phys}**.")
        ans = {"page": p, "offset": d, "physical": phys}
    return {"id": f"num-paging-{i:03d}", "topic": "Memory Management", "subtype": f"paging_{kind}",
            "question": question, "solution": solution, "answer": ans, "difficulty": "easy"}


def gen_eat(i):
    if rng.random() < 0.5:
        t_mem = rng.choice([50, 80, 100, 120])
        t_tlb = rng.choice([5, 10, 20])
        h = rng.choice([0.8, 0.85, 0.9, 0.95, 0.98])
        hit_t, miss_t = t_tlb + t_mem, t_tlb + 2 * t_mem
        eat = round(h * hit_t + (1 - h) * miss_t, 2)
        question = (f"Memory access takes {t_mem} ns and a TLB lookup takes {t_tlb} ns. With a TLB hit ratio of "
                    f"{int(h * 100)}%, what is the effective memory access time?")
        solution = (f"On a hit: TLB + one memory access = {t_tlb} + {t_mem} = {hit_t} ns.\n"
                    f"On a miss: TLB + page table access + the actual access = {t_tlb} + 2×{t_mem} = {miss_t} ns.\n"
                    f"EAT = {h} × {hit_t} + {round(1 - h, 2)} × {miss_t} = **{eat} ns**.")
        return {"id": f"num-eat-{i:03d}", "topic": "Memory Management", "subtype": "eat_tlb",
                "question": question, "solution": solution, "answer": {"eat_ns": eat}, "difficulty": "easy"}
    t_mem = rng.choice([100, 200])
    t_pf_ms = rng.choice([4, 8, 10])
    p_inv = rng.choice([1000, 5000, 10000, 100000])
    p = 1 / p_inv
    eat = round((1 - p) * t_mem + p * t_pf_ms * 1_000_000, 1)
    question = (f"Memory access time is {t_mem} ns and servicing a page fault takes {t_pf_ms} ms. If one access "
                f"in {p_inv:,} causes a page fault, what is the effective access time?")
    solution = (f"Convert units: {t_pf_ms} ms = {t_pf_ms * 1_000_000:,} ns, and p = 1/{p_inv:,}.\n"
                f"EAT = (1 − p) × {t_mem} + p × {t_pf_ms * 1_000_000:,} = **{eat:,} ns**, which is about "
                f"{round(eat / t_mem, 1)}× slower than memory alone. Even a tiny fault rate hurts a lot.")
    return {"id": f"num-eat-{i:03d}", "topic": "Virtual Memory", "subtype": "eat_page_fault",
            "question": question, "solution": solution, "answer": {"eat_ns": eat}, "difficulty": "medium"}


def gen_fork(i):
    n = rng.randint(2, 5)
    inside = rng.random() < 0.5
    r = S.fork_loop(n, inside)
    code = (f"for (int i = 0; i < {n}; i++) {{\n    fork();\n    printf(\"hi\\n\");\n}}" if inside else
            f"for (int i = 0; i < {n}; i++)\n    fork();\nprintf(\"hi\\n\");")
    question = f"How many times is \"hi\" printed, and how many processes exist in total?\n\n```c\n{code}\n```"
    if inside:
        terms = " + ".join(str(2 ** k) for k in range(1, n + 1))
        solution = (f"Each fork() doubles the number of processes: after iteration k there are 2^k processes, "
                    f"and every one of them prints once in that iteration.\nPrints = {terms} = **{r['prints']}** "
                    f"(formula 2^(n+1) − 2). Total processes = 2^{n} = **{r['processes']}** "
                    f"({r['children_created']} children + the original).")
    else:
        solution = (f"{n} forks run in sequence and every process continues the loop, so the count doubles "
                    f"{n} times: 2^{n} = **{r['processes']} processes** ({r['children_created']} newly created). "
                    f"The printf is after the loop, so each process prints once: **{r['prints']} times**.")
    return {"id": f"num-fork-{i:03d}", "topic": "System Calls", "subtype": "fork_count",
            "question": question, "solution": solution, "answer": r, "difficulty": "easy" if not inside else "medium"}


def fit_verdict(placed, res):
    top = max(placed.values())
    winners = [a for a, v in placed.items() if v == top]
    if len(winners) == 1:
        return f"**{winners[0]}** places the most processes ({top} of 4) here, so it uses memory best for this input."
    big = {a: max(res[a]["holes_after"]) for a in winners}
    keep = max(big, key=big.get)
    names = ", ".join(winners[:-1]) + " and " + winners[-1]
    return (f"{names} each place {top} of 4 processes. Among them, **{keep}** leaves the largest "
            f"free hole ({big[keep]} KB) for a future large process, so it uses memory best here.")


def gen_fit(i):
    while True:
        holes = [rng.choice(range(100, 700, 50)) for _ in range(5)]
        sizes = [rng.choice(range(80, 420, 10)) for _ in range(4)]
        res = {a: S.fit(holes, sizes, a) for a in ("First fit", "Best fit", "Worst fit")}
        if len({tuple(r["placed_in"]) for r in res.values()}) == 3:
            break
    hole_names = [f"H{k+1}({h} KB)" for k, h in enumerate(holes)]
    question = (f"Memory holes (in order): {', '.join(hole_names)}. Processes of size "
                f"{', '.join(f'{s} KB' for s in sizes)} arrive in that order. Show the placement using first fit, "
                f"best fit and worst fit. Which uses memory best?")
    lines = []
    for a, r in res.items():
        pl = [f"{s} KB → " + (f"H{p+1}" if p is not None else "**must wait**") for s, p in zip(sizes, r["placed_in"])]
        lines.append(f"- **{a}:** " + "; ".join(pl) + f". Holes left: {r['holes_after']}")
    placed = {a: sum(p is not None for p in r["placed_in"]) for a, r in res.items()}
    best = max(placed, key=placed.get)
    solution = "\n".join(["First fit takes the first hole big enough, best fit the smallest hole big enough, "
                          "worst fit the largest hole. A hole shrinks after each placement.", ""] + lines + [
        "", fit_verdict(placed, res)])
    return {"id": f"num-fit-{i:03d}", "topic": "Memory Management", "subtype": "memory_fit",
            "question": question, "solution": solution,
            "answer": {a: r["placed_in"] for a, r in res.items()}, "data": {"holes": holes, "sizes": sizes},
            "difficulty": "medium"}


PLAN = [(gen_scheduling, 60), (gen_sched_compare, 15), (gen_page, 40), (gen_page_compare, 15), (gen_belady, 8),
        (gen_disk, 36), (gen_bankers, 25), (gen_bank_request, 15), (gen_paging, 20), (gen_eat, 16),
        (gen_fork, 12), (gen_fit, 12)]


def to_mcq(item):
    st, a = item["subtype"], item["answer"]
    if st == "scheduling":
        correct, unit, q = a["avg_wt"], "", f"{item['question'].split('Draw the Gantt')[0]}Using {item['algorithm']}, what is the average waiting time?"
    elif st == "page_replacement":
        correct, unit, q = a["faults"], "", item["question"]
    elif st == "disk_scheduling":
        correct, unit, q = a["total"], " cylinders", item["question"]
    elif st == "fork_count":
        correct, unit, q = a["prints"], "", item["question"].replace(", and how many processes exist in total", "")
    else:
        return None
    pool = {correct}
    while len(pool) < 4:
        delta = rng.choice([-3, -2, -1, 1, 2, 3]) * (1 if isinstance(correct, int) else rng.choice([0.25, 0.5, 1]))
        cand = round(correct + delta, 2) if not isinstance(correct, int) else correct + int(delta)
        if cand >= 0:
            pool.add(cand)
    opts = sorted(pool)
    return {"id": item["id"].replace("num-", "nmcq-"), "topic": item["topic"], "question": q,
            "options": [f"{o}{unit}" for o in opts], "answer_index": opts.index(correct),
            "explanation": item["solution"], "source": "generated-numerical"}


def main():
    OUT.mkdir(exist_ok=True)
    items = []
    for fn, count in PLAN:
        items += [fn(i) for i in range(1, count + 1)]
    with open(OUT / "numericals.jsonl", "w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    mcqs = [m for m in (to_mcq(it) for it in items) if m]
    with open(OUT / "numerical_mcqs.jsonl", "w") as f:
        for m in mcqs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"numericals: {len(items)}  numerical MCQs: {len(mcqs)}")
    return items


if __name__ == "__main__":
    main()
