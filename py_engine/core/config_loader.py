import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

_config_cache: Optional[Dict[str, Any]] = None

def load_bias_config() -> Dict[str, Any]:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    
    # Try to find config file
    current_dir = Path(__file__).parent
    config_path = current_dir / 'bias_config.json'
    
    # Allow override via env var
    env_config = os.environ.get('FAIRMIND_BIAS_CONFIG')
    if env_config:
        config_path = Path(env_config)
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                _config_cache = config
                return config
        except Exception as e:
            import sys
            print(f"[WARNING] Failed to load bias config from {config_path}: {e}", file=sys.stderr)
            
    # Fallback to empty if file missing
    _config_cache = {}
    return _config_cache


