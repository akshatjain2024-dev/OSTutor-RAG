---
topic: auto
source: Viva questions
doc_type: question_bank
---
# Viva questions and answers

## Process Management
Q: Name the five process states.
A: New, Ready, Running, Waiting (Blocked) and Terminated.
Q: What is stored in a PCB?
A: Process state, PID, program counter, CPU registers, scheduling info like priority, memory-management info like page tables, accounting info and the list of open files.
Q: Can a process go directly from Waiting to Running?
A: No. When the event it waited for completes, it moves to the Ready state and must be picked by the scheduler before it runs again.
Q: What is an orphan process?
A: A process whose parent terminated before it. In Linux it is adopted by init (or systemd), which reaps it when it ends.
Q: Which scheduler runs most frequently?
A: The short-term (CPU) scheduler, which may run every few milliseconds, so it must be very fast.
Q: What is the PID of init or systemd in Linux?
A: PID 1. It is the first user process started by the kernel and the ancestor of all other user processes.

## Threads
Q: What does a thread have of its own, and what does it share?
A: Each thread has its own thread ID, program counter, registers and stack. It shares the code, data, heap and open files with other threads of the same process.
Q: Which multithreading model does Linux use?
A: One-to-one: each user thread maps to its own kernel thread (Linux calls them tasks).
Q: What is the drawback of the many-to-one model?
A: If one thread makes a blocking system call, the whole process blocks, and threads cannot run in parallel on multiple cores.
Q: What flag is used to compile a Pthreads program with gcc?
A: The -pthread flag, for example gcc prog.c -o prog -pthread.
Q: Can you have concurrency without parallelism?
A: Yes. On a single core, the OS interleaves tasks so they all make progress, but only one runs at any instant.

## CPU Scheduling
Q: What is the goal of CPU scheduling?
A: To keep the CPU busy and decide which ready process runs next, balancing utilization, throughput, turnaround time, waiting time and response time.
Q: Which algorithm gives the minimum average waiting time?
A: SJF (and its preemptive form SRTF) gives the minimum average waiting time for a given set of processes.
Q: What is aging?
A: Gradually increasing the priority of processes that have waited a long time, so that low-priority processes eventually run and do not starve.
Q: What happens in Round Robin if the time quantum is very large?
A: RR behaves like FCFS because most processes finish within one quantum.
Q: What happens if the time quantum is very small?
A: There are too many context switches, so the overhead becomes large and useful CPU time drops.
Q: Is FCFS preemptive?
A: No. Once a process gets the CPU it keeps it until it finishes or blocks.
Q: Which Linux scheduler is the default for normal processes?
A: The Completely Fair Scheduler (CFS), which tracks each task's virtual runtime and always runs the task with the smallest vruntime. Newer kernels (6.6+) replaced it with EEVDF, which works on similar fairness ideas.

## Process Synchronization
Q: What is a race condition?
A: A situation where the result depends on the order in which concurrent processes access shared data, for example two threads incrementing a counter and losing an update.
Q: What are the three requirements for a critical section solution?
A: Mutual exclusion, progress and bounded waiting.
Q: What are the two operations on a semaphore?
A: wait() (P, down), which decrements and may block, and signal() (V, up), which increments and may wake a waiting process. Both must be atomic.
Q: What is the difference between a mutex and a binary semaphore?
A: Both allow one process at a time, but a mutex has an owner and must be released by the thread that locked it, while any process can signal a semaphore.
Q: What can go wrong if wait(empty) and wait(mutex) are swapped in the producer?
A: The producer may hold the mutex while waiting on a full buffer, and the consumer can never get the mutex to empty it, causing a deadlock.
Q: What is a spinlock?
A: A lock where a waiting thread keeps looping (busy waiting) until the lock is free. It avoids context switches, so it suits short critical sections on multicore systems.
Q: What is priority inversion?
A: When a high-priority process waits for a lock held by a low-priority process, which is itself preempted by a medium-priority process. Priority inheritance fixes it by temporarily raising the low-priority holder's priority.

