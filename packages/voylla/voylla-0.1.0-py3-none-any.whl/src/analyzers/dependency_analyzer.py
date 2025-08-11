"""
Dependency analyzer: extract imports, external calls, and module dependencies using AST analysis.
"""
from __future__ import annotations

import re
import tree_sitter
from typing import List, Dict, Set, Optional, Tuple
import logging

from ..interfaces.base_interfaces import Dependency, EdgeCase

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Comprehensive dependency analysis using AST parsing and pattern recognition.

    Detects:
    - Import statements (all languages)
    - External API calls and database connections
    - Module dependencies and circular imports
    - Third-party library usage
    - File system and network operations
    """

    # Language-specific import node types
    IMPORT_NODES = {
        'python': {'import_statement', 'import_from_statement'},
        'javascript': {'import_statement', 'import_declaration'},
        'typescript': {'import_statement', 'import_declaration'},
        'java': {'import_declaration'}
    }

    # Language-specific function call node types
    CALL_NODES = {
        'python': {'call'},
        'javascript': {'call_expression'},
        'typescript': {'call_expression'},
        'java': {'method_invocation'}
    }

    # Patterns for detecting external dependencies
    EXTERNAL_PATTERNS = {
        'database': [
            r'sqlite3?', r'mysql', r'postgresql', r'psycopg2', r'pymongo', r'redis',
            r'sequelize', r'mongoose', r'knex', r'typeorm', r'prisma',
            r'jdbc', r'hibernate', r'mybatis', r'jpa'
        ],
        'http_client': [
            r'requests', r'urllib', r'httpx', r'aiohttp',
            r'axios', r'fetch', r'xhr', r'superagent',
            r'okhttp', r'apache\.http', r'java\.net\.http'
        ],
        'web_framework': [
            r'flask', r'django', r'fastapi', r'tornado', r'pyramid',
            r'express', r'koa', r'nestjs', r'next', r'nuxt',
            r'spring', r'struts', r'jersey'
        ],
        'testing': [
            r'pytest', r'unittest', r'nose', r'mock',
            r'jest', r'mocha', r'jasmine', r'cypress', r'playwright',
            r'junit', r'testng', r'mockito'
        ],
        'cloud_services': [
            r'boto3', r'azure', r'google\.cloud',
            r'aws-sdk', r'@azure', r'@google-cloud',
            r'amazonaws', r'azure\.', r'google\.cloud'
        ]
    }

    def detect(self, code: str, language: str, ast_node: Optional[tree_sitter.Node] = None) -> List[Dependency]:
        """Detect dependencies using both AST and pattern-based analysis."""
        if ast_node is not None:
            return self._detect_with_ast(ast_node, code, language)
        else:
            return self._detect_text_based(code, language)

    def _detect_text_based(self, code: str, language: str) -> List[Dependency]:
        """Fallback text-based dependency detection for backward compatibility."""
        deps: List[Dependency] = []
        lines = code.splitlines()

        def add(name: str, kind: str, source: str = None):
            deps.append(Dependency(name=name, type=kind, source=source))

        if language == 'python':
            for ln in lines:
                m = re.match(r"\s*import\s+([\w\.]+)", ln)
                if m:
                    add(m.group(1), 'import', ln.strip())
                m = re.match(r"\s*from\s+([\w\.]+)\s+import\s+([\w\*,\s]+)", ln)
                if m:
                    add(m.group(1), 'import', ln.strip())
        elif language in ('javascript', 'typescript'):
            for ln in lines:
                m = re.match(r"\s*import\s+.*from\s+['\"]([^'\"]+)['\"]", ln)
                if m:
                    add(m.group(1), 'import', ln.strip())
                m = re.match(r"\s*const\s+\w+\s*=\s*require\(['\"]([^'\"]+)['\"]\)\s*;?", ln)
                if m:
                    add(m.group(1), 'import', ln.strip())
        elif language == 'java':
            for ln in lines:
                m = re.match(r"\s*import\s+([\w\.\*]+);", ln)
                if m:
                    add(m.group(1), 'import', ln.strip())

        return deps

    def _detect_with_ast(self, ast_node: tree_sitter.Node, code: str, language: str) -> List[Dependency]:
        """Comprehensive AST-based dependency detection."""
        dependencies = []
        
        # Detect import statements
        import_deps = self._detect_imports(ast_node, code, language)
        dependencies.extend(import_deps)
        
        # Detect external API calls
        api_deps = self._detect_external_calls(ast_node, code, language)
        dependencies.extend(api_deps)
        
        # Detect file system operations
        fs_deps = self._detect_file_operations(ast_node, code, language)
        dependencies.extend(fs_deps)
        
        # Detect network operations
        network_deps = self._detect_network_operations(ast_node, code, language)
        dependencies.extend(network_deps)
        
        # Categorize dependencies by type
        self._categorize_dependencies(dependencies)
        
        return dependencies

    def _detect_imports(self, node: tree_sitter.Node, code: str, language: str) -> List[Dependency]:
        """Detect import statements using AST."""
        imports = []
        import_nodes = self.IMPORT_NODES.get(language, set())
        
        def traverse(n: tree_sitter.Node):
            if n.type in import_nodes:
                import_info = self._extract_import_info(n, code, language)
                if import_info:
                    imports.append(import_info)
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return imports

    def _extract_import_info(self, node: tree_sitter.Node, code: str, language: str) -> Optional[Dependency]:
        """Extract detailed import information from AST node."""
        node_text = code[node.start_byte:node.end_byte]
        
        if language == 'python':
            return self._extract_python_import(node, code, node_text)
        elif language in ('javascript', 'typescript'):
            return self._extract_js_import(node, code, node_text)
        elif language == 'java':
            return self._extract_java_import(node, code, node_text)
        
        return None

    def _extract_python_import(self, node: tree_sitter.Node, code: str, node_text: str) -> Optional[Dependency]:
        """Extract Python import information."""
        if node.type == 'import_statement':
            # Handle: import module
            for child in node.children:
                if child.type == 'dotted_name':
                    module_name = code[child.start_byte:child.end_byte]
                    return Dependency(name=module_name, type='import', source=node_text.strip())
        elif node.type == 'import_from_statement':
            # Handle: from module import item
            module_name = None
            for child in node.children:
                if child.type == 'dotted_name':
                    module_name = code[child.start_byte:child.end_byte]
                    break
            if module_name:
                return Dependency(name=module_name, type='import', source=node_text.strip())
        
        return None

    def _extract_js_import(self, node: tree_sitter.Node, code: str, node_text: str) -> Optional[Dependency]:
        """Extract JavaScript/TypeScript import information."""
        # Look for string literals in import statements
        for child in node.children:
            if child.type == 'string':
                module_name = code[child.start_byte:child.end_byte].strip('\'"')
                return Dependency(name=module_name, type='import', source=node_text.strip())
        
        return None

    def _extract_java_import(self, node: tree_sitter.Node, code: str, node_text: str) -> Optional[Dependency]:
        """Extract Java import information."""
        # Look for scoped identifier in import declaration
        for child in node.children:
            if child.type in ('scoped_identifier', 'identifier'):
                module_name = code[child.start_byte:child.end_byte]
                return Dependency(name=module_name, type='import', source=node_text.strip())
        
        return None

    def _detect_external_calls(self, node: tree_sitter.Node, code: str, language: str) -> List[Dependency]:
        """Detect calls to external APIs and services."""
        external_calls = []
        call_nodes = self.CALL_NODES.get(language, set())
        
        def traverse(n: tree_sitter.Node):
            if n.type in call_nodes:
                call_info = self._analyze_function_call(n, code, language)
                if call_info and self._is_external_call(call_info):
                    external_calls.append(Dependency(
                        name=call_info['name'],
                        type='external_call',
                        source=f"Line {n.start_point[0] + 1}: {call_info['full_call']}"
                    ))
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return external_calls

    def _analyze_function_call(self, node: tree_sitter.Node, code: str, language: str) -> Optional[Dict]:
        """Analyze a function call node to extract call information."""
        call_text = code[node.start_byte:node.end_byte]
        
        # Extract the function name being called
        function_name = None
        for child in node.children:
            if child.type == 'identifier':
                function_name = code[child.start_byte:child.end_byte]
                break
            elif child.type == 'attribute':  # Python: obj.method()
                function_name = code[child.start_byte:child.end_byte]
                break
            elif child.type == 'member_expression':  # JS: obj.method()
                function_name = code[child.start_byte:child.end_byte]
                break
        
        if function_name:
            return {
                'name': function_name,
                'full_call': call_text,
                'line': node.start_point[0] + 1
            }
        
        return None

    def _is_external_call(self, call_info: Dict) -> bool:
        """Determine if a function call is to an external service."""
        call_name = call_info['name'].lower()
        
        # Check against known external patterns
        for category, patterns in self.EXTERNAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, call_name, re.IGNORECASE):
                    return True
        
        # Check for common external call patterns
        external_indicators = [
            'http', 'url', 'api', 'request', 'fetch', 'get', 'post', 'put', 'delete',
            'connect', 'query', 'execute', 'select', 'insert', 'update',
            'redis', 'cache', 'session', 'auth', 'login', 'oauth'
        ]
        
        return any(indicator in call_name for indicator in external_indicators)

    def _detect_file_operations(self, node: tree_sitter.Node, code: str, language: str) -> List[Dependency]:
        """Detect file system operations."""
        file_ops = []
        
        # Language-specific file operation patterns
        file_patterns = {
            'python': ['open', 'file', 'os.path', 'pathlib', 'shutil', 'glob'],
            'javascript': ['fs.', 'path.', 'require(\'fs\')', 'require(\'path\')'],
            'typescript': ['fs.', 'path.', 'import.*fs', 'import.*path'],
            'java': ['File', 'Files', 'Path', 'FileInputStream', 'FileOutputStream']
        }
        
        patterns = file_patterns.get(language, [])
        call_nodes = self.CALL_NODES.get(language, set())
        
        def traverse(n: tree_sitter.Node):
            if n.type in call_nodes:
                call_text = code[n.start_byte:n.end_byte]
                for pattern in patterns:
                    if pattern in call_text:
                        file_ops.append(Dependency(
                            name=pattern,
                            type='file_operation',
                            source=f"Line {n.start_point[0] + 1}: {call_text[:50]}..."
                        ))
                        break
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return file_ops

    def _detect_network_operations(self, node: tree_sitter.Node, code: str, language: str) -> List[Dependency]:
        """Detect network operations and HTTP calls."""
        network_ops = []
        
        # Network operation patterns
        network_patterns = {
            'python': ['requests.', 'urllib.', 'httpx.', 'aiohttp.', 'socket.'],
            'javascript': ['fetch(', 'axios.', 'XMLHttpRequest', 'WebSocket'],
            'typescript': ['fetch(', 'axios.', 'XMLHttpRequest', 'WebSocket'],
            'java': ['HttpClient', 'URLConnection', 'Socket', 'ServerSocket']
        }
        
        patterns = network_patterns.get(language, [])
        call_nodes = self.CALL_NODES.get(language, set())
        
        def traverse(n: tree_sitter.Node):
            if n.type in call_nodes:
                call_text = code[n.start_byte:n.end_byte]
                for pattern in patterns:
                    if pattern in call_text:
                        network_ops.append(Dependency(
                            name=pattern,
                            type='network_operation',
                            source=f"Line {n.start_point[0] + 1}: {call_text[:50]}..."
                        ))
                        break
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return network_ops

    def _categorize_dependencies(self, dependencies: List[Dependency]) -> None:
        """Categorize dependencies by their likely purpose."""
        for dep in dependencies:
            dep_name = dep.name.lower()
            
            # Categorize based on patterns
            for category, patterns in self.EXTERNAL_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, dep_name, re.IGNORECASE):
                        # Update the type to be more specific
                        if dep.type == 'import':
                            dep.type = f'import_{category}'
                        elif dep.type == 'external_call':
                            dep.type = f'call_{category}'
                        break

    def analyze_dependency_complexity(self, dependencies: List[Dependency]) -> List[EdgeCase]:
        """Analyze dependencies for potential complexity and risk issues."""
        risks = []
        
        # Count dependencies by type
        dep_counts = {}
        for dep in dependencies:
            dep_type = dep.type
            dep_counts[dep_type] = dep_counts.get(dep_type, 0) + 1
        
        # Check for too many dependencies
        total_deps = len(dependencies)
        if total_deps > 20:
            risks.append(EdgeCase(
                type='high_dependency_count',
                location='Global',
                description=f'High number of dependencies ({total_deps}) may indicate tight coupling',
                severity=2
            ))
        
        # Check for database dependencies without proper error handling
        db_deps = [d for d in dependencies if 'database' in d.type]
        if db_deps:
            risks.append(EdgeCase(
                type='database_dependency',
                location='Multiple locations',
                description=f'Database dependencies detected ({len(db_deps)}) - ensure proper connection handling and error recovery',
                severity=3
            ))
        
        # Check for network dependencies
        network_deps = [d for d in dependencies if 'network' in d.type or 'http' in d.type]
        if network_deps:
            risks.append(EdgeCase(
                type='network_dependency',
                location='Multiple locations',
                description=f'Network dependencies detected ({len(network_deps)}) - ensure timeout handling and retry logic',
                severity=2
            ))
        
        # Check for circular import potential (simplified heuristic)
        import_deps = [d for d in dependencies if d.type.startswith('import')]
        local_imports = [d for d in import_deps if not self._is_standard_library(d.name)]
        if len(local_imports) > 10:
            risks.append(EdgeCase(
                type='potential_circular_imports',
                location='Multiple locations',
                description=f'Many local imports ({len(local_imports)}) may indicate potential circular dependency issues',
                severity=2
            ))
        
        return risks

    def _is_standard_library(self, module_name: str) -> bool:
        """Check if a module is part of the standard library (simplified)."""
        # This is a simplified check - a real implementation would be more comprehensive
        standard_libs = {
            'python': ['os', 'sys', 'json', 'datetime', 'collections', 'itertools', 'functools', 're', 'math', 'random'],
            'javascript': ['console', 'JSON', 'Math', 'Date', 'Array', 'Object', 'String', 'Number'],
            'java': ['java.lang', 'java.util', 'java.io', 'java.net', 'java.time']
        }
        
        for lang, libs in standard_libs.items():
            if any(module_name.startswith(lib) for lib in libs):
                return True
        
        return False
