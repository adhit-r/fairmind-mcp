# Performance Benchmarking Guide

## Overview

The benchmarking suite measures key performance metrics for FairMind MCP:

- **Token Savings**: TOON vs JSON format comparison
- **Latency**: Response times for different tools and content sizes
- **Throughput**: Requests per second under load
- **Success Rate**: Reliability metrics

## Running Benchmarks

```bash
# Run full benchmark suite
bun run test:benchmark
```

## What Gets Measured

### 1. Content Size Impact
Tests `evaluate_bias` with:
- Small content (~50 words)
- Medium content (~100 words)
- Large content (~200 words)
- Code samples

### 2. Tool Performance Comparison
Benchmarks all major tools:
- `evaluate_bias`
- `generate_counterfactuals`
- `evaluate_bias_advanced`

### 3. Token Savings Analysis
Compares TOON vs JSON encoding:
- Token count estimation (1 token ≈ 4 characters)
- Percentage savings
- Real-world impact

### 4. Throughput Test
Measures concurrent request handling:
- 10 concurrent requests
- Requests per second
- Error rate

## Expected Results

### Target Metrics

- **Latency**: P95 < 1.5s for <500 word audits
- **Token Savings**: >30% reduction vs JSON
- **Throughput**: >5 requests/second
- **Success Rate**: >95%

### Sample Output

```
Tool Performance:
  evaluate_bias:
    Avg Latency: 234.56ms
    Avg Token Savings: 42.3%
    Success Rate: 100.0%

Overall Metrics:
  Average Latency: 245.12ms
  P95 Latency: 456.78ms
  Average Token Savings: 38.5%
  Throughput: 6.23 req/s
```

## Interpreting Results

### Latency
- **< 200ms**: Excellent
- **200-500ms**: Good
- **500-1000ms**: Acceptable
- **> 1000ms**: Needs optimization

### Token Savings
- **> 40%**: Excellent (TOON working well)
- **30-40%**: Good
- **20-30%**: Acceptable
- **< 20%**: May need format optimization

### Throughput
- **> 10 req/s**: Excellent
- **5-10 req/s**: Good
- **2-5 req/s**: Acceptable
- **< 2 req/s**: May need optimization

## Troubleshooting

### High Latency
- Check Python process startup time
- Verify network latency (if using remote models)
- Check for blocking operations

### Low Token Savings
- Verify TOON encoding is being used
- Check response payload size
- Consider optimizing response structure

### Low Throughput
- Check Python bridge queue handling
- Verify no blocking operations
- Consider connection pooling

## Continuous Benchmarking

Add to CI/CD pipeline:

```yaml
- name: Run Performance Benchmarks
  run: bun run test:benchmark
  continue-on-error: true
```

## Next Steps

1. **Baseline Establishment**: Run benchmarks to establish current performance
2. **Optimization**: Identify bottlenecks and optimize
3. **Regression Testing**: Run benchmarks on each PR to catch regressions
4. **Documentation**: Update performance targets based on real data

