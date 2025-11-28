# py_engine/tools/evaluate_bias_advanced.py
"""
Tool handler for evaluate_bias_advanced MCP tool.
Advanced bias evaluation with full Fairlearn MetricFrame and AIF360 support.
"""
from typing import Dict, Any
from core.auditor import evaluate_bias_advanced
from models import EvaluateBiasAdvancedRequest


def handle_evaluate_bias_advanced(req: EvaluateBiasAdvancedRequest) -> Dict[str, Any]:
    """
    Handle evaluate_bias_advanced tool request.
    
    Args:
        req: Validated EvaluateBiasAdvancedRequest
        
    Returns:
        Response dictionary with advanced evaluation results
    """
    if not req.protected_attributes:
        return {'error': 'protected_attributes list cannot be empty'}
    
    result = evaluate_bias_advanced(
        req.content,
        req.protected_attributes,
        req.task_type,
        req.use_metricframe,
        req.use_aif360,
        req.metric_names,
        req.content_type
    )
    return {'result': result}

