# py_engine/tools/evaluate_prompt_suite.py
"""
Tool handler for evaluate_prompt_suite MCP tool.
Systematic prompt suite testing for LLMs/fine-tuned models.
"""
from typing import Dict, Any
from core.auditor import (
    evaluate_bias_audit,
    aggregate_bias_results,
    compare_suite_results,
)
from core.code_auditor import evaluate_code_bias
from models import EvaluatePromptSuiteRequest


def handle_evaluate_prompt_suite(req: EvaluatePromptSuiteRequest) -> Dict[str, Any]:
    """
    Handle evaluate_prompt_suite tool request.
    
    Args:
        req: Validated EvaluatePromptSuiteRequest
        
    Returns:
        Response dictionary with suite report
    """
    if len(req.prompts) != len(req.model_outputs):
        return {'error': 'prompts and model_outputs must have the same length'}
    
    if not req.protected_attributes:
        return {'error': 'protected_attributes list cannot be empty'}
    
    # Evaluate all outputs for each attribute
    all_results = []
    per_prompt_results = []
    
    for idx, output in enumerate(req.model_outputs):
        prompt_result = {
            'prompt': req.prompts[idx],
            'output': output,
            'evaluations': {},
            'overall_status': 'PASS'
        }
        
        for attr in req.protected_attributes:
            if req.content_type == 'code':
                result = evaluate_code_bias(output, attr)
            else:
                result = evaluate_bias_audit(output, attr, req.task_type)
            
            prompt_result['evaluations'][attr] = result
            all_results.append(result)
            
            # Update overall status if any attribute fails
            if result.get('status') == 'FAIL':
                prompt_result['overall_status'] = 'FAIL'
        
        per_prompt_results.append(prompt_result)
    
    # Aggregate results
    aggregated = aggregate_bias_results(all_results, req.protected_attributes)
    
    # Add per-prompt results
    suite_report = {
        'suite_name': req.suite_name,
        'total_prompts': len(req.prompts),
        'aggregate_results': aggregated,
        'per_prompt_results': per_prompt_results
    }
    
    # Compare with previous results if provided
    if req.previous_results:
        comparison = compare_suite_results(aggregated, req.previous_results)
        suite_report['comparison'] = comparison
    
    return {'result': suite_report}

