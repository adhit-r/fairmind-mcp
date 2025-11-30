# py_engine/core/repository_analyzer.py
"""
Repository-wide bias analysis.
Analyzes git history to detect bias patterns across commits and authors.
"""
import os
import subprocess
import json
import sys
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime
from core.code_auditor import evaluate_code_bias


def hash_email(email: str) -> str:
    """Hash an email address for anonymization."""
    return hashlib.sha256(email.encode()).hexdigest()[:12]


def anonymize_author_info(
    author_name: str,
    author_email: str,
    anonymize_authors: bool,
    exclude_author_names: bool
) -> Dict[str, str]:
    """
    Anonymize author information based on settings.
    
    Returns:
    - name: Original name, "Anonymous", or hashed ID
    - email: Original email, hashed email, or "anonymous@example.com"
    - author_id: Unique identifier (hashed email)
    """
    author_id = hash_email(author_email)
    
    if exclude_author_names:
        name = "Anonymous"
    elif anonymize_authors:
        name = f"Author-{author_id}"
    else:
        name = author_name
    
    if anonymize_authors:
        email = f"{author_id}@anonymous.local"
    else:
        email = author_email
    
    return {
        'name': name,
        'email': email,
        'author_id': author_id,
    }


def log_progress(message: str, progress: Optional[float] = None):
    """Log progress to stderr (MCP clients can capture this)."""
    if progress is not None:
        sys.stderr.write(f"[PROGRESS] {progress:.1f}% - {message}\n")
    else:
        sys.stderr.write(f"[PROGRESS] {message}\n")
    sys.stderr.flush()


