---
topic: Deadlocks
source: Class notes - Unit 3
---
# Deadlocks

A deadlock is a situation where a set of processes are all waiting for each other, and none of them can ever continue. For example, P1 holds a printer and waits for a scanner, while P2 holds the scanner and waits for the printer.

## Four necessary conditions (Coffman conditions)
A deadlock can happen only if all four hold at the same time:
1. Mutual exclusion: at least one resource is non-shareable.
2. Hold and wait: a process holds at least one resource while waiting for more.
3. No preemption: a resource cannot be forcibly taken away; it is released only voluntarily.
4. Circular wait: there is a cycle P0 waits for P1, P1 waits for P2, ..., Pn waits for P0.

## Resource allocation graph
Processes are drawn as circles and resource types as rectangles with dots for instances. A request edge goes from a process to a resource; an assignment edge goes from a resource to a process. If the graph has no cycle there is no deadlock. If there is a cycle and every resource has a single instance, there is a deadlock. With multiple instances a cycle means a deadlock is possible but not certain.

## Handling deadlocks
- Prevention: make sure at least one of the four conditions can never hold, for example by imposing a total ordering of resources so circular wait is impossible.
- Avoidance: the OS uses extra information about future requests to decide whether granting a request keeps the system in a safe state.
- Detection and recovery: let deadlocks happen, detect them periodically, then recover by terminating processes or preempting resources.
- Ignoring the problem: most general-purpose systems, including Linux and Windows, do this (the ostrich algorithm).

## Safe state and Banker's algorithm
A state is safe if there is some order (a safe sequence) in which every process can get its maximum needs and finish. An unsafe state is not necessarily a deadlock, but it may lead to one. The Banker's algorithm keeps four data structures: Available, Max, Allocation and Need, where Need = Max - Allocation. The safety algorithm sets Work = Available and repeatedly finds a process whose Need is less than or equal to Work, pretends it finishes, and adds its Allocation to Work. If every process can finish, the state is safe. A request is granted only if the resulting state is still safe.

## Recovery
Recovery options are aborting all deadlocked processes, aborting one at a time until the cycle is broken, or preempting resources from a victim and rolling it back. Choosing victims carelessly can cause starvation, so the number of rollbacks is usually included in the cost.

## Wait-for graph
When every resource has a single instance, deadlock detection uses a wait-for graph: remove the resource nodes from the resource allocation graph and draw an edge Pi → Pj if Pi is waiting for a resource that Pj holds. A deadlock exists if and only if the wait-for graph has a cycle, so the OS periodically runs a cycle-detection algorithm (O(n²) for n processes). With multiple instances, a Banker's-like detection algorithm using Available, Allocation and Request matrices is used instead.

## Deadlock vs starvation
In a deadlock, every process in the set waits forever and none progress. In starvation, the system keeps progressing but one process is postponed indefinitely, for example a low-priority process in priority scheduling. Deadlock implies starvation for the processes involved, but starvation does not imply deadlock.

## Minimum Resources to Avoid Deadlock
With n processes sharing R identical units, where process i needs at most d_i units, the worst case is every process holding d_i - 1 units and waiting for one more. So deadlock is impossible exactly when R > sum(d_i - 1), i.e. R + n > sum of all demands. Example: 3 processes each needing 2 units need at least 3*(2-1) + 1 = 4 units; with 3 units all three can hold one each and deadlock. GATE 2018: 3 processes sharing 4 units, the largest k each may request with no deadlock is k = 2, since 4 + 3 > 3*2 but not > 3*3. If the demands are 3, 4 and 5, then 2 + 3 + 4 = 9 units can still deadlock and 10 is the minimum that is always safe.
