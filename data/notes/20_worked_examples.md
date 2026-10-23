---
topic: auto
source: Worked examples (solver-verified)
---
# Worked examples

## Worked example: FCFS (CPU Scheduling)

Question: Consider the following processes:

| Process | Arrival | Burst |
|---|---|---|
| P1 | 0 | 8 |
| P2 | 1 | 4 |
| P3 | 3 | 1 |
| P4 | 8 | 10 |
| P5 | 8 | 2 |

Draw the Gantt chart using FCFS scheduling and find the average waiting time and average turnaround time.

Solution: **Rule for FCFS:** processes run strictly in arrival order and nobody is interrupted. Ties are broken by earlier arrival, then lower process number.

**Gantt chart** (times between the brackets):
`0 [P1] 8 [P2] 12 [P3] 13 [P4] 23 [P5] 25`

**Table:** completion time (CT) comes from the Gantt chart, then TAT = CT − AT, WT = TAT − BT, RT = first time on CPU − AT.

| Process | AT | BT | CT | TAT = CT-AT | WT = TAT-BT | RT |
|---|---|---|---|---|---|---|
| P1 | 0 | 8 | 8 | 8 | 0 | 0 |
| P2 | 1 | 4 | 12 | 11 | 7 | 7 |
| P3 | 3 | 1 | 13 | 10 | 9 | 9 |
| P4 | 8 | 10 | 23 | 15 | 5 | 5 |
| P5 | 8 | 2 | 25 | 17 | 15 | 15 |

Average waiting time = 36/5 = **7.2**
Average turnaround time = 61/5 = **12.2**
Average response time = 7.2

## Worked example: FCFS (CPU Scheduling)

Question: Consider the following processes:

| Process | Arrival | Burst |
|---|---|---|
| P1 | 0 | 7 |
| P2 | 0 | 9 |
| P3 | 5 | 2 |
| P4 | 7 | 6 |
| P5 | 7 | 2 |

Draw the Gantt chart using FCFS scheduling and find the average waiting time and average turnaround time.

Solution: **Rule for FCFS:** processes run strictly in arrival order and nobody is interrupted. Ties are broken by earlier arrival, then lower process number.

**Gantt chart** (times between the brackets):
`0 [P1] 7 [P2] 16 [P3] 18 [P4] 24 [P5] 26`

**Table:** completion time (CT) comes from the Gantt chart, then TAT = CT − AT, WT = TAT − BT, RT = first time on CPU − AT.

| Process | AT | BT | CT | TAT = CT-AT | WT = TAT-BT | RT |
|---|---|---|---|---|---|---|
| P1 | 0 | 7 | 7 | 7 | 0 | 0 |
| P2 | 0 | 9 | 16 | 16 | 7 | 7 |
| P3 | 5 | 2 | 18 | 13 | 11 | 11 |
| P4 | 7 | 6 | 24 | 17 | 11 | 11 |
| P5 | 7 | 2 | 26 | 19 | 17 | 17 |

Average waiting time = 46/5 = **9.2**
Average turnaround time = 72/5 = **14.4**
Average response time = 9.2

## Worked example: scheduling compare (CPU Scheduling)

Question: Four processes arrive at time 0 with burst times P1 = 5, P2 = 4, P3 = 9, P4 = 6. Compare FCFS, SJF and Round Robin (q = 3) by average waiting time. Which is best?

Solution: All processes arrive at 0, so we only need the order each algorithm runs them in.

- **FCFS:** Gantt `0 [P1] 5 [P2] 9 [P3] 18 [P4] 24` → average WT = 8.0, average TAT = 14.0
- **SJF:** Gantt `0 [P2] 4 [P1] 9 [P4] 15 [P3] 24` → average WT = 7.0, average TAT = 13.0
- **RR (q=3):** Gantt `0 [P1] 3 [P2] 6 [P3] 9 [P4] 12 [P1] 14 [P2] 15 [P3] 18 [P4] 21 [P3] 24` → average WT = 12.5, average TAT = 18.5

