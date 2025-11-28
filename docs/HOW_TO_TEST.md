# How to Test FairMind MCP

## Quick Test (30 seconds)

### 1. Test Server Starts Correctly

```bash
cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
./scripts/verify-tools.sh
```

This will verify:
- ✅ Server can start
- ✅ Python bridge works
- ✅ Tools are defined
- ✅ Dependencies installed
- ✅ Claude Desktop configured

### 2. Test Python Components Directly

```bash
# Test bias detection
bun run test:auditor

# Test counterfactual generation
bun run test:inference

# Test full Python bridge
bun run test
```

## Test in Claude Desktop

### Step 1: Restart Claude Desktop
- **Quit completely** (Cmd+Q on macOS)
- **Reopen** Claude Desktop
- Wait for it to fully load

### Step 2: Verify Tools Are Available

Type this in Claude Desktop:

```
What tools do you have available? Can you list all your MCP tools?
```

**Expected Response:** Claude should mention:
- `evaluate_bias` - Evaluates text for bias
- `generate_counterfactuals` - Generates bias-free alternatives

### Step 3: Test Bias Detection

**Prompt:**
```
Please evaluate this text for gender bias: 
"Nurses are gentle women who care for patients"
```

**What Should Happen:**
1. Claude calls `evaluate_bias` tool
2. You see a response with:
   - Status: `FAIL` (this text is biased)
   - Metrics: Gender_Stereotype_Disparity, Occupational_Gender_Bias, Trait_Gender_Bias
   - Details explaining what was found

**Expected Output:**
```json
{
  "result": {
    "status": "FAIL",
    "metrics": [
      {
        "name": "Gender_Stereotype_Disparity",
        "value": 1.0,
        "threshold": 0.5,
        "result": "FAIL"
      },
      {
        "name": "Occupational_Gender_Bias",
        "value": 1.0,
        "threshold": 0.6,
        "result": "FAIL"
      },
      {
        "name": "Trait_Gender_Bias",
        "value": 1.0,
        "threshold": 0.6,
        "result": "FAIL"
      }
    ],
    "details": "Detected 2 female-associated and 0 male-associated stereotype terms..."
  }
}
```

### Step 4: Test Counterfactual Generation

**Prompt:**
```
The text "The nurse was gentle" contains potential gender bias. 
Please use the generate_counterfactuals tool to suggest alternative wording.
```

**Expected Output:**
```json
{
  "counterfactuals": [
    "The medical professional was gentle",
    "The healthcare worker was gentle",
    "The clinician was gentle"
  ]
}
```

### Step 5: Test Full Workflow

**Prompt:**
```
I'm writing a job description. Please:
1. Check it for bias
2. If bias is found, generate counterfactuals
3. Provide a revised, bias-free version

Text: "We need an aggressive software engineer who is competitive and driven."
```

Claude should:
1. Evaluate for bias
2. Detect issues
3. Generate alternatives
4. Provide revised text

## Troubleshooting

### Tools Don't Appear

1. **Check Claude Desktop Logs:**
   ```bash
   tail -f ~/Library/Logs/Claude/mcp-server-fairmind.log
   ```
   Look for errors when you restart Claude Desktop.

2. **Verify Configuration:**
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   Should show `fairmind` MCP server.

3. **Test Server Manually:**
   ```bash
   cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
   bun run src/index.ts
   ```
   Should show: "FairMind MCP server running on stdio"

### Server Errors

If you see errors in the logs:

1. **Check Python Environment:**
   ```bash
   cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp/py_engine
   uv run python --version
   ```
   Should be Python 3.11+

2. **Reinstall Dependencies:**
   ```bash
   cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
   bun install
   cd py_engine && uv sync
   ```

3. **Check Paths:**
   The server should log:
   ```
   [FairMind] Project root: /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
   [FairMind] Python path: .../py_engine/.venv/bin/python
   ```

### Claude Doesn't Call Tools

- Make sure you're being explicit: "Please use the evaluate_bias tool..."
- Try: "Can you check this for bias using your tools?"
- Check if Claude mentions the tools when you ask "What tools do you have?"

## Test Checklist

- [ ] Server starts without errors
- [ ] Python bridge test passes (`bun run test`)
- [ ] Claude Desktop restarted completely
- [ ] Tools appear when asking "What tools do you have?"
- [ ] `evaluate_bias` works with test text
- [ ] `generate_counterfactuals` works
- [ ] Full workflow (evaluate → generate → revise) works

## Quick Test Commands

```bash
# All-in-one test
cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp
./scripts/verify-tools.sh && bun run test
```

## Success Indicators

✅ **Server Working:**
- No errors in `mcp-server-fairmind.log`
- Server starts and stays running
- Python process spawns successfully

✅ **Tools Available:**
- Claude lists both tools when asked
- Tools can be called explicitly
- Tools return results

✅ **Results Correct:**
- Bias detection identifies stereotypes
- Counterfactuals are generated
- Metrics are accurate

## Next Steps After Testing

Once everything works:
1. Try with your own text
2. Integrate into your workflow
3. Check out [Integration Examples](./docs/INTEGRATION_EXAMPLES.md) for more use cases
