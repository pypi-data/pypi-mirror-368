"""
Code Analyzer - Analyzes code structure, flow, and potential edge cases
"""
import ast
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int
    line_start: int
    line_end: int

@dataclass
class AnalysisResult:
    language: str
    functions: List[FunctionInfo]
    classes: List[Dict[str, Any]]
    imports: List[str]
    edge_cases: List[str]
    performance_risks: List[str]
    complexity_score: int

class CodeAnalyzer:
    """Analyzes code to understand structure and identify test scenarios."""
    
    def __init__(self):
        self.language_detectors = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java'
        }
    
    def analyze_file(self, file_path: str, language: Optional[str] = None) -> AnalysisResult:
        """Analyze a code file and return structured analysis."""
        path = Path(file_path)
        
        if not language:
            language = self._detect_language(path)
        
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if language == 'python':
            return self._analyze_python(code)
        elif language in ['javascript', 'typescript']:
            return self._analyze_javascript(code)
        elif language == 'java':
            return self._analyze_java(code)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _detect_language(self, path: Path) -> str:
        """Detect programming language from file extension."""
        suffix = path.suffix.lower()
        return self.language_detectors.get(suffix, 'unknown')
    
    def _analyze_python(self, code: str) -> AnalysisResult:
        """Analyze Python code using AST."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Python syntax error: {e}")
        
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(self._extract_python_function(node))
            elif isinstance(node, ast.ClassDef):
                classes.append(self._extract_python_class(node))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.extend(self._extract_python_imports(node))
        
        edge_cases = self._identify_edge_cases(code, 'python')
        performance_risks = self._identify_performance_risks(code, 'python')
        complexity_score = self._calculate_complexity(functions)
        
        return AnalysisResult(
            language='python',
            functions=functions,
            classes=classes,
            imports=imports,
            edge_cases=edge_cases,
            performance_risks=performance_risks,
            complexity_score=complexity_score
        )
    
    def _extract_python_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract function information from AST node."""
        args = [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node)
        complexity = self._calculate_cyclomatic_complexity(node)
        
        return FunctionInfo(
            name=node.name,
            args=args,
            return_type=None,  # Could be enhanced with type hints
            docstring=docstring,
            complexity=complexity,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno
        )
    
    def _extract_python_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract class information from AST node."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        return {
            'name': node.name,
            'methods': methods,
            'line_start': node.lineno,
            'line_end': node.end_lineno or node.lineno
        }
    
    def _extract_python_imports(self, node) -> List[str]:
        """Extract import statements."""
        imports = []
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
        return imports
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _identify_edge_cases(self, code: str, language: str) -> List[str]:
        """Identify potential edge cases in the code."""
        edge_cases = []
        
        # Common edge case patterns
        patterns = {
            'python': [
                (r'len\([^)]+\)', 'Empty collection handling'),
                (r'\/\s*[^\/]', 'Division by zero'),
                (r'\[[^\]]*\]', 'Index out of bounds'),
                (r'int\(', 'Invalid type conversion'),
                (r'open\(', 'File not found'),
                (r'\.split\(', 'Empty string splitting'),
            ]
        }
        
        for pattern, description in patterns.get(language, []):
            if re.search(pattern, code):
                edge_cases.append(description)
        
        return edge_cases
    
    def _identify_performance_risks(self, code: str, language: str) -> List[str]:
        """Identify potential performance risks."""
        risks = []
        
        patterns = {
            'python': [
                (r'for.*in.*for.*in', 'Nested loops'),
                (r'\.append\(.*for.*in', 'List comprehension in loop'),
                (r'time\.sleep\(', 'Blocking sleep calls'),
                (r'requests\.get\(', 'Synchronous HTTP calls'),
            ]
        }
        
        for pattern, description in patterns.get(language, []):
            if re.search(pattern, code):
                risks.append(description)
        
        return risks
    
    def _calculate_complexity(self, functions: List[FunctionInfo]) -> int:
        """Calculate overall complexity score."""
        if not functions:
            return 0
        return sum(f.complexity for f in functions) // len(functions)
    
    def _analyze_javascript(self, code: str) -> AnalysisResult:
        """Basic JavaScript analysis (simplified)."""
        # This would use tree-sitter or similar for proper JS parsing
        functions = self._extract_js_functions(code)
        edge_cases = self._identify_edge_cases(code, 'javascript')
        performance_risks = self._identify_performance_risks(code, 'javascript')
        
        return AnalysisResult(
            language='javascript',
            functions=functions,
            classes=[],
            imports=[],
            edge_cases=edge_cases,
            performance_risks=performance_risks,
            complexity_score=len(functions)
        )
    
    def _extract_js_functions(self, code: str) -> List[FunctionInfo]:
        """Extract JavaScript functions using regex (simplified)."""
        functions = []
        
        # Match function declarations and expressions
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',
            r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
            r'(\w+)\s*:\s*function\s*\(([^)]*)\)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                name = match.group(1)
                args = [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
                
                functions.append(FunctionInfo(
                    name=name,
                    args=args,
                    return_type=None,
                    docstring=None,
                    complexity=1,
                    line_start=code[:match.start()].count('\n') + 1,
                    line_end=code[:match.end()].count('\n') + 1
                ))
        
        return functions
    
    def _analyze_java(self, code: str) -> AnalysisResult:
        """Basic Java analysis (simplified)."""
        # This would use tree-sitter or similar for proper Java parsing
        functions = self._extract_java_methods(code)
        edge_cases = self._identify_edge_cases(code, 'java')
        performance_risks = self._identify_performance_risks(code, 'java')
        
        return AnalysisResult(
            language='java',
            functions=functions,
            classes=[],
            imports=[],
            edge_cases=edge_cases,
            performance_risks=performance_risks,
            complexity_score=len(functions)
        )
    
    def _extract_java_methods(self, code: str) -> List[FunctionInfo]:
        """Extract Java methods using regex (simplified)."""
        functions = []
        
        # Match method declarations
        pattern = r'(public|private|protected)?\s*(static)?\s*(\w+)\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            name = match.group(4)
            args_str = match.group(5)
            args = []
            
            if args_str.strip():
                for arg in args_str.split(','):
                    parts = arg.strip().split()
                    if len(parts) >= 2:
                        args.append(parts[-1])  # Parameter name
            
            functions.append(FunctionInfo(
                name=name,
                args=args,
                return_type=match.group(3),
                docstring=None,
                complexity=1,
                line_start=code[:match.start()].count('\n') + 1,
                line_end=code[:match.end()].count('\n') + 1
            ))
        
        return functions