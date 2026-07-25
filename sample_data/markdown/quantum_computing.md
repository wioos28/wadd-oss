# Quantum Computing

## 1. Fundamentals

### Classical vs Quantum
| Feature | Classical | Quantum |
|---------|-----------|---------|
| Bit | 0 or 1 | Superposition of 0 and 1 |
| Processing | Sequential/Parallel | Quantum parallelism |
| Error Rate | Low | High (currently) |
| Maturity | Mature | Experimental |

### Qubits
- Basic unit of quantum information
- Can be 0, 1, or superposition
- Represented as: |ψ⟩ = α|0⟩ + β|1⟩
- |α|² + |β|² = 1 (normalization)

## 2. Quantum Properties

### Superposition
```
Classical: 0 OR 1
Quantum:   0 AND 1 simultaneously

|ψ⟩ = (1/√2)|0⟩ + (1/√2)|1⟩
```

### Entanglement
- Two qubits correlated
- Measuring one affects the other
- "Spooky action at a distance"

### Interference
- Probability amplitudes can cancel
- Used to amplify correct answers
- Suppress wrong answers

## 3. Quantum Gates

### Single-Qubit Gates
| Gate | Matrix | Effect |
|------|--------|--------|
| X (NOT) | [[0,1],[1,0]] | Bit flip |
| Z | [[1,0],[0,-1]] | Phase flip |
| H (Hadamard) | 1/√2 [[1,1],[1,-1]] | Superposition |
| Y | [[0,-i],[i,0]] | Bit + phase flip |

### Multi-Qubit Gates
| Gate | Effect |
|------|--------|
| CNOT | Controlled NOT |
| SWAP | Swap two qubits |
| Toffoli | Controlled-controlled NOT |

### Circuit Model
```
q0: ──H──●──
          │
q1: ──────⊕──
```

## 4. Quantum Algorithms

### Shor's Algorithm
- Integer factorization
- Exponential speedup over classical
- Threatens RSA encryption
- Runs on: O((log N)³) time

### Grover's Algorithm
- Unstructured search
- Quadratic speedup: O(√N) vs O(N)
- Applications: Database search, optimization

### Quantum Walk
- Quantum version of random walk
- Applications: Graph problems, search

## 5. Quantum Computing Models

### Circuit Model
- Most common
- Quantum gates applied sequentially
- Used by: IBM, Google

### Adiabatic
- Start with easy Hamiltonian
- Slowly evolve to problem Hamiltonian
- Used by: D-Wave

### Measurement-Based
- Start with entangled state
- Perform measurements
- Cluster state computing

## 6. Quantum Hardware

### Physical Implementations
| Technology | Companies | Pros/Cons |
|------------|-----------|-----------|
| Superconducting | IBM, Google, Rigetti | Fast, but needs cooling |
| Trapped Ion | IonQ, Honeywell | Stable, but slow |
| Photonic | Xanadu, PsiQuantum | Room temp, but lossy |
| Topological | Microsoft | Theoretical, robust |

### Error Correction
- **Surface Code**: Most promising
- **Physical Qubits**: ~1000s
- **Logical Qubits**: Need ~1000 physical per logical

## 7. Quantum Software

### Programming Languages
- **Qiskit**: IBM (Python)
- **Cirq**: Google (Python)
- **Q#**: Microsoft
- **PennyLane**: Xanadu (ML focus)

### Example (Qiskit)
```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)           # Hadamard on q0
qc.cx(0, 1)       # CNOT
qc.measure([0,1], [0,1])

# Execute on simulator
from qiskit import Aer
simulator = Aer.get_backend('qasm_simulator')
result = execute(qc, simulator).result()
```

## 8. Applications

### Current Applications
- Quantum chemistry simulation
- Optimization problems
- Machine learning (quantum ML)

### Potential Applications
- Drug discovery
- Materials science
- Financial modeling
- Cryptography (breaking and quantum-safe)
- Climate modeling

## 9. Quantum Threats & Post-Quantum Cryptography

### Threats
- Shor's algorithm breaks RSA, ECC
- Grover's weakens symmetric crypto
- Timeline: 10-20 years?

### Post-Quantum Algorithms
| Type | Algorithm | Status |
|------|-----------|--------|
| Lattice | CRYSTALS-Kyber | NIST standard |
| Hash-based | SPHINCS+ | NIST standard |
| Code-based | Classic McEliece | NIST candidate |
| Multivariate | Rainbow | NIST candidate |

## 10. Current Limitations

- Decoherence: Qubits lose state quickly
- Error rates: ~0.1-1% per gate
- Scalability: Difficult to scale
- Temperature: Most need near absolute zero
- Programming: No mature debugging tools
