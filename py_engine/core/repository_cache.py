# py_engine/core/repository_cache.py
"""
Caching layer for repository analysis results.
Stores analysis results to avoid re-analyzing unchanged commits.
"""
import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


def get_cache_key(repository_path: str, max_commits: int, file_extensions: List[str], exclude_paths: List[str]) -> str:
    """Generate a cache key for repository analysis parameters."""
    key_data = {
        'repo': os.path.abspath(repository_path),
        'max_commits': max_commits,
        'file_extensions': sorted(file_extensions),
        'exclude_paths': sorted(exclude_paths),
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()


def get_cache_dir() -> Path:
    """Get the cache directory path."""
    cache_dir = Path.home() / '.fairmind' / 'cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_path(cache_key: str) -> Path:
    """Get the cache file path for a given key."""
    return get_cache_dir() / f"{cache_key}.json"


def get_last_commit_hash(repository_path: str) -> Optional[str]:
    """Get the hash of the most recent commit in the repository."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repository_path,
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None


def load_cached_analysis(cache_key: str, repository_path: str) -> Optional[Dict[str, Any]]:
    """
    Load cached analysis if it exists and is still valid.
    
    Returns:
    - Cached analysis if valid, None otherwise
    """
    cache_path = get_cache_path(cache_key)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'r') as f:
            cached = json.load(f)
        
        # Check if cache is still valid (repository hasn't changed)
        cached_head = cached.get('repository_head')
        current_head = get_last_commit_hash(repository_path)
        
        if cached_head != current_head:
            # Repository has new commits, cache is stale
            return None
        
        # Check cache age (invalidate after 7 days)
        cache_time = datetime.fromisoformat(cached.get('cache_time', ''))
        age_days = (datetime.now() - cache_time).days
        if age_days > 7:
            return None
        
        return cached.get('analysis')
    
    except Exception:
        # If cache is corrupted, ignore it
        return None


def save_cached_analysis(cache_key: str, repository_path: str, analysis: Dict[str, Any]) -> None:
    """Save analysis results to cache."""
    cache_path = get_cache_path(cache_key)
    
    current_head = get_last_commit_hash(repository_path)
    
    cached_data = {
        'cache_time': datetime.now().isoformat(),
        'repository_head': current_head,
        'analysis': analysis,
    }
    
    try:
        with open(cache_path, 'w') as f:
            json.dump(cached_data, f, indent=2)
    except Exception:
        # If caching fails, continue without cache
        pass


def get_analyzed_commits(cache_key: str, repository_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Get previously analyzed commits from cache.
    
    Returns:
    - Dictionary mapping commit hash to analysis result
    """
    cached = load_cached_analysis(cache_key, repository_path)
    if not cached:
        return {}
    
    # Extract commit analyses
    analyzed = {}
    author_scorecards = cached.get('author_scorecards', [])
    
    # Reconstruct commit analyses from scorecards
    # Note: This is a simplified reconstruction
    # Full incremental analysis would require storing individual commit results
    for scorecard in author_scorecards:
        author_id = scorecard.get('author_id') or scorecard.get('author_email', '')
        # We can't fully reconstruct individual commits from scorecards
        # This is a limitation of the current cache design
    
    return analyzed


def clear_cache(cache_key: Optional[str] = None) -> None:
    """Clear cache for a specific key or all caches."""
    cache_dir = get_cache_dir()
    
    if cache_key:
        cache_path = get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()
    else:
        # Clear all caches
        for cache_file in cache_dir.glob('*.json'):
            cache_file.unlink()

