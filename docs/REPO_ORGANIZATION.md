# Repository Organization Analysis

## Current Structure
```
fairmind-mcp/
├── src/
│   ├── index.ts          # All 7 tools in one file
│   ├── python_bridge.ts
│   └── types.ts
└── py_engine/
    ├── main.py           # All tool handlers in one file
    ├── auditor.py
    ├── code_auditor.py
    └── ...
```

## Proposed: Modular Tool Organization

### Option A: Separate MCP Servers (Not Recommended)
❌ **Cons:**
- Each tool needs its own Python process (resource heavy)
- Shared code duplication (bridge, codec, config)
- Complex setup for users (multiple servers to configure)
- MCP clients expect one server per domain

### Option B: Modular Code Organization (Recommended ✅)
✅ **Pros:**
- Single MCP server (one Python process)
- Clear separation of concerns
- Easy for contributors to find/edit specific tools
- Shared infrastructure stays shared
- Better testability

## Recommended Structure

```
fairmind-mcp/
├── src/
│   ├── index.ts                    # Main MCP server (registers all tools)
│   ├── python_bridge.ts            # Shared bridge
│   ├── types.ts                    # Shared types
│   └── tools/                      # ✨ NEW: Tool modules
│       ├── evaluate_bias.ts
│       ├── evaluate_bias_advanced.ts
│       ├── compare_code_bias.ts
│       ├── generate_counterfactuals.ts
│       ├── evaluate_model_outputs.ts
│       ├── evaluate_prompt_suite.ts
│       └── evaluate_model_response.ts
├── py_engine/
│   ├── main.py                     # Router (delegates to tool handlers)
│   ├── tools/                      # ✨ NEW: Tool handlers
│   │   ├── __init__.py
│   │   ├── evaluate_bias.py
│   │   ├── evaluate_bias_advanced.py
│   │   ├── compare_code_bias.py
│   │   ├── generate_counterfactuals.py
│   │   ├── evaluate_model_outputs.py
│   │   ├── evaluate_prompt_suite.py
│   │   └── evaluate_model_response.py
│   ├── core/                       # ✨ NEW: Shared core
│   │   ├── __init__.py
│   │   ├── auditor.py
│   │   ├── code_auditor.py
│   │   ├── ast_analyzer.py
│   │   ├── inference.py
│   │   └── config_loader.py
│   ├── models.py
│   └── codec.py
└── test/
    └── tools/                      # ✨ NEW: Per-tool tests
        ├── evaluate_bias.test.ts
        └── ...
```

## Benefits for Contributors

1. **Clear Ownership**: Each tool is self-contained
2. **Easy Navigation**: `src/tools/evaluate_bias.ts` → `py_engine/tools/evaluate_bias.py`
3. **Independent Testing**: Test one tool without running all
4. **Shared Code**: Core logic in `py_engine/core/` prevents duplication
5. **Scalability**: Adding a new tool = add 2 files (TS + Python)

## Migration Path

1. Create `src/tools/` and `py_engine/tools/` directories
2. Extract each tool handler into its own module
3. Update `index.ts` to import from `tools/`
4. Update `main.py` to import from `tools/`
5. Move shared code to `py_engine/core/`

This keeps the single-server architecture while making the codebase much more maintainable.

