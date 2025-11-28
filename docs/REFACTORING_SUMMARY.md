# Repository Organization - Implementation Summary

## ✅ Completed Refactoring

The codebase has been successfully refactored into a **modular, maintainable architecture** that makes it easy for contributors to work on individual tools while maintaining a single, efficient MCP server.

## New Structure

```
fairmind-mcp/
├── src/
│   ├── index.ts                    # Clean MCP server (50 lines vs 465)
│   ├── python_bridge.ts            # Robust bridge with auto-restart
│   ├── types.ts                    # Shared types
│   └── tools/                      # ✨ NEW: Tool modules
│       ├── registry.ts             # Central tool registry
│       ├── evaluate_bias.ts
│       ├── evaluate_bias_advanced.ts
│       ├── generate_counterfactuals.ts
│       ├── compare_code_bias.ts
│       ├── evaluate_model_outputs.ts
│       ├── evaluate_prompt_suite.ts
│       └── evaluate_model_response.ts
│
├── py_engine/
│   ├── main.py                     # Clean router (30 lines vs 221)
│   ├── models.py                   # Pydantic validation
│   ├── bias_config.json            # Configurable patterns
│   │
│   ├── core/                       # ✨ NEW: Shared utilities
│   │   ├── __init__.py
│   │   ├── auditor.py              # Bias detection logic
│   │   ├── code_auditor.py         # Code-specific detection
│   │   ├── ast_analyzer.py         # AST parsing (Python/Esprima)
│   │   ├── inference.py            # Counterfactual generation
│   │   ├── config_loader.py        # Configuration management
│   │   ├── inclusive_terminology.py
│   │   ├── differential_analyzer.py
│   │   └── codec.py                # TOON encoding
│   │
│   └── tools/                       # ✨ NEW: Tool handlers
│       ├── __init__.py
│       ├── registry.py             # Python tool registry
│       ├── evaluate_bias.py
│       ├── evaluate_bias_advanced.py
│       ├── generate_counterfactuals.py
│       ├── compare_code_bias.py
│       ├── evaluate_model_outputs.py
│       ├── evaluate_prompt_suite.py
│       └── evaluate_model_response.py
│
└── [old files remain for backward compatibility]
```

## Key Benefits

### 1. **For Contributors**
- **Clear Ownership**: Each tool is self-contained in its own file
- **Easy Navigation**: `src/tools/evaluate_bias.ts` → `py_engine/tools/evaluate_bias.py`
- **Independent Development**: Work on one tool without touching others
- **Simple Testing**: Test individual tools in isolation

### 2. **For Maintainability**
- **Single Source of Truth**: Tool definition and handler in same module
- **Registry Pattern**: Adding a new tool = add 2 files + 1 registry entry
- **Shared Code**: Core utilities in `core/` prevent duplication
- **Type Safety**: Pydantic models ensure runtime validation

### 3. **For Performance**
- **Single Process**: One Python process, one MCP server (efficient)
- **Lazy Loading**: Tools only loaded when needed
- **No Breaking Changes**: Backward compatibility maintained

## Adding a New Tool

### Step 1: Create Python Handler
```python
# py_engine/tools/my_new_tool.py
from core.auditor import evaluate_bias_audit
from models import MyNewToolRequest

def handle_my_new_tool(req: MyNewToolRequest) -> dict:
    # Tool logic here
    result = evaluate_bias_audit(...)
    return {'result': result}
```

### Step 2: Add to Python Registry
```python
# py_engine/tools/registry.py
from .my_new_tool import handle_my_new_tool

TOOL_HANDLERS = {
    # ... existing tools
    'my_new_tool': handle_my_new_tool,
}
```

### Step 3: Create TypeScript Definition
```typescript
// src/tools/my_new_tool.ts
export const myNewToolTool: Tool = {
  name: 'my_new_tool',
  description: '...',
  inputSchema: { ... }
};

export async function handleMyNewTool(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  // Call bridge method
}
```

### Step 4: Add to TypeScript Registry
```typescript
// src/tools/registry.ts
import { myNewToolTool, handleMyNewTool } from './my_new_tool.js';

export const TOOLS: ToolHandler[] = [
  // ... existing tools
  { tool: myNewToolTool, handler: handleMyNewTool },
];
```

**That's it!** The tool is now available via MCP.

## Backward Compatibility

All old import paths still work:
- `from auditor import ...` → re-exports from `core.auditor`
- `from code_auditor import ...` → re-exports from `core.code_auditor`
- etc.

This ensures no breaking changes for existing code or external dependencies.

## Testing

All existing tests pass:
```bash
bun run test/python-bridge-test.ts  # ✅ Passes
```

## Next Steps

1. **Remove old files** (after verification period):
   - `py_engine/auditor.py` (now just re-exports)
   - `py_engine/code_auditor.py` (now just re-exports)
   - etc.

2. **Add per-tool tests**:
   - `test/tools/evaluate_bias.test.ts`
   - `test/tools/generate_counterfactuals.test.ts`
   - etc.

3. **Documentation**:
   - Update contributor guide
   - Add tool development guide

## Architecture Principles Applied

✅ **Separation of Concerns**: Tools isolated, core shared  
✅ **DRY**: No code duplication  
✅ **Single Responsibility**: Each module has one clear purpose  
✅ **Open/Closed**: Easy to extend, no need to modify existing code  
✅ **Dependency Inversion**: Tools depend on core abstractions  
✅ **Registry Pattern**: Centralized tool discovery  
✅ **Backward Compatibility**: Zero breaking changes

This architecture scales to 20+ tools without becoming unmaintainable.

