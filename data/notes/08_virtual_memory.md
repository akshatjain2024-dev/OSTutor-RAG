---
topic: Virtual Memory
source: Class notes - Unit 4
---
# Virtual Memory

Virtual memory lets a process run even if only part of it is in physical memory. The logical address space can be much larger than physical memory, more programs can run at once, and programmers do not need to worry about memory size.

## Demand paging
With demand paging, a page is loaded into memory only when it is first needed. Each page-table entry has a valid-invalid bit. If a process accesses a page marked invalid, the hardware raises a page fault. The OS then finds a free frame, reads the page from disk (the backing store or swap space), updates the page table, and restarts the instruction that caused the fault.

Effective access time = (1 - p) x memory access time + p x page fault service time, where p is the page fault rate. Because servicing a fault takes milliseconds while a memory access takes nanoseconds, even a tiny page fault rate slows the system down a lot.

## Page replacement
If no frame is free, a victim page must be replaced. A dirty (modify) bit tells whether the page must be written back to disk first.

- FIFO: replace the oldest page in memory. Simple, but can suffer from Belady's anomaly, where adding more frames increases the number of page faults.
- Optimal (OPT/MIN): replace the page that will not be used for the longest time in the future. Gives the lowest possible page fault rate but needs future knowledge, so it is used only as a benchmark.
- LRU (Least Recently Used): replace the page that has not been used for the longest time. A good approximation of OPT, implemented with counters or a stack. LRU and OPT are stack algorithms and do not suffer from Belady's anomaly.
- Second chance (clock): FIFO with a reference bit; a page with reference bit 1 gets a second chance.
- LFU and MFU: count-based schemes, rarely used.

## Worked example
Reference string 7 0 1 2 0 3 0 4 2 3 0 3 2 with 3 frames. FIFO gives 10 page faults, LRU gives 9 and OPT gives 7.

## Thrashing
Thrashing happens when a process does not have enough frames, so it spends more time paging than executing. CPU utilization drops, the OS may wrongly increase the degree of multiprogramming, and things get worse. Solutions use locality: the working-set model gives each process enough frames for the pages it used in the last delta references, and page fault frequency control adds or removes frames to keep the fault rate within bounds.

## Copy-on-write
After fork(), parent and child initially share the same pages marked copy-on-write. A page is copied only when one of them writes to it, which makes fork() fast.
