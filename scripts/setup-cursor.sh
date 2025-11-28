#!/usr/bin/env bash
# scripts/setup-cursor.sh
# Helper script to set up Cursor MCP integration

set -e

echo "FairMind MCP - Cursor Setup"
echo ""

# Get absolute path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
ABS_PATH="$PROJECT_DIR"

echo "Project directory: $ABS_PATH"
echo ""

# Try to find Cursor config location
CURSOR_CONFIGS=(
    "$HOME/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json"
    "$HOME/Library/Application Support/Cursor/User/settings.json"
    "$HOME/.cursor/mcp.json"
    "$HOME/.config/cursor/mcp.json"
)

CONFIG_FILE=""
for config in "${CURSOR_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        CONFIG_FILE="$config"
        echo "Found Cursor config: $CONFIG_FILE"
        break
    fi
done

if [ -z "$CONFIG_FILE" ]; then
    # Try to create the most common location
    CONFIG_FILE="$HOME/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json"
    mkdir -p "$(dirname "$CONFIG_FILE")"
    echo "{}" > "$CONFIG_FILE"
    echo "Created new config file: $CONFIG_FILE"
else
    echo "Using existing config file"
    # Backup existing config
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backed up existing config"
fi

# Create MCP server config
MCP_CONFIG=$(cat <<EOF
{
  "mcpServers": {
    "fairmind": {
      "command": "bun",
      "args": [
        "run",
        "$ABS_PATH/src/index.ts"
      ],
      "cwd": "$ABS_PATH"
    }
  }
}
EOF
)

# Merge with existing config
python3 <<PYTHON
import json
import sys

config_file = "$CONFIG_FILE"
mcp_config = json.loads('''$MCP_CONFIG''')

try:
    with open(config_file, 'r') as f:
        existing = json.load(f)
except:
    existing = {}

# Handle different config structures
if 'mcpServers' not in existing:
    if isinstance(existing, dict):
        existing['mcpServers'] = {}
    else:
        existing = {'mcpServers': {}}

existing['mcpServers'].update(mcp_config['mcpServers'])

with open(config_file, 'w') as f:
    json.dump(existing, f, indent=2)

print("Added FairMind MCP server to Cursor config")
PYTHON

echo ""
echo "✨ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Restart Cursor"
echo "   2. Use MCP tools to check generated code for bias"
echo "   3. Example: 'Generate a user role function, then check it for gender bias using @fairmind evaluate_bias with content_type=\"code\"'"
echo "   4. For interactive testing, use: bun run ui"
echo ""
echo "💡 Code Bias Detection Examples:"
echo "   - Check comments for stereotypes"
echo "   - Detect biased variable/function names"
echo "   - Find hardcoded demographic assumptions"
echo "   - Compare code versions for bias differences"
echo ""
echo "📚 Documentation:"
echo "   - Cursor Setup: docs/CURSOR_SETUP.md"
echo "   - Integration Examples: docs/INTEGRATION_EXAMPLES.md"
echo ""

