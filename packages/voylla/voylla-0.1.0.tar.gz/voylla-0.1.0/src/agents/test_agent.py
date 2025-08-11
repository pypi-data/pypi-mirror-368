"""
Test Generator Agent - AI-powered test case generation and refinement
"""
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

from src.analyzers.code_analyzer import CodeAnalyzer, AnalysisResult
from src.generators.test_generator import TestGenerator, TestCase
from src.config.configuration_manager import ConfigurationManager
from src.interfaces.base_interfaces import ITestGeneratorAgent, ICodeAnalyzer, ITestGenerator, IAIProvider

console = Console()

class TestGeneratorAgent(ITestGeneratorAgent):
    """AI agent that orchestrates code analysis and test generation."""
    
    def __init__(self, analyzer: ICodeAnalyzer, generator: ITestGenerator, 
                 config_manager: ConfigurationManager, ai_provider: IAIProvider):
        self.analyzer = analyzer
        self.generator = generator
        self.config_manager = config_manager
        self.ai_provider = ai_provider
        self.current_analysis: Optional[AnalysisResult] = None
        self.current_tests: List[TestCase] = []
    
    def _get_ai_provider_info(self) -> str:
        """Get information about the current AI provider."""
        provider_type = self.config_manager.get_preferred_ai_provider()
        ai_config = self.config_manager.get_ai_provider_config()
        
        if provider_type == 'openai':
            return f"OpenAI {ai_config['openai_model']}"
        elif provider_type == 'anthropic':
            return f"Anthropic {ai_config['anthropic_model']}"
        else:
            return "Mock (no API key configured)"
    
    def process_file(self, file_path: str, language: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Process a code file and generate comprehensive test cases."""
        
        # Step 1: Analyze the code
        console.print("[yellow]🔍 Analyzing code structure and flow...[/yellow]")
        self.current_analysis = self.analyzer.analyze_file(file_path, language)
        
        # Step 2: Display analysis results
        self._display_analysis_summary()
        
        # Step 3: Generate initial test cases
        console.print("[yellow]🧪 Generating test cases...[/yellow]")
        generated = self.generator.generate_tests(self.current_analysis)
        # Support generators that return a TestSuite or a raw list
        try:
            # Prefer attribute access to avoid import cycles
            test_cases = getattr(generated, 'test_cases', None)
            self.current_tests = list(test_cases) if test_cases is not None else list(generated)
        except TypeError:
            # Fallback if generated is not iterable
            self.current_tests = []
        # Final safety: coerce any remaining container into a list of tests
        if not isinstance(self.current_tests, list) and hasattr(self.current_tests, 'test_cases'):
            try:
                self.current_tests = list(getattr(self.current_tests, 'test_cases'))
            except Exception:
                self.current_tests = []
        
        # Step 4: Enhance tests with AI insights
        console.print("[yellow]🤖 Enhancing tests with AI insights...[/yellow]")
        self._enhance_tests_with_ai()
        
        # Step 5: Generate coverage report
        coverage_percentage = self._calculate_coverage()
        
        # Step 6: Save generated tests
        if output_dir:
            self._save_tests(output_dir)
        
        return {
            'test_count': len(self.current_tests),
            'coverage_percentage': coverage_percentage,
            'analysis': self.current_analysis,
            'tests': self.current_tests
        }
    
    def _display_analysis_summary(self):
        """Display code analysis summary."""
        if not self.current_analysis:
            return
        
        # Create analysis summary table
        table = Table(title="Code Analysis Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Language", self.current_analysis.language)
        table.add_row("Functions Found", str(len(self.current_analysis.functions)))
        table.add_row("Classes Found", str(len(self.current_analysis.classes)))
        table.add_row("Complexity Score", str(self.current_analysis.complexity_score))
        table.add_row("Edge Cases Detected", str(len(self.current_analysis.edge_cases)))
        table.add_row("Performance Risks", str(len(self.current_analysis.performance_risks)))
        
        console.print(table)
        
        # Display detected issues
        if self.current_analysis.edge_cases:
            console.print("\n[yellow]⚠️  Detected Edge Cases:[/yellow]")
            for edge_case in self.current_analysis.edge_cases:
                console.print(f"  • {edge_case}")
        
        if self.current_analysis.performance_risks:
            console.print("\n[red]🚨 Performance Risks:[/red]")
            for risk in self.current_analysis.performance_risks:
                console.print(f"  • {risk}")
    
    def _enhance_tests_with_ai(self):
        """Use AI to enhance generated test cases."""
        if not self.current_analysis or not self.current_tests:
            return
        
        # Prepare context for AI
        context = self._prepare_ai_context()
        
        # Get AI suggestions for each test
        for test in self.current_tests:
            enhanced_test = self.ai_provider.enhance_test_case(test, context)
            if enhanced_test:
                test.test_code = enhanced_test.get('code', test.test_code)
                test.description = enhanced_test.get('description', test.description)
                if enhanced_test.get('assertions'):
                    test.assertions = enhanced_test['assertions']
    
    def _prepare_ai_context(self) -> Dict[str, Any]:
        """Prepare context for AI enhancement."""
        return {
            'language': self.current_analysis.language,
            'functions': [
                {
                    'name': f.name,
                    'args': f.args,
                    'complexity': f.complexity,
                    'docstring': f.docstring
                }
                for f in self.current_analysis.functions
            ],
            'edge_cases': self.current_analysis.edge_cases,
            'performance_risks': self.current_analysis.performance_risks,
            'imports': self.current_analysis.imports
        }
    
    def _calculate_coverage(self) -> float:
        """Calculate estimated test coverage."""
        if not self.current_analysis or not self.current_tests:
            return 0.0
        
        total_functions = len(self.current_analysis.functions)
        if total_functions == 0:
            return 100.0
        
        covered_functions = set()
        for test in self.current_tests:
            covered_functions.add(test.function_name)
        
        return (len(covered_functions) / total_functions) * 100
    
    def _save_tests(self, output_dir: str):
        """Save generated tests to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Group tests by function
        tests_by_function = {}
        for test in self.current_tests:
            if test.function_name not in tests_by_function:
                tests_by_function[test.function_name] = []
            tests_by_function[test.function_name].append(test)
        
        # Generate test files
        for function_name, tests in tests_by_function.items():
            filename = f"test_{function_name}.{self._get_test_file_extension()}"
            filepath = output_path / filename
            
            with open(filepath, 'w') as f:
                f.write(self._generate_test_file_header())
                for test in tests:
                    f.write(f"\n{test.test_code}\n")
            
            console.print(f"[green]✓ Generated {filepath}[/green]")
    
    def _get_test_file_extension(self) -> str:
        """Get appropriate test file extension."""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java'
        }
        return extensions.get(self.current_analysis.language, 'txt')
    
    def _generate_test_file_header(self) -> str:
        """Generate test file header."""
        if self.current_analysis.language == 'python':
            return """import pytest
import unittest
from unittest.mock import Mock, patch

# Generated test cases
"""
        elif self.current_analysis.language in ['javascript', 'typescript']:
            return """const { describe, test, expect, beforeEach, afterEach } = require('@jest/globals');

// Generated test cases
"""
        elif self.current_analysis.language == 'java':
            return """import org.junit.Test;
import org.junit.Before;
import org.junit.After;
import static org.junit.Assert.*;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

// Generated test cases
"""
        return "// Generated test cases\n"
    
    def interactive_refinement(self):
        """Interactive mode for test case refinement."""
        if not self.current_tests:
            console.print("[red]No tests available for refinement[/red]")
            return
        
        console.print(Panel.fit(
            "[bold blue]Interactive Test Refinement[/bold blue]\n"
            "Review and refine your generated test cases",
            border_style="blue"
        ))
        
        while True:
            # Display current tests
            self._display_test_summary()
            
            # Get user choice
            choice = Prompt.ask(
                "\nWhat would you like to do?",
                choices=["view", "edit", "add", "remove", "enhance", "save", "quit"],
                default="quit"
            )
            
            if choice == "view":
                self._view_test_details()
            elif choice == "edit":
                self._edit_test()
            elif choice == "add":
                self._add_custom_test()
            elif choice == "remove":
                self._remove_test()
            elif choice == "enhance":
                self._enhance_specific_test()
            elif choice == "save":
                output_dir = Prompt.ask("Output directory", default="./tests")
                self._save_tests(output_dir)
            elif choice == "quit":
                break
    
    def _display_test_summary(self):
        """Display summary of current tests."""
        table = Table(title="Generated Test Cases")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Function", style="blue")
        
        for i, test in enumerate(self.current_tests):
            table.add_row(
                str(i + 1),
                test.name,
                test.test_type.value,
                test.function_name
            )
        
        console.print(table)
    
    def _view_test_details(self):
        """View details of a specific test."""
        test_id = Prompt.ask("Enter test ID to view")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                test = self.current_tests[test_index]
                console.print(Panel(
                    f"[bold]{test.name}[/bold]\n\n"
                    f"Type: {test.test_type.value}\n"
                    f"Function: {test.function_name}\n"
                    f"Description: {test.description}\n\n"
                    f"[yellow]Code:[/yellow]\n{test.test_code}",
                    title="Test Details"
                ))
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    def _edit_test(self):
        """Edit a specific test case."""
        test_id = Prompt.ask("Enter test ID to edit")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                test = self.current_tests[test_index]
                
                # Show current test
                console.print(f"[yellow]Current test:[/yellow]\n{test.test_code}")
                
                # Get AI suggestions for improvement
                suggestions = self.ai_provider.suggest_test_improvements(test, self._prepare_ai_context())
                if suggestions:
                    console.print(f"[blue]AI Suggestions:[/blue]\n{suggestions}")
                
                # Allow manual editing
                if Confirm.ask("Would you like to manually edit this test?"):
                    console.print("[yellow]Enter new test code (press Ctrl+D when done):[/yellow]")
                    new_code = ""
                    try:
                        while True:
                            line = input()
                            new_code += line + "\n"
                    except EOFError:
                        pass
                    
                    if new_code.strip():
                        test.test_code = new_code.strip()
                        console.print("[green]✓ Test updated[/green]")
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    def _add_custom_test(self):
        """Add a custom test case."""
        console.print("[yellow]Adding custom test case...[/yellow]")
        
        name = Prompt.ask("Test name")
        test_type = Prompt.ask("Test type", choices=["unit", "integration", "edge"], default="unit")
        function_name = Prompt.ask("Function name")
        description = Prompt.ask("Description")
        
        console.print("[yellow]Enter test code (press Ctrl+D when done):[/yellow]")
        test_code = ""
        try:
            while True:
                line = input()
                test_code += line + "\n"
        except EOFError:
            pass
        
        if test_code.strip():
            custom_test = TestCase(
                name=name,
                test_type=test_type,
                function_name=function_name,
                description=description,
                test_code=test_code.strip()
            )
            self.current_tests.append(custom_test)
            console.print("[green]✓ Custom test added[/green]")
    
    def _remove_test(self):
        """Remove a test case."""
        test_id = Prompt.ask("Enter test ID to remove")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                removed_test = self.current_tests.pop(test_index)
                console.print(f"[green]✓ Removed test: {removed_test.name}[/green]")
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    def _enhance_specific_test(self):
        """Enhance a specific test with AI."""
        test_id = Prompt.ask("Enter test ID to enhance")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                test = self.current_tests[test_index]
                console.print(f"[yellow]Enhancing test: {test.name}...[/yellow]")
                
                enhanced = self.ai_provider.enhance_test_case(test, self._prepare_ai_context())
                if enhanced:
                    test.test_code = enhanced.get('code', test.test_code)
                    test.description = enhanced.get('description', test.description)
                    console.print("[green]✓ Test enhanced[/green]")
                else:
                    console.print("[yellow]No enhancements suggested[/yellow]")
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

    def generate_coverage_report(self, tests) -> Dict[str, Any]:
        """Generate coverage report for test suite."""
        if not self.current_analysis:
            return {'overall_percentage': 0.0, 'coverage_gaps': []}
        
        total_functions = len(self.current_analysis.functions)
        if total_functions == 0:
            return {'overall_percentage': 100.0, 'coverage_gaps': []}
        
        covered_functions = set()
        for test in tests:
            covered_functions.add(test.function_name)
        
        coverage_percentage = (len(covered_functions) / total_functions) * 100
        
        # Identify uncovered functions
        uncovered_functions = []
        for func in self.current_analysis.functions:
            if func.name not in covered_functions:
                uncovered_functions.append(func.name)
        
        return {
            'overall_percentage': coverage_percentage,
            'line_coverage': {},  # Would need more sophisticated analysis
            'untested_functions': uncovered_functions,
            'coverage_gaps': [
                {
                    'function_name': func_name,
                    'description': f'Function {func_name} has no test coverage',
                    'suggested_tests': [f'test_{func_name}_basic', f'test_{func_name}_edge_cases']
                }
                for func_name in uncovered_functions
            ]
        }