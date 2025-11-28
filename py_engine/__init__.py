# py_engine/__init__.py
"""
FairMind MCP Python Engine Package

Backward compatibility: Re-exports all core modules for existing imports.
All functionality is now in core/ and tools/ subdirectories.
"""
# Re-export all core modules for backward compatibility
from core.auditor import *  # noqa: F401, F403
from core.code_auditor import *  # noqa: F401, F403
from core.ast_analyzer import *  # noqa: F401, F403
from core.inference import *  # noqa: F401, F403
from core.config_loader import *  # noqa: F401, F403
from core.inclusive_terminology import *  # noqa: F401, F403
from core.differential_analyzer import *  # noqa: F401, F403
from core.codec import *  # noqa: F401, F403

# Also allow direct imports from root for convenience
__all__ = [
    # Core modules (imported via * above)
    'evaluate_bias_audit',
    'evaluate_code_bias',
    'generate_counterfactuals_nlp',
    'load_bias_config',
    # ... (all exports from core modules)
]
