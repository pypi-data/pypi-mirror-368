#!/usr/bin/env python3
"""
Test Case Generator Bot - Main Entry Point
"""
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.test_agent import TestGeneratorAgent
from src.analyzers.code_analyzer import CodeAnalyzer
from src.generators.test_generator import TestGenerator
from src.config.configuration_manager import ConfigurationManager
from src.factories.analyzer_factory import AnalyzerFactory
from src.factories.generator_factory import GeneratorFactory
from src.factories.ai_provider_factory import AIProviderFactory
from src.interfaces.base_interfaces import Language

console = Console()

@click.command()
@click.option('--file', '-f', required=True, help='Path to the code file to analyze')
@click.option('--language', '-l', help='Programming language (auto-detected if not specified)')
@click.option('--output', '-o', help='Output directory for generated tests')
@click.option('--interactive', '-i', is_flag=True, help='Enable interactive mode for test refinement')
@click.option('--coverage', '-c', is_flag=True, help='Generate coverage report')
def main(file, language, output, interactive, coverage):
    """Test Case Generator Bot - Analyze code and generate comprehensive test cases."""
    
    console.print(Panel.fit(
        "[bold blue]Test Case Generator Bot[/bold blue]\n"
        "Analyzing code and generating intelligent test cases...",
        border_style="blue"
    ))
    
    # Initialize configuration manager
    config_manager = ConfigurationManager()
    
    # Show AI configuration status
    available_providers = config_manager.get_available_ai_providers()
    preferred_provider = config_manager.get_preferred_ai_provider()
    
    if preferred_provider != 'mock':
        console.print(f"[green]🤖 AI Enhancement: {preferred_provider.title()}[/green]")
    else:
        console.print("[yellow]🤖 AI Enhancement: Disabled (set OPENAI_API_KEY or ANTHROPIC_API_KEY, or create a .env)[/yellow]")
    
    # Validate input file
    code_file = Path(file)
    if not code_file.exists():
        console.print(f"[red]Error: File {file} not found[/red]")
        sys.exit(1)
    
    # Detect language if not specified
    if not language:
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java'
        }
        language = language_map.get(code_file.suffix.lower())
        if not language:
            console.print(f"[red]Error: Unable to detect language for {code_file.suffix}[/red]")
            sys.exit(1)
    
    # Initialize factories
    analyzer_factory = AnalyzerFactory()
    generator_factory = GeneratorFactory()
    ai_provider_factory = AIProviderFactory()
    
    # Create language-specific components
    try:
        lang_enum = Language(language)
        analyzer = analyzer_factory.create_analyzer(lang_enum)
        generator = generator_factory.create_generator(lang_enum)
        
        # Create AI provider
        ai_config = config_manager.get_ai_provider_config()
        ai_provider = ai_provider_factory.create_provider(preferred_provider, ai_config)
        
        # Initialize agent with configuration
        agent = TestGeneratorAgent(analyzer, generator, config_manager, ai_provider)
        
    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
    
    try:
        # Analyze and generate tests
        console.print(f"[yellow]Analyzing {code_file.name}...[/yellow]")
        results = agent.process_file(str(code_file), language, output)
        
        # Display results
        console.print(f"[green]✓ Generated {results['test_count']} test cases[/green]")
        console.print(f"[green]✓ Coverage: {results['coverage_percentage']:.1f}%[/green]")
        
        if interactive:
            agent.interactive_refinement()
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()