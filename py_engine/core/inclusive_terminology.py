# py_engine/inclusive_terminology.py
"""
Inclusive Terminology Scanner (REQ-LEX-01)
Detects non-inclusive terms in code with context-aware filtering to reduce false positives.
"""
import re
from typing import Dict, List, Tuple, Optional


# Denylist of non-inclusive terms with context exceptions
INCLUSIVE_TERMINOLOGY_DENYLIST = {
    # Master/Slave terminology
    'master': {
        'patterns': [r'\bmaster\b', r'\bmaster\s*[-_]?(?:slave|primary|main)', r'\bslave\b'],
        'exceptions': [
            r"master'?s?\s+degree",  # "Master's Degree"
            r"master'?s?\s+thesis",
            r"master'?s?\s+program",
            r"master\s+of\s+",  # "Master of Science"
            r"grand\s+master",  # Chess/Go titles
            r"master\s+key",
        ],
        'severity': 'high',
        'recommendation': 'Use "primary/secondary", "leader/follower", or "main/replica" instead'
    },
    'slave': {
        'patterns': [r'\bslave\b'],
        'exceptions': [],
        'severity': 'high',
        'recommendation': 'Use "replica", "follower", or "secondary" instead'
    },
    
    # Whitelist/Blacklist terminology
    'whitelist': {
        'patterns': [r'\bwhitelist\b', r'\bwhite[-_]list\b'],
        'exceptions': [],
        'severity': 'medium',
        'recommendation': 'Use "allowlist" or "permit list" instead'
    },
    'blacklist': {
        'patterns': [r'\bblacklist\b', r'\bblack[-_]list\b'],
        'exceptions': [],
        'severity': 'medium',
        'recommendation': 'Use "denylist" or "blocklist" instead'
    },
    
    # Sanity check terminology
    'sanity': {
        'patterns': [r'\bsanity\s+check\b', r'\bsanityCheck\b', r'\bsanity_check\b'],
        'exceptions': [],
        'severity': 'low',
        'recommendation': 'Use "validity check", "coherence check", or "consistency check" instead'
    },
    
    # Dummy/test data terminology
    'dummy': {
        'patterns': [r'\bdummy\b', r'\bdummy\s+(?:data|value|object|variable)'],
        'exceptions': [
            r"dummy'?s?\s+guide",  # "Dummy's Guide"
            r"crash\s+dummy",  # Safety testing
        ],
        'severity': 'low',
        'recommendation': 'Use "placeholder", "sample", "test data", or "mock" instead'
    },
    
    # Other problematic terms
    'cripple': {
        'patterns': [r'\bcripple\b', r'\bcrippled\b'],
        'exceptions': [],
        'severity': 'high',
        'recommendation': 'Use "disable" or "degrade" instead'
    },
    'retard': {
        'patterns': [r'\bretard\b', r'\bretarded\b'],
        'exceptions': [],
        'severity': 'high',
        'recommendation': 'Use "delay", "slow", or "throttle" instead'
    },
    'gypsy': {
        'patterns': [r'\bgypsy\b', r'\bgipsy\b'],
        'exceptions': [],
        'severity': 'high',
        'recommendation': 'Use "itinerant" or "nomadic" instead'
    },
    'tribal': {
        'patterns': [r'\btribal\s+knowledge\b'],
        'exceptions': [],
        'severity': 'low',
        'recommendation': 'Use "institutional knowledge" or "team knowledge" instead'
    },
}


