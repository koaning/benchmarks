"""
Benchmark multiple approaches to counting/summing numbers to 100,000 in Python.

This script compares various Pythonic ways to perform iteration and accumulation:
1. For-loop (imperative)
2. While loop
3. Recursion (functional)
4. sum() with range()
5. sum() with generator expression
6. functools.reduce()
7. itertools.accumulate()
8. List comprehension with sum()
9. Math formula (Gauss formula for sum of sequence)
10. numpy.sum() (if available)

Note: Python's default recursion limit is ~1000, so we increase it for recursion.
"""

import time
import sys
import statistics
import json
from pathlib import Path
from functools import reduce
from itertools import accumulate


def for_loop_sum(n: int) -> int:
    """Sum numbers from 0 to n-1 using a for-loop."""
    total = 0
    for i in range(n):
        total += i
    return total


def while_loop_sum(n: int) -> int:
    """Sum numbers from 0 to n-1 using a while loop."""
    total = 0
    i = 0
    while i < n:
        total += i
        i += 1
    return total


def recursive_sum(n: int, current: int = 0, total: int = 0) -> int:
    """Sum numbers from 0 to n-1 using recursion."""
    if current >= n:
        return total
    return recursive_sum(n, current + 1, total + current)


def sum_range(n: int) -> int:
    """Sum numbers using built-in sum() and range()."""
    return sum(range(n))


def sum_generator(n: int) -> int:
    """Sum numbers using sum() with a generator expression."""
    return sum(i for i in range(n))


def reduce_sum(n: int) -> int:
    """Sum numbers using functools.reduce()."""
    return reduce(lambda acc, x: acc + x, range(n), 0)


def accumulate_sum(n: int) -> int:
    """Sum numbers using itertools.accumulate() and getting the last value."""
    return list(accumulate(range(n)))[-1]


def list_comp_sum(n: int) -> int:
    """Sum numbers using a list comprehension with sum()."""
    return sum([i for i in range(n)])


def math_formula_sum(n: int) -> int:
    """Sum numbers using Gauss's formula: n*(n-1)/2."""
    return (n * (n - 1)) // 2


def numpy_sum(n: int) -> int:
    """Sum numbers using numpy (if available)."""
    try:
        import numpy as np
        return int(np.sum(np.arange(n)))
    except ImportError:
        return None


def measure_performance(func, n: int, iterations: int = 5, name: str = "") -> dict:
    """Measure execution time of a function."""
    times = []
    result = None

    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)
        start = time.perf_counter()
        try:
            result = func(n)
            end = time.perf_counter()
            elapsed = end - start
            times.append(elapsed)
            print(f"{elapsed*1000:.4f}ms (result: {result})")
        except Exception as e:
            print(f"FAILED: {e}")
            return None

    if not times:
        return None

    return {
        "name": name,
        "mean": statistics.mean(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "all_times": times,
        "result": result
    }


def main():
    # Configuration
    count_to = 100_000
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    # Increase recursion limit for recursive approach
    original_limit = sys.getrecursionlimit()
    new_limit = count_to + 1000
    sys.setrecursionlimit(new_limit)

    print(f"Comprehensive Loop/Sum Benchmark ({iterations} iterations)")
    print(f"Summing numbers from 0 to {count_to-1:,} (sum = {math_formula_sum(count_to):,})")
    print(f"Recursion limit increased: {original_limit:,} → {new_limit:,}\n")

    # Define all methods to benchmark
    methods = [
        ("For-loop", for_loop_sum),
        ("While loop", while_loop_sum),
        ("sum(range(n))", sum_range),
        ("sum(generator)", sum_generator),
        ("sum([list comp])", list_comp_sum),
        ("functools.reduce()", reduce_sum),
        ("itertools.accumulate()", accumulate_sum),
        ("Math formula (Gauss)", math_formula_sum),
        ("Recursion", recursive_sum),
    ]

    # Check if numpy is available
    try:
        import numpy as np
        methods.append(("numpy.sum()", numpy_sum))
        has_numpy = True
    except ImportError:
        has_numpy = False
        print("Note: numpy not available, skipping numpy benchmark\n")

    # Run benchmarks
    results = []
    for idx, (name, func) in enumerate(methods, 1):
        print(f"[{idx}/{len(methods)}] Benchmarking {name}...")
        result = measure_performance(func, count_to, iterations, name)
        if result:
            results.append(result)
        print()

    # Sort results by mean time
    results.sort(key=lambda x: x["mean"])

    # Print results
    print("=" * 80)
    print("RESULTS (sorted by speed)")
    print("=" * 80)

    fastest_time = results[0]["mean"]

    for idx, r in enumerate(results, 1):
        mean_ms = r["mean"] * 1000
        stdev_ms = r["stdev"] * 1000
        min_ms = r["min"] * 1000
        max_ms = r["max"] * 1000
        slowdown = r["mean"] / fastest_time

        print(f"\n{idx}. {r['name']}")
        print(f"   Mean: {mean_ms:.4f}ms ± {stdev_ms:.4f}ms")
        print(f"   Min:  {min_ms:.4f}ms | Max: {max_ms:.4f}ms")
        print(f"   Slowdown: {slowdown:.2f}x")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nFastest: {results[0]['name']} ({results[0]['mean']*1000:.4f}ms)")
    print(f"Slowest: {results[-1]['name']} ({results[-1]['mean']*1000:.4f}ms)")
    print(f"Speed difference: {results[-1]['mean']/results[0]['mean']:.2f}x")
    print("=" * 80)

    # Save results to JSONL
    output = {
        "timestamp": time.time(),
        "count_to": count_to,
        "iterations": iterations,
        "recursion_limit": new_limit,
        "has_numpy": has_numpy,
        "methods": {r["name"]: {
            "mean": r["mean"],
            "stdev": r["stdev"],
            "min": r["min"],
            "max": r["max"],
            "all_times": r["all_times"],
            "result": r["result"]
        } for r in results},
        "ranking": [r["name"] for r in results]
    }

    results_path = Path(__file__).parent / "results_all_methods.jsonl"
    with open(results_path, "a") as f:
        f.write(json.dumps(output) + "\n")

    print(f"\nResults saved to {results_path}")

    # Restore original recursion limit
    sys.setrecursionlimit(original_limit)


if __name__ == "__main__":
    main()
