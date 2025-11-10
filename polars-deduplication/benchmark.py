"""
Benchmark different approaches to filtering new items against existing seen items.

Use case: You have a set of items you've seen before, and new items come in.
You want to find which new items you haven't seen yet.

Compares:
- Polars anti-join (new_df.join(seen_df, how="anti"))
- Python set difference (new_set - seen_set)
- Python set with list comprehension
- Polars is_in() filter
"""

import time
import statistics
import json
import sys
from pathlib import Path
import numpy as np
import polars as pl
import pandas as pd


def generate_data(seen_size: int, new_size: int, overlap_rate: float, seed: int = 42):
    """
    Generate test data: existing "seen" items and new incoming items.

    Args:
        seen_size: Number of items in the existing "seen" set
        new_size: Number of new incoming items
        overlap_rate: Fraction of new items that overlap with seen (0.0 to 1.0)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (seen_df, new_df) - both Polars DataFrames with 'id' column
    """
    np.random.seed(seed)

    # Generate existing "seen" items
    seen_ids = np.arange(seen_size)
    seen_df = pl.DataFrame({"id": seen_ids})

    # Generate new items with controlled overlap
    overlap_count = int(new_size * overlap_rate)
    new_count = new_size - overlap_count

    # Items that overlap with seen
    overlapping = np.random.choice(seen_ids, size=overlap_count, replace=True)

    # Items that are truly new
    new_unique = np.arange(seen_size, seen_size + new_count)

    # Combine and shuffle
    new_ids = np.concatenate([overlapping, new_unique])
    np.random.shuffle(new_ids)

    new_df = pl.DataFrame({"id": new_ids})

    return seen_df, new_df


def method_polars_anti_join(seen_df: pl.DataFrame, new_df: pl.DataFrame) -> pl.DataFrame:
    """
    Use Polars anti-join to find new items not in seen set.
    This is the "proper" way to do it in Polars.
    """
    return new_df.join(seen_df, on="id", how="anti")


def method_python_set_difference(seen_df: pl.DataFrame, new_df: pl.DataFrame) -> pl.DataFrame:
    """
    Use Python set difference: new_set - seen_set
    """
    seen_set = set(seen_df["id"].to_list())
    new_set = set(new_df["id"].to_list())
    result_set = new_set - seen_set
    return pl.DataFrame({"id": list(result_set)})


def method_python_set_comprehension(seen_df: pl.DataFrame, new_df: pl.DataFrame) -> pl.DataFrame:
    """
    Use Python set with list comprehension to preserve order.
    """
    seen_set = set(seen_df["id"].to_list())
    new_ids = new_df["id"].to_list()
    result = [id_val for id_val in new_ids if id_val not in seen_set]
    return pl.DataFrame({"id": result})


def method_polars_is_in(seen_df: pl.DataFrame, new_df: pl.DataFrame) -> pl.DataFrame:
    """
    Use Polars is_in() to filter new items.
    """
    seen_ids = seen_df["id"]
    return new_df.filter(~pl.col("id").is_in(seen_ids))


def method_pandas_merge(seen_df: pl.DataFrame, new_df: pl.DataFrame) -> pl.DataFrame:
    """
    Use Pandas merge with indicator to simulate anti-join.
    """
    seen_pdf = seen_df.to_pandas()
    new_pdf = new_df.to_pandas()

    merged = new_pdf.merge(seen_pdf, on="id", how="left", indicator=True)
    result_pdf = merged[merged["_merge"] == "left_only"][["id"]]

    return pl.from_pandas(result_pdf)


def measure_method(method_func, seen_df: pl.DataFrame, new_df: pl.DataFrame, iterations: int = 5) -> dict:
    """
    Measure execution time of a filtering method.

    Returns:
        dict with timing stats and result size
    """
    times = []

    # Warmup
    result = method_func(seen_df, new_df)
    result_size = len(result)

    for _ in range(iterations):
        start = time.perf_counter()
        result = method_func(seen_df, new_df)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": statistics.mean(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "all_times": times,
        "result_size": result_size
    }


