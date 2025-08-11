"""
Unit Test Generator - Specialized generator for individual function testing
"""
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging

from ..interfaces.base_interfaces import (
    FunctionInfo, Parameter, TestCase, TestType, Language
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TestDataGenerator:
    """Generates test data for different data types and contexts."""
    
    @staticmethod
    def generate_for_type(param_name: str, type_hint: Optional[str], language: str, context: str = "basic") -> List[Any]:
        """Generate test values for a parameter based on its type and context."""
        param_lower = param_name.lower()
        type_lower = type_hint.lower() if type_hint else ""
        
        # Type-based generation
        if type_hint:
            if type_lower in ['int', 'integer', 'number']:
                return TestDataGenerator._generate_integer_values(context)
            elif type_lower in ['float', 'double', 'decimal']:
                return TestDataGenerator._generate_float_values(context)
            elif type_lower in ['str', 'string', 'text']:
                return TestDataGenerator._generate_string_values(context)
            elif type_lower in ['bool', 'boolean']:
                return [True, False]
            elif type_lower in ['list', 'array', 'collection']:
                return TestDataGenerator._generate_list_values(context)
            elif type_lower in ['dict', 'map', 'object']:
                return TestDataGenerator._generate_dict_values(context)
        
        # Name-based inference
        if any(word in param_lower for word in ['num', 'count', 'size', 'length', 'index', 'id']):
            return TestDataGenerator._generate_integer_values(context)
        elif any(word in param_lower for word in ['rate', 'ratio', 'percent', 'score', 'value']):
            return TestDataGenerator._generate_float_values(context)
        elif any(word in param_lower for word in ['name', 'text', 'message', 'title', 'description']):
            return TestDataGenerator._generate_string_values(context)
        elif any(word in param_lower for word in ['flag', 'enabled', 'active', 'valid']):
            return [True, False]
        elif any(word in param_lower for word in ['list', 'items', 'data', 'collection']):
            return TestDataGenerator._generate_list_values(context)
        elif any(word in param_lower for word in ['config', 'options', 'settings', 'params']):
            return TestDataGenerator._generate_dict_values(context)
        
        # Default mixed values
        return TestDataGenerator._generate_mixed_values(context)
    
    @staticmethod
    def _generate_integer_values(context: str) -> List[int]:
        """Generate integer test values based on context."""
        base_values = [0, 1, -1, 10, 100]
        
        if context == "edge":
            return [0, -1, 1, -2147483648, 2147483647]  # Include min/max int values
        elif context == "boundary":
            return [-1, 0, 1, 99, 100, 101]
        elif context == "performance":
            return [0, 1, 1000, 10000, 100000]
        else:
            return base_values
    
    @staticmethod
    def _generate_float_values(context: str) -> List[float]:
        """Generate float test values based on context."""
        base_values = [0.0, 1.0, -1.0, 3.14, 10.5]
        
        if context == "edge":
            return [0.0, -0.0, float('inf'), float('-inf'), float('nan')]
        elif context == "boundary":
            return [-1.0, 0.0, 1.0, 0.999, 1.001]
        elif context == "performance":
            return [0.0, 1.0, 1000.0, 1e6, 1e-6]
        else:
            return base_values
    
    @staticmethod
    def _generate_string_values(context: str) -> List[str]:
        """Generate string test values based on context."""
        base_values = ["", "test", "hello world", "Test123"]
        
        if context == "edge":
            return ["", " ", "\n", "\t", "🚀", "a" * 1000, "null", "undefined"]
        elif context == "boundary":
            return ["", "a", "ab", "a" * 255, "a" * 256]
        elif context == "special":
            return ["", "null", "None", "<script>", "'; DROP TABLE;", "../../etc/passwd"]
        else:
            return base_values
    
    @staticmethod
    def _generate_list_values(context: str) -> List[List]:
        """Generate list test values based on context."""
        base_values = [[], [1], [1, 2, 3], ["a", "b", "c"]]
        
        if context == "edge":
            return [[], [None], [1], list(range(1000))]
        elif context == "boundary":
            return [[], [1], [1, 2], list(range(100))]
        else:
            return base_values
    
    @staticmethod
    def _generate_dict_values(context: str) -> List[Dict]:
        """Generate dictionary test values based on context."""
        base_values = [{}, {"key": "value"}, {"a": 1, "b": 2}]
        
        if context == "edge":
            return [{}, {"": ""}, {"null": None}, {str(i): i for i in range(100)}]
        elif context == "boundary":
            return [{}, {"key": "value"}, {"a": 1, "b": 2, "c": 3}]
        else:
            return base_values
    
    @staticmethod
    def _generate_mixed_values(context: str) -> List[Any]:
        """Generate mixed type test values."""
        base_values = [None, 0, "", [], {}]
        
        if context == "edge":
            return [None, 0, "", [], {}, float('nan'), float('inf')]
        else:
            return base_values


class AssertionGenerator:
    """Generates appropriate assertions for test cases."""
    
    @staticmethod
    def generate_assertions(function_info: FunctionInfo, test_inputs: Dict[str, Any], 
                          expected_behavior: str, language: str) -> List[str]:
        """Generate assertions based on function info and expected behavior."""
        assertions = []
        func_name = function_info.name
        
        # Generate function call
        if language == "python":
            call_args = ", ".join([f"{k}={repr(v)}" for k, v in test_inputs.items()])
            function_call = f"{func_name}({call_args})"
        elif language in ["javascript", "typescript"]:
            call_args = ", ".join([AssertionGenerator._js_repr(v) for v in test_inputs.values()])
            function_call = f"{func_name}({call_args})"
        elif language == "java":
            call_args = ", ".join([AssertionGenerator._java_repr(v) for v in test_inputs.values()])
            function_call = f"{func_name}({call_args})"
        else:
            call_args = ", ".join([repr(v) for v in test_inputs.values()])
            function_call = f"{func_name}({call_args})"
        
        # Generate assertions based on expected behavior
        if expected_behavior == "returns_value":
            assertions.extend(AssertionGenerator._generate_return_value_assertions(
                function_call, function_info, language))
        elif expected_behavior == "throws_exception":
            assertions.extend(AssertionGenerator._generate_exception_assertions(
                function_call, function_info, language))
        elif expected_behavior == "modifies_state":
            assertions.extend(AssertionGenerator._generate_state_assertions(
                function_call, function_info, language))
        elif expected_behavior == "validates_input":
            assertions.extend(AssertionGenerator._generate_validation_assertions(
                function_call, function_info, language))
        else:
            # Default basic assertions
            assertions.extend(AssertionGenerator._generate_basic_assertions(
                function_call, function_info, language))
        
        return assertions
    
    @staticmethod
    def _generate_return_value_assertions(function_call: str, function_info: FunctionInfo, 
                                        language: str) -> List[str]:
        """Generate assertions for return value testing."""
        assertions = []
        
        if language == "python":
            assertions.append(f"result = {function_call}")
            assertions.append("assert result is not None")
            
            # Type-specific assertions based on return type
            if function_info.return_type:
                return_type = function_info.return_type.lower()
                if return_type in ['int', 'integer']:
                    assertions.append("assert isinstance(result, int)")
                elif return_type in ['str', 'string']:
                    assertions.append("assert isinstance(result, str)")
                elif return_type in ['list', 'array']:
                    assertions.append("assert isinstance(result, list)")
                elif return_type in ['dict', 'dictionary']:
                    assertions.append("assert isinstance(result, dict)")
                elif return_type in ['bool', 'boolean']:
                    assertions.append("assert isinstance(result, bool)")
            
        elif language in ["javascript", "typescript"]:
            assertions.append(f"const result = {function_call};")
            assertions.append("expect(result).toBeDefined();")
            
            if function_info.return_type:
                return_type = function_info.return_type.lower()
                if return_type in ['number', 'int', 'integer']:
                    assertions.append("expect(typeof result).toBe('number');")
                elif return_type in ['string', 'str']:
                    assertions.append("expect(typeof result).toBe('string');")
                elif return_type in ['boolean', 'bool']:
                    assertions.append("expect(typeof result).toBe('boolean');")
                elif return_type in ['array', 'list']:
                    assertions.append("expect(Array.isArray(result)).toBe(true);")
                elif return_type in ['object', 'dict']:
                    assertions.append("expect(typeof result).toBe('object');")
            
        elif language == "java":
            assertions.append(f"Object result = {function_call};")
            assertions.append("assertNotNull(result);")
            
            if function_info.return_type:
                return_type = function_info.return_type
                if return_type in ['int', 'Integer']:
                    assertions.append("assertTrue(result instanceof Integer);")
                elif return_type in ['String']:
                    assertions.append("assertTrue(result instanceof String);")
                elif return_type in ['boolean', 'Boolean']:
                    assertions.append("assertTrue(result instanceof Boolean);")
        
        return assertions
    
    @staticmethod
    def _generate_exception_assertions(function_call: str, function_info: FunctionInfo, 
                                     language: str) -> List[str]:
        """Generate assertions for exception testing."""
        assertions = []
        
        if language == "python":
            assertions.append("with pytest.raises(Exception):")
            assertions.append(f"    {function_call}")
            
        elif language in ["javascript", "typescript"]:
            assertions.append(f"expect(() => {function_call}).toThrow();")
            
        elif language == "java":
            assertions.append(f"assertThrows(Exception.class, () -> {function_call});")
        
        return assertions
    
    @staticmethod
    def _generate_state_assertions(function_call: str, function_info: FunctionInfo, 
                                 language: str) -> List[str]:
        """Generate assertions for state modification testing."""
        assertions = []
        
        if language == "python":
            assertions.append(f"{function_call}")
            assertions.append("# Verify state changes")
            assertions.append("# Add specific state assertions here")
            
        elif language in ["javascript", "typescript"]:
            assertions.append(f"{function_call};")
            assertions.append("// Verify state changes")
            assertions.append("// Add specific state assertions here")
            
        elif language == "java":
            assertions.append(f"{function_call};")
            assertions.append("// Verify state changes")
            assertions.append("// Add specific state assertions here")
        
        return assertions
    
    @staticmethod
    def _generate_validation_assertions(function_call: str, function_info: FunctionInfo, 
                                      language: str) -> List[str]:
        """Generate assertions for input validation testing."""
        assertions = []
        
        if language == "python":
            assertions.append("with pytest.raises((ValueError, TypeError)):")
            assertions.append(f"    {function_call}")
            
        elif language in ["javascript", "typescript"]:
            assertions.append(f"expect(() => {function_call}).toThrow();")
            
        elif language == "java":
            assertions.append(f"assertThrows(IllegalArgumentException.class, () -> {function_call});")
        
        return assertions
    
    @staticmethod
    def _generate_basic_assertions(function_call: str, function_info: FunctionInfo, 
                                 language: str) -> List[str]:
        """Generate basic assertions when behavior is unknown."""
        assertions = []
        
        if language == "python":
            assertions.append(f"result = {function_call}")
            assertions.append("# Add specific assertions based on expected behavior")
            
        elif language in ["javascript", "typescript"]:
            assertions.append(f"const result = {function_call};")
            assertions.append("// Add specific assertions based on expected behavior")
            
        elif language == "java":
            assertions.append(f"Object result = {function_call};")
            assertions.append("// Add specific assertions based on expected behavior")
        
        return assertions
    
    @staticmethod
    def _js_repr(value: Any) -> str:
        """JavaScript representation of a value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            return f"[{', '.join(AssertionGenerator._js_repr(v) for v in value)}]"
        elif isinstance(value, dict):
            items = [f'"{k}": {AssertionGenerator._js_repr(v)}' for k, v in value.items()]
            return f"{{{', '.join(items)}}}"
        else:
            return str(value)
    
    @staticmethod
    def _java_repr(value: Any) -> str:
        """Java representation of a value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            return f"Arrays.asList({', '.join(AssertionGenerator._java_repr(v) for v in value)})"
        elif isinstance(value, dict):
            return "new HashMap<>()" # Simplified for now
        else:
            return str(value)


class UnitTestGenerator:
    """Specialized generator for individual function unit testing."""
    
    def __init__(self):
        """Initialize the unit test generator."""
        self.test_data_generator = TestDataGenerator()
        self.assertion_generator = AssertionGenerator()
        
        # Language-specific test templates
        self.templates = {
            "python": self._get_python_template(),
            "javascript": self._get_javascript_template(),
            "typescript": self._get_typescript_template(),
            "java": self._get_java_template()
        }
    
    def generate_unit_tests(self, function_info: FunctionInfo, language: str, 
                          test_scenarios: Optional[List[str]] = None) -> List[TestCase]:
        """Generate comprehensive unit tests for a single function.
        
        Args:
            function_info: Information about the function to test
            language: Programming language (python, javascript, java)
            test_scenarios: Optional list of specific scenarios to test
            
        Returns:
            List of generated unit test cases
        """
        test_cases = []
        
        # Default test scenarios if none provided
        if not test_scenarios:
            test_scenarios = self._determine_test_scenarios(function_info)
        
        for scenario in test_scenarios:
            test_case = self._generate_test_case_for_scenario(
                function_info, language, scenario
            )
            if test_case:
                test_cases.append(test_case)
        
        logger.info(f"Generated {len(test_cases)} unit tests for {function_info.name}")
        return test_cases
    
    def generate_parameter_variations(self, function_info: FunctionInfo, language: str) -> List[TestCase]:
        """Generate test cases for different parameter variations.
        
        Args:
            function_info: Function information
            language: Programming language
            
        Returns:
            List of test cases covering parameter variations
        """
        test_cases = []
        
        if not function_info.parameters:
            # No parameters - generate simple test
            test_case = self._generate_no_param_test(function_info, language)
            test_cases.append(test_case)
            return test_cases
        
        # Generate tests for each parameter
        for i, param in enumerate(function_info.parameters):
            # Generate test with focus on this parameter
            test_values = self.test_data_generator.generate_for_type(
                param.name, param.type_hint, language, "basic"
            )
            
            for j, test_value in enumerate(test_values[:3]):  # Limit to 3 variations per param
                test_inputs = self._generate_base_inputs(function_info, language)
                test_inputs[param.name] = test_value
                
                test_case = self._create_test_case(
                    function_info, language, test_inputs,
                    f"test_{function_info.name}_param_{param.name}_{j}",
                    f"Test {function_info.name} with {param.name}={repr(test_value)}",
                    "returns_value"
                )
                test_cases.append(test_case)
        
        return test_cases
    
    def generate_edge_case_tests(self, function_info: FunctionInfo, language: str) -> List[TestCase]:
        """Generate edge case tests for a function.
        
        Args:
            function_info: Function information
            language: Programming language
            
        Returns:
            List of edge case test cases
        """
        test_cases = []
        
        # Generate edge cases for each parameter
        for param in function_info.parameters:
            edge_values = self.test_data_generator.generate_for_type(
                param.name, param.type_hint, language, "edge"
            )
            
            for edge_value in edge_values[:2]:  # Limit to 2 edge cases per param
                test_inputs = self._generate_base_inputs(function_info, language)
                test_inputs[param.name] = edge_value
                
                # Determine expected behavior for edge case
                expected_behavior = self._determine_edge_case_behavior(param, edge_value)
                
                test_case = self._create_test_case(
                    function_info, language, test_inputs,
                    f"test_{function_info.name}_edge_{param.name}_{self._safe_name(edge_value)}",
                    f"Test {function_info.name} edge case: {param.name}={repr(edge_value)}",
                    expected_behavior
                )
                test_cases.append(test_case)
        
        return test_cases
    
    def _determine_test_scenarios(self, function_info: FunctionInfo) -> List[str]:
        """Determine appropriate test scenarios for a function."""
        scenarios = ["basic_functionality"]
        
        # Add scenarios based on function characteristics
        if function_info.parameters:
            scenarios.append("parameter_variations")
            scenarios.append("edge_cases")
        
        # Add scenarios based on function name patterns
        func_name_lower = function_info.name.lower()
        
        if any(word in func_name_lower for word in ['validate', 'check', 'verify']):
            scenarios.append("validation_tests")
        
        if any(word in func_name_lower for word in ['calculate', 'compute', 'process']):
            scenarios.append("computation_tests")
        
        if any(word in func_name_lower for word in ['parse', 'format', 'convert']):
            scenarios.append("transformation_tests")
        
        return scenarios
    
    def _generate_test_case_for_scenario(self, function_info: FunctionInfo, 
                                       language: str, scenario: str) -> Optional[TestCase]:
        """Generate a test case for a specific scenario."""
        if scenario == "basic_functionality":
            return self._generate_basic_functionality_test(function_info, language)
        elif scenario == "parameter_variations":
            variations = self.generate_parameter_variations(function_info, language)
            return variations[0] if variations else None
        elif scenario == "edge_cases":
            edge_cases = self.generate_edge_case_tests(function_info, language)
            return edge_cases[0] if edge_cases else None
        elif scenario == "validation_tests":
            return self._generate_validation_test(function_info, language)
        elif scenario == "computation_tests":
            return self._generate_computation_test(function_info, language)
        elif scenario == "transformation_tests":
            return self._generate_transformation_test(function_info, language)
        else:
            return self._generate_basic_functionality_test(function_info, language)
    
    def _generate_basic_functionality_test(self, function_info: FunctionInfo, 
                                         language: str) -> TestCase:
        """Generate a basic functionality test."""
        test_inputs = self._generate_base_inputs(function_info, language)
        
        return self._create_test_case(
            function_info, language, test_inputs,
            f"test_{function_info.name}_basic",
            f"Test basic functionality of {function_info.name}",
            "returns_value"
        )
    
    def _generate_validation_test(self, function_info: FunctionInfo, language: str) -> TestCase:
        """Generate a validation test with invalid inputs."""
        test_inputs = {}
        
        # Generate invalid inputs for validation testing
        for param in function_info.parameters:
            if param.type_hint and param.type_hint.lower() in ['str', 'string']:
                test_inputs[param.name] = None  # Invalid string
            elif param.type_hint and param.type_hint.lower() in ['int', 'integer']:
                test_inputs[param.name] = "not_a_number"  # Invalid integer
            else:
                test_inputs[param.name] = None
        
        return self._create_test_case(
            function_info, language, test_inputs,
            f"test_{function_info.name}_validation",
            f"Test {function_info.name} input validation",
            "throws_exception"
        )
    
    def _generate_computation_test(self, function_info: FunctionInfo, language: str) -> TestCase:
        """Generate a computation test with known inputs/outputs."""
        test_inputs = {}
        
        # Generate predictable inputs for computation testing
        for param in function_info.parameters:
            param_lower = param.name.lower()
            if any(word in param_lower for word in ['num', 'value', 'x', 'y']):
                test_inputs[param.name] = 10
            elif any(word in param_lower for word in ['list', 'array', 'data']):
                test_inputs[param.name] = [1, 2, 3, 4, 5]
            else:
                test_inputs[param.name] = self._get_default_value_for_param(param, language)
        
        return self._create_test_case(
            function_info, language, test_inputs,
            f"test_{function_info.name}_computation",
            f"Test {function_info.name} computation with known values",
            "returns_value"
        )
    
    def _generate_transformation_test(self, function_info: FunctionInfo, language: str) -> TestCase:
        """Generate a transformation test."""
        test_inputs = {}
        
        # Generate inputs suitable for transformation testing
        for param in function_info.parameters:
            param_lower = param.name.lower()
            if any(word in param_lower for word in ['text', 'string', 'input']):
                test_inputs[param.name] = "Hello World"
            elif any(word in param_lower for word in ['data', 'obj', 'item']):
                test_inputs[param.name] = {"key": "value"}
            else:
                test_inputs[param.name] = self._get_default_value_for_param(param, language)
        
        return self._create_test_case(
            function_info, language, test_inputs,
            f"test_{function_info.name}_transformation",
            f"Test {function_info.name} data transformation",
            "returns_value"
        )
    
    def _generate_no_param_test(self, function_info: FunctionInfo, language: str) -> TestCase:
        """Generate test for function with no parameters."""
        return self._create_test_case(
            function_info, language, {},
            f"test_{function_info.name}_no_params",
            f"Test {function_info.name} with no parameters",
            "returns_value"
        )
    
    def _create_test_case(self, function_info: FunctionInfo, language: str, 
                         test_inputs: Dict[str, Any], test_name: str, 
                         description: str, expected_behavior: str) -> TestCase:
        """Create a test case with generated code."""
        # Generate assertions
        assertions = self.assertion_generator.generate_assertions(
            function_info, test_inputs, expected_behavior, language
        )
        
        # Generate test code using template
        template = self.templates.get(language, self.templates["python"])
        test_code = template.format(
            test_name=test_name,
            function_name=function_info.name,
            test_inputs=test_inputs,
            assertions="\n    ".join(assertions),
            description=description
        )
        
        return TestCase(
            name=test_name,
            test_type=TestType.UNIT,
            function_name=function_info.name,
            description=description,
            test_code=test_code,
            requirements_covered=["1.1", "1.2", "8.1", "8.2", "8.3", "8.4"]
        )
    
    def _generate_base_inputs(self, function_info: FunctionInfo, language: str) -> Dict[str, Any]:
        """Generate base input values for all parameters."""
        inputs = {}
        
        for param in function_info.parameters:
            inputs[param.name] = self._get_default_value_for_param(param, language)
        
        return inputs
    
    def _get_default_value_for_param(self, param: Parameter, language: str) -> Any:
        """Get a default test value for a parameter."""
        if param.default_value is not None:
            return param.default_value
        
        # Generate based on type hint
        if param.type_hint:
            type_lower = param.type_hint.lower()
            if type_lower in ['int', 'integer']:
                return 42
            elif type_lower in ['float', 'double']:
                return 3.14
            elif type_lower in ['str', 'string']:
                return "test_string"
            elif type_lower in ['bool', 'boolean']:
                return True
            elif type_lower in ['list', 'array']:
                return [1, 2, 3]
            elif type_lower in ['dict', 'map', 'object']:
                return {"key": "value"}
        
        # Generate based on parameter name
        param_lower = param.name.lower()
        if any(word in param_lower for word in ['num', 'count', 'size']):
            return 10
        elif any(word in param_lower for word in ['name', 'text', 'message']):
            return "test_value"
        elif any(word in param_lower for word in ['flag', 'enabled']):
            return True
        elif any(word in param_lower for word in ['list', 'items']):
            return [1, 2, 3]
        else:
            return "test_value"
    
    def _determine_edge_case_behavior(self, param: Parameter, edge_value: Any) -> str:
        """Determine expected behavior for an edge case value."""
        if edge_value is None:
            return "throws_exception"
        elif isinstance(edge_value, str) and edge_value == "":
            return "validates_input"
        elif isinstance(edge_value, (list, dict)) and len(edge_value) == 0:
            return "returns_value"
        elif isinstance(edge_value, (int, float)) and edge_value == 0:
            return "returns_value"
        elif isinstance(edge_value, float) and (edge_value == float('inf') or edge_value == float('-inf')):
            return "throws_exception"
        elif isinstance(edge_value, float) and str(edge_value) == 'nan':
            return "throws_exception"
        else:
            return "returns_value"
    
    def _safe_name(self, value: Any) -> str:
        """Generate a safe name for test case from a value."""
        if value is None:
            return "none"
        elif isinstance(value, str):
            if value == "":
                return "empty_string"
            elif len(value) > 20:
                return "long_string"
            else:
                return "string"
        elif isinstance(value, (list, tuple)):
            if len(value) == 0:
                return "empty_list"
            elif len(value) == 1:
                return "single_item"
            else:
                return "list"
        elif isinstance(value, dict):
            if len(value) == 0:
                return "empty_dict"
            else:
                return "dict"
        elif isinstance(value, (int, float)):
            if value == 0:
                return "zero"
            elif value < 0:
                return "negative"
            elif value == float('inf'):
                return "infinity"
            elif value == float('-inf'):
                return "neg_infinity"
            elif str(value) == 'nan':
                return "nan"
            else:
                return "positive"
        elif isinstance(value, bool):
            return "true" if value else "false"
        else:
            return "value"
    
    def _infer_parameter_type(self, param: Parameter, language: str) -> Optional[str]:
        """Infer parameter type from name and default value."""
        if param.type_hint:
            return param.type_hint
        
        # Infer from default value
        if param.default_value is not None:
            if isinstance(param.default_value, int):
                return "int"
            elif isinstance(param.default_value, float):
                return "float"
            elif isinstance(param.default_value, str):
                return "str"
            elif isinstance(param.default_value, bool):
                return "bool"
            elif isinstance(param.default_value, list):
                return "list"
            elif isinstance(param.default_value, dict):
                return "dict"
        
        # Infer from parameter name
        param_lower = param.name.lower()
        if any(word in param_lower for word in ['num', 'count', 'size', 'length', 'index', 'id']):
            return "int"
        elif any(word in param_lower for word in ['rate', 'ratio', 'percent', 'score', 'value']):
            return "float"
        elif any(word in param_lower for word in ['name', 'text', 'message', 'title', 'description']):
            return "str"
        elif any(word in param_lower for word in ['flag', 'enabled', 'active', 'valid']):
            return "bool"
        elif any(word in param_lower for word in ['list', 'items', 'data', 'collection']):
            return "list"
        elif any(word in param_lower for word in ['config', 'options', 'settings', 'params']):
            return "dict"
        
        return None
    
    def _get_python_template(self) -> str:
        """Get Python test template."""
        return '''def {test_name}():
    """{description}"""
    {assertions}'''
    
    def _get_javascript_template(self) -> str:
        """Get JavaScript test template."""
        return '''test('{test_name}', () => {{
    // {description}
    {assertions}
}});'''
    
    def _get_typescript_template(self) -> str:
        """Get TypeScript test template."""
        return '''test('{test_name}', () => {{
    // {description}
    {assertions}
}});'''
    
    def _get_java_template(self) -> str:
        """Get Java test template."""
        return '''@Test
public void {test_name}() {{
    // {description}
    {assertions}
}}'''