**SJF** gives the lowest average waiting time. SJF is provably optimal for average waiting time when all jobs are known in advance; RR trades some waiting time for better response time.

## Worked example: scheduling compare (CPU Scheduling)

Question: Four processes arrive at time 0 with burst times P1 = 10, P2 = 9, P3 = 3, P4 = 9. Compare FCFS, SJF and Round Robin (q = 2) by average waiting time. Which is best?

Solution: All processes arrive at 0, so we only need the order each algorithm runs them in.

- **FCFS:** Gantt `0 [P1] 10 [P2] 19 [P3] 22 [P4] 31` → average WT = 12.75, average TAT = 20.5
- **SJF:** Gantt `0 [P3] 3 [P2] 12 [P4] 21 [P1] 31` → average WT = 9.0, average TAT = 16.75
- **RR (q=2):** Gantt `0 [P1] 2 [P2] 4 [P3] 6 [P4] 8 [P1] 10 [P2] 12 [P3] 13 [P4] 15 [P1] 17 [P2] 19 [P4] 21 [P1] 23 [P2] 25 [P4] 27 [P1] 29 [P2] 30 [P4] 31` → average WT = 18.0, average TAT = 25.75

**SJF** gives the lowest average waiting time. SJF is provably optimal for average waiting time when all jobs are known in advance; RR trades some waiting time for better response time.

## Worked example: OPT (Virtual Memory)

Question: For the reference string 4, 0, 2, 1, 0, 3, 1, 2, 4, 4, 4, 1, 2, 4 with 3 frames (initially empty), find the number of page faults using OPT page replacement.

Solution: **Rule for OPT:** replace the page whose next use is farthest in the future (look forwards); a page never used again goes first. The first 3 distinct pages fill empty frames and each is a fault.

| Ref | F1 | F2 | F3 | Result |
|---|---|---|---|---|
| 4 | 4 | - | - | fault |
| 0 | 4 | 0 | - | fault |
| 2 | 4 | 0 | 2 | fault |
| 1 | 1 | 0 | 2 | fault (replace 4) |
| 0 | 1 | 0 | 2 | hit |
| 3 | 1 | 3 | 2 | fault (replace 0) |
| 1 | 1 | 3 | 2 | hit |
| 2 | 1 | 3 | 2 | hit |
| 4 | 1 | 4 | 2 | fault (replace 3) |
| 4 | 1 | 4 | 2 | hit |
| 4 | 1 | 4 | 2 | hit |
| 1 | 1 | 4 | 2 | hit |
| 2 | 1 | 4 | 2 | hit |
| 4 | 1 | 4 | 2 | hit |

Total page faults = **6**, hits = 8, fault rate = 6/14 = 0.429

## Worked example: FIFO (Virtual Memory)

Question: For the reference string 1, 5, 3, 4, 0, 1, 5, 3, 6, 1, 4, 4, 5, 3 with 3 frames (initially empty), find the number of page faults using FIFO page replacement.

Solution: **Rule for FIFO:** replace the page that has been in memory the longest. The first 3 distinct pages fill empty frames and each is a fault.

| Ref | F1 | F2 | F3 | Result |
|---|---|---|---|---|
| 1 | 1 | - | - | fault |
| 5 | 1 | 5 | - | fault |
| 3 | 1 | 5 | 3 | fault |
| 4 | 4 | 5 | 3 | fault (replace 1) |
| 0 | 4 | 0 | 3 | fault (replace 5) |
| 1 | 4 | 0 | 1 | fault (replace 3) |
| 5 | 5 | 0 | 1 | fault (replace 4) |
| 3 | 5 | 3 | 1 | fault (replace 0) |
| 6 | 5 | 3 | 6 | fault (replace 1) |
| 1 | 1 | 3 | 6 | fault (replace 5) |
| 4 | 1 | 4 | 6 | fault (replace 3) |
| 4 | 1 | 4 | 6 | hit |
| 5 | 1 | 4 | 5 | fault (replace 6) |
| 3 | 3 | 4 | 5 | fault (replace 1) |