def run_benchmark_suite(seen_size: int, new_size: int, overlap_rate: float, iterations: int = 5):
    """
    Run all filtering methods for a given configuration.

    Args:
        seen_size: Number of items in existing "seen" set
        new_size: Number of new incoming items
        overlap_rate: Fraction of new items that already exist in seen set
    """
    print(f"\n{'='*70}")
    print(f"Seen: {seen_size:,} items | New: {new_size:,} items | Overlap: {overlap_rate*100:.0f}%")
    print(f"{'='*70}")

    # Generate data
    seen_df, new_df = generate_data(seen_size, new_size, overlap_rate)

    # Calculate expected result size
    expected_new = int(new_size * (1 - overlap_rate))
    print(f"Expected truly new items: ~{expected_new:,}")

    methods = [
        ("Polars anti-join", method_polars_anti_join),
        ("Python set difference", method_python_set_difference),
        ("Python set comprehension", method_python_set_comprehension),
        ("Polars is_in() filter", method_polars_is_in),
        ("Pandas merge indicator", method_pandas_merge),
    ]

    results = {}

    for name, method in methods:
        print(f"\nTesting {name}...", end=" ", flush=True)
        try:
            stats = measure_method(method, seen_df, new_df, iterations)
            results[name] = stats
            print(f"{stats['mean']*1000:.2f}ms ± {stats['stdev']*1000:.2f}ms (found {stats['result_size']:,} new items)")
        except Exception as e:
            print(f"ERROR: {e}")
            results[name] = None

    # Calculate speedups relative to Python set comprehension (most common pattern)
    baseline_name = "Python set comprehension"
    if baseline_name in results and results[baseline_name]:
        baseline = results[baseline_name]["mean"]
        print(f"\n{'='*70}")
        print(f"Speedup vs {baseline_name}:")
        print(f"{'='*70}")
        for name, stats in results.items():
            if stats and name != baseline_name:
                speedup = baseline / stats["mean"]
                print(f"{name:30s}: {speedup:6.2f}x")

    return {
        "seen_size": seen_size,
        "new_size": new_size,
        "overlap_rate": overlap_rate,
        "expected_new": expected_new,
        "iterations": iterations,
        "results": results
    }


def main():
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    print("="*70)
    print("Polars Anti-Join: Filter New Items vs Seen Items")
    print("="*70)
    print(f"Iterations per test: {iterations}")
    print("\nUse case: Filter incoming items against existing 'seen' set")

    # Test configurations: (seen_size, new_size, overlap_rate)
    configs = [
        # Small: 1K seen, various new batch sizes
        (1_000, 1_000, 0.5),      # Equal size, 50% overlap
        (1_000, 1_000, 0.9),      # Equal size, 90% overlap
        (1_000, 10_000, 0.5),     # Large new batch

        # Medium: 100K seen
        (100_000, 10_000, 0.5),   # Small new batch
        (100_000, 100_000, 0.5),  # Equal size, 50% overlap
        (100_000, 100_000, 0.9),  # Equal size, 90% overlap

        # Large: 1M seen
        (1_000_000, 100_000, 0.5),   # Medium new batch
        (1_000_000, 1_000_000, 0.5), # Equal size, 50% overlap
        (1_000_000, 1_000_000, 0.9), # Equal size, 90% overlap
    ]

    all_results = []

    for seen_size, new_size, overlap_rate in configs:
        result = run_benchmark_suite(seen_size, new_size, overlap_rate, iterations)
        all_results.append(result)

    # Save results to JSONL
    results_path = Path(__file__).parent / "results.jsonl"
    with open(results_path, "w") as f:  # Overwrite old results
        f.write(json.dumps({
            "timestamp": time.time(),
            "benchmarks": all_results
        }) + "\n")

    print(f"\n{'='*70}")
    print(f"Results saved to {results_path}")
    print(f"{'='*70}")

    return all_results


if __name__ == "__main__":
    main()
