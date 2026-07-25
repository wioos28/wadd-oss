# Operating Systems

## 1. Process Management

### Process vs Thread
| Feature | Process | Thread |
|---------|---------|--------|
| Memory | Separate address space | Shared address space |
| Creation | Expensive | Cheap |
| Communication | IPC (inter-process) | Direct (shared memory) |
| Failure | Isolated | Affects all threads |

### Process States
```
New → Ready → Running → Terminated
          ↑         ↓
          ← Blocked ←
```

### Scheduling Algorithms
- **FCFS**: First Come First Served
- **SJF**: Shortest Job First
- **Round Robin**: Time slicing
- **Priority**: Based on priority
- **MLFQ**: Multi-Level Feedback Queue

## 2. Memory Management

### Virtual Memory
- Each process has virtual address space
- Page table maps virtual → physical
- Enables memory protection and isolation

### Paging
- Fixed-size blocks (pages)
- No external fragmentation
- Page table overhead

### Segmentation
- Variable-size segments
- Logical divisions (code, data, stack)
- External fragmentation possible

### Page Replacement Algorithms
- **FIFO**: First In First Out
- **LRU**: Least Recently Used
- **Optimal**: Replace page not used longest time (theoretical)
- **Clock**: Approximation of LRU

## 3. File Systems

### Types
- **FAT**: Simple, used in USB drives
- **NTFS**: Windows, supports permissions
- **ext4**: Linux default
- **APFS**: Apple, optimized for SSD
- **ZFS**: Advanced, copy-on-write

### Inodes
- Store file metadata (owner, permissions, timestamps)
- Point to data blocks
- No filename stored in inode

### Journaling
- Log changes before applying
- Enables fast recovery after crash
- Used in ext3/4, NTFS, APFS

## 4. I/O Management

### I/O Methods
- **Programmed I/O**: CPU polls device
- **Interrupt-driven**: Device interrupts CPU
- **DMA**: Direct Memory Access, no CPU involvement

### Buffering
- Temporary storage for data in transit
- Handles speed mismatch between devices

### Spooling
- Simultaneous Peripheral Operations
- Queue print jobs, etc.

## 5. Concurrency

### Synchronization
- **Mutex**: Mutual exclusion
- **Semaphore**: Counting resource access
- **Monitor**: High-level synchronization construct
- **Condition Variables**: Wait/notify pattern

### Deadlock
**Conditions (all must hold):**
1. Mutual exclusion
2. Hold and wait
3. No preemption
4. Circular wait

**Prevention:**
- Break one condition
- Resource ordering
- Banker's algorithm

### Race Condition
```
Thread 1: read x
Thread 2: read x
Thread 1: write x + 1
Thread 2: write x + 1  // Lost update!
```

**Solution:** Locks, atomic operations

## 6. System Calls

### Categories
- **Process**: fork, exec, wait, exit
- **File**: open, read, write, close
- **Device**: ioctl, read, write
- **Information**: getpid, alarm, sleep
- **Communication**: pipe, shmget, mmap
- **Protection**: chmod, chown

### fork() Example
```c
pid_t pid = fork();
if (pid == 0) {
    // Child process
    execl("/bin/ls", "ls", NULL);
} else if (pid > 0) {
    // Parent process
    wait(NULL);
}
```

## 7. Security

### Protection Mechanisms
- **Access Control Lists (ACL)**
- **Capabilities**
- **Address Space Layout Randomization (ASLR)**
- **Data Execution Prevention (DEP)**
- **Stack canaries**

### Authentication
- Passwords (hashed, salted)
- Biometrics
- Multi-factor authentication
- Kerberos

## 8. Linux Internals

### Kernel Components
- **Process Scheduler**
- **Memory Manager**
- **Virtual File System (VFS)**
- **Network Stack**
- **Device Drivers**

### System Calls in Linux
```c
// File operations
open(), read(), write(), close()

// Process operations
fork(), exec(), wait(), exit()

// Memory operations
mmap(), brk(), sbrk()
```

### /proc Filesystem
- Virtual filesystem for process info
- `/proc/cpuinfo` - CPU information
- `/proc/meminfo` - Memory information
- `/proc/[pid]/` - Per-process info
