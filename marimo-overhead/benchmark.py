"""
Benchmark the overhead of marimo vs plain Python.

This script measures:
1. Plain Python script execution time
2. Marimo import overhead
3. Marimo app initialization overhead
"""

import time
import subprocess
import statistics
import json
import sys
from pathlib import Path


def measure_plain_python(script_path: str, iterations: int = 3) -> list[float]:
    """Measure execution time of plain Python script."""
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


def measure_marimo_import(iterations: int = 3) -> list[float]:
    """Measure marimo import overhead."""
    import_script = '''
import time
start = time.perf_counter()
import marimo
elapsed = time.perf_counter() - start
print(elapsed)
'''
    script_path = Path(__file__).parent / "test_import.py"
    script_path.write_text(import_script)

    times = []
    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            check=True,
            timeout=10,
            text=True
        )
        elapsed = float(result.stdout.strip())
        times.append(elapsed)
        print(f"{elapsed:.3f}s")

    script_path.unlink()
    return times


def measure_marimo_app_init(iterations: int = 3) -> list[float]:
    """Measure marimo app initialization overhead."""
    app_script = '''
import time
import marimo

start = time.perf_counter()
app = marimo.App()

@app.cell
def __():
    result = sum(range(1000))
    return result,

elapsed = time.perf_counter() - start
print(elapsed)
'''
    script_path = Path(__file__).parent / "test_app_init.py"
    script_path.write_text(app_script)

    times = []
    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            check=True,
            timeout=10,
            text=True
        )
        elapsed = float(result.stdout.strip())
        times.append(elapsed)
        print(f"{elapsed:.3f}s")

    script_path.unlink()
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
    # Allow command line override for iterations
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    print(f"Marimo Overhead Benchmark ({iterations} iterations)\n")

    print("[1/3] Creating baseline Python script...")
    plain_script = create_simple_script()

    print("\n[2/3] Measuring plain Python execution...")
    plain_times = measure_plain_python(plain_script, iterations)

    print("\n[3/3] Measuring marimo import time...")
    import_times = measure_marimo_import(iterations)

    print("\n[4/4] Measuring marimo app initialization...")
    app_init_times = measure_marimo_app_init(iterations)

    # Calculate statistics
    plain_mean = statistics.mean(plain_times)
    plain_stdev = statistics.stdev(plain_times) if len(plain_times) > 1 else 0

    import_mean = statistics.mean(import_times)
    import_stdev = statistics.stdev(import_times) if len(import_times) > 1 else 0

    app_init_mean = statistics.mean(app_init_times)
    app_init_stdev = statistics.stdev(app_init_times) if len(app_init_times) > 1 else 0

    # Print results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"\nPlain Python script execution:")
    print(f"  Mean: {plain_mean*1000:.2f}ms ± {plain_stdev*1000:.2f}ms")
    print(f"  Min:  {min(plain_times)*1000:.2f}ms")
    print(f"  Max:  {max(plain_times)*1000:.2f}ms")

    print(f"\nMarimo import time:")
    print(f"  Mean: {import_mean*1000:.2f}ms ± {import_stdev*1000:.2f}ms")
    print(f"  Min:  {min(import_times)*1000:.2f}ms")
    print(f"  Max:  {max(import_times)*1000:.2f}ms")

    print(f"\nMarimo app initialization:")
    print(f"  Mean: {app_init_mean*1000:.2f}ms ± {app_init_stdev*1000:.2f}ms")
    print(f"  Min:  {min(app_init_times)*1000:.2f}ms")
    print(f"  Max:  {max(app_init_times)*1000:.2f}ms")

    total_marimo = import_mean + app_init_mean
    print(f"\nTotal marimo overhead:")
    print(f"  Import + Init: {total_marimo*1000:.2f}ms")
    print(f"  vs Plain Python: {(total_marimo/plain_mean)*100:.1f}x slower")
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
        "marimo_import": {
            "mean": import_mean,
            "stdev": import_stdev,
            "min": min(import_times),
            "max": max(import_times),
            "all_times": import_times
        },
        "marimo_app_init": {
            "mean": app_init_mean,
            "stdev": app_init_stdev,
            "min": min(app_init_times),
            "max": max(app_init_times),
            "all_times": app_init_times
        },
        "total_overhead": {
            "absolute": total_marimo,
            "relative_to_plain": total_marimo / plain_mean
        }
    }

    results_path = Path(__file__).parent / "results.jsonl"
    with open(results_path, "a") as f:
        f.write(json.dumps(results) + "\n")

    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
