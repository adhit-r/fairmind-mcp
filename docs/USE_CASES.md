# FairMind MCP - Use Case Guide

Practical examples for using FairMind MCP in real-world scenarios.

## 1. Self-Checking: Have Claude Review Its Own Outputs

### Use Case
Before Claude sends a response, have it check its own text for bias to ensure fair and inclusive communication.

### Example Workflows

#### Workflow A: Two-Step Self-Check
```
You: Write a job description for a software engineer position.

Claude: [Generates job description]

You: Now check that job description for gender bias.
```

#### Workflow B: Single Prompt with Self-Check
```
You: Write a job description for a software engineer, then immediately check it for gender and race bias.
```

#### Workflow C: Review Previous Response
```
You: Check your previous response for any gender, race, or age bias.
```

#### Workflow D: Iterative Improvement
```
You: I need you to write a product description, but first check it for bias before sending it to me.
```

### Best Practices
- ✅ Ask Claude to check its own outputs before finalizing
- ✅ Specify which attributes to check (gender, race, age, disability)
- ✅ Request counterfactuals if bias is found
- ✅ Use for sensitive content (job postings, marketing, communications)

### Example Prompts
```
Write a customer service email, then check it for gender bias before sending.
```

```
Generate a product description and verify it's free of racial stereotypes.
```

```
Create a team announcement, then evaluate it for age and disability bias.
```

---

## 2. Content Review: Check Your Writing Before Publishing

### Use Case
Review your own writing (emails, articles, social media posts) for bias before publishing or sending.

### Example Workflows

#### Workflow A: Pre-Publish Review
```
You: I wrote this blog post. Check it for bias:
[Paste your content]

Claude: [Uses evaluate_bias tool and provides feedback]
```

#### Workflow B: Email Review
```
You: Review this email for gender bias before I send it:
"Dear team, we need a strong leader who can take charge..."
```

#### Workflow C: Social Media Check
```
You: Is this tweet biased? "Great to see more women in tech! They bring a nurturing perspective."
```

#### Workflow D: Document Review
```
You: I'm writing a company policy document. Check this section for any bias:
[Paste section]
```

### Best Practices
- ✅ Check all external-facing content
- ✅ Review for multiple attributes simultaneously
- ✅ Get counterfactuals for biased phrases
- ✅ Use for sensitive topics (hiring, policies, public statements)

### Example Prompts
```
Check this job posting before I publish it: [content]
```

```
Review this customer communication for any bias: [content]
```

```
Is this product description inclusive? [content]
```

---

## 3. Code Review: Check Code Comments and Variable Names

### Use Case
Review code for biased comments, variable names, and algorithmic bias before merging.

### Example Workflows

#### Workflow A: Comment Review
```
You: Check this code for gender bias in comments:
```python
# Nurses are gentle women who care for patients
def assign_role(user):
    if user.gender == 'female':
        return 'nurse'
    return 'engineer'
```
```

#### Workflow B: Variable Name Review
```
You: Review these variable names for bias:
```javascript
const blacklist = ['admin', 'user'];
const masterNode = getPrimaryNode();
```
```

#### Workflow C: Algorithmic Bias Check
```
You: Check this algorithm for gender bias:
```python
def calculate_salary(employee):
    if employee.gender == 'female':
        return base_salary * 0.9  # Women get 10% less
    return base_salary
```
```

#### Workflow D: Full File Review
```
You: Analyze this entire file for code bias:
[Paste file content]
```

### Best Practices
- ✅ Use `content_type: "code"` for code analysis
- ✅ Check comments, variable names, and logic
- ✅ Review for algorithmic bias (discriminatory logic)
- ✅ Use in PR reviews and code audits

### Example Prompts
```
Check this code for gender and race bias in comments and variable names:
[code block]
```

```
Review this function for algorithmic bias:
[code block]
```

```
Analyze this entire file for any bias patterns:
[file content]
```

### Repository-Level Code Review
```
You: Analyze this repository for code bias patterns across all commits:
/path/to/repository
```

---

## 4. Team Feedback: Review Team Communications

### Use Case
Review team communications (Slack messages, emails, documentation) for bias before sending.

### Example Workflows

#### Workflow A: Slack Message Review
```
You: Check this Slack message for bias before I send it:
"Hey team, we need someone who can work late hours. Young people usually handle this better."
```

#### Workflow B: Team Email Review
```
You: Review this team email for gender bias:
"Hi everyone, we're looking for a strong, assertive leader..."
```

#### Workflow C: Documentation Review
```
You: Check our team documentation for any biased language:
[Paste documentation]
```

#### Workflow D: Meeting Notes Review
```
You: Review these meeting notes for bias:
[Paste notes]
```

### Best Practices
- ✅ Check communications before sending to team
- ✅ Review for multiple attributes (gender, race, age, disability)
- ✅ Use for sensitive topics (hiring, promotions, feedback)
- ✅ Get counterfactuals for improvement

### Example Prompts
```
Check this team announcement for any bias:
[content]
```

```
Review this feedback I'm giving to a team member:
[content]
```

```
Is this team communication inclusive?
[content]
```

---

## 5. Advanced Use Cases

### Batch Evaluation
```
You: Check all of these job descriptions for bias:
1. "We need a strong leader..."
2. "Looking for someone nurturing..."
3. "Seeking an assertive manager..."
```

### Multi-Attribute Analysis
```
You: Check this text for gender, race, and age bias simultaneously:
[content]
```

### Counterfactual Generation
```
You: This phrase has gender bias: "The nurse was gentle." Generate alternatives.
```

### Repository Analysis
```
You: Analyze our entire codebase for bias patterns and show me which authors need training:
/path/to/repository
```

---

## Quick Reference

### Protected Attributes
- `gender` - Gender stereotypes and bias
- `race` - Racial stereotypes and bias
- `age` - Age-related bias
- `disability` - Disability-related bias

### Content Types
- `text` - Natural language content (default)
- `code` - Source code (comments, variables, logic)

### Task Types
- `generative` - For generated text (default)
- `classification` - For classification tasks

### Common Prompts
```
Check [content] for [attribute] bias
Analyze [code] for bias
Review [text] before publishing
Generate counterfactuals for: [phrase]
Analyze repository: [path]
```

---

## Tips for Best Results

1. **Be Specific**: Mention which attributes to check
2. **Provide Context**: Explain what the content is for
3. **Request Counterfactuals**: Ask for alternatives if bias is found
4. **Use Code Type**: Specify `content_type: "code"` for code analysis
5. **Batch When Possible**: Check multiple items at once
6. **Iterate**: Use feedback to improve content

---

## Example Workflows

### Workflow 1: Job Posting Review
```
1. Write job posting
2. Check for gender bias
3. Check for race bias
4. Get counterfactuals for biased phrases
5. Revise and finalize
```

### Workflow 2: Code PR Review
```
1. Submit PR
2. Run repository analysis
3. Check specific files for code bias
4. Review author scorecard
5. Address issues before merge
```

### Workflow 3: Team Communication
```
1. Draft message
2. Check for bias
3. Get counterfactuals
4. Revise
5. Send
```

---

**Remember**: FairMind MCP works with natural language. You don't need exact syntax - just describe what you want to check!