Total page faults = **13**, hits = 1, fault rate = 13/14 = 0.929

## Worked example: page compare (Virtual Memory)

Question: Reference string: 5, 4, 0, 0, 0, 0, 5, 0, 5, 2, 5, 1. With 3 frames, compare the number of page faults for FIFO, LRU and Optimal replacement.

Solution: Simulating each algorithm frame by frame:

- FIFO: **6** faults
- LRU: **5** faults
- OPT: **5** faults

OPT is always the lowest because it uses future knowledge; it can't be implemented in practice and is used as a benchmark. LRU is the practical approximation of OPT.

## Worked example: page compare (Virtual Memory)

Question: Reference string: 0, 3, 0, 0, 4, 0, 3, 0, 1, 4, 1, 3. With 3 frames, compare the number of page faults for FIFO, LRU and Optimal replacement.

Solution: Simulating each algorithm frame by frame:

- FIFO: **4** faults
- LRU: **6** faults
- OPT: **4** faults

OPT is always the lowest because it uses future knowledge; it can't be implemented in practice and is used as a benchmark. LRU is the practical approximation of OPT.

## Worked example: belady (Virtual Memory)

Question: Using FIFO on the reference string 5, 1, 1, 2, 2, 2, 3, 2, 4, 5, 3, 4, find the page faults with 3 frames and with 4 frames. Does this string show Belady's anomaly?

Solution: FIFO with 3 frames gives **6** faults and with 4 frames gives **6** faults. More frames did not increase the faults, so **this string does not show Belady's anomaly**. (The anomaly is possible with FIFO but only for particular strings; LRU and OPT never show it.)

## Worked example: belady (Virtual Memory)

Question: Using FIFO on the reference string 5, 1, 3, 2, 5, 1, 4, 5, 1, 3, 2, 4, find the page faults with 3 frames and with 4 frames. Does this string show Belady's anomaly?

Solution: FIFO with 3 frames gives **9** faults and with 4 frames gives **10** faults. Adding a frame INCREASED the faults, so **yes, this is Belady's anomaly**. It happens with FIFO because the set of pages kept with 3 frames is not always a subset of the set kept with 4 frames.

## Worked example: C-SCAN (Disk Scheduling)

Question: A disk has 200 cylinders (0–199). The request queue is 66, 11, 135, 138, 98, 126, 14 and the head is at 116, moving towards cylinder 0. Find the total head movement using C-SCAN.

Solution: **Rule for C-SCAN:** move in the given direction to the end of the disk, jump to the other end, and continue in the same direction (the jump is counted).

Head path: 116 → 98 → 66 → 14 → 11 → 0 → 199 → 138 → 135 → 126

Total head movement = |98−116| + |66−98| + |14−66| + |11−14| + |0−11| + |199−0| + |138−199| + |135−138| + |126−135| = **388 cylinders**

## Worked example: C-LOOK (Disk Scheduling)

Question: A disk has 200 cylinders (0–199). The request queue is 187, 8, 182, 185, 35, 124 and the head is at 128, moving towards higher cylinder numbers. Find the total head movement using C-LOOK.

Solution: **Rule for C-LOOK:** go up to the last request in the direction, jump to the farthest request at the other side, continue the same direction (the jump is counted).

Head path: 128 → 182 → 185 → 187 → 8 → 35 → 124

Total head movement = |182−128| + |185−182| + |187−185| + |8−187| + |35−8| + |124−35| = **354 cylinders**

## Worked example: bankers safety (Deadlocks)

Question: Using the Banker's algorithm, determine whether the system is in a safe state. If it is, give a safe sequence.

| Allocation | A | B | C |
|---|---|---|---|
| P0 | 2 | 4 | 2 |
| P1 | 2 | 0 | 1 |
| P2 | 3 | 1 | 0 |
| P3 | 2 | 1 | 6 |

| Max | A | B | C |
|---|---|---|---|
| P0 | 8 | 4 | 5 |
| P1 | 2 | 1 | 6 |
| P2 | 3 | 1 | 1 |
| P3 | 8 | 2 | 8 |

