# py_engine/code_auditor.py
"""
Code-specific bias detection for programming languages.
Detects bias in code comments, variable names, algorithmic logic, and data handling.
"""
import re
from typing import Dict, List, Optional
from core.inclusive_terminology import scan_inclusive_terminology
from core.config_loader import load_bias_config


def evaluate_code_bias(
    code: str,
    protected_attribute: str,
    language: Optional[str] = None
) -> dict:
    """
    Evaluates code for bias in comments, naming, logic, and data handling.
    
    Args:
        code: The source code to evaluate
        protected_attribute: One of 'gender', 'race', 'age', 'disability'
        language: Optional programming language hint (python, javascript, etc.)
    
    Returns:
        Dictionary with status, metrics, and details
    """
    
    code_lower = code.lower()
    
    # Extract different code components
    comments = _extract_comments(code, language)
    variable_names = _extract_variable_names(code, language)
    function_names = _extract_function_names(code, language)
    string_literals = _extract_string_literals(code, language)
    
    # Combine all text for analysis
    all_text = ' '.join([
        ' '.join(comments),
        ' '.join(variable_names),
        ' '.join(function_names),
        ' '.join(string_literals)
    ]).lower()
    
    # Always run inclusive terminology scan (REQ-LEX-01)
    inclusive_scan = scan_inclusive_terminology(code, variable_names, function_names, comments)
    
    # Run protected attribute-specific analysis
    if protected_attribute == 'gender':
        bias_result = _evaluate_code_gender_bias(code, code_lower, all_text, comments, variable_names, function_names)
    elif protected_attribute == 'race':
        bias_result = _evaluate_code_race_bias(code, code_lower, all_text, comments, variable_names, function_names)
    elif protected_attribute == 'age':
        bias_result = _evaluate_code_age_bias(code, code_lower, all_text, comments, variable_names, function_names)
    elif protected_attribute == 'disability':
        bias_result = _evaluate_code_disability_bias(code, code_lower, all_text, comments, variable_names, function_names)
    else:
        bias_result = {
            'status': 'PASS',
            'metrics': [],
            'details': f'Code bias check for {protected_attribute} completed.',
        }
    
    # Merge inclusive terminology results with bias results
    # Add inclusive terminology as a metric
    inclusive_metric = {
        'name': 'Inclusive_Terminology_Scan',
        'value': inclusive_scan['true_positives'],
        'threshold': 0,
        'result': 'FAIL' if inclusive_scan['true_positives'] > 0 else 'PASS',
        'details': {
            'detection_rate': inclusive_scan['detection_rate'],
            'false_positive_rate': inclusive_scan['false_positive_rate'],
            'meets_criteria': inclusive_scan['meets_criteria'],
            'findings_by_severity': inclusive_scan['findings_by_severity'],
        }
    }
    
    # Combine metrics
    combined_metrics = [inclusive_metric] + bias_result.get('metrics', [])
    
    # Determine overall status
    overall_status = 'FAIL' if (
        bias_result['status'] == 'FAIL' or 
        inclusive_scan['status'] == 'FAIL'
    ) else 'PASS'
    
    # Combine details
    combined_details = (
        f"{inclusive_scan['details']} "
        f"{bias_result.get('details', '')}"
    ).strip()
    
    return {
        'status': overall_status,
        'metrics': combined_metrics,
        'details': combined_details,
        'inclusive_terminology': {
            'findings': inclusive_scan['findings'],
            'recommendations': inclusive_scan['recommendations'],
        },
    }


def _extract_comments(code: str, language: Optional[str] = None) -> List[str]:
    """Extract comments from code."""
    comments = []
    
    # Single-line comments (//, #, %)
    single_line_patterns = [
        r'//(.+)',           # JavaScript, C++, Java, etc.
        r'#(.+)',            # Python, Ruby, Shell, etc.
        r'%(.+)',            # MATLAB, LaTeX
        r'--(.+)',           # SQL, Haskell, Lua
    ]
    
    for pattern in single_line_patterns:
        matches = re.findall(pattern, code)
        comments.extend(matches)
    
    # Multi-line comments (/* */, <!-- -->)
    multi_line_patterns = [
        r'/\*(.+?)\*/',      # C-style
        r'<!--(.+?)-->',      # HTML/XML
    ]
    
    for pattern in multi_line_patterns:
        matches = re.findall(pattern, code, re.DOTALL)
        comments.extend(matches)
    
    return [c.strip() for c in comments if c.strip()]


