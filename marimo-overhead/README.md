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
# Test default versions (0.6.0, 0.7.0, 0.8.0, 0.9.0, 0.10.0, 0.12.0, 0.14.0, 0.16.0, 0.17.0) with 10 iterations
python benchmark_import.py

# Test with more iterations for better accuracy
python benchmark_import.py 20

# Test specific versions
python benchmark_import.py 10 0.8.0 0.9.0 0.10.0 0.17.0

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

Actual benchmark results (10 iterations each):

```
Marimo Import Time Benchmark
Testing 9 version(s) with 10 iterations each

Versions to test: 0.6.0, 0.7.0, 0.8.0, 0.9.0, 0.10.0, 0.12.0, 0.14.0, 0.16.0, 0.17.0

===============================================================================================
RESULTS SUMMARY
===============================================================================================
Version      Mean         StdDev       Variance      Min          Max          Change
-----------------------------------------------------------------------------------------------
0.6.0          636.53ms     21.01ms     441.33ms²    593.74ms    663.05ms    (baseline)
0.7.0          747.45ms     50.85ms    2585.95ms²    683.01ms    853.74ms        +17.4%
0.8.0          793.73ms     30.24ms     914.55ms²    753.57ms    838.83ms        +24.7%
0.9.0          834.31ms     26.98ms     727.67ms²    803.35ms    889.64ms        +31.1%
0.10.0         732.10ms     32.12ms    1031.42ms²    669.83ms    770.54ms        +15.0%
0.12.0         841.36ms     21.01ms     441.51ms²    821.04ms    893.32ms        +32.2%
0.14.0        1038.94ms     40.86ms    1669.91ms²    967.42ms   1107.10ms        +63.2%
0.16.0        1069.03ms     53.14ms    2824.32ms²    987.42ms   1165.92ms        +67.9%
0.17.0        1082.62ms     49.48ms    2448.67ms²    998.77ms   1135.77ms        +70.1%
===============================================================================================

Results saved to import_benchmark_results.jsonl
```

### Interpretation

Key findings from the benchmark:

- **Import time trend**: Import time has increased significantly from 0.6.0 (636ms) to 0.17.0 (1083ms), a **70% increase**
- **Version 0.10.0 optimization**: Version 0.10.0 (732ms) showed a 12% improvement over 0.9.0 (834ms), indicating deliberate optimization work
- **Major jump at 0.14.0**: There was a significant increase from 0.12.0 (841ms) to 0.14.0 (1039ms) - a 24% jump, suggesting new features or dependencies were added
- **Variance analysis**: Most versions have relatively low variance (400-1000ms²), with 0.7.0 and 0.16.0 showing higher variance (2500-2800ms²)
- **Baseline comparison**: All comparisons are relative to the first version tested (0.6.0 as baseline)
- **Results persistence**: All results are saved to `import_benchmark_results.jsonl` for historical tracking

### Notes

- The script automatically restores your original marimo version after testing
- Each import is measured in a fresh subprocess to avoid caching effects
- More iterations provide more accurate results but take longer to run
- Results may vary based on your system and Python environment
