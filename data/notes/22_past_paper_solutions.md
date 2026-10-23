---
topic: auto
source: Solutions to past CAT numericals (solver-verified)
---
# Solved past-paper numericals (BACSE106 CAT papers)

All numbers below were computed with the project's scheduling, Banker's and allocation solvers. Conventions: ties go to the earlier arrival, then the lower process number; in Round Robin a process arriving when a quantum ends joins the queue before the preempted one.

## SRTF with seven processes (CPU Scheduling) - CAT-1 Fall 2026-27 C2, Q4
Arrival / burst: P1 0/5, P2 1/3, P3 2/2, P4 3/3, P5 4/1, P6 5/1, P7 6/1. The policy (always run the process with the least remaining time, preempt if a shorter one arrives) is Shortest Remaining Time First, the preemptive form of SJF. Advantage: it gives the minimum average waiting time, so short urgent requests finish quickly.
Gantt chart: 0 [P1] 1 [P2] 4 [P5] 5 [P6] 6 [P7] 7 [P3] 9 [P4] 12 [P1] 16.
Completion times: P1 16, P2 4, P3 9, P4 12, P5 5, P6 6, P7 7.
Turnaround: 16, 3, 7, 9, 1, 1, 1 → average 38/7 = 5.43. Waiting: 11, 0, 5, 6, 0, 0, 0 → average 22/7 = 3.14.
Note: at time 4 P2 finishes, and P5 (burst 1) beats P3 (remaining 2), so P3 waits until the one-unit jobs P5, P6, P7 are done.

## Priority, SJF and Round Robin with six processes (CPU Scheduling) - CAT-1 Winter 2025-26 G1, Q4
Priority / burst / arrival: P1 5/13/6, P2 10/15/10, P3 30/40/15, P4 3/12/12, P5 2/4/0, P6 6/4/5. Lower value = higher priority. The CPU is idle from 4 to 5 because P6 arrives at 5.
i) Preemptive priority: 0 [P5] 4 [idle] 5 [P6] 6 [P1] 12 [P4] 24 [P1] 31 [P6] 34 [P2] 49 [P3] 89. P1 (priority 5) preempts P6 (6) at 6, and P4 (3) preempts P1 at 12.
Completion: P1 31, P2 49, P3 89, P4 24, P5 4, P6 34. Turnaround: 25, 39, 74, 12, 4, 29 → average 30.5. Waiting: 12, 24, 34, 0, 0, 25 → average 15.83.
ii) Non-preemptive SJF: 0 [P5] 4 [idle] 5 [P6] 9 [P1] 22 [P4] 34 [P2] 49 [P3] 89.
Turnaround: 16, 39, 74, 22, 4, 4 → average 26.5. Waiting: 3, 24, 34, 10, 0, 0 → average 11.83.
iii) Round Robin, q = 10: 0 [P5] 4 [idle] 5 [P6] 9 [P1] 19 [P2] 29 [P4] 39 [P3] 49 [P1] 52 [P2] 57 [P4] 59 [P3] 89.
Turnaround: 46, 47, 74, 47, 4, 4 → average 37.0. Waiting: 33, 32, 34, 35, 0, 0 → average 22.33.
SJF gives the lowest average waiting time, as expected.

## SRTF and Round Robin with 80% CPU bursts (CPU Scheduling) - CAT-1 Winter 2025-26 G2, Q4
CPU bursts = 80% of total time, rounded: 20→16, 18→14 (14.4), 15→12, 10→8, 6→5 (4.8), 12→10 (9.6). Arrivals 0, 1, 2, 4, 5, 6.
SRTF: 0 [P1] 1 [P2] 2 [P3] 4 [P4] 5 [P5] 10 [P4] 17 [P3] 27 [P6] 37 [P2] 50 [P1] 65.
Turnaround: 65, 49, 25, 13, 5, 31 → average 31.33. Waiting: 49, 35, 13, 5, 0, 21 → average 20.5. Response: 0, 0, 0, 0, 0, 21 → average 3.5.
Round Robin q = 5: 0 [P1] 5 [P2] 10 [P3] 15 [P4] 20 [P5] 25 [P1] 30 [P6] 35 [P2] 40 [P3] 45 [P4] 48 [P1] 53 [P6] 58 [P2] 62 [P3] 64 [P1] 65.
Turnaround: 65, 61, 62, 44, 20, 52 → average 50.67. Waiting = turnaround − burst: 49, 47, 50, 36, 15, 42 → average 239/6 = 39.83. Response: 0, 4, 8, 11, 15, 24 → average 10.33.
Check against the official answer key: SRTF and the RR turnaround and response times match, but the key lists RR waiting times 49, 48, 52, 10, 20, 48 (average 37.83). Those don't satisfy waiting = turnaround − burst (for example P4: 44 − 8 = 36, not 10), so 39.83 is the consistent value.

