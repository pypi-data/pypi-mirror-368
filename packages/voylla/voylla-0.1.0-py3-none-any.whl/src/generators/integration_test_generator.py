"""
Integration Test Generator - Specialized generator for integration testing with mocking strategies
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
import logging

from ..interfaces.base_interfaces import (
    FunctionInfo, Parameter, TestCase, TestType, Language, Dependency, EdgeCase
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MockStrategy:
    """Represents a mocking strategy for a dependency."""
    dependency_name: str
    mock_type: str  # 'patch', 'mock_object', 'stub', 'fake'
    mock_setup: str
    mock_assertions: List[str]
    teardown_code: str = ""


@dataclass
class IntegrationScenario:
    """Represents an integration test scenario."""
    name: str
    description: str
    dependencies: List[Dependency]
    mock_strategies: List[MockStrategy]
    setup_requirements: List[str]
    expected_interactions: List[str]


class MockStrategyGenerator:
    """Generates appropriate mocking strategies for different types of dependencies."""
    
    @staticmethod
    def generate_mock_strategy(dependency: Dependency, language: str) -> MockStrategy:
        """Generate appropriate mock strategy based on dependency type and language."""
        dep_type = dependency.type.lower()
        dep_name = dependency.name
        
        if 'database' in dep_type:
            return MockStrategyGenerator._generate_database_mock(dependency, language)
        elif 'http' in dep_type or 'network' in dep_type:
            return MockStrategyGenerator._generate_http_mock(dependency, language)
        elif 'file' in dep_type:
            return MockStrategyGenerator._generate_file_mock(dependency, language)
        elif 'external_call' in dep_type:
            return MockStrategyGenerator._generate_external_call_mock(dependency, language)
        else:
            return MockStrategyGenerator._generate_generic_mock(dependency, language)
    
    @staticmethod
    def _generate_database_mock(dependency: Dependency, language: str) -> MockStrategy:
        """Generate database mocking strategy."""
        if language == "python":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='patch',
                mock_setup=f"""
# Mock database connection
mock_db = Mock()
mock_cursor = Mock()
mock_db.cursor.return_value = mock_cursor
mock_cursor.fetchall.return_value = [('test_data',)]
mock_cursor.fetchone.return_value = ('test_record',)
mock_cursor.execute.return_value = None""",
                mock_assertions=[
                    "mock_db.cursor.assert_called()",
                    "mock_cursor.execute.assert_called()",
                    "assert mock_cursor.execute.call_count >= 1"
                ],
                teardown_code="mock_db.reset_mock()"
            )
        elif language in ["javascript", "typescript"]:
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock database connection
const mockDb = {{
    query: jest.fn().mockResolvedValue([{{ id: 1, name: 'test' }}]),
    connect: jest.fn().mockResolvedValue(true),
    close: jest.fn().mockResolvedValue(true)
}};""",
                mock_assertions=[
                    "expect(mockDb.connect).toHaveBeenCalled();",
                    "expect(mockDb.query).toHaveBeenCalled();",
                    "expect(mockDb.close).toHaveBeenCalled();"
                ],
                teardown_code="jest.clearAllMocks();"
            )
        elif language == "java":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock database connection
Connection mockConnection = Mockito.mock(Connection.class);
PreparedStatement mockStatement = Mockito.mock(PreparedStatement.class);
ResultSet mockResultSet = Mockito.mock(ResultSet.class);

when(mockConnection.prepareStatement(anyString())).thenReturn(mockStatement);
when(mockStatement.executeQuery()).thenReturn(mockResultSet);
when(mockResultSet.next()).thenReturn(true).thenReturn(false);
when(mockResultSet.getString(anyString())).thenReturn("test_data");""",
                mock_assertions=[
                    "verify(mockConnection).prepareStatement(anyString());",
                    "verify(mockStatement).executeQuery();",
                    "verify(mockResultSet, atLeastOnce()).next();"
                ],
                teardown_code="Mockito.reset(mockConnection, mockStatement, mockResultSet);"
            )
        else:
            return MockStrategyGenerator._generate_generic_mock(dependency, language)
    
    @staticmethod
    def _generate_http_mock(dependency: Dependency, language: str) -> MockStrategy:
        """Generate HTTP/network mocking strategy."""
        if language == "python":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='patch',
                mock_setup=f"""
