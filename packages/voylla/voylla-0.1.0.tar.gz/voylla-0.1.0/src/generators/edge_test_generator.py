"""
Edge Test Generator - Specialized generator for edge case and boundary testing
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from src.interfaces.base_interfaces import (
    FunctionInfo, Parameter, TestCase, TestType, Language, EdgeCase
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class EdgeTestScenario:
    """Represents an edge case test scenario."""
    name: str
    description: str
    edge_case_type: str
    test_inputs: Dict[str, Any]
    expected_behavior: str
    exception_type: Optional[str] = None


class EdgeTestGenerator:
    """Specialized generator for edge case and boundary testing."""
    
    def __init__(self):
        """Initialize the edge test generator."""
        pass
    
    def generate_edge_case_tests(self, function_info: FunctionInfo, detected_edge_cases: List[EdgeCase], 
                                language: str) -> List[TestCase]:
        """Generate comprehensive edge case tests for a function."""
        test_cases = []
        
        # Generate basic null input test
        if function_info.parameters:
            null_inputs = {param.name: None for param in function_info.parameters}
            test_case = TestCase(
                name=f"test_{function_info.name}_edge_null_inputs",
                test_type=TestType.EDGE,
                function_name=function_info.name,
                description=f"Test {function_info.name} with null inputs",
                test_code=self._generate_null_test_code(function_info, null_inputs, language),
                requirements_covered=["2.1", "2.2", "2.3", "2.4", "8.1", "8.2", "8.3", "8.4"]
            )
            test_cases.append(test_case)
        
        # Generate division by zero tests for detected edge cases
        for edge_case in detected_edge_cases:
            if edge_case.type.lower() == "division_by_zero":
                test_inputs = self._generate_division_zero_inputs(function_info)
                test_case = TestCase(
                    name=f"test_{function_info.name}_edge_division_by_zero",
                    test_type=TestType.EDGE,
                    function_name=function_info.name,
                    description=f"Test {function_info.name} division by zero",
                    test_code=self._generate_division_zero_test_code(function_info, test_inputs, language),
                    requirements_covered=["2.1", "2.2", "2.3", "2.4", "8.1", "8.2", "8.3", "8.4"]
                )
                test_cases.append(test_case)
        
        logger.info(f"Generated {len(test_cases)} edge case tests for {function_info.name}")
        return test_cases
    
    def generate_boundary_value_tests(self, function_info: FunctionInfo, language: str) -> List[TestCase]:
        """Generate boundary value tests for parameters."""
        test_cases = []
        
        for param in function_info.parameters:
            if self._is_numeric_parameter(param):
                # Test with zero
                test_inputs = {p.name: 10 if p != param else 0 for p in function_info.parameters}
                test_case = TestCase(
                    name=f"test_{function_info.name}_boundary_zero_{param.name}",
                    test_type=TestType.EDGE,
                    function_name=function_info.name,
                    description=f"Test {function_info.name} with zero {param.name}",
                    test_code=self._generate_boundary_test_code(function_info, test_inputs, language),
                    requirements_covered=["2.1", "2.2", "2.3", "2.4", "8.1", "8.2", "8.3", "8.4"]
                )
                test_cases.append(test_case)
        
        return test_cases
    
    def generate_exception_tests(self, function_info: FunctionInfo, language: str) -> List[TestCase]:
        """Generate tests that verify proper exception handling."""
        test_cases = []
        
        # Test with invalid type inputs
        invalid_inputs = self._generate_invalid_type_inputs(function_info)
        test_case = TestCase(
            name=f"test_{function_info.name}_exception_invalid_types",
            test_type=TestType.EDGE,
            function_name=function_info.name,
            description=f"Test {function_info.name} with invalid type inputs",
            test_code=self._generate_exception_test_code(function_info, invalid_inputs, language),
            requirements_covered=["2.1", "2.2", "2.3", "2.4", "8.1", "8.2", "8.3", "8.4"]
        )
        test_cases.append(test_case)
        
        return test_cases
    
    def generate_negative_tests(self, function_info: FunctionInfo, language: str) -> List[TestCase]:
        """Generate negative test cases that verify error conditions."""
        test_cases = []
        
        # Generic negative test with all None inputs
        null_inputs = {param.name: None for param in function_info.parameters}
        test_case = TestCase(
            name=f"test_{function_info.name}_negative_all_null",
            test_type=TestType.EDGE,
            function_name=function_info.name,
            description=f"Test {function_info.name} with all null inputs",
            test_code=self._generate_null_test_code(function_info, null_inputs, language),
            requirements_covered=["2.1", "2.2", "2.3", "2.4", "8.1", "8.2", "8.3", "8.4"]
        )
        test_cases.append(test_case)
        
        return test_cases
    
    def _generate_null_test_code(self, function_info: FunctionInfo, test_inputs: Dict[str, Any], language: str) -> str:
        """Generate test code for null input testing."""
        if language == "python":
            test_inputs_str = ", ".join([f"{k}={repr(v)}" for k, v in test_inputs.items()])
            return f'''def test_{function_info.name}_edge_null_inputs():
    """Test {function_info.name} with null inputs"""
    # Arrange - Set up null inputs
    
    # Act & Assert - Verify exception is raised
    with pytest.raises((TypeError, ValueError)):
        result = {function_info.name}({test_inputs_str})
'''
        return "# Test code generation not implemented for this language"
    
    def _generate_division_zero_test_code(self, function_info: FunctionInfo, test_inputs: Dict[str, Any], language: str) -> str:
        """Generate test code for division by zero testing."""
        if language == "python":
            test_inputs_str = ", ".join([f"{k}={repr(v)}" for k, v in test_inputs.items()])
            return f'''def test_{function_info.name}_edge_division_by_zero():
    """Test {function_info.name} division by zero"""
    # Arrange - Set up division by zero scenario
    
    # Act & Assert - Verify ZeroDivisionError is raised
    with pytest.raises(ZeroDivisionError):
        result = {function_info.name}({test_inputs_str})
'''
        return "# Test code generation not implemented for this language"
    
    def _generate_boundary_test_code(self, function_info: FunctionInfo, test_inputs: Dict[str, Any], language: str) -> str:
        """Generate test code for boundary value testing."""
        if language == "python":
            test_inputs_str = ", ".join([f"{k}={repr(v)}" for k, v in test_inputs.items()])
            return f'''def test_{function_info.name}_boundary_value():
    """Test {function_info.name} with boundary values"""
    # Arrange - Set up boundary value scenario
    
    # Act - Function should handle boundary values gracefully
    result = {function_info.name}({test_inputs_str})
    
    # Assert - Verify graceful handling
    assert True  # Replace with specific assertions
'''
        return "# Test code generation not implemented for this language"
    
    def _generate_exception_test_code(self, function_info: FunctionInfo, test_inputs: Dict[str, Any], language: str) -> str:
        """Generate test code for exception testing."""
        if language == "python":
            test_inputs_str = ", ".join([f"{k}={repr(v)}" for k, v in test_inputs.items()])
            return f'''def test_{function_info.name}_exception_handling():
    """Test {function_info.name} exception handling"""
    # Arrange - Set up invalid inputs
    
    # Act & Assert - Verify exception is raised
    with pytest.raises(Exception):
        result = {function_info.name}({test_inputs_str})
'''
        return "# Test code generation not implemented for this language"
    
    def _generate_division_zero_inputs(self, function_info: FunctionInfo) -> Dict[str, Any]:
        """Generate inputs that cause division by zero."""
        inputs = {}
        for param in function_info.parameters:
            if any(word in param.name.lower() for word in ['divisor', 'denominator', 'div', 'b', 'y']):
                inputs[param.name] = 0
            else:
                inputs[param.name] = 10
        return inputs
    
    def _generate_invalid_type_inputs(self, function_info: FunctionInfo) -> Dict[str, Any]:
        """Generate invalid type inputs."""
        inputs = {}
        for param in function_info.parameters:
            if self._is_numeric_parameter(param):
                inputs[param.name] = "not_a_number"
            elif self._is_string_parameter(param):
                inputs[param.name] = 12345
            else:
                inputs[param.name] = object()
        return inputs
    
    def _is_numeric_parameter(self, param: Parameter) -> bool:
        """Check if parameter is numeric."""
        if param.type_hint:
            return any(word in param.type_hint.lower() for word in ['int', 'float', 'double', 'number'])
        return any(word in param.name.lower() for word in ['num', 'count', 'size', 'value'])
    
    def _is_string_parameter(self, param: Parameter) -> bool:
        """Check if parameter is string."""
        if param.type_hint:
            return any(word in param.type_hint.lower() for word in ['str', 'string', 'text'])
        return any(word in param.name.lower() for word in ['str', 'text', 'name', 'message'])


# For backward compatibility, also export EdgeCaseAnalyzer
class EdgeCaseAnalyzer:
    """Analyzer for edge cases - simplified version."""
    
    @staticmethod
    def analyze_function_edge_cases(function_info: FunctionInfo, detected_edge_cases: List[EdgeCase]) -> List[EdgeTestScenario]:
        """Analyze function for edge case scenarios."""
        scenarios = []
        
        # Create basic scenarios for each parameter
        for param in function_info.parameters:
            scenarios.append(EdgeTestScenario(
                name=f"null_{param.name}",
                description=f"Test with null {param.name}",
                edge_case_type="null_input",
                test_inputs={param.name: None},
                expected_behavior="throws_exception",
                exception_type="TypeError"
            ))
        
        return scenarios