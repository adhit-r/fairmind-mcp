# Enhanced Metrics Features

FairMind MCP now supports advanced statistical fairness metrics beyond heuristic-based detection, including full Fairlearn MetricFrame integration, AIF360 support, multi-attribute detection, and LiteRT model loading.

## Overview

The enhanced metrics features provide:

1. **Full Fairlearn MetricFrame Integration** - Statistical rigor for generative tasks
2. **AIF360 ClassificationMetric Support** - Comprehensive fairness analysis
3. **Multi-Attribute Detection** - Check multiple protected attributes simultaneously
4. **LiteRT Model Loading** - Actual ML models for counterfactual generation

## Tools

### 1. `evaluate_bias` (Enhanced)

The existing `evaluate_bias` tool now supports multiple attributes while maintaining backward compatibility.

**Single Attribute (Backward Compatible)**:
```typescript
{
  content: "Nurses are gentle women",
  protected_attribute: "gender",
  task_type: "generative"
}
```

**Multiple Attributes**:
```typescript
{
  content: "Nurses are gentle women",
  protected_attributes: ["gender", "age"],
  task_type: "generative"
}
```

**Features**:
- Detects intersectional bias when multiple attributes fail
- Per-attribute results with combined status
- Backward compatible with single attribute usage

### 2. `evaluate_bias_advanced` (New)

Advanced evaluation with full MetricFrame and AIF360 support.

**Input Schema**:
```typescript
{
  content: string,
  protected_attributes: string[],      // Multiple attributes required
  task_type: 'generative' | 'classification',
  use_metricframe?: boolean,            // Default: true
  use_aif360?: boolean,                 // Default: false
  metric_names?: string[],              // Custom metrics
  content_type?: 'text' | 'code'       // Default: 'text'
}
```

**Example**:
```typescript
{
  content: "Nurses are gentle women who care for patients",
  protected_attributes: ["gender", "age"],
  task_type: "generative",
  use_metricframe: true,
  use_aif360: false
}
```

**Output**:
- Per-attribute results with basic and MetricFrame analysis
- Multi-attribute intersectional bias detection
- Statistical metrics (DPD, EOD, Demographic Parity Ratio)
- Group-wise metric breakdowns

## Metrics Available

### Fairlearn Metrics

- **Demographic Parity Difference (DPD)**: Measures selection rate differences
- **Equalized Odds Difference (EOD)**: Measures true/false positive rate differences
- **Demographic Parity Ratio (DPR)**: Ratio of selection rates
- **Selection Rate**: Proportion of positive predictions
- **True Positive Rate**: Sensitivity/recall
- **False Positive Rate**: Fallout
- **True Negative Rate**: Specificity
- **False Negative Rate**: Miss rate

### AIF360 Metrics

- **Equalized Odds**: Fairness metric for equalized odds
- **Demographic Parity**: Statistical parity difference
- **Average Odds Difference**: Average of TPR and FPR differences

## Use Cases

### Use Case 1: Multi-Attribute Detection

Check for bias across multiple protected attributes simultaneously:

```python
# Using evaluate_bias with multiple attributes
result = evaluate_bias(
    content="Seeking a young, energetic nurse",
    protected_attributes=["gender", "age"],
    task_type="generative"
)

# Result includes:
# - Per-attribute analysis
# - Intersectional bias detection
# - Combined status
```

### Use Case 2: Statistical Rigor with MetricFrame

Use statistical metrics instead of just heuristics:

```python
# Using evaluate_bias_advanced with MetricFrame
result = evaluate_bias_advanced(
    content="Nurses are gentle women",
    protected_attributes=["gender"],
    task_type="generative",
    use_metricframe=True
)

# Result includes:
# - Statistical metrics (DPD, EOD, DPR)
# - Group-wise breakdowns
# - MetricFrame summary
```

### Use Case 3: Classification Tasks with AIF360

For classification tasks with actual predictions:

```python
# Requires actual predictions and labels
# Use evaluate_bias_with_dataframe for classification tasks
result = evaluate_bias_with_dataframe(
    df=dataframe,
    protected_col="gender",
    target_col="label",
    predictions_col="prediction"
)

# Or use AIF360 directly
aif360_result = evaluate_with_aif360(
    y_true=true_labels,
    y_pred=predictions,
    sensitive_features=protected_attributes
)
```

## When to Use Which Tool

### Use `evaluate_bias` when:
- Quick bias check needed
- Single or multiple attributes
- Heuristic-based detection is sufficient
- Backward compatibility required

### Use `evaluate_bias_advanced` when:
- Statistical rigor needed
- Multiple attributes to check
- Intersectional bias detection required
- MetricFrame analysis desired
- Production-grade evaluation needed

