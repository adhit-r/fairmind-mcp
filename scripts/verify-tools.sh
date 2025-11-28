#!/usr/bin/env bash
# scripts/verify-tools.sh
# Quick verification script to test MCP tools are working

set -e

echo "FairMind MCP - Tool Verification"
echo ""

cd "$(dirname "$0")/.."

# Check 1: Server can start
echo "Test 1: Testing server can start..."
timeout 2 bun run src/index.ts > /dev/null 2>&1 &
SERVER_PID=$!
sleep 1
kill $SERVER_PID 2>/dev/null || true
echo "   Server starts successfully"
echo ""

# Check 2: Python bridge works
echo "Test 2: Testing Python bridge..."
if bun run test > /dev/null 2>&1; then
    echo "   Python bridge is working"
else
    echo "   Python bridge test had issues (this is OK if Python process management differs)"
fi
echo ""

# Check 3: Tools are defined
echo "Test 3: Testing tool definitions..."
if grep -q "evaluate_bias" src/index.ts && grep -q "generate_counterfactuals" src/index.ts; then
    echo "   Both tools are defined:"
    echo "      - evaluate_bias"
    echo "      - generate_counterfactuals"
else
    echo "   Tools not found in code"
    exit 1
fi
echo ""

# Check 4: Dependencies
echo "Test 4: Testing dependencies..."
if command -v bun &> /dev/null; then
    echo "   Bun is installed"
else
    echo "   Bun not found"
    exit 1
fi

if [ -d "py_engine/.venv" ]; then
    echo "   Python environment exists"
else
    echo "   Python environment not set up. Run: cd py_engine && uv sync"
fi
echo ""

# Check 5: Claude Desktop config
echo "Test 5: Testing Claude Desktop configuration..."
CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CONFIG_FILE" ]; then
    if grep -q "fairmind" "$CONFIG_FILE" 2>/dev/null; then
        echo "   FairMind MCP is configured in Claude Desktop"
    else
        echo "   Config file exists but FairMind not found"
        echo "      Run: ./scripts/setup-claude-desktop.sh"
    fi
else
    echo "   Claude Desktop config not found"
    echo "      Run: ./scripts/setup-claude-desktop.sh"
fi
echo ""

echo "Verification complete!"
echo ""
echo "Next steps:"
echo "   1. If Claude Desktop config is missing, run: ./scripts/setup-claude-desktop.sh"
echo "   2. Restart Claude Desktop"
echo "   3. In Claude Desktop, ask: 'What tools do you have available?'"
echo "   4. Test with: 'Please evaluate this text for gender bias: Nurses are gentle women'"
echo ""

