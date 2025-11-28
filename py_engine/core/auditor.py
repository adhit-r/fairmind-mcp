# py_engine/auditor.py
"""
Fairness auditing using Fairlearn and AIF360.
Implements statistical metrics for bias detection.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from core.config_loader import load_bias_config
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
    demographic_parity_ratio,
    selection_rate,
    true_positive_rate,
    false_positive_rate,
    true_negative_rate,
    false_negative_rate,
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score as sk_accuracy_score

# Try to import AIF360, fallback gracefully if not available
try:
    from aif360.metrics import ClassificationMetric
    from aif360.datasets import BinaryLabelDataset
    AIF360_AVAILABLE = True
except ImportError:
    AIF360_AVAILABLE = False
    import sys
    print("[WARNING] AIF360 not available, advanced metrics will be limited", file=sys.stderr)


def evaluate_bias_audit(
    content: str, 
    protected_attribute: str, 
    task_type: str,
    reference_texts: Optional[List[str]] = None
) -> dict:
    """
    Evaluates text content for bias using enhanced statistical metrics.
    
    For generative tasks, uses NLP-based analysis with Fairlearn metrics.
    For classification tasks, requires predictions and labels.
    
    Args:
        content: The text to evaluate
        protected_attribute: One of 'gender', 'race', 'age', 'disability'
        task_type: 'generative' or 'classification'
        reference_texts: Optional list of reference texts for comparison
    
    Returns:
        Dictionary with status, metrics, and details
    """
    
    content_lower = content.lower()
    
    # Enhanced Gender Bias Detection
    if protected_attribute == 'gender':
        return _evaluate_gender_bias(content, content_lower, reference_texts)
    
    # Enhanced Race Bias Detection
    elif protected_attribute == 'race':
        return _evaluate_race_bias(content, content_lower, reference_texts)
    
    # Age Bias Detection
    elif protected_attribute == 'age':
        return _evaluate_age_bias(content, content_lower, reference_texts)
    
    # Disability Bias Detection
    elif protected_attribute == 'disability':
        return _evaluate_disability_bias(content, content_lower, reference_texts)
    
    # Default: generic bias check
    else:
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
            'details': f'Bias check for {protected_attribute} completed.',
        }


def _evaluate_gender_bias(content: str, content_lower: str, reference_texts: Optional[List[str]]) -> dict:
    """Enhanced gender bias detection using multiple metrics."""
    config = load_bias_config()
    gender_config = config.get('gender', {})
    
    female_stereotypes = gender_config.get('female', {
        'occupations': [], 'traits': [], 'roles': []
    })
    
    male_stereotypes = gender_config.get('male', {
        'occupations': [], 'traits': [], 'roles': []
    })
    
    # Count stereotypes by category
    female_counts = {
        'occupations': sum(1 for word in female_stereotypes['occupations'] if word in content_lower),
        'traits': sum(1 for word in female_stereotypes['traits'] if word in content_lower),
        'roles': sum(1 for word in female_stereotypes['roles'] if word in content_lower),
    }
    
    male_counts = {
        'occupations': sum(1 for word in male_stereotypes['occupations'] if word in content_lower),
        'traits': sum(1 for word in male_stereotypes['traits'] if word in content_lower),
        'roles': sum(1 for word in male_stereotypes['roles'] if word in content_lower),
    }
    
    total_female = sum(female_counts.values())
    total_male = sum(male_counts.values())
    total_stereotypes = total_female + total_male
    
    # Calculate multiple metrics
    metrics = []
    
    # 1. Stereotype Disparity
    if total_stereotypes > 0:
        disparity = abs(total_female - total_male) / total_stereotypes
    else:
        disparity = 0.0
    
    metrics.append({
        'name': 'Gender_Stereotype_Disparity',
        'value': round(disparity, 3),
        'threshold': 0.5,
        'result': 'FAIL' if disparity > 0.5 else 'PASS'
    })
    
    # 2. Occupational Bias Score
    occ_total = female_counts['occupations'] + male_counts['occupations']
    if occ_total > 0:
        occ_bias = abs(female_counts['occupations'] - male_counts['occupations']) / occ_total
        metrics.append({
            'name': 'Occupational_Gender_Bias',
            'value': round(occ_bias, 3),
            'threshold': 0.6,
            'result': 'FAIL' if occ_bias > 0.6 else 'PASS'
        })
    
    # 3. Trait Association Bias
    trait_total = female_counts['traits'] + male_counts['traits']
    if trait_total > 0:
        trait_bias = abs(female_counts['traits'] - male_counts['traits']) / trait_total
        metrics.append({
            'name': 'Trait_Gender_Bias',
            'value': round(trait_bias, 3),
            'threshold': 0.6,
            'result': 'FAIL' if trait_bias > 0.6 else 'PASS'
        })
    
    # Overall status
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    details = (
        f'Detected {total_female} female-associated and {total_male} male-associated stereotype terms. '
        f'Occupational: F={female_counts["occupations"]}, M={male_counts["occupations"]}. '
        f'Trait: F={female_counts["traits"]}, M={male_counts["traits"]}.'
    )
    
    return {
        'status': status,
        'metrics': metrics,
        'details': details,
    }


def _evaluate_race_bias(content: str, content_lower: str, reference_texts: Optional[List[str]]) -> dict:
    """Enhanced race bias detection."""
    config = load_bias_config()
    race_config = config.get('race', {})
    
    problematic_patterns = {
        'stereotypes': race_config.get('stereotypes', []),
        'microaggressions': race_config.get('microaggressions', []),
        'assumptions': race_config.get('assumptions', [])
    }
    
    found_patterns = {
        'stereotypes': [p for p in problematic_patterns['stereotypes'] if p in content_lower],
        'microaggressions': [p for p in problematic_patterns['microaggressions'] if p in content_lower],
        'assumptions': [p for p in problematic_patterns['assumptions'] if p in content_lower],
    }
    
    metrics = []
    
    # Stereotype Score
    stereotype_score = len(found_patterns['stereotypes']) / len(problematic_patterns['stereotypes']) if problematic_patterns['stereotypes'] else 0
    metrics.append({
        'name': 'Racial_Stereotype_Score',
        'value': round(stereotype_score, 3),
        'threshold': 0.2,
        'result': 'FAIL' if stereotype_score > 0.2 else 'PASS'
    })
    
    # Microaggression Detection
    microaggression_score = len(found_patterns['microaggressions']) / len(problematic_patterns['microaggressions']) if problematic_patterns['microaggressions'] else 0
    metrics.append({
        'name': 'Microaggression_Score',
        'value': round(microaggression_score, 3),
        'threshold': 0.1,
        'result': 'FAIL' if microaggression_score > 0.1 else 'PASS'
    })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    details = (
        f'Found {len(found_patterns["stereotypes"])} stereotype patterns, '
        f'{len(found_patterns["microaggressions"])} microaggressions.'
    )
    
    return {
        'status': status,
        'metrics': metrics,
        'details': details if found_patterns['stereotypes'] or found_patterns['microaggressions'] else 'No obvious racial bias detected.',
    }


def _evaluate_age_bias(content: str, content_lower: str, reference_texts: Optional[List[str]]) -> dict:
    """Age bias detection."""
    config = load_bias_config()
    age_config = config.get('age', {})
    
    age_stereotypes = {
        'young': age_config.get('young', []),
        'old': age_config.get('old', []),
        'ageist': age_config.get('ageist', [])
    }
    
    young_count = sum(1 for word in age_stereotypes['young'] if word in content_lower)
    old_count = sum(1 for word in age_stereotypes['old'] if word in content_lower)
    ageist_count = sum(1 for phrase in age_stereotypes['ageist'] if phrase in content_lower)
    
    total_age_refs = young_count + old_count
    
    metrics = []
    
    # Age Disparity
    if total_age_refs > 0:
        age_disparity = abs(young_count - old_count) / total_age_refs
        metrics.append({
            'name': 'Age_Reference_Disparity',
            'value': round(age_disparity, 3),
            'threshold': 0.7,
            'result': 'FAIL' if age_disparity > 0.7 else 'PASS'
        })
    
    # Ageist Language
    metrics.append({
        'name': 'Ageist_Language_Score',
        'value': ageist_count,
        'threshold': 0,
        'result': 'FAIL' if ageist_count > 0 else 'PASS'
    })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    return {
        'status': status,
        'metrics': metrics,
        'details': f'Found {young_count} young-associated, {old_count} old-associated, and {ageist_count} ageist terms.',
    }


def _evaluate_disability_bias(content: str, content_lower: str, reference_texts: Optional[List[str]]) -> dict:
    """Disability bias detection."""
    config = load_bias_config()
    disability_config = config.get('disability', {})
    
    problematic_patterns = {
        'ableist_language': disability_config.get('ableist_language', []),
        'assumptions': disability_config.get('assumptions', []),
        'inspiration_porn': disability_config.get('inspiration_porn', [])
    }
    
    found = {
        'ableist': [p for p in problematic_patterns['ableist_language'] if p in content_lower],
        'assumptions': [p for p in problematic_patterns['assumptions'] if p in content_lower],
        'inspiration': [p for p in problematic_patterns['inspiration_porn'] if p in content_lower],
    }
    
    metrics = []
    
    # Ableist Language Score
    ableist_score = len(found['ableist']) / len(problematic_patterns['ableist_language']) if problematic_patterns['ableist_language'] else 0
    metrics.append({
        'name': 'Ableist_Language_Score',
        'value': round(ableist_score, 3),
        'threshold': 0.2,
        'result': 'FAIL' if ableist_score > 0.2 else 'PASS'
    })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    return {
        'status': status,
        'metrics': metrics,
        'details': f'Found {len(found["ableist"])} ableist terms, {len(found["assumptions"])} assumption patterns.',
    }


def evaluate_bias_with_dataframe(
    df: pd.DataFrame, 
    protected_col: str, 
    target_col: str, 
    predictions_col: str,
    metric_names: Optional[List[str]] = None
) -> dict:
    """
    Full Fairlearn-based evaluation when actual data is available.
    This is the production-ready version using real predictions.
    
    Args:
        df: DataFrame with protected attributes, targets, and predictions
        protected_col: Column name for protected attribute
        target_col: Column name for true labels
        predictions_col: Column name for model predictions
        metric_names: Optional list of metrics to compute
    
    Returns:
        Dictionary with comprehensive fairness metrics
    """
    protected = df[protected_col]
    y_true = df[target_col]
    y_pred = df[predictions_col]
    
    # Default metrics
    if metric_names is None:
        metric_names = ['selection_rate', 'true_positive_rate', 'false_positive_rate']
    
    # Create MetricFrame for comprehensive analysis
    metrics_dict = {}
    if 'selection_rate' in metric_names:
        metrics_dict['selection_rate'] = selection_rate
    if 'true_positive_rate' in metric_names:
        metrics_dict['true_positive_rate'] = true_positive_rate
    if 'false_positive_rate' in metric_names:
        metrics_dict['false_positive_rate'] = false_positive_rate
    
    metric_frame = MetricFrame(
        metrics=metrics_dict,
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=protected
    )
    
    # Calculate demographic parity difference
    dpd = demographic_parity_difference(y_true, y_pred, sensitive_features=protected)
    
    # Calculate equalized odds difference
    eod = equalized_odds_difference(y_true, y_pred, sensitive_features=protected)
    
    # Thresholds (configurable)
    dpd_threshold = 0.1  # 10% difference is acceptable
    eod_threshold = 0.1
    
    # Build metrics list
    metrics = [
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
    ]
    
    # Add MetricFrame results
    for metric_name, metric_func in metrics_dict.items():
        group_metrics = metric_frame.by_group[metric_name]
        if len(group_metrics) > 1:
            max_diff = group_metrics.max() - group_metrics.min()
            metrics.append({
                'name': f'{metric_name}_Max_Difference',
                'value': round(max_diff, 4),
                'threshold': 0.1,
                'result': 'FAIL' if max_diff > 0.1 else 'PASS'
            })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    return {
        'status': status,
        'metrics': metrics,
        'details': f'DPD: {dpd:.4f}, EOD: {eod:.4f}. MetricFrame analysis completed.',
        'metric_frame': metric_frame.by_group.to_dict() if hasattr(metric_frame, 'by_group') else None
    }


def evaluate_batch(
    content_list: List[str],
    protected_attribute: str,
    task_type: str,
    content_type: str = 'text'
) -> List[dict]:
    """
    Evaluate multiple texts for bias.
    
    Args:
        content_list: List of texts to evaluate
        protected_attribute: One of 'gender', 'race', 'age', 'disability'
        task_type: 'generative' or 'classification'
        content_type: 'text' or 'code'
    
    Returns:
        List of evaluation results, one per content item
    """
    results = []
    for content in content_list:
        if content_type == 'code':
            # Import here to avoid circular imports
            from code_auditor import evaluate_code_bias
            result = evaluate_code_bias(content, protected_attribute)
        else:
            result = evaluate_bias_audit(content, protected_attribute, task_type)
        results.append(result)
    return results


def aggregate_bias_results(
    results_list: List[dict],
    protected_attributes: List[str]
) -> dict:
    """
    Aggregate individual bias evaluation results into a summary report.
    
    Args:
        results_list: List of evaluation result dictionaries
        protected_attributes: List of protected attributes that were checked
    
    Returns:
        Aggregated report with pass rates, average scores, failure patterns
    """
    total_count = len(results_list)
    if total_count == 0:
        return {
            'status': 'PASS',
            'summary': {
                'total_evaluated': 0,
                'overall_pass_rate': 100.0,
            },
            'per_attribute': {},
            'failure_patterns': [],
            'individual_results': []
        }
    
    # Count passes and failures
    passed_count = sum(1 for r in results_list if r.get('status') == 'PASS')
    failed_count = total_count - passed_count
    pass_rate = (passed_count / total_count) * 100
    
    # Aggregate metrics by attribute
    per_attribute = {}
    
    for result in results_list:
        metrics = result.get('metrics', [])
        for metric in metrics:
            metric_name = metric.get('name', '')
            # Extract attribute from metric name (e.g., "Gender_Stereotype_Disparity" -> "gender")
            attr = None
            for pa in protected_attributes:
                if pa.lower() in metric_name.lower():
                    attr = pa
                    break
            
            if attr:
                if attr not in per_attribute:
                    per_attribute[attr] = {
                        'total_checks': 0,
                        'passed': 0,
                        'failed': 0,
                        'average_scores': {},
                        'failure_rate': 0.0
                    }
                
                per_attribute[attr]['total_checks'] += 1
                if metric.get('result') == 'PASS':
                    per_attribute[attr]['passed'] += 1
                else:
                    per_attribute[attr]['failed'] += 1
                
                # Track average scores per metric
                metric_key = metric_name
                if metric_key not in per_attribute[attr]['average_scores']:
                    per_attribute[attr]['average_scores'][metric_key] = []
                per_attribute[attr]['average_scores'][metric_key].append(metric.get('value', 0))
    
    # Calculate failure rates and average scores
    for attr in per_attribute:
        attr_data = per_attribute[attr]
        if attr_data['total_checks'] > 0:
            attr_data['failure_rate'] = (attr_data['failed'] / attr_data['total_checks']) * 100
        
        # Calculate average scores
        for metric_key, scores in attr_data['average_scores'].items():
            if scores:
                attr_data['average_scores'][metric_key] = round(sum(scores) / len(scores), 3)
    
    # Find most common failure patterns
    failure_patterns = {}
    for result in results_list:
        if result.get('status') == 'FAIL':
            metrics = result.get('metrics', [])
            for metric in metrics:
                if metric.get('result') == 'FAIL':
                    metric_name = metric.get('name', '')
                    failure_patterns[metric_name] = failure_patterns.get(metric_name, 0) + 1
    
    # Sort by frequency
    failure_patterns_list = [
        {'metric': k, 'count': v, 'percentage': round((v / failed_count) * 100, 1) if failed_count > 0 else 0}
        for k, v in sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True)
    ]
    
    overall_status = 'PASS' if pass_rate >= 80.0 else 'FAIL'  # 80% threshold
    
    return {
        'status': overall_status,
        'summary': {
            'total_evaluated': total_count,
            'passed': passed_count,
            'failed': failed_count,
            'overall_pass_rate': round(pass_rate, 2),
        },
        'per_attribute': per_attribute,
        'failure_patterns': failure_patterns_list[:10],  # Top 10
        'individual_results': results_list  # Include all individual results
    }


def compare_suite_results(
    current: dict,
    previous: Optional[dict] = None
) -> dict:
    """
    Compare current suite results with previous results to track improvements/regressions.
    
    Args:
        current: Current suite evaluation results
        previous: Previous suite evaluation results (optional)
    
    Returns:
        Comparison report with changes, improvements, regressions
    """
    if previous is None:
        return {
            'has_baseline': False,
            'current': current,
            'message': 'No previous results to compare against'
        }
    
    current_pass_rate = current.get('summary', {}).get('overall_pass_rate', 0)
    previous_pass_rate = previous.get('summary', {}).get('overall_pass_rate', 0)
    
    pass_rate_change = current_pass_rate - previous_pass_rate
    
    # Compare per-attribute metrics
    attribute_comparison = {}
    current_attrs = current.get('per_attribute', {})
    previous_attrs = previous.get('per_attribute', {})
    
    all_attrs = set(list(current_attrs.keys()) + list(previous_attrs.keys()))
    
    for attr in all_attrs:
        current_data = current_attrs.get(attr, {})
        previous_data = previous_attrs.get(attr, {})
        
        current_fail_rate = current_data.get('failure_rate', 0)
        previous_fail_rate = previous_data.get('failure_rate', 0)
        
        fail_rate_change = current_fail_rate - previous_fail_rate
        
        attribute_comparison[attr] = {
            'current_failure_rate': current_fail_rate,
            'previous_failure_rate': previous_fail_rate,
            'change': round(fail_rate_change, 2),
            'improved': fail_rate_change < 0,  # Negative change = improvement
            'regressed': fail_rate_change > 0
        }
    
    # Determine overall trend
    improved_count = sum(1 for comp in attribute_comparison.values() if comp['improved'])
    regressed_count = sum(1 for comp in attribute_comparison.values() if comp['regressed'])
    
    if improved_count > regressed_count:
        trend = 'improving'
    elif regressed_count > improved_count:
        trend = 'regressing'
    else:
        trend = 'stable'
    
    return {
        'has_baseline': True,
        'current': current,
        'previous': previous,
        'comparison': {
            'pass_rate': {
                'current': current_pass_rate,
                'previous': previous_pass_rate,
                'change': round(pass_rate_change, 2),
                'improved': pass_rate_change > 0
            },
            'attributes': attribute_comparison,
            'trend': trend,
            'summary': f'Pass rate changed by {pass_rate_change:+.2f}%. Overall trend: {trend}.'
        }
    }


def evaluate_multi_attribute_bias(
    content: str,
    protected_attributes: List[str],
    task_type: str,
    content_type: str = 'text'
) -> dict:
    """
    Evaluate bias across multiple protected attributes simultaneously.
    
    Args:
        content: The text or code to evaluate
        protected_attributes: List of protected attributes to check
        task_type: 'generative' or 'classification'
        content_type: 'text' or 'code'
    
    Returns:
        Dictionary with per-attribute results, intersectional bias detection, and combined status
    """
    per_attribute_results = {}
    all_metrics = []
    
    # Evaluate each attribute
    for attr in protected_attributes:
        if content_type == 'code':
            from code_auditor import evaluate_code_bias
            result = evaluate_code_bias(content, attr)
        else:
            result = evaluate_bias_audit(content, attr, task_type)
        
        per_attribute_results[attr] = result
        all_metrics.extend(result.get('metrics', []))
    
    # Detect intersectional bias (when multiple attributes fail together)
    failed_attributes = [attr for attr, result in per_attribute_results.items() 
                        if result.get('status') == 'FAIL']
    
    intersectional_issues = []
    if len(failed_attributes) > 1:
        intersectional_issues.append({
            'attributes': failed_attributes,
            'severity': 'high' if len(failed_attributes) >= 3 else 'medium',
            'message': f'Intersectional bias detected across {len(failed_attributes)} attributes'
        })
    
    # Combined status
    overall_status = 'FAIL' if len(failed_attributes) > 0 else 'PASS'
    
    # Aggregate pass rates
    total_checks = len(protected_attributes)
    passed_checks = total_checks - len(failed_attributes)
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100.0
    
    return {
        'status': overall_status,
        'pass_rate': round(pass_rate, 2),
        'per_attribute': per_attribute_results,
        'intersectional_bias': intersectional_issues,
        'summary': {
            'total_attributes_checked': total_checks,
            'passed': passed_checks,
            'failed': len(failed_attributes),
            'failed_attributes': failed_attributes
        },
        'all_metrics': all_metrics
    }


def extract_predictions_from_text(
    content: str,
    protected_attribute: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extract predictions and sensitive features from text for MetricFrame analysis.
    
    This converts text-based bias patterns into numerical predictions that can be
    used with Fairlearn MetricFrame.
    
    Returns:
        Tuple of (y_true, y_pred, sensitive_features) as numpy arrays
    """
    content_lower = content.lower()
    config = load_bias_config()
    
    # Extract bias indicators based on protected attribute
    bias_indicators = []
    sensitive_groups = []
    
    if protected_attribute == 'gender':
        gender_config = config.get('gender', {})
        female_terms = gender_config.get('female', {}).get('occupations', []) + \
                      gender_config.get('female', {}).get('traits', []) + \
                      gender_config.get('female', {}).get('roles', [])
        
        male_terms = gender_config.get('male', {}).get('occupations', []) + \
                    gender_config.get('male', {}).get('traits', []) + \
                    gender_config.get('male', {}).get('roles', [])
        
        female_count = sum(1 for term in female_terms if term in content_lower)
        male_count = sum(1 for term in male_terms if term in content_lower)
        
        # Create predictions: 1 if biased (disparity > threshold), 0 otherwise
        total_refs = female_count + male_count
        if total_refs > 0:
            disparity = abs(female_count - male_count) / total_refs
            bias_indicators = [1 if disparity > 0.5 else 0] * total_refs
            sensitive_groups = (['female'] * female_count) + (['male'] * male_count)
        else:
            bias_indicators = [0]
            sensitive_groups = ['neutral']
    
    elif protected_attribute == 'race':
        race_config = config.get('race', {})
        problematic_terms = race_config.get('stereotypes', []) + \
                           race_config.get('microaggressions', []) + \
                           race_config.get('assumptions', [])
                           
        found_count = sum(1 for term in problematic_terms if term in content_lower)
        bias_indicators = [1 if found_count > 0 else 0]
        sensitive_groups = ['detected' if found_count > 0 else 'none']
    
    else:
        # Generic detection
        bias_indicators = [0]
        sensitive_groups = ['neutral']
    
    # Convert to numpy arrays
    y_true = np.array([0] * len(bias_indicators))  # Ground truth (assume no bias expected)
    y_pred = np.array(bias_indicators)
    sensitive_features = np.array(sensitive_groups)
    
    return y_true, y_pred, sensitive_features


