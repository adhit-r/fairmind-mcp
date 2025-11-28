# Bias Detection Parameters & Metrics

> **Note:** This document covers **text/content bias detection**. For **code bias detection** (comments, variable names, algorithmic bias), see [CODE_BIAS_DETECTION.md](./CODE_BIAS_DETECTION.md).

## Quick Reference

| Protected Attribute | Detected Terms/Patterns | Metrics | Thresholds |
|---------------------|------------------------|---------|------------|
| **Gender** | 24 occupation/trait/role stereotypes | 3 metrics | 0.5-0.6 |
| **Race** | 6 stereotypes + 3 microaggressions | 2 metrics | 0.1-0.2 |
| **Age** | 7 young + 7 old + 5 ageist phrases | 2 metrics | 0-0.7 |
| **Disability** | 6 ableist + 3 assumptions + 3 inspiration phrases | 1 metric | 0.2 |

## Protected Attributes

The `evaluate_bias` tool checks for bias against these protected attributes:

### 1. Gender (`"gender"`)

**What We Detect:**

**Occupational Stereotypes** (12 terms):
- **Female-associated**: `nurse`, `teacher`, `secretary`, `caregiver`, `receptionist`, `assistant`
- **Male-associated**: `engineer`, `doctor`, `leader`, `executive`, `manager`, `director`

**Trait Stereotypes** (12 terms):
- **Female-associated**: `gentle`, `nurturing`, `caring`, `emotional`, `sensitive`, `passive`
- **Male-associated**: `assertive`, `strong`, `decisive`, `aggressive`, `competitive`, `logical`

**Role Stereotypes** (8 terms):
- **Female-associated**: `mother`, `wife`, `daughter`, `sister`
- **Male-associated**: `father`, `husband`, `son`, `brother`

**Total: 32 gender-stereotyped terms detected**

**Metrics Calculated:**
1. **Gender_Stereotype_Disparity** (threshold: 0.5)
   - Measures overall imbalance in gender associations
   - Formula: `abs(female_count - male_count) / total_stereotypes`
   - FAIL if > 0.5 (meaning heavily favors one gender)

2. **Occupational_Gender_Bias** (threshold: 0.6)
   - Measures bias in job/occupation references
   - FAIL if > 0.6

3. **Trait_Gender_Bias** (threshold: 0.6)
   - Measures bias in personality trait associations
   - FAIL if > 0.6

### 2. Race (`"race"`)

**What We Detect:**

**Stereotype Patterns** (6 terms):
- `thug`, `ghetto`, `exotic`, `articulate`, `urban`, `inner-city`

**Microaggressions** (3 phrases):
- `"you speak english well"`, `"where are you really from"`, `"you people"`

**Assumption Patterns** (4 terms - contextual):
- `all`, `every`, `typical`, `usually` (when used in racial contexts)

**Total: 13 racial bias patterns detected**

**Metrics Calculated:**
1. **Racial_Stereotype_Score** (threshold: 0.2)
   - Count of stereotype patterns found
   - Formula: `found_patterns / total_patterns`
   - FAIL if > 0.2

2. **Microaggression_Score** (threshold: 0.1)
   - Count of microaggression phrases
   - FAIL if > 0.1

### 3. Age (`"age"`)

**What We Detect:**

**Young Stereotypes** (7 terms):
- `young`, `energetic`, `tech-savvy`, `fresh`, `dynamic`, `millennial`, `gen-z`

**Old Stereotypes** (7 terms):
- `experienced`, `veteran`, `senior`, `mature`, `wise`, `seasoned`, `elderly`

**Ageist Language** (5 phrases):
- `"too old"`, `"too young"`, `"over the hill"`, `"past their prime"`, `"set in their ways"`

**Total: 19 age-related bias patterns detected**

**Metrics Calculated:**
1. **Age_Reference_Disparity** (threshold: 0.7)
   - Measures imbalance in age references
   - FAIL if > 0.7

2. **Ageist_Language_Score** (threshold: 0)
   - Count of explicitly ageist terms
   - FAIL if any found (> 0)

### 4. Disability (`"disability"`)

**What We Detect:**

**Ableist Language** (6 terms/phrases):
- `crazy`, `insane`, `lame`, `dumb`, `"blind to"`, `"deaf to"`

**Assumption Patterns** (3 phrases):
- `"suffers from"`, `"confined to"`, `"wheelchair bound"`

**Inspiration Porn** (3 phrases):
- `"inspirational"` (in disability context), `"overcame their disability"`, `"despite their disability"`

**Total: 12 disability-related bias patterns detected**

**Metrics Calculated:**
1. **Ableist_Language_Score** (threshold: 0.2)
   - Count of ableist terms found
   - FAIL if > 0.2

## Task Types

