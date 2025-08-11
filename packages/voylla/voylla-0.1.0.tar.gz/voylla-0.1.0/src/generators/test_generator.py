"""
Test Generator - Generates unit, integration, and edge test cases with AI integration
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.analyzers.code_analyzer import AnalysisResult, FunctionInfo
from src.interfaces.base_interfaces import TestType, TestCase, TestSuite, Language, IAIProvider, ITestGenerator
from src.config.ai_provider_manager import AIProviderManager
from .integration_test_generator import IntegrationTestGenerator

class TestGenerator(ITestGenerator):
    """Generates comprehensive test cases based on code analysis with AI integration."""
    
    def __init__(self, ai_provider_manager: Optional[AIProviderManager] = None):
        self.ai_provider_manager = ai_provider_manager or AIProviderManager()
        self.ai_provider = self.ai_provider_manager.get_provider()
        
        # Initialize specialized generators
        self.integration_test_generator = IntegrationTestGenerator()
        
        # Language-specific test frameworks
        self.test_frameworks = {
            'python': 'pytest',
            'javascript': 'jest',
            'typescript': 'jest',
            'java': 'junit'
        }
        
        self.test_templates = {
            'python': {
                'unit': self._python_unit_template,
                'edge': self._python_edge_template,
                'integration': self._python_integration_template
            },
            'javascript': {
                'unit': self._javascript_unit_template,
                'edge': self._javascript_edge_template,
                'integration': self._javascript_integration_template
            },
            'java': {
                'unit': self._java_unit_template,
                'edge': self._java_edge_template,
                'integration': self._java_integration_template
            }
        }
    
    def generate_tests(self, analysis: AnalysisResult) -> TestSuite:
        """Generate comprehensive test cases from analysis results with AI enhancement."""
        test_cases = []
        
        # Get AI analysis of the code patterns
        ai_analysis = self._get_ai_code_analysis(analysis)
        
        # Normalize function parameters: support analyzer FunctionInfo that exposes 'args'
        for function in analysis.functions:
            if not hasattr(function, 'parameters'):
                try:
                    arg_names = getattr(function, 'args', []) or []
                    function.parameters = [Parameter(name=n) for n in arg_names]
                except Exception:
                    function.parameters = []

        for function in analysis.functions:
            # Generate unit tests
            unit_tests = self._generate_unit_tests(function, analysis)
            test_cases.extend(self._enhance_tests_with_ai(unit_tests, analysis, ai_analysis))
            
            # Generate edge case tests
            edge_tests = self._generate_edge_tests(function, analysis)
            test_cases.extend(self._enhance_tests_with_ai(edge_tests, analysis, ai_analysis))
            
            # Generate integration tests if applicable
            if self._needs_integration_tests(function, analysis):
                integration_tests = self._generate_integration_tests(function, analysis)
                test_cases.extend(self._enhance_tests_with_ai(integration_tests, analysis, ai_analysis))
        
        # Create test suite
        language = Language(analysis.language.lower())
        framework = self.test_frameworks.get(analysis.language.lower(), 'unknown')
        
        return TestSuite(
            language=language,
            framework=framework,
            test_cases=test_cases,
            setup_code=self._generate_setup_code_for_language(analysis.language),
            teardown_code=self._generate_teardown_code_for_language(analysis.language)
        )
    
    def generate_unit_tests(self, functions: List[FunctionInfo]) -> List[TestCase]:
        """Generate unit tests for functions (interface implementation)."""
        test_cases = []
        for function in functions:
            # Create a minimal analysis result for compatibility
            analysis = type('AnalysisResult', (), {
                'language': 'python',  # Default language
                'functions': [function],
                'edge_cases': [],
                'imports': []
            })()
            test_cases.extend(self._generate_unit_tests(function, analysis))
        return test_cases
    
    def generate_integration_tests(self, dependencies: List) -> List[TestCase]:
        """Generate integration tests with mocking strategies (interface implementation)."""
        # Import the correct FunctionInfo from interfaces
        from ..interfaces.base_interfaces import FunctionInfo as InterfaceFunctionInfo, Parameter
        
        # Create a dummy function info for interface compatibility
        dummy_function = InterfaceFunctionInfo(
            name="integration_test_function",
            parameters=[],
            return_type="Any",
            complexity=1,
            line_range=(1, 10),
            docstring="Integration test function"
        )
        
        # Use the specialized integration test generator
        return self.integration_test_generator.generate_integration_tests(
            dummy_function, dependencies, "python"  # Default to Python for interface calls
        )
    
    def generate_edge_case_tests(self, edge_cases: List) -> List[TestCase]:
        """Generate edge case tests for boundary conditions (interface implementation)."""
        test_cases = []
        for edge_case in edge_cases:
            test_case = TestCase(
                name=f"test_edge_{edge_case.type if hasattr(edge_case, 'type') else 'case'}",
                test_type=TestType.EDGE,
                function_name="edge_test",
                description=f"Edge case test for {edge_case}",
                test_code=self._generate_basic_edge_test(str(edge_case)),
                requirements_covered=[]
            )
            test_cases.append(test_case)
        return test_cases
    
    def format_tests(self, tests: List[TestCase], language: Language) -> str:
        """Format tests according to language-specific frameworks (interface implementation)."""
        framework = self.test_frameworks.get(language.value, 'unknown')
        formatted_tests = []
        
        # Add framework-specific imports and setup
        if language == Language.PYTHON:
            formatted_tests.append("import pytest")
            formatted_tests.append("from unittest.mock import Mock, patch")
            formatted_tests.append("")
        elif language == Language.JAVASCRIPT:
            formatted_tests.append("const { describe, test, expect, jest } = require('@jest/globals');")
            formatted_tests.append("")
        elif language == Language.JAVA:
            formatted_tests.append("import org.junit.jupiter.api.Test;")
            formatted_tests.append("import org.junit.jupiter.api.BeforeEach;")
            formatted_tests.append("import org.junit.jupiter.api.AfterEach;")
            formatted_tests.append("import static org.junit.jupiter.api.Assertions.*;")
            formatted_tests.append("")
        
        # Add each test case
        for test in tests:
            formatted_tests.append(test.test_code)
            formatted_tests.append("")
        
        return "\n".join(formatted_tests)
    
    def _get_ai_code_analysis(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Get AI analysis of code patterns for enhanced test generation."""
        try:
            # Reconstruct code snippet from analysis for AI analysis
            code_snippet = self._reconstruct_code_from_analysis(analysis)
            ai_result = self.ai_provider.analyze_code_patterns(code_snippet, analysis.language)
            return ai_result
        except Exception as e:
            print(f"Warning: AI analysis failed: {e}")
            return {'analysis': 'AI analysis unavailable', 'provider': 'none'}
    
    def _enhance_tests_with_ai(self, test_cases: List[TestCase], analysis: AnalysisResult, 
                              ai_analysis: Dict[str, Any]) -> List[TestCase]:
        """Enhance test cases using AI provider."""
        enhanced_tests = []
        
        for test in test_cases:
            try:
                # Create context for AI enhancement
                context = {
                    'language': analysis.language,
                    'edge_cases': [str(ec) for ec in analysis.edge_cases],
                    'performance_risks': self._identify_performance_risks(analysis),
                    'ai_insights': ai_analysis.get('analysis', '')
                }
                
                # Get AI enhancement
                enhancement = self.ai_provider.enhance_test_case(test, context)
                
                if enhancement:
                    # Apply AI enhancements
                    enhanced_test = TestCase(
                        name=test.name,
                        test_type=test.test_type,
                        function_name=test.function_name,
                        description=enhancement.get('description', test.description),
                        test_code=enhancement.get('code', test.test_code),
                        setup_code=test.setup_code,
                        teardown_code=test.teardown_code,
                        assertions=enhancement.get('assertions', test.assertions),
                        requirements_covered=test.requirements_covered
                    )
                    enhanced_tests.append(enhanced_test)
                else:
                    enhanced_tests.append(test)
                    
            except Exception as e:
                print(f"Warning: AI enhancement failed for {test.name}: {e}")
                enhanced_tests.append(test)
        
        return enhanced_tests
    
    def _reconstruct_code_from_analysis(self, analysis: AnalysisResult) -> str:
        """Reconstruct a code snippet from analysis results for AI processing."""
        code_lines = []
        
        # Add imports
        if hasattr(analysis, 'imports') and analysis.imports:
            for imp in analysis.imports[:5]:  # Limit to first 5 imports
                code_lines.append(imp)
            code_lines.append("")
        
        # Add function signatures
        for func in analysis.functions[:3]:  # Limit to first 3 functions
            names = self._get_param_names(func)
            if names:
                params_str = ", ".join(names)
                code_lines.append(f"def {func.name}({params_str}):")
            else:
                code_lines.append(f"def {func.name}():")
            
            if hasattr(func, 'docstring') and func.docstring:
                code_lines.append(f'    """{func.docstring}"""')
            
            code_lines.append("    # Function implementation")
            code_lines.append("")
        
        return "\n".join(code_lines)

    def _get_param_names(self, function: FunctionInfo) -> list:
        """Return a list of parameter names for a function from either .parameters or .args."""
        params = getattr(function, 'parameters', None)
        if params is not None:
            try:
                return [p.name for p in params if hasattr(p, 'name')]
            except Exception:
                return []
        args = getattr(function, 'args', None)
        if isinstance(args, list):
            return [str(a) for a in args]
        return []
    
    def _identify_performance_risks(self, analysis: AnalysisResult) -> List[str]:
        """Identify performance risks from analysis."""
        risks = []
        
        for func in analysis.functions:
            if hasattr(func, 'complexity') and func.complexity > 10:
                risks.append(f"High complexity in {func.name}")
            
            # Check for potential performance issues in function names
            if any(keyword in func.name.lower() for keyword in ['loop', 'recursive', 'sort', 'search']):
                risks.append(f"Potential performance concern in {func.name}")
        
        return risks
    
    def _generate_setup_code_for_language(self, language: str) -> Optional[str]:
        """Generate language-specific setup code."""
        if language.lower() == 'python':
            return """# Test setup
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))"""
        elif language.lower() in ['javascript', 'typescript']:
            return """// Test setup
beforeEach(() => {
    // Setup code here
});"""
        elif language.lower() == 'java':
            return """@BeforeEach
void setUp() {
    // Setup code here
}"""
        return None
    
    def _generate_teardown_code_for_language(self, language: str) -> Optional[str]:
        """Generate language-specific teardown code."""
        if language.lower() == 'python':
            return """# Test teardown
# Cleanup code here"""
        elif language.lower() in ['javascript', 'typescript']:
            return """afterEach(() => {
    // Cleanup code here
});"""
        elif language.lower() == 'java':
            return """@AfterEach
void tearDown() {
    // Cleanup code here
}"""
        return None
    
    def _generate_basic_integration_test(self, dependency: str) -> str:
        """Generate a basic integration test template."""
        return f"""def test_integration_{dependency.lower().replace(' ', '_')}():
    \"\"\"Integration test for {dependency}.\"\"\"
    # Arrange
    # Set up integration test environment
    
    # Act
    # Call method that integrates with {dependency}
    
    # Assert
    # Verify integration behavior
    assert True  # Replace with actual assertions"""
    
    def _generate_basic_edge_test(self, edge_case: str) -> str:
        """Generate a basic edge case test template."""
        return f"""def test_edge_{edge_case.lower().replace(' ', '_')}():
    \"\"\"Edge case test for {edge_case}.\"\"\"
    # Arrange
    # Set up edge case scenario
    
    # Act & Assert
    # Test edge case behavior
    assert True  # Replace with actual assertions"""
    
    def _generate_unit_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> List[TestCase]:
        """Generate unit tests for a function."""
        tests = []
        template_func = self.test_templates[analysis.language]['unit']
        
        # Basic functionality test
        test_code = template_func(function, 'basic', self._generate_basic_inputs(function))
        tests.append(TestCase(
            name=f"test_{function.name}_basic",
            test_type=TestType.UNIT,
            function_name=function.name,
            description=f"Test basic functionality of {function.name}",
            test_code=test_code
        ))
        
        # Test with different input types if function has parameters
        names = self._get_param_names(function)
        if names:
            for i, pname in enumerate(names):
                test_code = template_func(function, f'param_{i}', self._generate_param_variations(function, i))
                tests.append(TestCase(
                    name=f"test_{function.name}_param_{pname}",
                    test_type=TestType.UNIT,
                    function_name=function.name,
                    description=f"Test {function.name} with different {pname} values",
                    test_code=test_code
                ))
        
        return tests
    
    def _generate_edge_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> List[TestCase]:
        """Generate edge case tests."""
        tests = []
        template_func = self.test_templates[analysis.language]['edge']
        
        edge_scenarios = self._identify_edge_scenarios(function, analysis)
        
        for scenario in edge_scenarios:
            test_code = template_func(function, scenario['type'], scenario['inputs'])
            tests.append(TestCase(
                name=f"test_{function.name}_edge_{scenario['type']}",
                test_type=TestType.EDGE,
                function_name=function.name,
                description=f"Test {function.name} edge case: {scenario['description']}",
                test_code=test_code
            ))
        
        return tests
    
    def _generate_integration_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> List[TestCase]:
        """Generate integration tests using the specialized IntegrationTestGenerator."""
        # Extract dependencies from analysis
        dependencies = getattr(analysis, 'dependencies', [])
        edge_cases = getattr(analysis, 'edge_cases', [])
        
        # Use the specialized integration test generator
        # Adapt analyzer FunctionInfo to interface FunctionInfo expected by the integration generator
        try:
            from ..interfaces.base_interfaces import FunctionInfo as IFFunctionInfo, Parameter as IFParameter
            param_names = self._get_param_names(function)
            iface_func = IFFunctionInfo(
                name=function.name,
                parameters=[IFParameter(name=n) for n in param_names],
                return_type=getattr(function, 'return_type', None),
                complexity=getattr(function, 'complexity', 1),
                line_range=(getattr(function, 'line_start', 1), getattr(function, 'line_end', 1)),
                docstring=getattr(function, 'docstring', None)
            )
            integration_tests = self.integration_test_generator.generate_integration_tests(
                iface_func, dependencies, analysis.language, edge_cases
            )
        except Exception:
            integration_tests = []
        
        return integration_tests
    
    def _needs_integration_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> bool:
        """Determine if function needs integration tests."""
        # Check for external dependencies
        external_indicators = ['requests', 'urllib', 'database', 'api', 'file', 'open']
        
        if function.docstring:
            return any(indicator in function.docstring.lower() for indicator in external_indicators)
        
        # Check imports for external libraries
        return any(indicator in ' '.join(analysis.imports).lower() for indicator in external_indicators)
    
    def _identify_edge_scenarios(self, function: FunctionInfo, analysis: AnalysisResult) -> List[Dict[str, Any]]:
        """Identify context-aware edge case scenarios for a function."""
        scenarios = []
        context = self._analyze_function_context(function)
        
        # Context-aware edge cases based on function domain
        names = self._get_param_names(function)
        if names:
            # Always include null input test
            scenarios.append({
                'type': 'null_input',
                'description': f'null/None input values in {context["domain"]} context',
                'inputs': {name: None for name in names}
            })
            
            # Domain-specific empty input scenarios
            empty_inputs = {}
            for pname in names:
                empty_inputs[pname] = self._get_context_aware_empty_value(pname, context, analysis.language)
            
            scenarios.append({
                'type': 'empty_input',
                'description': f'empty input values in {context["domain"]} context',
                'inputs': empty_inputs
            })
        
        # Domain-specific edge cases
        if context['domain'] == 'mathematical':
            scenarios.extend([
                {
                    'type': 'negative_numbers',
                    'description': 'negative number inputs',
                    'inputs': {pname: -1 for pname in names if 'num' in pname.lower()}
                },
                {
                    'type': 'zero_values',
                    'description': 'zero value inputs',
                    'inputs': {pname: 0 for pname in names if 'num' in pname.lower()}
                }
            ])
            
        elif context['domain'] == 'text_processing':
            scenarios.extend([
                {
                    'type': 'special_characters',
                    'description': 'special characters and unicode',
                    'inputs': {pname: "!@#$%^&*()_+{}|:<>?[]\\;'\",./" if 'str' in pname.lower() or 'text' in pname.lower() else pname 
                              for pname in names}
                },
                {
                    'type': 'very_long_string',
                    'description': 'extremely long string input',
                    'inputs': {pname: "x" * 10000 if 'str' in pname.lower() or 'text' in pname.lower() else pname 
                              for pname in names}
                }
            ])
            
        elif context['domain'] == 'data_structures':
            scenarios.extend([
                {
                    'type': 'single_element',
                    'description': 'single element collection',
                    'inputs': {pname: [1] if 'list' in pname.lower() or 'arr' in pname.lower() else pname 
                              for pname in names}
                },
                {
                    'type': 'large_collection',
                    'description': 'very large collection',
                    'inputs': {pname: list(range(10000)) if 'list' in pname.lower() or 'arr' in pname.lower() else pname 
                              for pname in names}
                }
            ])
        
        # Add scenarios based on detected edge cases from analysis
        for edge_case in analysis.edge_cases:
            desc = getattr(edge_case, 'description', None)
            edge_case_str = str(desc if desc is not None else edge_case).lower()
            if 'division' in edge_case_str:
                scenarios.append({
                    'type': 'division_by_zero',
                    'description': 'division by zero scenario',
                    'inputs': self._generate_division_zero_inputs(function)
                })
            elif 'index' in edge_case_str:
                scenarios.append({
                    'type': 'index_error',
                    'description': 'index out of bounds scenario',
                    'inputs': self._generate_index_error_inputs(function)
                })
            elif 'file' in edge_case_str:
                scenarios.append({
                    'type': 'file_not_found',
                    'description': 'file not found scenario',
                    'inputs': {pname: 'nonexistent_file.txt' if 'file' in pname.lower() or 'path' in pname.lower() else pname 
                              for pname in names}
                })
        
        return scenarios
    
    def _generate_basic_inputs(self, function: FunctionInfo) -> Dict[str, Any]:
        """Generate context-aware basic test inputs for a function."""
        inputs = {}
        
        # Analyze function context for smarter input generation
        function_context = self._analyze_function_context(function)
        
        for pname in self._get_param_names(function):
            inputs[pname] = self._get_context_aware_value(pname, function_context)
        return inputs
    
    def _generate_param_variations(self, function: FunctionInfo, param_index: int) -> Dict[str, Any]:
        """Generate parameter variations for testing."""
        inputs = self._generate_basic_inputs(function)
        names = self._get_param_names(function)
        if not names or param_index >= len(names):
            return inputs
        param_name = names[param_index]
        
        # Generate different values based on parameter name
        if 'num' in param_name.lower() or 'count' in param_name.lower():
            inputs[param_name] = [0, 1, -1, 100, -100]
        elif 'str' in param_name.lower() or 'text' in param_name.lower():
            inputs[param_name] = ['', 'test', 'a' * 1000]
        elif 'list' in param_name.lower() or 'arr' in param_name.lower():
            inputs[param_name] = [[], [1], [1, 2, 3]]
        
        return inputs
    
    def _analyze_function_context(self, function: FunctionInfo) -> Dict[str, Any]:
        """Analyze function context to understand its purpose and expected inputs."""
        context = {
            'domain': 'general',
            'data_type': 'mixed',
            'expected_operations': [],
            'validation_needs': []
        }
        
        # Analyze function name for domain context
        name_lower = function.name.lower()
        
        # Mathematical functions
        if any(word in name_lower for word in ['calculate', 'compute', 'math', 'sum', 'average', 'max', 'min']):
            context['domain'] = 'mathematical'
            context['data_type'] = 'numeric'
            context['expected_operations'] = ['arithmetic', 'comparison']
            
        # String processing functions
        elif any(word in name_lower for word in ['parse', 'format', 'clean', 'validate', 'process']):
            context['domain'] = 'text_processing'
            context['data_type'] = 'string'
            context['expected_operations'] = ['string_manipulation', 'validation']
            
        # Data structure functions
        elif any(word in name_lower for word in ['find', 'search', 'filter', 'sort', 'merge']):
            context['domain'] = 'data_structures'
            context['data_type'] = 'collection'
            context['expected_operations'] = ['iteration', 'comparison', 'filtering']
            
        # File/IO functions
        elif any(word in name_lower for word in ['read', 'write', 'save', 'load', 'file']):
            context['domain'] = 'file_io'
            context['data_type'] = 'string'
            context['expected_operations'] = ['file_operations']
            context['validation_needs'] = ['file_exists', 'permissions']
            
        # API/Network functions
        elif any(word in name_lower for word in ['fetch', 'request', 'api', 'http', 'get', 'post']):
            context['domain'] = 'network'
            context['data_type'] = 'mixed'
            context['expected_operations'] = ['http_requests']
            context['validation_needs'] = ['connectivity', 'response_format']
        
        # Analyze docstring for additional context
        if function.docstring:
            docstring_lower = function.docstring.lower()
            
            # Look for validation requirements
            if 'raises' in docstring_lower:
                context['validation_needs'].extend(['exception_handling'])
            if 'empty' in docstring_lower:
                context['validation_needs'].extend(['empty_input'])
            if 'none' in docstring_lower or 'null' in docstring_lower:
                context['validation_needs'].extend(['null_input'])
                
        return context
    
    def _get_context_aware_value(self, param_name: str, context: Dict[str, Any]) -> Any:
        """Get context-aware test value based on parameter name and function context."""
        param_lower = param_name.lower()
        
        # Use context to generate more appropriate values
        if context['domain'] == 'mathematical':
            if any(word in param_lower for word in ['num', 'value', 'x', 'y', 'a', 'b']):
                return 10.5 if 'float' in param_lower else 42
            elif any(word in param_lower for word in ['list', 'numbers', 'data', 'values']):
                return [1.5, 2.7, 3.14, 4.0, 5.2]
                
        elif context['domain'] == 'text_processing':
            if any(word in param_lower for word in ['text', 'string', 'input', 'data']):
                return "Hello, World! This is a test string with 123 numbers."
            elif 'pattern' in param_lower:
                return r'\d+'
            elif 'delimiter' in param_lower:
                return ','
                
        elif context['domain'] == 'data_structures':
            if any(word in param_lower for word in ['list', 'array', 'data', 'items']):
                return [1, 2, 3, 4, 5]
            elif 'key' in param_lower:
                return 'test_key'
            elif 'index' in param_lower:
                return 2
                
        elif context['domain'] == 'file_io':
            if any(word in param_lower for word in ['path', 'filename', 'file']):
                return 'test_file.txt'
            elif 'content' in param_lower:
                return "Test file content\nLine 2\nLine 3"
            elif 'mode' in param_lower:
                return 'r'
                
        elif context['domain'] == 'network':
            if 'url' in param_lower:
                return 'https://api.example.com/test'
            elif any(word in param_lower for word in ['headers', 'header']):
                return {'Content-Type': 'application/json'}
            elif 'timeout' in param_lower:
                return 30
        
        # Fallback to parameter name analysis
        return self._get_default_value(param_name)
    
    def _get_default_value(self, param_name: str) -> Any:
        """Get default test value based on parameter name (fallback method)."""
        param_lower = param_name.lower()
        
        if any(word in param_lower for word in ['num', 'count', 'size', 'length', 'index']):
            return 5
        elif any(word in param_lower for word in ['str', 'text', 'name', 'message']):
            return 'test_string'
        elif any(word in param_lower for word in ['list', 'arr', 'items', 'data']):
            return [1, 2, 3]
        elif any(word in param_lower for word in ['bool', 'flag', 'enabled']):
            return True
        elif any(word in param_lower for word in ['dict', 'map', 'config']):
            return {'key': 'value'}
        else:
            return 'test_value'
    
    def _get_empty_value(self, language: str) -> Any:
        """Get empty value for the language."""
        if language == 'python':
            return ''
        elif language in ['javascript', 'typescript']:
            return 'null'
        elif language == 'java':
            return 'null'
        return ''
    
    def _generate_division_zero_inputs(self, function: FunctionInfo) -> Dict[str, Any]:
        """Generate inputs that might cause division by zero."""
        inputs = self._generate_basic_inputs(function)
        # Look for parameters that might be divisors
        for pname in self._get_param_names(function):
            if 'divisor' in pname.lower() or 'denom' in pname.lower() or 'denominator' in pname.lower():
                inputs[pname] = 0
        return inputs
    
    def _generate_index_error_inputs(self, function: FunctionInfo) -> Dict[str, Any]:
        """Generate inputs that might cause index errors."""
        inputs = self._generate_basic_inputs(function)
        for pname in self._get_param_names(function):
            if 'index' in pname.lower() or 'idx' in pname.lower():
                inputs[pname] = -1  # Negative index
        return inputs
    
    # Template functions for different languages
    def _python_unit_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate context-aware Python unit test template."""
        context = self._analyze_function_context(function)
        
        test_code = f"""def test_{function.name}_{test_type}():
    \"\"\"Test {function.name} - {self._generate_test_description(function, test_type, context)}.\"\"\"
    # Arrange
