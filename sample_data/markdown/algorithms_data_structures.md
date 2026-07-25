# Algorithms & Data Structures

## 1. Big O Notation

### Time Complexity
| Notation | Name | Example |
|----------|------|---------|
| O(1) | Constant | Array access, Hash lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Linear search |
| O(n log n) | Linearithmic | Merge sort, Quick sort |
| O(n²) | Quadratic | Bubble sort, Selection sort |
| O(2ⁿ) | Exponential | Recursive Fibonacci |
| O(n!) | Factorial | Permutations |

### Space Complexity
- **O(1)**: In-place algorithms
- **O(n)**: Linear data structures
- **O(n²)**: 2D arrays, matrices

## 2. Data Structures

### Arrays
```python
# Static array
arr = [1, 2, 3, 4, 5]

# Access: O(1)
# Search: O(n)
# Insert: O(n)
# Delete: O(n)
```

### Linked Lists
```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

# Singly linked: O(n) access, O(1) insert/delete at head
# Doubly linked: O(n) access, O(1) insert/delete
```

### Stacks
- LIFO (Last In, First Out)
- Operations: push, pop, peek, isEmpty
- Use: Function calls, undo, backtracking

### Queues
- FIFO (First In, First Out)
- Operations: enqueue, dequeue, peek
- Use: BFS, task scheduling

### Hash Tables
```python
# Average case
# Access: O(1)
# Insert: O(1)
# Delete: O(1)

# Worst case (collisions)
# Access: O(n)
```

### Trees

#### Binary Search Tree (BST)
```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

# Search: O(log n) average, O(n) worst
# Insert: O(log n) average
```

#### AVL Tree
- Self-balancing BST
- Height difference ≤ 1
- Guarantees O(log n)

#### Red-Black Tree
- Self-balancing BST
- Used in: Java TreeMap, C++ std::map

#### Heap
- Complete binary tree
- Max-heap: Parent ≥ children
- Min-heap: Parent ≤ children
- Use: Priority queues

### Graphs
```python
# Adjacency list
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A'],
    'D': ['B']
}

# Adjacency matrix
# 2D array, good for dense graphs
```

## 3. Sorting Algorithms

### Comparison Sorts
| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | No |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |

### Non-Comparison Sorts
| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| Counting Sort | O(n+k) | O(k) | Small range integers |
| Radix Sort | O(nk) | O(n+k) | Fixed-length strings |
| Bucket Sort | O(n) average | O(n) | Uniform distribution |

## 4. Searching Algorithms

### Linear Search
```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
# Time: O(n)
```

### Binary Search
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
# Time: O(log n)
```

## 5. Graph Algorithms

### BFS (Breadth-First Search)
```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
# Time: O(V + E)
```

### DFS (Depth-First Search)
```python
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    return visited
# Time: O(V + E)
```

### Dijkstra's Algorithm
- Shortest path in weighted graph
- Time: O((V + E) log V) with priority queue
- Use: Navigation, network routing

### A* Search
- Dijkstra + heuristic
- Faster for single destination
- Use: Game pathfinding, maps

## 6. Dynamic Programming

### Key Concepts
1. Optimal substructure
2. Overlapping subproblems
3. Memoization or tabulation

### Classic Problems
- **Fibonacci**: O(n) time, O(n) space
- **Knapsack**: O(nW) time, O(nW) space
- **Longest Common Subsequence**: O(mn) time, O(mn) space
- **Edit Distance**: O(mn) time, O(mn) space

## 7. Greedy Algorithms

### Properties
1. Greedy choice property
2. Optimal substructure

### Examples
- Activity selection
- Huffman coding
- Kruskal's/Prim's MST
- Dijkstra's shortest path

## 8. Recursion & Backtracking

### Recursion
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

### Backtracking
- Build solution incrementally
- Remove solutions that fail
- Examples: N-Queens, Sudoku, Maze solving
