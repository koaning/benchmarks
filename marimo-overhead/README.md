# Marimo Overhead Benchmark

This benchmark measures the execution overhead of running scripts via marimo compared to plain Python.

## What it measures

- Startup time for plain Python scripts
- Startup time for marimo run in headless mode
- Absolute and relative overhead of marimo execution

## Running the benchmark

```bash
# Install dependencies
pip install -r requirements.txt

# Run the benchmark
make benchmark

# Or run directly
python benchmark.py
```

## Results

Results are saved to `results.jsonl` with timing statistics for both plain Python and marimo execution.

## Interpretation

The benchmark creates two equivalent scripts:
1. A simple Python script that performs basic computation
2. A marimo app that performs the same computation

Each is executed multiple times (default: 10 iterations) and the execution times are compared to calculate the overhead.