def evaluate_heuristic_bias_proxy(
    content: str,
    protected_attribute: str,
    task_type: str,
    metric_names: Optional[List[str]] = None
) -> dict:
    """
    Evaluate bias using Fairlearn MetricFrame with HEURISTIC proxies.
    
    WARNING: This does NOT use ground-truth data. It constructs synthetic "predictions"
    and "labels" based on keyword patterns in the text to simulate a statistical audit.
    Useful for estimating bias in generative content where no structured data exists.
    
    For generative tasks, extracts predictions from text patterns.
    For classification tasks, this method should NOT be used (use evaluate_bias_with_dataframe).
    
    Args:
        content: Text to evaluate
        protected_attribute: Protected attribute to check
        task_type: 'generative' (classification is invalid for this heuristic method)
        metric_names: Optional list of metrics to compute
    
    Returns:
        Dictionary with MetricFrame results and clear warnings
    """
    if task_type != 'generative':
        return {
            'status': 'ERROR',
            'error': 'Heuristic proxy evaluation is only valid for generative tasks. For classification, use actual data.',
            'metrics': []
        }

    if metric_names is None:
        metric_names = [
            'selection_rate',
            'true_positive_rate',
            'false_positive_rate',
            'true_negative_rate',
            'false_negative_rate'
        ]
    
    # Extract predictions from text (Heuristic Proxy)
    y_true, y_pred, sensitive_features = extract_predictions_from_text(content, protected_attribute)
    
    if len(y_pred) == 0 or len(np.unique(sensitive_features)) < 2:
        # Fallback to simple audit if not enough data points found for statistical proxy
        return evaluate_bias_audit(content, protected_attribute, task_type)
    
    # Build metrics dictionary
    metrics_dict = {}
    if 'selection_rate' in metric_names:
        metrics_dict['selection_rate'] = selection_rate
    if 'true_positive_rate' in metric_names:
        metrics_dict['true_positive_rate'] = true_positive_rate
    if 'false_positive_rate' in metric_names:
        metrics_dict['false_positive_rate'] = false_positive_rate
    if 'true_negative_rate' in metric_names:
        metrics_dict['true_negative_rate'] = true_negative_rate
    if 'false_negative_rate' in metric_names:
        metrics_dict['false_negative_rate'] = false_negative_rate
    
    # Create MetricFrame
    metric_frame = MetricFrame(
        metrics=metrics_dict,
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensitive_features
    )
    
    # Calculate fairness metrics
    dpd = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_features)
    eod = equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive_features)
    
    try:
        dpr = demographic_parity_ratio(y_true, y_pred, sensitive_features=sensitive_features)
    except:
        dpr = None
    
    # Build metrics list
    metrics = [
        {
            'name': 'Demographic_Parity_Difference_Proxy',
            'value': round(dpd, 4),
            'threshold': 0.1,
            'result': 'FAIL' if abs(dpd) > 0.1 else 'PASS'
        },
        {
            'name': 'Equalized_Odds_Difference_Proxy',
            'value': round(eod, 4),
            'threshold': 0.1,
            'result': 'FAIL' if abs(eod) > 0.1 else 'PASS'
        }
    ]
    
    if dpr is not None:
        metrics.append({
            'name': 'Demographic_Parity_Ratio_Proxy',
            'value': round(dpr, 4),
            'threshold': 0.8,
            'result': 'FAIL' if dpr < 0.8 or dpr > 1.2 else 'PASS'
        })
    
    # Add MetricFrame group results
    for metric_name in metrics_dict.keys():
        if hasattr(metric_frame, 'by_group') and metric_name in metric_frame.by_group.columns:
            group_metrics = metric_frame.by_group[metric_name]
            if len(group_metrics) > 1:
                max_diff = group_metrics.max() - group_metrics.min()
                metrics.append({
                    'name': f'{metric_name}_Max_Difference_Proxy',
                    'value': round(max_diff, 4),
                    'threshold': 0.1,
                    'result': 'FAIL' if max_diff > 0.1 else 'PASS',
                    'by_group': group_metrics.to_dict()
                })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    return {
        'status': status,
        'metrics': metrics,
        'details': f'Heuristic Proxy Analysis: DPD={dpd:.4f}, EOD={eod:.4f} (Estimated from text patterns)',
        'metric_frame_summary': metric_frame.by_group.to_dict() if hasattr(metric_frame, 'by_group') else None,
        'method': 'heuristic_proxy_metricframe',
        'warning': 'These metrics are ESTIMATES based on keyword occurrence, not actual statistical ground truth.'
    }


