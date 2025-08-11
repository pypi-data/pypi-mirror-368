"""
Tree-sitter based code parser for multi-language support.
"""
import tree_sitter
from tree_sitter import Language, Parser
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass

from ..interfaces.base_interfaces import (
    ICodeAnalyzer, CodeAnalysis, FunctionInfo, ClassInfo, Parameter,
    EdgeCase, Dependency, ComplexityMetrics
)
from .edge_case_detector import EdgeCaseDetector

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ASTNode:
    """Wrapper for tree-sitter nodes with additional metadata."""
    node: tree_sitter.Node
    source_code: str
    language: str = None
    
    @property
    def text(self) -> str:
        """Get the text content of the node."""
        return self.source_code[self.node.start_byte:self.node.end_byte]
    
    @property
    def type(self) -> str:
        """Get the node type."""
        return self.node.type
    
    @property
    def start_point(self) -> Tuple[int, int]:
        """Get start position (row, column)."""
        return self.node.start_point
    
    @property
    def end_point(self) -> Tuple[int, int]:
        """Get end position (row, column)."""
        return self.node.end_point


class CodeParser(ICodeAnalyzer):
    """Tree-sitter based code parser supporting Python, Java, and JavaScript."""
    
    def __init__(self):
        """Initialize the parser with language support."""
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self.edge_case_detector = EdgeCaseDetector()
        self._setup_languages()
    
    def _setup_languages(self):
        """Set up tree-sitter languages and parsers."""
        try:
            # Import tree-sitter language bindings
            import tree_sitter_python as tspython
            import tree_sitter_javascript as tsjavascript
            import tree_sitter_java as tsjava
            
            # Create language objects
            self.languages['python'] = Language(tspython.language())
            self.languages['javascript'] = Language(tsjavascript.language())
            self.languages['typescript'] = Language(tsjavascript.language())  # Use JS parser for TS
            self.languages['java'] = Language(tsjava.language())
            
            # Create parsers for each language
            for lang_name, language in self.languages.items():
                parser = Parser(language)
                self.parsers[lang_name] = parser
                
            logger.info(f"Initialized parsers for languages: {list(self.languages.keys())}")
            
        except ImportError as e:
            logger.error(f"Failed to import tree-sitter language bindings: {e}")
            raise RuntimeError(f"Tree-sitter language bindings not available: {e}")
    
    def analyze_file(self, file_path: str, language: Optional[str] = None) -> CodeAnalysis:
        """Analyze a code file and return structured analysis."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect language if not provided
        if not language:
            language = self._detect_language(path)
        
        if language not in self.languages:
            raise ValueError(f"Unsupported language: {language}")
        
        # Read file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(path, 'r', encoding='latin-1') as f:
                code = f.read()
        
        return self.analyze_code(code, language)
    
    def analyze_code(self, code: str, language: str) -> CodeAnalysis:
        """Analyze code string and return structured analysis."""
        if language not in self.languages:
            raise ValueError(f"Unsupported language: {language}")
        
        # Parse code into AST
        ast = self.parse_code(code, language)
        
        # Extract information from AST
        functions = self.identify_functions(ast)
        classes = self.identify_classes(ast)
        edge_cases = self.detect_edge_cases(ast)
        dependencies = self.find_dependencies(ast)
        complexity_metrics = self.analyze_complexity(ast)
        
        return CodeAnalysis(
            language=language,
            functions=functions,
            classes=classes,
            edge_cases=edge_cases,
            dependencies=dependencies,
            complexity_metrics=complexity_metrics
        )
    
    def parse_code(self, code: str, language: str) -> ASTNode:
        """Parse code into an abstract syntax tree."""
        if language not in self.parsers:
            raise ValueError(f"No parser available for language: {language}")
        
        parser = self.parsers[language]
        tree = parser.parse(bytes(code, 'utf-8'))
        
        if tree.root_node.has_error:
            logger.warning(f"Parse errors detected in {language} code")
        
        return ASTNode(tree.root_node, code, language)
    
    def _get_language_name(self, ast: ASTNode) -> Optional[str]:
        """Determine language name from AST node."""
        return ast.language
    
    def identify_functions(self, ast: ASTNode) -> List[FunctionInfo]:
        """Extract function information from AST."""
        functions = []
        language = self._get_language_name(ast)
        
        if language == 'python':
            functions.extend(self._extract_python_functions(ast))
        elif language in ['javascript', 'typescript']:
            functions.extend(self._extract_javascript_functions(ast))
        elif language == 'java':
            functions.extend(self._extract_java_functions(ast))
        
        return functions
    
    def identify_classes(self, ast: ASTNode) -> List[ClassInfo]:
        """Extract class information from AST."""
        classes = []
        language = self._get_language_name(ast)
        
        if language == 'python':
            classes.extend(self._extract_python_classes(ast))
        elif language in ['javascript', 'typescript']:
            classes.extend(self._extract_javascript_classes(ast))
        elif language == 'java':
            classes.extend(self._extract_java_classes(ast))
        
        return classes
    
    def detect_edge_cases(self, ast: ASTNode) -> List[EdgeCase]:
        """Detect potential edge cases in code."""
        edge_cases = []
        language = self._get_language_name(ast)
        
        # Use the EdgeCaseDetector for heuristic-based detection
        heuristic_cases = self.edge_case_detector.detect(ast.source_code, language)
        edge_cases.extend(heuristic_cases)
        
        # Also use AST-based language-specific edge case detection for more precise detection
        if language == 'python':
            edge_cases.extend(self._detect_python_edge_cases(ast))
        elif language in ['javascript', 'typescript']:
            edge_cases.extend(self._detect_javascript_edge_cases(ast))
        elif language == 'java':
            edge_cases.extend(self._detect_java_edge_cases(ast))
        
        return edge_cases
    
    def analyze_complexity(self, ast: ASTNode) -> ComplexityMetrics:
        """Analyze code complexity metrics."""
        cyclomatic = self._calculate_cyclomatic_complexity(ast)
        cognitive = self._calculate_cognitive_complexity(ast)
        loc = self._count_lines_of_code(ast)
        maintainability = self._calculate_maintainability_index(cyclomatic, loc)
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=maintainability
        )
    
    def find_dependencies(self, ast: ASTNode) -> List[Dependency]:
        """Find code dependencies."""
        dependencies = []
        language = self._get_language_name(ast)
        
        if language == 'python':
            dependencies.extend(self._find_python_dependencies(ast))
        elif language in ['javascript', 'typescript']:
            dependencies.extend(self._find_javascript_dependencies(ast))
        elif language == 'java':
            dependencies.extend(self._find_java_dependencies(ast))
        
        return dependencies
    
    def _detect_language(self, path: Path) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java'
        }
        
        suffix = path.suffix.lower()
        language = extension_map.get(suffix)
        
        if not language:
            raise ValueError(f"Cannot detect language for file extension: {suffix}")
        
        return language
    
    def _traverse_ast(self, node: tree_sitter.Node, source_code: str, node_type: str = None, language: str = None) -> List[ASTNode]:
        """Traverse AST and find nodes of specific type."""
        nodes = []
        
        if node_type is None or node.type == node_type:
            nodes.append(ASTNode(node, source_code, language))
        
        for child in node.children:
            nodes.extend(self._traverse_ast(child, source_code, node_type, language))
        
        return nodes
    
    # Python-specific methods
    def _extract_python_functions(self, ast: ASTNode) -> List[FunctionInfo]:
        """Extract Python function information."""
        functions = []
        function_nodes = self._traverse_ast(ast.node, ast.source_code, 'function_definition', ast.language)
        
        for func_node in function_nodes:
            name = self._get_python_function_name(func_node)
            parameters = self._get_python_function_parameters(func_node)
            return_type = self._get_python_return_type(func_node)
            complexity = self._calculate_function_complexity(func_node)
            line_range = (func_node.start_point[0] + 1, func_node.end_point[0] + 1)
            docstring = self._get_python_docstring(func_node)
            
            functions.append(FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=return_type,
                complexity=complexity,
                line_range=line_range,
                docstring=docstring
            ))
        
        return functions
    
    def _extract_python_classes(self, ast: ASTNode) -> List[ClassInfo]:
        """Extract Python class information."""
        classes = []
        class_nodes = self._traverse_ast(ast.node, ast.source_code, 'class_definition', ast.language)
        
        for class_node in class_nodes:
            name = self._get_python_class_name(class_node)
            methods = self._get_python_class_methods(class_node)
            line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
            inheritance = self._get_python_class_inheritance(class_node)
            
            classes.append(ClassInfo(
                name=name,
                methods=methods,
                line_range=line_range,
                inheritance=inheritance
            ))
        
        return classes
    
    def _detect_python_edge_cases(self, ast: ASTNode) -> List[EdgeCase]:
        """Detect Python-specific edge cases."""
        edge_cases = []
        
        # Find division operations (potential division by zero)
        div_nodes = self._traverse_ast(ast.node, ast.source_code, 'binary_operator', ast.language)
        for node in div_nodes:
            if '/' in node.text:
                edge_cases.append(EdgeCase(
                    type='division_by_zero',
                    location=f"Line {node.start_point[0] + 1}",
                    description='Potential division by zero',
                    severity=3
                ))
        
        # Find list/dict access (potential index/key errors)
        subscript_nodes = self._traverse_ast(ast.node, ast.source_code, 'subscript', ast.language)
        for node in subscript_nodes:
            edge_cases.append(EdgeCase(
                type='index_access',
                location=f"Line {node.start_point[0] + 1}",
                description='Potential index/key error',
                severity=2
            ))
        
        return edge_cases
    
    def _find_python_dependencies(self, ast: ASTNode) -> List[Dependency]:
        """Find Python import dependencies."""
        dependencies = []
        
        # Find import statements
        import_nodes = self._traverse_ast(ast.node, ast.source_code, 'import_statement', ast.language)
        import_from_nodes = self._traverse_ast(ast.node, ast.source_code, 'import_from_statement', ast.language)
        
        for node in import_nodes + import_from_nodes:
            dep_name = self._extract_import_name(node)
            if dep_name:
                dependencies.append(Dependency(
                    name=dep_name,
                    type='import',
                    source=node.text.strip()
                ))
        
        return dependencies
    
    # JavaScript-specific methods (simplified implementations)
    def _extract_javascript_functions(self, ast: ASTNode) -> List[FunctionInfo]:
        """Extract JavaScript function information."""
        functions = []
        
        # Find function declarations and expressions
        func_types = ['function_declaration', 'function_expression', 'arrow_function']
        for func_type in func_types:
            func_nodes = self._traverse_ast(ast.node, ast.source_code, func_type, ast.language)
            for func_node in func_nodes:
                name = self._get_javascript_function_name(func_node, func_type)
                parameters = self._get_javascript_function_parameters(func_node)
                complexity = self._calculate_function_complexity(func_node)
                line_range = (func_node.start_point[0] + 1, func_node.end_point[0] + 1)
                
                functions.append(FunctionInfo(
                    name=name,
                    parameters=parameters,
                    return_type=None,  # TypeScript would have type info
                    complexity=complexity,
                    line_range=line_range
                ))
        
        # Also find class methods
        method_nodes = self._traverse_ast(ast.node, ast.source_code, 'method_definition', ast.language)
        for method_node in method_nodes:
            name = self._get_javascript_method_name(method_node)
            parameters = self._get_javascript_function_parameters(method_node)
            complexity = self._calculate_function_complexity(method_node)
            line_range = (method_node.start_point[0] + 1, method_node.end_point[0] + 1)
            
            functions.append(FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=None,
                complexity=complexity,
                line_range=line_range
            ))
        
        return functions
    
    def _extract_javascript_classes(self, ast: ASTNode) -> List[ClassInfo]:
        """Extract JavaScript class information."""
        classes = []
        class_nodes = self._traverse_ast(ast.node, ast.source_code, 'class_declaration', ast.language)
        
        for class_node in class_nodes:
            name = self._get_javascript_class_name(class_node)
            methods = self._get_javascript_class_methods(class_node)
            line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
            
            classes.append(ClassInfo(
                name=name,
                methods=methods,
                line_range=line_range,
                inheritance=[]
            ))
        
        return classes
    
    def _detect_javascript_edge_cases(self, ast: ASTNode) -> List[EdgeCase]:
        """Detect JavaScript-specific edge cases."""
        edge_cases = []
        
        # Find null/undefined checks
        binary_nodes = self._traverse_ast(ast.node, ast.source_code, 'binary_expression', ast.language)
        for node in binary_nodes:
            if 'null' in node.text or 'undefined' in node.text:
                edge_cases.append(EdgeCase(
                    type='null_undefined_check',
                    location=f"Line {node.start_point[0] + 1}",
                    description='Null/undefined handling needed',
                    severity=2
                ))
        
        # Find logical expressions that might indicate edge case handling
        unary_nodes = self._traverse_ast(ast.node, ast.source_code, 'unary_expression', ast.language)
        for node in unary_nodes:
            if '!' in node.text:
                edge_cases.append(EdgeCase(
                    type='negation_check',
                    location=f"Line {node.start_point[0] + 1}",
                    description='Negation check - potential edge case handling',
                    severity=1
                ))
        
        # Find try-catch blocks
        try_nodes = self._traverse_ast(ast.node, ast.source_code, 'try_statement', ast.language)
        for node in try_nodes:
            edge_cases.append(EdgeCase(
                type='exception_handling',
                location=f"Line {node.start_point[0] + 1}",
                description='Exception handling detected',
                severity=1
            ))
        
        # Find throw statements
        throw_nodes = self._traverse_ast(ast.node, ast.source_code, 'throw_statement', ast.language)
        for node in throw_nodes:
            edge_cases.append(EdgeCase(
                type='error_throwing',
                location=f"Line {node.start_point[0] + 1}",
                description='Error throwing detected',
                severity=2
            ))
        
        return edge_cases
    
    def _find_javascript_dependencies(self, ast: ASTNode) -> List[Dependency]:
        """Find JavaScript import/require dependencies."""
        dependencies = []
        
        # Find import statements
        import_nodes = self._traverse_ast(ast.node, ast.source_code, 'import_statement', ast.language)
        for node in import_nodes:
            dep_name = self._extract_js_import_name(node)
            if dep_name:
                dependencies.append(Dependency(
                    name=dep_name,
                    type='import',
                    source=node.text.strip()
                ))
        
        return dependencies
    
    # Java-specific methods (simplified implementations)
    def _extract_java_functions(self, ast: ASTNode) -> List[FunctionInfo]:
        """Extract Java method information."""
        functions = []
        method_nodes = self._traverse_ast(ast.node, ast.source_code, 'method_declaration', ast.language)
        
        for method_node in method_nodes:
            name = self._get_java_method_name(method_node)
            parameters = self._get_java_method_parameters(method_node)
            return_type = self._get_java_return_type(method_node)
            complexity = self._calculate_function_complexity(method_node)
            line_range = (method_node.start_point[0] + 1, method_node.end_point[0] + 1)
            
            functions.append(FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=return_type,
                complexity=complexity,
                line_range=line_range
            ))
        
        return functions
    
    def _extract_java_classes(self, ast: ASTNode) -> List[ClassInfo]:
        """Extract Java class information."""
        classes = []
        class_nodes = self._traverse_ast(ast.node, ast.source_code, 'class_declaration', ast.language)
        
        for class_node in class_nodes:
            name = self._get_java_class_name(class_node)
            methods = self._get_java_class_methods(class_node)
            line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
            inheritance = self._get_java_class_inheritance(class_node)
            
            classes.append(ClassInfo(
                name=name,
                methods=methods,
                line_range=line_range,
                inheritance=inheritance
            ))
        
        return classes
    
    def _detect_java_edge_cases(self, ast: ASTNode) -> List[EdgeCase]:
        """Detect Java-specific edge cases."""
        edge_cases = []
        
        # Find null pointer potential from field access
        member_access_nodes = self._traverse_ast(ast.node, ast.source_code, 'field_access', ast.language)
        for node in member_access_nodes:
            edge_cases.append(EdgeCase(
                type='null_pointer',
                location=f"Line {node.start_point[0] + 1}",
                description='Potential null pointer exception',
                severity=3
            ))
        
        # Find method invocations (potential null pointer)
        method_invocation_nodes = self._traverse_ast(ast.node, ast.source_code, 'method_invocation', ast.language)
        for node in method_invocation_nodes:
            edge_cases.append(EdgeCase(
                type='null_pointer',
                location=f"Line {node.start_point[0] + 1}",
                description='Potential null pointer exception on method call',
                severity=2
            ))
        
        # Find array access (potential index out of bounds)
        array_access_nodes = self._traverse_ast(ast.node, ast.source_code, 'array_access', ast.language)
        for node in array_access_nodes:
            edge_cases.append(EdgeCase(
                type='array_bounds',
                location=f"Line {node.start_point[0] + 1}",
                description='Potential array index out of bounds',
                severity=3
            ))
        
        # Find null comparisons (good practice, but indicates null handling)
        binary_expr_nodes = self._traverse_ast(ast.node, ast.source_code, 'binary_expression', ast.language)
        for node in binary_expr_nodes:
            if 'null' in node.text:
                edge_cases.append(EdgeCase(
                    type='null_check',
                    location=f"Line {node.start_point[0] + 1}",
                    description='Null check detected',
                    severity=1
                ))
        
        return edge_cases
    
    def _find_java_dependencies(self, ast: ASTNode) -> List[Dependency]:
        """Find Java import dependencies."""
        dependencies = []
        
        import_nodes = self._traverse_ast(ast.node, ast.source_code, 'import_declaration', ast.language)
        for node in import_nodes:
            dep_name = self._extract_java_import_name(node)
            if dep_name:
                dependencies.append(Dependency(
                    name=dep_name,
                    type='import',
                    source=node.text.strip()
                ))
        
        return dependencies
    
    # Helper methods for extracting specific information
    def _get_python_function_name(self, func_node: ASTNode) -> str:
        """Extract Python function name."""
        for child in func_node.node.children:
            if child.type == 'identifier':
                return func_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_python_function_parameters(self, func_node: ASTNode) -> List[Parameter]:
        """Extract Python function parameters."""
        parameters = []
        for child in func_node.node.children:
            if child.type == 'parameters':
                # Look for parameter nodes within the parameters
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_name = func_node.source_code[param_child.start_byte:param_child.end_byte]
                        parameters.append(Parameter(name=param_name))
                    elif param_child.type == 'default_parameter':
                        # Handle parameters with default values
                        for default_child in param_child.children:
                            if default_child.type == 'identifier':
                                param_name = func_node.source_code[default_child.start_byte:default_child.end_byte]
                                parameters.append(Parameter(name=param_name))
                                break
                    elif param_child.type == 'typed_parameter':
                        # Handle typed parameters
                        for typed_child in param_child.children:
                            if typed_child.type == 'identifier':
                                param_name = func_node.source_code[typed_child.start_byte:typed_child.end_byte]
                                parameters.append(Parameter(name=param_name))
                                break
                    elif param_child.type == 'typed_default_parameter':
                        # Handle typed parameters with default values
                        for typed_default_child in param_child.children:
                            if typed_default_child.type == 'identifier':
                                param_name = func_node.source_code[typed_default_child.start_byte:typed_default_child.end_byte]
                                parameters.append(Parameter(name=param_name))
                                break
        return parameters
    
    def _get_python_return_type(self, func_node: ASTNode) -> Optional[str]:
        """Extract Python function return type annotation."""
        # Look for type annotation after '->'
        for child in func_node.node.children:
            if child.type == 'type':
                return func_node.source_code[child.start_byte:child.end_byte]
        return None
    
    def _get_python_docstring(self, func_node: ASTNode) -> Optional[str]:
        """Extract Python function docstring."""
        # Look for string literal as first statement in function body
        for child in func_node.node.children:
            if child.type == 'block':
                for stmt in child.children:
                    if stmt.type == 'expression_statement':
                        for expr_child in stmt.children:
                            if expr_child.type == 'string':
                                return func_node.source_code[expr_child.start_byte:expr_child.end_byte].strip('"\'')
        return None
    
    def _get_python_class_name(self, class_node: ASTNode) -> str:
        """Extract Python class name."""
        for child in class_node.node.children:
            if child.type == 'identifier':
                return class_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_python_class_methods(self, class_node: ASTNode) -> List[str]:
        """Extract Python class method names."""
        methods = []
        for child in class_node.node.children:
            if child.type == 'block':
                func_nodes = self._traverse_ast(child, class_node.source_code, 'function_definition', class_node.language)
                for func_node in func_nodes:
                    method_name = self._get_python_function_name(func_node)
                    methods.append(method_name)
        return methods
    
    def _get_python_class_inheritance(self, class_node: ASTNode) -> List[str]:
        """Extract Python class inheritance."""
        inheritance = []
        for child in class_node.node.children:
            if child.type == 'argument_list':
                for arg_child in child.children:
                    if arg_child.type == 'identifier':
                        inheritance.append(class_node.source_code[arg_child.start_byte:arg_child.end_byte])
        return inheritance
    
    # Simplified implementations for JavaScript and Java helper methods
    def _get_javascript_function_name(self, func_node: ASTNode, func_type: str) -> str:
        """Extract JavaScript function name."""
        if func_type == 'arrow_function':
            return 'anonymous_arrow'
        
        for child in func_node.node.children:
            if child.type == 'identifier':
                return func_node.source_code[child.start_byte:child.end_byte]
        return 'anonymous'
    
    def _get_javascript_function_parameters(self, func_node: ASTNode) -> List[Parameter]:
        """Extract JavaScript function parameters."""
        parameters = []
        for child in func_node.node.children:
            if child.type == 'formal_parameters':
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_name = func_node.source_code[param_child.start_byte:param_child.end_byte]
                        parameters.append(Parameter(name=param_name))
        return parameters
    
    def _get_javascript_method_name(self, method_node: ASTNode) -> str:
        """Extract JavaScript method name."""
        for child in method_node.node.children:
            if child.type == 'property_identifier':
                return method_node.source_code[child.start_byte:child.end_byte]
            elif child.type == 'identifier':
                return method_node.source_code[child.start_byte:child.end_byte]
        return 'unknown_method'
    
    def _get_javascript_class_name(self, class_node: ASTNode) -> str:
        """Extract JavaScript class name."""
        for child in class_node.node.children:
            if child.type == 'identifier':
                return class_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_javascript_class_methods(self, class_node: ASTNode) -> List[str]:
        """Extract JavaScript class method names."""
        methods = []
        for child in class_node.node.children:
            if child.type == 'class_body':
                # Look for method definitions and constructor
                method_nodes = self._traverse_ast(child, class_node.source_code, 'method_definition', class_node.language)
                for method_node in method_nodes:
                    for method_child in method_node.node.children:
                        if method_child.type == 'property_identifier':
                            method_name = class_node.source_code[method_child.start_byte:method_child.end_byte]
                            methods.append(method_name)
                        elif method_child.type == 'constructor' or method_child.type == 'identifier':
                            method_name = class_node.source_code[method_child.start_byte:method_child.end_byte]
                            if method_name not in methods:
                                methods.append(method_name)
        return methods
    
    def _get_java_method_name(self, method_node: ASTNode) -> str:
        """Extract Java method name."""
        for child in method_node.node.children:
            if child.type == 'identifier':
                return method_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_java_method_parameters(self, method_node: ASTNode) -> List[Parameter]:
        """Extract Java method parameters."""
        parameters = []
        for child in method_node.node.children:
            if child.type == 'formal_parameters':
                for param_child in child.children:
                    if param_child.type == 'formal_parameter':
                        # Extract parameter name (last identifier in formal_parameter)
                        identifiers = [c for c in param_child.children if c.type == 'identifier']
                        if identifiers:
                            param_name = method_node.source_code[identifiers[-1].start_byte:identifiers[-1].end_byte]
                            parameters.append(Parameter(name=param_name))
        return parameters
    
    def _get_java_return_type(self, method_node: ASTNode) -> Optional[str]:
        """Extract Java method return type."""
        # Look for type before method name
        for i, child in enumerate(method_node.node.children):
            if child.type == 'identifier' and i > 0:
                # Previous child might be the return type
                prev_child = method_node.node.children[i-1]
                if prev_child.type in ['type_identifier', 'primitive_type']:
                    return method_node.source_code[prev_child.start_byte:prev_child.end_byte]
        return None
    
    def _get_java_class_name(self, class_node: ASTNode) -> str:
        """Extract Java class name."""
        for child in class_node.node.children:
            if child.type == 'identifier':
                return class_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_java_class_methods(self, class_node: ASTNode) -> List[str]:
        """Extract Java class method names."""
        methods = []
        for child in class_node.node.children:
            if child.type == 'class_body':
                method_nodes = self._traverse_ast(child, class_node.source_code, 'method_declaration', class_node.language)
                for method_node in method_nodes:
                    method_name = self._get_java_method_name(method_node)
                    methods.append(method_name)
        return methods
    
    def _get_java_class_inheritance(self, class_node: ASTNode) -> List[str]:
        """Extract Java class inheritance."""
        inheritance = []
        for child in class_node.node.children:
            if child.type == 'superclass':
                for super_child in child.children:
                    if super_child.type == 'type_identifier':
                        inheritance.append(class_node.source_code[super_child.start_byte:super_child.end_byte])
        return inheritance
    
    # Complexity calculation methods
    def _calculate_cyclomatic_complexity(self, ast: ASTNode) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_nodes = ['if_statement', 'while_statement', 'for_statement', 
                         'try_statement', 'catch_clause', 'switch_statement']
        
        for node_type in decision_nodes:
            nodes = self._traverse_ast(ast.node, ast.source_code, node_type, ast.language)
            complexity += len(nodes)
        
        return complexity
    
    def _calculate_cognitive_complexity(self, ast: ASTNode) -> int:
        """Calculate cognitive complexity (simplified)."""
        # For now, use cyclomatic complexity as approximation
        return self._calculate_cyclomatic_complexity(ast)
    
    def _count_lines_of_code(self, ast: ASTNode) -> int:
        """Count lines of code."""
        return len(ast.source_code.split('\n'))
    
    def _calculate_maintainability_index(self, cyclomatic: int, loc: int) -> float:
        """Calculate maintainability index (simplified formula)."""
        if loc == 0:
            return 100.0
        
        # Simplified MI calculation
        mi = max(0, (171 - 5.2 * (cyclomatic / loc) * 100 - 0.23 * cyclomatic - 16.2 * (loc / 1000)) / 171 * 100)
        return round(mi, 2)
    
    def _calculate_function_complexity(self, func_node: ASTNode) -> int:
        """Calculate complexity for a specific function."""
        return self._calculate_cyclomatic_complexity(func_node)
    
    # Import extraction methods
    def _extract_import_name(self, import_node: ASTNode) -> Optional[str]:
        """Extract import name from Python import node."""
        # Simplified extraction - would need more sophisticated parsing
        text = import_node.text.strip()
        if text.startswith('import '):
            return text.replace('import ', '').split()[0]
        elif text.startswith('from '):
            parts = text.split()
            if len(parts) >= 2:
                return parts[1]
        return None
    
    def _extract_js_import_name(self, import_node: ASTNode) -> Optional[str]:
        """Extract import name from JavaScript import node."""
        # Look for string literal in import statement
        for child in import_node.node.children:
            if child.type == 'string':
                return import_node.source_code[child.start_byte:child.end_byte].strip('"\'')
        return None
    
    def _extract_java_import_name(self, import_node: ASTNode) -> Optional[str]:
        """Extract import name from Java import node."""
        # Look for scoped_identifier or identifier
        for child in import_node.node.children:
            if child.type in ['scoped_identifier', 'identifier']:
                return import_node.source_code[child.start_byte:child.end_byte]
        return None