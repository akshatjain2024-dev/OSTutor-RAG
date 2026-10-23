from collections import deque


def _finish(procs, gantt):
    res = {}
    for p in procs:
        pid = p["pid"]
        segs = [g for g in gantt if g[0] == pid]
        ct = max(e for _, _, e in segs)
        first = min(s for _, s, _ in segs)
        tat = ct - p["at"]
        res[pid] = {"at": p["at"], "bt": p["bt"], "pr": p.get("pr"), "ct": ct,
                    "tat": tat, "wt": tat - p["bt"], "rt": first - p["at"]}
    n = len(procs)
    avg = {k: round(sum(r[k] for r in res.values()) / n, 2) for k in ("tat", "wt", "rt")}
    return {"gantt": _merge(gantt), "table": res, "avg": avg}


def _merge(gantt):
    out = []
    for pid, s, e in gantt:
        if out and out[-1][0] == pid and out[-1][2] == s:
            out[-1] = (pid, out[-1][1], e)
        else:
            out.append((pid, s, e))
    return out


def _order_key(p):
    return (p["at"], int(p["pid"][1:]))


def fcfs(procs):
    t, gantt = 0, []
    for p in sorted(procs, key=_order_key):
        if t < p["at"]:
            gantt.append(("idle", t, p["at"]))
            t = p["at"]
        gantt.append((p["pid"], t, t + p["bt"]))
        t += p["bt"]
    return _finish(procs, [g for g in gantt if g[0] != "idle"]) | {"gantt": _merge(gantt)}


def _nonpreemptive(procs, key):
    t, done, gantt = 0, set(), []
    while len(done) < len(procs):
        ready = [p for p in procs if p["at"] <= t and p["pid"] not in done]
        if not ready:
            nxt = min(p["at"] for p in procs if p["pid"] not in done)
            gantt.append(("idle", t, nxt))
            t = nxt
            continue
        p = min(ready, key=lambda p: (key(p),) + _order_key(p))
        gantt.append((p["pid"], t, t + p["bt"]))
        t += p["bt"]
        done.add(p["pid"])
    return _finish(procs, [g for g in gantt if g[0] != "idle"]) | {"gantt": _merge(gantt)}


def _preemptive(procs, key):
    rem = {p["pid"]: p["bt"] for p in procs}
    t, gantt = 0, []
    while any(rem.values()):
        ready = [p for p in procs if p["at"] <= t and rem[p["pid"]] > 0]
        if not ready:
            nxt = min(p["at"] for p in procs if rem[p["pid"]] > 0)
            gantt.append(("idle", t, nxt))
            t = nxt
            continue
        p = min(ready, key=lambda p: (key(p, rem),) + _order_key(p))
        gantt.append((p["pid"], t, t + 1))
        rem[p["pid"]] -= 1
        t += 1
    real = [g for g in gantt if g[0] != "idle"]
    return _finish(procs, real) | {"gantt": _merge(gantt)}


def sjf(procs):
    return _nonpreemptive(procs, lambda p: p["bt"])


def srtf(procs):
    return _preemptive(procs, lambda p, rem: rem[p["pid"]])


def priority_np(procs):
    return _nonpreemptive(procs, lambda p: p["pr"])


def priority_p(procs):
    return _preemptive(procs, lambda p, rem: p["pr"])


def round_robin(procs, q):
    procs_s = sorted(procs, key=_order_key)
    rem = {p["pid"]: p["bt"] for p in procs}
    t, i, queue, gantt = 0, 0, deque(), []

    def admit(upto):
        nonlocal i
        while i < len(procs_s) and procs_s[i]["at"] <= upto:
            queue.append(procs_s[i]["pid"])
            i += 1

    admit(0)
    while queue or i < len(procs_s):
        if not queue:
            gantt.append(("idle", t, procs_s[i]["at"]))
            t = procs_s[i]["at"]
            admit(t)
            continue
        pid = queue.popleft()
        run = min(q, rem[pid])
        gantt.append((pid, t, t + run))
        t += run
        rem[pid] -= run
        admit(t)
        if rem[pid] > 0:
            queue.append(pid)
    real = [g for g in gantt if g[0] != "idle"]
    return _finish(procs, real) | {"gantt": _merge(gantt)}


SCHEDULERS = {
    "FCFS": fcfs, "SJF (non-preemptive)": sjf, "SRTF (preemptive SJF)": srtf,
    "Priority (non-preemptive)": priority_np, "Priority (preemptive)": priority_p,
}


def page_replacement(refs, nframes, algo):
    frames, steps, faults = [], [], 0
    last_used, loaded = {}, {}
    for t, page in enumerate(refs):
        hit = page in frames
        victim = None
        if not hit:
            faults += 1
            if len(frames) < nframes:
                frames.append(page)
            else:
                if algo == "FIFO":
                    victim = min(frames, key=lambda f: loaded[f])
                elif algo == "LRU":
                    victim = min(frames, key=lambda f: last_used[f])
                elif algo == "OPT":
                    def next_use(f):
                        try:
                            return refs.index(f, t + 1)
                        except ValueError:
                            return float("inf")
                    victim = max(frames, key=lambda f: (next_use(f), -loaded[f]))
                else:
                    raise ValueError(algo)
                frames[frames.index(victim)] = page
            loaded[page] = t
        last_used[page] = t
        steps.append({"ref": page, "frames": list(frames), "hit": hit, "victim": victim})
    return {"faults": faults, "hits": len(refs) - faults, "steps": steps,
            "fault_rate": round(faults / len(refs), 3)}


