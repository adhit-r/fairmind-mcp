# py_engine/tools/compare_code_bias.py
"""
Tool handler for compare_code_bias MCP tool.
Compares two code snippets for structural bias.
"""
from typing import Dict, Any
from core.differential_analyzer import differential_code_analysis
from models import CompareCodeBiasRequest


def handle_compare_code_bias(req: CompareCodeBiasRequest) -> Dict[str, Any]:
    """
    Handle compare_code_bias tool request.
    
    Args:
        req: Validated CompareCodeBiasRequest
        
    Returns:
        Response dictionary with comparison results
    """
    result = differential_code_analysis(
        req.code_a, 
        req.code_b, 
        req.persona_a, 
        req.persona_b, 
        req.language_a, 
        req.language_b
    )
    return {'result': result}

