"""
Coverage gap detection and reporting system for identifying untested code paths.
"""
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from src.interfaces.base_interfaces import (
    CoverageGap, TestCase, TestType, Language, FunctionInfo
)


class GapType(Enum):
    """Types of coverage gaps."""
    UNTESTED_FUNCTION = "untested_function"
    PARTIAL_COVERAGE = "partial_coverage"
    MISSING_EDGE_CASES = "missing_edge_cases"
    UNCOVERED_BRANCHES = "uncovered_branches"
    ERROR_HANDLING = "error_handling"


class GapSeverity(Enum):
    """Severity levels for coverage gaps."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DetailedCoverageGap(CoverageGap):
    """Extended coverage gap with additional metadata."""
    gap_type: GapType
    severity: GapSeverity
    confidence: float  # 0.0 to 1.0
    code_snippet: str
    suggested_test_types: List[TestType]
    priority: int  # 1-10, higher is more important


@dataclass
class CoverageMetrics:
    """Detailed coverage metrics."""
    total_lines: int
    executable_lines: int
    covered_lines: int
    uncovered_lines: int
    function_coverage: float
    branch_coverage: float
    statement_coverage: float
    complexity_weighted_coverage: float


@dataclass
class DetailedCoverageReport:
    """Enhanced coverage report with detailed metrics and analysis."""
    overall_percentage: float
    line_coverage: Dict[int, bool]
    untested_functions: List[str]
    coverage_gaps: List[DetailedCoverageGap]
    metrics: CoverageMetrics
    recommendations: List[str]
    improvement_suggestions: List[Dict[str, Any]]


class CoverageGapDetector:
    """
    Advanced coverage gap detection system that identifies untested code paths,
    analyzes coverage quality, and provides detailed improvement suggestions.
    """
    
    def __init__(self):
        """Initialize the coverage gap detector."""
        self._branch_patterns = {
            'python': [
                r'^\s*if\s+(.+):',
                r'^\s*elif\s+(.+):',
                r'^\s*else\s*:',
                r'^\s*for\s+.+\s+in\s+(.+):',
                r'^\s*while\s+(.+):',
                r'^\s*try\s*:',
                r'^\s*except\s+(.+):',
                r'^\s*finally\s*:',
                r'^\s*with\s+(.+):',
            ],
            'java': [
                r'^\s*if\s*\((.+)\)',
                r'^\s*else\s*{',
                r'^\s*for\s*\((.+)\)',
                r'^\s*while\s*\((.+)\)',
                r'^\s*try\s*{',
                r'^\s*catch\s*\((.+)\)',
                r'^\s*finally\s*{',
                r'^\s*switch\s*\((.+)\)',
                r'^\s*case\s+(.+):',
            ],
            'javascript': [
                r'^\s*if\s*\((.+)\)',
                r'^\s*else\s*{',
                r'^\s*for\s*\((.+)\)',
                r'^\s*while\s*\((.+)\)',
                r'^\s*try\s*{',
                r'^\s*catch\s*\((.+)\)',
                r'^\s*finally\s*{',
                r'^\s*switch\s*\((.+)\)',
                r'^\s*case\s+(.+):',
            ]
        }
        
        self._error_patterns = {
            'python': [
                r'raise\s+\w+',
                r'assert\s+',
                r'except\s+\w+',
                r'ValueError',
                r'TypeError',
                r'KeyError',
                r'IndexError',
            ],
            'java': [
                r'throw\s+new\s+\w+',
                r'throws\s+\w+',
                r'catch\s*\(\s*\w+',
                r'Exception',
                r'RuntimeException',
                r'IllegalArgumentException',
            ],
            'javascript': [
                r'throw\s+new\s+\w+',
                r'catch\s*\(\s*\w+',
                r'Error',
                r'TypeError',
                r'ReferenceError',
                r'RangeError',
            ]
        }
    
    def detect_coverage_gaps(self, code: str, language: str, 
                           covered_functions: Set[str], 
                           line_coverage: Dict[int, bool],
                           functions: List[FunctionInfo]) -> List[DetailedCoverageGap]:
        """
        Detect comprehensive coverage gaps in the code.
        
        Args:
            code: Source code to analyze
            language: Programming language
            covered_functions: Set of functions with test coverage
            line_coverage: Line-by-line coverage mapping
            functions: List of function information
            
        Returns:
            List of detailed coverage gaps with metadata
        """
        gaps = []
        code_lines = code.split('\n')
        
        # Detect untested functions
        gaps.extend(self._detect_untested_functions(
            functions, covered_functions, code_lines, language
        ))
        
        # Detect partial coverage gaps
        gaps.extend(self._detect_partial_coverage(
            functions, line_coverage, code_lines, language
        ))
        
        # Detect missing edge case coverage
        gaps.extend(self._detect_missing_edge_cases(
            code_lines, line_coverage, language
        ))
        
        # Detect uncovered branches
        gaps.extend(self._detect_uncovered_branches(
            code_lines, line_coverage, language
        ))
        
        # Detect missing error handling tests
        gaps.extend(self._detect_error_handling_gaps(
            code_lines, line_coverage, language
        ))
        
        # Sort gaps by priority and severity
        gaps.sort(key=lambda g: (g.severity.value, -g.priority, -g.confidence))
        
        return gaps
    
    def generate_detailed_report(self, code: str, language: str,
                               covered_functions: Set[str],
                               line_coverage: Dict[int, bool],
                               functions: List[FunctionInfo]) -> DetailedCoverageReport:
        """
        Generate a comprehensive coverage report with detailed metrics.
        
        Args:
            code: Source code to analyze
            language: Programming language
            covered_functions: Set of functions with test coverage
            line_coverage: Line-by-line coverage mapping
            functions: List of function information
            
        Returns:
            Detailed coverage report with metrics and recommendations
        """
        # Calculate detailed metrics
        metrics = self._calculate_detailed_metrics(
            code, line_coverage, functions, covered_functions
        )
        
        # Detect coverage gaps
        gaps = self.detect_coverage_gaps(
            code, language, covered_functions, line_coverage, functions
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(gaps, metrics)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(gaps)
        
        # Calculate overall percentage
        overall_percentage = (metrics.covered_lines / metrics.executable_lines * 100) \
                           if metrics.executable_lines > 0 else 0.0
        
        return DetailedCoverageReport(
            overall_percentage=overall_percentage,
            line_coverage=line_coverage,
            untested_functions=list(set(f.name for f in functions) - covered_functions),
            coverage_gaps=gaps,
            metrics=metrics,
            recommendations=recommendations,
            improvement_suggestions=improvement_suggestions
        )
    
    def suggest_test_improvements(self, gaps: List[DetailedCoverageGap]) -> List[TestCase]:
        """
        Generate specific test case suggestions to address coverage gaps.
        
        Args:
            gaps: List of coverage gaps to address
            
        Returns:
            List of suggested test cases
        """
        suggested_tests = []
        
        for gap in gaps:
            test_cases = self._generate_gap_specific_tests(gap)
            suggested_tests.extend(test_cases)
        
        return suggested_tests
    
    def _detect_untested_functions(self, functions: List[FunctionInfo],
                                 covered_functions: Set[str],
                                 code_lines: List[str],
                                 language: str) -> List[DetailedCoverageGap]:
        """Detect functions with no test coverage."""
        gaps = []
        
        for func in functions:
            if func.name not in covered_functions:
                # Extract code snippet
                start_line, end_line = func.line_range
                code_snippet = '\n'.join(code_lines[start_line-1:end_line])
                
                # Determine severity based on function complexity
                severity = GapSeverity.CRITICAL if func.complexity > 10 else \
                          GapSeverity.HIGH if func.complexity > 5 else \
                          GapSeverity.MEDIUM
                
                gap = DetailedCoverageGap(
                    function_name=func.name,
                    line_range=func.line_range,
                    description=f"Function '{func.name}' has no test coverage",
                    suggested_tests=[
                        f"Add unit test for {func.name}",
                        f"Test edge cases for {func.name}",
                        f"Test error handling in {func.name}"
                    ],
                    gap_type=GapType.UNTESTED_FUNCTION,
                    severity=severity,
                    confidence=1.0,
                    code_snippet=code_snippet,
                    suggested_test_types=[TestType.UNIT, TestType.EDGE],
                    priority=10 if severity == GapSeverity.CRITICAL else 8
                )
                gaps.append(gap)
        
        return gaps
    
    def _detect_partial_coverage(self, functions: List[FunctionInfo],
                               line_coverage: Dict[int, bool],
                               code_lines: List[str],
                               language: str) -> List[DetailedCoverageGap]:
        """Detect functions with partial coverage."""
        gaps = []
        
        for func in functions:
            start_line, end_line = func.line_range
            func_lines = list(range(start_line, end_line + 1))
            
            # Count covered vs uncovered lines in function
            covered_count = sum(1 for line_num in func_lines 
                              if line_coverage.get(line_num, False))
            total_count = len(func_lines)
            
            if total_count > 0:
                coverage_ratio = covered_count / total_count
                
                # Flag functions with partial coverage (20-80%)
                if 0.2 <= coverage_ratio <= 0.8:
                    uncovered_lines = [line_num for line_num in func_lines 
                                     if not line_coverage.get(line_num, False)]
                    
                    code_snippet = '\n'.join(code_lines[start_line-1:end_line])
                    
                    severity = GapSeverity.HIGH if coverage_ratio < 0.5 else GapSeverity.MEDIUM
                    
                    gap = DetailedCoverageGap(
                        function_name=func.name,
                        line_range=(min(uncovered_lines), max(uncovered_lines)),
                        description=f"Function '{func.name}' has partial coverage ({coverage_ratio:.1%})",
                        suggested_tests=[
                            f"Add tests for uncovered branches in {func.name}",
                            f"Test additional scenarios in {func.name}"
                        ],
                        gap_type=GapType.PARTIAL_COVERAGE,
                        severity=severity,
                        confidence=0.8,
                        code_snippet=code_snippet,
                        suggested_test_types=[TestType.UNIT, TestType.EDGE],
                        priority=7 if severity == GapSeverity.HIGH else 5
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _detect_missing_edge_cases(self, code_lines: List[str],
                                 line_coverage: Dict[int, bool],
                                 language: str) -> List[DetailedCoverageGap]:
        """Detect potential edge cases that lack test coverage."""
        gaps = []
        edge_case_patterns = {
            'python': [
                (r'if\s+.*\bnot\b\s+', 'Negative condition check'),
                (r'if\s+.*\blen\(.*\)\s*==\s*0', 'Empty collection check'),
                (r'if\s+.*\bis\s+None', 'None value check'),
                (r'if\s+.*<\s*0', 'Negative value check'),
                (r'if\s+.*>\s*\d+', 'Upper bound check'),
            ],
            'java': [
                (r'if\s*\(.*==\s*null\)', 'Null value check'),
                (r'if\s*\(.*\.isEmpty\(\)', 'Empty collection check'),
                (r'if\s*\(.*<\s*0\)', 'Negative value check'),
                (r'if\s*\(.*>\s*\d+\)', 'Upper bound check'),
            ],
            'javascript': [
                (r'if\s*\(.*===\s*null\)', 'Null value check'),
                (r'if\s*\(.*===\s*undefined\)', 'Undefined value check'),
                (r'if\s*\(.*\.length\s*===\s*0\)', 'Empty array check'),
                (r'if\s*\(.*<\s*0\)', 'Negative value check'),
            ]
        }
        
        patterns = edge_case_patterns.get(language, [])
        
        for i, line in enumerate(code_lines, 1):
            if not line_coverage.get(i, False):
                for pattern, description in patterns:
                    if re.search(pattern, line):
                        gap = DetailedCoverageGap(
                            function_name="unknown",
                            line_range=(i, i),
                            description=f"Uncovered edge case: {description}",
                            suggested_tests=[f"Add test for {description.lower()}"],
                            gap_type=GapType.MISSING_EDGE_CASES,
                            severity=GapSeverity.MEDIUM,
                            confidence=0.7,
                            code_snippet=line.strip(),
                            suggested_test_types=[TestType.EDGE],
                            priority=6
                        )
                        gaps.append(gap)
        
        return gaps
    
    def _detect_uncovered_branches(self, code_lines: List[str],
                                 line_coverage: Dict[int, bool],
                                 language: str) -> List[DetailedCoverageGap]:
        """Detect uncovered conditional branches."""
        gaps = []
        branch_patterns = self._branch_patterns.get(language, [])
        
        for i, line in enumerate(code_lines, 1):
            if not line_coverage.get(i, False):
                for pattern in branch_patterns:
                    if re.search(pattern, line):
                        gap = DetailedCoverageGap(
                            function_name="unknown",
                            line_range=(i, i),
                            description=f"Uncovered branch condition",
                            suggested_tests=["Add test for this branch condition"],
                            gap_type=GapType.UNCOVERED_BRANCHES,
                            severity=GapSeverity.MEDIUM,
                            confidence=0.8,
                            code_snippet=line.strip(),
                            suggested_test_types=[TestType.UNIT, TestType.EDGE],
                            priority=6
                        )
                        gaps.append(gap)
                        break
        
        return gaps
    
    def _detect_error_handling_gaps(self, code_lines: List[str],
                                  line_coverage: Dict[int, bool],
                                  language: str) -> List[DetailedCoverageGap]:
        """Detect missing error handling test coverage."""
        gaps = []
        error_patterns = self._error_patterns.get(language, [])
        
        for i, line in enumerate(code_lines, 1):
            if not line_coverage.get(i, False):
                for pattern in error_patterns:
                    if re.search(pattern, line):
                        gap = DetailedCoverageGap(
                            function_name="unknown",
                            line_range=(i, i),
                            description=f"Uncovered error handling code",
                            suggested_tests=["Add test for error handling scenario"],
                            gap_type=GapType.ERROR_HANDLING,
                            severity=GapSeverity.HIGH,
                            confidence=0.9,
                            code_snippet=line.strip(),
                            suggested_test_types=[TestType.EDGE],
                            priority=8
                        )
                        gaps.append(gap)
                        break
        
        return gaps
    
    def _calculate_detailed_metrics(self, code: str, line_coverage: Dict[int, bool],
                                  functions: List[FunctionInfo],
                                  covered_functions: Set[str]) -> CoverageMetrics:
        """Calculate detailed coverage metrics."""
        code_lines = code.split('\n')
        total_lines = len(code_lines)
        
        # Count executable lines (non-empty, non-comment)
        executable_lines = sum(1 for line in code_lines 
                             if line.strip() and not line.strip().startswith('#'))
        
        # Count covered lines
        covered_lines = sum(1 for is_covered in line_coverage.values() if is_covered)
        uncovered_lines = executable_lines - covered_lines
        
        # Calculate function coverage
        total_functions = len(functions)
        covered_function_count = len(covered_functions)
        function_coverage = (covered_function_count / total_functions * 100) \
                          if total_functions > 0 else 0.0
        
        # Estimate branch coverage (simplified)
        branch_coverage = min(function_coverage * 0.8, 100.0)  # Rough estimate
        
        # Calculate statement coverage
        statement_coverage = (covered_lines / executable_lines * 100) \
                           if executable_lines > 0 else 0.0
        
        # Calculate complexity-weighted coverage
        total_complexity = sum(f.complexity for f in functions)
        covered_complexity = sum(f.complexity for f in functions 
                               if f.name in covered_functions)
        complexity_weighted_coverage = (covered_complexity / total_complexity * 100) \
                                     if total_complexity > 0 else 0.0
        
        return CoverageMetrics(
            total_lines=total_lines,
            executable_lines=executable_lines,
            covered_lines=covered_lines,
            uncovered_lines=uncovered_lines,
            function_coverage=function_coverage,
            branch_coverage=branch_coverage,
            statement_coverage=statement_coverage,
            complexity_weighted_coverage=complexity_weighted_coverage
        )
    
    def _generate_recommendations(self, gaps: List[DetailedCoverageGap],
                                metrics: CoverageMetrics) -> List[str]:
        """Generate coverage improvement recommendations."""
        recommendations = []
        
        # Overall coverage recommendations
        if metrics.statement_coverage < 80:
            recommendations.append(
                f"Statement coverage is {metrics.statement_coverage:.1f}%. "
                f"Aim for at least 80% coverage."
            )
        
        if metrics.function_coverage < 90:
            recommendations.append(
                f"Function coverage is {metrics.function_coverage:.1f}%. "
                f"Consider adding tests for untested functions."
            )
        
        # Gap-specific recommendations
        critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
        if critical_gaps:
            recommendations.append(
                f"Found {len(critical_gaps)} critical coverage gaps. "
                f"Prioritize testing these areas."
            )
        
        high_gaps = [g for g in gaps if g.severity == GapSeverity.HIGH]
        if high_gaps:
            recommendations.append(
                f"Found {len(high_gaps)} high-priority coverage gaps. "
                f"Consider adding tests for better coverage."
            )
        
        # Edge case recommendations
        edge_gaps = [g for g in gaps if g.gap_type == GapType.MISSING_EDGE_CASES]
        if edge_gaps:
            recommendations.append(
                f"Found {len(edge_gaps)} potential edge cases without tests. "
                f"Add edge case testing to improve robustness."
            )
        
        return recommendations
    
    def _generate_improvement_suggestions(self, gaps: List[DetailedCoverageGap]) -> List[Dict[str, Any]]:
        """Generate specific improvement suggestions."""
        suggestions = []
        
        # Group gaps by type for better suggestions
        gap_groups = {}
        for gap in gaps:
            gap_type = gap.gap_type.value
            if gap_type not in gap_groups:
                gap_groups[gap_type] = []
            gap_groups[gap_type].append(gap)
        
        for gap_type, type_gaps in gap_groups.items():
            suggestion = {
                'type': gap_type,
                'count': len(type_gaps),
                'priority': max(g.priority for g in type_gaps),
                'description': self._get_gap_type_description(gap_type),
                'action_items': self._get_gap_type_actions(gap_type, type_gaps)
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_gap_specific_tests(self, gap: DetailedCoverageGap) -> List[TestCase]:
        """Generate specific test cases for a coverage gap."""
        test_cases = []
        
        for i, suggestion in enumerate(gap.suggested_tests):
            test_name = f"test_{gap.function_name}_{gap.gap_type.value}_{i+1}"
            
            # Generate basic test template based on gap type
            test_code = self._generate_test_template(gap, suggestion)
            
            test_case = TestCase(
                name=test_name,
                test_type=gap.suggested_test_types[0] if gap.suggested_test_types else TestType.UNIT,
                function_name=gap.function_name,
                description=f"Test to address {gap.gap_type.value}: {suggestion}",
                test_code=test_code,
                requirements_covered=[f"Coverage gap: {gap.description}"]
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_test_template(self, gap: DetailedCoverageGap, suggestion: str) -> str:
        """Generate a test template for a specific gap."""
        if gap.gap_type == GapType.UNTESTED_FUNCTION:
            return f"""
