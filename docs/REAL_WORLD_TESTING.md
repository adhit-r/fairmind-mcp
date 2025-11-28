# Real-World Testing Guide

## Overview

This guide documents how to test FairMind MCP with real MCP clients (Claude Desktop, Cursor, Cline) to validate end-to-end functionality.

## Prerequisites

1. **FairMind MCP Server**: Installed and configured
2. **MCP Client**: One of:
   - Claude Desktop (Anthropic)
   - Cursor IDE
   - Cline (VS Code extension)
3. **Python Environment**: Python 3.11+ with dependencies installed

## Testing with Claude Desktop

### Setup

1. **Install Claude Desktop** (if not already installed)
   - Download from: https://claude.ai/download
   - macOS: Install from DMG
   - Windows: Install from EXE

2. **Configure Claude Desktop**
   - Open Claude Desktop
   - Go to Settings → Developer
   - Edit `claude_desktop_config.json` (location varies by OS):
     - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. **Add FairMind MCP Configuration**

```json
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": [
        "run",
        "/path/to/fairmind-mcp/src/index.ts"
      ],
      "env": {
        "FAIRMIND_PYTHON_PATH": "/path/to/fairmind-mcp/py_engine/.venv/bin/python",
        "FAIRMIND_PY_DIR": "/path/to/fairmind-mcp/py_engine"
      }
    }
  }
}
```

4. **Restart Claude Desktop**

### Test Cases

#### Test 1: Basic Bias Evaluation
**Prompt**: "Evaluate this text for gender bias: 'Nurses are gentle women who care for patients.'"

**Expected**: 
- Tool call to `evaluate_bias`
- Response with status "FAIL" and metrics showing gender bias

**Validation**:
- ✅ Tool is called
- ✅ Response contains `status: "FAIL"`
- ✅ Response contains `metrics` array
- ✅ Metrics include gender-related findings

#### Test 2: Counterfactual Generation
**Prompt**: "Generate counterfactuals for: 'The nurse was gentle'"

**Expected**:
- Tool call to `generate_counterfactuals`
- Response with alternative phrases

**Validation**:
- ✅ Tool is called
- ✅ Response contains `counterfactuals` array
- ✅ Counterfactuals are gender-neutral alternatives

#### Test 3: Code Bias Detection
**Prompt**: "Check this code for bias: `if user.gender == 'female': apply_discount(user, 0.1)`"

**Expected**:
- Tool call to `evaluate_bias` with `content_type: "code"`
- Response with code bias findings

**Validation**:
- ✅ Tool is called with correct parameters
- ✅ Response includes code-specific metrics
- ✅ AST analysis results are present

#### Test 4: Advanced Multi-Attribute Evaluation
**Prompt**: "Evaluate this text for both gender and race bias: 'The software engineer was Asian and very technical.'"

**Expected**:
- Tool call to `evaluate_bias_advanced`
- Response with multiple attribute evaluations

**Validation**:
- ✅ Tool is called
- ✅ Response includes evaluations for both attributes
- ✅ Metrics are properly categorized

## Testing with Cursor IDE

> **Note**: Cursor is a code editor, so the primary use case is **code bias detection** rather than text bias detection. Use FairMind to check generated code for bias in comments, variable names, string literals, and algorithmic logic.

### Setup

1. **Install Cursor IDE** (if not already installed)
   - Download from: https://cursor.sh
   - Install following platform-specific instructions

2. **Configure MCP in Cursor**
   - Open Cursor Settings
   - Navigate to Features → MCP
   - Add server configuration:

```json
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": ["run", "/path/to/fairmind-mcp/src/index.ts"],
      "env": {
        "FAIRMIND_PYTHON_PATH": "/path/to/fairmind-mcp/py_engine/.venv/bin/python"
      }
    }
  }
}
```

3. **Restart Cursor**

### Test Cases (Code-Focused)

#### Test 1: Code Comment Bias Detection
**Prompt**: "Check this code for gender bias: 
```javascript
// Nurses are gentle women who care for patients
function assignRole(user) {
  if (user.gender === 'female') {
    return 'nurse';
  }
  return 'engineer';
}
```"

**Expected**:
- Tool call to `evaluate_bias` with `content_type: "code"`
- Response showing bias in comments and hardcoded gender assumptions

**Validation**:
- ✅ Tool is called with `content_type: "code"`
- ✅ Response includes `Comment_Gender_Bias` metric
- ✅ Response includes `Hardcoded_Gender_Assumptions` metric
- ✅ Both metrics show FAIL status

#### Test 2: Variable Naming Bias
**Prompt**: "Check this code for racial bias:
```python
def process_user(blackUser, whiteUser):
    if blackUser.credit_score < 600:
        return "denied"
    return "approved"
```"

**Expected**:
- Tool call to `evaluate_bias` with `content_type: "code"` and `protected_attribute: "race"`
- Response showing bias in variable names

**Validation**:
- ✅ Tool is called with correct parameters
- ✅ Response includes `Naming_Racial_Bias` metric
- ✅ Response includes `Hardcoded_Race_Assumptions` metric

#### Test 3: Code Comparison for Bias
**Prompt**: "Compare these two code snippets for bias differences:
```javascript
// Snippet 1
if (user.gender === 'female') {
  applyDiscount(user, 0.1);
}

// Snippet 2
if (user.membership === 'premium') {
  applyDiscount(user, 0.1);
}
```"

