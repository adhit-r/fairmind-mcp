# Claude Desktop - Example Prompts That Work

## ✅ All of These Will Work!

Claude Desktop understands natural language, so you can phrase requests in many ways. Here are examples that will successfully trigger the `evaluate_bias` tool:

### Simple & Direct
```
Check this for gender bias: "Nurses are gentle women who care for patients."
```

```
Is this text biased? "Nurses are gentle women who care for patients."
```

```
Evaluate this for bias: "Nurses are gentle women who care for patients."
```

### More Specific
```
Please evaluate this text for gender bias: "Nurses are gentle women who care for patients."
```

```
Can you check if this has gender bias? "Nurses are gentle women who care for patients."
```

```
Analyze this sentence for gender bias: "Nurses are gentle women who care for patients."
```

### Even More Casual
```
"Nurses are gentle women who care for patients." - is this biased?
```

```
Does this have gender bias? "Nurses are gentle women who care for patients."
```

### What Claude Will Do

When you use any of these prompts, Claude will:
1. ✅ Recognize you want bias evaluation
2. ✅ Call the `evaluate_bias` tool automatically
3. ✅ Extract the text: `"Nurses are gentle women who care for patients."`
4. ✅ Infer `protected_attribute: "gender"` from your prompt
5. ✅ Use `task_type: "generative"` (default for text)
6. ✅ Use `content_type: "text"` (default)
7. ✅ Return the bias analysis results

### What You'll Get Back

The tool returns JSON with:
- `status`: "FAIL" or "PASS"
- `metrics`: Array of bias findings
- `protected_attribute`: Which attribute was checked
- `content_type`: "text" or "code"

Claude will then explain the results in natural language.

## 🎯 Best Practices

### For Best Results, Include:
1. **The text to analyze** (in quotes helps)
2. **The type of bias** (gender, race, age, disability)
3. **Context if needed** (e.g., "this is code" or "this is a job description")

### Examples:

**Text Analysis:**
```
Check this job posting for gender bias: "We're looking for a strong, assertive leader to join our team."
```

**Code Analysis:**
```
Check this code for gender bias:
```javascript
if (user.gender === 'female') {
  return 'nurse';
} else {
  return 'engineer';
}
```
```

**Multiple Attributes:**
```
Check this for both gender and race bias: "The software engineer was Asian and very technical."
```

## ❓ What If It Doesn't Work?

If Claude doesn't call the tool:
1. Be more explicit: "Use the evaluate_bias tool to check..."
2. Specify the attribute: "Check for gender bias..."
3. Make sure the MCP server is running and configured

## 🔍 How to Verify It's Working

1. **Watch for tool calls**: Claude will show "Using evaluate_bias tool" or similar
2. **Check the response**: Should include bias metrics and status
3. **Look for JSON**: The raw tool response includes structured data

---

**TL;DR**: Yes, any natural language prompt that mentions bias checking will work! Claude is smart enough to understand your intent and call the right tool.