def disk(requests, head, algo, direction="up", size=200):
    reqs, order, pos = list(requests), [], head
    if algo == "FCFS":
        order = reqs
    elif algo == "SSTF":
        left = reqs[:]
        while left:
            nxt = min(left, key=lambda r: (abs(r - pos), r))
            order.append(nxt)
            left.remove(nxt)
            pos = nxt
    else:
        lower = sorted([r for r in reqs if r < head], reverse=True)
        upper = sorted([r for r in reqs if r >= head])
        if algo == "SCAN":
            order = (upper + ([size - 1] if lower else []) + lower) if direction == "up" \
                else (lower + ([0] if upper else []) + upper)
        elif algo == "LOOK":
            order = upper + lower if direction == "up" else lower + upper
        elif algo == "C-SCAN":
            order = (upper + ([size - 1, 0] if lower else []) + sorted(lower)) if direction == "up" \
                else (lower + ([0, size - 1] if upper else []) + sorted(upper, reverse=True))
        elif algo == "C-LOOK":
            order = upper + sorted(lower) if direction == "up" else lower + sorted(upper, reverse=True)
        else:
            raise ValueError(algo)
    total, pos, path = 0, head, [head]
    for r in order:
        total += abs(r - pos)
        pos = r
        path.append(r)
    served = [p for p in path[1:] if p in requests]
    return {"path": path, "total": total, "service_order": served}


def bankers(avail, maxm, alloc):
    n, m = len(maxm), len(avail)
    need = [[maxm[i][j] - alloc[i][j] for j in range(m)] for i in range(n)]
    work, finish, seq, trace = list(avail), [False] * n, [], []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                before = list(work)
                work = [work[j] + alloc[i][j] for j in range(m)]
                finish[i] = True
                seq.append(i)
                trace.append({"p": i, "need": need[i], "work_before": before, "work_after": list(work)})
                progress = True
    return {"need": need, "safe": all(finish), "sequence": seq, "trace": trace}


def bankers_request(avail, maxm, alloc, pid, req):
    need = [maxm[pid][j] - alloc[pid][j] for j in range(len(avail))]
    if any(req[j] > need[j] for j in range(len(avail))):
        return {"granted": False, "reason": "request exceeds the process's remaining need (error)"}
    if any(req[j] > avail[j] for j in range(len(avail))):
        return {"granted": False, "reason": "not enough resources available, so the process must wait"}
    a2 = [avail[j] - req[j] for j in range(len(avail))]
    al2 = [row[:] for row in alloc]
    al2[pid] = [alloc[pid][j] + req[j] for j in range(len(avail))]
    r = bankers(a2, maxm, al2)
    return {"granted": r["safe"], "reason": "the new state is safe" if r["safe"] else
            "the new state would be unsafe", "after": r, "avail_after": a2}


def fork_loop(n, print_inside=False):
    procs, prints = 1, 0
    for _ in range(n):
        procs *= 2
        if print_inside:
            prints += procs
    if not print_inside:
        prints = procs
    return {"processes": procs, "children_created": procs - 1, "prints": prints}


def fit(holes, sizes, algo):
    holes = list(holes)
    out = []
    for s in sizes:
        cands = [(i, h) for i, h in enumerate(holes) if h >= s]
        if not cands:
            out.append(None)
            continue
        if algo == "First fit":
            i, h = cands[0]
        elif algo == "Best fit":
            i, h = min(cands, key=lambda x: (x[1], x[0]))
        else:
            i, h = max(cands, key=lambda x: (x[1], -x[0]))
        out.append(i)
        holes[i] -= s
    return {"placed_in": out, "holes_after": holes}


if __name__ == "__main__":
    P = lambda *bts: [{"pid": f"P{i+1}", "at": 0, "bt": b} for i, b in enumerate(bts)]
    assert fcfs(P(24, 3, 3))["avg"]["wt"] == 17.0
    assert sjf(P(6, 8, 7, 3))["avg"]["wt"] == 7.0
    assert round_robin(P(24, 3, 3), 4)["avg"]["wt"] == 5.67
    srt = [{"pid": "P1", "at": 0, "bt": 8}, {"pid": "P2", "at": 1, "bt": 4},
           {"pid": "P3", "at": 2, "bt": 9}, {"pid": "P4", "at": 3, "bt": 5}]
    assert srtf(srt)["avg"]["wt"] == 6.5
    pr = [{"pid": f"P{i+1}", "at": 0, "bt": b, "pr": p}
          for i, (b, p) in enumerate([(10, 3), (1, 1), (2, 4), (1, 5), (5, 2)])]
    assert priority_np(pr)["avg"]["wt"] == 8.2
    ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    assert page_replacement(ref, 3, "FIFO")["faults"] == 15
    assert page_replacement(ref, 3, "LRU")["faults"] == 12
    assert page_replacement(ref, 3, "OPT")["faults"] == 9
    belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    assert page_replacement(belady, 3, "FIFO")["faults"] == 9
    assert page_replacement(belady, 4, "FIFO")["faults"] == 10
    q = [98, 183, 37, 122, 14, 124, 65, 67]
    assert disk(q, 53, "FCFS")["total"] == 640
    assert disk(q, 53, "SSTF")["total"] == 236
    assert disk(q, 53, "SCAN", "down")["total"] == 236
    b = bankers([3, 3, 2], [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
                [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]])
    assert b["safe"] and b["sequence"][0] == 1
    assert bankers_request([3, 3, 2], [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
                           [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]], 1, [1, 0, 2])["granted"]
    assert fork_loop(3)["processes"] == 8 and fork_loop(2, True)["prints"] == 6
    assert fit([100, 500, 200, 300, 600], [212, 417, 112, 426], "First fit")["placed_in"] == [1, 4, 1, None]
    assert fit([100, 500, 200, 300, 600], [212, 417, 112, 426], "Best fit")["placed_in"] == [3, 1, 2, 4]
    print("All solver self-tests match textbook answers.")