# Mock HTTP requests
mock_response = Mock()
mock_response.status_code = 200
mock_response.json.return_value = {{'status': 'success', 'data': 'test_data'}}
mock_response.text = 'test response'
mock_response.raise_for_status.return_value = None""",
                mock_assertions=[
                    "mock_response.raise_for_status.assert_called()",
                    "assert mock_response.status_code == 200",
                    "mock_response.json.assert_called()"
                ],
                teardown_code="mock_response.reset_mock()"
            )
        elif language in ["javascript", "typescript"]:
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock HTTP client
const mockHttpClient = {{
    get: jest.fn().mockResolvedValue({{
        status: 200,
        data: {{ message: 'success' }},
        headers: {{ 'content-type': 'application/json' }}
    }}),
    post: jest.fn().mockResolvedValue({{
        status: 201,
        data: {{ id: 1, created: true }}
    }})
}};""",
                mock_assertions=[
                    "expect(mockHttpClient.get).toHaveBeenCalled();",
                    "expect(mockHttpClient.get).toHaveBeenCalledWith(expect.any(String));",
                    "expect(mockHttpClient.post).toHaveBeenCalledTimes(1);"
                ],
                teardown_code="jest.clearAllMocks();"
            )
        elif language == "java":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock HTTP client
HttpClient mockHttpClient = Mockito.mock(HttpClient.class);
HttpResponse<String> mockResponse = Mockito.mock(HttpResponse.class);

when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
    .thenReturn(mockResponse);
when(mockResponse.statusCode()).thenReturn(200);
when(mockResponse.body()).thenReturn("{{\\"status\\": \\"success\\"}}")""",
                mock_assertions=[
                    "verify(mockHttpClient).send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class));",
                    "verify(mockResponse).statusCode();",
                    "verify(mockResponse).body();"
                ],
                teardown_code="Mockito.reset(mockHttpClient, mockResponse);"
            )
        else:
            return MockStrategyGenerator._generate_generic_mock(dependency, language)
    
    @staticmethod
    def _generate_file_mock(dependency: Dependency, language: str) -> MockStrategy:
        """Generate file system mocking strategy."""
        if language == "python":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='patch',
                mock_setup=f"""
# Mock file operations
mock_file = Mock()
mock_file.read.return_value = "test file content"
mock_file.write.return_value = None
mock_file.close.return_value = None
mock_file.__enter__.return_value = mock_file
mock_file.__exit__.return_value = None""",
                mock_assertions=[
                    "mock_file.read.assert_called()",
                    "mock_file.write.assert_called()",
                    "mock_file.close.assert_called()"
                ],
                teardown_code="mock_file.reset_mock()"
            )
        elif language in ["javascript", "typescript"]:
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock file system operations
const mockFs = {{
    readFile: jest.fn().mockResolvedValue('test file content'),
    writeFile: jest.fn().mockResolvedValue(undefined),
    existsSync: jest.fn().mockReturnValue(true),
    statSync: jest.fn().mockReturnValue({{ isFile: () => true, size: 1024 }})
}};""",
                mock_assertions=[
                    "expect(mockFs.readFile).toHaveBeenCalled();",
                    "expect(mockFs.writeFile).toHaveBeenCalled();",
                    "expect(mockFs.existsSync).toHaveBeenCalled();"
                ],
                teardown_code="jest.clearAllMocks();"
            )
        elif language == "java":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock file operations
File mockFile = Mockito.mock(File.class);
FileInputStream mockInputStream = Mockito.mock(FileInputStream.class);
FileOutputStream mockOutputStream = Mockito.mock(FileOutputStream.class);

