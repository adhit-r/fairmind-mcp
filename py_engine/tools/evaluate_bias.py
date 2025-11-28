# py_engine/tools/evaluate_bias.py
"""
Tool handler for evaluate_bias MCP tool.
Evaluates text, code, or data for bias against protected attributes.
"""
from typing import Dict, Any
from core.auditor import (
    evaluate_bias_audit,
    evaluate_multi_attribute_bias,
)
from core.code_auditor import evaluate_code_bias
from models import EvaluateBiasRequest


def handle_evaluate_bias(req: EvaluateBiasRequest) -> Dict[str, Any]:
    """
    Handle evaluate_bias tool request.
    
    Args:
        req: Validated EvaluateBiasRequest
        
    Returns:
        Response dictionary with result
    """
    protected_attributes = req.protected_attributes
    protected_attribute = req.protected_attribute
    
    # Support both single attribute (backward compatible) and multiple attributes
    if protected_attributes is not None and len(protected_attributes) > 0:
        # Multiple attributes - use multi-attribute evaluation if > 1
        if len(protected_attributes) > 1:
            result = evaluate_multi_attribute_bias(
                req.content, 
                protected_attributes, 
                req.task_type, 
                req.content_type
            )
            return {'result': result}
        else:
            # Single attribute in list format
            target_attr = protected_attributes[0]
    else:
        target_attr = protected_attribute or ''
    
    # Single attribute evaluation
    if req.content_type == 'code':
        result = evaluate_code_bias(req.content, target_attr)
    else:
        result = evaluate_bias_audit(req.content, target_attr, req.task_type)
    
    return {'result': result}

