# Compiler Theory

## 1. Compilation Phases

```
Source Code
    │
    ▼
┌─────────────────┐
│  Lexical Analysis│ → Tokens
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Syntax Analysis  │ → AST
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Semantic Analysis│ → Annotated AST
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Optimization     │ → Optimized IR
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Code Generation  │ → Target Code
└─────────────────┘
```

## 2. Lexical Analysis

### Regular Expressions
```
a       → character
a|b     → alternation
ab      → concatenation
a*      → zero or more
a+      → one or more
a?      → zero or one
[a-z]   → character class
[^a]    → negation
```

### Finite Automata
- **DFA**: Deterministic Finite Automaton
- **NFA**: Nondeterministic Finite Automata
- Thompson's construction: Regex → NFA
- Subset construction: NFA → DFA

### Token Types
- Keywords: `if`, `while`, `return`
- Identifiers: variable names
- Literals: numbers, strings
- Operators: `+`, `-`, `*`
- Delimiters: `(`, `)`, `{`, `}`

## 3. Syntax Analysis

### Context-Free Grammars (CFG)
```
E → E + T | T
T → T * F | F
F → ( E ) | id
```

### Parse Trees
```
      E
     /|\
    E + T
    |   |
    T   F
    |   |
    F   id
    |
    id
```

### Parsing Algorithms

#### Top-Down
- **Recursive Descent**: Simple, hand-written
- **LL Parsing**: Table-driven, leftmost derivation

#### Bottom-Up
- **Shift-Reduce**: Stack-based
- **LR Parsing**: More powerful than LL
- **LALR(1)**: Used in yacc/bison

### AST (Abstract Syntax Tree)
```python
# Expression: a + b * c
BinOp(
    left=BinOp(
        left=Var('a'),
        op='+',
        right=Var('b')
    ),
    op='*',
    right=Var('c')
)
```

## 4. Semantic Analysis

### Type Checking
- Static vs Dynamic typing
- Type inference
- Type promotion

### Symbol Table
```python
class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # Stack of scopes
    
    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        self.scopes.pop()
    
    def define(self, name, symbol):
        self.scopes[-1][name] = symbol
    
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
```

### Type Systems
- **Strong vs Weak**: Type enforcement strictness
- **Static vs Dynamic**: When types are checked
- **Nominal vs Structural**: How types relate

## 5. Intermediate Representations (IR)

### Three-Address Code
```
t1 = a + b
t2 = t1 * c
d = t2
```

### SSA (Static Single Assignment)
- Each variable assigned exactly once
- Makes optimization easier
- Phi functions for control flow merge

### Control Flow Graph
```
    [Entry]
        │
        ▼
    [Block 1]
        │
    ┌───┴───┐
    ▼       ▼
[Block 2] [Block 3]
    │       │
    └───┬───┘
        ▼
    [Block 4]
        │
        ▼
    [Exit]
```

## 6. Optimization

### Local Optimizations
- Constant folding
- Constant propagation
- Dead code elimination
- Common subexpression elimination

### Loop Optimizations
- Loop invariant code motion
- Loop unrolling
- Loop fusion/fission
- Strength reduction

### Global Optimizations
- Data flow analysis
- Global value numbering
- Interprocedural optimization

### SSA-Based Optimizations
- Constant propagation
- Dead code elimination
- Register allocation

## 7. Code Generation

### Instruction Selection
- Tree patterns
- Dynamic programming

### Register Allocation
- Graph coloring
- Linear scan

### Instruction Scheduling
- Avoid pipeline stalls
- Reorder instructions

## 8. Compiler Tools

### Lexer Generators
- **Lex/Flex**: Regular expression → DFA

### Parser Generators
- **Yacc/Bison**: Grammar → Parser
- **ANTLR**: LL(*) parser generator
- **PEG Parsers**: Parsing Expression Grammar

### LLVM
- Modular compiler infrastructure
- Multiple frontends (Clang, Swift, Rust)
- Rich optimization passes