when(mockFile.exists()).thenReturn(true);
when(mockFile.canRead()).thenReturn(true);
when(mockFile.canWrite()).thenReturn(true);
when(mockFile.length()).thenReturn(1024L);""",
                mock_assertions=[
                    "verify(mockFile).exists();",
                    "verify(mockFile).canRead();",
                    "verify(mockFile).canWrite();"
                ],
                teardown_code="Mockito.reset(mockFile, mockInputStream, mockOutputStream);"
            )
        else:
            return MockStrategyGenerator._generate_generic_mock(dependency, language)
    
    @staticmethod
    def _generate_external_call_mock(dependency: Dependency, language: str) -> MockStrategy:
        """Generate external service call mocking strategy."""
        if language == "python":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='patch',
                mock_setup=f"""
# Mock external service call
mock_service = Mock()
mock_service.return_value = {{'result': 'success', 'data': 'test_data'}}
mock_service.side_effect = None  # No exceptions by default""",
                mock_assertions=[
                    "mock_service.assert_called()",
                    "assert mock_service.call_count >= 1",
                    "mock_service.assert_called_with(expected_args)"
                ],
                teardown_code="mock_service.reset_mock()"
            )
        elif language in ["javascript", "typescript"]:
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock external service
const mockService = {{
    call: jest.fn().mockResolvedValue({{ success: true, data: 'test_data' }}),
    authenticate: jest.fn().mockResolvedValue({{ token: 'mock_token' }}),
    disconnect: jest.fn().mockResolvedValue(true)
}};""",
                mock_assertions=[
                    "expect(mockService.call).toHaveBeenCalled();",
                    "expect(mockService.authenticate).toHaveBeenCalled();",
                    "expect(mockService.disconnect).toHaveBeenCalled();"
                ],
                teardown_code="jest.clearAllMocks();"
            )
        elif language == "java":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock external service
ExternalService mockService = Mockito.mock(ExternalService.class);
ServiceResponse mockResponse = new ServiceResponse("success", "test_data");

when(mockService.call(any())).thenReturn(mockResponse);
when(mockService.authenticate(anyString())).thenReturn(true);
when(mockService.isConnected()).thenReturn(true);""",
                mock_assertions=[
                    "verify(mockService).call(any());",
                    "verify(mockService).authenticate(anyString());",
                    "verify(mockService).isConnected();"
                ],
                teardown_code="Mockito.reset(mockService);"
            )
        else:
            return MockStrategyGenerator._generate_generic_mock(dependency, language)
    
    @staticmethod
    def _generate_generic_mock(dependency: Dependency, language: str) -> MockStrategy:
        """Generate generic mocking strategy for unknown dependency types."""
        if language == "python":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='patch',
                mock_setup=f"""
# Mock {dependency.name}
mock_{dependency.name.replace('.', '_')} = Mock()
mock_{dependency.name.replace('.', '_')}.return_value = 'mocked_result'""",
                mock_assertions=[
                    f"mock_{dependency.name.replace('.', '_')}.assert_called()"
                ],
                teardown_code=f"mock_{dependency.name.replace('.', '_')}.reset_mock()"
            )
        elif language in ["javascript", "typescript"]:
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock {dependency.name}
const mock{dependency.name.replace('.', '').replace('-', '').title()} = {{
    method: jest.fn().mockReturnValue('mocked_result')
}};""",
                mock_assertions=[
                    f"expect(mock{dependency.name.replace('.', '').replace('-', '').title()}.method).toHaveBeenCalled();"
                ],
                teardown_code="jest.clearAllMocks();"
            )
        elif language == "java":
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='mock_object',
                mock_setup=f"""