**Expected**:
- Tool call to `compare_code_bias`
- Response showing bias differences between snippets

**Validation**:
- ✅ Tool is called
- ✅ Response shows differential analysis
- ✅ First snippet flagged for gender bias, second snippet passes

#### Test 4: Generated Code Review
**Prompt**: "I just generated this function. Check it for any bias:
```javascript
function getUserRole(user) {
  // Young developers are more energetic
  if (user.age < 25) {
    return 'junior_developer';
  }
  return 'senior_developer';
}
```"

**Expected**:
- Tool call to `evaluate_bias` with `content_type: "code"` and `protected_attribute: "age"`
- Response showing age bias in comments and logic

**Validation**:
- ✅ Tool is called
- ✅ Response includes age-related bias metrics
- ✅ Both comment and hardcoded assumption metrics fail

### Common Cursor Use Cases

1. **Code Generation Review**: After Cursor generates code, ask it to check for bias
2. **Refactoring Safety**: Before refactoring, check if changes introduce bias
3. **Code Review**: Use FairMind as part of your code review process
4. **Variable Naming**: Check if variable/function names contain biased language
5. **Comment Analysis**: Ensure code comments don't contain stereotypes

## Testing with Cline (VS Code Extension)

### Setup

1. **Install VS Code** (if not already installed)
   - Download from: https://code.visualstudio.com

2. **Install Cline Extension**
   - Open VS Code
   - Go to Extensions (Cmd/Ctrl + Shift + X)
   - Search for "Cline"
   - Install the extension

3. **Configure Cline**
   - Open VS Code Settings (Cmd/Ctrl + ,)
   - Search for "Cline MCP"
   - Add server configuration in `settings.json`:

```json
{
  "cline.mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": ["run", "/path/to/fairmind-mcp/src/index.ts"],
      "env": {
        "FAIRMIND_PYTHON_PATH": "/path/to/fairmind-mcp/py_engine/.venv/bin/python"
      }
    }
  }
}
```

4. **Reload VS Code**

### Test Cases

Same as above. Cline provides MCP integration within VS Code.

## Automated Test Script

Create a test script to validate all tools:

```bash
#!/bin/bash
# test/real-world-test.sh

echo "Testing FairMind MCP Tools..."

# Test 1: evaluate_bias
echo "Test 1: evaluate_bias"
RESULT=$(bun run src/index.ts <<< '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"evaluate_bias","arguments":{"content":"Nurses are gentle","protected_attribute":"gender","task_type":"generative","content_type":"text"}}}')
echo "$RESULT" | grep -q "status" && echo "✅ evaluate_bias works" || echo "❌ evaluate_bias failed"

# Test 2: generate_counterfactuals
echo "Test 2: generate_counterfactuals"
RESULT=$(bun run src/index.ts <<< '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"generate_counterfactuals","arguments":{"content":"The nurse was gentle","sensitive_group":"gender"}}}')
echo "$RESULT" | grep -q "counterfactuals" && echo "✅ generate_counterfactuals works" || echo "❌ generate_counterfactuals failed"

# Add more tests...
```

## Validation Checklist

For each test case, verify:

- [ ] **Tool Discovery**: Client can discover all FairMind tools
- [ ] **Tool Execution**: Tools execute without errors
- [ ] **Response Format**: Responses are valid JSON
- [ ] **Response Content**: Responses contain expected fields
- [ ] **Performance**: Response time < 2 seconds (after warm-up)
- [ ] **Error Handling**: Errors are properly formatted and informative
- [ ] **Python Bridge**: Python process stays alive between requests
- [ ] **Warm-up**: First request penalty is eliminated

## Common Issues

### Issue: "Tool not found"
**Solution**: 
- Verify MCP server configuration path
- Check that `bun` is in PATH
- Ensure `src/index.ts` exists and is executable

### Issue: "Python process not found"
**Solution**:
- Verify `FAIRMIND_PYTHON_PATH` environment variable
- Check Python virtual environment exists
- Run `cd py_engine && uv sync` to ensure dependencies

### Issue: "Timeout errors"
**Solution**:
- Check Python process is starting correctly
- Verify no blocking operations in Python code
- Increase timeout in client configuration if needed

### Issue: "Import errors in Python"
**Solution**:
- Run `cd py_engine && uv sync`
- Verify all dependencies in `pyproject.toml`
- Check Python version (3.11+)

## Performance Benchmarks

After setup, run benchmarks to establish baseline:

```bash
bun run test:benchmark
```

Expected results:
- First request: < 500ms (with warm-up)
- Subsequent requests: < 10ms
- Success rate: > 95%

## Reporting Issues

When reporting issues, include:

1. **Client**: Claude Desktop / Cursor / Cline
2. **OS**: macOS / Windows / Linux
3. **Error Message**: Full error text
4. **Tool**: Which tool failed
5. **Input**: What you tried to evaluate
6. **Logs**: Relevant log output from client and server

## Next Steps

After successful testing:

1. **Document Findings**: Update this guide with any issues found
2. **Performance Tuning**: Optimize based on real-world usage patterns
3. **User Feedback**: Collect feedback from actual users
4. **Continuous Testing**: Add automated tests to CI/CD

