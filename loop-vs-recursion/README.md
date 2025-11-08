# Loop vs Recursion Counting Benchmark

This benchmark compares the performance of counting to 100,000 using two different approaches in Python:
1. **For-loop (imperative)**: Traditional iterative counting
2. **Recursion (functional)**: Functional recursive counting

## Motivation

Python is often criticized for being slow with recursion compared to other functional programming languages. This benchmark quantifies the performance difference between imperative and functional approaches for a simple counting task.

## Key Findings

**Recursion is ~58x slower than for-loops for counting to 100,000**

- **For-loop**: ~1.3ms
- **Recursion**: ~78.5ms

## Why is Recursion So Slow in Python?

1. **No Tail Call Optimization**: Python does not optimize tail-recursive calls, so each recursive call consumes stack space
2. **Function Call Overhead**: Each recursive call involves pushing a new frame onto the call stack
3. **CPython Optimization**: Python's for-loops are highly optimized in the CPython implementation
4. **Recursion Limit**: Python's default recursion limit is ~1000, requiring manual adjustment for deep recursion

## Running the Benchmark

```bash
python benchmark.py [iterations]
```

Default: 5 iterations

Example:
```bash
python benchmark.py 10  # Run with 10 iterations
```

## Results

The benchmark automatically increases Python's recursion limit from 1,000 to 101,000 to handle counting to 100,000.

Sample output:
```
For-loop (imperative):
  Mean: 1.342ms ± 0.017ms
  Min:  1.312ms
  Max:  1.353ms

Recursion (functional):
  Mean: 78.464ms ± 8.928ms
  Min:  71.726ms
  Max:  94.009ms

Comparison:
  Overhead: 77.122ms (5744.7%)
  Slowdown: 58.45x
```

## Takeaways

- **Use for-loops for counting/iteration in Python**: Much faster and more idiomatic
- **Recursion has significant overhead**: ~58x slower for this task
- **Python is not optimized for deep recursion**: Unlike languages like Scheme or Haskell
- **Functional programming in Python**: While Python supports functional programming, it's not optimized for it at the interpreter level

## Implementation Notes

The recursive implementation is intentionally simple:

```python
def count_with_recursion(n: int, current: int = 0) -> int:
    if current >= n:
        return current - 1
    return count_with_recursion(n, current + 1)
```

This is not tail-recursive optimizable (even if Python supported it), but it demonstrates the fundamental overhead of function calls in Python.