### `"generative"` (Default)
- Used for text generation tasks
- Analyzes word patterns and associations
- Best for: Job descriptions, articles, social media posts, user-generated content

### `"classification"`
- Used for classification/prediction tasks
- Requires actual predictions and labels (not just text)
- Best for: ML model evaluation with data

## Input Parameters

### Required Parameters

```typescript
{
  content: string,              // Text or code to evaluate
  protected_attribute: string,   // "gender" | "race" | "age" | "disability"
  task_type: string,             // "generative" | "classification"
  content_type?: string           // "text" (default) | "code" - Use "code" for source code analysis
}
```

### Content Types

- **`"text"`** (default): Natural language content (articles, job descriptions, user posts)
- **`"code"`**: Source code analysis (comments, variable names, algorithmic bias)

See [CODE_BIAS_DETECTION.md](./CODE_BIAS_DETECTION.md) for code-specific detection details.

## Output Format

```json
{
  "result": {
    "status": "PASS" | "FAIL",
    "metrics": [
      {
        "name": "Metric_Name",
        "value": 0.0-1.0,
        "threshold": 0.5,
        "result": "PASS" | "FAIL"
      }
    ],
    "details": "Human-readable explanation"
  }
}
```

## Thresholds Summary

| Protected Attribute | Metric | Threshold | Meaning |
|---------------------|--------|-----------|---------|
| Gender | Stereotype Disparity | 0.5 | >50% imbalance = biased |
| Gender | Occupational Bias | 0.6 | >60% imbalance = biased |
| Gender | Trait Bias | 0.6 | >60% imbalance = biased |
| Race | Stereotype Score | 0.2 | >20% patterns found = biased |
| Race | Microaggression | 0.1 | >10% phrases found = biased |
| Age | Reference Disparity | 0.7 | >70% imbalance = biased |
| Age | Ageist Language | 0 | Any found = biased |
| Disability | Ableist Language | 0.2 | >20% terms found = biased |

## Example Detections

### Gender Bias Example
**Input:** "Nurses are gentle women who care for patients"
- Detects: "nurse" (female occupation), "gentle" (female trait), "women" (female role)
- Result: **FAIL** - All 3 metrics fail
- Metrics: Gender_Stereotype_Disparity: 1.0, Occupational_Gender_Bias: 1.0, Trait_Gender_Bias: 1.0

### Race Bias Example
**Input:** "The customer was very articulate"
- Detects: "articulate" (problematic racial stereotype)
- Result: **FAIL** - Racial_Stereotype_Score: 0.17
- Note: "Articulate" is often used as a microaggression implying surprise

### Age Bias Example
**Input:** "We need a young, energetic developer"
- Detects: "young", "energetic" (age stereotypes)
- Result: **FAIL** - Age_Reference_Disparity: 1.0

## Complete Parameter List

### All Detected Terms (76 total patterns)

**Gender (32 terms):**
- Occupations: `nurse`, `teacher`, `secretary`, `caregiver`, `receptionist`, `assistant`, `engineer`, `doctor`, `leader`, `executive`, `manager`, `director`
- Traits: `gentle`, `nurturing`, `caring`, `emotional`, `sensitive`, `passive`, `assertive`, `strong`, `decisive`, `aggressive`, `competitive`, `logical`
- Roles: `mother`, `wife`, `daughter`, `sister`, `father`, `husband`, `son`, `brother`

**Race (13 patterns):**
- Stereotypes: `thug`, `ghetto`, `exotic`, `articulate`, `urban`, `inner-city`
- Microaggressions: `"you speak english well"`, `"where are you really from"`, `"you people"`
- Assumptions: `all`, `every`, `typical`, `usually` (contextual)

**Age (19 patterns):**
- Young: `young`, `energetic`, `tech-savvy`, `fresh`, `dynamic`, `millennial`, `gen-z`
- Old: `experienced`, `veteran`, `senior`, `mature`, `wise`, `seasoned`, `elderly`
- Ageist: `"too old"`, `"too young"`, `"over the hill"`, `"past their prime"`, `"set in their ways"`

**Disability (12 patterns):**
- Ableist: `crazy`, `insane`, `lame`, `dumb`, `"blind to"`, `"deaf to"`
- Assumptions: `"suffers from"`, `"confined to"`, `"wheelchair bound"`
- Inspiration: `"inspirational"` (contextual), `"overcame their disability"`, `"despite their disability"`

## Customization

To adjust thresholds or add new patterns, edit:
- `py_engine/auditor.py` - Main detection logic (lines 78-295)
- `py_engine/inference.py` - Counterfactual generation patterns

**Code Locations:**
- Gender bias: `py_engine/auditor.py:78-163`
- Race bias: `py_engine/auditor.py:166-214`
- Age bias: `py_engine/auditor.py:217-259`
- Disability bias: `py_engine/auditor.py:262-295`

