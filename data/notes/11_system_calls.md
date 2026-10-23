---
topic: System Calls
source: Lab manual - Experiment 3
---
# System Calls and the Process API

A system call is the interface through which a user program asks the kernel for a service. Libraries such as glibc wrap system calls in normal C functions. Categories: process control, file management, device management, information maintenance, communication and protection.

## fork()
fork() creates a new child process that is a copy of the parent. It is called once but returns twice: it returns 0 in the child, the child's PID in the parent, and -1 on failure. After fork both processes continue from the next statement. If fork() is called n times in sequence without conditions, the total number of processes is 2^n (so 2^n - 1 new children).

## exec()
The exec family (execl, execlp, execv, execvp and others) replaces the current process image with a new program. The PID stays the same. If exec succeeds it never returns, so any code after a successful exec call is never run. The usual pattern is fork-then-exec: the child calls exec to run a new program while the parent waits.

## wait() and waitpid()
wait() blocks the parent until any child terminates and returns that child's PID. waitpid(pid, &status, options) waits for a specific child; with WNOHANG it returns immediately if the child has not finished. Calling wait reaps the child, so it does not stay a zombie.

## exit() and getpid()
exit(status) terminates the calling process and returns the status to the parent. getpid() returns the caller's PID and getppid() returns the parent's PID.

## File system calls
- open(path, flags, mode) returns a file descriptor, the lowest unused one. Flags include O_RDONLY, O_WRONLY, O_RDWR, O_CREAT, O_TRUNC and O_APPEND.
- read(fd, buf, n) reads up to n bytes and returns the number actually read, 0 at end of file.
- write(fd, buf, n) writes n bytes and returns how many were written.
- close(fd) frees the descriptor. lseek(fd, offset, whence) moves the file offset.
File descriptors 0, 1 and 2 are standard input, standard output and standard error. Because open returns the lowest free descriptor, closing 1 and then opening a file makes that file the new standard output, which is how the shell does output redirection. dup2(oldfd, newfd) does the same thing directly.

## Tracing tip for lab exams
Draw the process tree, write down what fork returns in each process, check whether wait forces an order, and cross out code after a successful exec.