def _extract_variable_names(code: str, language: Optional[str] = None) -> List[str]:
    """Extract variable names from code."""
    # Common variable declaration patterns
    patterns = [
        r'\b(let|const|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)',  # JavaScript/TypeScript
        r'\b(def|val|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)',    # Python/Scala
        r'\b(int|string|float|bool)\s+([a-zA-Z_][a-zA-Z0-9_]*)',  # C-style
        r'\$([a-zA-Z_][a-zA-Z0-9_]*)',                     # PHP
    ]
    
    names = []
    for pattern in patterns:
        matches = re.findall(pattern, code)
        for match in matches:
            if isinstance(match, tuple):
                names.append(match[-1])  # Get the variable name
            else:
                names.append(match)
    
    return names


def _extract_function_names(code: str, language: Optional[str] = None) -> List[str]:
    """Extract function/method names from code."""
    patterns = [
        r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)',         # JavaScript
        r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)',              # Python
        r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',               # Generic function call
        r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function',      # Function assignment
    ]
    
    names = []
    for pattern in patterns:
        matches = re.findall(pattern, code)
        names.extend(matches)
    
    return names


def _extract_string_literals(code: str, language: Optional[str] = None) -> List[str]:
    """Extract string literals from code."""
    # Match strings in quotes (single, double, template literals)
    patterns = [
        r'"([^"]*)"',           # Double quotes
        r"'([^']*)'",            # Single quotes
        r'`([^`]*)`',            # Template literals
    ]
    
    strings = []
    for pattern in patterns:
        matches = re.findall(pattern, code)
        strings.extend(matches)
    
    return strings


def _evaluate_code_gender_bias(
    code: str, code_lower: str, all_text: str,
    comments: List[str], variable_names: List[str], function_names: List[str]
) -> dict:
    """Detect gender bias in code."""
    config = load_bias_config()
    gender_config = config.get('gender', {})
    
    # Gender stereotypes in code context
    female_config = gender_config.get('female', {})
    female_stereotypes = {
        'occupations': female_config.get('occupations', []),
        'traits': female_config.get('traits', []),
        'roles': female_config.get('roles', []),
        'code_patterns': female_config.get('code_patterns', [])
    }
    
    male_config = gender_config.get('male', {})
    male_stereotypes = {
        'occupations': male_config.get('occupations', []),
        'traits': male_config.get('traits', []),
        'roles': male_config.get('roles', []),
        'code_patterns': male_config.get('code_patterns', [])
    }
    
    metrics = []
    
    # 1. Comment bias
    comment_text = ' '.join(comments).lower()
    female_in_comments = sum(1 for word in 
        female_stereotypes['occupations'] + female_stereotypes['traits'] + female_stereotypes['roles']
        if word in comment_text)
    male_in_comments = sum(1 for word in 
        male_stereotypes['occupations'] + male_stereotypes['traits'] + male_stereotypes['roles']
        if word in comment_text)
    
    total_comment_refs = female_in_comments + male_in_comments
    if total_comment_refs > 0:
        comment_disparity = abs(female_in_comments - male_in_comments) / total_comment_refs
        metrics.append({
            'name': 'Comment_Gender_Bias',
            'value': round(comment_disparity, 3),
            'threshold': 0.7,
            'result': 'FAIL' if comment_disparity > 0.7 else 'PASS'
        })
    
    # 2. Variable/function name bias
    all_names = ' '.join(variable_names + function_names).lower()
    female_in_names = sum(1 for pattern in female_stereotypes['code_patterns'] if pattern.lower() in all_names)
    male_in_names = sum(1 for pattern in male_stereotypes['code_patterns'] if pattern.lower() in all_names)
    
    total_name_refs = female_in_names + male_in_names
    if total_name_refs > 0:
        name_disparity = abs(female_in_names - male_in_names) / total_name_refs
        metrics.append({
            'name': 'Naming_Gender_Bias',
            'value': round(name_disparity, 3),
            'threshold': 0.7,
            'result': 'FAIL' if name_disparity > 0.7 else 'PASS'
        })
    
    # 3. String literal bias
    string_text = ' '.join(_extract_string_literals(code)).lower()
    female_in_strings = sum(1 for word in 
        female_stereotypes['occupations'] + female_stereotypes['traits'] + female_stereotypes['roles']
        if word in string_text)
    male_in_strings = sum(1 for word in 
        male_stereotypes['occupations'] + male_stereotypes['traits'] + male_stereotypes['roles']
        if word in string_text)
    
    total_string_refs = female_in_strings + male_in_strings
    if total_string_refs > 0:
        string_disparity = abs(female_in_strings - male_in_strings) / total_string_refs
        metrics.append({
            'name': 'String_Literal_Gender_Bias',
            'value': round(string_disparity, 3),
            'threshold': 0.7,
            'result': 'FAIL' if string_disparity > 0.7 else 'PASS'
        })
    
    # 4. Hardcoded gender assumptions (e.g., if user.gender == 'male')
    hardcoded_patterns = [
        r"gender\s*[=!]+\s*['\"]male['\"]",
        r"gender\s*[=!]+\s*['\"]female['\"]",
        r"sex\s*[=!]+\s*['\"]m['\"]",
        r"sex\s*[=!]+\s*['\"]f['\"]",
    ]
    
    hardcoded_count = sum(1 for pattern in hardcoded_patterns if re.search(pattern, code_lower))
    if hardcoded_count > 0:
        metrics.append({
            'name': 'Hardcoded_Gender_Assumptions',
            'value': hardcoded_count,
            'threshold': 0,
            'result': 'FAIL' if hardcoded_count > 0 else 'PASS'
        })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    details = (
        f'Code analysis: {len(comments)} comments, {len(variable_names)} variables, '
        f'{len(function_names)} functions. Found {female_in_comments + female_in_names} female references, '
        f'{male_in_comments + male_in_names} male references. {hardcoded_count} hardcoded gender assumptions.'
    )
    
    return {
        'status': status,
        'metrics': metrics,
        'details': details,
    }