## Deadlocks
Q: What is a deadlock?
A: A situation where a set of processes are each waiting for a resource held by another process in the set, so none of them can ever proceed.
Q: What is a safe state?
A: A state in which there exists at least one order (safe sequence) in which all processes can obtain their maximum resources and finish.
Q: How is the Need matrix calculated in the Banker's algorithm?
A: Need = Max − Allocation, for every process and resource type.
Q: What is the difference between deadlock and starvation?
A: In deadlock processes wait on each other forever and none progress. In starvation a process waits indefinitely while others keep progressing, for example due to low priority.
Q: When does a cycle in a resource allocation graph mean a definite deadlock?
A: When every resource type in the cycle has only one instance. With multiple instances, a cycle only means deadlock is possible.
Q: What approach do Linux and Windows take for deadlocks?
A: They mostly ignore the problem (the ostrich approach) and leave it to application developers, because prevention and avoidance are expensive.

## Memory Management
Q: What does the MMU do?
A: The Memory Management Unit translates logical (virtual) addresses generated by the CPU into physical addresses at run time.
Q: What is external fragmentation?
A: Enough total free memory exists to satisfy a request, but it is scattered in small non-contiguous holes.
Q: What is internal fragmentation?
A: Wasted space inside an allocated block because the block is larger than the memory requested.
Q: Does paging cause external fragmentation?
A: No. Any free frame can be used for any page, so there is no external fragmentation, but the last page of a process can cause internal fragmentation.
Q: Why is multi-level paging used?
A: With large address spaces a single page table becomes huge. Multi-level paging pages the page table itself so only the parts in use need to be in memory.
Q: What is segmentation?
A: A memory scheme that divides a program into variable-size logical segments like code, data and stack, each addressed by a segment number and an offset.
Q: Which placement strategy is usually fastest?
A: First fit, because it stops searching as soon as it finds a hole that is large enough.

## Virtual Memory
Q: What is virtual memory?
A: A technique that lets a process execute even when only part of it is in physical memory, giving each process a large logical address space backed by disk.
Q: What is demand paging?
A: Loading a page into memory only when it is first referenced, instead of loading the whole program at the start.
Q: What is a page fault?
A: A trap raised when a process accesses a page that is not currently in memory (its valid bit is invalid). The OS then loads the page from disk.
Q: Which page replacement algorithm has the lowest fault rate?
A: The Optimal algorithm (replace the page not used for the longest time in the future), but it needs future knowledge so it is only used as a benchmark.
Q: What is Belady's anomaly?
A: When increasing the number of frames increases the number of page faults. It can happen with FIFO but not with LRU or OPT.
Q: Why don't LRU and OPT suffer from Belady's anomaly?
A: They are stack algorithms: the set of pages in memory with n frames is always a subset of the set with n+1 frames.
Q: Why is copy-on-write useful?
A: After fork(), parent and child share pages until one writes, so pages are copied only when necessary and fork() becomes fast, especially when exec() follows.

## File Systems
Q: What is a file?
A: A named collection of related information stored on secondary storage; the smallest logical unit of storage visible to users.
Q: What is an inode?
A: A UNIX data structure storing a file's metadata (owner, permissions, size, timestamps, link count) and pointers to its data blocks. It does not store the file name.
Q: What is the difference between a hard link and a soft link?
A: A hard link is another directory entry pointing to the same inode, so it survives deletion of the original name. A soft (symbolic) link is a separate file containing a path, and it breaks if the target is deleted.
Q: What is the main problem with contiguous allocation?
A: External fragmentation, and it is hard to grow a file if the following blocks are already used.
Q: What does the execute permission mean on a directory?
A: It allows you to enter (cd into) the directory and access files inside it by name.
Q: What is journaling?
A: The file system first writes metadata changes to a log (journal) before applying them, so after a crash it can replay or discard incomplete operations quickly. ext4 uses it.

## Disk Scheduling
Q: Which component of disk access time does disk scheduling try to reduce?
A: Seek time, which is usually the largest part.
Q: Why is SCAN called the elevator algorithm?
A: Because the head moves in one direction serving requests until the end, then reverses, like an elevator going up and down.
Q: What is the advantage of C-SCAN over SCAN?
A: It gives more uniform waiting times, since the head serves requests in only one direction and jumps back to the start.
Q: Which disk scheduling algorithm can cause starvation?
A: SSTF, because requests far from the head can keep getting skipped if new nearby requests keep arriving.

