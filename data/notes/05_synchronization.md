---
topic: Process Synchronization
source: Class notes - Unit 3
---
# Process Synchronization

When cooperating processes or threads share data, the final result can depend on the exact order in which they run. This situation is called a race condition. For example, if two threads both run count++ at the same time, one update can be lost, because count++ is really three steps: load, add, store.

## Critical section problem
The critical section is the part of code where shared data is accessed. A correct solution must satisfy three requirements:
- Mutual exclusion: only one process can be in its critical section at a time.
- Progress: if no one is in the critical section, the choice of who enters next cannot be postponed forever.
- Bounded waiting: there is a limit on how many times others can enter before a waiting process gets its turn.

## Peterson's solution
Peterson's solution works for two processes using two shared variables: an integer turn and a boolean array flag[2]. A process sets its own flag to true, gives the turn to the other process, and then waits while the other's flag is true and it is the other's turn. It satisfies all three requirements, but may fail on modern hardware because of instruction reordering.

## Hardware support
Atomic instructions like test_and_set() and compare_and_swap() read and modify a memory word in one uninterruptible step, which can be used to build locks.

## Mutex locks
A mutex lock protects a critical section with acquire() and release(). If the lock is busy, the caller waits. A spinlock is a mutex that busy-waits in a loop; it wastes CPU but avoids a context switch, so it is useful when locks are held for a very short time on multicore systems.

## Semaphores
A semaphore S is an integer accessed only through two atomic operations: wait() (also called P or down), which decrements S and blocks if it becomes negative, and signal() (also called V or up), which increments S and wakes a waiting process. A binary semaphore takes only 0 or 1 and works like a mutex. A counting semaphore can take any non-negative value and is used to control access to a resource with several instances.

## Classic problems
- Bounded buffer (producer-consumer): uses semaphores mutex = 1, empty = n and full = 0.
- Readers-writers: many readers can read together, but a writer needs exclusive access.
- Dining philosophers: five philosophers share five chopsticks; a naive solution can deadlock if all pick up their left chopstick at once.

## Monitors
A monitor is a high-level construct where only one process can be active inside at a time. Condition variables with wait() and signal() let processes wait for specific conditions inside the monitor.

## Busy waiting and blocking semaphores
A simple spinning implementation of wait() keeps looping while the semaphore is not positive; this busy waiting wastes CPU time. A blocking implementation gives each semaphore a list of waiting processes: wait() puts the caller on the list and blocks it (sending it to the waiting state), and signal() removes one process from the list and wakes it up (moves it to ready). With this implementation the semaphore value can become negative, and its magnitude is the number of waiting processes.

## Priority inversion
A high-priority process H needs a lock held by a low-priority process L. A medium-priority process M, which does not need the lock, preempts L, so L cannot finish and release the lock, and H effectively waits for M. This is priority inversion (it famously caused resets on the Mars Pathfinder lander). The fix is priority inheritance: while L holds a lock that H wants, L temporarily inherits H's priority, so M cannot preempt it.
