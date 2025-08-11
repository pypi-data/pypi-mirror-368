"""
Build a CodeAnalysis by combining existing analyzers.
"""
from __future__ import annotations

from typing import Optional

from ..interfaces.base_interfaces import CodeAnalysis
from .code_parser import CodeParser
from .function_analyzer import FunctionAnalyzer
from .class_analyzer import ClassAnalyzer
from .edge_case_detector import EdgeCaseDetector
from .dependency_analyzer import DependencyAnalyzer
from .complexity_analyzer import ComplexityAnalyzer


class AnalysisOrchestrator:
    """High-level API to produce a CodeAnalysis from code+language."""

    def __init__(self,
                 parser: Optional[CodeParser] = None,
                 func_analyzer: Optional[FunctionAnalyzer] = None,
                 class_analyzer: Optional[ClassAnalyzer] = None,
                 edge_detector: Optional[EdgeCaseDetector] = None,
                 dep_analyzer: Optional[DependencyAnalyzer] = None,
                 complexity_analyzer: Optional[ComplexityAnalyzer] = None):
        self.parser = parser or CodeParser()
        self.func_analyzer = func_analyzer or FunctionAnalyzer(self.parser)
        self.class_analyzer = class_analyzer or ClassAnalyzer(self.parser)
        self.edge_detector = edge_detector or EdgeCaseDetector()
        self.dep_analyzer = dep_analyzer or DependencyAnalyzer()
        self.complexity_analyzer = complexity_analyzer or ComplexityAnalyzer()

    def analyze(self, code: str, language: str) -> CodeAnalysis:
        functions = self.func_analyzer.analyze_functions(code, language)
        classes = self.class_analyzer.analyze_classes(code, language)
        edge_cases = self.edge_detector.detect(code, language)
        dependencies = self.dep_analyzer.detect(code, language)
        complexity = self.complexity_analyzer.analyze(code)

        return CodeAnalysis(
            language=language,
            functions=functions,
            classes=classes,
            edge_cases=edge_cases,
            dependencies=dependencies,
            complexity_metrics=complexity,
        )
