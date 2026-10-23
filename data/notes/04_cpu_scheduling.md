---
topic: CPU Scheduling
source: Class notes - Unit 2
---
# CPU Scheduling

CPU scheduling decides which process in the ready queue gets the CPU next. Processes alternate between CPU bursts and I/O bursts, and the scheduler tries to keep the CPU busy while being fair to everyone.

## Preemptive vs non-preemptive
In non-preemptive scheduling, once a process gets the CPU it keeps it until it finishes or blocks for I/O. In preemptive scheduling the OS can take the CPU away, for example when a time slice ends or a higher priority process arrives. The dispatcher is the module that actually hands the CPU over; the time it takes is called dispatch latency.

## Scheduling criteria
- CPU utilization: keep the CPU as busy as possible.
- Throughput: number of processes completed per unit time.
- Turnaround time: completion time minus arrival time.
- Waiting time: turnaround time minus burst time; total time spent in the ready queue.
- Response time: time from submission until the first response is produced.

## Algorithms
**First Come First Served (FCFS):** processes run in arrival order. Simple and non-preemptive, but suffers from the convoy effect, where short processes wait behind one long process.

**Shortest Job First (SJF):** the process with the smallest next CPU burst runs first. It gives the minimum average waiting time for a given set of processes, but burst lengths must be predicted, usually with exponential averaging. The preemptive version is Shortest Remaining Time First (SRTF).

**Priority scheduling:** the process with the highest priority runs first. Its main problem is starvation (indefinite blocking) of low priority processes. The fix is aging, which slowly increases the priority of processes that have waited a long time.

**Round Robin (RR):** each process gets a fixed time quantum, then goes to the back of the ready queue. It is designed for time-sharing and gives good response time. If the quantum is very large RR behaves like FCFS; if it is very small, context switch overhead dominates. A common rule is that about 80 percent of CPU bursts should be shorter than the quantum.

**Multilevel queue:** the ready queue is split into separate queues (for example foreground and background), each with its own algorithm. **Multilevel feedback queue:** processes can move between queues based on their behaviour, so CPU-heavy processes sink to lower priority queues and interactive ones stay high.

## Worked example (FCFS)
Processes P1, P2, P3 arrive at time 0 with burst times 24, 3 and 3. With FCFS order P1, P2, P3 the waiting times are 0, 24 and 27, so the average waiting time is 17. If the order were P2, P3, P1 the waiting times would be 6, 0 and 3, giving an average of only 3. This shows the convoy effect and why SJF helps.

## Predicting the next CPU burst (exponential averaging)
τ(n+1) = α·t(n) + (1 − α)·τ(n), where t(n) is the length of the most recent burst, τ(n) the previous prediction and 0 ≤ α ≤ 1. With α = 0 recent history is ignored; with α = 1 only the last burst counts; α = 1/2 is common. Example: τ(0) = 10, α = 0.5 and the actual burst is 6, so the next prediction is 0.5 × 6 + 0.5 × 10 = 8.
