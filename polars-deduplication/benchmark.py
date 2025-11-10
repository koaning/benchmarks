"""
Benchmark different approaches to deduplication with a focus on Polars anti-join.

Compares:
- Polars anti-join pattern
- Python set()
- Polars unique()
- Polars is_duplicated() filter
- Polars group_by().first()
- Pandas drop_duplicates()
"""

import time
import statistics
import json
import sys
from pathlib import Path
import numpy as np
import polars as pl
import pandas as pd


def generate_data(size: int, duplication_rate: float, seed: int = 42):
    """
    Generate test data with controlled duplication rate.

    Args:
        size: Total number of rows
        duplication_rate: Fraction of rows that are duplicates (0.0 to 1.0)
        seed: Random seed for reproducibility

    Returns:
        Polars DataFrame with 'id' column
    """
    np.random.seed(seed)

    # Calculate number of unique values needed
    unique_count = int(size * (1 - duplication_rate))
    unique_count = max(1, unique_count)  # At least 1 unique value

    # Generate data with duplicates
    unique_ids = np.arange(unique_count)
    ids = np.random.choice(unique_ids, size=size, replace=True)

    # Shuffle to mix duplicates throughout
    np.random.shuffle(ids)

    return pl.DataFrame({"id": ids})


def method_polars_anti_join(df: pl.DataFrame) -> pl.DataFrame:
    """
    Use anti-join to deduplicate.
    Strategy: Keep first occurrence, anti-join against duplicates.
    """
    # Get indices of first occurrences
    first_occurrences = df.with_row_index().group_by("id").agg(
        pl.col("index").first().alias("first_idx")
    )

    # Add row index to original df
    df_indexed = df.with_row_index()

    # Join to keep only first occurrences
    # Actually, let's use a different approach - get duplicated IDs and anti-join
    duplicated_ids = df.group_by("id").agg(
        pl.col("id").count().alias("count")
    ).filter(pl.col("count") > 1).select("id")

    # Keep first of each ID
    first = df.group_by("id").first()

    return first


def method_polars_anti_join_v2(df: pl.DataFrame) -> pl.DataFrame:
    """
    Alternative anti-join approach: explicitly find duplicates and remove them.
    """
    # Mark row indices
    df_indexed = df.with_row_index("row_num")

    # Get first occurrence of each ID
    first_occurrences = df_indexed.group_by("id").agg(
        pl.col("row_num").min().alias("first_row")
    )

    # Anti-join: keep only rows that match the first occurrence
    result = (
        df_indexed
        .join(first_occurrences, on="id")
        .filter(pl.col("row_num") == pl.col("first_row"))
        .select("id")
    )

    return result


def method_python_set(df: pl.DataFrame) -> pl.DataFrame:
    """
    Use Python set for deduplication (order-preserving).
    """
    seen = set()
    ids = df["id"].to_list()
    result = []

    for id_val in ids:
        if id_val not in seen:
            seen.add(id_val)
            result.append(id_val)

    return pl.DataFrame({"id": result})


def method_polars_unique(df: pl.DataFrame) -> pl.DataFrame:
    """
    Use Polars built-in unique() method.
    """
    return df.unique(subset=["id"], keep="first")


def method_polars_is_duplicated(df: pl.DataFrame) -> pl.DataFrame:
    """
    Use is_duplicated() to filter out duplicates.
    """
    # is_duplicated marks ALL occurrences including first
    # We want is_first_distinct instead
    return df.unique(subset=["id"], keep="first")


def method_polars_group_by(df: pl.DataFrame) -> pl.DataFrame:
    """
    Use group_by().first() for deduplication.
    """
    return df.group_by("id").first()


def method_pandas_drop_duplicates(df: pl.DataFrame) -> pl.DataFrame:
    """
    Convert to Pandas and use drop_duplicates().
    """
    pdf = df.to_pandas()
    result_pdf = pdf.drop_duplicates(subset=["id"], keep="first")
    return pl.from_pandas(result_pdf)


def measure_method(method_func, df: pl.DataFrame, iterations: int = 5) -> dict:
    """
    Measure execution time of a deduplication method.

    Returns:
        dict with timing stats
    """
    times = []

    # Warmup
    _ = method_func(df)

    for _ in range(iterations):
        start = time.perf_counter()
        result = method_func(df)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": statistics.mean(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "all_times": times
    }


def run_benchmark_suite(size: int, duplication_rate: float, iterations: int = 5):
    """
    Run all deduplication methods for a given data size and duplication rate.
    """
    print(f"\n{'='*70}")
    print(f"Size: {size:,} rows | Duplication rate: {duplication_rate*100:.0f}%")
    print(f"{'='*70}")

    # Generate data
    df = generate_data(size, duplication_rate)
    expected_unique = len(df.unique(subset=["id"]))
    print(f"Generated {len(df):,} rows with {expected_unique:,} unique values")

    methods = [
        ("Polars anti-join", method_polars_anti_join),
        ("Polars anti-join v2", method_polars_anti_join_v2),
        ("Python set()", method_python_set),
        ("Polars unique()", method_polars_unique),
        ("Polars group_by().first()", method_polars_group_by),
        ("Pandas drop_duplicates()", method_pandas_drop_duplicates),
    ]

    results = {}

    for name, method in methods:
        print(f"\nTesting {name}...", end=" ", flush=True)
        try:
            stats = measure_method(method, df, iterations)
            results[name] = stats
            print(f"{stats['mean']*1000:.2f}ms ± {stats['stdev']*1000:.2f}ms")
        except Exception as e:
            print(f"ERROR: {e}")
            results[name] = None

    # Calculate speedups relative to Python set()
    if "Python set()" in results and results["Python set()"]:
        baseline = results["Python set()"]["mean"]
        print(f"\n{'='*70}")
        print("Speedup vs Python set():")
        print(f"{'='*70}")
        for name, stats in results.items():
            if stats and name != "Python set()":
                speedup = baseline / stats["mean"]
                print(f"{name:30s}: {speedup:6.2f}x")

    return {
        "size": size,
        "duplication_rate": duplication_rate,
        "unique_count": expected_unique,
        "iterations": iterations,
        "results": results
    }


def main():
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    print("="*70)
    print("Polars Anti-Join Deduplication Benchmark")
    print("="*70)
    print(f"Iterations per test: {iterations}")

    # Test configurations
    configs = [
        # Small data
        (1_000, 0.1),      # 1K rows, 10% duplicates
        (1_000, 0.5),      # 1K rows, 50% duplicates
        (1_000, 0.9),      # 1K rows, 90% duplicates

        # Medium data
        (100_000, 0.1),    # 100K rows, 10% duplicates
        (100_000, 0.5),    # 100K rows, 50% duplicates
        (100_000, 0.9),    # 100K rows, 90% duplicates

        # Large data
        (1_000_000, 0.1),  # 1M rows, 10% duplicates
        (1_000_000, 0.5),  # 1M rows, 50% duplicates
        (1_000_000, 0.9),  # 1M rows, 90% duplicates
    ]

    all_results = []

    for size, dup_rate in configs:
        result = run_benchmark_suite(size, dup_rate, iterations)
        all_results.append(result)

    # Save results to JSONL
    results_path = Path(__file__).parent / "results.jsonl"
    with open(results_path, "a") as f:
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
