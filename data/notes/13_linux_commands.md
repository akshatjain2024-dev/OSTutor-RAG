---
topic: Linux Commands
source: Lab manual - Experiment 1
---
# Basic Linux Commands

## Files and directories
- pwd prints the current working directory.
- ls lists files; ls -l gives a long listing with permissions, ls -a shows hidden files, ls -i shows inode numbers.
- cd dir changes directory; cd .. goes up one level and cd ~ goes home.
- mkdir creates a directory, rmdir removes an empty one, and rm -r removes a directory with its contents.
- cp src dst copies, mv src dst moves or renames, touch file creates an empty file or updates its timestamp.
- cat shows a file, more and less page through it, head and tail show the first or last lines (tail -f follows a growing file).

## Permissions
chmod changes permissions. In numeric form r = 4, w = 2, x = 1, so chmod 755 file gives rwxr-xr-x (owner can do everything, group and others can read and execute). chmod u+x file adds execute permission for the owner. chown changes the owner and umask sets default permissions for new files.

## Searching and text processing
- grep pattern file searches for lines matching a pattern; -i ignores case, -n shows line numbers, -v inverts the match, -c counts matches.
- find /path -name "*.c" finds files by name.
- wc counts lines (-l), words (-w) and characters (-c).
- sort sorts lines, uniq removes adjacent duplicates, cut extracts columns, tr translates characters.
- awk and sed are used for field processing and stream editing.

## Process commands
- ps shows processes; ps -ef or ps aux shows all of them.
- top shows live CPU and memory usage.
- kill PID sends SIGTERM; kill -9 PID sends SIGKILL.
- jobs, fg and bg manage background jobs; a trailing & runs a command in the background.
- nice and renice change a process's priority.

## Redirection and pipes
> redirects output to a file (overwrites), >> appends, < takes input from a file, and 2> redirects standard error. A pipe | sends one command's output into another, for example ps aux | grep bash.

## Getting help
man command opens the manual page. Section 1 is user commands, section 2 is system calls and section 3 is library functions, so man 2 fork shows the system call.
