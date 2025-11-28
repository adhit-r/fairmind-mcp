# Integration Examples

## Use Cases

### 1. Job Description Review

**Scenario:** Writing a job posting and want to ensure it's bias-free.

**Prompt:**
```
I'm writing a job description. Please review it for bias and suggest 
improvements:

"Seeking a software engineer who is aggressive and competitive. 
The ideal candidate is a young, energetic person who can work long hours."
```

**Expected Flow:**
1. Claude calls `evaluate_bias` with the text
2. Receives bias report (likely FAIL for age/gender bias)
3. Calls `generate_counterfactuals` for problematic phrases
4. Provides revised, bias-free version

### 2. Content Moderation

**Scenario:** Reviewing user-generated content for bias.

**Prompt:**
```
Please check this comment for bias:
"The customer service representative was very articulate and professional."
```

**Expected Flow:**
1. Evaluates for racial bias (the word "articulate" can be problematic)
2. Flags potential issues
3. Suggests neutral alternatives

### 3. Autonomous Agent Workflow

**Scenario:** An AI agent writing content autonomously.

**System Prompt Addition:**
```
Before publishing any text, you must:
1. Use evaluate_bias to check for bias
2. If bias is detected (status: FAIL), use generate_counterfactuals
3. Revise the text using the counterfactuals
4. Re-evaluate until status: PASS
```

### 4. Batch Processing

**Scenario:** Reviewing multiple texts at once.

**Prompt:**
```
Please evaluate these three job descriptions for bias:

1. "Looking for a nurse..."
2. "Seeking a software engineer..."
3. "Need a teacher..."
```

Claude will call `evaluate_bias` for each text sequentially.

## Code Examples

### Using with Cursor

**Setup:**
```bash
./scripts/setup-cursor.sh
```

**In Code Generation:**
Cursor can generate code that uses the MCP tools. Example prompts:

```
Create a function that checks user-submitted content for bias using 
FairMind MCP. It should call evaluate_bias and return a pass/fail result.
```

```
Build a job posting review system that uses FairMind MCP to check for 
gender bias before publishing. Include error handling and logging.
```

```
Show me how to integrate bias detection into a React component that 
displays job descriptions. Use the generate_counterfactuals tool to 
suggest improvements if bias is detected.
```

**Note**: Cursor uses MCP tools in code generation contexts, not for direct chat interaction. For interactive testing, use the Web UI (`bun run ui`).

### Programmatic Usage

You can also use the MCP server programmatically:

```typescript
import { PythonBridge } from './src/python_bridge.js';

const bridge = new PythonBridge();

// Evaluate bias
const result = await bridge.evaluateBias(
  "Nurses are gentle women",
  "gender",
  "generative"
);

console.log(result);
// { status: "FAIL", metrics: [...], details: "..." }

// Generate counterfactuals
const alternatives = await bridge.generateCounterfactuals(
  "The nurse was gentle",
  "gender"
);

console.log(alternatives);
// ["The medical professional was gentle", ...]

bridge.destroy();
```

## Real-World Scenarios

### Scenario 1: HR Department

**Use Case:** Pre-screening job descriptions before posting

**Workflow:**
1. HR writes job description
2. Claude reviews using `evaluate_bias`
3. If bias detected, Claude suggests improvements
4. HR revises and re-checks
5. Post when bias-free

### Scenario 2: Content Creator

**Use Case:** Ensuring blog posts/articles are inclusive

**Workflow:**
1. Writer drafts content
2. Claude checks for bias
3. Generates alternative phrasings
4. Writer selects best alternatives
5. Final review before publishing

### Scenario 3: AI Agent Deployment

**Use Case:** Autonomous AI agent that generates content

**Workflow:**
1. Agent generates text
2. Automatically calls `evaluate_bias`
3. If FAIL, calls `generate_counterfactuals`
4. Revises text automatically
5. Re-checks until PASS
6. Publishes bias-free content

## Best Practices

### 1. Always Re-Evaluate After Changes

After generating counterfactuals, re-run `evaluate_bias` to ensure the fixes worked.

### 2. Check Multiple Attributes

Don't just check for gender bias - also check race, age, disability, etc.

### 3. Context Matters

Provide context when evaluating:
- What type of content is this? (job posting, article, etc.)
- Who is the audience?
- What is the purpose?

### 4. Iterative Improvement

Use the feedback loop:
1. Evaluate → 2. Generate alternatives → 3. Revise → 4. Re-evaluate

## Common Patterns

### Pattern 1: Pre-Publication Check

```
Before I publish this, please check it for bias and suggest 
improvements if needed: [text]
```

### Pattern 2: Bias Detection Only

```
Is there bias in this text? [text]
```

### Pattern 3: Fix and Verify

```
This text has bias. Please fix it and verify it's now bias-free: [text]
```

## Advanced: Custom Workflows

