# py_engine/tools/evaluate_model_response.py
"""
Tool handler for evaluate_model_response MCP tool.
Real-time single output testing for LLM responses.
"""
from typing import Dict, Any
from core.auditor import evaluate_bias_audit
from core.code_auditor import evaluate_code_bias
from models import EvaluateModelResponseRequest


def handle_evaluate_model_response(req: EvaluateModelResponseRequest) -> Dict[str, Any]:
    """
    Handle evaluate_model_response tool request.
    
    Args:
        req: Validated EvaluateModelResponseRequest
        
    Returns:
        Response dictionary with evaluation results
    """
    if not req.protected_attributes:
        return {'error': 'protected_attributes list cannot be empty'}
    
    # Quick evaluation for all attributes
    results = {}
    overall_status = 'PASS'
    key_issues = []
    
    for attr in req.protected_attributes:
        if req.content_type == 'code':
            result = evaluate_code_bias(req.response, attr)
        else:
            result = evaluate_bias_audit(req.response, attr, req.task_type)
        
        results[attr] = result
        
        if result.get('status') == 'FAIL':
            overall_status = 'FAIL'
            # Extract key issues
            failed_metrics = [m for m in result.get('metrics', []) if m.get('result') == 'FAIL']
            for metric in failed_metrics:
                key_issues.append(f"{attr}: {metric.get('name')} (value: {metric.get('value')})")
    
    return {
        'result': {
            'status': overall_status,
            'prompt': req.prompt,
            'response': req.response,
            'evaluations': results,
            'key_issues': key_issues[:5]  # Top 5 issues
        }
    }

