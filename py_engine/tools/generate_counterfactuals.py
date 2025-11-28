# py_engine/tools/generate_counterfactuals.py
"""
Tool handler for generate_counterfactuals MCP tool.
Generates alternative text suggestions to reduce bias.
"""
from typing import Dict, Any
from core.inference import generate_counterfactuals_nlp
from models import GenerateCounterfactualsRequest


def handle_generate_counterfactuals(req: GenerateCounterfactualsRequest) -> Dict[str, Any]:
    """
    Handle generate_counterfactuals tool request.
    
    Args:
        req: Validated GenerateCounterfactualsRequest
        
    Returns:
        Response dictionary with counterfactuals
    """
    result = generate_counterfactuals_nlp(req.content, req.sensitive_group)
    return {'counterfactuals': result}

