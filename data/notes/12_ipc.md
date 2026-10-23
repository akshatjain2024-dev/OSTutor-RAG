---
topic: Inter-Process Communication
source: Class notes - Unit 2
---
# Inter-Process Communication (IPC)

Independent processes cannot affect each other, but cooperating processes share data, so they need a way to communicate. The two basic IPC models are shared memory and message passing.

## Shared memory
The processes map a common region of memory into their address spaces and read and write it directly. It is very fast because the kernel is only involved in setting it up, but the processes themselves must synchronize access (usually with semaphores). System V calls: shmget() creates the segment, shmat() attaches it, shmdt() detaches it and shmctl() controls or removes it.

## Message passing
Processes exchange messages through the kernel with send() and receive(). It is easier to use and works across machines, but each message needs a system call so it is slower. Communication can be direct (naming the other process) or indirect (through mailboxes or ports), and synchronous (blocking) or asynchronous (non-blocking). System V message queues use msgget(), msgsnd() and msgrcv().

## Pipes
An ordinary (anonymous) pipe is a one-way channel between related processes, usually a parent and child. pipe(fd) creates it: fd[0] is the read end and fd[1] is the write end. Each process should close the end it does not use, otherwise the reader never sees end of file. In the shell, ls | wc -l connects two commands with a pipe.

A named pipe (FIFO) has a name in the file system, created with mkfifo, and can be used by unrelated processes.

## Signals
A signal is a software notification sent to a process, for example SIGINT when you press Ctrl+C, SIGKILL to kill a process (cannot be caught), SIGTERM to ask it to terminate and SIGCHLD when a child ends. signal() or sigaction() install a handler, and kill(pid, sig) sends a signal.

## Sockets
Sockets are endpoints for communication between processes, on the same machine or across a network, identified by an IP address and a port.
