# Computer Architecture

## 1. Number Systems

### Binary Conversions
| Decimal | Binary | Hexadecimal |
|---------|--------|-------------|
| 0 | 0000 | 0 |
| 1 | 0001 | 1 |
| 2 | 0010 | 2 |
| 10 | 1010 | A |
| 16 | 10000 | 10 |
| 255 | 11111111 | FF |

### Two's Complement (Negative Numbers)
```
+5 = 00000101
-5 = 11111011 (invert bits + 1)
```

## 2. CPU Architecture

### Von Neumann Architecture
- Single shared memory for instructions and data
- Sequential execution
- Bottleneck: memory bandwidth

### Harvard Architecture
- Separate instruction and data memory
- Parallel access
- Used in: DSPs, microcontrollers

### CPU Components
- **ALU**: Arithmetic Logic Unit
- **CU**: Control Unit
- **Registers**: Fast internal storage
- **Cache**: Fast external storage

### Pipeline Stages
```
IF → ID → EX → MEM → WB
│    │    │    │     │
│    │    │    │     └─ Write Back
│    │    │    └─────── Memory Access
│    │    └──────────── Execute
│    └───────────────── Instruction Decode
└────────────────────── Instruction Fetch
```

## 3. Memory Hierarchy

```
Registers      │ ~1 ns    │ ~KB
L1 Cache       │ ~2 ns    │ ~64KB
L2 Cache       │ ~10 ns   │ ~256KB
L3 Cache       │ ~30 ns   │ ~8MB
Main Memory    │ ~100 ns  │ ~GB
SSD            │ ~100 μs  │ ~TB
HDD            │ ~10 ms   │ ~TB
```

### Cache Mapping
- **Direct**: Each block maps to exactly one cache line
- **Associative**: Any block can go anywhere
- **Set-Associative**: Compromise between direct and associative

### Cache Replacement Policies
- **LRU**: Least Recently Used
- **FIFO**: First In First Out
- **Random**: Random replacement

## 4. Instruction Set Architecture (ISA)

### CISC vs RISC
| Feature | CISC | RISC |
|---------|------|------|
| Instructions | Many, complex | Few, simple |
| Instruction length | Variable | Fixed |
| Execution time | Variable | Single cycle |
| Registers | Few | Many |
| Examples | x86, x86-64 | ARM, MIPS, RISC-V |

### Addressing Modes
- **Immediate**: Operand in instruction
- **Direct**: Address in instruction
- **Indirect**: Address of address
- **Register**: Operand in register
- **Register Indirect**: Address in register
- **Indexed**: Base + offset

## 5. Parallelism

### Flynn's Taxonomy
| Type | Description | Example |
|------|-------------|---------|
| SISD | Single Instruction, Single Data | Sequential CPU |
| SIMD | Single Instruction, Multiple Data | GPU, SSE/AVX |
| MISD | Multiple Instruction, Single Data | Rare |
| MIMD | Multiple Instruction, Multiple Data | Multi-core CPU |

### Multi-core Architecture
- Shared memory multiprocessing
- Cache coherence protocols (MESI)
- NUMA (Non-Uniform Memory Access)

### GPU Architecture
- Thousands of small cores
- Optimized for parallel computation
- CUDA, OpenCL programming models

## 6. I/O Systems

### I/O Methods
- **Programmed I/O**: CPU polls device
- **Interrupt-driven**: Device interrupts CPU
- **DMA**: Direct Memory Access

### Bus Architecture
- **Data Bus**: Transfers data
- **Address Bus**: Specifies memory location
- **Control Bus**: Control signals

## 7. Performance Metrics

### CPU Performance Equation
```
CPU Time = Instructions × CPI × Clock Period

CPI = Cycles Per Instruction
Clock Period = 1 / Clock Frequency
```

### Amdahl's Law
```
Speedup = 1 / ((1 - P) + P/S)

P = Parallel portion
S = Speedup of parallel portion
```

## 8. Modern Architectures

### ARM Architecture
- RISC-based
- Power efficient
- Used in: Mobile devices, Apple Silicon, AWS Graviton

### RISC-V
- Open-source ISA
- Modular extensions
- Growing ecosystem

### x86-64
- CISC architecture
- Backward compatible
- Dominant in desktop/server