## Deadlock detection with six resource types (Deadlocks) - CAT-2 Winter 2025-26 G2, Q1
Allocation (R1..R6): P1 (1,0,0,0,1,0), P2 (1,0,0,1,0,0), P3 (0,0,0,0,0,1), P4 (0,1,0,1,0,0), P5 (0,0,1,0,0,1). Request: P1 (0,0,0,1,0,0), P2 (0,1,0,0,0,0), P3 (0,0,0,1,0,0), P4 (0,0,0,0,0,1), P5 none. Totals (2,1,2,2,1,2).
Available = totals − allocated = (2−2, 1−1, 2−1, 2−2, 1−1, 2−2) = (0, 0, 1, 0, 0, 0).
Here the Request matrix plays the role of Need. Work = (0,0,1,0,0,0):
- P1, P2, P3, P4 cannot proceed at first (each needs a resource with 0 available). P5 requests nothing → finishes: Work = (0,0,2,0,0,1).
- P4 requests R6 = 1 ≤ 1 → finishes: Work = (0,1,2,1,0,1).
- P1 requests R4 = 1 ≤ 1 → finishes: Work = (1,1,2,1,1,1).
- P2 requests R2 = 1 ≤ 1 → finishes: Work = (2,1,2,2,1,1).
- P3 requests R4 = 1 ≤ 2 → finishes: Work = (2,1,2,2,1,2).
No deadlock; safe sequence **<P5, P4, P1, P2, P3>**. In the RAG, assignment edges go from each held resource instance to its process, and request edges from P1→R4, P2→R2, P3→R4, P4→R6.

## Fixed partitions: first, best and worst fit (Memory Management) - CAT-2 Winter 2025-26 G2, Q4
Partitions 120, 350, 600, 200, 450, 700, 180, 500, 320, 260 KB; processes 115, 420, 180, 610, 90, 300, 275, 510, 140, 350 KB. Each partition holds one process (fixed partitioning).
- First fit: 115→120, 420→600, 180→350, 610→700, 90→200, 300→450, 275→500, 510→none, 140→180, 350→none. Unallocated partitions: 320 and 260 (too small for 510 and 350). Processes waiting: 510 KB and 350 KB. Internal fragmentation 970 KB.
- Best fit: 115→120, 420→450, 180→180, 610→700, 90→200, 300→320, 275→350, 510→600, 140→260, 350→500. Every process is placed and no partition is left; internal fragmentation 690 KB.
- Worst fit: 115→700, 420→600, 180→500, 610→none, 90→450, 300→350, 275→320, 510→none, 140→260, 350→none. Unallocated partitions 120, 200, 180 (all too small); 610, 510 and 350 KB must wait. Internal fragmentation 1660 KB.
Best fit works best here because it saves the big partitions for the big processes.

## TLB timing and segmentation (Memory Management) - CAT-2 Winter 2025-26 G2, Q5
i) Batch 1: 120 accesses at 70% hits = 84 hits × 6 + 36 misses × 36 = 504 + 1296 = 1800 ms. Batch 2: 80 accesses at 85% = 68 × 6 + 12 × 36 = 408 + 432 = 840 ms. Overall time = 2640 ms over 200 accesses, so the average access time is 13.2 ms.
ii) A valid address needs offset < length; physical = base + offset.
- (A, 199): 199 < 200 → valid, physical 300.
- (C, 100): 100 < 300 → valid, physical 1100.
- (D, 260): 260 ≥ 250 → invalid (trap: segmentation fault).
- (E, 120): 120 < 150 → valid, physical 2020.
Memory map: A 100–299, B 400–899, C 1000–1299, D 1500–1749, E 1900–2049.

## fork() inside a loop with printf (System Calls) - CAT-1 Fall 2026-27 C1, Q2(ii)
for (i = 0; i < 2; i++) { if (fork()) printf("P "); else printf("C "); }
Each fork() returns the child's PID (non-zero) in the parent, so the parent prints "P ", and 0 in the child, which prints "C ". Two iterations create 4 processes in total.
The trick: "P " and "C " have no newline, so the text stays in each process's stdio buffer. At the second fork the child gets a copy of the parent's unflushed buffer. Each of the 4 final processes therefore prints its whole path when it exits: "P P ", "P C ", "C P ", "C C ". The output is 8 tokens (four P and four C), and the order of the four pairs can vary between runs. If the output had a newline, or the buffer were flushed with fflush(stdout), only 6 tokens would appear (2 from the first iteration plus 4 from the second).
Process tree: the original process (P path) forks child A; in iteration 2 both the original and A fork again, giving 4 leaves.