"""
        
        # Generate more realistic variable assignments
        for arg, value in inputs.items():
            if isinstance(value, str) and not value.startswith('test_'):
                test_code += f"    {arg} = '{value}'\n"
            elif isinstance(value, list):
                test_code += f"    {arg} = {value}\n"
            elif isinstance(value, dict):
                test_code += f"    {arg} = {value}\n"
            else:
                test_code += f"    {arg} = {value}\n"
        
        # Add context-aware setup if needed
        setup_code = self._generate_setup_code(function, context)
        if setup_code:
            test_code += f"\n    # Setup\n{setup_code}\n"
        
        test_code += f"""    
    # Act
    result = {function.name}({', '.join(inputs.keys())})
    
    # Assert
{self._generate_context_aware_assertions(function, context, test_type)}
"""
        return test_code
    
    def _python_edge_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate context-aware Python edge case test template."""
        context = self._analyze_function_context(function)
        
        test_code = f"""def test_{function.name}_edge_{test_type}():
    \"\"\"Test {function.name} edge case: {self._get_edge_case_description(test_type, context)}.\"\"\"
    
    # Arrange
"""
        
        for arg, value in inputs.items():
            if value is None:
                test_code += f"    {arg} = None\n"
            elif isinstance(value, str):
                test_code += f"    {arg} = '{value}'\n"
            else:
                test_code += f"    {arg} = {value}\n"
        
        # Generate context-aware edge case handling
        if test_type == 'division_by_zero':
            test_code += f"""    
    # Act & Assert
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero|division by zero"):
        {function.name}({', '.join(inputs.keys())})
"""
        elif test_type == 'null_input':
            expected_exception = self._get_expected_exception_for_null(context)
            test_code += f"""    
    # Act & Assert
    with pytest.raises({expected_exception}):
        {function.name}({', '.join(inputs.keys())})
"""
        elif test_type == 'empty_input':
            if context['domain'] == 'mathematical':
                test_code += f"""    
    # Act & Assert
    with pytest.raises(ValueError, match="empty|cannot.*empty"):
        {function.name}({', '.join(inputs.keys())})
"""
            else:
                test_code += f"""    
    # Act
    result = {function.name}({', '.join(inputs.keys())})
    
    # Assert
    {self._generate_empty_input_assertions(context)}
"""
        elif test_type == 'index_error':
            test_code += f"""    
    # Act & Assert
    with pytest.raises(IndexError, match="index out of range|list index"):
        {function.name}({', '.join(inputs.keys())})
"""
        else:
            test_code += f"""    
    # Act
    result = {function.name}({', '.join(inputs.keys())})
    
    # Assert
    {self._generate_context_aware_assertions(function, context, f"edge_{test_type}")}
"""
        
        return test_code
    
    def _python_integration_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Python integration test template."""
        return f"""def test_{function.name}_integration():
    # Integration test for {function.name}
    # This test should verify the function works with real external dependencies
    
    # Arrange
    # Set up test environment, mock external services if needed
    
    # Act
    result = {function.name}()  # Call with appropriate parameters
    
    # Assert
    assert result is not None
    # Add assertions to verify integration behavior
