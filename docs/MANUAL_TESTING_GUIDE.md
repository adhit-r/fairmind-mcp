# Manual Testing Guide - Claude Desktop & Cursor

## Quick Start

### Step 1: Verify Setup

Run the setup scripts (already done):
```bash
./scripts/setup-claude-desktop.sh
./scripts/setup-cursor.sh
```

### Step 2: Restart Applications

**Claude Desktop:**
- Quit Claude Desktop completely
- Reopen Claude Desktop
- Check Settings → Developer to verify MCP server is connected

**Cursor:**
- Quit Cursor completely
- Reopen Cursor
- MCP tools should be available automatically

### Step 3: Test Tools

Use the test prompts below to verify everything works.

---

## Testing with Claude Desktop

### Test 1: Basic Text Bias Evaluation

**Prompt:**
```
Please evaluate this text for gender bias: "Nurses are gentle women who care for patients."
```

**Expected Behavior:**
- Claude should call the `evaluate_bias` tool
- Response should show:
  - Status: "FAIL" (bias detected)
  - Metrics showing gender stereotypes
  - Explanation of why it's biased

**What to Look For:**
- ✅ Tool is called automatically
- ✅ Response includes bias analysis
- ✅ Metrics are clear and actionable

---

### Test 2: Self-Checking (Claude Reviews Its Own Output)

**Prompt:**
```
I'm writing a job description. Here's my draft: "We're looking for a strong leader who can make tough decisions and drive results. The ideal candidate is a young professional with 5+ years of experience."

Please review this for bias and suggest improvements.
```

**Expected Behavior:**
- Claude should use `evaluate_bias_advanced` or `evaluate_bias`
- Should detect age bias ("young professional")
- Should detect potential gender bias ("strong leader")
- Should suggest improvements

**What to Look For:**
- ✅ Claude automatically checks its own suggestions
- ✅ Multiple bias types detected
- ✅ Actionable recommendations provided

---

### Test 3: Counterfactual Generation

**Prompt:**
```
Generate alternative ways to say: "The nurse was gentle and caring"
```

**Expected Behavior:**
- Claude should call `generate_counterfactuals`
- Should provide gender-neutral alternatives
- Examples: "The healthcare professional was gentle and caring"

**What to Look For:**
- ✅ Counterfactuals are generated
- ✅ Alternatives are gender-neutral
- ✅ Meaning is preserved

---

### Test 4: Code Bias Detection

**Prompt:**
```
Check this code for bias:

```python
def get_user_role(user):
    if user.gender == 'female':
        return 'nurse'
    elif user.gender == 'male':
        return 'doctor'
    else:
        return 'staff'
```
```

**Expected Behavior:**
- Claude should call `evaluate_bias` with `content_type: "code"`
- Should detect hardcoded gender assumptions
- Should flag the gender-based role assignment

**What to Look For:**
- ✅ Code-specific bias detection
- ✅ AST analysis results
- ✅ Clear explanation of bias in code

---

### Test 5: Repository Analysis

**Prompt:**
```
Analyze this repository for bias patterns: /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
```

**Expected Behavior:**
- Claude should call `analyze_repository_bias`
- Should show progress updates
- Should return author scorecards and bias patterns

**What to Look For:**
- ✅ Repository analysis starts
- ✅ Progress updates appear
- ✅ Results include author scorecards
- ⚠️ This may take a few minutes for large repos

---

## Testing with Cursor

### Test 1: Code Review for Bias

**Scenario:** You've written some code and want to check it for bias.

**Step 1:** Write or select code in Cursor:
```typescript
function assignRole(user) {
  if (user.gender === 'female') {
    return 'nurse';
  } else {
    return 'doctor';
  }
}
```

**Step 2:** Ask Cursor:
```
Check this code for bias using the FairMind tools
```

**Expected Behavior:**
- Cursor should use `evaluate_bias` with `content_type: "code"`
- Should detect gender-based role assignment
- Should suggest improvements

**What to Look For:**
- ✅ Code is analyzed
- ✅ Bias is detected
- ✅ Suggestions are code-specific

---

### Test 2: Variable Name Bias Check

**Scenario:** Check variable names and comments for bias.

**Code:**
```python
# The admin user is typically a man
admin_user = get_admin()

# Female users get special treatment
if user.gender == 'female':
    apply_discount(user)
```

**Prompt:**
```
Review this code for bias in comments and variable names
```

**Expected Behavior:**
- Should detect biased comments
- Should flag gender assumptions
- Should suggest neutral alternatives

---

### Test 3: Compare Code Versions

**Scenario:** You've refactored code and want to compare bias levels.