def test_{gap.function_name}():
    \"\"\"Test for {gap.function_name} - {suggestion}\"\"\"
    # TODO: Implement test for {gap.function_name}
    # Gap: {gap.description}
    # Lines: {gap.line_range[0]}-{gap.line_range[1]}
    pass
"""
        elif gap.gap_type == GapType.MISSING_EDGE_CASES:
            return f"""
def test_{gap.function_name}_edge_case():
    \"\"\"Test edge case - {suggestion}\"\"\"
    # TODO: Test edge case scenario
    # Code: {gap.code_snippet}
    pass
"""
        elif gap.gap_type == GapType.ERROR_HANDLING:
            return f"""
def test_{gap.function_name}_error_handling():
    \"\"\"Test error handling - {suggestion}\"\"\"
    # TODO: Test error handling scenario
    # Code: {gap.code_snippet}
    with pytest.raises(Exception):
        pass
"""
        else:
            return f"""
def test_{gap.function_name}_coverage_gap():
    \"\"\"Test to address coverage gap - {suggestion}\"\"\"
    # TODO: Implement test
    # Gap type: {gap.gap_type.value}
    # Description: {gap.description}
    pass
"""
    
    def _get_gap_type_description(self, gap_type: str) -> str:
        """Get description for gap type."""
        descriptions = {
            'untested_function': 'Functions without any test coverage',
            'partial_coverage': 'Functions with incomplete test coverage',
            'missing_edge_cases': 'Edge cases that lack test coverage',
            'uncovered_branches': 'Conditional branches without tests',
            'error_handling': 'Error handling code without tests'
        }
        return descriptions.get(gap_type, 'Unknown gap type')
    
    def _get_gap_type_actions(self, gap_type: str, gaps: List[DetailedCoverageGap]) -> List[str]:
        """Get action items for gap type."""
        actions = {
            'untested_function': [
                'Add unit tests for each untested function',
                'Focus on functions with high complexity first',
                'Include both positive and negative test cases'
            ],
            'partial_coverage': [
                'Identify uncovered code paths in partially tested functions',
                'Add tests for missing branches and conditions',
                'Review existing tests for completeness'
            ],
            'missing_edge_cases': [
                'Add tests for boundary conditions',
                'Test null/undefined/empty value scenarios',
                'Include error condition testing'
            ],
            'uncovered_branches': [
                'Add tests for each conditional branch',
                'Test both true and false conditions',
                'Include nested condition scenarios'
            ],
            'error_handling': [
                'Add tests for exception scenarios',
                'Test error message accuracy',
                'Verify proper error recovery'
            ]
        }
        return actions.get(gap_type, ['Review and add appropriate tests'])