"""
    
    def _javascript_unit_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate JavaScript unit test template."""
        test_code = f"""describe('{function.name}', () => {{
    test('should handle {test_type} case', () => {{
        // Arrange
"""
        
        for arg, value in inputs.items():
            if isinstance(value, str):
                test_code += f"        const {arg} = '{value}';\n"
            else:
                test_code += f"        const {arg} = {str(value).lower()};\n"
        
        test_code += f"""        
        // Act
        const result = {function.name}({', '.join(inputs.keys())});
        
        // Assert
        expect(result).toBeDefined();
        // Add specific assertions
    }});
}});
"""
        return test_code
    
    def _javascript_edge_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate JavaScript edge case test template."""
        return f"""describe('{function.name} edge cases', () => {{
    test('should handle {test_type}', () => {{
        // Arrange
        // Set up edge case inputs
        
        // Act & Assert
        expect(() => {{
            {function.name}(/* edge case parameters */);
        }}).toThrow(); // or not.toThrow() based on expected behavior
    }});
}});
"""
    
    def _javascript_integration_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate JavaScript integration test template."""
        return f"""describe('{function.name} integration', () => {{
    test('should integrate with external systems', async () => {{
        // Arrange
        // Set up integration test environment
        
        // Act
        const result = await {function.name}();
        
        // Assert
        expect(result).toBeDefined();
        // Add integration-specific assertions
    }});
}});
"""
    
    def _java_unit_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Java unit test template."""
        return f"""@Test
