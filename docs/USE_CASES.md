# FairMind Use Cases - Practical Examples

## Overview

FairMind MCP can be used in many real-world scenarios. This guide provides practical examples for common use cases.

---

## 1. Self-Checking: Have Claude Review Its Own Outputs

### Use Case
Before Claude sends a response, have it check its own text for bias to ensure fair and inclusive communication.

### Example Workflow

**Scenario 1: Job Description Generation**
```
User: Write a job description for a software engineer position.

Claude: [Generates job description]

User: Now check that job description for gender and race bias.

Claude: [Uses evaluate_bias tool, finds issues, suggests improvements]
```

**Scenario 2: Content Generation with Self-Review**
```
User: Write a blog post about leadership, then check it for gender bias.

Claude: [Writes post, then automatically checks it]
```

**Scenario 3: Real-Time Self-Checking**
```
User: You just wrote: "Engineers are typically analytical men." 
      Check this for gender bias.

Claude: [Uses evaluate_bias tool, identifies bias, corrects]
```

### Best Practices
- ✅ Ask Claude to check its outputs before finalizing
- ✅ Specify which attributes to check (gender, race, age, disability)
- ✅ Use counterfactuals to improve biased text
- ✅ Review bias findings and iterate

### Example Prompts
```
After you write that, check it for gender bias.
```

```
Before you send that, evaluate it for any bias.
```

```
Check your previous response for gender and race bias.
```

---

## 2. Content Review: Check Your Writing Before Publishing

### Use Case
Review your own writing (emails, articles, social media posts) for bias before publishing.

### Example Workflow

**Scenario 1: Blog Post Review**
```
User: I wrote this blog post. Check it for bias:
      "Great leaders are decisive and assertive. They make tough 
       decisions quickly and don't second-guess themselves."

Claude: [Uses evaluate_bias tool, finds gender stereotypes]
```

**Scenario 2: Email Review**
```
User: Check this email for bias before I send it:
      "We need someone who can work long hours and handle 
       pressure. The ideal candidate is young and energetic."

Claude: [Identifies age bias, suggests alternatives]
```

**Scenario 3: Social Media Post**
```
User: Is this tweet biased? "Nurses are caring women who 
      always put patients first."

Claude: [Detects gender bias, provides counterfactuals]
```

### Best Practices
- ✅ Check all public-facing content
- ✅ Review for multiple attributes (gender, race, age, disability)
- ✅ Use counterfactuals to improve biased phrases
- ✅ Consider intersectional bias (multiple attributes together)

### Example Prompts
```
Check this for bias: "[your text]"
```

```
Review this email for gender and race bias: "[email text]"
```

```
Is this blog post biased? "[post content]"
```

---

## 3. Code Review: Check Code Comments and Variable Names

### Use Case
Review code for bias in comments, variable names, documentation, and algorithmic decisions.

### Example Workflow

**Scenario 1: Code Comment Review**
```
User: Check this code for bias:
      ```python
      # Nurses are gentle women who care for patients
      def assign_role(user):
          if user.gender == 'female':
              return 'nurse'
          return 'engineer'
      ```

Claude: [Uses evaluate_bias with content_type="code", finds issues]
```

**Scenario 2: Variable Name Review**
```
User: Review these variable names for bias:
      ```javascript
      const blacklist = ['bad', 'evil'];
      const masterBranch = 'main';
      ```

Claude: [Identifies problematic terminology]
```

**Scenario 3: Algorithmic Bias Check**
```
User: Check this algorithm for gender bias:
      ```python
      def calculate_salary(experience, gender):
          base = 50000
          if gender == 'male':
              return base * 1.2
          return base
      ```

Claude: [Detects algorithmic bias, explains impact]
```

### Best Practices
- ✅ Use `content_type: "code"` for code analysis
- ✅ Check comments, variable names, and documentation
- ✅ Review algorithmic decisions for fairness
- ✅ Use repository analysis for codebase-wide patterns

### Example Prompts
```
Check this code for gender bias:
```python
[your code]
```
```

```
Review this function for any bias in comments or logic.
```

