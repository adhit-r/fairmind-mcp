#!/usr/bin/env bash
# scripts/setup-claude-desktop.sh
# Helper script to set up Claude Desktop integration

set -e

echo "FairMind MCP - Claude Desktop Setup"
echo ""

# Get absolute path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
ABS_PATH="$PROJECT_DIR"

echo "Project directory: $ABS_PATH"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_FILE="$HOME/.config/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    CONFIG_FILE="$APPDATA/Claude/claude_desktop_config.json"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Config file: $CONFIG_FILE"
echo ""

# Create config directory if it doesn't exist
CONFIG_DIR=$(dirname "$CONFIG_FILE")
mkdir -p "$CONFIG_DIR"

# Check if config file exists
if [ -f "$CONFIG_FILE" ]; then
    echo "Config file exists"
    # Backup existing config
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backed up existing config"
else
    echo "Creating new config file"
    echo "{}" > "$CONFIG_FILE"
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

# Check if fairmind already exists in config
if grep -q '"fairmind"' "$CONFIG_FILE" 2>/dev/null; then
    echo "⚠️  FairMind MCP server already configured"
    echo "   To update, manually edit: $CONFIG_FILE"
else
    # Merge with existing config using Python (more reliable than jq)
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

if 'mcpServers' not in existing:
    existing['mcpServers'] = {}

existing['mcpServers'].update(mcp_config['mcpServers'])

with open(config_file, 'w') as f:
    json.dump(existing, f, indent=2)

print("Added FairMind MCP server to config")
PYTHON
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Restart Claude Desktop"
echo "   2. Verify tools are available (evaluate_bias, generate_counterfactuals)"
echo "   3. Test with: 'Please evaluate this text for gender bias: Nurses are gentle women'"
echo ""
echo "📚 Documentation:"
echo "   - Claude Desktop Setup: docs/CLAUDE_DESKTOP_SETUP.md"
echo "   - Integration Examples: docs/INTEGRATION_EXAMPLES.md"
echo ""

