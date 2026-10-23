---
topic: Disk Scheduling
source: Class notes - Unit 5
---
# Disk Scheduling

On a hard disk, access time = seek time (moving the head to the right cylinder) + rotational latency (waiting for the sector to come under the head) + transfer time. Seek time usually dominates, so disk scheduling tries to reduce total head movement.

## Algorithms
- FCFS: serve requests in arrival order. Fair, but the head can swing wildly.
- SSTF (Shortest Seek Time First): serve the request closest to the current head position. Reduces seek time but can starve far-away requests.
- SCAN (elevator algorithm): the head moves in one direction serving requests until it reaches the end of the disk, then reverses.
- C-SCAN (circular SCAN): like SCAN but serves requests only in one direction; at the end it jumps back to the start without serving. Gives more uniform waiting times.
- LOOK and C-LOOK: like SCAN and C-SCAN, but the head only goes as far as the last request in each direction instead of the physical end of the disk.

## Worked example
Queue: 98, 183, 37, 122, 14, 124, 65, 67 with the head at cylinder 53.
- FCFS total head movement = 640 cylinders.
- SSTF order 65, 67, 37, 14, 98, 122, 124, 183, total = 236 cylinders.
- SCAN moving toward 0 then reversing gives 236 cylinders (53 down to 0 and back up to 183).
- C-LOOK moving toward higher cylinders: 65, 67, 98, 122, 124, 183, then jump to 14, 37.

## SSDs and RAID
SSDs have no moving head, so FCFS is usually fine; the concern is wear levelling instead. RAID combines disks for performance and reliability: RAID 0 is striping with no redundancy, RAID 1 is mirroring, and RAID 5 is block-level striping with distributed parity.
