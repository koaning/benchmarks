"""
Benchmark the import overhead of marimo across different versions.

This script measures how long it takes to import marimo for different versions,
allowing you to track performance changes over time.
"""

import time
import subprocess
import statistics
import json
import sys
from pathlib import Path
from typing import List, Dict
import tempfile
import venv


def get_installed_marimo_version() -> str:
    """Get the currently installed marimo version."""
    try:
        result = subprocess.run(
            ["python", "-c", "import marimo; print(marimo.__version__)"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def measure_import_time(iterations: int = 10) -> List[float]:
    """Measure the time it takes to import marimo."""
    times = []

    for i in range(iterations):
        print(f"    Iteration {i+1}/{iterations}...", end=" ", flush=True)

        # Use a subprocess to ensure fresh import each time
        start = time.perf_counter()
        result = subprocess.run(
            ["python", "-c", "import marimo"],
            capture_output=True,
            check=True,
            timeout=10
        )
        end = time.perf_counter()

        elapsed = end - start
        times.append(elapsed)
        print(f"{elapsed*1000:.2f}ms")

    return times


def install_marimo_version(version: str) -> bool:
    """Install a specific version of marimo."""
    print(f"  Installing marimo=={version}...", end=" ", flush=True)
    try:
        subprocess.run(
            ["pip", "install", "-q", f"marimo=={version}"],
            check=True,
            timeout=120
        )
        print("Done")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed: {e}")
        return False


def benchmark_version(version: str, iterations: int) -> Dict:
    """Benchmark a specific marimo version."""
    print(f"\nBenchmarking marimo {version}")

    # Install the version
    if not install_marimo_version(version):
        return None

    # Verify installation
    installed_version = get_installed_marimo_version()
    if installed_version != version:
        print(f"  Warning: Expected {version}, got {installed_version}")

    # Measure import time
    print(f"  Measuring import time...")
    times = measure_import_time(iterations)

    # Calculate statistics
    mean = statistics.mean(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)

    print(f"  Results: {mean*1000:.2f}ms ± {stdev*1000:.2f}ms (min: {min_time*1000:.2f}ms, max: {max_time*1000:.2f}ms)")

    return {
        "version": version,
        "mean": mean,
        "stdev": stdev,
        "min": min_time,
        "max": max_time,
        "all_times": times
    }


def print_results_table(results: List[Dict]):
    """Print results in a formatted table."""
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print(f"{'Version':<15} {'Mean':<12} {'StdDev':<12} {'Min':<12} {'Max':<12} {'Change':<12}")
    print("-"*80)

    baseline = None
    for result in results:
        version = result["version"]
        mean_ms = result["mean"] * 1000
        stdev_ms = result["stdev"] * 1000
        min_ms = result["min"] * 1000
        max_ms = result["max"] * 1000

        if baseline is None:
            baseline = result["mean"]
            change_str = "(baseline)"
        else:
            change = ((result["mean"] - baseline) / baseline) * 100
            change_str = f"{change:+.1f}%"

        print(f"{version:<15} {mean_ms:>8.2f}ms  {stdev_ms:>8.2f}ms  {min_ms:>8.2f}ms  {max_ms:>8.2f}ms  {change_str:>12}")

    print("="*80)


def main():
    # Default versions to test - you can customize this list
    default_versions = [
        "0.6.0",
        "0.7.0",
        "0.8.0",
        "0.9.0",
        "0.10.0",
    ]

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python benchmark_import.py [iterations] [version1 version2 ...]")
            print("\nExamples:")
            print("  python benchmark_import.py                    # Test default versions with 10 iterations")
            print("  python benchmark_import.py 20                 # Test default versions with 20 iterations")
            print("  python benchmark_import.py 10 0.8.0 0.9.0    # Test specific versions with 10 iterations")
            return

        # First arg might be iterations
        try:
            iterations = int(sys.argv[1])
            versions = sys.argv[2:] if len(sys.argv) > 2 else default_versions
        except ValueError:
            # If first arg is not a number, treat all as versions
            iterations = 10
            versions = sys.argv[1:]
    else:
        iterations = 10
        versions = default_versions

    print("Marimo Import Time Benchmark")
    print(f"Testing {len(versions)} version(s) with {iterations} iterations each\n")
    print(f"Versions to test: {', '.join(versions)}")

    # Store original version to restore later
    original_version = get_installed_marimo_version()
    print(f"\nOriginal marimo version: {original_version}")

    # Benchmark each version
    results = []
    for version in versions:
        result = benchmark_version(version, iterations)
        if result:
            results.append(result)

    # Print results table
    if results:
        print_results_table(results)

        # Save results to JSONL
        output = {
            "timestamp": time.time(),
            "iterations": iterations,
            "results": results
        }

        results_path = Path(__file__).parent / "import_benchmark_results.jsonl"
        with open(results_path, "a") as f:
            f.write(json.dumps(output) + "\n")

        print(f"\nResults saved to {results_path}")

    # Restore original version
    if original_version != "unknown":
        print(f"\nRestoring original marimo version {original_version}...")
        install_marimo_version(original_version)


if __name__ == "__main__":
    main()
