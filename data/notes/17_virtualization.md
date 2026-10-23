---
topic: Virtualization
source: Class notes - Unit 6
---
# Virtualization

Virtualization lets one physical machine run several isolated operating systems at the same time. Each guest OS runs inside a virtual machine (VM) and believes it has its own CPU, memory and devices.

## Hypervisor (Virtual Machine Monitor)
The hypervisor creates and manages VMs and shares the real hardware among them.
- Type 1 (bare-metal) hypervisors run directly on the hardware with no host OS underneath. Examples: VMware ESXi, Xen, Microsoft Hyper-V. Linux KVM turns the Linux kernel itself into a type 1 hypervisor. These are used in data centres and clouds.
- Type 2 (hosted) hypervisors run as an application on top of a normal host OS. Examples: Oracle VirtualBox, VMware Workstation. Easier to install and good for students and developers, but with more overhead.

## How guest kernels are handled
A guest kernel expects to run privileged instructions, but it actually runs in a less privileged mode. Approaches:
- Trap-and-emulate: privileged instructions from the guest trap to the hypervisor, which emulates them.
- Binary translation: the hypervisor scans guest kernel code and rewrites problem instructions on the fly (used by early VMware on x86).
- Hardware-assisted virtualization: Intel VT-x and AMD-V add a new CPU mode for guests, and nested/extended page tables let the hardware translate guest addresses efficiently.
- Paravirtualization: the guest OS is modified to know it is virtualized and calls the hypervisor directly (hypercalls) instead of using privileged instructions. Xen popularised this. It is faster but needs a modified guest.

## Benefits
Isolation between guests, running different operating systems on one machine, server consolidation (fewer physical servers), snapshots and easy backup, and live migration of a running VM to another host.

## Containers
Containers (Docker, LXC) are lighter than VMs. All containers share the host's kernel; there is no guest OS. Isolation comes from two Linux kernel features:
- Namespaces give each container its own view of process IDs, network interfaces, mount points, users and hostname.
- Control groups (cgroups) limit and account for CPU, memory and I/O used by a group of processes.
Containers start in seconds and use little memory, but they can only run programs for the same kernel type, and isolation is weaker than with full VMs.

## VM vs container in one line
A VM virtualizes the hardware and runs a whole OS; a container virtualizes the OS and runs just the application with its libraries.
