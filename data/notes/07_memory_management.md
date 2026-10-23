---
topic: Memory Management
source: Class notes - Unit 4
---
# Memory Management

Main memory must hold the OS and several user processes at once, so the OS has to decide where each process goes and protect processes from each other.

## Logical vs physical addresses
The CPU generates logical (virtual) addresses. The memory unit sees physical addresses. The Memory Management Unit (MMU) maps logical to physical addresses at run time. With simple relocation, the MMU adds the value of a relocation (base) register to every address and checks it against a limit register for protection.

## Contiguous allocation
Each process gets one contiguous block of memory. Free blocks are called holes. Placement strategies:
- First fit: use the first hole that is big enough. Fast.
- Best fit: use the smallest hole that is big enough. Leaves the smallest leftover.
- Worst fit: use the largest hole. Leaves the largest leftover.
First fit and best fit usually perform better than worst fit.

## Fragmentation
External fragmentation means there is enough total free memory but it is split into small non-contiguous holes. It can be fixed by compaction or by paging. Internal fragmentation means memory inside an allocated block is wasted because the block is larger than requested, which happens with fixed-size partitions and with the last page of a process.

## Paging
Paging divides physical memory into fixed-size frames and logical memory into pages of the same size. A logical address is split into a page number p and an offset d. The page table maps each page number to a frame number. Paging removes external fragmentation, but can still have internal fragmentation in the last page.

Example: with a 4 KB page size, the offset needs 12 bits. In a 32-bit address space the page number is the remaining 20 bits, so the page table can have up to 2^20 entries.

## TLB
Looking up the page table in memory doubles the number of memory accesses. A Translation Lookaside Buffer (TLB) is a small fast associative cache of recent page-table entries. On a TLB hit the frame is found immediately; on a miss the page table is consulted and the TLB is updated. Effective access time = hit ratio x (TLB time + memory time) + (1 - hit ratio) x (TLB time + 2 x memory time).

## Page table structures
Large address spaces make page tables huge, so hierarchical (multi-level) paging, hashed page tables and inverted page tables are used to reduce their size.

## Segmentation
Segmentation divides a program into logical units like code, stack and data, each with its own length. A logical address is a pair (segment number, offset), and a segment table stores the base and limit of each segment. It matches the programmer's view of memory but suffers from external fragmentation.

## Swapping
A process can be temporarily moved out of memory to a backing store (disk) and brought back later, which lets the total memory of all processes exceed physical memory. Swapping a whole process is slow because transfer time is proportional to its size, so modern systems instead swap individual pages (paging out), and mobile systems such as Android and iOS usually avoid swapping and terminate background apps instead.

## Degree of Multiprogramming and CPU Utilization
If each process spends a fraction p of its time waiting for I/O and n processes are in memory, the CPU is idle only when all n are waiting at once, so CPU utilization = 1 - p^n. With p = 0.7: one process gives 1 - 0.7 = 30%, two processes give 1 - 0.49 = 51%, four processes give 1 - 0.2401 = 76%, and eight processes give about 94%. More RAM lets more processes fit, which raises the degree of multiprogramming and the utilization. (The Gate Smashers L-5.1 video quotes 76% for two and 93% for four processes; those figures are off by one step, the correct values are 51% and 76%.)
