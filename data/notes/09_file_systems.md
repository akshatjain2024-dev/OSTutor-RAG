---
topic: File Systems
source: Class notes - Unit 5
---
# File Systems

A file is a named collection of related information stored on secondary storage. The file system provides the mapping from file names to disk blocks and handles access, protection and free space.

## File attributes and operations
Attributes include name, identifier, type, location, size, protection and timestamps. Basic operations are create, open, read, write, seek (reposition), delete and truncate. The OS keeps an open-file table so it does not have to search the directory on every access.

## Access methods
Sequential access reads records in order, like a tape. Direct (random) access can read any block by its number, which suits databases. Indexed access uses an index to find records quickly.

## Directory structures
Single-level (one directory for everyone), two-level (one directory per user), tree-structured (subdirectories, absolute and relative paths), acyclic graph (allows sharing using links) and general graph directories. Linux uses a tree with hard links and symbolic links.

## Allocation methods
- Contiguous allocation: each file occupies consecutive blocks. Fast sequential and direct access, but external fragmentation and files are hard to grow.
- Linked allocation: each block points to the next. No external fragmentation, but direct access is slow and a broken pointer loses the rest of the file. FAT (File Allocation Table) is a variant that keeps all the pointers in a table.
- Indexed allocation: each file has an index block holding the addresses of its data blocks. Supports direct access without external fragmentation. Large files use linked, multilevel or combined index schemes.

## Inodes
UNIX and Linux use the inode (index node). Each inode holds the file's metadata (owner, permissions, size, timestamps, link count) and pointers to its data: typically 12 direct pointers, one single indirect, one double indirect and one triple indirect pointer. The file name is not stored in the inode; it lives in the directory entry, which maps names to inode numbers. You can see inode numbers with ls -i.

## Free space management
Free space can be tracked with a bit vector (bitmap, one bit per block), a linked list of free blocks, grouping, or counting runs of free blocks.

## Protection
UNIX permissions use three classes (owner, group, others) and three rights (read, write, execute), shown as rwxr-xr-x and changed with chmod. Access control lists give finer control.

## Maximum file size with an inode
Example: 4 KB blocks, 4-byte block pointers, 12 direct pointers plus single, double and triple indirect. One block holds 4096 / 4 = 1024 pointers.
- Direct: 12 × 4 KB = 48 KB
- Single indirect: 1024 × 4 KB = 4 MB
- Double indirect: 1024 × 1024 × 4 KB = 4 GB
- Triple indirect: 1024 × 1024 × 1024 × 4 KB = 4 TB
Maximum file size ≈ 48 KB + 4 MB + 4 GB + 4 TB, roughly 4 TB. Small files need only the direct pointers, which is why the scheme is fast for the common case.

## Journaling
A journaling file system (ext4, NTFS) first writes the intended metadata changes to a log called the journal, and only then applies them to the real structures. If the system crashes in the middle, on reboot the OS replays complete transactions from the journal and discards incomplete ones, so it does not have to scan the whole disk with fsck.

## Mounting
Before a file system can be used it must be mounted, that is attached to a directory (the mount point) in the existing tree. For example mount /dev/sdb1 /mnt/usb makes the USB drive's files appear under /mnt/usb. umount detaches it.
