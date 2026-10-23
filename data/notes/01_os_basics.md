---
topic: OS Basics
source: Class notes - Unit 1
---
# Introduction to Operating Systems

An operating system (OS) is the layer of software that sits between the hardware and user programs. It manages the CPU, memory, storage and I/O devices, and gives programs a clean interface to use them. You can think of it as a resource manager plus a control program: it decides who gets which resource and stops programs from interfering with each other.

## Kernel mode and user mode
Modern CPUs have at least two privilege levels. The kernel runs in kernel mode (also called supervisor or privileged mode) and can execute any instruction, including ones that touch hardware directly. Normal applications run in user mode. When a user program needs something only the kernel can do, like reading a file, it makes a system call, which switches the CPU into kernel mode through a trap. A mode bit in the CPU records the current mode.

## Types of operating systems
- Batch systems: jobs are collected and run one after another without user interaction.
- Multiprogramming: several jobs are kept in memory so the CPU always has something to run when one job waits for I/O.
- Time-sharing (multitasking): the CPU switches between jobs so quickly that each user feels they have the machine to themselves.
- Real-time systems: correctness depends on meeting deadlines. Hard real-time systems must never miss a deadline; soft real-time systems try their best.
- Distributed systems: a group of networked machines that appear to the user as one system.

## Kernel structures
A monolithic kernel (traditional UNIX, Linux) puts most services in one large kernel for speed. A microkernel (Mach, QNX) keeps only the essentials in the kernel and moves services like file systems and drivers to user space, which is more reliable but adds message-passing overhead. Linux is monolithic but supports loadable kernel modules, so drivers can be added at run time.

## Interrupts
An interrupt is a signal to the CPU that an event needs attention, such as a key press or a disk finishing a read. The CPU saves its state, jumps to an interrupt service routine through the interrupt vector, handles the event, and then resumes. A trap (or exception) is a software-generated interrupt caused by an error or a system call.
