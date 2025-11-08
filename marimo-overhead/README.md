# Marimo Overhead Benchmark

This benchmark measures the execution overhead of running a marimo notebook as a script (`python notebook.py`) compared to plain Python.

## What it measures

Compares the execution time of:
- `python plain_script.py` - Plain Python script
- `python marimo_notebook.py` - Marimo notebook run as a script

Both scripts perform the same simple computation, allowing you to measure the overhead of marimo's framework.

## Running the benchmark

```bash
# Install dependencies
pip install -r requirements.txt

# Run the benchmark (default: 3 iterations)
make benchmark

# Or run directly with custom iterations
python benchmark.py 5
```

## Results

Results are saved to `results.jsonl` with timing statistics including:
- Mean, min, max execution times
- Standard deviation
- Absolute and relative overhead
- Slowdown factor

## Interpretation

The benchmark measures the real-world overhead you'd experience when running a marimo notebook as a script vs plain Python. This is the most pragmatic comparison since marimo notebooks are valid Python files that can be executed directly.
