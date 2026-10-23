import re
from collections import Counter

TOPIC_KEYWORDS = {
    "OS Basics": ["kernel mode", "user mode", "mode bit", "interrupt", "trap", "monolithic",
                  "microkernel", "batch system", "timer", "boot", "bios", "uefi", "system program", "time-sharing", "real-time", "multiprogramming"],
    "Process Management": ["process state", "pcb", "process control block", "context switch",
                           "zombie", "orphan", "long-term scheduler", "short-term scheduler",
                           "ready queue", "task_struct", "process"],
    "Threads": ["thread", "pthread", "multithreading", "many-to-one", "one-to-one",
                "many-to-many", "user-level thread", "kernel thread", "concurrency", "parallelism"],
    "CPU Scheduling": ["scheduling", "fcfs", "sjf", "srtf", "round robin", "time quantum",
                       "turnaround", "waiting time", "response time", "convoy", "aging",
                       "priority scheduling", "multilevel", "burst", "throughput", "dispatcher"],
    "Process Synchronization": ["race condition", "critical section", "semaphore", "mutex",
                                "peterson", "spinlock", "monitor", "producer", "consumer",
                                "readers-writers", "dining philosophers", "test_and_set",
                                "bounded buffer", "mutual exclusion", "condition variable", "pthread_cond",
                                "spin lock", "ticket lock", "fetch-and-add", "compare-and-swap", "lock()",
                                "atomicity violation", "order violation", "missed wakeup", "throttling"],
    "Deadlocks": ["deadlock", "banker", "safe state", "safe sequence", "circular wait",
                  "hold and wait", "resource allocation graph", "coffman", "no preemption"],
    "Memory Management": ["paging", "page table", "frame", "fragmentation", "tlb",
                          "segmentation", "first fit", "best fit", "worst fit", "mmu",
                          "logical address", "physical address", "compaction", "page directory",
                          "multi-level page table", "linear page table", "pfn", "base and bounds"],
    "Virtual Memory": ["virtual memory", "demand paging", "page fault", "page replacement",
                       "lru", "fifo", "optimal", "belady", "thrashing", "working set",
                       "copy-on-write", "dirty bit", "swap"],
    "File Systems": ["file system", "inode", "directory", "contiguous allocation",
                     "linked allocation", "indexed allocation", "fat", "free space",
                     "bitmap", "hard link", "symbolic link", "access method"],
    "Disk Scheduling": ["disk scheduling", "seek time", "sstf", "scan", "c-scan", "look",
                        "c-look", "rotational latency", "head movement", "raid", "cylinder"],
    "System Calls": ["system call", "fork", "exec", "execvp", "wait()", "waitpid", "getpid",
                     "file descriptor", "open()", "read()", "write()", "dup2", "lseek"],
    "Inter-Process Communication": ["ipc", "pipe", "shared memory", "message passing",
                                    "shmget", "msgget", "fifo pipe", "mkfifo", "signal",
                                    "sigint", "sigkill", "socket", "mailbox"],
    "Linux Commands": ["chmod", "grep", "ls -l", "ps aux", "kill -9", "find", "wc",
                       "redirect", "man page", "chown", "umask", "top", "linux command"],
    "I/O Systems": ["dma", "direct memory access", "polling", "spooling", "buffering", "double buffering",
                    "device driver", "block device", "character device", "interrupt-driven", "non-blocking i/o",
                    "controller", "asynchronous i/o"],
    "Protection and Security": ["protection", "security", "access matrix", "access control list", "acl",
                                "capability", "least privilege", "trojan", "trap door", "buffer overflow",
                                "virus", "worm", "setuid", "authentication", "password", "salt", "domain"],
    "Virtualization": ["virtualization", "virtual machine", "hypervisor", "vmm", "type 1", "type 2",
                       "container", "docker", "namespace", "cgroup", "paravirtualization", "kvm", "xen",
                       "virtualbox", "guest os"],
    "Shell Programming": ["shell script", "bash", "shebang", "$#", "$?", "for loop",
                          "while loop", "case statement", "expr", "read var", "#!/bin/bash"],
}

SYNONYMS = {
    "rr": "round robin time quantum",
    "fcfs": "first come first served",
    "fifo": "first in first out",
    "sjf": "shortest job first",
    "srtf": "shortest remaining time first",
    "sstf": "shortest seek time first",
    "lru": "least recently used",
    "opt": "optimal page replacement",
    "pcb": "process control block",
    "tlb": "translation lookaside buffer",
    "ipc": "inter process communication",
    "mmu": "memory management unit",
    "rag": "resource allocation graph",
    "vm": "virtual memory",
    "cow": "copy on write",
    "p()": "wait semaphore", "v()": "signal semaphore",
    "lock": "mutex lock critical section",
    "starvation": "starvation aging indefinite blocking",
    "elevator": "scan disk scheduling",
    "deadly embrace": "deadlock",
    "context switching": "context switch",
    "permissions": "chmod rwx permission",
    "background job": "background & jobs fg bg",
    "zombie": "zombie process wait reap",
    "page miss": "page fault",
    "waiting for each other": "deadlock circular wait hold and wait",
    "each others": "deadlock circular wait",
    "stuck": "deadlock",
    "hangs": "deadlock",
    "infinite wait": "deadlock starvation",
    "vms": "virtual machine hypervisor",
    "cv": "condition variable wait signal",
    "cvs": "condition variable wait signal",
    "spinlock": "spin lock test-and-set",
    "containers": "container namespace cgroup",
    "acls": "access control list",
    "cfs": "completely fair scheduler linux scheduling vruntime",
    "rms": "rate monotonic real-time scheduling",
    "edf": "earliest deadline first real-time scheduling",
}

STOPWORDS = set("""a an the is are was were be been of to in on for and or with what why how
explain define describe give me tell about difference between vs versus does do can
please short notes example examples using use it its this that which""".split())


def tokenize(text: str):
    out = []
    for t in re.findall(r"[a-z0-9_\-\$#\?\(\)]+", text.lower()):
        if not t.startswith("$"):
            t = t.rstrip("?")
            if t.startswith("("):
                t = t.strip("()")
            elif t.endswith(")") and "(" not in t:
                t = t.rstrip(")")
        if not t:
            continue
        out.append(t)
        if "-" in t.strip("-"):
            out += [p for p in t.split("-") if len(p) > 1]
    return out


def expand_query(q: str) -> str:
    ql = q.lower()
    extra = [exp for key, exp in SYNONYMS.items()
             if re.search(rf"(?<![a-z]){re.escape(key)}(?![a-z])", ql)]
    return q + (" " + " ".join(extra) if extra else "")


def detect_topics(text: str, top_n: int = 2, min_hits: int = 1):
    tl = " " + text.lower() + " "
    scores = Counter()
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            n = len(re.findall(rf"(?<![a-z0-9]){re.escape(kw)}(?:'?s)?(?![a-z0-9])", tl))
            if n:
                scores[topic] += n * (2 if " " in kw else 1)
    return [t for t, s in scores.most_common(top_n) if s >= min_hits]