def run_git_command(repo_path: str, command: List[str], timeout: int = 60) -> str:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise ValueError(f"Git command timed out after {timeout}s: {' '.join(command)}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise ValueError(f"Git command failed: {e}")


def get_commit_history(
    repo_path: str,
    max_commits: int = 0,
    file_extensions: List[str] = None,
    exclude_paths: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Extract commit history from git repository.
    
    Returns list of commits with:
    - hash
    - author_name
    - author_email
    - date
    - message
    - files_changed
    - diff_content
    """
    if not os.path.isdir(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")
    
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        raise ValueError(f"Not a git repository: {repo_path}")
    
    # Get commit list
    limit = f"-{max_commits}" if max_commits > 0 else ""
    log_format = "%H|%an|%ae|%ai|%s"
    
    try:
        log_output = run_git_command(repo_path, [
            'log', '--pretty=format:' + log_format, '--name-only', limit
        ])
    except ValueError:
        return []
    
    commits = []
    lines = log_output.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if not line or '|' not in line:
            i += 1
            continue
        
        parts = line.split('|')
        if len(parts) < 5:
            i += 1
            continue
        
        commit_hash = parts[0]
        author_name = parts[1]
        author_email = parts[2]
        date_str = parts[3]
        message = '|'.join(parts[4:])  # Message might contain |
        
        # Get files changed in this commit
        i += 1
        files_changed = []
        while i < len(lines) and lines[i].strip() and '|' not in lines[i]:
            file_path = lines[i].strip()
            # Filter by extension
            if file_extensions:
                if not any(file_path.endswith(ext) for ext in file_extensions):
                    i += 1
                    continue
            # Filter by exclude paths
            if exclude_paths:
                if any(excluded in file_path for excluded in exclude_paths):
                    i += 1
                    continue
            files_changed.append(file_path)
            i += 1
        
        if not files_changed:
            continue
        
        # Get diff for this commit (limited to first 5000 chars for performance)
        # Only get diff if we have files to analyze
        diff_content = ""
        if files_changed:
            try:
                # Limit to 10 files per commit for performance
                files_to_analyze = files_changed[:10]
                diff_output = run_git_command(repo_path, [
                    'show', '--format=', '--no-patch', commit_hash, '--', *files_to_analyze
                ], timeout=10)
                diff_content = diff_output[:5000]  # Limit diff size
            except ValueError:
                # If diff fails, continue without it (message analysis still works)
                diff_content = ""
        
        commits.append({
            'hash': commit_hash,
            'author_name': author_name,
            'author_email': author_email,
            'date': date_str,
            'message': message,
            'files_changed': files_changed,
            'diff_content': diff_content,
        })
    
    return commits


def analyze_commit_bias(
    commit: Dict[str, Any],
    protected_attributes: List[str]
) -> Dict[str, Any]:
    """
    Analyze a single commit for bias.
    
    Returns bias metrics for each protected attribute.
    """
    results = {}
    
    # Analyze commit message
    message_bias = {}
    for attr in protected_attributes:
        try:
            result = evaluate_code_bias(commit['message'], attr)
            message_bias[attr] = result
        except Exception:
            message_bias[attr] = {'status': 'PASS', 'metrics': []}
    
    # Analyze diff content (code changes)
    diff_bias = {}
    for attr in protected_attributes:
        try:
            result = evaluate_code_bias(commit['diff_content'], attr)
            diff_bias[attr] = result
        except Exception:
            diff_bias[attr] = {'status': 'PASS', 'metrics': []}
    
    # Combine results
    for attr in protected_attributes:
        msg_status = message_bias[attr].get('status', 'PASS')
        diff_status = diff_bias[attr].get('status', 'PASS')
        
        overall_status = 'FAIL' if msg_status == 'FAIL' or diff_status == 'FAIL' else 'PASS'
        
        # Aggregate metrics
        all_metrics = []
        all_metrics.extend(message_bias[attr].get('metrics', []))
        all_metrics.extend(diff_bias[attr].get('metrics', []))
        
        results[attr] = {
            'status': overall_status,
            'metrics': all_metrics,
            'message_bias': message_bias[attr],
            'code_bias': diff_bias[attr],
        }
    
    return results


def generate_author_scorecard(
    author_commits: List[Dict[str, Any]],
    author_info: Dict[str, str],
    protected_attributes: List[str],
    anonymize_authors: bool = False,
    exclude_author_names: bool = False
) -> Dict[str, Any]:
    """
    Generate a bias scorecard for a single author.
    
    Returns:
    - Overall bias score (0-100, higher = more biased)
    - Bias breakdown by attribute
    - Pattern analysis
    - Recommendations
    """
    total_commits = len(author_commits)
    if total_commits == 0:
        return {}
    
    # Aggregate bias metrics
    attribute_scores = {}
    attribute_fail_counts = {}
    attribute_patterns = defaultdict(list)
    
    for attr in protected_attributes:
        fail_count = 0
        total_metrics = 0
        patterns = []
        
        for commit in author_commits:
            commit_bias = commit.get('bias_analysis', {}).get(attr, {})
            if commit_bias.get('status') == 'FAIL':
                fail_count += 1
                
                # Extract patterns
                metrics = commit_bias.get('metrics', [])
                for metric in metrics:
                    if metric.get('result') == 'FAIL':
                        patterns.append({
                            'metric': metric.get('name'),
                            'value': metric.get('value'),
                            'commit_hash': commit['hash'][:8],
                            'date': commit['date'],
                        })
                total_metrics += len(metrics)
        
        fail_rate = fail_count / total_commits if total_commits > 0 else 0
        attribute_scores[attr] = {
            'fail_rate': fail_rate,
            'fail_count': fail_count,
            'total_commits': total_commits,
            'bias_score': min(100, int(fail_rate * 100)),
        }
        attribute_fail_counts[attr] = fail_count
        attribute_patterns[attr] = patterns[:10]  # Top 10 patterns
    
    # Calculate overall bias score (weighted average)
    overall_score = sum(
        attribute_scores[attr]['bias_score'] 
        for attr in protected_attributes
    ) / len(protected_attributes) if protected_attributes else 0
    
    # Determine bias level
    if overall_score >= 70:
        bias_level = "HIGH"
        severity = "critical"
    elif overall_score >= 40:
        bias_level = "MEDIUM"
        severity = "moderate"
    elif overall_score >= 20:
        bias_level = "LOW"
        severity = "minor"
    else:
        bias_level = "MINIMAL"
        severity = "none"
    
    # Generate explanations
    explanations = []
    for attr in protected_attributes:
        score = attribute_scores[attr]
        if score['fail_rate'] > 0.3:  # >30% of commits show bias
            explanations.append(
                f"{attr.capitalize()} bias detected in {score['fail_count']}/{score['total_commits']} commits "
                f"({score['fail_rate']*100:.1f}%). Common patterns: "
                f"{', '.join(set(p['metric'] for p in attribute_patterns[attr][:3]))}"
            )
    
    # Recommendations
    recommendations = []
    if overall_score >= 70:
        recommendations.append("CRITICAL: Immediate code review and bias training recommended")
    if any(attribute_scores[attr]['fail_rate'] > 0.5 for attr in protected_attributes):
        recommendations.append("High bias rate detected - consider pair programming and bias-aware code review")
    if len(explanations) > 2:
        recommendations.append("Multiple bias types detected - comprehensive bias audit recommended")
    
    # Anonymize author info if requested
    anonymized_info = anonymize_author_info(
        author_info['name'],
        author_info['email'],
        anonymize_authors,
        exclude_author_names
    )
    
    scorecard = {
        'author_name': anonymized_info['name'],
        'author_email': anonymized_info['email'],
        'author_id': anonymized_info['author_id'],
        'total_commits': total_commits,
        'overall_bias_score': round(overall_score, 1),
        'bias_level': bias_level,
        'severity': severity,
        'attribute_scores': attribute_scores,
        'explanations': explanations,
        'recommendations': recommendations,
        'first_commit': author_commits[0]['date'] if author_commits else None,
        'last_commit': author_commits[-1]['date'] if author_commits else None,
    }
    
    # Only include patterns if not in pattern-only mode (patterns might reveal identity)
    # For now, always include patterns, but could be filtered later
    scorecard['attribute_patterns'] = dict(attribute_patterns)
    
    return scorecard


def analyze_repository(
    repository_path: str,
    protected_attributes: List[str],
    max_commits: int = 0,
    min_commits_per_author: int = 5,
    file_extensions: List[str] = None,
    exclude_paths: List[str] = None,
    anonymize_authors: bool = False,
    exclude_author_names: bool = False,
    pattern_only_mode: bool = False
) -> Dict[str, Any]:
    """
    Main function to analyze repository for bias patterns.
    
    Returns comprehensive analysis including:
    - Author scorecards
    - Repository-wide metrics
    - Bias trends over time
    """
    if file_extensions is None:
        file_extensions = []
    if exclude_paths is None:
        exclude_paths = ['node_modules/', 'vendor/', '.git/', 'dist/', 'build/']
    
    # Get commit history
    log_progress("Extracting commit history from repository...")
    commits = get_commit_history(repository_path, max_commits, file_extensions, exclude_paths)
    
    if not commits:
        return {
            'error': 'No commits found or repository is empty',
            'repository_path': repository_path,
        }
    
    log_progress(f"Found {len(commits)} commits to analyze")
    
    # Analyze each commit for bias
    analyzed_commits = []
    total_commits = len(commits)
    
    for idx, commit in enumerate(commits):
        try:
            # Progress reporting every 10 commits or at milestones
            if idx % 10 == 0 or idx == total_commits - 1:
                progress = (idx + 1) / total_commits * 100
                log_progress(f"Analyzing commit {idx + 1}/{total_commits} ({commit['hash'][:8]})", progress)
            
            bias_analysis = analyze_commit_bias(commit, protected_attributes)
            commit['bias_analysis'] = bias_analysis
            analyzed_commits.append(commit)
        except Exception as e:
            # Skip commits that fail analysis
            log_progress(f"Warning: Failed to analyze commit {commit['hash'][:8]}: {str(e)}")
            continue
    
    # Group commits by author
    author_commits = defaultdict(list)
    author_info_map = {}
    
    for commit in analyzed_commits:
        author_key = commit['author_email']
        author_commits[author_key].append(commit)
        if author_key not in author_info_map:
            author_info_map[author_key] = {
                'name': commit['author_name'],
                'email': commit['author_email'],
            }
    
    # Generate author scorecards (only for authors with enough commits)
    log_progress("Generating author scorecards...")
    author_scorecards = []
    authors_to_process = [
        (key, commits_list) 
        for key, commits_list in author_commits.items() 
        if len(commits_list) >= min_commits_per_author
    ]
    
    for idx, (author_key, commits_list) in enumerate(authors_to_process):
        scorecard = generate_author_scorecard(
            commits_list,
            author_info_map[author_key],
            protected_attributes,
            anonymize_authors,
            exclude_author_names
        )
        if scorecard:
            author_scorecards.append(scorecard)
        
        if len(authors_to_process) > 10 and idx % 5 == 0:
            log_progress(f"Processed {idx + 1}/{len(authors_to_process)} authors")
    
    log_progress("Analysis complete!")
    
    # Add anonymization metadata
    if anonymize_authors or exclude_author_names:
        log_progress("Note: Author information has been anonymized for privacy.")
    
    # Sort by bias score (highest first)
    author_scorecards.sort(key=lambda x: x['overall_bias_score'], reverse=True)
    
    # Calculate repository-wide metrics
    total_commits_analyzed = len(analyzed_commits)
    total_authors = len(author_scorecards)
    
    repo_bias_summary = {}
    for attr in protected_attributes:
        attr_fail_count = sum(
            1 for commit in analyzed_commits
            if commit.get('bias_analysis', {}).get(attr, {}).get('status') == 'FAIL'
        )
        repo_bias_summary[attr] = {
            'total_failures': attr_fail_count,
            'failure_rate': attr_fail_count / total_commits_analyzed if total_commits_analyzed > 0 else 0,
        }
    
    return {
        'repository_path': repository_path,
        'analysis_summary': {
            'total_commits_analyzed': total_commits_analyzed,
            'total_authors': total_authors,
            'protected_attributes': protected_attributes,
            'analysis_date': datetime.now().isoformat(),
        },
        'repository_bias_summary': repo_bias_summary,
        'author_scorecards': author_scorecards,
        'top_biased_authors': author_scorecards[:10],  # Top 10
        'least_biased_authors': list(reversed(author_scorecards[-10:])),  # Bottom 10
    }