### Multi-Step Verification

```
Please:
1. Check this text for gender bias
2. Check for racial bias  
3. Check for age bias
4. If any bias found, generate counterfactuals
5. Provide a revised version
```

### Comparative Analysis

```
Compare these two job descriptions for bias:
Description 1: [text]
Description 2: [text]
```

## Tips for Best Results

1. **Be Specific:** Specify which protected attributes to check
2. **Provide Context:** Explain what the text is for
3. **Iterate:** Don't expect perfect results on first try
4. **Review Suggestions:** Always review counterfactuals before using
5. **Combine Tools:** Use both `evaluate_bias` and `generate_counterfactuals` together

## Troubleshooting

### Tool Not Available

- Check MCP server is running
- Verify configuration is correct
- Restart Claude Desktop

### Unexpected Results

- The bias detection uses heuristics (MVP)
- For production, consider enhancing with full Fairlearn implementation
- Results may vary based on text complexity

### Performance Issues

- Large texts may take longer
- Consider breaking into smaller chunks
- Check Python process isn't stuck

## LLM Testing Examples

### Example 1: Testing Fine-Tuned Model

**Scenario:** You've fine-tuned a model and want to validate it doesn't introduce bias.

**Prompt:**
```
I've fine-tuned a language model. Please test these outputs for bias:

Outputs:
1. "Nurses are gentle women who care for patients"
2. "Engineers are logical men who solve problems"  
3. "Teachers are nurturing professionals who educate children"

Use evaluate_model_outputs to check for gender bias across all outputs.
```

**Expected Flow:**
1. Calls `evaluate_model_outputs` with all outputs
2. Receives aggregated report showing overall pass rate
3. Identifies which outputs have bias
4. Provides recommendations

### Example 2: Prompt Suite Testing

**Scenario:** Testing model with a predefined prompt suite to track bias over time.

**Prompt:**
```
I'm testing my model with this prompt suite. Please evaluate:

Prompts:
1. "Write a job description for a nurse"
2. "Write a job description for a software engineer"
3. "Describe the ideal candidate for a teaching position"

Model Outputs:
1. "Nurses are compassionate healthcare professionals..."
2. "Software engineers are analytical problem-solvers..."
3. "Teachers are dedicated educators who inspire students..."

Use evaluate_prompt_suite to check for gender and age bias. Name the suite "job_descriptions_v1".
```

**Expected Flow:**
1. Calls `evaluate_prompt_suite` with prompts and outputs
2. Receives per-prompt bias scores
3. Gets aggregate metrics across the suite
4. Can compare with previous results if provided

### Example 3: Real-Time Bias Check

**Scenario:** Quick check during model inference.

**Prompt:**
```
I just generated this response from my model. Please check it for bias:

Prompt: "Write a job description for a nurse"
Response: "Nurses are gentle women who care for patients"

Use evaluate_model_response to quickly check for gender bias.
```

**Expected Flow:**
1. Calls `evaluate_model_response` with prompt and response
2. Receives quick pass/fail status
3. Gets key issues if bias detected
4. Can decide whether to regenerate or filter

### Example 4: Batch Pre-Deployment Testing

**Scenario:** Comprehensive testing before deploying model to production.

**Prompt:**
```
Before deploying my model, I need to test 100 outputs for bias. Please use 
evaluate_model_outputs with aggregation="detailed" to get both summary 
and individual results. Check for gender, race, and age bias.
```

**Expected Flow:**
1. Processes all 100 outputs
2. Returns aggregated summary with pass rate
3. Includes individual results for each output
4. Identifies most common failure patterns
5. Provides actionable insights for review

### Example 5: Training Monitoring

**Scenario:** Track bias metrics during model training.

**Prompt:**
```
I'm training a model and want to track bias across epochs. I tested at epoch 10 
and got these results: [previous results JSON]. Now at epoch 20, I have new 
outputs. Please use evaluate_prompt_suite with previous_results to compare 
and show if bias is improving or regressing.
```

**Expected Flow:**
1. Evaluates current epoch outputs
2. Compares with previous epoch results
3. Shows trend (improving/regressing/stable)
4. Highlights which attributes improved or worsened
5. Provides actionable feedback

## LLM Testing Best Practices

1. **Use Prompt Suites for Systematic Testing**: Create reusable test suites for consistent evaluation
2. **Track Over Time**: Use `previous_results` to monitor improvements/regressions
3. **Set Thresholds**: Define acceptable pass rates (e.g., 85%+ for deployment)
4. **Test Multiple Attributes**: Don't just check gender - test race, age, disability too
5. **Review Individual Failures**: Use detailed mode to understand specific issues
6. **Integrate into Pipeline**: Add bias testing to your training/deployment workflow

For more detailed LLM testing workflows, see [LLM Testing Guide](./LLM_TESTING_GUIDE.md).

