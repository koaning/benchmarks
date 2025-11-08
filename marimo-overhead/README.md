# Marimo Overhead Benchmark

This directory contains two benchmarks:
1. **Execution Overhead** - measures the overhead of running a marimo notebook as a script compared to plain Python
2. **Import Time** - measures the time it takes to import marimo across different versions

---

## 1. Execution Overhead Benchmark

### What it measures

Compares the execution time of three scripts:
1. `python plain_script.py` - Plain Python script
2. `python marimo_notebook.py` - Marimo notebook run as a script
3. `python marimo_notebook_with_import.py` - Marimo notebook with an additional import cell

All scripts perform the same simple computation, allowing you to measure the overhead of marimo's framework.

### Running the benchmark

```bash
# Install dependencies
pip install -r requirements.txt

# Run the benchmark (default: 3 iterations)
make benchmark

# Or run directly with custom iterations
python benchmark.py 5
```

### Results

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

#### Key Findings

- **Marimo adds ~1.3 seconds of overhead** when running notebooks as scripts
- **Adding an extra import cell** (importing marimo in a cell) adds only **~5ms overhead**
- Most overhead comes from framework initialization, not from additional cells
- Results are saved to `results.jsonl` with full timing statistics

### Interpretation

The benchmark measures the real-world overhead you'd experience when running a marimo notebook as a script vs plain Python. This is the most pragmatic comparison since marimo notebooks are valid Python files that can be executed directly.

The additional test case with an import cell demonstrates that marimo's overhead is primarily from initialization - adding extra cells has minimal impact on execution time.

---

## 2. Import Time Benchmark

### What it measures

Measures how long it takes to `import marimo` across different versions of the library. This helps track whether import time has increased or decreased over time, which is important for:
- Development workflow (fast imports = faster iteration)
- Notebook startup time
- Script execution overhead

### Running the benchmark

```bash
# Test default versions (0.6.0, 0.7.0, 0.8.0, 0.9.0, 0.10.0) with 10 iterations
python benchmark_import.py

# Test with more iterations for better accuracy
python benchmark_import.py 20

# Test specific versions
python benchmark_import.py 10 0.8.0 0.9.0 0.10.0

# Show help
python benchmark_import.py --help
```

### How it works

For each version:
1. Installs the specific marimo version using pip
2. Measures import time across multiple iterations (default: 10)
3. Each measurement runs in a fresh subprocess to ensure accurate timing
4. Calculates mean, standard deviation, min, and max times
5. Compares results across versions

After testing, it automatically restores your original marimo version.

### Results

Example output:

```
Marimo Import Time Benchmark
Testing 5 version(s) with 10 iterations each

Versions to test: 0.6.0, 0.7.0, 0.8.0, 0.9.0, 0.10.0

================================================================================
RESULTS SUMMARY
================================================================================
Version              Mean        StdDev          Min          Max       Change
--------------------------------------------------------------------------------
0.6.0             245.23ms      12.34ms     232.10ms     265.87ms    (baseline)
0.7.0             258.45ms      15.67ms     241.32ms     282.11ms         +5.4%
0.8.0             271.89ms      13.21ms     255.43ms     289.76ms        +10.9%
0.9.0             283.12ms      18.45ms     262.34ms     308.92ms        +15.5%
0.10.0            295.67ms      16.78ms     275.21ms     320.45ms        +20.6%
================================================================================

Results saved to import_benchmark_results.jsonl
```

### Interpretation

- **Baseline comparison**: The first version tested is used as the baseline (0%)
- **Percentage change**: Shows how much slower/faster each version is compared to baseline
- **Trend analysis**: Track whether import time is increasing over releases
- **Results persistence**: All results are saved to `import_benchmark_results.jsonl` for historical tracking

### Notes

- The script automatically restores your original marimo version after testing
- Each import is measured in a fresh subprocess to avoid caching effects
- More iterations provide more accurate results but take longer to run
- Results may vary based on your system and Python environment
