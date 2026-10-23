---
topic: Threads
source: Class notes - Unit 2
---
# Threads

A thread is the basic unit of CPU use inside a process. It has its own thread ID, program counter, register set and stack, but it shares the code section, data section, heap and open files with the other threads of the same process. A process with several threads can do several things at once, like a browser downloading a file while you keep scrolling.

## Why use threads
- Responsiveness: one thread can keep the user interface alive while another does slow work.
- Resource sharing: threads share memory by default, so no special IPC is needed.
- Economy: creating a thread and switching between threads is much cheaper than doing the same for processes.
- Scalability: threads can run in parallel on multicore CPUs.

## Concurrency vs parallelism
Concurrency means more than one task is making progress, possibly by taking turns on one core. Parallelism means tasks are literally running at the same time on different cores. A single-core system can be concurrent but not parallel.

## User threads and kernel threads
User-level threads are managed by a thread library without kernel involvement, so they are fast, but if one blocks on a system call the whole process can block. Kernel-level threads are managed by the OS, so the kernel can schedule them on different cores.

## Multithreading models
- Many-to-one: many user threads map to one kernel thread. Cheap, but no true parallelism and one blocking call blocks all.
- One-to-one: each user thread gets a kernel thread. True parallelism; used by Linux and Windows. Cost is that creating many threads creates many kernel threads.
- Many-to-many: many user threads multiplexed over a smaller or equal number of kernel threads. Flexible but complex.

## Pthreads
POSIX threads (Pthreads) is the standard thread API on Linux. pthread_create() starts a new thread running a given function, pthread_join() waits for a thread to finish, and pthread_exit() ends the calling thread. Programs are compiled with the -pthread flag, for example gcc prog.c -pthread.

## Thread pools
Creating a new thread for every request (for example every web request) costs time, and unlimited threads can exhaust memory. A thread pool creates a fixed number of threads at start-up; incoming tasks are placed in a queue and an idle pool thread picks each one up. This is faster than creating threads on demand and limits the number of threads running at once.
