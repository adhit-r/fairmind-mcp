#!/usr/bin/env bash
# scripts/verify-manual-setup.sh
# Quick verification that manual testing setup is ready

set -e

echo "FairMind MCP - Manual Testing Setup Verification"
echo "================================================"
echo ""

# Check 1: Bun is installed
echo "1. Checking Bun installation..."
if command -v bun &> /dev/null; then
    BUN_VERSION=$(bun --version)
    echo "   ✅ Bun installed: $BUN_VERSION"
else
    echo "   ❌ Bun not found. Install from: https://bun.sh"
    exit 1
fi

# Check 2: Python venv exists
echo ""
echo "2. Checking Python environment..."
if [ -d "py_engine/.venv" ]; then
    echo "   ✅ Python venv exists"
    PYTHON_VERSION=$(py_engine/.venv/bin/python --version 2>&1 || echo "unknown")
    echo "   ✅ Python version: $PYTHON_VERSION"
else
    echo "   ⚠️  Python venv not found. Run: cd py_engine && python -m venv .venv"
fi

# Check 3: Claude Desktop config
echo ""
echo "3. Checking Claude Desktop configuration..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
fi

if [ -f "$CLAUDE_CONFIG" ]; then
    if grep -q '"fairmind"' "$CLAUDE_CONFIG" 2>/dev/null; then
        echo "   ✅ FairMind configured in Claude Desktop"
        echo "   📍 Config: $CLAUDE_CONFIG"
    else
        echo "   ⚠️  FairMind not found in Claude Desktop config"
        echo "   📍 Config: $CLAUDE_CONFIG"
        echo "   💡 Run: ./scripts/setup-claude-desktop.sh"
    fi
else
    echo "   ⚠️  Claude Desktop config not found"
    echo "   💡 Run: ./scripts/setup-claude-desktop.sh"
fi

# Check 4: Cursor config
echo ""
echo "4. Checking Cursor configuration..."
CURSOR_CONFIGS=(
    "$HOME/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json"
    "$HOME/Library/Application Support/Cursor/User/settings.json"
    "$HOME/.cursor/mcp.json"
)

CURSOR_FOUND=false
for config in "${CURSOR_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        if grep -q '"fairmind"' "$config" 2>/dev/null; then
            echo "   ✅ FairMind configured in Cursor"
            echo "   📍 Config: $config"
            CURSOR_FOUND=true
            break
        fi
    fi
done

if [ "$CURSOR_FOUND" = false ]; then
    echo "   ⚠️  FairMind not found in Cursor config"
    echo "   💡 Run: ./scripts/setup-cursor.sh"
fi

# Check 5: Project structure
echo ""
echo "5. Checking project structure..."
if [ -f "src/index.ts" ]; then
    echo "   ✅ MCP server entry point exists"
else
    echo "   ❌ MCP server entry point not found"
    exit 1
fi

if [ -f "py_engine/main.py" ]; then
    echo "   ✅ Python engine exists"
else
    echo "   ❌ Python engine not found"
    exit 1
fi

# Summary
echo ""
echo "================================================"
echo "Verification Complete!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Restart Claude Desktop:"
echo "   - Quit Claude Desktop completely"
echo "   - Reopen Claude Desktop"
echo "   - Check Settings → Developer for MCP servers"
echo ""
echo "2. Restart Cursor:"
echo "   - Quit Cursor completely"
echo "   - Reopen Cursor"
echo "   - MCP tools should be available"
echo ""
echo "3. Test with example prompts:"
echo "   - See: docs/MANUAL_TESTING_GUIDE.md"
echo ""
echo "4. Run automated tests:"
echo "   bun run test:real-world"
echo ""
echo "📚 Documentation:"
echo "   - Manual Testing Guide: docs/MANUAL_TESTING_GUIDE.md"
echo "   - Real-World Testing: docs/REAL_WORLD_TESTING.md"
echo ""

