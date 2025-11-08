"""
Benchmark the overhead of marimo vs plain Python.

This script measures the overhead of running a marimo notebook as a script
(python notebook.py) compared to plain Python.
"""

import time
import subprocess
import statistics
import json
import sys
from pathlib import Path


def measure_execution(script_path: str, iterations: int = 3) -> list[float]:
    """Measure execution time of a script."""
    times = []
    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)
        start = time.perf_counter()
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            check=True,
            timeout=10
        )
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        print(f"{elapsed:.3f}s")
    return times


def create_plain_script():
    """Create a simple plain Python test script."""
    script_content = '''# Simple computation
result = sum(range(1000))
print(f"Result: {result}")
'''
    script_path = Path(__file__).parent / "plain_script.py"
    script_path.write_text(script_content)
    return str(script_path)


def create_marimo_notebook():
    """Create a simple marimo notebook."""
    script_content = '''import marimo

__generated_with = "0.9.0"
app = marimo.App()


@app.cell
def __():
    # Simple computation
    result = sum(range(1000))
    print(f"Result: {result}")
    return result,


if __name__ == "__main__":
    app.run()
'''
    script_path = Path(__file__).parent / "marimo_notebook.py"
    script_path.write_text(script_content)
    return str(script_path)


def main():
    # Allow command line override for iterations
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    print(f"Marimo Overhead Benchmark ({iterations} iterations)")
    print("Comparing: python script.py vs python notebook.py\n")

    print("[1/2] Creating test scripts...")
    plain_script = create_plain_script()
    marimo_notebook = create_marimo_notebook()

    print("\n[2/2] Running benchmarks...")
    print("\nPlain Python (python plain_script.py):")
    plain_times = measure_execution(plain_script, iterations)

    print("\nMarimo notebook (python marimo_notebook.py):")
    marimo_times = measure_execution(marimo_notebook, iterations)

    # Calculate statistics
    plain_mean = statistics.mean(plain_times)
    plain_stdev = statistics.stdev(plain_times) if len(plain_times) > 1 else 0

    marimo_mean = statistics.mean(marimo_times)
    marimo_stdev = statistics.stdev(marimo_times) if len(marimo_times) > 1 else 0

    overhead = marimo_mean - plain_mean
    overhead_pct = (overhead / plain_mean) * 100

    # Print results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"\nPlain Python (python plain_script.py):")
    print(f"  Mean: {plain_mean*1000:.2f}ms ± {plain_stdev*1000:.2f}ms")
    print(f"  Min:  {min(plain_times)*1000:.2f}ms")
    print(f"  Max:  {max(plain_times)*1000:.2f}ms")

    print(f"\nMarimo notebook (python marimo_notebook.py):")
    print(f"  Mean: {marimo_mean*1000:.2f}ms ± {marimo_stdev*1000:.2f}ms")
    print(f"  Min:  {min(marimo_times)*1000:.2f}ms")
    print(f"  Max:  {max(marimo_times)*1000:.2f}ms")

    print(f"\nOverhead:")
    print(f"  Absolute: {overhead*1000:.2f}ms")
    print(f"  Relative: {overhead_pct:.1f}%")
    print(f"  Slowdown: {marimo_mean/plain_mean:.1f}x")
    print("="*60)

    # Save results to JSONL
    results = {
        "timestamp": time.time(),
        "iterations": iterations,
        "plain_python": {
            "mean": plain_mean,
            "stdev": plain_stdev,
            "min": min(plain_times),
            "max": max(plain_times),
            "all_times": plain_times
        },
        "marimo_notebook": {
            "mean": marimo_mean,
            "stdev": marimo_stdev,
            "min": min(marimo_times),
            "max": max(marimo_times),
            "all_times": marimo_times
        },
        "overhead": {
            "absolute": overhead,
            "relative_pct": overhead_pct,
            "slowdown": marimo_mean / plain_mean
        }
    }

    results_path = Path(__file__).parent / "results.jsonl"
    with open(results_path, "a") as f:
        f.write(json.dumps(results) + "\n")

    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
