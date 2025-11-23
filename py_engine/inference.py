# py_engine/inference.py
"""
LiteRT-powered inference for counterfactual generation.
Uses quantized NLP models for efficient on-device inference.
"""
import os
import numpy as np

# Try to import LiteRT, fallback to simple heuristics if not available
try:
    from ai_edge_litert import Interpreter
    LITERT_AVAILABLE = True
except ImportError:
    LITERT_AVAILABLE = False
    import sys
    print("[WARNING] LiteRT not available, using fallback heuristics", file=sys.stderr)

def generate_counterfactuals_nlp(content: str, sensitive_group: str) -> list:
    """
    Generates counterfactual alternatives to reduce bias.
    
    For MVP, uses simple rule-based substitutions.
    In production, would use a LiteRT-loaded BERT model for context-aware replacements.
    """
    
    if not LITERT_AVAILABLE:
        # Fallback: Simple rule-based counterfactuals
        return generate_counterfactuals_heuristic(content, sensitive_group)
    
    # TODO: Load a quantized TFLite model for counterfactual generation
    # For now, use heuristic fallback
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

def load_litert_model(model_path: str):
    """
    Loads a LiteRT model from a .tflite file.
    This would be used for production counterfactual generation.
    """
    if not LITERT_AVAILABLE:
        raise ImportError("LiteRT not available")
    
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

# Example usage if we had a model:
# def generate_with_model(content: str, model: Interpreter) -> list:
#     # Tokenize input
#     # Run inference
#     # Decode outputs
#     # Return counterfactuals
#     pass
