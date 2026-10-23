---
topic: OS Basics
source: Class notes - Unit 1 (OS structures)
---
# OS Services, Structures and Booting

## Services an OS provides
For users and programs: user interface (command line, GUI, touch), program execution, I/O operations, file-system manipulation, communication between processes, and error detection. For efficient operation of the system itself: resource allocation, accounting (who used how much), and protection and security.

## User interfaces
The command interpreter (shell) reads a command and executes it, either by running built-in code or, as in UNIX, by finding and running a program with that name. Graphical and touch interfaces sit on top of the same system calls.

## System programs
Utilities that come with the OS but are not part of the kernel: file management (ls, cp), status information (date, df, top), file modification (editors), programming-language support (compilers, debuggers), program loading and execution (loaders, linkers), communication (ssh, mail) and background services (daemons).

## Ways to structure an OS
- Simple / monolithic: all services in one kernel address space. Original UNIX had the kernel plus system programs. Fast because components call each other directly, but hard to maintain.
- Layered: the OS is built in layers, each using only the layer below. Easy to debug layer by layer, but hard to define layers and every call passes through several layers.
- Microkernel: only minimal functions in the kernel; everything else runs as user-level servers that communicate through message passing. More reliable and secure, slower because of message overhead.
- Loadable kernel modules: a core kernel with modules (drivers, file systems) that can be linked in at run time. Linux uses this; lsmod lists modules and modprobe/insmod loads them.
- Hybrid: real systems mix approaches. Windows and macOS are hybrids; Linux is monolithic plus modules.

## Booting
1. At power-on, the CPU runs firmware (BIOS or UEFI) stored in non-volatile memory.
2. The firmware runs power-on self-tests and finds a bootable device.
3. It loads a boot loader (for Linux usually GRUB), which lets you choose a kernel.
4. The boot loader loads the kernel image and an initial RAM file system (initramfs) into memory and jumps to the kernel.
5. The kernel initializes hardware, memory management and drivers, mounts the root file system and starts the first user process, init or systemd (PID 1).
6. systemd starts services and the login prompt or desktop.

## Multiprocessor terms
Symmetric multiprocessing (SMP): every CPU is a peer and runs the OS. Asymmetric: one master CPU controls the others. Multicore: several cores on one chip. Clustered systems: separate computers joined by a network that provide high availability.
