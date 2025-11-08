# Marimo Overhead Benchmark

This benchmark measures the execution overhead of running a marimo notebook as a script (`python notebook.py`) compared to plain Python.

## What it measures

Compares the execution time of three scripts:
1. `python plain_script.py` - Plain Python script
2. `python marimo_notebook.py` - Marimo notebook run as a script
3. `python marimo_notebook_with_import.py` - Marimo notebook with an additional import cell

All scripts perform the same simple computation, allowing you to measure the overhead of marimo's framework.

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

Example results (3 iterations):

```
Plain Python (python plain_script.py):
  Mean: 28.93ms ± 0.32ms
  Min:  28.67ms
  Max:  29.28ms

Marimo notebook (python marimo_notebook.py):
  Mean: 1295.09ms ± 20.79ms
  Min:  1275.91ms
  Max:  1317.17ms
  Overhead: 1266.15ms (4376.4%, 44.8x)

Marimo notebook with import (python marimo_notebook_with_import.py):
  Mean: 1300.81ms ± 6.87ms
  Min:  1293.31ms
  Max:  1306.81ms
  Overhead: 1271.87ms (4396.2%, 45.0x)

Comparison:
  Import cell overhead: 5.72ms
```

### Key Findings

- **Marimo adds ~1.3 seconds of overhead** when running notebooks as scripts
- **Adding an extra import cell** (importing marimo in a cell) adds only **~5ms overhead**
- Most overhead comes from framework initialization, not from additional cells
- Results are saved to `results.jsonl` with full timing statistics

## Interpretation

The benchmark measures the real-world overhead you'd experience when running a marimo notebook as a script vs plain Python. This is the most pragmatic comparison since marimo notebooks are valid Python files that can be executed directly.

The additional test case with an import cell demonstrates that marimo's overhead is primarily from initialization - adding extra cells has minimal impact on execution time.
