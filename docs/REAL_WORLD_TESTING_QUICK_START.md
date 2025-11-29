# Real-World Testing Guide - Quick Start

## ✅ Test 1: Repository Analysis - COMPLETED

The repository analysis feature has been tested and works correctly!

**Test Results:**
- Git parsing: ✅ Working
- Commit analysis: ✅ Working  
- Author scorecards: ✅ Working
- Performance: ✅ Fast (< 1 second for 5 commits)

## 🧪 Test 2: Claude Desktop - READY TO TEST

### Quick Test Steps

1. **Verify Configuration**
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   Should show FairMind MCP server configured.

2. **Restart Claude Desktop**
   - Quit completely (Cmd+Q)
   - Reopen Claude Desktop

3. **Test Tool Discovery**
   - Open a new conversation
   - Ask: "What MCP tools do you have available?"
   - Should list FairMind tools

4. **Test evaluate_bias**
   - Prompt: "Please evaluate this text for gender bias: 'Nurses are gentle women who care for patients.'"
   - Should call `evaluate_bias` tool
   - Should return bias analysis

5. **Test generate_counterfactuals**
   - Prompt: "Generate counterfactuals for: 'The nurse was gentle'"
   - Should call `generate_counterfactuals` tool
   - Should return alternative phrases

6. **Test analyze_repository_bias**
   - Prompt: "Analyze this repository for bias: /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp"
   - Should call `analyze_repository_bias` tool
   - Should return repository analysis

### Expected Results

- ✅ Tools are discoverable
- ✅ Tools execute without errors
- ✅ Responses are valid and useful
- ✅ Performance is acceptable (< 2 seconds)

### Troubleshooting

If tools don't appear:
1. Check `bun` is in PATH: `which bun`
2. Verify repository path is correct
3. Check Claude Desktop logs for errors
4. Try manual test: `cd fairmind-mcp && bun run src/index.ts`

---

## 🧪 Test 3: Cursor - READY TO TEST

### Quick Test Steps

1. **Verify Configuration**
   ```bash
   cat ~/Library/Application\ Support/Cursor/User/settings.json | grep -A 10 mcpServers
   ```
   Should show FairMind MCP server configured.

2. **Restart Cursor**
   - Quit completely (Cmd+Q)
   - Reopen Cursor

3. **Test Code Bias Detection**
   - Prompt: "Check this code for gender bias:
   ```javascript
   // Nurses are gentle women
   function assignRole(user) {
     if (user.gender === 'female') return 'nurse';
     return 'engineer';
   }
   ```"
   - Should call `evaluate_bias` with `content_type: "code"`
   - Should return code bias analysis

4. **Test Repository Analysis**
   - Prompt: "Analyze this repository for code bias patterns"
   - Should call `analyze_repository_bias`
   - Should return repository analysis

### Expected Results

- ✅ Tools work for code analysis
- ✅ Repository analysis works
- ✅ Responses are actionable

---

## 📝 Testing Checklist

- [x] Repository analysis feature tested
- [ ] Claude Desktop tool discovery
- [ ] Claude Desktop evaluate_bias
- [ ] Claude Desktop generate_counterfactuals
- [ ] Claude Desktop analyze_repository_bias
- [ ] Cursor tool discovery
- [ ] Cursor code bias detection
- [ ] Cursor repository analysis
- [ ] Document any issues found
- [ ] Create example prompts that work well

---

## 🐛 Issue Reporting

If you find issues during testing:

1. **Document the issue:**
   - What tool were you testing?
   - What was the input?
   - What error occurred?
   - What was expected?

2. **Check logs:**
   - Claude Desktop: Check console/developer tools
   - Cursor: Check developer console
   - MCP Server: Check terminal output

3. **Report:**
   - Add to `docs/TEST_RESULTS_REAL_WORLD.md`
   - Or create GitHub issue

---

## ✅ Success Criteria

Testing is successful when:
- All tools are discoverable
- All tools execute without errors
- Responses are valid and useful
- Performance is acceptable
- No critical bugs found

