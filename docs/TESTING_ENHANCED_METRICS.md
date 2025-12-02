# Testing Enhanced Metrics Features

This guide shows how to test all the new enhanced metrics features including Fairlearn MetricFrame, AIF360, multi-attribute detection, and LiteRT model loading.

## Quick Test (5 minutes)

### 1. Install Dependencies

```bash
cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
cd py_engine
uv sync  # This will install aif360 if not already installed
```

### 2. Test Python Components Directly

```bash
# Test enhanced metrics functions
cd py_engine
python3 -c "
from auditor import evaluate_bias_advanced, evaluate_multi_attribute_bias, evaluate_bias_with_metricframe
import json

# Test multi-attribute detection
result = evaluate_multi_attribute_bias(
    'Nurses are gentle women who care for patients',
    ['gender', 'age'],
    'generative'
)
print('Multi-attribute test:', json.dumps(result, indent=2))

# Test advanced evaluation
result = evaluate_bias_advanced(
    'Nurses are gentle women',
    ['gender'],
    'generative',
    use_metricframe=True
)
print('\nAdvanced evaluation test:', json.dumps(result, indent=2))
"
```

## Testing Methods

### Method 1: Web UI (Easiest)

```bash
cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
bun run ui
```

Then open http://localhost:3000 and test:
- `evaluate_bias` with multiple attributes
- `evaluate_bias_advanced` with MetricFrame enabled

### Method 2: Python Direct Testing

Create a test script:

```bash
cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
cat > test_enhanced_metrics.py << 'EOF'
#!/usr/bin/env python3
"""Test enhanced metrics features"""
import sys
import json
sys.path.insert(0, 'py_engine')

from auditor import (
    evaluate_bias_advanced,
    evaluate_multi_attribute_bias,
    evaluate_bias_with_metricframe
)

print("=" * 60)
print("Testing Enhanced Metrics Features")
print("=" * 60)

# Test 1: Multi-attribute detection
print("\n1. Testing Multi-Attribute Detection")
print("-" * 60)
result = evaluate_multi_attribute_bias(
    "Seeking a young, energetic female nurse",
    ["gender", "age"],
    "generative"
)
print(json.dumps(result, indent=2))

# Test 2: Advanced evaluation with MetricFrame
print("\n2. Testing Advanced Evaluation with MetricFrame")
print("-" * 60)
result = evaluate_bias_advanced(
    "Nurses are gentle women who care for patients",
    ["gender"],
    "generative",
    use_metricframe=True,
    use_aif360=False
)
print(json.dumps(result, indent=2))

# Test 3: MetricFrame directly
print("\n3. Testing MetricFrame Directly")
print("-" * 60)
result = evaluate_bias_with_metricframe(
    "Nurses are gentle women",
    "gender",
    "generative"
)
print(json.dumps(result, indent=2))

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
EOF

python3 test_enhanced_metrics.py
```

### Method 3: MCP Tool Testing (Claude Desktop/Cursor)

#### Test 1: Multi-Attribute Detection

**In Claude Desktop or Cursor:**

```
Please test this text for bias across multiple attributes:

Text: "Seeking a young, energetic female nurse"

Use evaluate_bias with protected_attributes=["gender", "age"] to check for intersectional bias.
```

**Expected**: Should detect both gender and age bias, plus intersectional bias.

#### Test 2: Advanced Evaluation

```
Please use evaluate_bias_advanced to test this text with full MetricFrame analysis:

Text: "Nurses are gentle women who care for patients"
Protected attributes: ["gender"]
Use MetricFrame: true
```

**Expected**: Should return statistical metrics (DPD, EOD) in addition to heuristic results.

#### Test 3: Backward Compatibility

```
Please evaluate this text for gender bias using the basic evaluate_bias tool:

"Nurses are gentle women"
```

**Expected**: Should work exactly as before (backward compatible).

### Method 4: Using Test Script

```bash
cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
bun run test:enhanced-metrics
```

## Test Cases

### Test Case 1: Multi-Attribute Detection

**Input**:
```json
{
  "content": "Seeking a young, energetic female nurse",
  "protected_attributes": ["gender", "age"],
  "task_type": "generative"
}
```

**Expected Output**:
- Status: FAIL
- Per-attribute results for both gender and age
- Intersectional bias detected
- Pass rate < 100%

### Test Case 2: Advanced Evaluation with MetricFrame

**Input**:
```json
{
  "content": "Nurses are gentle women",
  "protected_attributes": ["gender"],
  "task_type": "generative",
  "use_metricframe": true
}
```

**Expected Output**:
- Basic evaluation results
- MetricFrame results with DPD, EOD metrics
- Group-wise breakdowns
- Method: "metricframe"

### Test Case 3: Backward Compatibility

**Input**:
```json
{
  "content": "Nurses are gentle women",
  "protected_attribute": "gender",
  "task_type": "generative"
}
```

**Expected Output**:
- Should work exactly as before
- Single attribute evaluation
- Heuristic-based results

### Test Case 4: AIF360 (Classification Tasks)

**Note**: AIF360 requires actual predictions and labels, not just text.

**Input** (requires actual data):
```python
from auditor import evaluate_with_aif360
import numpy as np

y_true = np.array([0, 1, 0, 1, 0])
y_pred = np.array([0, 1, 1, 1, 0])
sensitive_features = np.array(['male', 'female', 'male', 'female', 'male'])

result = evaluate_with_aif360(y_true, y_pred, sensitive_features)
```

**Expected Output**:
- AIF360 metrics (Equalized Odds, Demographic Parity, etc.)
- Status based on thresholds

## Verification Checklist

- [ ] Multi-attribute detection works
- [ ] Intersectional bias is detected
- [ ] MetricFrame provides statistical metrics
- [ ] Advanced evaluation combines multiple methods
- [ ] Backward compatibility maintained
- [ ] AIF360 works (if classification data available)
- [ ] LiteRT model loading framework works (falls back gracefully)

## Troubleshooting

### AIF360 Not Available

If you see warnings:
```bash
cd py_engine
uv sync  # Reinstall dependencies
```

### MetricFrame Falls Back to Heuristics

This is expected if:
- Text doesn't have enough bias patterns
- Protected attribute not supported
- Not enough data for statistical analysis

### Models Not Loading

LiteRT models are optional. The system will:
1. Check for models in `py_engine/models/`
2. Fall back to heuristics if none found
3. This is expected behavior

## Performance Testing

```bash
# Test performance with multiple attributes
time python3 -c "
from auditor import evaluate_bias_advanced
result = evaluate_bias_advanced(
    'Nurses are gentle women',
    ['gender', 'race', 'age'],
    'generative',
    use_metricframe=True
)
"
```

Expected: < 1 second for most cases

## Integration Testing

Test with actual MCP client:

```bash
# Start MCP server
bun run src/index.ts

# In another terminal, test via MCP protocol
# (Use Claude Desktop or Cursor for full integration testing)
```

## Next Steps

1. Test each feature individually
2. Test combinations of features
3. Test edge cases (empty text, no bias, etc.)
4. Test performance with large batches
5. Test in production-like scenarios




