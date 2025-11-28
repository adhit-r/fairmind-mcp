# Claude Desktop Integration Guide

## Quick Setup

### 1. Locate Claude Desktop Config File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### 2. Add FairMind MCP Server

Edit the config file (create it if it doesn't exist):

```json
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": [
        "run",
        "/absolute/path/to/fairmind-mcp/src/index.ts"
      ],
      "cwd": "/absolute/path/to/fairmind-mcp"
    }
  }
}
```

**Important:** Replace `/absolute/path/to/fairmind-mcp` with your actual path.

### 3. Get Your Absolute Path

Run this command to get your path:

```bash
cd /Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp && pwd
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop for changes to take effect.

### 5. Verify Installation

In Claude Desktop, you should see:
- Two new tools available: `evaluate_bias` and `generate_counterfactuals`
- Claude can now autonomously check for bias and generate counterfactuals

## Example Prompts

### Bias Detection
```
Please evaluate this job description for gender bias: 
"We are looking for a nurse who is gentle and nurturing. 
The ideal candidate is a woman who cares deeply about patients."
```

### Counterfactual Generation
```
The text "The nurse was gentle" contains potential gender bias. 
Please generate alternative wording that is more neutral.
```

### Autonomous Bias Correction
```
I'm writing a job description. Please review it for bias and 
suggest improvements if needed:
[Your text here]
```

## Troubleshooting

### Server Not Starting

1. **Check Bun is installed:**
   ```bash
   bun --version
   ```

2. **Verify Python environment:**
   ```bash
   cd /path/to/fairmind-mcp/py_engine
   uv sync
   ```

3. **Check server logs:**
   Look for errors in Claude Desktop's console or terminal output

### Tools Not Appearing

1. **Verify config file syntax:** Use a JSON validator
2. **Check path is absolute:** Relative paths won't work
3. **Restart Claude Desktop:** Changes require a full restart
4. **Check permissions:** Ensure Bun/Python have execute permissions

### Python Errors

1. **Install dependencies:**
   ```bash
   cd py_engine && uv sync
   ```

2. **Check Python version:**
   ```bash
   cd py_engine && uv run python --version
   ```
   Should be Python 3.11+

## Advanced Configuration

### Custom Python Path

If you need to use a specific Python interpreter:

```json
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": [
        "run",
        "/path/to/fairmind-mcp/src/index.ts"
      ],
      "cwd": "/path/to/fairmind-mcp",
      "env": {
        "PYTHON_PATH": "/custom/path/to/python"
      }
    }
  }
}
```

### Multiple MCP Servers

You can run multiple MCP servers simultaneously:

```json
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": ["run", "/path/to/fairmind-mcp/src/index.ts"],
      "cwd": "/path/to/fairmind-mcp"
    },
    "other-server": {
      "command": "node",
      "args": ["/path/to/other/server.js"]
    }
  }
}
```

## Testing the Integration

After setup, test with this prompt in Claude Desktop:

```
Use the evaluate_bias tool to check this text for gender bias:
"Nurses are gentle women who care for patients. Doctors are 
assertive leaders who make decisions."
```

Claude should:
1. Recognize the tool is available
2. Call `evaluate_bias` with the text
3. Receive the fairness report
4. Interpret the results and provide recommendations

## Next Steps

- Try the example prompts above
- Integrate into your workflow
- Check out [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) for more use cases

