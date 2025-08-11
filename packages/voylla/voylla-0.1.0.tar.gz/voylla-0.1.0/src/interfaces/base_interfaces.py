"""
Base interfaces and abstract classes for all core components.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TestType(Enum):
    """Enumeration of test types."""
    UNIT = "unit"
    INTEGRATION = "integration"
    EDGE = "edge"


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"


@dataclass
class CodeAnalysis:
    """Structured result of code analysis."""
    language: str
    functions: List['FunctionInfo']
    classes: List['ClassInfo']
    edge_cases: List['EdgeCase']
    dependencies: List['Dependency']
    complexity_metrics: 'ComplexityMetrics'


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    parameters: List['Parameter']
    return_type: Optional[str]
    complexity: int
    line_range: tuple[int, int]
    docstring: Optional[str] = None


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    methods: List[str]
    line_range: tuple[int, int]
    inheritance: List[str] = None


@dataclass
class Parameter:
    """Function parameter information."""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[Any] = None


@dataclass
class EdgeCase:
    """Detected edge case in code."""
    type: str
    location: str
    description: str
    severity: int


@dataclass
class Dependency:
    """Code dependency information."""
    name: str
    type: str  # 'import', 'external_api', 'database', etc.
    source: Optional[str] = None


@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    maintainability_index: float


@dataclass
class TestCase:
    """Generated test case."""
    name: str
    test_type: TestType
    function_name: str
    description: str
    test_code: str
    setup_code: str = ""
    teardown_code: str = ""
    assertions: List[str] = None
    requirements_covered: List[str] = None


@dataclass
class TestSuite:
    """Collection of test cases."""
    language: Language
    framework: str
    test_cases: List[TestCase]
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    coverage_estimate: float = 0.0


@dataclass
class CoverageReport:
    """Test coverage analysis report."""
    overall_percentage: float
    line_coverage: Dict[int, bool]
    untested_functions: List[str]
    coverage_gaps: List['CoverageGap']


@dataclass
class CoverageGap:
    """Identified gap in test coverage."""
    function_name: str
    line_range: tuple[int, int]
    description: str
    suggested_tests: List[str]


class ICodeAnalyzer(ABC):
    """Interface for code analyzers."""
    
    @abstractmethod
    def analyze_file(self, file_path: str, language: Optional[str] = None) -> CodeAnalysis:
        """Analyze a code file and return structured analysis."""
        pass
    
    @abstractmethod
    def parse_code(self, code: str, language: str) -> Any:
        """Parse code into an abstract syntax tree."""
        pass
    
    @abstractmethod
    def identify_functions(self, ast: Any) -> List[FunctionInfo]:
        """Extract function information from AST."""
        pass
    
    @abstractmethod
    def detect_edge_cases(self, ast: Any) -> List[EdgeCase]:
        """Detect potential edge cases in code."""
        pass
    
    @abstractmethod
    def analyze_complexity(self, ast: Any) -> ComplexityMetrics:
        """Analyze code complexity metrics."""
        pass
    
    @abstractmethod
    def find_dependencies(self, ast: Any) -> List[Dependency]:
        """Find code dependencies."""
        pass


class ITestGenerator(ABC):
    """Interface for test generators."""
    
    @abstractmethod
    def generate_tests(self, analysis: CodeAnalysis) -> TestSuite:
        """Generate comprehensive test suite from analysis."""
        pass
    
    @abstractmethod
    def generate_unit_tests(self, functions: List[FunctionInfo]) -> List[TestCase]:
        """Generate unit tests for functions."""
        pass
    
    @abstractmethod
    def generate_integration_tests(self, dependencies: List[Dependency]) -> List[TestCase]:
        """Generate integration tests with mocking strategies."""
        pass
    
    @abstractmethod
    def generate_edge_case_tests(self, edge_cases: List[EdgeCase]) -> List[TestCase]:
        """Generate edge case tests for boundary conditions."""
        pass
    
    @abstractmethod
    def format_tests(self, tests: List[TestCase], language: Language) -> str:
        """Format tests according to language-specific frameworks."""
        pass


class ICoverageAnalyzer(ABC):
    """Interface for coverage analyzers."""
    
    @abstractmethod
    def estimate_coverage(self, tests: TestSuite, code: str) -> CoverageReport:
        """Estimate test coverage for generated tests."""
        pass
    
    @abstractmethod
    def identify_gaps(self, coverage: CoverageReport) -> List[CoverageGap]:
        """Identify untested code paths and coverage gaps."""
        pass
    
    @abstractmethod
    def suggest_additional_tests(self, gaps: List[CoverageGap]) -> List[TestCase]:
        """Suggest additional test cases to improve coverage."""
        pass


class IConversationManager(ABC):
    """Interface for conversational refinement."""
    
    @abstractmethod
    def start_conversation(self, tests: TestSuite) -> None:
        """Start interactive conversation for test refinement."""
        pass
    
    @abstractmethod
    def process_feedback(self, feedback: str, context: Dict[str, Any]) -> TestSuite:
        """Process user feedback and update tests accordingly."""
        pass
    
    @abstractmethod
    def maintain_context(self, conversation_history: List[Dict[str, Any]]) -> None:
        """Preserve context across conversation turns."""
        pass


class IAIProvider(ABC):
    """Interface for AI providers."""
    
    @abstractmethod
    def enhance_test_case(self, test: TestCase, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enhance test case using AI analysis."""
        pass
    
    @abstractmethod
    def suggest_test_improvements(self, test: TestCase, context: Dict[str, Any]) -> str:
        """Get AI suggestions for test improvements."""
        pass
    
    @abstractmethod
    def analyze_code_patterns(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code patterns and suggest test strategies."""
        pass


class IIntegrationManager(ABC):
    """Interface for CI/CD integrations."""
    
    @abstractmethod
    def analyze_pr_changes(self, repo_info: Dict[str, str]) -> List[str]:
        """Analyze pull request changes and return modified files."""
        pass
    
    @abstractmethod
    def post_test_suggestions(self, repo_info: Dict[str, str], suggestions: Dict[str, Any]) -> None:
        """Post test suggestions to pull request."""
        pass
    
    @abstractmethod
    def create_workflow_file(self, output_path: str) -> str:
        """Generate CI/CD workflow file."""
        pass


class IConfigurationManager(ABC):
    """Interface for configuration management."""
    
    @abstractmethod
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file and environment."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration settings."""
        pass
    
    @abstractmethod
    def get_ai_provider_config(self) -> Dict[str, Any]:
        """Get AI provider configuration."""
        pass
    
    @abstractmethod
    def get_language_config(self, language: Language) -> Dict[str, Any]:
        """Get language-specific configuration."""
        pass


class ITestGeneratorAgent(ABC):
    """Interface for the main test generator agent."""
    
    @abstractmethod
    def process_file(self, file_path: str, language: Optional[str] = None, 
                    output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Process a code file and generate comprehensive test cases."""
        pass
    
    @abstractmethod
    def interactive_refinement(self) -> None:
        """Start interactive mode for test case refinement."""
        pass
    
    @abstractmethod
    def generate_coverage_report(self, tests: TestSuite) -> CoverageReport:
        """Generate coverage report for test suite."""
        pass


# Factory interfaces for creating language-specific implementations

class IAnalyzerFactory(ABC):
    """Factory for creating language-specific analyzers."""
    
    @abstractmethod
    def create_analyzer(self, language: Language) -> ICodeAnalyzer:
        """Create analyzer for specific language."""
        pass


class IGeneratorFactory(ABC):
    """Factory for creating language-specific generators."""
    
    @abstractmethod
    def create_generator(self, language: Language) -> ITestGenerator:
        """Create test generator for specific language."""
        pass


class IAIProviderFactory(ABC):
    """Factory for creating AI providers."""
    
    @abstractmethod
    def create_provider(self, provider_type: str, config: Dict[str, Any]) -> IAIProvider:
        """Create AI provider instance."""
        pass