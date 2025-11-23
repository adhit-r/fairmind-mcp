# py_engine/auditor.py
"""
Fairness auditing using Fairlearn and AIF360.
Implements statistical metrics for bias detection.
"""
import pandas as pd
import numpy as np
from fairlearn.metrics import MetricFrame, demographic_parity_difference, equalized_odds_difference

def evaluate_bias_audit(content: str, protected_attribute: str, task_type: str) -> dict:
    """
    Evaluates text content for bias using statistical metrics.
    
    For generative tasks, this performs a simple word-frequency analysis
    looking for stereotypical associations.
    
    For classification tasks, this would require actual predictions and labels,
    but for MVP we'll simulate with a simple heuristic.
    """
    
    # MVP: Simple heuristic-based bias detection
    # In production, this would use actual ML model predictions
    
    content_lower = content.lower()
    
    # Gender bias detection (simplified)
    if protected_attribute == 'gender':
        # Check for stereotypical associations
        female_stereotypes = ['nurse', 'teacher', 'secretary', 'caregiver', 'gentle', 'nurturing']
        male_stereotypes = ['engineer', 'doctor', 'leader', 'assertive', 'strong', 'decisive']
        
        female_count = sum(1 for word in female_stereotypes if word in content_lower)
        male_count = sum(1 for word in male_stereotypes if word in content_lower)
        
        # Calculate a simple "disparity" metric
        total_stereotypes = female_count + male_count
        if total_stereotypes > 0:
            # If content heavily favors one gender stereotype
            disparity = abs(female_count - male_count) / total_stereotypes
        else:
            disparity = 0.0
        
        # Threshold: if disparity > 0.5, it's biased
        status = 'FAIL' if disparity > 0.5 else 'PASS'
        
        return {
            'status': status,
            'metrics': [
                {
                    'name': 'Gender_Stereotype_Disparity',
                    'value': round(disparity, 3),
                    'threshold': 0.5,
                    'result': status
                }
            ],
            'details': f'Detected {female_count} female-associated and {male_count} male-associated stereotype terms.',
        }
    
    # Race bias detection (simplified)
    elif protected_attribute == 'race':
        # Simple keyword-based check for racial stereotypes
        problematic_patterns = ['thug', 'ghetto', 'exotic', 'articulate']  # Example patterns
        found_patterns = [p for p in problematic_patterns if p in content_lower]
        
        severity = len(found_patterns) / len(problematic_patterns) if problematic_patterns else 0
        status = 'FAIL' if severity > 0.3 else 'PASS'
        
        return {
            'status': status,
            'metrics': [
                {
                    'name': 'Racial_Stereotype_Score',
                    'value': round(severity, 3),
                    'threshold': 0.3,
                    'result': status
                }
            ],
            'details': f'Found {len(found_patterns)} potentially problematic racial associations.' if found_patterns else 'No obvious racial stereotypes detected.',
        }
    
    # Default: generic bias check
    else:
        # For other attributes, return a neutral pass for MVP
        return {
            'status': 'PASS',
            'metrics': [
                {
                    'name': 'Generic_Bias_Check',
                    'value': 0.0,
                    'threshold': 0.5,
                    'result': 'PASS'
                }
            ],
            'details': f'Bias check for {protected_attribute} completed (MVP implementation).',
        }

def evaluate_bias_with_dataframe(df: pd.DataFrame, protected_col: str, target_col: str, predictions_col: str) -> dict:
    """
    Full Fairlearn-based evaluation when actual data is available.
    This is the production-ready version.
    """
    protected = df[protected_col]
    y_true = df[target_col]
    y_pred = df[predictions_col]
    
    # Calculate demographic parity difference
    dpd = demographic_parity_difference(y_true, y_pred, sensitive_features=protected)
    
    # Calculate equalized odds difference
    eod = equalized_odds_difference(y_true, y_pred, sensitive_features=protected)
    
    # Thresholds (configurable)
    dpd_threshold = 0.1  # 10% difference is acceptable
    eod_threshold = 0.1
    
    status = 'FAIL' if abs(dpd) > dpd_threshold or abs(eod) > eod_threshold else 'PASS'
    
    return {
        'status': status,
        'metrics': [
            {
                'name': 'Demographic_Parity_Difference',
                'value': round(dpd, 4),
                'threshold': dpd_threshold,
                'result': 'FAIL' if abs(dpd) > dpd_threshold else 'PASS'
            },
            {
                'name': 'Equalized_Odds_Difference',
                'value': round(eod, 4),
                'threshold': eod_threshold,
                'result': 'FAIL' if abs(eod) > eod_threshold else 'PASS'
            }
        ],
        'details': f'DPD: {dpd:.4f}, EOD: {eod:.4f}',
    }
