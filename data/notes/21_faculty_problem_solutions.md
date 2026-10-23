---
topic: Deadlocks
source: Solution to faculty problem: Deadlock (RAG + Banker's)
---
# Solved faculty problems

## Deadlock problem: resource allocation graph and safe sequence
Problem (from the faculty sheet): four processes P0–P3 and four resource types R1–R4 with multiple instances. R1 has 2 instances (one held by P0, one by P1). R2 has 3 instances (one each held by P1, P2, P3). R3 is held by P0 with one instance free. R4 has 2 instances (one held by P3, one by P2). Requests: P1 wants 1 R1; P0 wants 1 R2; P3 wants 1 R1 and 2 R2; P0 and P2 each want 1 R3. Draw the resource allocation graph, check for deadlock and give the safe sequence.

Note on the wording: the sheet says R3 has "two instances allocated to P0 and remaining one instance is not allocated". Whether P0 holds 1 or 2 instances of R3, exactly one R3 instance is free, and the answer below is the same either way. The working uses P0 holding 1.

### i) Resource allocation graph
Draw P0–P3 as circles and R1–R4 as boxes with dots for instances (R1: 2, R2: 3, R3: 2 or 3, R4: 2).
- Assignment edges (resource → process): R1 → P0, R1 → P1, R2 → P1, R2 → P2, R2 → P3, R3 → P0, R4 → P2, R4 → P3.
- Request edges (process → resource): P1 → R1, P0 → R2, P3 → R1, P3 → R2 (two instances), P0 → R3, P2 → R3.
The graph has cycles (for example P0 → R2 → P1 → R1 → P0), but resources have several instances, so a cycle alone does not prove deadlock. We run the detection algorithm.

### ii) Matrices (order R1 R2 R3 R4)
| Process | Allocation | Request |
|---|---|---|
| P0 | 1 0 1 0 | 0 1 1 0 |
| P1 | 1 1 0 0 | 1 0 0 0 |
| P2 | 0 1 0 1 | 0 0 1 0 |
| P3 | 0 1 0 1 | 1 2 0 0 |
Available = total − allocated = (2−2, 3−3, 1 free, 2−2) = (0, 0, 1, 0).

### iii) Banker's-style detection
Work = Available = (0, 0, 1, 0). Find a process whose Request ≤ Work, let it finish and add its Allocation to Work.
- P2: Request (0,0,1,0) ≤ (0,0,1,0) ✓ → Work = (0,0,1,0) + (0,1,0,1) = (0,1,1,1)
- P0: Request (0,1,1,0) ≤ (0,1,1,1) ✓ → Work = (0,1,1,1) + (1,0,1,0) = (1,1,2,1)
- P1: Request (1,0,0,0) ≤ (1,1,2,1) ✓ → Work = (1,1,2,1) + (1,1,0,0) = (2,2,2,1)
- P3: Request (1,2,0,0) ≤ (2,2,2,1) ✓ → Work = (2,2,2,1) + (0,1,0,1) = (2,3,2,2)

All processes can finish, so the system is **not deadlocked**. Safe sequence: **<P2, P0, P1, P3>**. P2 is the key: it only needs the one free R3, and once it finishes it frees an R2 and an R4, which unblocks P0.
