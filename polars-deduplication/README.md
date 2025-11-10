# Polars Anti-Join vs Alternatives for Deduplication

Benchmark comparing different approaches to single-column deduplication, with a focus on Polars anti-join performance versus Python's built-in `set()`.

## Methods Tested

1. **Polars anti-join** - Using join operations to filter duplicates
2. **Polars anti-join v2** - Alternative anti-join implementation with explicit row indexing
3. **Python set()** - Classic Python approach with order preservation
4. **Polars unique()** - Built-in Polars deduplication method
5. **Polars group_by().first()** - Aggregation-based approach

## Key Findings

### Small Data (1,000 rows)

For small datasets, **Python set() is fastest**:

| Method | Mean Time | Speedup vs set() |
|--------|-----------|------------------|
| Python set() | 0.13ms | 1.00x (baseline) |
| Polars unique() | 0.16ms | 0.81x (slower) |
| Polars group_by() | 1.84ms | 0.07x |
| Polars anti-join | 4.93ms | 0.03x |

**Why?** For small data, the overhead of Polars operations outweighs the benefits. Python's native set() is highly optimized for small collections.

### Medium Data (100,000 rows)

The crossover point where **Polars starts winning**:

| Duplication Rate | Python set() | Polars unique() | Polars group_by() | Best Speedup |
|------------------|--------------|-----------------|-------------------|--------------|
| 10% duplicates | 13.23ms | 2.41ms | 2.10ms | **6.31x** |
| 50% duplicates | 11.02ms | 2.20ms | 1.83ms | **6.01x** |
| 90% duplicates | 7.74ms | 0.86ms | 0.93ms | **8.95x** |

**Pattern:** Higher duplication rates favor Polars even more, as it handles fewer unique values more efficiently.

### Large Data (1,000,000 rows)

Polars dominates for large datasets:

| Duplication Rate | Python set() | Polars unique() | Polars group_by() | Best Speedup |
|------------------|--------------|-----------------|-------------------|--------------|
| 10% duplicates | 217.16ms | 20.29ms | 12.43ms | **17.48x** |
| 50% duplicates | 166.65ms | 14.06ms | 11.86ms | **14.05x** |
| 90% duplicates | 100.45ms | 6.80ms | 5.28ms | **19.01x** |

**Winner:** `group_by().first()` consistently delivers the best performance at scale.

## Anti-Join Performance

While anti-join works for deduplication, it's **not the fastest approach**:

- At 1M rows, anti-join is 5-7x faster than Python set()
- However, it's 2-3x slower than `unique()` or `group_by().first()`
- Anti-join overhead comes from explicit row indexing and multiple operations

## Recommendations

### Use Python set() when:
- Dataset < 10,000 rows
- Working with simple Python lists/iterables
- Don't need Polars DataFrame output

### Use Polars when:
- Dataset > 10,000 rows
- Data is already in a DataFrame
- Need to maintain DataFrame structure
- Performance matters

### Best Polars method:
1. **`group_by().first()`** - Fastest overall (up to 19x vs Python set())
2. **`unique()`** - Close second, slightly simpler syntax
3. **Anti-join** - Works but slower; better suited for comparing two different DataFrames

## Code Examples

### Fastest: Polars group_by().first()
```python
import polars as pl

df = pl.DataFrame({"id": [1, 2, 2, 3, 3, 3]})
result = df.group_by("id").first()
# Result: 3 unique rows
```

### Alternative: Polars unique()
```python
result = df.unique(subset=["id"], keep="first")
```

### Python set() (for small data)
```python
seen = set()
ids = df["id"].to_list()
result = [x for x in ids if x not in seen and not seen.add(x)]
```

## Benchmark Details

- **Test data:** Randomly generated integers with controlled duplication rates
- **Iterations:** 3 runs per configuration with warmup
- **Sizes tested:** 1K, 100K, 1M rows
- **Duplication rates:** 10%, 50%, 90%
- **Hardware:** Single-threaded performance

## Running the Benchmark

```bash
# Install dependencies
pip install polars pandas numpy

# Run with default iterations (5)
python benchmark.py

# Run with custom iterations
python benchmark.py 10
```

Results are saved to `results.jsonl` for further analysis.

## Conclusion

**TL;DR:** For deduplication on single columns:
- Small data (< 10K): Use Python `set()`
- Large data (> 10K): Use Polars `group_by().first()` or `unique()`
- Anti-join is viable but not optimal for deduplication - it's better suited for comparing two different DataFrames

The performance gap widens dramatically with data size. At 1M rows with high duplication, Polars can be **19x faster** than Python's set().
