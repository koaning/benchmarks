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

## Motivation

Python is often criticized for being slow with recursion compared to other functional programming languages. This benchmark quantifies the performance differences across multiple iteration and accumulation strategies.

## Key Findings

**Math formula is ~170,000x faster than recursion!**

Complete ranking (fastest to slowest):
1. **Math formula (Gauss)**: 0.0005ms ⚡ (baseline)
2. **sum(range(n))**: 1.01ms (1,838x slower)
3. **sum(generator)**: 2.57ms (4,677x slower)
4. **For-loop**: 2.68ms (4,873x slower)
5. **sum([list comp])**: 3.69ms (6,714x slower)
6. **itertools.accumulate()**: 4.52ms (8,231x slower)
7. **functools.reduce()**: 4.99ms (9,086x slower)
8. **While loop**: 5.56ms (10,124x slower)
9. **Recursion**: 93.41ms (170,027x slower) 🐌

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
   Mean: 0.0005ms ± 0.0003ms
   Slowdown: 1.00x

2. sum(range(n))
   Mean: 1.0098ms ± 0.0111ms
   Slowdown: 1838.00x

3. sum(generator)
   Mean: 2.5697ms ± 0.0517ms
   Slowdown: 4677.26x

4. For-loop
   Mean: 2.6774ms ± 0.0343ms
   Slowdown: 4873.37x

5. sum([list comp])
   Mean: 3.6889ms ± 1.7269ms
   Slowdown: 6714.49x

6. itertools.accumulate()
   Mean: 4.5220ms ± 0.8788ms
   Slowdown: 8230.79x

7. functools.reduce()
   Mean: 4.9917ms ± 0.2486ms
   Slowdown: 9085.70x

8. While loop
   Mean: 5.5619ms ± 0.0774ms
   Slowdown: 10123.61x

9. Recursion
   Mean: 93.4129ms ± 8.4918ms
   Slowdown: 170027.14x
```

## Takeaways

### General Performance Insights

1. **Think mathematically first**: If there's a closed-form formula (like Gauss's formula), use it! It's orders of magnitude faster.
2. **Built-in functions are optimized**: `sum(range(n))` is surprisingly fast - faster than hand-written loops!
3. **For-loops are still good**: Traditional for-loops perform well and are readable
4. **While loops are slower**: While loops have more overhead than for-loops in Python
5. **Avoid recursion for iteration**: Recursion is dramatically slower (93ms vs 0.0005ms for math formula)

### Why is sum(range(n)) faster than for-loops?

The built-in `sum()` function with `range()` is implemented in C and highly optimized. It beats hand-written Python for-loops because:
- Less Python bytecode interpretation overhead
- Optimized C implementation
- No manual accumulator management

### When to use each approach

- **Math formula**: When a closed-form solution exists (always the fastest!)
- **sum(range())**: For simple sequential sums - clean and fast
- **Generator expressions**: Memory-efficient for large ranges
- **For-loops**: When you need complex logic or side effects
- **While loops**: Only when the iteration condition is truly dynamic
- **Recursion**: Avoid for iteration; use for tree/graph traversal where appropriate
- **reduce/accumulate**: Rarely - only when the functional style clarifies intent

### Recursion in Python

- **Massive overhead**: 170,000x slower than the math formula, 35x slower than for-loops
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

The recursive implementation uses an accumulator pattern but still suffers from Python's lack of tail-call optimization.
