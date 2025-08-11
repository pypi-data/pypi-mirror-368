"""
Function Analyzer - Extracts function signatures and metadata from code.
"""
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging

from ..interfaces.base_interfaces import (
    FunctionInfo, ClassInfo, Parameter, ComplexityMetrics
)
from .code_parser import CodeParser, ASTNode

# Configure logging
logger = logging.getLogger(__name__)


class FunctionAnalyzer:
    """Analyzes functions and classes to extract signatures and metadata."""
    
    def __init__(self, code_parser: Optional[CodeParser] = None):
        """Initialize the function analyzer.
        
        Args:
            code_parser: Optional CodeParser instance. If None, creates a new one.
        """
        self.code_parser = code_parser or CodeParser()
    
    def analyze_functions(self, code: str, language: str) -> List[FunctionInfo]:
        """Analyze code and extract function information.
        
        Args:
            code: Source code to analyze
            language: Programming language (python, javascript, java)
            
        Returns:
            List of FunctionInfo objects with extracted metadata
        """
        try:
            # Gracefully handle unsupported languages for test expectations
            if language not in (self.code_parser.languages.keys() if hasattr(self.code_parser, 'languages') else {}):
                logger.warning(f"Unsupported language for function analysis: {language}")
                return []
            ast = self.code_parser.parse_code(code, language)
            functions = self._extract_functions_from_ast(ast, language)
            
            # Enhance functions with additional metadata
            for i, func in enumerate(functions):
                func.complexity = self._calculate_function_complexity(ast, func, language)
                # Best-effort parameter type enhancement
                functions[i].parameters = self.detect_parameter_types(func, language)
                # Best-effort return type inference if missing
                inferred = self.infer_return_type(func, language)
                if inferred and not func.return_type:
                    functions[i].return_type = inferred
                
            logger.info(f"Extracted {len(functions)} functions from {language} code")
            return functions
            
        except Exception as e:
            # Treat unknown languages as warnings to match tests; real errors remain errors upstream
            if isinstance(e, (ValueError,)) and 'Unsupported language' in str(e):
                logger.warning(f"Unsupported language for function analysis: {language}")
            else:
                logger.error(f"Error analyzing functions in {language} code: {e}")
            return []
    
    def analyze_classes(self, code: str, language: str) -> List[ClassInfo]:
        """Analyze code and extract class information.
        
        Args:
            code: Source code to analyze
            language: Programming language (python, javascript, java)
            
        Returns:
            List of ClassInfo objects with extracted metadata
        """
        try:
            if language not in (self.code_parser.languages.keys() if hasattr(self.code_parser, 'languages') else {}):
                logger.warning(f"Unsupported language for class analysis: {language}")
                return []
            ast = self.code_parser.parse_code(code, language)
            classes = self._extract_classes_from_ast(ast, language)
            
            logger.info(f"Extracted {len(classes)} classes from {language} code")
            return classes
            
        except Exception as e:
            if isinstance(e, (ValueError,)) and 'Unsupported language' in str(e):
                logger.warning(f"Unsupported language for class analysis: {language}")
            else:
                logger.error(f"Error analyzing classes in {language} code: {e}")
            return []
    
    def get_function_signature(self, func_info: FunctionInfo, language: str) -> str:
        """Generate a function signature string.
        
        Args:
            func_info: Function information
            language: Programming language
            
        Returns:
            Formatted function signature string
        """
        if language == 'python':
            return self._get_python_signature(func_info)
        elif language in ['javascript', 'typescript']:
            return self._get_javascript_signature(func_info)
        elif language == 'java':
            return self._get_java_signature(func_info)
        else:
            return f"{func_info.name}({', '.join(p.name for p in func_info.parameters)})"
    
    def detect_parameter_types(self, func_info: FunctionInfo, language: str) -> List[Parameter]:
        """Detect or infer parameter types for a function.
        
        Args:
            func_info: Function information
            language: Programming language
            
        Returns:
            List of parameters with enhanced type information
        """
        enhanced_params = []
        
        for param in func_info.parameters:
            # Normalize some default value strings to simplify inference across languages
            default_val = param.default_value
            if isinstance(default_val, str) and language == 'python':
                if default_val == 'True':
                    default_val_norm = 'true'
                elif default_val == 'False':
                    default_val_norm = 'false'
                else:
                    default_val_norm = default_val
            else:
                default_val_norm = default_val

            enhanced_param = Parameter(
                name=param.name,
                type_hint=param.type_hint or self._infer_parameter_type(Parameter(name=param.name, type_hint=param.type_hint, default_value=default_val_norm), language),
                default_value=param.default_value
            )
            enhanced_params.append(enhanced_param)
        
        return enhanced_params

    def infer_return_type(self, func_info: FunctionInfo, language: str) -> Optional[str]:
        """Best-effort return type inference using simple heuristics (non-invasive)."""
        if func_info.return_type:
            return func_info.return_type
        # Prefer explicit language semantics. For now, keep conservative.
        if language == 'python':
            return None
        if language in ['javascript', 'typescript']:
            return None
        if language == 'java':
            return None
        return None
    
    def _extract_functions_from_ast(self, ast: ASTNode, language: str) -> List[FunctionInfo]:
        """Extract function information from AST based on language."""
        if language == 'python':
            return self._extract_python_functions(ast)
        elif language in ['javascript', 'typescript']:
            return self._extract_javascript_functions(ast)
        elif language == 'java':
            return self._extract_java_functions(ast)
        else:
            logger.warning(f"Unsupported language for function extraction: {language}")
            return []
    
    def _extract_classes_from_ast(self, ast: ASTNode, language: str) -> List[ClassInfo]:
        """Extract class information from AST based on language."""
        if language == 'python':
            return self._extract_python_classes(ast)
        elif language in ['javascript', 'typescript']:
            return self._extract_javascript_classes(ast)
        elif language == 'java':
            return self._extract_java_classes(ast)
        else:
            logger.warning(f"Unsupported language for class extraction: {language}")
            return []
    
    def _extract_python_functions(self, ast: ASTNode) -> List[FunctionInfo]:
        """Extract Python function information from AST."""
        functions = []
        function_nodes = self._find_nodes_by_type(ast, 'function_definition')
        
        for func_node in function_nodes:
            try:
                name = self._get_python_function_name(func_node)
                parameters = self._get_python_function_parameters(func_node)
                return_type = self._get_python_return_type(func_node)
                line_range = (func_node.start_point[0] + 1, func_node.end_point[0] + 1)
                docstring = self._get_python_docstring(func_node)
                
                func_info = FunctionInfo(
                    name=name,
                    parameters=parameters,
                    return_type=return_type,
                    complexity=1,  # Will be calculated later
                    line_range=line_range,
                    docstring=docstring
                )
                functions.append(func_info)
                
            except Exception as e:
                logger.warning(f"Error extracting Python function: {e}")
                continue
        
        return functions
    
    def _extract_python_classes(self, ast: ASTNode) -> List[ClassInfo]:
        """Extract Python class information from AST."""
        classes = []
        class_nodes = self._find_nodes_by_type(ast, 'class_definition')
        
        for class_node in class_nodes:
            try:
                name = self._get_python_class_name(class_node)
                methods = self._get_python_class_methods(class_node)
                line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
                inheritance = self._get_python_class_inheritance(class_node)
                
                class_info = ClassInfo(
                    name=name,
                    methods=methods,
                    line_range=line_range,
                    inheritance=inheritance
                )
                classes.append(class_info)
                
            except Exception as e:
                logger.warning(f"Error extracting Python class: {e}")
                continue
        
        return classes
    
    def _extract_javascript_functions(self, ast: ASTNode) -> List[FunctionInfo]:
        """Extract JavaScript function information from AST."""
        functions = []
        
        # Find different types of function declarations
        function_types = [
            'function_declaration',
            'function_expression', 
            'arrow_function',
            'method_definition'
        ]
        
        for func_type in function_types:
            func_nodes = self._find_nodes_by_type(ast, func_type)
            
            for func_node in func_nodes:
                try:
                    name = self._get_javascript_function_name(func_node, func_type)
                    parameters = self._get_javascript_function_parameters(func_node)
                    line_range = (func_node.start_point[0] + 1, func_node.end_point[0] + 1)
                    
                    func_info = FunctionInfo(
                        name=name,
                        parameters=parameters,
                        return_type=None,  # TypeScript would have type info
                        complexity=1,  # Will be calculated later
                        line_range=line_range
                    )
                    functions.append(func_info)
                    
                except Exception as e:
                    logger.warning(f"Error extracting JavaScript function: {e}")
                    continue
        
        return functions
    
    def _extract_javascript_classes(self, ast: ASTNode) -> List[ClassInfo]:
        """Extract JavaScript class information from AST."""
        classes = []
        class_nodes = self._find_nodes_by_type(ast, 'class_declaration')
        
        for class_node in class_nodes:
            try:
                name = self._get_javascript_class_name(class_node)
                methods = self._get_javascript_class_methods(class_node)
                line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
                
                class_info = ClassInfo(
                    name=name,
                    methods=methods,
                    line_range=line_range,
                    inheritance=[]  # Could be enhanced to detect extends
                )
                classes.append(class_info)
                
            except Exception as e:
                logger.warning(f"Error extracting JavaScript class: {e}")
                continue
        
        return classes
    
    def _extract_java_functions(self, ast: ASTNode) -> List[FunctionInfo]:
        """Extract Java method information from AST."""
        functions = []
        method_nodes = self._find_nodes_by_type(ast, 'method_declaration')
        
        for method_node in method_nodes:
            try:
                name = self._get_java_method_name(method_node)
                parameters = self._get_java_method_parameters(method_node)
                return_type = self._get_java_return_type(method_node)
                line_range = (method_node.start_point[0] + 1, method_node.end_point[0] + 1)
                
                func_info = FunctionInfo(
                    name=name,
                    parameters=parameters,
                    return_type=return_type,
                    complexity=1,  # Will be calculated later
                    line_range=line_range
                )
                functions.append(func_info)
                
            except Exception as e:
                logger.warning(f"Error extracting Java method: {e}")
                continue
        
        return functions
    
    def _extract_java_classes(self, ast: ASTNode) -> List[ClassInfo]:
        """Extract Java class information from AST."""
        classes = []
        class_nodes = self._find_nodes_by_type(ast, 'class_declaration')
        
        for class_node in class_nodes:
            try:
                name = self._get_java_class_name(class_node)
                methods = self._get_java_class_methods(class_node)
                line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
                inheritance = self._get_java_class_inheritance(class_node)
                
                class_info = ClassInfo(
                    name=name,
                    methods=methods,
                    line_range=line_range,
                    inheritance=inheritance
                )
                classes.append(class_info)
                
            except Exception as e:
                logger.warning(f"Error extracting Java class: {e}")
                continue
        
        return classes
    
    def _find_nodes_by_type(self, ast: ASTNode, node_type: str) -> List[ASTNode]:
        """Find all nodes of a specific type in the AST."""
        nodes = []
        
        def traverse(node):
            if node.node.type == node_type:
                nodes.append(ASTNode(node.node, ast.source_code, ast.language))
            
            for child in node.node.children:
                traverse(ASTNode(child, ast.source_code, ast.language))
        
        traverse(ast)
        return nodes
    
    def _calculate_function_complexity(self, ast: ASTNode, func_info: FunctionInfo, language: str) -> int:
        """Calculate cyclomatic complexity for a specific function."""
        # Find the function node in the AST
        function_nodes = self._find_nodes_by_type(ast, self._get_function_node_type(language))
        
        for func_node in function_nodes:
            if self._node_matches_function(func_node, func_info, language):
                return self._calculate_cyclomatic_complexity(func_node)
        
        return 1  # Default complexity
    
    def _get_function_node_type(self, language: str) -> str:
        """Get the primary function node type for a language."""
        if language == 'python':
            return 'function_definition'
        elif language in ['javascript', 'typescript']:
            return 'function_declaration'
        elif language == 'java':
            return 'method_declaration'
        else:
            return 'function_definition'
    
    def _node_matches_function(self, node: ASTNode, func_info: FunctionInfo, language: str) -> bool:
        """Check if an AST node matches a specific function."""
        try:
            if language == 'python':
                node_name = self._get_python_function_name(node)
            elif language in ['javascript', 'typescript']:
                node_name = self._get_javascript_function_name(node, node.node.type)
            elif language == 'java':
                node_name = self._get_java_method_name(node)
            else:
                return False
            
            return node_name == func_info.name
        except:
            return False
    
    def _calculate_cyclomatic_complexity(self, func_node: ASTNode) -> int:
        """Calculate cyclomatic complexity for a function node."""
        complexity = 1  # Base complexity
        
        # Decision points that increase complexity
        decision_nodes = [
            'if_statement', 'while_statement', 'for_statement', 'for_in_statement',
            'try_statement', 'catch_clause', 'conditional_expression',
            'switch_statement', 'case_clause', 'logical_operator'
        ]
        
        def count_decisions(node):
            nonlocal complexity
            if node.node.type in decision_nodes:
                complexity += 1
            
            for child in node.node.children:
                count_decisions(ASTNode(child, func_node.source_code, func_node.language))
        
        count_decisions(func_node)
        return complexity
    
    # Language-specific helper methods
    def _get_python_function_name(self, func_node: ASTNode) -> str:
        """Extract Python function name from AST node."""
        for child in func_node.node.children:
            if child.type == 'identifier':
                return func_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_python_function_parameters(self, func_node: ASTNode) -> List[Parameter]:
        """Extract Python function parameters from AST node."""
        parameters = []
        
        for child in func_node.node.children:
            if child.type == 'parameters':
                parameters.extend(self._parse_python_parameters(child, func_node.source_code))
        
        return parameters
    
    def _parse_python_parameters(self, params_node, source_code: str) -> List[Parameter]:
        """Parse Python parameter list."""
        parameters = []
        
        for child in params_node.children:
            if child.type == 'identifier':
                param_name = source_code[child.start_byte:child.end_byte]
                parameters.append(Parameter(name=param_name))
            elif child.type == 'default_parameter':
                # Handle parameters with default values
                param_name = None
                default_value = None
                
                for default_child in child.children:
                    if default_child.type == 'identifier':
                        param_name = source_code[default_child.start_byte:default_child.end_byte]
                    elif default_child.type in ['integer', 'float', 'string', 'true', 'false', 'none']:
                        default_value = source_code[default_child.start_byte:default_child.end_byte]
                
                if param_name:
                    parameters.append(Parameter(name=param_name, default_value=default_value))
            elif child.type == 'typed_parameter':
                # Handle typed parameters
                param_name = None
                type_hint = None
                
                for typed_child in child.children:
                    if typed_child.type == 'identifier':
                        param_name = source_code[typed_child.start_byte:typed_child.end_byte]
                    elif typed_child.type == 'type':
                        type_hint = source_code[typed_child.start_byte:typed_child.end_byte]
                
                if param_name:
                    parameters.append(Parameter(name=param_name, type_hint=type_hint))
            elif child.type == 'typed_default_parameter':
                # Handle typed parameters with default values
                param_name = None
                type_hint = None
                default_value = None
                
                for typed_default_child in child.children:
                    if typed_default_child.type == 'identifier':
                        param_name = source_code[typed_default_child.start_byte:typed_default_child.end_byte]
                    elif typed_default_child.type == 'type':
                        type_hint = source_code[typed_default_child.start_byte:typed_default_child.end_byte]
                    elif typed_default_child.type in ['integer', 'float', 'string', 'true', 'false', 'none']:
                        default_value = source_code[typed_default_child.start_byte:typed_default_child.end_byte]
                
                if param_name:
                    parameters.append(Parameter(name=param_name, type_hint=type_hint, default_value=default_value))
        
        return parameters
    
    def _get_python_return_type(self, func_node: ASTNode) -> Optional[str]:
        """Extract Python function return type annotation."""
        for child in func_node.node.children:
            if child.type == 'type':
                return func_node.source_code[child.start_byte:child.end_byte]
        return None
    
    def _get_python_docstring(self, func_node: ASTNode) -> Optional[str]:
        """Extract Python function docstring."""
        for child in func_node.node.children:
            if child.type == 'block':
                for stmt in child.children:
                    if stmt.type == 'expression_statement':
                        for expr_child in stmt.children:
                            if expr_child.type == 'string':
                                docstring = func_node.source_code[expr_child.start_byte:expr_child.end_byte]
                                return docstring.strip('"\'')
        return None
    
    def _get_python_class_name(self, class_node: ASTNode) -> str:
        """Extract Python class name from AST node."""
        for child in class_node.node.children:
            if child.type == 'identifier':
                return class_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_python_class_methods(self, class_node: ASTNode) -> List[str]:
        """Extract Python class method names."""
        methods = []
        
        for child in class_node.node.children:
            if child.type == 'block':
                method_nodes = self._find_nodes_by_type(
                    ASTNode(child, class_node.source_code, class_node.language),
                    'function_definition'
                )
                for method_node in method_nodes:
                    method_name = self._get_python_function_name(method_node)
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
    
    def _get_javascript_function_name(self, func_node: ASTNode, func_type: str) -> str:
        """Extract JavaScript function name from AST node."""
        if func_type == 'arrow_function':
            return 'anonymous_arrow'
        
        for child in func_node.node.children:
            if child.type == 'identifier':
                return func_node.source_code[child.start_byte:child.end_byte]
            elif child.type == 'property_identifier':
                return func_node.source_code[child.start_byte:child.end_byte]
        
        return 'anonymous'
    
    def _get_javascript_function_parameters(self, func_node: ASTNode) -> List[Parameter]:
        """Extract JavaScript function parameters from AST node."""
        parameters = []
        
        for child in func_node.node.children:
            if child.type == 'formal_parameters':
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_name = func_node.source_code[param_child.start_byte:param_child.end_byte]
                        parameters.append(Parameter(name=param_name))
                    elif param_child.type == 'assignment_pattern':
                        # Handle parameters with default values
                        param_name = None
                        default_value = None
                        
                        for assign_child in param_child.children:
                            if assign_child.type == 'identifier':
                                param_name = func_node.source_code[assign_child.start_byte:assign_child.end_byte]
                            else:
                                default_value = func_node.source_code[assign_child.start_byte:assign_child.end_byte]
                        
                        if param_name:
                            parameters.append(Parameter(name=param_name, default_value=default_value))
        
        return parameters
    
    def _get_javascript_class_name(self, class_node: ASTNode) -> str:
        """Extract JavaScript class name from AST node."""
        for child in class_node.node.children:
            if child.type == 'identifier':
                return class_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_javascript_class_methods(self, class_node: ASTNode) -> List[str]:
        """Extract JavaScript class method names."""
        methods = []
        
        method_nodes = self._find_nodes_by_type(class_node, 'method_definition')
        for method_node in method_nodes:
            method_name = self._get_javascript_function_name(method_node, 'method_definition')
            methods.append(method_name)
        
        return methods
    
    def _get_java_method_name(self, method_node: ASTNode) -> str:
        """Extract Java method name from AST node."""
        for child in method_node.node.children:
            if child.type == 'identifier':
                return method_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_java_method_parameters(self, method_node: ASTNode) -> List[Parameter]:
        """Extract Java method parameters from AST node."""
        parameters = []
        
        for child in method_node.node.children:
            if child.type == 'formal_parameters':
                for param_child in child.children:
                    if param_child.type == 'formal_parameter':
                        param_name = None
                        type_hint = None
                        
                        for formal_child in param_child.children:
                            if formal_child.type == 'identifier':
                                param_name = method_node.source_code[formal_child.start_byte:formal_child.end_byte]
                            elif formal_child.type in ['type_identifier', 'generic_type', 'array_type', 'integral_type', 'floating_point_type']:
                                type_hint = method_node.source_code[formal_child.start_byte:formal_child.end_byte]
                        
                        if param_name:
                            parameters.append(Parameter(name=param_name, type_hint=type_hint))
        
        return parameters
    
    def _get_java_return_type(self, method_node: ASTNode) -> Optional[str]:
        """Extract Java method return type."""
        for child in method_node.node.children:
            if child.type in ['type_identifier', 'generic_type', 'array_type', 'void_type', 'integral_type', 'floating_point_type']:
                return method_node.source_code[child.start_byte:child.end_byte]
        return None
    
    def _get_java_class_name(self, class_node: ASTNode) -> str:
        """Extract Java class name from AST node."""
        for child in class_node.node.children:
            if child.type == 'identifier':
                return class_node.source_code[child.start_byte:child.end_byte]
        return 'unknown'
    
    def _get_java_class_methods(self, class_node: ASTNode) -> List[str]:
        """Extract Java class method names."""
        methods = []
        
        method_nodes = self._find_nodes_by_type(class_node, 'method_declaration')
        for method_node in method_nodes:
            method_name = self._get_java_method_name(method_node)
            methods.append(method_name)
        
        return methods
    
    def _get_java_class_inheritance(self, class_node: ASTNode) -> List[str]:
        """Extract Java class inheritance (extends and implements)."""
        inheritance = []
        
        for child in class_node.node.children:
            if child.type == 'superclass':
                for super_child in child.children:
                    if super_child.type == 'type_identifier':
                        inheritance.append(class_node.source_code[super_child.start_byte:super_child.end_byte])
            elif child.type == 'super_interfaces':
                for interface_child in child.children:
                    if interface_child.type == 'type_identifier':
                        inheritance.append(class_node.source_code[interface_child.start_byte:interface_child.end_byte])
        
        return inheritance
    
    def _get_python_signature(self, func_info: FunctionInfo) -> str:
        """Generate Python function signature."""
        params = []
        for param in func_info.parameters:
            param_str = param.name
            if param.type_hint:
                param_str += f": {param.type_hint}"
            if param.default_value:
                param_str += f" = {param.default_value}"
            params.append(param_str)
        
        signature = f"def {func_info.name}({', '.join(params)})"
        if func_info.return_type:
            signature += f" -> {func_info.return_type}"
        
        return signature
    
    def _get_javascript_signature(self, func_info: FunctionInfo) -> str:
        """Generate JavaScript function signature."""
        params = []
        for param in func_info.parameters:
            param_str = param.name
            if param.default_value:
                param_str += f" = {param.default_value}"
            params.append(param_str)
        
        return f"function {func_info.name}({', '.join(params)})"
    
    def _get_java_signature(self, func_info: FunctionInfo) -> str:
        """Generate Java method signature."""
        params = []
        for param in func_info.parameters:
            param_str = f"{param.type_hint or 'Object'} {param.name}"
            params.append(param_str)
        
        return_type = func_info.return_type or "void"
        return f"public {return_type} {func_info.name}({', '.join(params)})"
    
    def _infer_parameter_type(self, param: Parameter, language: str) -> Optional[str]:
        """Infer parameter type based on default value and language."""
        if not param.default_value:
            return None
        
        default_val = param.default_value.lower()
        
        if language == 'python':
            if default_val in ['true', 'false']:
                return 'bool'
            elif default_val == 'none':
                return 'Optional[Any]'
            elif default_val.startswith('"') or default_val.startswith("'"):
                return 'str'
            elif default_val.isdigit():
                return 'int'
            elif '.' in default_val and default_val.replace('.', '').isdigit():
                return 'float'
            elif default_val.startswith('['):
                return 'List'
            elif default_val.startswith('{'):
                return 'Dict'
        
        elif language in ['javascript', 'typescript']:
            if default_val in ['true', 'false']:
                return 'boolean'
            elif default_val == 'null' or default_val == 'undefined':
                return 'any'
            elif default_val.startswith('"') or default_val.startswith("'"):
                return 'string'
            elif default_val.isdigit() or ('.' in default_val and default_val.replace('.', '').isdigit()):
                return 'number'
            elif default_val.startswith('['):
                return 'Array'
            elif default_val.startswith('{'):
                return 'Object'
        
        elif language == 'java':
            if default_val in ['true', 'false']:
                return 'boolean'
            elif default_val == 'null':
                return 'Object'
            elif default_val.startswith('"'):
                return 'String'
            elif default_val.isdigit():
                return 'int'
            elif '.' in default_val and default_val.replace('.', '').isdigit():
                return 'double'
        
        return None