---
topic: I/O Systems
source: Class notes - Unit 5
---
# I/O Systems

The I/O subsystem lets the OS talk to a huge variety of devices (keyboards, disks, network cards, printers) through a uniform interface. Each device is connected through a controller, and the OS talks to the controller using a device driver.

## Ways to do I/O
- Polling (programmed I/O): the CPU repeatedly reads the device's status register until the device is ready, then moves the data itself. Simple, but it wastes CPU cycles when the device is slow.
- Interrupt-driven I/O: the CPU starts the operation and goes on with other work; the controller raises an interrupt when it is done. Better for slow devices, but transferring a large block still causes many interrupts.
- Direct Memory Access (DMA): the CPU tells the DMA controller the source, destination and byte count; the DMA controller moves the whole block between the device and memory and interrupts the CPU only once at the end. Used for disks and network cards. While DMA uses the memory bus, the CPU may be briefly slowed (cycle stealing).

## Device types
- Block devices (disks, SSDs) transfer fixed-size blocks and support random access with read, write and seek.
- Character devices (keyboard, mouse, serial port) transfer a stream of bytes one at a time.
- Network devices use a socket interface.
In Linux, devices appear as special files under /dev; ls -l shows b for block devices and c for character devices.

## Blocking and non-blocking I/O
Blocking I/O suspends the process until the operation finishes, which is easy to program. Non-blocking I/O returns immediately with whatever data is available. Asynchronous I/O starts the operation and notifies the process later when it completes.

## Kernel I/O subsystem services
- Scheduling: ordering I/O requests to improve efficiency, for example disk scheduling.
- Buffering: a memory area that holds data while it moves between a device and an application. It copes with speed mismatches (a modem filling a buffer that is written to disk all at once) and size mismatches. Double buffering lets the device fill one buffer while the other is being processed.
- Caching: keeping a copy of frequently used data in faster storage. The difference from a buffer is that a cache only holds a copy; a buffer may hold the only copy of the data.
- Spooling: a buffer for a device that can serve only one request at a time, such as a printer. Output from each process is written to a spool file on disk, and the spooler sends them to the printer one by one.
- Error handling and protection: all I/O instructions are privileged, so user programs must use system calls.

## I/O software layers
From top to bottom: user-level I/O libraries, the device-independent part of the kernel (naming, buffering, protection), device drivers (one per device type, which understand the controller's registers), interrupt handlers, and finally the hardware controller and device.
