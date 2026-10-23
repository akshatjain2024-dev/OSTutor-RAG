---
topic: Process Management
source: Class notes - Unit 2
---
# Processes

A process is a program in execution. A program is a passive file on disk; it becomes a process when it is loaded into memory and starts running. One program can create many processes, for example several terminals running bash.

## Memory layout of a process
A process has a text section (the code), a data section (global variables), a heap (memory allocated at run time with malloc) and a stack (function parameters, return addresses and local variables). The heap grows upward and the stack grows downward.

## Process states
A process moves between five states:
- New: being created.
- Ready: waiting to be given the CPU.
- Running: instructions are executing.
- Waiting (Blocked): waiting for an event such as I/O completion.
- Terminated: finished execution.
Transitions: New to Ready (admitted), Ready to Running (scheduler dispatch), Running to Ready (interrupt or time slice over), Running to Waiting (I/O or event wait), Waiting to Ready (I/O or event done), Running to Terminated (exit).

## Process Control Block (PCB)
The kernel keeps a PCB for every process. It stores the process state, process ID (PID), program counter, CPU registers, scheduling information such as priority, memory management information such as page tables, accounting information and the list of open files. In Linux the PCB is the task_struct structure.

## Context switch
When the CPU switches from one process to another, the kernel saves the state of the old process into its PCB and loads the saved state of the new one. This is called a context switch. It is pure overhead because no useful work is done while switching, so its speed depends on hardware support and the amount of state to copy.

## Schedulers
The long-term scheduler (job scheduler) decides which jobs are admitted into memory and controls the degree of multiprogramming. The short-term scheduler (CPU scheduler) picks which ready process runs next and runs very frequently. The medium-term scheduler swaps processes out of memory and back in to reduce load.

## Zombie and orphan processes
A zombie process has finished but its parent has not yet called wait(), so its entry still sits in the process table. An orphan process is one whose parent finished first; in Linux it is adopted by init (or systemd), which later reaps it.