Available = (4, 3, 4)

Solution: **Step 1: Need = Max − Allocation**

| Need | A | B | C |
|---|---|---|---|
| P0 | 6 | 0 | 3 |
| P1 | 0 | 1 | 5 |
| P2 | 0 | 0 | 1 |
| P3 | 6 | 1 | 2 |

**Step 2: Safety algorithm.** Start with Work = Available = (4, 3, 4). Scan P0, P1, ... repeatedly; any process whose Need ≤ Work can finish and release its allocation.

- P2: Need (0, 0, 1) ≤ Work (4, 3, 4) ✓ → it finishes, Work = (4, 3, 4) + Alloc (3, 1, 0) = (7, 4, 4)
- P3: Need (6, 1, 2) ≤ Work (7, 4, 4) ✓ → it finishes, Work = (7, 4, 4) + Alloc (2, 1, 6) = (9, 5, 10)
- P0: Need (6, 0, 3) ≤ Work (9, 5, 10) ✓ → it finishes, Work = (9, 5, 10) + Alloc (2, 4, 2) = (11, 9, 12)
- P1: Need (0, 1, 5) ≤ Work (11, 9, 12) ✓ → it finishes, Work = (11, 9, 12) + Alloc (2, 0, 1) = (13, 9, 13)

All processes finish, so the system is **SAFE**. Safe sequence: **<P2, P3, P0, P1>** (other safe sequences may also exist).

## Worked example: bankers safety (Deadlocks)

Question: Using the Banker's algorithm, determine whether the system is in a safe state. If it is, give a safe sequence.

| Allocation | A | B | C |
|---|---|---|---|
| P0 | 1 | 2 | 2 |
| P1 | 1 | 0 | 1 |
| P2 | 5 | 0 | 4 |
| P3 | 6 | 1 | 1 |

| Max | A | B | C |
|---|---|---|---|
| P0 | 6 | 4 | 3 |
| P1 | 1 | 1 | 1 |
| P2 | 6 | 7 | 5 |
| P3 | 8 | 1 | 1 |

Available = (4, 1, 0)

Solution: **Step 1: Need = Max − Allocation**

| Need | A | B | C |
|---|---|---|---|
| P0 | 5 | 2 | 1 |
| P1 | 0 | 1 | 0 |
| P2 | 1 | 7 | 1 |
| P3 | 2 | 0 | 0 |

**Step 2: Safety algorithm.** Start with Work = Available = (4, 1, 0). Scan P0, P1, ... repeatedly; any process whose Need ≤ Work can finish and release its allocation.

- P1: Need (0, 1, 0) ≤ Work (4, 1, 0) ✓ → it finishes, Work = (4, 1, 0) + Alloc (1, 0, 1) = (5, 1, 1)
- P3: Need (2, 0, 0) ≤ Work (5, 1, 1) ✓ → it finishes, Work = (5, 1, 1) + Alloc (6, 1, 1) = (11, 2, 2)
- P0: Need (5, 2, 1) ≤ Work (11, 2, 2) ✓ → it finishes, Work = (11, 2, 2) + Alloc (1, 2, 2) = (12, 4, 4)

No remaining process (P2) has Need ≤ Work = (12, 4, 4), so the system is **NOT SAFE** (unsafe state — a deadlock may occur).

## Worked example: bankers request (Deadlocks)

Question: For the system below, process P2 requests (0, 1, 2). Can the request be granted immediately?

| Allocation | A | B | C |
|---|---|---|---|
| P0 | 2 | 7 | 3 |
| P1 | 1 | 0 | 7 |
| P2 | 4 | 3 | 3 |
| P3 | 8 | 1 | 1 |

| Max | A | B | C |
|---|---|---|---|
| P0 | 2 | 7 | 4 |
| P1 | 3 | 2 | 8 |
| P2 | 4 | 6 | 7 |
| P3 | 8 | 6 | 8 |

Available = (1, 4, 3)

