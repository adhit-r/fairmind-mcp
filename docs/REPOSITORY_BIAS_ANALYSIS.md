# Repository Bias Analysis

## Overview

The `analyze_repository_bias` tool analyzes entire git repositories to detect bias patterns across all commits and authors. It maps how each code author is biased, explains why, and provides comprehensive scorecards.

## Use Cases

- **Code Review**: Identify authors who consistently introduce biased code
- **Team Analysis**: Understand bias patterns across your development team
- **Compliance**: Generate reports for diversity and inclusion audits
- **Training**: Identify which developers need bias awareness training
- **Pattern Recognition**: Detect systemic bias in codebase over time

## Features

1. **Git History Analysis**: Parses entire commit history (handles 1000s of commits)
2. **Author Tracking**: Maps bias patterns to individual authors (handles 100s of users)
3. **Scorecard Generation**: Creates detailed bias scorecards per author
4. **Pattern Recognition**: Identifies common bias patterns and explains why they occur
5. **Trend Analysis**: Shows bias patterns over time

## Usage

### Basic Usage

```typescript
{
  "repository_path": "/path/to/repo",
  "protected_attributes": ["gender", "race", "age", "disability"]
}
```

### Advanced Usage

```typescript
{
  "repository_path": "/path/to/repo",
  "protected_attributes": ["gender", "race"],
  "max_commits": 1000,  // Limit analysis to last 1000 commits
  "min_commits_per_author": 10,  // Only analyze authors with 10+ commits
  "file_extensions": [".js", ".ts", ".py"],  // Only analyze these file types
  "exclude_paths": ["node_modules/", "vendor/", "dist/"]  // Exclude these paths
}
```

## Output Format

### Author Scorecard

Each author gets a detailed scorecard:

```json
{
  "author_name": "John Doe",
  "author_email": "john@example.com",
  "total_commits": 150,
  "overall_bias_score": 65.3,
  "bias_level": "HIGH",
  "severity": "critical",
  "attribute_scores": {
    "gender": {
      "fail_rate": 0.45,
      "fail_count": 68,
      "total_commits": 150,
      "bias_score": 45
    },
    "race": {
      "fail_rate": 0.12,
      "fail_count": 18,
      "total_commits": 150,
      "bias_score": 12
    }
  },
  "attribute_patterns": {
    "gender": [
      {
        "metric": "Comment_Gender_Bias",
        "value": 0.89,
        "commit_hash": "a1b2c3d4",
        "date": "2024-01-15T10:30:00"
      }
    ]
  },
  "explanations": [
    "Gender bias detected in 68/150 commits (45.0%). Common patterns: Comment_Gender_Bias, Hardcoded_Gender_Assumptions"
  ],
  "recommendations": [
    "CRITICAL: Immediate code review and bias training recommended",
    "High bias rate detected - consider pair programming and bias-aware code review"
  ],
  "first_commit": "2023-01-15T10:30:00",
  "last_commit": "2024-01-28T14:20:00"
}
```

### Repository Summary

```json
{
  "analysis_summary": {
    "total_commits_analyzed": 5234,
    "total_authors": 87,
    "protected_attributes": ["gender", "race", "age", "disability"],
    "analysis_date": "2024-01-28T15:30:00"
  },
  "repository_bias_summary": {
    "gender": {
      "total_failures": 1234,
      "failure_rate": 0.236
    },
    "race": {
      "total_failures": 456,
      "failure_rate": 0.087
    }
  },
  "top_biased_authors": [...],  // Top 10 authors by bias score
  "least_biased_authors": [...]  // Bottom 10 authors (least biased)
}
```

## Bias Score Interpretation

- **0-20**: MINIMAL bias - Excellent
- **20-40**: LOW bias - Good, minor improvements needed
- **40-70**: MEDIUM bias - Needs attention and training
- **70-100**: HIGH bias - Critical, immediate action required

## Performance

- **Small repos** (< 100 commits): ~10-30 seconds
- **Medium repos** (100-1000 commits): ~1-5 minutes
- **Large repos** (1000+ commits): ~5-15 minutes (can be limited with `max_commits`)

## Limitations

1. **Git Required**: Repository must be a valid git repository
2. **Performance**: Large repositories may take significant time
3. **File Types**: Only analyzes code files (not binary files)
4. **Diff Size**: Limits diff analysis to first 5000 characters per commit
5. **Author Threshold**: Authors with fewer than `min_commits_per_author` are excluded

## Best Practices

1. **Start Small**: Test with `max_commits: 100` first
2. **Filter Files**: Use `file_extensions` to focus on relevant code
3. **Exclude Paths**: Exclude generated/vendor code
4. **Review Results**: Scorecards are starting points, not definitive judgments
5. **Privacy**: Be mindful of author email addresses in results

## Example: Analyzing Your Own Repository

```bash
# In Cursor or Claude Desktop
"Analyze this repository for bias: /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp"
```

The tool will:
1. Parse all git commits
2. Analyze each commit for bias
3. Group by author
4. Generate scorecards
5. Provide recommendations

## Integration with CI/CD

You can integrate this into your CI/CD pipeline:

```yaml
- name: Repository Bias Analysis
  run: |
    # Use MCP tool to analyze repository
    # Generate report
    # Fail build if bias score > threshold
```

## Privacy Considerations

- Author emails are included in results
- Consider anonymizing results before sharing
- Use for internal team improvement, not public shaming
- Focus on patterns, not individuals