def _evaluate_code_race_bias(
    code: str, code_lower: str, all_text: str,
    comments: List[str], variable_names: List[str], function_names: List[str]
) -> dict:
    """Detect race bias in code."""
    config = load_bias_config()
    race_config = config.get('race', {})
    
    problematic_patterns = {
        'stereotypes': race_config.get('stereotypes', []),
        'code_patterns': race_config.get('code_patterns', []),
        'assumptions': race_config.get('assumptions', [])
    }
    
    metrics = []
    
    # Check comments and strings
    all_text_lower = all_text.lower()
    found_stereotypes = sum(1 for pattern in problematic_patterns['stereotypes'] if pattern in all_text_lower)
    
    stereotype_score = found_stereotypes / len(problematic_patterns['stereotypes']) if problematic_patterns['stereotypes'] else 0
    metrics.append({
        'name': 'Code_Racial_Stereotype_Score',
        'value': round(stereotype_score, 3),
        'threshold': 0.2,
        'result': 'FAIL' if stereotype_score > 0.2 else 'PASS'
    })
    
    # Check variable/function names
    all_names = ' '.join(variable_names + function_names).lower()
    found_name_patterns = sum(1 for pattern in problematic_patterns['code_patterns'] if pattern.lower() in all_names)
    
    if found_name_patterns > 0:
        metrics.append({
            'name': 'Naming_Racial_Bias',
            'value': found_name_patterns,
            'threshold': 0,
            'result': 'FAIL'
        })
    
    # Hardcoded race assumptions
    hardcoded_patterns = [
        r"race\s*[=!]+\s*['\"](white|black|asian|hispanic|native)['\"]",
        r"ethnicity\s*[=!]+\s*['\"](white|black|asian|hispanic|native)['\"]",
    ]
    
    hardcoded_count = sum(1 for pattern in hardcoded_patterns if re.search(pattern, code_lower))
    if hardcoded_count > 0:
        metrics.append({
            'name': 'Hardcoded_Race_Assumptions',
            'value': hardcoded_count,
            'threshold': 0,
            'result': 'FAIL'
        })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    return {
        'status': status,
        'metrics': metrics,
        'details': f'Found {found_stereotypes} racial stereotypes, {found_name_patterns} problematic name patterns, {hardcoded_count} hardcoded race assumptions.',
    }


