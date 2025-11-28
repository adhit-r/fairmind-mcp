# py_engine/inference.py
"""
LiteRT-powered inference for counterfactual generation.
Uses quantized NLP models for efficient on-device inference.
"""
import os
import numpy as np
from typing import Optional, List, Any
from pathlib import Path

# Try to import LiteRT, fallback to simple heuristics if not available
try:
    from ai_edge_litert import Interpreter
    LITERT_AVAILABLE = True
except ImportError:
    LITERT_AVAILABLE = False
    # Define a dummy class for type hints if not available
    class Interpreter:
        pass
        
    import sys
    print("[WARNING] LiteRT not available, using fallback heuristics", file=sys.stderr)

# Global model cache
_loaded_models = {}

def generate_counterfactuals_nlp(content: str, sensitive_group: str) -> list:
    """
    Generates counterfactual alternatives to reduce bias.
    
    Attempts to use LiteRT-loaded models if available, otherwise falls back to heuristics.
    """
    
    if not LITERT_AVAILABLE:
        # Fallback: Simple rule-based counterfactuals
        return generate_counterfactuals_heuristic(content, sensitive_group)
    
    # Try to load and use model
    model = get_or_load_model(sensitive_group)
    if model:
        try:
            return generate_with_model(content, model, sensitive_group)
        except Exception as e:
            import sys
            print(f"[WARNING] Model inference failed: {e}, falling back to heuristics", file=sys.stderr)
            return generate_counterfactuals_heuristic(content, sensitive_group)
    
    # No model available, use heuristic fallback
    return generate_counterfactuals_heuristic(content, sensitive_group)
    
def generate_counterfactuals_heuristic(content: str, sensitive_group: str) -> list:
    """
    Heuristic-based counterfactual generation.
    Provides simple word substitutions to reduce gender/racial bias.
    """
    counterfactuals = []
    content_lower = content.lower()
    
    if sensitive_group == 'gender':
        # Gender-neutral substitutions
        substitutions = {
            'nurse': ['medical professional', 'healthcare worker', 'clinician'],
            'doctor': ['physician', 'medical professional', 'clinician'],
            'teacher': ['educator', 'instructor', 'faculty member'],
            'secretary': ['administrative assistant', 'office coordinator'],
            'gentle': ['calm', 'composed', 'professional'],
            'assertive': ['decisive', 'confident', 'clear'],
            'nurturing': ['supportive', 'attentive', 'caring'],
            'strong': ['resilient', 'capable', 'determined'],
        }
        
        # Find substitutions
        for word, alternatives in substitutions.items():
            if word in content_lower:
                for alt in alternatives:
                    new_content = content.replace(word, alt)
                    if new_content != content:
                        counterfactuals.append(new_content)
                        if len(counterfactuals) >= 3:  # Limit to 3
                            break
                if len(counterfactuals) >= 3:
                    break
        
        # If no substitutions found, provide generic alternatives
        if not counterfactuals:
            # Try to make it more neutral by removing gendered descriptors
            neutral = content.replace(' she ', ' they ').replace(' he ', ' they ')
            if neutral != content:
                counterfactuals.append(neutral)
    
    elif sensitive_group == 'race':
        # Remove potentially problematic racial descriptors
        problematic = ['exotic', 'articulate', 'urban']
        for word in problematic:
            if word in content_lower:
                # Remove the word
                new_content = ' '.join([w for w in content.split() if word not in w.lower()])
                if new_content != content:
                    counterfactuals.append(new_content)
    
    # Default: return at least one alternative (original with minor variation)
    if not counterfactuals:
        counterfactuals.append(content + " (reviewed for bias)")
    
    return counterfactuals[:3]  # Return max 3

def load_litert_model(model_path: str) -> Optional[Any]:
    """
    Loads a LiteRT model from a .tflite file.
    This would be used for production counterfactual generation.
    
    Args:
        model_path: Path to .tflite model file
    
    Returns:
        Interpreter instance or None if loading fails
    """
    if not LITERT_AVAILABLE:
        return None
    
    if not os.path.exists(model_path):
        return None
    
    try:
        # Use Any as return type hint to avoid issues when Interpreter is not defined
        interpreter = Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        return interpreter
    except Exception as e:
        import sys
        print(f"[WARNING] Failed to load model from {model_path}: {e}", file=sys.stderr)
        return None


def get_or_load_model(sensitive_group: str) -> Optional[Any]:
    """
    Get or load a model for the given sensitive group.
    Checks standard model locations and caches loaded models.
    
    Args:
        sensitive_group: 'gender', 'race', 'age', etc.
    
    Returns:
        Interpreter instance or None if no model found
    """
    # Check cache first
    if sensitive_group in _loaded_models:
        return _loaded_models[sensitive_group]
    
    # Look for model files in standard locations
    # Check in py_engine/models/ directory
    script_dir = Path(__file__).parent
    model_dir = script_dir / 'models'
    
    # Possible model file names
    model_files = [
        model_dir / f'bias_mitigation_{sensitive_group}.tflite',
        model_dir / f'counterfactual_{sensitive_group}.tflite',
        model_dir / f'{sensitive_group}_model.tflite',
    ]
    
    for model_path in model_files:
        if model_path.exists():
            model = load_litert_model(str(model_path))
            if model:
                _loaded_models[sensitive_group] = model
                return model
    
    # No model found
    return None


def generate_with_model(content: str, model: Any, sensitive_group: str) -> List[str]:
    """
    Generate counterfactuals using a loaded LiteRT model.
    
    This is a framework implementation. Actual implementation would depend on
    the specific model architecture and tokenization scheme.
    
    Args:
        content: Input text
        model: Loaded LiteRT Interpreter
        sensitive_group: Sensitive group being addressed
    
    Returns:
        List of counterfactual alternatives
    """
    try:
        # Get model input/output details
        input_details = model.get_input_details()
        output_details = model.get_output_details()
        
        # For now, this is a placeholder framework
        # Actual implementation would:
        # 1. Tokenize input text
        # 2. Prepare input tensor
        # 3. Run inference
        # 4. Decode output to get counterfactuals
        
        # Since we don't have actual models, fall back to heuristics
        # In production, this would use the model for inference
        return generate_counterfactuals_heuristic(content, sensitive_group)
    
    except Exception as e:
        import sys
        print(f"[WARNING] Model inference error: {e}", file=sys.stderr)
        # Fallback to heuristics
        return generate_counterfactuals_heuristic(content, sensitive_group)


def ensure_model_directory():
    """
    Ensure the models directory exists for storing TFLite models.
    """
    script_dir = Path(__file__).parent
    model_dir = script_dir / 'models'
    model_dir.mkdir(exist_ok=True)
    return model_dir
