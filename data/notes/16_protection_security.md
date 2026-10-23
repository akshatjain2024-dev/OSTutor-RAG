---
topic: Protection and Security
source: Class notes - Unit 6
---
# Protection and Security

Protection is about controlling which processes and users can access which resources inside the system. Security is broader: it is about defending the system against attacks from outside and inside, and it depends on protection mechanisms working correctly.

## Principle of least privilege
Programs, users and system components should be given only the privileges they need to do their job, and only for as long as they need them. If a program is compromised, the damage is limited to what it was allowed to do.

## Domains and the access matrix
A protection domain is a set of (object, rights) pairs; a process runs inside a domain. The access matrix is the general model: rows are domains, columns are objects (files, printers, other domains), and each entry lists the rights, such as read, write or execute. The matrix is sparse, so real systems store it in one of two ways:
- Access control lists (ACLs): stored per object (per column). Each file keeps a list of which users or groups can do what. Easy to see who can access an object and to revoke access.
- Capability lists: stored per domain (per row). Each process holds a list of unforgeable tokens for the objects it may use. Easy to see what a process can do, but revocation is harder.
UNIX permissions (owner, group, others with rwx) are a simplified ACL.

## setuid and setgid
If the setuid bit is set on an executable, it runs with the privileges of the file's owner rather than the user who started it. For example, passwd is owned by root and has setuid set, so ordinary users can change their own password entry. A setuid program with a bug is dangerous because the bug runs with root privileges.

## Program threats
- Trojan horse: a program that looks useful but secretly misuses the privileges of the user who runs it.
- Trap door (back door): a hidden way into a program or system left by its designer that bypasses normal authentication.
- Logic bomb: code that does damage only when a certain condition occurs, such as a date.
- Buffer overflow (stack overflow): a program copies more input into a buffer than it can hold, overwriting adjacent memory such as the saved return address. The attacker can make the function return into their own code. Defences include bounds checking, non-executable stacks, stack canaries and address space layout randomization (ASLR).

## System and network threats
- Virus: code that attaches itself to legitimate programs and spreads when they run.
- Worm: a standalone program that spreads itself over the network without user action.
- Denial of service: overloading a system so legitimate users can't use it.
- Port scanning: probing a machine to find open services to attack.

## Authentication
Passwords should never be stored in plain text. The OS stores a salted hash: a random salt is combined with the password and passed through a one-way hash function, and only the salt and hash are kept (in Linux, in /etc/shadow, readable only by root). At login the same computation is repeated and the results compared. Salting stops attackers from using precomputed tables. Stronger schemes add one-time passwords or two-factor authentication.
