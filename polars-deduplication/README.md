# Polars Anti-Join for Filtering New Items Against Seen Items

Benchmark comparing different approaches to filter incoming items against an existing "seen" set.

**Use Case:** You have a set of items you've already processed (the "seen" set), and new items come in. You want to identify which new items you haven't seen before.

## Methods Tested

1. **Polars anti-join** - `new_df.join(seen_df, on="id", how="anti")` (designed for this!)
2. **Python set difference** - `new_set - seen_set`
3. **Python set comprehension** - `[x for x in new if x not in seen]` (order-preserving)
4. **Polars is_in() filter** - `new_df.filter(~pl.col("id").is_in(seen_ids))`

## Key Findings

### Small Data (< 10K items)

For small datasets, **Python set comprehension is fastest**:

| Seen | New | Overlap | Python set | Polars anti-join | Speedup |
|------|-----|---------|------------|------------------|---------|
| 1K | 1K | 50% | 0.12ms | 0.75ms | 0.16x (slower) |
| 1K | 10K | 50% | 0.69ms | 0.95ms | 0.73x (slower) |

**Why?** For small data, Python's native set operations have less overhead.

### Medium Data (100K seen items)

**Polars starts dominating:**

| Seen | New | Overlap | Python set | Polars anti-join | Speedup |
|------|-----|---------|------------|------------------|---------|
| 100K | 10K | 50% | 5.11ms | 1.24ms | **4.13x** |
| 100K | 100K | 50% | 16.40ms | 1.85ms | **8.87x** |
| 100K | 100K | 90% | 14.10ms | 1.67ms | **8.43x** |

The crossover point is around 100K seen items - after this, Polars is consistently faster.

### Large Data (1M seen items)

**Polars anti-join destroys Python set:**

| Seen | New | Overlap | Python set | Polars anti-join | Speedup |
|------|-----|---------|------------|------------------|---------|
| 1M | 100K | 50% | 128.31ms | 5.95ms | **21.57x** |
| 1M | 1M | 50% | 268.09ms | 12.17ms | **22.02x** |
| 1M | 1M | 90% | 326.60ms | 10.34ms | **31.58x** |

At 1M seen items with high overlap, **anti-join is 32x faster** than Python!

## Why Anti-Join Wins

1. **Optimized hash joins** - Polars uses efficient hash-based joins under the hood
2. **No Python overhead** - Operations stay in Rust, avoiding Python list conversions
3. **Memory efficient** - Doesn't need to materialize intermediate Python lists
4. **Scales beautifully** - Performance gap increases with data size

## Pattern Analysis

**Key insight:** The size of the "seen" set matters most!

- Small seen set (< 10K): Python set is fine
- Medium seen set (100K): Anti-join is 4-8x faster
- Large seen set (1M+): Anti-join is 20-30x faster

**Overlap rate** has minimal impact - anti-join is fast regardless.

## Recommendations

### Use Python set when:
- Seen set < 10K items
- Working with simple Python lists
- One-off script with no Polars dependency

### Use Polars anti-join when:
- Seen set > 10K items (use it!)
- Seen set > 100K items (definitely use it!)
- Data already in DataFrames
- Performance matters
- Processing batches repeatedly

### Second best: Polars is_in()
- 3-4x slower than anti-join
- But still 6-10x faster than Python set for large data
- Simpler syntax if you prefer filtering

## Code Examples

### Best: Polars Anti-Join (22-32x faster)
```python
import polars as pl

# Your existing seen items
seen_df = pl.DataFrame({"id": [1, 2, 3, 4, 5]})

# New batch of items comes in
new_df = pl.DataFrame({"id": [3, 4, 5, 6, 7, 8]})

# Find items you haven't seen before
unseen = new_df.join(seen_df, on="id", how="anti")
# Result: [6, 7, 8]
```

### Alternative: Polars is_in() (6-10x faster)
```python
seen_ids = seen_df["id"]
unseen = new_df.filter(~pl.col("id").is_in(seen_ids))
```

### Python set (baseline - works for small data)
```python
seen_set = set(seen_df["id"].to_list())
new_ids = new_df["id"].to_list()
unseen = [x for x in new_ids if x not in seen_set]
```

## Practical Example

Imagine processing a stream of user events:

```python
import polars as pl

# Initialize seen events (load from database/cache)
seen_events = pl.DataFrame({"event_id": [...]})  # 1M events

# New batch arrives
new_batch = pl.DataFrame({"event_id": [...]})  # 100K events

# Filter to only unseen events (5.95ms with anti-join vs 128ms with Python)
unseen_events = new_batch.join(seen_events, on="event_id", how="anti")

# Process only the unseen events
process(unseen_events)

# Update seen set for next batch
seen_events = pl.concat([seen_events, unseen_events])
```

## Benchmark Details

- **Test configurations:** Various combinations of seen/new sizes and overlap rates
- **Iterations:** 3 runs per configuration with warmup
- **Seen sizes:** 1K, 100K, 1M items
- **New batch sizes:** 1K to 1M items
- **Overlap rates:** 50%, 90% (how many new items are duplicates)

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

**TL;DR:** For filtering new items against a seen set:
- **Small seen set (< 10K):** Python set comprehension is fine
- **Medium seen set (100K):** Use Polars anti-join (8x faster)
- **Large seen set (1M+):** Use Polars anti-join (20-30x faster!)

This is exactly what anti-join was designed for. Unlike self-deduplication (where `unique()` or `group_by()` are better), comparing two different datasets is where anti-join truly shines.

The performance gap is dramatic: at scale, **Polars anti-join can be 30x faster** than Python's set operations.
