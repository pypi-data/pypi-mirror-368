"""
Analyzer Factory - Creates language-specific code analyzers
"""
from typing import Dict, Type
from src.interfaces.base_interfaces import ICodeAnalyzer, IAnalyzerFactory, Language
from src.analyzers.code_analyzer import CodeAnalyzer


class PythonCodeAnalyzer(CodeAnalyzer):
    """Python-specific code analyzer."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.PYTHON


class JavaScriptCodeAnalyzer(CodeAnalyzer):
    """JavaScript-specific code analyzer."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.JAVASCRIPT


class TypeScriptCodeAnalyzer(CodeAnalyzer):
    """TypeScript-specific code analyzer."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.TYPESCRIPT


class JavaCodeAnalyzer(CodeAnalyzer):
    """Java-specific code analyzer."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.JAVA


class AnalyzerFactory(IAnalyzerFactory):
    """Factory for creating language-specific code analyzers."""
    
    def __init__(self):
        self._analyzers: Dict[Language, Type[ICodeAnalyzer]] = {
            Language.PYTHON: PythonCodeAnalyzer,
            Language.JAVASCRIPT: JavaScriptCodeAnalyzer,
            Language.TYPESCRIPT: TypeScriptCodeAnalyzer,
            Language.JAVA: JavaCodeAnalyzer
        }
    
    def create_analyzer(self, language: Language) -> ICodeAnalyzer:
        """Create analyzer for specific language."""
        if language not in self._analyzers:
            raise ValueError(f"Unsupported language: {language}")
        
        analyzer_class = self._analyzers[language]
        return analyzer_class()
    
    def get_supported_languages(self) -> list[Language]:
        """Get list of supported languages."""
        return list(self._analyzers.keys())
    
    def register_analyzer(self, language: Language, analyzer_class: Type[ICodeAnalyzer]) -> None:
        """Register a new analyzer for a language."""
        self._analyzers[language] = analyzer_class