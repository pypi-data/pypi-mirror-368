"""
Coverage analysis engine for estimating test coverage and identifying gaps.
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from src.interfaces.base_interfaces import (
    ICoverageAnalyzer, TestSuite, TestCase, CoverageReport, CoverageGap,
    FunctionInfo, TestType
)
from src.analyzers.coverage_gap_detector import (
    CoverageGapDetector, DetailedCoverageReport, DetailedCoverageGap
)


@dataclass
class LineInfo:
    """Information about a line of code."""
    line_number: int
    content: str
    is_executable: bool
    function_name: Optional[str] = None
    is_covered: bool = False


class CoverageAnalyzer(ICoverageAnalyzer):
    """
    Analyzes test coverage by mapping test cases to code lines and functions.
    Provides coverage estimation and gap identification.
    """
    
    def __init__(self):
        """Initialize the coverage analyzer."""
        self.gap_detector = CoverageGapDetector()
        self._executable_patterns = {
            'python': [
                r'^\s*def\s+\w+',  # Function definitions
                r'^\s*class\s+\w+',  # Class definitions
                r'^\s*if\s+',  # If statements
                r'^\s*elif\s+',  # Elif statements
                r'^\s*else\s*:',  # Else statements
                r'^\s*for\s+',  # For loops
                r'^\s*while\s+',  # While loops
                r'^\s*try\s*:',  # Try blocks
                r'^\s*except\s+',  # Except blocks
                r'^\s*finally\s*:',  # Finally blocks
                r'^\s*with\s+',  # With statements
                r'^\s*return\s+',  # Return statements
                r'^\s*yield\s+',  # Yield statements
                r'^\s*raise\s+',  # Raise statements
                r'^\s*assert\s+',  # Assert statements
                r'^\s*\w+\s*=',  # Assignments
                r'^\s*\w+\(',  # Function calls
            ],
            'java': [
                r'^\s*public\s+',  # Public methods/fields
                r'^\s*private\s+',  # Private methods/fields
                r'^\s*protected\s+',  # Protected methods/fields
                r'^\s*if\s*\(',  # If statements
                r'^\s*else\s*{',  # Else statements
                r'^\s*for\s*\(',  # For loops
                r'^\s*while\s*\(',  # While loops
                r'^\s*try\s*{',  # Try blocks
                r'^\s*catch\s*\(',  # Catch blocks
                r'^\s*finally\s*{',  # Finally blocks
                r'^\s*return\s+',  # Return statements
                r'^\s*throw\s+',  # Throw statements
                r'^\s*\w+\s*=',  # Assignments
                r'^\s*\w+\(',  # Method calls
            ],
            'javascript': [
                r'^\s*function\s+\w+',  # Function declarations
                r'^\s*const\s+\w+\s*=\s*\(',  # Arrow functions
                r'^\s*let\s+\w+\s*=\s*\(',  # Arrow functions
                r'^\s*var\s+\w+\s*=\s*\(',  # Arrow functions
                r'^\s*if\s*\(',  # If statements
                r'^\s*else\s*{',  # Else statements
                r'^\s*for\s*\(',  # For loops
                r'^\s*while\s*\(',  # While loops
                r'^\s*try\s*{',  # Try blocks
                r'^\s*catch\s*\(',  # Catch blocks
                r'^\s*finally\s*{',  # Finally blocks
                r'^\s*return\s+',  # Return statements
                r'^\s*throw\s+',  # Throw statements
                r'^\s*\w+\s*=',  # Assignments
                r'^\s*\w+\(',  # Function calls
            ]
        }
        
        self._comment_patterns = {
            'python': [r'^\s*#', r'^\s*"""', r"^\s*'''"],
            'java': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'javascript': [r'^\s*//', r'^\s*/\*', r'^\s*\*']
        }
    
    def estimate_coverage(self, tests: TestSuite, code: str) -> CoverageReport:
        """
        Estimate test coverage for generated tests.
        
        Args:
            tests: Test suite containing generated test cases
            code: Source code to analyze coverage for
            
        Returns:
            CoverageReport with coverage metrics and line-by-line analysis
        """
        # Parse code into lines with metadata
        lines = self._parse_code_lines(code, tests.language.value)
        
        # Map test cases to covered functions and lines
        covered_functions = self._map_test_coverage(tests, lines)
        
        # Calculate line coverage
        line_coverage = self._calculate_line_coverage(lines, covered_functions)
        
        # Identify untested functions
        untested_functions = self._identify_untested_functions(lines, covered_functions)
        
        # Calculate overall coverage percentage
        executable_lines = sum(1 for line in lines if line.is_executable)
        covered_lines = sum(1 for line in lines if line.is_executable and line.is_covered)
        overall_percentage = (covered_lines / executable_lines * 100) if executable_lines > 0 else 0.0
        
        # Identify coverage gaps
        coverage_gaps = self._identify_coverage_gaps(lines, untested_functions)
        
        return CoverageReport(
            overall_percentage=overall_percentage,
            line_coverage=line_coverage,
            untested_functions=untested_functions,
            coverage_gaps=coverage_gaps
        )
    
    def identify_gaps(self, coverage: CoverageReport) -> List[CoverageGap]:
        """
        Identify untested code paths and coverage gaps.
        
        Args:
            coverage: Coverage report to analyze
            
        Returns:
            List of identified coverage gaps
        """
        return coverage.coverage_gaps
    
    def suggest_additional_tests(self, gaps: List[CoverageGap]) -> List[TestCase]:
        """
        Suggest additional test cases to improve coverage.
        
        Args:
            gaps: List of coverage gaps to address
            
        Returns:
            List of suggested test cases
        """
        suggested_tests = []
        
        for gap in gaps:
            # Create basic test case suggestions for each gap
            test_case = TestCase(
                name=f"test_{gap.function_name}_coverage_gap",
                test_type=TestType.UNIT,
                function_name=gap.function_name,
                description=f"Test to cover gap: {gap.description}",
                test_code=self._generate_basic_test_template(gap),
                requirements_covered=[f"Coverage gap at lines {gap.line_range[0]}-{gap.line_range[1]}"]
            )
            suggested_tests.append(test_case)
        
        return suggested_tests
    
    def generate_detailed_coverage_report(self, tests: TestSuite, code: str, 
                                        functions: List[FunctionInfo]) -> DetailedCoverageReport:
        """
        Generate a comprehensive coverage report with detailed gap analysis.
        
        Args:
            tests: Test suite containing generated test cases
            code: Source code to analyze coverage for
            functions: List of function information from code analysis
            
        Returns:
            DetailedCoverageReport with comprehensive metrics and recommendations
        """
        # Parse code into lines with metadata
        lines = self._parse_code_lines(code, tests.language.value)
        
        # Map test cases to covered functions and lines
        covered_functions = self._map_test_coverage(tests, lines)
        
        # Calculate line coverage
        line_coverage = self._calculate_line_coverage(lines, covered_functions)
        
        # Use gap detector for comprehensive analysis
        return self.gap_detector.generate_detailed_report(
            code, tests.language.value, covered_functions, line_coverage, functions
        )
    
    def detect_advanced_gaps(self, tests: TestSuite, code: str, 
                           functions: List[FunctionInfo]) -> List[DetailedCoverageGap]:
        """
        Detect advanced coverage gaps using the gap detector.
        
        Args:
            tests: Test suite containing generated test cases
            code: Source code to analyze
            functions: List of function information
            
        Returns:
            List of detailed coverage gaps
        """
        # Parse code and calculate coverage
        lines = self._parse_code_lines(code, tests.language.value)
        covered_functions = self._map_test_coverage(tests, lines)
        line_coverage = self._calculate_line_coverage(lines, covered_functions)
        
        # Use gap detector for advanced analysis
        return self.gap_detector.detect_coverage_gaps(
            code, tests.language.value, covered_functions, line_coverage, functions
        )
    
    def suggest_improved_tests(self, gaps: List[DetailedCoverageGap]) -> List[TestCase]:
        """
        Generate improved test suggestions using the gap detector.
        
        Args:
            gaps: List of detailed coverage gaps
            
        Returns:
            List of improved test case suggestions
        """
        return self.gap_detector.suggest_test_improvements(gaps)
    
    def _parse_code_lines(self, code: str, language: str) -> List[LineInfo]:
        """Parse code into lines with executable metadata."""
        lines = []
        code_lines = code.split('\n')
        current_function = None
        
        executable_patterns = self._executable_patterns.get(language, [])
        comment_patterns = self._comment_patterns.get(language, [])
        
        for i, line in enumerate(code_lines, 1):
            # Check if line is a comment or empty
            is_comment = any(re.match(pattern, line) for pattern in comment_patterns)
            is_empty = line.strip() == ''
            
            # Check if line is executable
            is_executable = False
            if not is_comment and not is_empty:
                is_executable = any(re.match(pattern, line) for pattern in executable_patterns)
            
            # Track current function context
            if language == 'python' and re.match(r'^\s*def\s+(\w+)', line):
                match = re.match(r'^\s*def\s+(\w+)', line)
                current_function = match.group(1) if match else None
            elif language == 'java' and re.search(r'\b(\w+)\s*\([^)]*\)\s*{', line):
                match = re.search(r'\b(\w+)\s*\([^)]*\)\s*{', line)
                current_function = match.group(1) if match else None
            elif language == 'javascript' and re.match(r'^\s*function\s+(\w+)', line):
                match = re.match(r'^\s*function\s+(\w+)', line)
                current_function = match.group(1) if match else None
            
            lines.append(LineInfo(
                line_number=i,
                content=line,
                is_executable=is_executable,
                function_name=current_function
            ))
        
        return lines
    
    def _map_test_coverage(self, tests: TestSuite, lines: List[LineInfo]) -> Set[str]:
        """Map test cases to covered functions."""
        covered_functions = set()
        
        for test_case in tests.test_cases:
            # Extract function name from test case
            if test_case.function_name:
                covered_functions.add(test_case.function_name)
            
            # Also try to extract from test name patterns
            test_name = test_case.name.lower()
            for line in lines:
                if line.function_name and line.function_name.lower() in test_name:
                    covered_functions.add(line.function_name)
        
        return covered_functions
    
    def _calculate_line_coverage(self, lines: List[LineInfo], covered_functions: Set[str]) -> Dict[int, bool]:
        """Calculate line-by-line coverage mapping."""
        line_coverage = {}
        
        for line in lines:
            if line.is_executable:
                # Mark line as covered if it's in a tested function
                is_covered = line.function_name in covered_functions if line.function_name else False
                line.is_covered = is_covered
                line_coverage[line.line_number] = is_covered
        
        return line_coverage
    
    def _identify_untested_functions(self, lines: List[LineInfo], covered_functions: Set[str]) -> List[str]:
        """Identify functions that have no test coverage."""
        all_functions = set()
        
        for line in lines:
            if line.function_name:
                all_functions.add(line.function_name)
        
        return list(all_functions - covered_functions)
    
    def _identify_coverage_gaps(self, lines: List[LineInfo], untested_functions: List[str]) -> List[CoverageGap]:
        """Identify specific coverage gaps in the code."""
        gaps = []
        
        # Group lines by function to identify gaps
        function_lines = {}
        for line in lines:
            if line.function_name:
                if line.function_name not in function_lines:
                    function_lines[line.function_name] = []
                function_lines[line.function_name].append(line)
        
        # Create gaps for untested functions
        for func_name in untested_functions:
            if func_name in function_lines:
                func_lines = function_lines[func_name]
                executable_lines = [l for l in func_lines if l.is_executable]
                
                if executable_lines:
                    start_line = min(l.line_number for l in executable_lines)
                    end_line = max(l.line_number for l in executable_lines)
                    
                    gap = CoverageGap(
                        function_name=func_name,
                        line_range=(start_line, end_line),
                        description=f"Function '{func_name}' has no test coverage",
                        suggested_tests=[
                            f"Add unit test for {func_name}",
                            f"Test edge cases for {func_name}",
                            f"Test error handling in {func_name}"
                        ]
                    )
                    gaps.append(gap)
        
        # Identify partially covered functions
        for func_name, func_lines in function_lines.items():
            if func_name not in untested_functions:
                executable_lines = [l for l in func_lines if l.is_executable]
                uncovered_lines = [l for l in executable_lines if not l.is_covered]
                
                if uncovered_lines and len(uncovered_lines) > len(executable_lines) * 0.3:  # >30% uncovered
                    start_line = min(l.line_number for l in uncovered_lines)
                    end_line = max(l.line_number for l in uncovered_lines)
                    
                    gap = CoverageGap(
                        function_name=func_name,
                        line_range=(start_line, end_line),
                        description=f"Function '{func_name}' has partial coverage - {len(uncovered_lines)} uncovered lines",
                        suggested_tests=[
                            f"Add tests for uncovered branches in {func_name}",
                            f"Test additional scenarios in {func_name}"
                        ]
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _generate_basic_test_template(self, gap: CoverageGap) -> str:
        """Generate a basic test template for a coverage gap."""
        return f"""
def test_{gap.function_name}_gap():
    \"\"\"Test to address coverage gap: {gap.description}\"\"\"
    # TODO: Implement test for {gap.function_name}
    # Lines {gap.line_range[0]}-{gap.line_range[1]} need coverage
    pass
"""