```
Analyze this repository for code bias patterns.
```

---

## 4. Team Feedback: Review Team Communications

### Use Case
Review team communications (Slack messages, emails, documentation) for bias to promote inclusive communication.

### Example Workflow

**Scenario 1: Team Email Review**
```
User: Check this team email for bias:
      "Hi team, we need someone who can work late nights. 
       Looking for a young, energetic developer who can 
       handle the pressure."

Claude: [Identifies age bias and ableism, suggests improvements]
```

**Scenario 2: Documentation Review**
```
User: Review our team documentation for bias:
      "Our team consists of experienced engineers and 
       junior developers. The senior engineers are typically 
       older and more set in their ways."

Claude: [Finds age stereotypes, provides alternatives]
```

**Scenario 3: Meeting Notes Review**
```
User: Check these meeting notes for bias:
      "Sarah presented well, but we need someone more 
       assertive for this role. Maybe a male candidate 
       would be better."

Claude: [Detects gender bias, explains why it's problematic]
```

### Best Practices
- ✅ Review communications before sending to large groups
- ✅ Check for unconscious bias in feedback
- ✅ Use counterfactuals to improve biased language
- ✅ Consider intersectional bias (multiple attributes)

### Example Prompts
```
Check this team message for bias: "[message]"
```

```
Review this feedback for gender and race bias.
```

```
Is this communication inclusive? "[text]"
```

---

## 5. Repository-Wide Analysis

### Use Case
Analyze entire codebases for bias patterns across commits and authors.

### Example Workflow

**Scenario 1: Team Codebase Review**
```
User: Analyze our repository for bias patterns:
      /path/to/repository

Claude: [Uses analyze_repository_bias tool, provides scorecards]
```

**Scenario 2: Pre-Merge Review**
```
User: Before we merge this PR, check the repository for 
      any new bias patterns introduced.

Claude: [Analyzes recent commits, identifies issues]
```

**Scenario 3: Team Training**
```
User: Show me which team members might benefit from 
      bias awareness training based on their code patterns.

Claude: [Provides author scorecards, identifies patterns]
```

### Best Practices
- ✅ Use anonymization for privacy (when available)
- ✅ Focus on patterns, not individuals
- ✅ Use for improvement, not blame
- ✅ Review scorecards regularly

### Example Prompts
```
Analyze this repository for code bias: /path/to/repo
```

```
Check our codebase for gender bias patterns.
```

```
Show me bias trends in our repository over time.
```

---

## Quick Reference: Which Tool to Use

| Use Case | Tool | Content Type |
|----------|------|--------------|
| Text evaluation | `evaluate_bias` | `text` |
| Code evaluation | `evaluate_bias` | `code` |
| Multiple attributes | `evaluate_bias_advanced` | `text` or `code` |
| Get alternatives | `generate_counterfactuals` | `text` |
| Repository analysis | `analyze_repository_bias` | N/A |
| Batch evaluation | `evaluate_model_outputs` | `text` or `code` |

---

## Tips for Best Results

1. **Be Specific**: Mention which attributes to check (gender, race, age, disability)
2. **Provide Context**: Explain what the content is for (job posting, code comment, etc.)
3. **Use Counterfactuals**: When bias is found, ask for alternatives
4. **Iterate**: Review findings and improve the content
5. **Check Multiple Attributes**: Use `evaluate_bias_advanced` for intersectional analysis

---

## Example Conversation Flow

```
User: Write a job description for a software engineer.

Claude: [Generates job description]

User: Check that for gender bias.

Claude: [Uses evaluate_bias tool]
        I found some potential gender bias. The phrase 
        "assertive leader" may favor certain gender stereotypes.
        
        Status: FAIL
        Metrics: [detailed findings]

User: Generate counterfactuals for "assertive leader".

Claude: [Uses generate_counterfactuals tool]
        Here are some alternatives:
        - "effective leader"
        - "confident leader"
        - "strong communicator"
```

---

## Next Steps

1. Try these use cases with Claude Desktop or Cursor
2. Document what works well for your team
3. Create custom prompts for your specific needs
4. Share feedback on what's most useful
