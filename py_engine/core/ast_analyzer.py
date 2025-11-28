# py_engine/ast_analyzer.py
"""
AST Analysis for Code Bias Detection (REQ-STR-01)
Parses Abstract Syntax Trees and calculates McCabe's Cyclomatic Complexity.
Supports Python (native ast) and JavaScript/TypeScript (via esprima-python or regex fallback).
"""
import ast
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import sys

try:
    import esprima
    ESPRIMA_AVAILABLE = True
except ImportError:
    ESPRIMA_AVAILABLE = False

@dataclass
class ComplexityMetrics:
    """Complexity metrics for a code snippet."""
    cyclomatic_complexity: int
    node_count: int
    edge_count: int
    decision_points: int
    function_count: int
    max_nesting: int
    control_flow_nodes: List[str]


def parse_python_ast(code: str) -> Optional[ast.AST]:
    """
    Parse Python code into an AST.
    
    Args:
        code: Python source code
    
    Returns:
        AST node or None if parsing fails
    """
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def parse_javascript_ast(code: str) -> Optional[Dict]:
    """
    Parse JavaScript/TypeScript code into a simplified AST structure.
    Uses esprima-python if available, otherwise regex-based approximation.
    
    Args:
        code: JavaScript/TypeScript source code
    
    Returns:
        Simplified AST structure or None
    """
    if ESPRIMA_AVAILABLE:
        try:
            return _parse_js_esprima(code)
        except Exception as e:
            print(f"Esprima parsing failed: {e}", file=sys.stderr)
            # Fallback to regex if esprima fails (e.g. newer TS syntax)
            return _parse_js_regex(code)
    else:
        return _parse_js_regex(code)

def _parse_js_esprima(code: str) -> Dict:
    """Parse JS using Esprima."""
    tree = esprima.parseScript(code, {'tolerant': True, 'loc': True})
    
    # Traverse tree to count metrics
    visitor = JSComplexityVisitor()
    visitor.visit(tree)
    
    return {
        'type': 'javascript',
        'decision_points': visitor.decision_points,
        'function_count': visitor.function_count,
        'nesting': visitor.max_nesting,
        'control_flow_nodes': visitor.control_flow_nodes,
        'code': code,
        'method': 'esprima'
    }

class JSComplexityVisitor:
    def __init__(self):
        self.decision_points = 0
        self.function_count = 0
        self.max_nesting = 0
        self.current_nesting = 0
        self.control_flow_nodes = []
        
    def visit(self, node):
        if not node:
            return
            
        # In esprima-python, nodes are objects, not dicts in the same way 
        # But wait, esprima.parseScript returns a specialized object
        
        # We need to handle both object attributes and dict keys if unsure
        # Typically esprima-python returns objects with a 'type' attribute
        
        type_name = getattr(node, 'type', None)
        if not type_name:
            # Check if it's a list (body usually is)
            if isinstance(node, list):
                for item in node:
                    self.visit(item)
                return
            return
            
        method_name = 'visit_' + type_name
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)
        
    def generic_visit(self, node):
        # Iterate over all attributes
        for key in dir(node):
            if key.startswith('_'): continue
            
            value = getattr(node, key)
            
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, 'type'):
                        self.visit(item)
            elif hasattr(value, 'type'):
                self.visit(value)

    def visit_IfStatement(self, node):
        self.decision_points += 1
        self.control_flow_nodes.append('if')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.visit(node.consequent)
        if getattr(node, 'alternate', None):
            self.visit(node.alternate)
        self.current_nesting -= 1

    def visit_ForStatement(self, node):
        self.decision_points += 1
        self.control_flow_nodes.append('for')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.visit(node.body)
        self.current_nesting -= 1

    def visit_WhileStatement(self, node):
        self.decision_points += 1
        self.control_flow_nodes.append('while')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.visit(node.body)
        self.current_nesting -= 1
        
    def visit_DoWhileStatement(self, node):
        self.decision_points += 1
        self.control_flow_nodes.append('do-while')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.visit(node.body)
        self.current_nesting -= 1

    def visit_FunctionDeclaration(self, node):
        self.function_count += 1
        self.visit(node.body)
        
    def visit_FunctionExpression(self, node):
        self.function_count += 1
        self.visit(node.body)
        
    def visit_ArrowFunctionExpression(self, node):
        self.function_count += 1
        self.visit(node.body)

    def visit_SwitchCase(self, node):
        if getattr(node, 'test', None): # default case doesn't add complexity
            self.decision_points += 1
            self.control_flow_nodes.append('case')
        
        # consequent is a list of statements
        if hasattr(node, 'consequent') and isinstance(node.consequent, list):
            for stmt in node.consequent:
                self.visit(stmt)

    def visit_CatchClause(self, node):
        self.decision_points += 1
        self.control_flow_nodes.append('catch')
        self.visit(node.body)
        
    def visit_LogicalExpression(self, node):
        if node.operator in ['&&', '||']:
            self.decision_points += 1
        self.visit(node.left)
        self.visit(node.right)
        
    def visit_ConditionalExpression(self, node):
        self.decision_points += 1
        self.visit(node.consequent)
        self.visit(node.alternate)