Solution: Need of P2 = Max − Allocation = (0, 3, 4).
1. Request ≤ Need? (0, 1, 2) ≤ (0, 3, 4) → yes
2. Request ≤ Available? (0, 1, 2) ≤ (1, 4, 3) → yes
3. Pretend to allocate: Available becomes (1, 3, 1), then run the safety algorithm.
   Safe sequence found: <P0, P1, P2, P3>

**Grant the request** — the new state is safe.

## Worked example: bankers request (Deadlocks)

Question: For the system below, process P0 requests (3, 0, 0). Can the request be granted immediately?

| Allocation | A | B | C |
|---|---|---|---|
| P0 | 2 | 0 | 1 |
| P1 | 1 | 5 | 3 |
| P2 | 3 | 1 | 6 |
| P3 | 1 | 7 | 4 |

| Max | A | B | C |
|---|---|---|---|
| P0 | 7 | 4 | 1 |
| P1 | 8 | 8 | 4 |
| P2 | 3 | 5 | 9 |
| P3 | 3 | 7 | 4 |

Available = (2, 1, 3)

Solution: Need of P0 = Max − Allocation = (5, 4, 0).
1. Request ≤ Need? (3, 0, 0) ≤ (5, 4, 0) → yes
2. Request ≤ Available? (3, 0, 0) ≤ (2, 1, 3) → NO

**Do not grant the request** — not enough resources available, so the process must wait.

## Worked example: paging bits (Memory Management)

Question: A system uses a 16-bit logical address and a page size of 4 KB. How many bits are used for the page number and the offset, and how many entries can the page table have?

Solution: Page size = 4 KB = 4096 bytes = 2^12, so the **offset needs 12 bits**.
Page number bits = 16 − 12 = **4 bits**, so the page table can have 2^4 = **16 entries**.

## Worked example: paging translate (Memory Management)

Question: Page size is 8192 bytes. The page table is {0: 3, 1: 4, 2: 17, 3: 21, 4: 25, 5: 24, 6: 30, 7: 18} (page → frame). Translate the logical address 2364 to a physical address.

Solution: Page number p = 2364 ÷ 8192 = **0**, offset d = 2364 mod 8192 = **2364**.
Page 0 is in frame 3, so physical address = frame × page size + offset = 3 × 8192 + 2364 = **26940**.

## Worked example: paging bits (Memory Management)

Question: A system uses a 20-bit logical address and a page size of 4 KB. How many bits are used for the page number and the offset, and how many entries can the page table have?

Solution: Page size = 4 KB = 4096 bytes = 2^12, so the **offset needs 12 bits**.
Page number bits = 20 − 12 = **8 bits**, so the page table can have 2^8 = **256 entries**.

## Worked example: paging translate (Memory Management)

Question: Page size is 1024 bytes. The page table is {0: 16, 1: 23, 2: 19, 3: 18, 4: 10, 5: 15, 6: 5, 7: 20} (page → frame). Translate the logical address 4255 to a physical address.

Solution: Page number p = 4255 ÷ 1024 = **4**, offset d = 4255 mod 1024 = **159**.
Page 4 is in frame 10, so physical address = frame × page size + offset = 10 × 1024 + 159 = **10399**.

## Worked example: eat page fault (Virtual Memory)

Question: Memory access time is 200 ns and servicing a page fault takes 10 ms. If one access in 10,000 causes a page fault, what is the effective access time?

Solution: Convert units: 10 ms = 10,000,000 ns, and p = 1/10,000.
EAT = (1 − p) × 200 + p × 10,000,000 = **1,200.0 ns**, which is about 6.0× slower than memory alone. Even a tiny fault rate hurts a lot.

## Worked example: eat tlb (Memory Management)

Question: Memory access takes 80 ns and a TLB lookup takes 20 ns. With a TLB hit ratio of 80%, what is the effective memory access time?

Solution: On a hit: TLB + one memory access = 20 + 80 = 100 ns.
On a miss: TLB + page table access + the actual access = 20 + 2×80 = 180 ns.
EAT = 0.8 × 100 + 0.2 × 180 = **116.0 ns**.

