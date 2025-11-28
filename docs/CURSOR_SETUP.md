# Cursor MCP Integration Guide

## Quick Setup

### 1. Locate Cursor Config File

**macOS:**
```bash
~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
```

Or check:
```bash
~/Library/Application Support/Cursor/User/settings.json
```

**Alternative locations:**
- `~/.cursor/mcp.json`
- `~/.config/cursor/mcp.json`

### 2. Add FairMind MCP Server

Edit the config file (create it if it doesn't exist):

```json
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": [
        "run",
        "/Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp/src/index.ts"
      ],
      "cwd": "/Users/adhi/axonome/fairmind-fairness-as-a-service-mcp/fairmind-mcp"
    }
  }
}
```

### 3. Restart Cursor

Close and reopen Cursor for changes to take effect.

## How MCP Tools Work in Cursor

Cursor is a **code generation tool**, so MCP tools are used when generating code that needs bias detection capabilities.

### Use Case: Generate Code That Uses Bias Detection

**Example Prompts:**

1. **Generate a Function:**
   ```
   Create a function that checks user-submitted job descriptions for gender bias 
   using the FairMind MCP evaluate_bias tool. The function should take a job 
   description string and return whether it passes or fails the bias check.
   ```

2. **Build a Content Moderation System:**
   ```
   Build a content moderation API endpoint that uses FairMind MCP to check 
   user comments for bias before they're posted. Use both evaluate_bias and 
   generate_counterfactuals tools.
   ```

3. **Integrate into Existing Code:**
   ```
   Show me how to integrate FairMind MCP bias detection into this Next.js API 
   route that reviews job postings before publishing.
   ```

4. **Generate Test Code:**
   ```
   Write unit tests for a bias detection service that uses the FairMind MCP 
   evaluate_bias tool. Include tests for gender, race, and age bias detection.
   ```

### What Cursor Will Generate

Cursor can generate code like:

```typescript
// Example: Cursor might generate this when you ask for bias checking
import { PythonBridge } from './fairmind-mcp/src/python_bridge.js';

async function checkJobDescriptionForBias(description: string) {
  const bridge = new PythonBridge();
  
  try {
    const result = await bridge.evaluateBias(
      description,
      'gender',
      'generative'
    );
    
    if (result.result.status === 'FAIL') {
      const alternatives = await bridge.generateCounterfactuals(
        description,
        'gender'
      );
      return {
        hasBias: true,
        metrics: result.result.metrics,
        alternatives: alternatives.counterfactuals
      };
    }
    
    return { hasBias: false, metrics: result.result.metrics };
  } finally {
    bridge.destroy();
  }
}
```

## When to Use Each Tool

### For Interactive Testing
- **Web UI**: `bun run ui` → http://localhost:3000
- **Claude Desktop**: For chat-based interaction

### For Code Generation
- **Cursor**: Generate code that uses the MCP tools
- **Programmatic**: Import and use `PythonBridge` directly

## Troubleshooting

### Config File Not Found

```bash
# Search for Cursor config files
find ~/Library/Application\ Support/Cursor -name "*mcp*" -o -name "*settings*" 2>/dev/null
```

### Tools Not Appearing in Code Generation

1. Verify MCP server is configured correctly
2. Restart Cursor completely
3. Try explicit prompts: "Use FairMind MCP tools to..."
4. Check Cursor's MCP documentation for latest integration details

## Note

Cursor uses MCP tools in **code generation contexts**, not for direct chat interaction like Claude Desktop. The tools help Cursor generate code that includes bias detection functionality.

For interactive testing and experimentation, use the **Web UI** (`bun run ui`) instead.