def _parse_js_regex(code: str) -> Dict:
    """Basic regex-based parsing for JavaScript (fallback)."""
    try:
        # Count decision points (if, while, for, switch, catch, &&, ||, ?)
        decision_patterns = [
            r'if\s*\(',
            r'while\s*\(',
            r'for\s*\(',
            r'switch\s*\(',
            r'catch\s*\(',
            r'&&',
            r'\|\|',
            r'\?',  # Ternary operator
        ]
        
        decision_count = sum(len(re.findall(pattern, code)) for pattern in decision_patterns)
        
        # Count functions
        function_patterns = [
            r'function\s+\w+',
            r'const\s+\w+\s*=\s*\([^)]*\)\s*=>',
            r'\w+\s*:\s*function',
            r'async\s+function',
        ]
        function_count = sum(len(re.findall(pattern, code)) for pattern in function_patterns)
        
        # Estimate nesting (count braces)
        nesting = _estimate_javascript_nesting(code)
        
        return {
            'type': 'javascript',
            'decision_points': decision_count,
            'function_count': function_count,
            'nesting': nesting,
            'code': code,
            'method': 'regex'
        }
    except Exception as e:
        print(f"Regex parsing failed: {e}", file=sys.stderr)
        return None


def _estimate_javascript_nesting(code: str) -> int:
    """Estimate maximum nesting level in JavaScript code."""
    max_depth = 0
    current_depth = 0
    
    for char in code:
        if char in '{([':
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char in '})]':
            current_depth = max(0, current_depth - 1)
    
    return max_depth


def calculate_python_complexity(ast_node: ast.AST) -> ComplexityMetrics:
    """
    Calculate McCabe's Cyclomatic Complexity for Python code.
    
    Formula: M = E - N + 2P
    Where:
    - E = number of edges
    - N = number of nodes
    - P = number of connected components (usually 1 for a single function)
    
    Args:
        ast_node: Python AST node
    
    Returns:
        ComplexityMetrics object
    """
    visitor = ComplexityVisitor()
    visitor.visit(ast_node)
    
    # McCabe's formula: M = E - N + 2P
    # For simplicity, we count decision points + 1
    # (Each decision point adds 1 to complexity)
    decision_points = visitor.decision_points
    cyclomatic_complexity = decision_points + 1  # Base complexity is 1
    
    return ComplexityMetrics(
        cyclomatic_complexity=cyclomatic_complexity,
        node_count=visitor.node_count,
        edge_count=visitor.edge_count,
        decision_points=decision_points,
        function_count=visitor.function_count,
        max_nesting=visitor.max_nesting,
        control_flow_nodes=visitor.control_flow_nodes,
    )


