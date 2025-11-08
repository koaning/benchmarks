"""
Benchmark for-loop counting vs functional recursive counting in Python.

This script compares the performance of counting to 100,000 using:
1. A traditional for-loop (imperative approach)
2. Functional recursion (recursive approach)

Note: Python's default recursion limit is ~1000, so we increase it to handle 100,000.
"""

import time
import sys
import statistics
import json
from pathlib import Path


def count_with_loop(n: int) -> int:
    """Count to n using a for-loop."""
    count = 0
    for i in range(n):
        count = i
    return count


def count_with_recursion(n: int, current: int = 0) -> int:
    """Count to n using recursion."""
    if current >= n:
        return current - 1
    return count_with_recursion(n, current + 1)


def measure_performance(func, n: int, iterations: int = 5) -> list[float]:
    """Measure execution time of a counting function."""
    times = []
    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)
        start = time.perf_counter()
        result = func(n)
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        print(f"{elapsed:.4f}s (result: {result})")
    return times


def main():
    # Configuration
    count_to = 100_000
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    # Increase recursion limit to handle deep recursion
    # Python's default is ~1000, we need at least 100,000
    original_limit = sys.getrecursionlimit()
    new_limit = count_to + 1000  # Add buffer for safety
    sys.setrecursionlimit(new_limit)

    print(f"Loop vs Recursion Counting Benchmark ({iterations} iterations)")
    print(f"Counting to: {count_to:,}")
    print(f"Recursion limit increased: {original_limit:,} → {new_limit:,}\n")

    # Run benchmarks
    print("[1/2] Benchmarking for-loop approach...")
    loop_times = measure_performance(count_with_loop, count_to, iterations)

    print("\n[2/2] Benchmarking recursive approach...")
    recursion_times = measure_performance(count_with_recursion, count_to, iterations)

    # Calculate statistics
    loop_mean = statistics.mean(loop_times)
    loop_stdev = statistics.stdev(loop_times) if len(loop_times) > 1 else 0

    recursion_mean = statistics.mean(recursion_times)
    recursion_stdev = statistics.stdev(recursion_times) if len(recursion_times) > 1 else 0

    slowdown = recursion_mean / loop_mean
    overhead = recursion_mean - loop_mean
    overhead_pct = (overhead / loop_mean) * 100

    # Print results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    print(f"\nFor-loop (imperative):")
    print(f"  Mean: {loop_mean*1000:.3f}ms ± {loop_stdev*1000:.3f}ms")
    print(f"  Min:  {min(loop_times)*1000:.3f}ms")
    print(f"  Max:  {max(loop_times)*1000:.3f}ms")

    print(f"\nRecursion (functional):")
    print(f"  Mean: {recursion_mean*1000:.3f}ms ± {recursion_stdev*1000:.3f}ms")
    print(f"  Min:  {min(recursion_times)*1000:.3f}ms")
    print(f"  Max:  {max(recursion_times)*1000:.3f}ms")

    print(f"\nComparison:")
    print(f"  Overhead: {overhead*1000:.3f}ms ({overhead_pct:.1f}%)")
    print(f"  Slowdown: {slowdown:.2f}x")
    print(f"  Result: Recursion is {slowdown:.2f}x slower than for-loop")

    print("="*70)

    # Save results to JSONL
    results = {
        "timestamp": time.time(),
        "count_to": count_to,
        "iterations": iterations,
        "recursion_limit": new_limit,
        "for_loop": {
            "mean": loop_mean,
            "stdev": loop_stdev,
            "min": min(loop_times),
            "max": max(loop_times),
            "all_times": loop_times
        },
        "recursion": {
            "mean": recursion_mean,
            "stdev": recursion_stdev,
            "min": min(recursion_times),
            "max": max(recursion_times),
            "all_times": recursion_times
        },
        "comparison": {
            "overhead_seconds": overhead,
            "overhead_pct": overhead_pct,
            "slowdown": slowdown
        }
    }

    results_path = Path(__file__).parent / "results.jsonl"
    with open(results_path, "a") as f:
        f.write(json.dumps(results) + "\n")

    print(f"\nResults saved to {results_path}")

    # Restore original recursion limit
    sys.setrecursionlimit(original_limit)


if __name__ == "__main__":
    main()