def scan_inclusive_terminology(
    code: str,
    variable_names: Optional[List[str]] = None,
    function_names: Optional[List[str]] = None,
    comments: Optional[List[str]] = None
) -> Dict:
    """
    Scans code for non-inclusive terminology (REQ-LEX-01).
    
    Args:
        code: Full source code
        variable_names: List of variable names (optional, for focused scanning)
        function_names: List of function names (optional, for focused scanning)
        comments: List of comments (optional, for focused scanning)
    
    Returns:
        Dictionary with findings, false positive rate estimate, and recommendations
    """
    
    findings = []
    total_matches = 0
    false_positives = 0
    
    # Combine all text sources
    text_sources = {
        'code': code,
        'variables': ' '.join(variable_names or []),
        'functions': ' '.join(function_names or []),
        'comments': ' '.join(comments or []),
    }
    
    # Scan each term in denylist
    for term, config in INCLUSIVE_TERMINOLOGY_DENYLIST.items():
        for pattern in config['patterns']:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            
            # Check each text source
            for source_name, source_text in text_sources.items():
                matches = compiled_pattern.finditer(source_text)
                
                for match in matches:
                    total_matches += 1
                    match_text = match.group(0)
                    match_start = match.start()
                    match_end = match.end()
                    
                    # Check for exceptions (context-aware filtering)
                    is_exception = False
                    for exception_pattern in config.get('exceptions', []):
                        exception_regex = re.compile(exception_pattern, re.IGNORECASE)
                        # Check context around the match
                        context_start = max(0, match_start - 20)
                        context_end = min(len(source_text), match_end + 20)
                        context = source_text[context_start:context_end]
                        
                        if exception_regex.search(context):
                            is_exception = True
                            false_positives += 1
                            break
                    
                    if not is_exception:
                        findings.append({
                            'term': term,
                            'match': match_text,
                            'source': source_name,
                            'position': match_start,
                            'severity': config['severity'],
                            'recommendation': config['recommendation'],
                        })
    
    # Calculate metrics
    true_positives = len(findings)
    false_positive_rate = (false_positives / total_matches * 100) if total_matches > 0 else 0.0
    detection_rate = (true_positives / total_matches * 100) if total_matches > 0 else 0.0
    
    # Group findings by severity
    findings_by_severity = {
        'high': [f for f in findings if f['severity'] == 'high'],
        'medium': [f for f in findings if f['severity'] == 'medium'],
        'low': [f for f in findings if f['severity'] == 'low'],
    }
    
    # Overall status
    status = 'FAIL' if len(findings) > 0 else 'PASS'
    
    # Success criteria check (REQ-LEX-01: >99% detection, <5% false positive)
    meets_criteria = detection_rate >= 99.0 and false_positive_rate < 5.0
    
    return {
        'status': status,
        'meets_criteria': meets_criteria,
        'total_matches': total_matches,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'detection_rate': round(detection_rate, 2),
        'false_positive_rate': round(false_positive_rate, 2),
        'findings': findings,
        'findings_by_severity': {
            'high': len(findings_by_severity['high']),
            'medium': len(findings_by_severity['medium']),
            'low': len(findings_by_severity['low']),
        },
        'details': (
            f'Found {true_positives} non-inclusive terms ({len(findings_by_severity["high"])} high, '
            f'{len(findings_by_severity["medium"])} medium, {len(findings_by_severity["low"])} low severity). '
            f'Detection rate: {detection_rate:.1f}%, False positive rate: {false_positive_rate:.1f}%.'
        ),
        'recommendations': list(set([f['recommendation'] for f in findings])),
    }


def get_inclusive_alternatives(term: str) -> List[str]:
    """
    Get recommended alternatives for a non-inclusive term.
    
    Args:
        term: The non-inclusive term
    
    Returns:
        List of alternative terms
    """
    alternatives_map = {
        'master': ['primary', 'main', 'leader', 'controller'],
        'slave': ['replica', 'follower', 'secondary', 'worker'],
        'whitelist': ['allowlist', 'permit list', 'approved list'],
        'blacklist': ['denylist', 'blocklist', 'rejected list'],
        'sanity': ['validity', 'coherence', 'consistency'],
        'dummy': ['placeholder', 'sample', 'mock', 'test data'],
        'cripple': ['disable', 'degrade', 'limit'],
        'retard': ['delay', 'slow', 'throttle'],
    }
    
    return alternatives_map.get(term.lower(), [])