## System Calls
Q: What is a system call?
A: The programming interface through which a user process requests a service from the kernel, such as creating a process or reading a file.
Q: How many processes are created by n consecutive fork() calls?
A: The total number of processes becomes 2^n, so 2^n − 1 new child processes are created.
Q: What does exec() do?
A: It replaces the current process image with a new program. The PID stays the same, and if exec succeeds it never returns.
Q: What is the difference between wait() and waitpid()?
A: wait() waits for any child to terminate. waitpid() can wait for a specific child and supports options like WNOHANG for non-blocking checks.
Q: What are file descriptors 0, 1 and 2?
A: Standard input, standard output and standard error.
Q: What does open() return?
A: The lowest-numbered unused file descriptor, or -1 on error.
Q: What does dup2(fd, 1) do?
A: It makes file descriptor 1 (standard output) refer to the same file as fd, so everything printed goes to that file. The shell uses this for redirection.

## Inter-Process Communication
Q: Which end of a pipe is fd[0]?
A: fd[0] is the read end and fd[1] is the write end.
Q: Can an ordinary pipe be used between unrelated processes?
A: No, it needs a parent-child (related) relationship. Unrelated processes can use a named pipe (FIFO).
Q: Which signal is sent when you press Ctrl+C?
A: SIGINT.
Q: Which signals cannot be caught or ignored?
A: SIGKILL and SIGSTOP.
Q: What does the kill() system call do?
A: It sends a signal to a process, not necessarily one that kills it.

## Linux Commands
Q: What does chmod 644 give?
A: rw-r--r--: the owner can read and write; group and others can only read.
Q: How do you see all running processes?
A: ps -ef or ps aux. top shows them live with CPU and memory usage.
Q: What is the difference between kill PID and kill -9 PID?
A: kill sends SIGTERM, which asks the process to exit and can be handled. kill -9 sends SIGKILL, which cannot be caught and terminates immediately.
Q: What does grep -v do?
A: It prints the lines that do NOT match the pattern.
Q: What is the difference between 2> and >?
A: > redirects standard output, while 2> redirects standard error.

## Shell Programming
Q: What is the shebang line?
A: The first line of a script, like #!/bin/bash, which tells the system which interpreter to run the script with.
Q: What does $? hold?
A: The exit status of the last command; 0 means success and non-zero means failure.
Q: What does $# hold?
A: The number of command-line arguments passed to the script.
Q: How do you compare two numbers in a bash if statement?
A: Using -eq, -ne, -gt, -lt, -ge or -le inside [ ], for example if [ $a -gt $b ].
Q: How do you make a script executable?
A: chmod +x script.sh, then run it with ./script.sh.

## OS Basics
Q: What is the kernel?
A: The kernel is the core part of the OS that is always running in memory in privileged mode. It handles process scheduling, memory management, device control and system calls.
Q: Why do we need dual-mode operation?
A: To protect the OS and other programs from errant or malicious user programs. Privileged instructions can only run in kernel mode, so a user program must ask the kernel through a system call.
Q: What is the difference between multiprogramming and multitasking?
A: Multiprogramming keeps several jobs in memory so the CPU switches when one waits for I/O, improving CPU utilization. Multitasking (time-sharing) switches the CPU frequently, even without I/O, so many users get quick responses.
Q: What is a bootstrap program?
A: It is the small program stored in firmware (BIOS/UEFI) that runs at power-on, initializes the hardware and loads the OS kernel into memory.
Q: Give one example each of a monolithic kernel and a microkernel.
A: Linux is a monolithic kernel; Mach and QNX are microkernels. macOS uses a hybrid built on Mach.

## I/O Systems
Q: What is DMA?
A: Direct Memory Access lets a device controller transfer a block of data directly between the device and memory, interrupting the CPU only when the whole transfer is done.
Q: What is polling?
A: The CPU repeatedly checks a device's status register to see if it is ready. It wastes CPU time when the device is slow.
Q: What is a device driver?
A: Kernel software that knows how to control a specific device and gives the rest of the OS a uniform interface to it.

## Protection and Security
Q: What is the difference between protection and security?
A: Protection controls access of processes and users to resources inside the system. Security defends the system against external and internal attacks.
Q: What is the access matrix?
A: A model where rows are domains (users or processes), columns are objects, and each entry lists the access rights the domain has on the object.
Q: What is a buffer overflow attack?
A: Writing more data into a buffer than it can hold so that it overwrites adjacent memory, such as a return address, letting the attacker run their own code.

## Virtualization
Q: What is a hypervisor?
A: Software (a virtual machine monitor) that creates and runs virtual machines and shares the physical hardware among them.
Q: What is the difference between type 1 and type 2 hypervisors?
A: A type 1 hypervisor runs directly on the hardware (for example VMware ESXi, Xen, KVM). A type 2 runs on top of a host OS (for example VirtualBox, VMware Workstation).
