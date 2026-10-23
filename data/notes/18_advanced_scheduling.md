---
topic: CPU Scheduling
source: Class notes - Unit 2 (advanced)
---
# Multiprocessor, Real-Time and Linux Scheduling

## Multiprocessor scheduling
In asymmetric multiprocessing one master processor makes all scheduling decisions and the others only run user code. In symmetric multiprocessing (SMP), used by all modern systems, each processor schedules itself, either from a common ready queue or from its own private queue.

Processor affinity: a process that has been running on one CPU has its data in that CPU's cache, so moving it to another CPU means the cache must be refilled. The OS therefore tries to keep a process on the same CPU. Soft affinity is a preference; hard affinity (sched_setaffinity in Linux) forces it.

Load balancing keeps work spread evenly when each CPU has its own queue. Push migration: a kernel task periodically moves processes from overloaded CPUs to idle ones. Pull migration: an idle CPU pulls a waiting task from a busy one. Load balancing works against affinity, so the OS must balance the two.

Multicore and hardware threads: when a core stalls waiting for memory (a memory stall), a chip with hyper-threading can switch to another hardware thread on the same core, so the OS sees each hardware thread as a logical CPU.

## Real-time scheduling
Real-time tasks have deadlines. Hard real-time tasks must always meet them; soft real-time tasks get priority but no guarantee. A real-time scheduler must be preemptive and priority-based. Periodic tasks are described by their processing time t, deadline d and period p (0 ≤ t ≤ d ≤ p).

- Rate Monotonic Scheduling (RMS): static priorities; the shorter the period, the higher the priority. It is optimal among static-priority schemes. A set of n tasks is guaranteed schedulable if total CPU utilization ≤ n(2^(1/n) − 1), which is about 83% for two tasks and approaches 69% for many tasks.
- Earliest Deadline First (EDF): dynamic priorities; the task whose deadline is closest runs first. In theory it can schedule any task set with utilization up to 100%.

Admission control: a real-time scheduler accepts a new task only if it can guarantee its deadline.

## Linux scheduling
For normal tasks Linux used the Completely Fair Scheduler (CFS) from kernel 2.6.23. CFS does not use fixed time slices. Each task has a virtual runtime (vruntime) that increases as it runs, scaled by its nice value: low-priority tasks' vruntime grows faster. The scheduler always picks the task with the smallest vruntime, kept in a red-black tree, so I/O-bound tasks that run briefly naturally get the CPU back quickly. Since kernel 6.6 the default fair scheduler is EEVDF (Earliest Eligible Virtual Deadline First), which keeps the fairness idea but also gives latency-sensitive tasks earlier deadlines.

Linux also has real-time classes SCHED_FIFO and SCHED_RR with priorities 0–99, which always run before normal tasks. Nice values range from −20 (highest priority) to +19 (lowest), and the nice and renice commands change them.

## Thread scheduling
With many-to-one and many-to-many models, the thread library schedules user threads onto kernel threads within the process; this is process-contention scope (PCS). The kernel schedules kernel threads across the whole system; this is system-contention scope (SCS). Linux, being one-to-one, uses only SCS.
