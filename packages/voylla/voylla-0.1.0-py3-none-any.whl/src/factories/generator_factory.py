"""
Generator Factory - Creates language-specific test generators
"""
from typing import Dict, Type
from src.interfaces.base_interfaces import ITestGenerator, IGeneratorFactory, Language
from src.generators.test_generator import TestGenerator


class PythonTestGenerator(TestGenerator):
    """Python-specific test generator."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.PYTHON


class JavaScriptTestGenerator(TestGenerator):
    """JavaScript-specific test generator."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.JAVASCRIPT


class TypeScriptTestGenerator(TestGenerator):
    """TypeScript-specific test generator."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.TYPESCRIPT


class JavaTestGenerator(TestGenerator):
    """Java-specific test generator."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.JAVA


class GeneratorFactory(IGeneratorFactory):
    """Factory for creating language-specific test generators."""
    
    def __init__(self):
        self._generators: Dict[Language, Type[ITestGenerator]] = {
            Language.PYTHON: PythonTestGenerator,
            Language.JAVASCRIPT: JavaScriptTestGenerator,
            Language.TYPESCRIPT: TypeScriptTestGenerator,
            Language.JAVA: JavaTestGenerator
        }
    
    def create_generator(self, language: Language) -> ITestGenerator:
        """Create test generator for specific language."""
        if language not in self._generators:
            raise ValueError(f"Unsupported language: {language}")
        
        generator_class = self._generators[language]
        return generator_class()
    
    def get_supported_languages(self) -> list[Language]:
        """Get list of supported languages."""
        return list(self._generators.keys())
    
    def register_generator(self, language: Language, generator_class: Type[ITestGenerator]) -> None:
        """Register a new generator for a language."""
        self._generators[language] = generator_class