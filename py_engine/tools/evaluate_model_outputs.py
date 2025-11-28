# py_engine/tools/evaluate_model_outputs.py
"""
Tool handler for evaluate_model_outputs MCP tool.
Batch evaluation for multiple LLM/fine-tuned model outputs.
"""
from typing import Dict, Any
from core.auditor import (
    evaluate_batch,
    aggregate_bias_results,
)
from core.code_auditor import evaluate_code_bias
from models import EvaluateModelOutputsRequest


def handle_evaluate_model_outputs(req: EvaluateModelOutputsRequest) -> Dict[str, Any]:
    """
    Handle evaluate_model_outputs tool request.
    
    Args:
        req: Validated EvaluateModelOutputsRequest
        
    Returns:
        Response dictionary with aggregated results
    """
    if not req.outputs:
        return {'error': 'outputs list cannot be empty'}
    
    if not req.protected_attributes:
        return {'error': 'protected_attributes list cannot be empty'}
    
    # Evaluate all outputs for each attribute
    all_results = []
    for attr in req.protected_attributes:
        batch_results = evaluate_batch(
            req.outputs, 
            attr, 
            req.task_type, 
            req.content_type
        )
        all_results.extend(batch_results)
    
    # Aggregate results
    aggregated = aggregate_bias_results(all_results, req.protected_attributes)
    
    # Format response based on aggregation preference
    if req.aggregation == 'detailed':
        return {'result': aggregated}
    else:
        # Summary format - exclude individual results
        summary = aggregated.copy()
        summary.pop('individual_results', None)
        return {'result': summary}