def _evaluate_code_age_bias(
    code: str, code_lower: str, all_text: str,
    comments: List[str], variable_names: List[str], function_names: List[str]
) -> dict:
    """Detect age bias in code."""
    config = load_bias_config()
    age_config = config.get('age', {})
    
    age_stereotypes = {
        'young': age_config.get('young', []),
        'old': age_config.get('old', []),
        'ageist': age_config.get('ageist', []),
        'code_patterns': age_config.get('code_patterns', [])
    }
    
    all_text_lower = all_text.lower()
    young_count = sum(1 for word in age_stereotypes['young'] if word in all_text_lower)
    old_count = sum(1 for word in age_stereotypes['old'] if word in all_text_lower)
    ageist_count = sum(1 for phrase in age_stereotypes['ageist'] if phrase in all_text_lower)
    
    metrics = []
    
    total_age_refs = young_count + old_count
    if total_age_refs > 0:
        age_disparity = abs(young_count - old_count) / total_age_refs
        metrics.append({
            'name': 'Code_Age_Reference_Disparity',
            'value': round(age_disparity, 3),
            'threshold': 0.7,
            'result': 'FAIL' if age_disparity > 0.7 else 'PASS'
        })
    
    if ageist_count > 0:
        metrics.append({
            'name': 'Code_Ageist_Language',
            'value': ageist_count,
            'threshold': 0,
            'result': 'FAIL'
        })
    
    # Hardcoded age assumptions
    hardcoded_patterns = [
        r"age\s*[<>=]+\s*\d+",
        r"age\s*[=!]+\s*['\"](young|old|senior|elderly)['\"]",
    ]
    
    hardcoded_count = sum(1 for pattern in hardcoded_patterns if re.search(pattern, code_lower))
    if hardcoded_count > 0:
        metrics.append({
            'name': 'Hardcoded_Age_Assumptions',
            'value': hardcoded_count,
            'threshold': 0,
            'result': 'FAIL'
        })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    return {
        'status': status,
        'metrics': metrics,
        'details': f'Found {young_count} young-associated, {old_count} old-associated, {ageist_count} ageist terms, {hardcoded_count} hardcoded age assumptions.',
    }


def _evaluate_code_disability_bias(
    code: str, code_lower: str, all_text: str,
    comments: List[str], variable_names: List[str], function_names: List[str]
) -> dict:
    """Detect disability bias in code."""
    config = load_bias_config()
    disability_config = config.get('disability', {})
    
    problematic_patterns = {
        'ableist_language': disability_config.get('ableist_language', []),
        'assumptions': disability_config.get('assumptions', []),
        'code_patterns': disability_config.get('code_patterns', [])
    }
    
    all_text_lower = all_text.lower()
    found_ableist = sum(1 for pattern in problematic_patterns['ableist_language'] if pattern in all_text_lower)
    found_assumptions = sum(1 for pattern in problematic_patterns['assumptions'] if pattern in all_text_lower)
    
    metrics = []
    
    ableist_score = found_ableist / len(problematic_patterns['ableist_language']) if problematic_patterns['ableist_language'] else 0
    metrics.append({
        'name': 'Code_Ableist_Language_Score',
        'value': round(ableist_score, 3),
        'threshold': 0.2,
        'result': 'FAIL' if ableist_score > 0.2 else 'PASS'
    })
    
    # Check naming
    all_names = ' '.join(variable_names + function_names).lower()
    found_name_patterns = sum(1 for pattern in problematic_patterns['code_patterns'] if pattern.lower() in all_names)
    
    if found_name_patterns > 0:
        metrics.append({
            'name': 'Naming_Disability_Bias',
            'value': found_name_patterns,
            'threshold': 0,
            'result': 'FAIL'
        })
    
    failed_metrics = [m for m in metrics if m['result'] == 'FAIL']
    status = 'FAIL' if len(failed_metrics) > 0 else 'PASS'
    
    return {
        'status': status,
        'metrics': metrics,
        'details': f'Found {found_ableist} ableist terms, {found_assumptions} assumption patterns, {found_name_patterns} problematic name patterns.',
    }