public void test{function.name.capitalize()}{test_type.capitalize()}() {{
    // Arrange
    // Set up test data
    
    // Act
    // Call the method under test
    
    // Assert
    assertNotNull(result);
    // Add specific assertions
}}
"""
    
    def _java_edge_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Java edge case test template."""
        return f"""@Test(expected = Exception.class)
public void test{function.name.capitalize()}Edge{test_type.capitalize()}() {{
    // Arrange
    // Set up edge case scenario
    
    // Act
    // This should throw an exception
    // Call method with edge case parameters
}}
"""
    
    def _java_integration_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Java integration test template."""
        return f"""@Test
public void test{function.name.capitalize()}Integration() {{
    // Arrange
    // Set up integration test environment
    
    // Act
    // Call method that integrates with external systems
    
    // Assert
    assertNotNull(result);
    // Add integration-specific assertions
}}
"""
    
    def _generate_test_description(self, function: FunctionInfo, test_type: str, context: Dict[str, Any]) -> str:
        """Generate a descriptive test description based on context."""
        if context['domain'] == 'mathematical':
            if test_type == 'basic':
                return f"basic mathematical operation with valid numeric inputs"
            elif 'param' in test_type:
                return f"mathematical operation with various numeric parameter values"
        elif context['domain'] == 'text_processing':
            if test_type == 'basic':
                return f"text processing with standard string input"
            elif 'param' in test_type:
                return f"text processing with different string formats and lengths"
        elif context['domain'] == 'data_structures':
            if test_type == 'basic':
                return f"data structure operation with typical collection"
            elif 'param' in test_type:
                return f"data structure operation with various collection sizes"
        elif context['domain'] == 'file_io':
            if test_type == 'basic':
                return f"file operation with valid file path and content"
        elif context['domain'] == 'network':
            if test_type == 'basic':
                return f"network operation with valid URL and parameters"
        
        return f"{test_type} functionality test"
    
    def _generate_setup_code(self, function: FunctionInfo, context: Dict[str, Any]) -> str:
        """Generate context-aware setup code."""
        setup_lines = []
        
        if context['domain'] == 'file_io':
            setup_lines.append("    # Create test file if needed")
            setup_lines.append("    import tempfile")
            setup_lines.append("    import os")
            
        elif context['domain'] == 'network':
            setup_lines.append("    # Mock network dependencies")
            setup_lines.append("    from unittest.mock import patch, Mock")
            
        elif context['domain'] == 'mathematical' and context.get('validation_needs'):
            setup_lines.append("    # Prepare mathematical test data")
            
        return '\n'.join(setup_lines) if setup_lines else ""
    
    def _generate_context_aware_assertions(self, function: FunctionInfo, context: Dict[str, Any], test_type: str) -> str:
        """Generate context-aware assertions based on function domain."""
        assertions = []
        
        if context['domain'] == 'mathematical':
            assertions.extend([
                "    assert result is not None",
                "    assert isinstance(result, (int, float))",
                "    # Verify mathematical correctness"
            ])
            if 'average' in function.name.lower():
                assertions.append("    # For average: result should be within expected range")
            elif 'max' in function.name.lower() or 'min' in function.name.lower():
                assertions.append("    # For min/max: result should be from input collection")
                
        elif context['domain'] == 'text_processing':
            assertions.extend([
                "    assert result is not None",
                "    assert isinstance(result, str)",
                "    # Verify text processing correctness"
            ])
            if 'clean' in function.name.lower() or 'format' in function.name.lower():
                assertions.append("    # Verify string formatting/cleaning applied correctly")
                
        elif context['domain'] == 'data_structures':
            assertions.extend([
                "    assert result is not None",
                "    # Verify data structure operation correctness"
            ])
            if 'find' in function.name.lower():
                assertions.append("    # For find operations: verify found item or None")
            elif 'sort' in function.name.lower():
                assertions.append("    # For sort operations: verify ordering")
                
        elif context['domain'] == 'file_io':
            assertions.extend([
                "    # Verify file operation completed successfully",
                "    # Check file exists/content as expected"
            ])
            
        elif context['domain'] == 'network':
            assertions.extend([
                "    assert result is not None",
                "    # Verify network response structure",
                "    # Check status codes, response format"
            ])
            
        else:
            # Generic assertions
            assertions.extend([
                "    assert result is not None",
                "    # Add specific assertions based on expected behavior"
            ])
        
        return '\n'.join(assertions)
    
    def _get_edge_case_description(self, test_type: str, context: Dict[str, Any]) -> str:
        """Get descriptive text for edge case based on context."""
        descriptions = {
            'null_input': f"handling None/null input values in {context['domain']} context",
            'empty_input': f"handling empty input values in {context['domain']} context", 
            'division_by_zero': "preventing division by zero errors",
            'index_error': "handling out-of-bounds index access",
            'invalid_type': f"handling invalid data types in {context['domain']} context"
        }
        return descriptions.get(test_type, f"edge case scenario: {test_type}")
    
    def _get_expected_exception_for_null(self, context: Dict[str, Any]) -> str:
        """Get expected exception type for null input based on context."""
        if context['domain'] == 'mathematical':
            return "TypeError"
        elif context['domain'] == 'text_processing':
            return "(TypeError, AttributeError)"
        elif context['domain'] == 'data_structures':
            return "(TypeError, AttributeError)"
        elif context['domain'] == 'file_io':
            return "(TypeError, FileNotFoundError)"
        else:
            return "(TypeError, ValueError)"
    
    def _generate_empty_input_assertions(self, context: Dict[str, Any]) -> str:
        """Generate assertions for empty input scenarios."""
        if context['domain'] == 'text_processing':
            return """    # For empty string input
    assert result == "" or result is None  # Depending on expected behavior"""
        elif context['domain'] == 'data_structures':
            return """    # For empty collection input
    assert result == [] or result is None  # Depending on expected behavior"""
        else:
            return """    # For empty input
    assert result is not None or result is None  # Adjust based on expected behavior"""
    
    def _get_context_aware_empty_value(self, param_name: str, context: Dict[str, Any], language: str) -> Any:
        """Get context-aware empty value for a parameter."""
        param_lower = param_name.lower()
        
        if context['domain'] == 'mathematical':
            if any(word in param_lower for word in ['list', 'numbers', 'data', 'values']):
                return []
            elif any(word in param_lower for word in ['num', 'value', 'count']):
                return 0
                
        elif context['domain'] == 'text_processing':
            if any(word in param_lower for word in ['text', 'string', 'input', 'data']):
                return ""
            elif 'pattern' in param_lower:
                return ""
                
        elif context['domain'] == 'data_structures':
            if any(word in param_lower for word in ['list', 'array', 'data', 'items']):
                return []
            elif any(word in param_lower for word in ['dict', 'map']):
                return {}
                
        elif context['domain'] == 'file_io':
            if any(word in param_lower for word in ['path', 'filename', 'file']):
                return ""
            elif 'content' in param_lower:
                return ""
        
        # Fallback to language-specific empty values
        return self._get_empty_value(language)