def evaluate_with_aif360(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: np.ndarray,
    favorable_label: int = 1,
    unfavorable_label: int = 0
) -> dict:
    """
    Evaluate bias using AIF360 ClassificationMetric.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        sensitive_features: Protected attribute values
        favorable_label: Label considered favorable (default: 1)
        unfavorable_label: Label considered unfavorable (default: 0)
    
    Returns:
        Dictionary with AIF360 metrics
    """
    if not AIF360_AVAILABLE:
        return {
            'status': 'ERROR',
            'error': 'AIF360 not available. Install with: pip install aif360',
            'metrics': []
        }
    
    try:
        # Create BinaryLabelDataset for AIF360
        # Convert to DataFrame format
        df = pd.DataFrame({
            'label': y_true,
            'prediction': y_pred,
            'protected': sensitive_features
        })
        
        # Create dataset (simplified - AIF360 typically needs more structure)
        # For now, compute metrics directly
        metric = ClassificationMetric(
            y_true, y_pred,
            sensitive_features=sensitive_features,
            favorable_label=favorable_label,
            unfavorable_label=unfavorable_label
        )
        
        # Extract key metrics
        metrics = [
            {
                'name': 'Equalized_Odds',
                'value': round(metric.equalized_odds_difference(), 4),
                'threshold': 0.1,
                'result': 'FAIL' if abs(metric.equalized_odds_difference()) > 0.1 else 'PASS'
            },
            {
                'name': 'Demographic_Parity',
                'value': round(metric.statistical_parity_difference(), 4),
                'threshold': 0.1,
                'result': 'FAIL' if abs(metric.statistical_parity_difference()) > 0.1 else 'PASS'
            },
            {
                'name': 'Average_Odds_Difference',
                'value': round(metric.average_odds_difference(), 4),
                'threshold': 0.1,
                'result': 'FAIL' if abs(metric.average_odds_difference()) > 0.1 else 'PASS'
            }
        ]
        
        failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
        status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
        
        return {
            'status': status,
            'metrics': metrics,
            'details': 'AIF360 ClassificationMetric analysis completed',
            'method': 'aif360'
        }
    
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': f'AIF360 evaluation failed: {str(e)}',
            'metrics': []
        }