**Prompt:**
```
Compare these two code versions for bias:

Version A:
```python
def get_leader():
    return "strong man"
```

Version B:
```python
def get_leader():
    return "capable person"
```
```

**Expected Behavior:**
- Cursor should use `compare_code_bias`
- Should show bias reduction
- Should explain improvements

---

### Test 4: Repository Analysis in Cursor

**Prompt:**
```
Analyze the current repository for bias patterns. Focus on code comments and variable names.
```

**Expected Behavior:**
- Should call `analyze_repository_bias`
- Should show progress
- Should return results with anonymization if requested

**Tip:** For privacy, add:
```
Analyze with anonymize_authors: true
```

---

## Verification Checklist

### Claude Desktop
- [ ] MCP server appears in Settings → Developer
- [ ] Tools are listed (evaluate_bias, generate_counterfactuals, etc.)
- [ ] Test 1 (basic text) works
- [ ] Test 2 (self-checking) works
- [ ] Test 3 (counterfactuals) works
- [ ] Test 4 (code bias) works
- [ ] Test 5 (repository) works (optional, may be slow)

### Cursor
- [ ] MCP tools are available
- [ ] Test 1 (code review) works
- [ ] Test 2 (variable names) works
- [ ] Test 3 (compare versions) works
- [ ] Test 4 (repository) works

---

## Troubleshooting

### Claude Desktop: Tools Not Appearing

**Problem:** Tools don't show up in Claude Desktop

**Solutions:**
1. Check config file location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Verify config JSON is valid:
   ```bash
   python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
3. Check that `bun` is in PATH:
   ```bash
   which bun
   ```
4. Restart Claude Desktop completely (quit and reopen)

### Cursor: Tools Not Working

**Problem:** MCP tools not responding in Cursor

**Solutions:**
1. Check Cursor config location (varies by setup)
2. Verify `bun` is installed and in PATH
3. Check Cursor's MCP logs (if available)
4. Restart Cursor completely

### Python Bridge Errors

**Problem:** "Python process exited unexpectedly"

**Solutions:**
1. Verify Python environment:
   ```bash
   cd fairmind-mcp/py_engine
   source .venv/bin/activate  # or activate your venv
   python --version  # Should be 3.11+
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Check Python path in config matches your venv

### Tool Timeout

**Problem:** Repository analysis times out

**Solutions:**
1. Use `max_commits` to limit scope:
   ```
   Analyze with max_commits: 50
   ```
2. Filter file types:
   ```
   Analyze only .ts and .py files
   ```
3. Check repository size (very large repos may need more time)

---

## Example Prompts Library

### For Claude Desktop

**Content Review:**
- "Review this email for bias before I send it: [paste email]"
- "Check this blog post for gender bias: [paste text]"
- "Evaluate this job description for bias: [paste JD]"

**Self-Checking:**
- "I just wrote this. Please check it for bias: [paste text]"
- "Review my response for any biased language"
- "Check if this sounds inclusive: [paste text]"

**Counterfactuals:**
- "Give me neutral alternatives to: 'The CEO was a strong leader'"
- "Rewrite this to be more inclusive: [paste text]"

### For Cursor

**Code Review:**
- "Check this function for bias"
- "Review this code for gender assumptions"
- "Analyze variable names for stereotypes"

**Repository Analysis:**
- "Analyze this repo for bias patterns"
- "Check all comments for bias"
- "Find biased code in this repository"

**Comparison:**
- "Compare these two functions for bias"
- "Which version is less biased?"

---

## Success Indicators

### ✅ Everything Working

- Tools are called automatically
- Responses include detailed analysis
- Bias is detected correctly
- Suggestions are actionable
- No errors in console/logs

### ⚠️ Partial Success

- Tools are called but responses are slow
- Some tools work, others don't
- Analysis works but suggestions are generic

**Action:** Check logs, verify Python environment, test individual tools

### ❌ Not Working

- Tools don't appear
- Errors when calling tools
- Python bridge crashes

**Action:** 
1. Verify setup scripts ran successfully
2. Check config files are valid JSON
3. Verify Python environment
4. Check `bun` is installed
5. Review troubleshooting section above

---

## Next Steps

Once manual testing is successful:

1. **Document Issues:** Note any problems or edge cases
2. **Test Edge Cases:** Try unusual inputs, very long text, etc.
3. **Performance Testing:** Test with large repositories
4. **User Feedback:** Get feedback from team members
5. **Production Readiness:** Verify all tools work reliably

---

## Quick Reference

**Claude Desktop Config:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Cursor Config:**
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`

**Test Command:**
```bash
bun run test:real-world
```

**Verify Setup:**
```bash
./scripts/verify-tools.sh
```

