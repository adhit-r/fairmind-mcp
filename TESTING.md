# Testing Guide

## Quick Tests

### 1. Test Python Components Directly

```bash
# Test TOON codec
bun run test:codec

# Test bias auditor
bun run test:auditor

# Test counterfactual generation
bun run test:inference
```

### 2. Test Python Bridge (Recommended)

This tests the TypeScript ↔ Python communication layer:

```bash
bun run test
```

This will:
- Start the Python bridge
- Send a bias evaluation request
- Send a counterfactual generation request
- Verify TOON encoding/decoding works

### 3. Test Full MCP Server

This simulates an MCP client:

```bash
bun run test:mcp
```

**Note:** MCP servers are designed to communicate with MCP clients (like Claude Desktop, Cline, or Cursor). The test script simulates this, but for full integration testing, you should use an actual MCP client.

## Integration Testing with MCP Clients

### Claude Desktop

1. Add to Claude Desktop's MCP configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": ["run", "/absolute/path/to/fairmind-mcp/src/index.ts"],
      "cwd": "/absolute/path/to/fairmind-mcp"
    }
  }
}
```

2. Restart Claude Desktop
3. The `evaluate_bias` and `generate_counterfactuals` tools will be available

### Cursor / Cline

Similar configuration in your editor's MCP settings. The server communicates via stdio, so any MCP-compatible client can connect.

## Test with Real LLM (Gemini)

Test the tools with Google Gemini API to see how an actual LLM agent would use them:

```bash
# Option 1: Set environment variable
export GEMINI_API_KEY=your_api_key_here
bun run test:gemini

# Option 2: Pass API key as argument
bun run test:gemini your_api_key_here
```

This test will:
1. Ask Gemini to evaluate a biased job description
2. Show how Gemini calls the `evaluate_bias` tool
3. Display the fairness audit results
4. Ask Gemini to generate counterfactuals
5. Show how Gemini uses the `generate_counterfactuals` tool

**Note:** This test uses Gemini's function calling feature, which simulates how an MCP client would interact with the tools.

## Manual Testing

You can also test the Python components directly:

```bash
# In py_engine directory
cd py_engine

# Test codec
uv run python codec.py

# Test auditor
uv run python -c "from auditor import evaluate_bias_audit; import json; print(json.dumps(evaluate_bias_audit('Nurses are gentle', 'gender', 'generative'), indent=2))"

# Test inference
uv run python -c "from inference import generate_counterfactuals_nlp; print(generate_counterfactuals_nlp('The nurse was gentle', 'gender'))"
```

## Expected Output

### Bias Evaluation
Should return a result with:
- `status`: "PASS" or "FAIL"
- `metrics`: Array of metric objects
- `details`: Human-readable explanation

### Counterfactual Generation
Should return an array of alternative text suggestions (typically 1-3 items).