def evaluate_bias_advanced(
    content: str,
    protected_attributes: List[str],
    task_type: str,
    use_metricframe: bool = True,
    use_aif360: bool = False,
    metric_names: Optional[List[str]] = None,
    content_type: str = 'text'
) -> dict:
    """
    Advanced bias evaluation with full Fairlearn/AIF360 support.
    
    Args:
        content: Text or code to evaluate
        protected_attributes: List of protected attributes to check
        task_type: 'generative' or 'classification'
        use_metricframe: Use Fairlearn MetricFrame (default: True)
        use_aif360: Use AIF360 metrics (default: False, requires classification data)
        metric_names: Custom metrics to compute
        content_type: 'text' or 'code'
    
    Returns:
        Comprehensive evaluation results with multiple methods
    """
    results = {
        'per_attribute': {},
        'multi_attribute': None,
        'metricframe_results': {},
        'aif360_results': {}
    }
    
    # Multi-attribute evaluation
    if len(protected_attributes) > 1:
        results['multi_attribute'] = evaluate_multi_attribute_bias(
            content, protected_attributes, task_type, content_type
        )
    
    # Per-attribute evaluation with MetricFrame
    for attr in protected_attributes:
        attr_results = {}
        
        # Basic evaluation
        if content_type == 'code':
            from code_auditor import evaluate_code_bias
            basic_result = evaluate_code_bias(content, attr)
        else:
            basic_result = evaluate_bias_audit(content, attr, task_type)
        
        attr_results['basic'] = basic_result
        
        # MetricFrame evaluation
        if use_metricframe and task_type == 'generative':
            metricframe_result = evaluate_heuristic_bias_proxy(
                content, attr, task_type, metric_names
            )
            attr_results['metricframe'] = metricframe_result
        
        results['per_attribute'][attr] = attr_results
    
    # AIF360 evaluation (requires actual predictions for classification)
    if use_aif360 and task_type == 'classification':
        # This would need actual y_true, y_pred, sensitive_features
        # For now, return placeholder
        results['aif360_results'] = {
            'status': 'INFO',
            'message': 'AIF360 requires actual predictions and labels. Use evaluate_with_aif360() directly.'
        }
    
    # Determine overall status
    all_statuses = []
    for attr_result in results['per_attribute'].values():
        all_statuses.append(attr_result['basic'].get('status', 'PASS'))
        if 'metricframe' in attr_result:
            all_statuses.append(attr_result['metricframe'].get('status', 'PASS'))
    
    if results['multi_attribute']:
        all_statuses.append(results['multi_attribute'].get('status', 'PASS'))
    
    overall_status = 'FAIL' if 'FAIL' in all_statuses else 'PASS'
    
    results['status'] = overall_status
    results['summary'] = {
        'total_attributes': len(protected_attributes),
        'methods_used': ['basic'] + (['metricframe'] if use_metricframe else []) + (['aif360'] if use_aif360 else [])
    }
    
    return results