// Mock {dependency.name}
Object mock{dependency.name.replace('.', '').title()} = Mockito.mock(Object.class);
when(mock{dependency.name.replace('.', '').title()}.toString()).thenReturn("mocked_result");""",
                mock_assertions=[
                    f"verify(mock{dependency.name.replace('.', '').title()}).toString();"
                ],
                teardown_code=f"Mockito.reset(mock{dependency.name.replace('.', '').title()});"
            )
        else:
            return MockStrategy(
                dependency_name=dependency.name,
                mock_type='generic',
                mock_setup=f"// Mock setup for {dependency.name}",
                mock_assertions=[f"// Verify {dependency.name} interactions"],
                teardown_code=f"// Cleanup {dependency.name} mock"
            )


class IntegrationTestGenerator:
    """Specialized generator for integration testing with comprehensive mocking strategies."""
    
    def __init__(self):
        """Initialize the integration test generator."""
        self.mock_strategy_generator = MockStrategyGenerator()
        
        # Language-specific test templates
        self.templates = {
            "python": self._get_python_template(),
            "javascript": self._get_javascript_template(),
            "typescript": self._get_typescript_template(),
            "java": self._get_java_template()
        }
    
    def generate_integration_tests(self, function_info: FunctionInfo, dependencies: List[Dependency], 
                                 language: str, edge_cases: Optional[List[EdgeCase]] = None) -> List[TestCase]:
        """Generate comprehensive integration tests for a function with its dependencies.
        
        Args:
            function_info: Information about the function to test
            dependencies: List of dependencies that need mocking
            language: Programming language (python, javascript, java)
            edge_cases: Optional list of edge cases to consider
            
        Returns:
            List of generated integration test cases
        """
        test_cases = []
        
        if not dependencies:
            logger.info(f"No dependencies found for {function_info.name}, skipping integration tests")
            return test_cases
        
        # Group dependencies by type for better test organization
        dependency_groups = self._group_dependencies_by_type(dependencies)
        
        # Generate integration scenarios
        scenarios = self._generate_integration_scenarios(function_info, dependency_groups, edge_cases)
        
        for scenario in scenarios:
            test_case = self._generate_test_case_for_scenario(function_info, scenario, language)
            if test_case:
                test_cases.append(test_case)
        
        logger.info(f"Generated {len(test_cases)} integration tests for {function_info.name}")
        return test_cases
    
    def generate_dependency_injection_tests(self, function_info: FunctionInfo, dependencies: List[Dependency], 
                                          language: str) -> List[TestCase]:
        """Generate tests that focus on dependency injection patterns.
        
        Args:
            function_info: Function information
            dependencies: List of dependencies
            language: Programming language
            
        Returns:
            List of dependency injection test cases
        """
        test_cases = []
        
        # Test with all dependencies properly injected
        test_case = self._generate_successful_injection_test(function_info, dependencies, language)
        test_cases.append(test_case)
        
        # Test with missing dependencies
        test_case = self._generate_missing_dependency_test(function_info, dependencies, language)
        test_cases.append(test_case)
        
        # Test with invalid dependencies
        test_case = self._generate_invalid_dependency_test(function_info, dependencies, language)
        test_cases.append(test_case)
        
        return test_cases
    
    def generate_mock_object_tests(self, function_info: FunctionInfo, dependencies: List[Dependency], 
                                 language: str) -> List[TestCase]:
        """Generate tests that focus on mock object creation and verification.
        
        Args:
            function_info: Function information
            dependencies: List of dependencies to mock
            language: Programming language
            
        Returns:
            List of mock object test cases
        """
        test_cases = []
        
        for dependency in dependencies:
            # Generate mock strategy
            mock_strategy = self.mock_strategy_generator.generate_mock_strategy(dependency, language)
            
            # Create test case for this specific dependency
            test_case = self._generate_mock_verification_test(
                function_info, dependency, mock_strategy, language
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _group_dependencies_by_type(self, dependencies: List[Dependency]) -> Dict[str, List[Dependency]]:
        """Group dependencies by their type for better test organization."""
        groups = {}
        
        for dep in dependencies:
            dep_type = dep.type
            if dep_type not in groups:
                groups[dep_type] = []
            groups[dep_type].append(dep)
        
        return groups
    
    def _generate_integration_scenarios(self, function_info: FunctionInfo, 
                                      dependency_groups: Dict[str, List[Dependency]], 
                                      edge_cases: Optional[List[EdgeCase]]) -> List[IntegrationScenario]:
        """Generate integration test scenarios based on dependencies and edge cases."""
        scenarios = []
        
        # Scenario 1: Happy path with all dependencies working
        happy_path_scenario = IntegrationScenario(
            name="happy_path_integration",
            description=f"Test {function_info.name} with all dependencies working correctly",
            dependencies=self._flatten_dependency_groups(dependency_groups),
            mock_strategies=[],
            setup_requirements=["All dependencies available and responsive"],
            expected_interactions=["All dependency calls succeed", "Function returns expected result"]
        )
        scenarios.append(happy_path_scenario)
        
        # Scenario 2: Database failure scenario (if database dependencies exist)
        if any('database' in group_type for group_type in dependency_groups.keys()):
            db_failure_scenario = IntegrationScenario(
                name="database_failure_integration",
                description=f"Test {function_info.name} when database operations fail",
                dependencies=[dep for deps in dependency_groups.values() for dep in deps if 'database' in dep.type],
                mock_strategies=[],
                setup_requirements=["Database connection fails or queries timeout"],
                expected_interactions=["Database errors are handled gracefully", "Appropriate exceptions are raised"]
            )
            scenarios.append(db_failure_scenario)
        
        # Scenario 3: Network failure scenario (if network dependencies exist)
        if any('network' in group_type or 'http' in group_type for group_type in dependency_groups.keys()):
            network_failure_scenario = IntegrationScenario(
                name="network_failure_integration",
                description=f"Test {function_info.name} when network calls fail",
                dependencies=[dep for deps in dependency_groups.values() for dep in deps 
                            if 'network' in dep.type or 'http' in dep.type],
                mock_strategies=[],
                setup_requirements=["Network requests timeout or return errors"],
                expected_interactions=["Network errors are handled", "Retry logic is tested", "Fallback behavior works"]
            )
            scenarios.append(network_failure_scenario)
        
        # Scenario 4: Partial dependency failure
        if len(dependency_groups) > 1:
            partial_failure_scenario = IntegrationScenario(
                name="partial_dependency_failure",
                description=f"Test {function_info.name} when some dependencies fail",
                dependencies=self._flatten_dependency_groups(dependency_groups),
                mock_strategies=[],
                setup_requirements=["Some dependencies fail while others succeed"],
                expected_interactions=["Function handles partial failures", "Degraded functionality works"]
            )
            scenarios.append(partial_failure_scenario)
        
        # Add edge case scenarios if provided
        if edge_cases:
            for edge_case in edge_cases:
                if 'dependency' in edge_case.type.lower():
                    edge_scenario = IntegrationScenario(
                        name=f"edge_case_{edge_case.type}",
                        description=f"Test {function_info.name} for edge case: {edge_case.description}",
                        dependencies=self._flatten_dependency_groups(dependency_groups),
                        mock_strategies=[],
                        setup_requirements=[f"Edge case condition: {edge_case.description}"],
                        expected_interactions=["Edge case is handled appropriately"]
                    )
                    scenarios.append(edge_scenario)
        
        return scenarios
    
    def _flatten_dependency_groups(self, dependency_groups: Dict[str, List[Dependency]]) -> List[Dependency]:
        """Flatten grouped dependencies into a single list."""
        flattened = []
        for deps in dependency_groups.values():
            flattened.extend(deps)
        return flattened
    
    def _generate_test_case_for_scenario(self, function_info: FunctionInfo, 
                                       scenario: IntegrationScenario, language: str) -> TestCase:
        """Generate a test case for a specific integration scenario."""
        # Generate mock strategies for all dependencies in the scenario
        mock_strategies = []
        for dependency in scenario.dependencies:
            mock_strategy = self.mock_strategy_generator.generate_mock_strategy(dependency, language)
            mock_strategies.append(mock_strategy)
        
        scenario.mock_strategies = mock_strategies
        
        # Generate test code using template
        template = self.templates.get(language, self.templates["python"])
        test_code = template.format(
            test_name=f"test_{function_info.name}_{scenario.name}",
            function_name=function_info.name,
            scenario=scenario,
            mock_setups=self._generate_mock_setups(mock_strategies, language),
            test_execution=self._generate_test_execution(function_info, scenario, language),
            mock_assertions=self._generate_mock_assertions(mock_strategies, language),
            teardown_code=self._generate_teardown_code(mock_strategies, language),
            description=scenario.description
        )
        
        return TestCase(
            name=f"test_{function_info.name}_{scenario.name}",
            test_type=TestType.INTEGRATION,
            function_name=function_info.name,
            description=scenario.description,
            test_code=test_code,
            requirements_covered=["3.1", "3.2", "3.3", "3.4", "8.1", "8.2", "8.3", "8.4"]
        )
    
    def _generate_successful_injection_test(self, function_info: FunctionInfo, 
                                          dependencies: List[Dependency], language: str) -> TestCase:
        """Generate test for successful dependency injection."""
        mock_strategies = [
            self.mock_strategy_generator.generate_mock_strategy(dep, language) 
            for dep in dependencies
        ]
        
        template = self.templates.get(language, self.templates["python"])
        test_code = template.format(
            test_name=f"test_{function_info.name}_successful_injection",
            function_name=function_info.name,
            scenario=IntegrationScenario(
                name="successful_injection",
                description="Test successful dependency injection",
                dependencies=dependencies,
                mock_strategies=mock_strategies,
                setup_requirements=["All dependencies properly injected"],
                expected_interactions=["Function executes successfully with injected dependencies"]
            ),
            mock_setups=self._generate_mock_setups(mock_strategies, language),
            test_execution=self._generate_successful_execution(function_info, language),
            mock_assertions=self._generate_mock_assertions(mock_strategies, language),
            teardown_code=self._generate_teardown_code(mock_strategies, language),
            description="Test successful dependency injection"
        )
        
        return TestCase(
            name=f"test_{function_info.name}_successful_injection",
            test_type=TestType.INTEGRATION,
            function_name=function_info.name,
            description="Test successful dependency injection",
            test_code=test_code,
            requirements_covered=["3.1", "3.2", "3.3", "3.4"]
        )
    
    def _generate_missing_dependency_test(self, function_info: FunctionInfo, 
                                        dependencies: List[Dependency], language: str) -> TestCase:
        """Generate test for missing dependency scenario."""
        template = self.templates.get(language, self.templates["python"])
        
        if language == "python":
            test_execution = f"""
    # Test with missing dependency (None)
    with pytest.raises((AttributeError, TypeError, ValueError)):
        result = {function_info.name}(None)"""
        elif language in ["javascript", "typescript"]:
            test_execution = f"""
    // Test with missing dependency (null)
    expect(() => {{
        {function_info.name}(null);
    }}).toThrow();"""
        elif language == "java":
            test_execution = f"""
    // Test with missing dependency (null)
    assertThrows(NullPointerException.class, () -> {{
        {function_info.name}(null);
    }});"""
        else:
            test_execution = f"// Test missing dependency for {function_info.name}"
        
        test_code = template.format(
            test_name=f"test_{function_info.name}_missing_dependency",
            function_name=function_info.name,
            scenario=IntegrationScenario(
                name="missing_dependency",
                description="Test behavior with missing dependencies",
                dependencies=dependencies,
                mock_strategies=[],
                setup_requirements=["Dependencies are missing or null"],
                expected_interactions=["Function handles missing dependencies gracefully"]
            ),
            mock_setups="# No mock setup needed for missing dependency test",
            test_execution=test_execution,
            mock_assertions="# No mock assertions for missing dependency test",
            teardown_code="# No teardown needed",
            description="Test behavior with missing dependencies"
        )
        
        return TestCase(
            name=f"test_{function_info.name}_missing_dependency",
            test_type=TestType.INTEGRATION,
            function_name=function_info.name,
            description="Test behavior with missing dependencies",
            test_code=test_code,
            requirements_covered=["3.1", "3.2", "3.3", "3.4"]
        )
    
    def _generate_invalid_dependency_test(self, function_info: FunctionInfo, 
                                        dependencies: List[Dependency], language: str) -> TestCase:
        """Generate test for invalid dependency scenario."""
        template = self.templates.get(language, self.templates["python"])
        
        if language == "python":
            test_execution = f"""
    # Test with invalid dependency type
    invalid_dependency = "invalid_string_instead_of_object"
    with pytest.raises((AttributeError, TypeError)):
        result = {function_info.name}(invalid_dependency)"""
        elif language in ["javascript", "typescript"]:
            test_execution = f"""
    // Test with invalid dependency type
    const invalidDependency = "invalid_string_instead_of_object";
    expect(() => {{
        {function_info.name}(invalidDependency);
    }}).toThrow();"""
        elif language == "java":
            test_execution = f"""
    // Test with invalid dependency type
    String invalidDependency = "invalid_string_instead_of_object";
    assertThrows(ClassCastException.class, () -> {{
        {function_info.name}(invalidDependency);
    }});"""
        else:
            test_execution = f"// Test invalid dependency for {function_info.name}"
        
        test_code = template.format(
            test_name=f"test_{function_info.name}_invalid_dependency",
            function_name=function_info.name,
            scenario=IntegrationScenario(
                name="invalid_dependency",
                description="Test behavior with invalid dependency types",
                dependencies=dependencies,
                mock_strategies=[],
                setup_requirements=["Dependencies have invalid types"],
                expected_interactions=["Function rejects invalid dependencies appropriately"]
            ),
            mock_setups="# No mock setup needed for invalid dependency test",
            test_execution=test_execution,
            mock_assertions="# No mock assertions for invalid dependency test",
            teardown_code="# No teardown needed",
            description="Test behavior with invalid dependency types"
        )
        
        return TestCase(
            name=f"test_{function_info.name}_invalid_dependency",
            test_type=TestType.INTEGRATION,
            function_name=function_info.name,
            description="Test behavior with invalid dependency types",
            test_code=test_code,
            requirements_covered=["3.1", "3.2", "3.3", "3.4"]
        )
    
    def _generate_mock_verification_test(self, function_info: FunctionInfo, dependency: Dependency, 
                                       mock_strategy: MockStrategy, language: str) -> TestCase:
        """Generate test that focuses on mock object verification."""
        template = self.templates.get(language, self.templates["python"])
        
        test_code = template.format(
            test_name=f"test_{function_info.name}_mock_{dependency.name.replace('.', '_')}",
            function_name=function_info.name,
            scenario=IntegrationScenario(
                name=f"mock_{dependency.name}",
                description=f"Test mock verification for {dependency.name}",
                dependencies=[dependency],
                mock_strategies=[mock_strategy],
                setup_requirements=[f"Mock {dependency.name} properly"],
                expected_interactions=[f"Verify {dependency.name} interactions"]
            ),
            mock_setups=mock_strategy.mock_setup,
            test_execution=self._generate_mock_test_execution(function_info, dependency, language),
            mock_assertions="\n    ".join(mock_strategy.mock_assertions),
            teardown_code=mock_strategy.teardown_code,
            description=f"Test mock verification for {dependency.name}"
        )
        
        return TestCase(
            name=f"test_{function_info.name}_mock_{dependency.name.replace('.', '_')}",
            test_type=TestType.INTEGRATION,
            function_name=function_info.name,
            description=f"Test mock verification for {dependency.name}",
            test_code=test_code,
            requirements_covered=["3.1", "3.2", "3.3", "3.4"]
        )
    
    def _generate_mock_setups(self, mock_strategies: List[MockStrategy], language: str) -> str:
        """Generate mock setup code for all strategies."""
        setups = []
        for strategy in mock_strategies:
            setups.append(strategy.mock_setup)
        return "\n    ".join(setups)
    
    def _generate_test_execution(self, function_info: FunctionInfo, 
                               scenario: IntegrationScenario, language: str) -> str:
        """Generate test execution code based on scenario."""
        if scenario.name == "happy_path_integration":
            return self._generate_successful_execution(function_info, language)
        elif "failure" in scenario.name:
            return self._generate_failure_execution(function_info, language)
        else:
            return self._generate_generic_execution(function_info, language)
    
    def _generate_successful_execution(self, function_info: FunctionInfo, language: str) -> str:
        """Generate successful execution test code."""
        if language == "python":
            return f"""
    # Execute function with mocked dependencies
    result = {function_info.name}()
    
    # Verify successful execution
    assert result is not None
    # Add specific assertions based on expected return value"""
        elif language in ["javascript", "typescript"]:
            return f"""
    // Execute function with mocked dependencies
    const result = {function_info.name}();
    
    // Verify successful execution
    expect(result).toBeDefined();
    // Add specific assertions based on expected return value"""
        elif language == "java":
            return f"""
    // Execute function with mocked dependencies
    Object result = {function_info.name}();
    
    // Verify successful execution
    assertNotNull(result);
    // Add specific assertions based on expected return value"""
        else:
            return f"// Execute {function_info.name} successfully"
    
    def _generate_failure_execution(self, function_info: FunctionInfo, language: str) -> str:
        """Generate failure scenario execution test code."""
        if language == "python":
            return f"""
    # Execute function expecting failure
    with pytest.raises(Exception) as exc_info:
        result = {function_info.name}()
    
    # Verify appropriate exception handling
    assert exc_info.value is not None"""
        elif language in ["javascript", "typescript"]:
            return f"""
    // Execute function expecting failure
    expect(() => {{
        {function_info.name}();
    }}).toThrow();"""
        elif language == "java":
            return f"""
    // Execute function expecting failure
    assertThrows(Exception.class, () -> {{
        {function_info.name}();
    }});"""
        else:
            return f"// Execute {function_info.name} with expected failure"
    
    def _generate_generic_execution(self, function_info: FunctionInfo, language: str) -> str:
        """Generate generic execution test code."""
        if language == "python":
            return f"""
    # Execute function
    result = {function_info.name}()
    
    # Add appropriate assertions based on scenario"""
        elif language in ["javascript", "typescript"]:
            return f"""
    // Execute function
    const result = {function_info.name}();
    
    // Add appropriate assertions based on scenario"""
        elif language == "java":
            return f"""
    // Execute function
    Object result = {function_info.name}();
    
    // Add appropriate assertions based on scenario"""
        else:
            return f"// Execute {function_info.name}"
    
    def _generate_mock_test_execution(self, function_info: FunctionInfo, 
                                    dependency: Dependency, language: str) -> str:
        """Generate test execution code focused on mock verification."""
        if language == "python":
            return f"""
    # Execute function to trigger dependency interaction
    with patch('{dependency.name}') as mock_dep:
        result = {function_info.name}()
    
    # Verify the function executed
    assert result is not None"""
        elif language in ["javascript", "typescript"]:
            return f"""
    // Execute function to trigger dependency interaction
    const result = {function_info.name}();
    
    // Verify the function executed
    expect(result).toBeDefined();"""
        elif language == "java":
            return f"""
    // Execute function to trigger dependency interaction
    Object result = {function_info.name}();
    
    // Verify the function executed
    assertNotNull(result);"""
        else:
            return f"// Execute {function_info.name} for mock verification"
    
    def _generate_mock_assertions(self, mock_strategies: List[MockStrategy], language: str) -> str:
        """Generate mock assertion code for all strategies."""
        assertions = []
        for strategy in mock_strategies:
            assertions.extend(strategy.mock_assertions)
        return "\n    ".join(assertions)
    
    def _generate_teardown_code(self, mock_strategies: List[MockStrategy], language: str) -> str:
        """Generate teardown code for all mock strategies."""
        teardowns = []
        for strategy in mock_strategies:
            if strategy.teardown_code:
                teardowns.append(strategy.teardown_code)
        return "\n    ".join(teardowns)
    
    def _get_python_template(self) -> str:
        """Get Python integration test template."""
        return '''def {test_name}():
    """{description}"""
    # Arrange
{mock_setups}
    
    # Act
{test_execution}
    
    # Assert
{mock_assertions}
    
    # Cleanup
{teardown_code}'''
    
    def _get_javascript_template(self) -> str:
        """Get JavaScript integration test template."""
        return '''describe('{function_name} integration tests', () => {{
    test('{test_name}', () => {{
        // {description}
        
        // Arrange
{mock_setups}
        
        // Act
{test_execution}
        
        // Assert
{mock_assertions}
        
        // Cleanup
{teardown_code}
    }});
}});'''
    
    def _get_typescript_template(self) -> str:
        """Get TypeScript integration test template."""
        return self._get_javascript_template()  # Same as JavaScript for now
    
    def _get_java_template(self) -> str:
        """Get Java integration test template."""
        return '''@Test
public void {test_name}() {{
    // {description}
    
    // Arrange
{mock_setups}
    
    // Act
{test_execution}
    
    // Assert
{mock_assertions}
    
    // Cleanup
{teardown_code}
}}'''