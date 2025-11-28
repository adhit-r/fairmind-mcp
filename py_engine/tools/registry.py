# py_engine/tools/registry.py
"""
Tool registry for routing commands to appropriate handlers.
This provides a clean, extensible pattern for adding new tools.
"""
from typing import Dict, Callable, Any
from models import RequestUnion

# Import all tool handlers
from tools.evaluate_bias import handle_evaluate_bias
from tools.evaluate_bias_advanced import handle_evaluate_bias_advanced
from tools.generate_counterfactuals import handle_generate_counterfactuals
from tools.compare_code_bias import handle_compare_code_bias
from tools.evaluate_model_outputs import handle_evaluate_model_outputs
from tools.evaluate_prompt_suite import handle_evaluate_prompt_suite
from tools.evaluate_model_response import handle_evaluate_model_response

# Registry mapping command names to handler functions
TOOL_HANDLERS: Dict[str, Callable[[Any], Dict[str, Any]]] = {
    'evaluate_bias': handle_evaluate_bias,
    'evaluate_bias_advanced': handle_evaluate_bias_advanced,
    'generate_counterfactuals': handle_generate_counterfactuals,
    'compare_code_bias': handle_compare_code_bias,
    'evaluate_model_outputs': handle_evaluate_model_outputs,
    'evaluate_prompt_suite': handle_evaluate_prompt_suite,
    'evaluate_model_response': handle_evaluate_model_response,
}


def dispatch_tool(req: RequestUnion) -> Dict[str, Any]:
    """
    Dispatch a validated request to the appropriate tool handler.
    
    Args:
        req: Validated request (Pydantic model)
        
    Returns:
        Response dictionary
        
    Raises:
        ValueError: If tool handler not found
    """
    command = req.command
    
    if command not in TOOL_HANDLERS:
        return {'error': f'Unknown command: {command}'}
    
    handler = TOOL_HANDLERS[command]
    return handler(req)

