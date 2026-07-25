# Mathematics Fundamentals

## 1. Linear Algebra

### Vectors
```
v = [v1, v2, ..., vn]

Operations:
- Addition: u + v = [u1+v1, u2+v2, ...]
- Scalar multiplication: c * v = [c*v1, c*v2, ...]
- Dot product: u · v = Σ(ui * vi)
- Cross product: u × v (3D only)
```

### Matrices
```
A = [[a11, a12],
     [a21, a22]]

Operations:
- Addition: A + B
- Multiplication: C = A × B
- Transpose: A^T
- Inverse: A^(-1)
```

### Eigenvalues & Eigenvectors
```
Av = λv

A: Square matrix
λ: Eigenvalue
v: Eigenvector

Applications: PCA, Google PageRank, Quantum mechanics
```

## 2. Calculus

### Derivatives
```
f'(x) = lim(h→0) [f(x+h) - f(x)] / h

Rules:
- Power: d/dx[x^n] = nx^(n-1)
- Product: (fg)' = f'g + fg'
- Chain: (f(g(x)))' = f'(g(x)) * g'(x)
```

### Integrals
```
∫f(x)dx = F(x) + C

Fundamental Theorem:
∫[a,b] f(x)dx = F(b) - F(a)
```

### Multivariable Calculus
- Partial derivatives
- Gradient: ∇f = [∂f/∂x, ∂f/∂y, ∂f/∂z]
- Divergence: ∇ · F
- Curl: ∇ × F

## 3. Probability

### Basic Probability
```
P(A) = Number of favorable outcomes / Total outcomes

Rules:
- P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
- P(A|B) = P(A ∩ B) / P(B)
```

### Bayes' Theorem
```
P(A|B) = P(B|A) × P(A) / P(B)

Applications:
- Medical diagnosis
- Spam filtering
- Machine learning
```

### Distributions
| Distribution | Use Case |
|--------------|----------|
| Bernoulli | Binary outcome |
| Binomial | Number of successes |
| Poisson | Rare events |
| Normal (Gaussian) | Natural phenomena |
| Uniform | Equal probability |

## 4. Statistics

### Descriptive Statistics
- Mean: μ = Σxi / n
- Variance: σ² = Σ(xi - μ)² / n
- Standard Deviation: σ = √variance
- Median: Middle value
- Mode: Most frequent value

### Hypothesis Testing
```
1. Null hypothesis (H0)
2. Alternative hypothesis (H1)
3. Choose significance level (α)
4. Calculate test statistic
5. Determine p-value
6. Reject or fail to reject H0
```

### Confidence Intervals
```
CI = x̄ ± z × (σ/√n)

x̄: Sample mean
z: Z-score
σ: Standard deviation
n: Sample size
```

## 5. Discrete Mathematics

### Set Theory
```
A ∪ B: Union
A ∩ B: Intersection
A \ B: Difference
A × B: Cartesian product
|A|: Cardinality
```

### Graph Theory
```
G = (V, E)

V: Vertices (nodes)
E: Edges (connections)

Types:
- Directed/Undirected
- Weighted/Unweighted
- Cyclic/Acyclic
```

### Combinatorics
```
Permutations: P(n,k) = n! / (n-k)!
Combinations: C(n,k) = n! / (k!(n-k)!)
```

## 6. Number Theory

### Modular Arithmetic
```
a ≡ b (mod n) means n | (a - b)

Properties:
- (a + b) mod n = [(a mod n) + (b mod n)] mod n
- (a × b) mod n = [(a mod n) × (b mod n)] mod n
```

### Prime Numbers
- Fundamental theorem of arithmetic
- Prime factorization
- Applications: RSA encryption

### Euler's Totient Function
```
φ(n) = n × ∏(1 - 1/p) for all prime factors p of n
```

## 7. Optimization

### Gradient Descent
```
θ = θ - α × ∇f(θ)

θ: Parameters
α: Learning rate
∇f: Gradient
```

### Convex Optimization
- Local minimum = Global minimum
- Efficient algorithms exist
- Applications: ML, control theory

### Lagrange Multipliers
```
∇f = λ × ∇g

Optimize f subject to constraint g = 0
```

## 8. Information Theory

### Entropy
```
H(X) = -Σ p(x) × log₂(p(x))

Measures uncertainty/information content
```

### Mutual Information
```
I(X;Y) = H(X) + H(Y) - H(X,Y)

Measures dependence between variables
```

### KL Divergence
```
D_KL(P||Q) = Σ p(x) × log(p(x)/q(x))

Measures difference between distributions
```
