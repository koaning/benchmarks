"""
Benchmark the overhead of running a script via marimo vs plain Python.

This script measures the startup time and execution overhead of marimo
compared to running equivalent Python code directly.
"""

import time
import subprocess
import statistics
import json
from pathlib import Path


def measure_plain_python(script_path: str, iterations: int = 10) -> list[float]:
    """Measure execution time of plain Python script."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            check=True
        )
        end = time.perf_counter()
        times.append(end - start)
    return times


def measure_marimo_run(script_path: str, iterations: int = 10) -> list[float]:
    """Measure execution time of marimo run."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = subprocess.run(
            ["marimo", "run", script_path, "--headless"],
            capture_output=True,
            check=True
        )
        end = time.perf_counter()
        times.append(end - start)
    return times


def create_simple_script():
    """Create a simple test script."""
    script_content = '''
import time

# Simple computation
result = sum(range(1000))
print(f"Result: {result}")
'''

    script_path = Path(__file__).parent / "test_script.py"
    script_path.write_text(script_content)
    return str(script_path)


def create_marimo_script():
    """Create a simple marimo test script."""
    script_content = '''import marimo

__generated_with = "0.9.0"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    # Simple computation
    result = sum(range(1000))
    print(f"Result: {result}")
    return result,


if __name__ == "__main__":
    app.run()
'''

    script_path = Path(__file__).parent / "test_script_marimo.py"
    script_path.write_text(script_content)
    return str(script_path)


def main():
    iterations = 10

    print("Creating test scripts...")
    plain_script = create_simple_script()
    marimo_script = create_marimo_script()

    print(f"\nRunning benchmark ({iterations} iterations each)...\n")

    print("Measuring plain Python execution...")
    plain_times = measure_plain_python(plain_script, iterations)

    print("Measuring marimo run execution...")
    marimo_times = measure_marimo_run(marimo_script, iterations)

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
    print(f"\nPlain Python:")
    print(f"  Mean: {plain_mean:.4f}s ± {plain_stdev:.4f}s")
    print(f"  Min:  {min(plain_times):.4f}s")
    print(f"  Max:  {max(plain_times):.4f}s")

    print(f"\nMarimo run:")
    print(f"  Mean: {marimo_mean:.4f}s ± {marimo_stdev:.4f}s")
    print(f"  Min:  {min(marimo_times):.4f}s")
    print(f"  Max:  {max(marimo_times):.4f}s")

    print(f"\nOverhead:")
    print(f"  Absolute: {overhead:.4f}s")
    print(f"  Relative: {overhead_pct:.2f}%")
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
        "marimo_run": {
            "mean": marimo_mean,
            "stdev": marimo_stdev,
            "min": min(marimo_times),
            "max": max(marimo_times),
            "all_times": marimo_times
        },
        "overhead": {
            "absolute": overhead,
            "relative_pct": overhead_pct
        }
    }

    results_path = Path(__file__).parent / "results.jsonl"
    with open(results_path, "a") as f:
        f.write(json.dumps(results) + "\n")

    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
