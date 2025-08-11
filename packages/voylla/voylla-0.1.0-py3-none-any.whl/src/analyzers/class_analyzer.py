"""
Class Analyzer - Extracts class structure information from code.
"""
from typing import List, Optional
import logging

from ..interfaces.base_interfaces import ClassInfo
from .code_parser import CodeParser, ASTNode


logger = logging.getLogger(__name__)


class ClassAnalyzer:
    """Analyzes classes to extract structure and metadata."""

    def __init__(self, code_parser: Optional[CodeParser] = None):
        self.code_parser = code_parser or CodeParser()

    def analyze_classes(self, code: str, language: str) -> List[ClassInfo]:
        """Analyze code and extract class information.

        Args:
            code: Source code to analyze
            language: Programming language (python, javascript, java)

        Returns:
            List of ClassInfo objects
        """
        try:
            ast = self.code_parser.parse_code(code, language)
            return self._extract_classes_from_ast(ast, language)
        except Exception as e:
            logger.error(f"Error analyzing classes in {language} code: {e}")
            return []

    def _extract_classes_from_ast(self, ast: ASTNode, language: str) -> List[ClassInfo]:
        if language == 'python':
            return self._extract_python_classes(ast)
        if language in ['javascript', 'typescript']:
            return self._extract_javascript_classes(ast)
        if language == 'java':
            return self._extract_java_classes(ast)
        logger.warning(f"Unsupported language for class extraction: {language}")
        return []

    # Python helpers
    def _extract_python_classes(self, ast: ASTNode) -> List[ClassInfo]:
        classes: List[ClassInfo] = []
        class_nodes = self._find_nodes_by_type(ast, 'class_definition')
        for class_node in class_nodes:
            name = self._get_identifier(class_node)
            methods = self._get_python_class_methods(class_node)
            line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
            inheritance = self._get_python_class_inheritance(class_node)
            classes.append(ClassInfo(name=name, methods=methods, line_range=line_range, inheritance=inheritance))
        return classes

    def _get_python_class_methods(self, class_node: ASTNode) -> List[str]:
        methods: List[str] = []
        for child in class_node.node.children:
            if child.type == 'block':
                block = ASTNode(child, class_node.source_code, class_node.language)
                for fn in self._find_nodes_by_type(block, 'function_definition'):
                    methods.append(self._get_identifier(fn))
        return methods

    def _get_python_class_inheritance(self, class_node: ASTNode) -> List[str]:
        bases: List[str] = []
        for child in class_node.node.children:
            if child.type == 'argument_list':
                for arg in child.children:
                    if arg.type == 'identifier':
                        bases.append(class_node.source_code[arg.start_byte:arg.end_byte])
        return bases

    # JavaScript helpers
    def _extract_javascript_classes(self, ast: ASTNode) -> List[ClassInfo]:
        classes: List[ClassInfo] = []
        class_nodes = self._find_nodes_by_type(ast, 'class_declaration')
        for class_node in class_nodes:
            name = self._get_identifier(class_node)
            methods = self._get_javascript_class_methods(class_node)
            line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
            classes.append(ClassInfo(name=name, methods=methods, line_range=line_range, inheritance=[]))
        return classes

    def _get_javascript_class_methods(self, class_node: ASTNode) -> List[str]:
        methods: List[str] = []
        for child in class_node.node.children:
            if child.type == 'class_body':
                body = ASTNode(child, class_node.source_code, class_node.language)
                for m in self._find_nodes_by_type(body, 'method_definition'):
                    for n in m.node.children:
                        if n.type in ['property_identifier', 'identifier', 'constructor']:
                            methods.append(class_node.source_code[n.start_byte:n.end_byte])
                            break
        return methods

    # Java helpers
    def _extract_java_classes(self, ast: ASTNode) -> List[ClassInfo]:
        classes: List[ClassInfo] = []
        class_nodes = self._find_nodes_by_type(ast, 'class_declaration')
        for class_node in class_nodes:
            name = self._get_identifier(class_node)
            methods = self._get_java_class_methods(class_node)
            line_range = (class_node.start_point[0] + 1, class_node.end_point[0] + 1)
            inheritance = self._get_java_class_inheritance(class_node)
            classes.append(ClassInfo(name=name, methods=methods, line_range=line_range, inheritance=inheritance))
        return classes

    def _get_java_class_methods(self, class_node: ASTNode) -> List[str]:
        methods: List[str] = []
        for child in class_node.node.children:
            if child.type == 'class_body':
                body = ASTNode(child, class_node.source_code, class_node.language)
                for m in self._find_nodes_by_type(body, 'method_declaration'):
                    # method name is identifier child
                    for n in m.node.children:
                        if n.type == 'identifier':
                            methods.append(class_node.source_code[n.start_byte:n.end_byte])
                            break
        return methods

    def _get_java_class_inheritance(self, class_node: ASTNode) -> List[str]:
        bases: List[str] = []
        for child in class_node.node.children:
            if child.type == 'superclass':
                for sc in child.children:
                    if sc.type == 'type_identifier':
                        bases.append(class_node.source_code[sc.start_byte:sc.end_byte])
            elif child.type == 'super_interfaces':
                for si in child.children:
                    if si.type == 'type_identifier':
                        bases.append(class_node.source_code[si.start_byte:si.end_byte])
        return bases

    # Common helpers
    def _find_nodes_by_type(self, ast: ASTNode, node_type: str) -> List[ASTNode]:
        nodes: List[ASTNode] = []
        def traverse(n: ASTNode):
            if n.node.type == node_type:
                nodes.append(n)
            for ch in n.node.children:
                traverse(ASTNode(ch, ast.source_code, ast.language))
        traverse(ast)
        return nodes

    def _get_identifier(self, node: ASTNode) -> str:
        for ch in node.node.children:
            if ch.type == 'identifier':
                return node.source_code[ch.start_byte:ch.end_byte]
        return 'unknown'