### Use `evaluate_bias_with_dataframe` when:
- Classification tasks with actual predictions
- Full Fairlearn MetricFrame needed
- Group-wise analysis required

## Multi-Attribute Detection

### Intersectional Bias

When checking multiple attributes, the system detects intersectional bias:

```python
result = evaluate_multi_attribute_bias(
    content="Seeking a young female nurse",
    protected_attributes=["gender", "age"],
    task_type="generative"
)

# Detects:
# - Gender bias (female stereotype)
# - Age bias (young stereotype)
# - Intersectional bias (young + female combination)
```

### Output Structure

```json
{
  "status": "FAIL",
  "pass_rate": 50.0,
  "per_attribute": {
    "gender": { "status": "FAIL", ... },
    "age": { "status": "FAIL", ... }
  },
  "intersectional_bias": [
    {
      "attributes": ["gender", "age"],
      "severity": "high",
      "message": "Intersectional bias detected across 2 attributes"
    }
  ],
  "summary": {
    "total_attributes_checked": 2,
    "passed": 0,
    "failed": 2,
    "failed_attributes": ["gender", "age"]
  }
}
```

## MetricFrame for Generative Tasks

For generative tasks, MetricFrame extracts predictions from text patterns:

1. **Pattern Extraction**: Identifies bias indicators in text
2. **Prediction Generation**: Converts patterns to numerical predictions
3. **MetricFrame Creation**: Builds statistical metrics
4. **Group Analysis**: Analyzes by sensitive groups

**Example**:
```python
# Text: "Nurses are gentle women"
# Extracts:
# - Female terms: ["nurse", "gentle", "women"]
# - Male terms: []
# - Creates predictions: [1, 1, 1] (biased)
# - Sensitive features: ["female", "female", "female"]
# - Computes DPD, EOD, etc.
```

## LiteRT Model Loading

The system attempts to load LiteRT models for counterfactual generation:

1. **Model Discovery**: Checks `py_engine/models/` directory
2. **Model Loading**: Loads `.tflite` files if available
3. **Fallback**: Uses heuristics if no model found
4. **Caching**: Caches loaded models for performance

**Model File Naming**:
- `bias_mitigation_{sensitive_group}.tflite`
- `counterfactual_{sensitive_group}.tflite`
- `{sensitive_group}_model.tflite`

**To Add Models**:
1. Place `.tflite` files in `py_engine/models/`
2. Name according to convention
3. Models will be auto-loaded on first use

## Performance Considerations

- **MetricFrame**: Adds ~100-200ms overhead for statistical analysis
- **Multi-Attribute**: Linear scaling with number of attributes
- **AIF360**: Requires actual predictions (not for generative tasks)
- **LiteRT Models**: First load takes time, subsequent uses are cached

## Migration Guide

### From Single to Multiple Attributes

**Before**:
```python
result1 = evaluate_bias(content, "gender", "generative")
result2 = evaluate_bias(content, "age", "generative")
```

**After**:
```python
result = evaluate_bias(
    content=content,
    protected_attributes=["gender", "age"],
    task_type="generative"
)
```

### From Basic to Advanced

**Before**:
```python
result = evaluate_bias(content, "gender", "generative")
```

**After**:
```python
result = evaluate_bias_advanced(
    content=content,
    protected_attributes=["gender"],
    task_type="generative",
    use_metricframe=True
)
```

## Best Practices

1. **Use Advanced for Production**: `evaluate_bias_advanced` provides statistical rigor
2. **Check Multiple Attributes**: Detect intersectional bias
3. **Enable MetricFrame**: Get group-wise breakdowns
4. **Use AIF360 for Classification**: When you have actual predictions
5. **Cache Results**: Store results for comparison over time

## Troubleshooting

### AIF360 Not Available

If you see warnings about AIF360:
```bash
cd py_engine
uv sync  # Installs aif360 dependency
```

### MetricFrame Returns Heuristics

If MetricFrame falls back to heuristics:
- Check that text has enough bias patterns
- Ensure protected attribute is supported
- Verify task_type is 'generative'

### Models Not Loading

If LiteRT models don't load:
- Check `py_engine/models/` directory exists
- Verify model file naming convention
- Check file permissions
- System will fallback to heuristics automatically

## See Also

- [Bias Parameters Reference](./BIAS_PARAMETERS.md) - All detected patterns
- [LLM Testing Guide](./LLM_TESTING_GUIDE.md) - Testing custom models
- [Integration Examples](./INTEGRATION_EXAMPLES.md) - Use case examples