def calculate_javascript_complexity(js_ast: Dict) -> ComplexityMetrics:
    """
    Calculate complexity metrics for JavaScript code.
    
    Args:
        js_ast: Simplified JavaScript AST structure
    
    Returns:
        ComplexityMetrics object
    """
    decision_points = js_ast.get('decision_points', 0)
    cyclomatic_complexity = decision_points + 1  # Base complexity is 1
    
    return ComplexityMetrics(
        cyclomatic_complexity=cyclomatic_complexity,
        node_count=0,  # Not calculated for JS regex parsing
        edge_count=0,  # Not calculated for JS regex parsing
        decision_points=decision_points,
        function_count=js_ast.get('function_count', 0),
        max_nesting=js_ast.get('nesting', 0),
        control_flow_nodes=js_ast.get('control_flow_nodes', []),
    )


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate complexity metrics."""
    
    def __init__(self):
        self.decision_points = 0
        self.node_count = 0
        self.edge_count = 0
        self.function_count = 0
        self.max_nesting = 0
        self.current_nesting = 0
        self.control_flow_nodes = []
    
    def visit(self, node):
        """Visit a node and increment counters."""
        self.node_count += 1
        return super().visit(node)
    
    def visit_If(self, node):
        """Count if statements as decision points."""
        self.decision_points += 1
        self.control_flow_nodes.append('if')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_For(self, node):
        """Count for loops as decision points."""
        self.decision_points += 1
        self.control_flow_nodes.append('for')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_While(self, node):
        """Count while loops as decision points."""
        self.decision_points += 1
        self.control_flow_nodes.append('while')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_With(self, node):
        """Count with statements (context managers)."""
        self.control_flow_nodes.append('with')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_Try(self, node):
        """Count try/except blocks."""
        self.decision_points += 1  # Exception handling adds complexity
        self.control_flow_nodes.append('try')
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_ExceptHandler(self, node):
        """Count exception handlers."""
        self.decision_points += 1
        self.control_flow_nodes.append('except')
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        """Count boolean operators (and/or) as decision points."""
        # Each operator in a chain adds complexity
        if len(node.values) > 1:
            self.decision_points += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_Compare(self, node):
        """Count comparison operators."""
        # Multiple comparisons add complexity
        if len(node.ops) > 1:
            self.decision_points += len(node.ops) - 1
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Count function definitions."""
        self.function_count += 1
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Count async function definitions."""
        self.function_count += 1
        self.generic_visit(node)
    
    def visit_Lambda(self, node):
        """Count lambda functions."""
        self.function_count += 1
        self.generic_visit(node)


def analyze_code_complexity(code: str, language: Optional[str] = None) -> Optional[ComplexityMetrics]:
    """
    Analyze code complexity for a given code snippet.
    
    Args:
        code: Source code
        language: Programming language ('python', 'javascript', 'typescript', or None for auto-detect)
    
    Returns:
        ComplexityMetrics or None if parsing fails
    """
    # Auto-detect language if not provided
    if language is None:
        if re.search(r'\bdef\s+\w+|import\s+\w+|from\s+\w+', code):
            language = 'python'
        elif re.search(r'\bfunction\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=', code):
            language = 'javascript'
        else:
            # Default to Python for now
            language = 'python'
    
    if language in ['python']:
        ast_node = parse_python_ast(code)
        if ast_node:
            return calculate_python_complexity(ast_node)
    
    elif language in ['javascript', 'typescript']:
        js_ast = parse_javascript_ast(code)
        if js_ast:
            return calculate_javascript_complexity(js_ast)
    
    return None


def normalize_ast_for_comparison(code: str, language: Optional[str] = None) -> str:
    """
    Normalize code for AST comparison by removing comments and formatting.
    
    Args:
        code: Source code
        language: Programming language
    
    Returns:
        Normalized code string
    """
    # Remove single-line comments
    if language in ['python']:
        # Remove Python comments (# ...)
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    elif language in ['javascript', 'typescript']:
        # Remove JavaScript comments (// ... and /* ... */)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    
    # Remove blank lines and normalize whitespace
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    return '\n'.join(lines)
