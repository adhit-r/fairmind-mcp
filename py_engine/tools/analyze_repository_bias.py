# py_engine/tools/analyze_repository_bias.py
"""
Tool handler for analyze_repository_bias MCP tool.
Analyzes git repository history to detect bias patterns across commits and authors.
"""
from typing import Dict, Any, List, Optional
from models import AnalyzeRepositoryBiasRequest
from core.repository_analyzer import analyze_repository


def handle_analyze_repository_bias(req: AnalyzeRepositoryBiasRequest) -> Dict[str, Any]:
    """
    Handle analyze_repository_bias tool request.
    
    Args:
        req: Validated AnalyzeRepositoryBiasRequest
        
    Returns:
        Response dictionary with repository analysis results including:
        - Author scorecards
        - Bias patterns over time
        - Overall repository metrics
    """
    result = analyze_repository(
        repository_path=req.repository_path,
        protected_attributes=req.protected_attributes,
        max_commits=req.max_commits,
        min_commits_per_author=req.min_commits_per_author,
        file_extensions=req.file_extensions,
        exclude_paths=req.exclude_paths,
        anonymize_authors=req.anonymize_authors,
        exclude_author_names=req.exclude_author_names,
        pattern_only_mode=req.pattern_only_mode,
    )
    return {'result': result}

