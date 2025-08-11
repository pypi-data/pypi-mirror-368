"""
Complexity analyzer: compute comprehensive code metrics using AST analysis.
"""
from __future__ import annotations

import tree_sitter
from typing import List, Dict, Set, Optional, Tuple
import logging

from ..interfaces.base_interfaces import ComplexityMetrics, EdgeCase

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """Computes comprehensive complexity metrics using AST analysis.

    - cyclomatic_complexity: McCabe complexity based on decision points
    - cognitive_complexity: Cognitive load considering nesting and control flow
    - lines_of_code: Non-empty, non-comment lines
    - maintainability_index: Microsoft maintainability index formula
    - performance_risks: Detects loops, recursion, and nested structures
    """

    # Language-specific control flow node types
    CONTROL_FLOW_NODES = {
        'python': {
            'if_statement', 'elif_clause', 'while_statement', 'for_statement',
            'try_statement', 'except_clause', 'with_statement', 'match_statement',
            'case_clause', 'conditional_expression'
        },
        'javascript': {
            'if_statement', 'while_statement', 'for_statement', 'for_in_statement',
            'for_of_statement', 'do_statement', 'switch_statement', 'case_clause',
            'try_statement', 'catch_clause', 'conditional_expression', 'ternary_expression'
        },
        'typescript': {
            'if_statement', 'while_statement', 'for_statement', 'for_in_statement',
            'for_of_statement', 'do_statement', 'switch_statement', 'case_clause',
            'try_statement', 'catch_clause', 'conditional_expression', 'ternary_expression'
        },
        'java': {
            'if_statement', 'while_statement', 'for_statement', 'enhanced_for_statement',
            'do_statement', 'switch_statement', 'case_clause', 'try_statement',
            'catch_clause', 'ternary_expression'
        }
    }

    # Language-specific loop node types
    LOOP_NODES = {
        'python': {'while_statement', 'for_statement'},
        'javascript': {'while_statement', 'for_statement', 'for_in_statement', 'for_of_statement', 'do_statement'},
        'typescript': {'while_statement', 'for_statement', 'for_in_statement', 'for_of_statement', 'do_statement'},
        'java': {'while_statement', 'for_statement', 'enhanced_for_statement', 'do_statement'}
    }

    # Language-specific function call node types
    FUNCTION_CALL_NODES = {
        'python': {'call'},
        'javascript': {'call_expression'},
        'typescript': {'call_expression'},
        'java': {'method_invocation'}
    }

    def analyze(self, code: str, language: str = 'python', ast_node: Optional[tree_sitter.Node] = None) -> ComplexityMetrics:
        """Analyze code complexity using both text-based and AST-based methods."""
        if ast_node is not None:
            return self._analyze_with_ast(ast_node, code, language)
        else:
            return self._analyze_text_based(code)

    def _analyze_text_based(self, code: str) -> ComplexityMetrics:
        """Fallback text-based analysis for backward compatibility."""
        CONTROL_TOKENS = (
            'if ', 'elif ', 'else:', 'for ', 'while ', 'case ', 'switch ', 'try:', 'except', 'catch', '&&', '||'
        )
        
        loc = sum(1 for ln in code.splitlines() if ln.strip())
        cyclo = 1
        for tok in CONTROL_TOKENS:
            cyclo += code.count(tok)
        cognitive = max(0, cyclo - 1)
        mi = max(0.0, 100.0 - (cyclo * 2 + cognitive * 1.5) - (loc * 0.1))
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclo,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=round(mi, 2),
        )

    def _analyze_with_ast(self, ast_node: tree_sitter.Node, code: str, language: str) -> ComplexityMetrics:
        """Comprehensive AST-based complexity analysis."""
        cyclomatic = self._calculate_cyclomatic_complexity(ast_node, language)
        cognitive = self._calculate_cognitive_complexity(ast_node, language)
        loc = self._count_effective_lines_of_code(ast_node, code, language)
        maintainability = self._calculate_maintainability_index(cyclomatic, cognitive, loc)
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=maintainability
        )

    def _calculate_cyclomatic_complexity(self, node: tree_sitter.Node, language: str) -> int:
        """Calculate McCabe cyclomatic complexity from AST."""
        complexity = 1  # Base complexity
        control_flow_nodes = self.CONTROL_FLOW_NODES.get(language, set())
        
        def traverse(n: tree_sitter.Node):
            nonlocal complexity
            if n.type in control_flow_nodes:
                complexity += 1
            
            # Special handling for logical operators
            if n.type in ('boolean_operator', 'binary_expression'):
                # Count && and || operators
                node_text = n.text.decode('utf-8') if hasattr(n, 'text') else ''
                complexity += node_text.count('&&') + node_text.count('||')
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return complexity

    def _calculate_cognitive_complexity(self, node: tree_sitter.Node, language: str) -> int:
        """Calculate cognitive complexity considering nesting and control flow."""
        cognitive = 0
        nesting_level = 0
        control_flow_nodes = self.CONTROL_FLOW_NODES.get(language, set())
        
        def traverse(n: tree_sitter.Node, level: int):
            nonlocal cognitive
            
            if n.type in control_flow_nodes:
                # Base increment for control flow
                cognitive += 1
                
                # Additional increment for nesting
                if level > 0:
                    cognitive += level
                
                # Recursively traverse with increased nesting
                for child in n.children:
                    traverse(child, level + 1)
            else:
                # Continue traversal without increasing nesting for non-control nodes
                for child in n.children:
                    traverse(child, level)
        
        traverse(node, 0)
        return cognitive

    def _count_effective_lines_of_code(self, node: tree_sitter.Node, code: str, language: str) -> int:
        """Count non-empty, non-comment lines of code."""
        lines = code.splitlines()
        effective_lines = 0
        
        # Language-specific comment patterns
        comment_patterns = {
            'python': ['#'],
            'javascript': ['//', '/*', '*/'],
            'typescript': ['//', '/*', '*/'],
            'java': ['//', '/*', '*/']
        }
        
        patterns = comment_patterns.get(language, ['#'])
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check if line is a comment
            is_comment = any(stripped.startswith(pattern) for pattern in patterns)
            if not is_comment:
                effective_lines += 1
        
        return effective_lines

    def _calculate_maintainability_index(self, cyclomatic: int, cognitive: int, loc: int) -> float:
        """Calculate maintainability index using Microsoft formula (simplified)."""
        import math
        
        # Avoid division by zero
        if loc == 0:
            return 100.0
        
        # Simplified maintainability index formula
        # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)
        # Since we don't have Halstead metrics, we use a simplified version
        
        halstead_volume = max(1, loc * 2)  # Simplified approximation
        mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic - 16.2 * math.log(max(1, loc))
        
        # Normalize to 0-100 scale
        mi = max(0.0, min(100.0, mi))
        
        return round(mi, 2)

    def detect_performance_risks(self, node: tree_sitter.Node, code: str, language: str) -> List[EdgeCase]:
        """Detect performance risks like nested loops, recursion, and complex operations."""
        risks = []
        
        # Detect nested loops
        nested_loops = self._detect_nested_loops(node, language)
        for loop_info in nested_loops:
            risks.append(EdgeCase(
                type='nested_loops',
                location=f"Line {loop_info['line']}",
                description=f"Nested loops detected (depth: {loop_info['depth']}) - potential O(n^{loop_info['depth']}) complexity",
                severity=min(5, loop_info['depth'])
            ))
        
        # Detect recursive function calls
        recursive_calls = self._detect_recursion(node, code, language)
        for call_info in recursive_calls:
            risks.append(EdgeCase(
                type='recursion',
                location=f"Line {call_info['line']}",
                description=f"Recursive call to '{call_info['function']}' - potential stack overflow risk",
                severity=3
            ))
        
        # Detect complex operations in loops
        complex_loop_operations = self._detect_complex_loop_operations(node, language)
        for op_info in complex_loop_operations:
            risks.append(EdgeCase(
                type='complex_loop_operation',
                location=f"Line {op_info['line']}",
                description=f"Complex operation in loop - potential performance bottleneck",
                severity=2
            ))
        
        return risks

    def _detect_nested_loops(self, node: tree_sitter.Node, language: str) -> List[Dict]:
        """Detect nested loop structures."""
        nested_loops = []
        loop_nodes = self.LOOP_NODES.get(language, set())
        
        def find_loops(n: tree_sitter.Node, depth: int = 0, parent_is_loop: bool = False):
            if n.type in loop_nodes:
                if parent_is_loop and depth > 1:
                    nested_loops.append({
                        'line': n.start_point[0] + 1,
                        'depth': depth,
                        'type': n.type
                    })
                
                # Continue searching for deeper nesting
                for child in n.children:
                    find_loops(child, depth + 1, True)
            else:
                for child in n.children:
                    find_loops(child, depth, parent_is_loop)
        
        find_loops(node)
        return nested_loops

    def _detect_recursion(self, node: tree_sitter.Node, code: str, language: str) -> List[Dict]:
        """Detect recursive function calls."""
        recursive_calls = []
        function_call_nodes = self.FUNCTION_CALL_NODES.get(language, set())
        
        # First, find all function definitions
        function_names = set()
        self._collect_function_names(node, language, function_names)
        
        # Then find calls to those functions within their own definitions
        def find_recursive_calls(n: tree_sitter.Node, current_function: Optional[str] = None):
            # Check if we're entering a function definition
            if self._is_function_definition(n, language):
                func_name = self._extract_function_name(n, code, language)
                if func_name:
                    current_function = func_name
            
            # Check for function calls
            if n.type in function_call_nodes and current_function:
                call_name = self._extract_call_name(n, code, language)
                if call_name == current_function:
                    recursive_calls.append({
                        'line': n.start_point[0] + 1,
                        'function': current_function,
                        'type': 'direct_recursion'
                    })
            
            for child in n.children:
                find_recursive_calls(child, current_function)
        
        find_recursive_calls(node)
        return recursive_calls

    def _detect_complex_loop_operations(self, node: tree_sitter.Node, language: str) -> List[Dict]:
        """Detect complex operations within loops that might cause performance issues."""
        complex_operations = []
        loop_nodes = self.LOOP_NODES.get(language, set())
        
        # Operations that are potentially expensive
        expensive_operations = {
            'python': {'call'},  # Function calls in loops
            'javascript': {'call_expression', 'new_expression'},
            'typescript': {'call_expression', 'new_expression'},
            'java': {'method_invocation', 'object_creation_expression'}
        }
        
        expensive_ops = expensive_operations.get(language, set())
        
        def find_operations_in_loops(n: tree_sitter.Node, in_loop: bool = False):
            if n.type in loop_nodes:
                in_loop = True
            
            if in_loop and n.type in expensive_ops:
                # Check if this is a nested operation (more expensive)
                nesting_depth = self._calculate_nesting_depth(n, loop_nodes)
                if nesting_depth > 1:
                    complex_operations.append({
                        'line': n.start_point[0] + 1,
                        'operation': n.type,
                        'nesting_depth': nesting_depth
                    })
            
            for child in n.children:
                find_operations_in_loops(child, in_loop)
        
        find_operations_in_loops(node)
        return complex_operations

    def _collect_function_names(self, node: tree_sitter.Node, language: str, function_names: Set[str]):
        """Collect all function names defined in the code."""
        if self._is_function_definition(node, language):
            func_name = self._extract_function_name(node, '', language)
            if func_name:
                function_names.add(func_name)
        
        for child in node.children:
            self._collect_function_names(child, language, function_names)

    def _is_function_definition(self, node: tree_sitter.Node, language: str) -> bool:
        """Check if node is a function definition."""
        function_def_types = {
            'python': {'function_definition'},
            'javascript': {'function_declaration', 'function_expression', 'arrow_function', 'method_definition'},
            'typescript': {'function_declaration', 'function_expression', 'arrow_function', 'method_definition'},
            'java': {'method_declaration'}
        }
        
        return node.type in function_def_types.get(language, set())

    def _extract_function_name(self, node: tree_sitter.Node, code: str, language: str) -> Optional[str]:
        """Extract function name from function definition node."""
        for child in node.children:
            if child.type == 'identifier':
                if hasattr(child, 'text'):
                    return child.text.decode('utf-8')
                elif code:
                    return code[child.start_byte:child.end_byte]
        return None

    def _extract_call_name(self, node: tree_sitter.Node, code: str, language: str) -> Optional[str]:
        """Extract function name from function call node."""
        # This is a simplified implementation - real implementation would be more complex
        for child in node.children:
            if child.type == 'identifier':
                if hasattr(child, 'text'):
                    return child.text.decode('utf-8')
                elif code:
                    return code[child.start_byte:child.end_byte]
        return None

    def _calculate_nesting_depth(self, node: tree_sitter.Node, loop_node_types: Set[str]) -> int:
        """Calculate how deeply nested a node is within loop structures."""
        depth = 0
        current = node.parent
        
        while current:
            if current.type in loop_node_types:
                depth += 1
            current = current.parent
        
        return depth
