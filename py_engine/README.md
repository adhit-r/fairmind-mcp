# py_engine Organization

## Clean Structure

```
py_engine/
├── __init__.py              # Consolidated backward compat exports
├── main.py                  # Entry point (MCP server)
├── models.py                # Pydantic request models
├── bias_config.json         # Bias detection configuration
├── pyproject.toml           # Python dependencies
├── uv.lock                  # Lock file
│
├── core/                    # Shared utilities
│   ├── auditor.py
│   ├── code_auditor.py
│   ├── ast_analyzer.py
│   ├── inference.py
│   ├── config_loader.py
│   ├── inclusive_terminology.py
│   ├── differential_analyzer.py
│   └── codec.py
│
├── tools/                   # Tool handlers
│   ├── registry.py
│   ├── evaluate_bias.py
│   ├── evaluate_bias_advanced.py
│   ├── generate_counterfactuals.py
│   ├── compare_code_bias.py
│   ├── evaluate_model_outputs.py
│   ├── evaluate_prompt_suite.py
│   └── evaluate_model_response.py
│
└── _compat/                 # Archived shims (gitignored)
    ├── README.md
    └── [old shim files]
```

## Root Files (Essential Only)

- **`__init__.py`** - Package initialization + backward compat exports
- **`main.py`** - MCP server entry point
- **`models.py`** - Pydantic request validation models
- **`bias_config.json`** - Configuration file
- **`pyproject.toml`** - Python project config
- **`uv.lock`** - Dependency lock file

## Backward Compatibility

All old imports still work via `__init__.py`:
```python
from py_engine import evaluate_bias_audit  # Works
from py_engine.core.auditor import evaluate_bias_audit  # Preferred
```

The individual shim files have been moved to `_compat/` and are gitignored.

