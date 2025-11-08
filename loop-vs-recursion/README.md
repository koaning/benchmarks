# Loop vs Recursion Counting Benchmark

This benchmark compares the performance of various approaches to summing numbers from 0 to 99,999 in Python:
1. **For-loop (imperative)**: Traditional iterative summing
2. **While loop**: Classic while-loop iteration
3. **Recursion (functional)**: Functional recursive approach
4. **sum(range(n))**: Built-in sum with range
5. **sum(generator)**: Sum with generator expression
6. **sum([list comp])**: Sum with list comprehension
7. **functools.reduce()**: Functional reduce approach
8. **itertools.accumulate()**: Accumulation with itertools
9. **Math formula (Gauss)**: Direct calculation using Gauss's formula: n*(n-1)/2
10. **numpy.sum()**: NumPy's optimized sum function

## Motivation

Python is often criticized for being slow with recursion compared to other functional programming languages. This benchmark quantifies the performance differences across multiple iteration and accumulation strategies.

## Key Findings

**Math formula is ~180,000x faster than recursion!**

Complete ranking (fastest to slowest):
1. **Math formula (Gauss)**: 0.0005ms ⚡ (baseline)
2. **numpy.sum()**: 0.092ms (179x slower) - NumPy is blazing fast!
3. **sum(range(n))**: 1.06ms (2,053x slower)
4. **For-loop**: 2.83ms (5,490x slower)
5. **sum(generator)**: 3.17ms (6,156x slower)
6. **itertools.accumulate()**: 4.40ms (8,554x slower)
7. **sum([list comp])**: 4.75ms (9,222x slower)
8. **functools.reduce()**: 4.83ms (9,381x slower)
9. **While loop**: 5.85ms (11,367x slower)
10. **Recursion**: 93.05ms (180,753x slower) 🐌

## Why is Recursion So Slow in Python?

1. **No Tail Call Optimization**: Python does not optimize tail-recursive calls, so each recursive call consumes stack space
2. **Function Call Overhead**: Each recursive call involves pushing a new frame onto the call stack
3. **CPython Optimization**: Python's for-loops are highly optimized in the CPython implementation
4. **Recursion Limit**: Python's default recursion limit is ~1000, requiring manual adjustment for deep recursion

## Running the Benchmarks

### Simple benchmark (loop vs recursion only)
```bash
python benchmark.py [iterations]
```

### Comprehensive benchmark (all 9 methods)
```bash
python benchmark_all_methods.py [iterations]
```

Default: 5 iterations

Example:
```bash
python benchmark_all_methods.py 10  # Run with 10 iterations
```

## Results

Both benchmarks automatically increase Python's recursion limit from 1,000 to 101,000 to handle deep recursion.

### Comprehensive Benchmark Results

```
================================================================================
RESULTS (sorted by speed)
================================================================================

1. Math formula (Gauss)
   Mean: 0.0005ms ± 0.0004ms
   Slowdown: 1.00x

2. numpy.sum()
   Mean: 0.0924ms ± 0.0751ms
   Slowdown: 179.40x

3. sum(range(n))
   Mean: 1.0568ms ± 0.0064ms
   Slowdown: 2052.78x

4. For-loop
   Mean: 2.8260ms ± 0.1689ms
   Slowdown: 5489.50x

5. sum(generator)
   Mean: 3.1691ms ± 0.6091ms
   Slowdown: 6156.06x

6. itertools.accumulate()
   Mean: 4.4036ms ± 0.4350ms
   Slowdown: 8553.99x

7. sum([list comp])
   Mean: 4.7473ms ± 2.0509ms
   Slowdown: 9221.63x

8. functools.reduce()
   Mean: 4.8294ms ± 0.0974ms
   Slowdown: 9381.20x

9. While loop
   Mean: 5.8515ms ± 0.3624ms
   Slowdown: 11366.57x

10. Recursion
   Mean: 93.0515ms ± 4.6025ms
   Slowdown: 180752.77x
```

## Takeaways

### General Performance Insights

1. **Think mathematically first**: If there's a closed-form formula (like Gauss's formula), use it! It's orders of magnitude faster.
2. **NumPy is incredibly fast**: `numpy.sum()` is 11x faster than `sum(range(n))` and 30x faster than for-loops!
3. **Built-in functions are optimized**: `sum(range(n))` is surprisingly fast - faster than hand-written loops!
4. **For-loops are still good**: Traditional for-loops perform well and are readable
5. **While loops are slower**: While loops have more overhead than for-loops in Python
6. **Avoid recursion for iteration**: Recursion is dramatically slower (93ms vs 0.0005ms for math formula)

### Why is numpy.sum() so fast?

NumPy is optimized for numerical operations and beats everything except the math formula:
- **Vectorized operations**: Works on entire arrays at once using optimized C/Fortran code
- **SIMD instructions**: Uses CPU vector instructions for parallel computation
- **Memory efficiency**: Contiguous memory layout for cache-friendly access
- **No Python overhead**: Minimal Python interpreter interaction during computation

NumPy is ~11x faster than `sum(range())` and ~30x faster than for-loops!

### Why is sum(range(n)) faster than for-loops?

The built-in `sum()` function with `range()` is implemented in C and highly optimized. It beats hand-written Python for-loops because:
- Less Python bytecode interpretation overhead
- Optimized C implementation
- No manual accumulator management

### When to use each approach

- **Math formula**: When a closed-form solution exists (always the fastest!)
- **NumPy**: For numerical operations on arrays - extremely fast and powerful
- **sum(range())**: For simple sequential sums - clean and fast
- **Generator expressions**: Memory-efficient for large ranges
- **For-loops**: When you need complex logic or side effects
- **While loops**: Only when the iteration condition is truly dynamic
- **Recursion**: Avoid for iteration; use for tree/graph traversal where appropriate
- **reduce/accumulate**: Rarely - only when the functional style clarifies intent

### Recursion in Python

- **Massive overhead**: 180,000x slower than the math formula, 1,000x slower than numpy, 33x slower than for-loops
- **Not tail-call optimized**: Each call adds stack overhead
- **Limited recursion depth**: Default limit of 1,000 calls
- **Use sparingly**: Only for naturally recursive problems (trees, graphs, divide-and-conquer)

## Implementation Notes

### Sample Implementations

**For-loop:**
```python
def for_loop_sum(n: int) -> int:
    total = 0
    for i in range(n):
        total += i
    return total
```

**sum(range()) - The Pythonic winner:**
```python
def sum_range(n: int) -> int:
    return sum(range(n))
```

**Recursion (slowest):**
```python
def recursive_sum(n: int, current: int = 0, total: int = 0) -> int:
    if current >= n:
        return total
    return recursive_sum(n, current + 1, total + current)
```

**Math formula (fastest):**
```python
def math_formula_sum(n: int) -> int:
    return (n * (n - 1)) // 2  # Gauss's formula
```

**NumPy (second fastest for actual computation):**
```python
import numpy as np

def numpy_sum(n: int) -> int:
    return int(np.sum(np.arange(n)))
```

The recursive implementation uses an accumulator pattern but still suffers from Python's lack of tail-call optimization. NumPy's vectorized operations make it ideal for numerical computations on large datasets.