## Worked example: eat page fault (Virtual Memory)

Question: Memory access time is 200 ns and servicing a page fault takes 10 ms. If one access in 100,000 causes a page fault, what is the effective access time?

Solution: Convert units: 10 ms = 10,000,000 ns, and p = 1/100,000.
EAT = (1 − p) × 200 + p × 10,000,000 = **300.0 ns**, which is about 1.5× slower than memory alone. Even a tiny fault rate hurts a lot.

## Worked example: eat tlb (Memory Management)

Question: Memory access takes 80 ns and a TLB lookup takes 5 ns. With a TLB hit ratio of 98%, what is the effective memory access time?

Solution: On a hit: TLB + one memory access = 5 + 80 = 85 ns.
On a miss: TLB + page table access + the actual access = 5 + 2×80 = 165 ns.
EAT = 0.98 × 85 + 0.02 × 165 = **86.6 ns**.

## Worked example: fork count (System Calls)

Question: How many times is "hi" printed, and how many processes exist in total?

```c
for (int i = 0; i < 5; i++)
    fork();
printf("hi\n");
```

Solution: 5 forks run in sequence and every process continues the loop, so the count doubles 5 times: 2^5 = **32 processes** (31 newly created). The printf is after the loop, so each process prints once: **32 times**.

## Worked example: fork count (System Calls)

Question: How many times is "hi" printed, and how many processes exist in total?

```c
for (int i = 0; i < 2; i++) {
    fork();
    printf("hi\n");
}
```

Solution: Each fork() doubles the number of processes: after iteration k there are 2^k processes, and every one of them prints once in that iteration.
Prints = 2 + 4 = **6** (formula 2^(n+1) − 2). Total processes = 2^2 = **4** (3 children + the original).

## Worked example: memory fit (Memory Management)

Question: Memory holes (in order): H1(350 KB), H2(650 KB), H3(600 KB), H4(650 KB), H5(600 KB). Processes of size 410 KB, 290 KB, 300 KB, 340 KB arrive in that order. Show the placement using first fit, best fit and worst fit. Which uses memory best?

Solution: First fit takes the first hole big enough, best fit the smallest hole big enough, worst fit the largest hole. A hole shrinks after each placement.

- **First fit:** 410 KB → H2; 290 KB → H1; 300 KB → H3; 340 KB → H4. Holes left: [60, 240, 300, 310, 600]
- **Best fit:** 410 KB → H3; 290 KB → H1; 300 KB → H5; 340 KB → H2. Holes left: [60, 310, 190, 650, 300]
- **Worst fit:** 410 KB → H2; 290 KB → H4; 300 KB → H3; 340 KB → H5. Holes left: [350, 240, 300, 360, 260]

First fit, Best fit and Worst fit each place 4 of 4 processes. Among them, **Best fit** leaves the largest free hole (650 KB) for a future large process, so it uses memory best here.

## Worked example: memory fit (Memory Management)

Question: Memory holes (in order): H1(550 KB), H2(500 KB), H3(450 KB), H4(200 KB), H5(450 KB). Processes of size 320 KB, 240 KB, 180 KB, 200 KB arrive in that order. Show the placement using first fit, best fit and worst fit. Which uses memory best?

Solution: First fit takes the first hole big enough, best fit the smallest hole big enough, worst fit the largest hole. A hole shrinks after each placement.

- **First fit:** 320 KB → H1; 240 KB → H2; 180 KB → H1; 200 KB → H2. Holes left: [50, 60, 450, 200, 450]
- **Best fit:** 320 KB → H3; 240 KB → H5; 180 KB → H4; 200 KB → H5. Holes left: [550, 500, 130, 20, 10]
- **Worst fit:** 320 KB → H1; 240 KB → H2; 180 KB → H3; 200 KB → H5. Holes left: [230, 260, 270, 200, 250]

First fit, Best fit and Worst fit each place 4 of 4 processes. Among them, **Best fit** leaves the largest free hole (550 KB) for a future large process, so it uses memory best here.
