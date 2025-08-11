"""
Configuration Manager - Centralized configuration management with environment variable support
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict, field
from src.interfaces.base_interfaces import IConfigurationManager, Language


@dataclass
class TestGeneratorConfig:
    """Main configuration for the test generator."""
    # AI Configuration
    ai_provider: str = "auto"
    openai_model: str = "gpt-4"
    anthropic_model: str = "claude-3-sonnet-20240229"
    ai_max_tokens: int = 1000
    ai_temperature: float = 0.3
    ai_timeout: int = 30
    
    # Test Generation Configuration
    default_test_framework: Dict[str, str] = field(default_factory=dict)
    coverage_threshold: float = 80.0
    max_test_cases_per_function: int = 5
    include_edge_cases: bool = True
    include_integration_tests: bool = True
    
    # Output Configuration
    output_format: str = "files"  # "files", "stdout", "json"
    test_file_prefix: str = "test_"
    test_directory: str = "tests"
    
    # CI/CD Configuration
    github_integration: bool = False
    auto_pr_comments: bool = True
    coverage_check_enabled: bool = True
    
    def __post_init__(self):
        if not self.default_test_framework:
            self.default_test_framework = {
                "python": "pytest",
                "javascript": "jest",
                "typescript": "jest",
                "java": "junit"
            }


class ConfigurationManager(IConfigurationManager):
    """Centralized configuration management with environment variable support."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/config.yaml"
        self.config = TestGeneratorConfig()
        self._config_data = self.load_config(self.config_path)
        self._apply_config()
        # Load from .env if present to make API keys available
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv()
        except Exception:
            pass

        self._load_from_env()
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file and environment variables."""
        config_data = {}
        
        # Load from YAML config file
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f) or {}
                except Exception as e:
                    print(f"Warning: Failed to load config file {config_path}: {e}")
        
        return config_data
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration settings."""
        try:
            # Validate AI provider settings
            ai_config = config.get('ai', {})
            valid_providers = ['openai', 'anthropic', 'auto', 'mock']
            if ai_config.get('provider') and ai_config['provider'] not in valid_providers:
                return False
            
            # Validate AI numeric settings
            ai_numeric_validations = [
                ('max_tokens', lambda x: isinstance(x, int) and x > 0),
                ('temperature', lambda x: isinstance(x, (int, float)) and 0 <= x <= 2),
                ('timeout', lambda x: isinstance(x, int) and x > 0)
            ]
            
            for key, validator in ai_numeric_validations:
                if key in ai_config and not validator(ai_config[key]):
                    return False
            
            # Validate test generation settings
            test_config = config.get('test_generation', {})
            if 'max_test_cases_per_function' in test_config:
                if not isinstance(test_config['max_test_cases_per_function'], int) or test_config['max_test_cases_per_function'] <= 0:
                    return False
            
            if 'coverage_threshold' in test_config:
                threshold = test_config['coverage_threshold']
                if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 100:
                    return False
            
            return True
        except Exception:
            return False
    
    def get_ai_provider_config(self) -> Dict[str, Any]:
        """Get AI provider configuration."""
        return {
            'provider': self.config.ai_provider,
            'openai_model': self.config.openai_model,
            'anthropic_model': self.config.anthropic_model,
            'max_tokens': self.config.ai_max_tokens,
            'temperature': self.config.ai_temperature,
            'timeout': self.config.ai_timeout
        }
    
    def get_language_config(self, language: Language) -> Dict[str, Any]:
        """Get language-specific configuration."""
        lang_str = language.value if isinstance(language, Language) else str(language)
        
        # Default language configurations
        default_configs = {
            'python': {
                'test_framework': 'pytest',
                'file_extension': '.py',
                'import_style': 'from module import function',
                'test_file_pattern': 'test_*.py',
                'setup_imports': ['import pytest', 'from unittest.mock import Mock, patch'],
                'assertion_style': 'assert'
            },
            'javascript': {
                'test_framework': 'jest',
                'file_extension': '.js',
                'import_style': 'const { function } = require("module")',
                'test_file_pattern': '*.test.js',
                'setup_imports': ['const { describe, test, expect, beforeEach, afterEach } = require("@jest/globals")'],
                'assertion_style': 'expect'
            },
            'typescript': {
                'test_framework': 'jest',
                'file_extension': '.ts',
                'import_style': 'import { function } from "module"',
                'test_file_pattern': '*.test.ts',
                'setup_imports': ['import { describe, test, expect, beforeEach, afterEach } from "@jest/globals"'],
                'assertion_style': 'expect'
            },
            'java': {
                'test_framework': 'junit',
                'file_extension': '.java',
                'import_style': 'import package.Class',
                'test_file_pattern': '*Test.java',
                'setup_imports': ['import org.junit.Test', 'import static org.junit.Assert.*'],
                'assertion_style': 'assert'
            }
        }
        
        # Get language-specific config from file
        languages_config = self._config_data.get('languages', {})
        file_config = languages_config.get(lang_str, {})
        
        # Merge with defaults
        default_config = default_configs.get(lang_str, {})
        
        # Override with global test framework setting if specified and not overridden in language config
        if lang_str in self.config.default_test_framework and 'test_framework' not in file_config:
            default_config['test_framework'] = self.config.default_test_framework[lang_str]
        
        # Apply language-specific overrides (this should come last to have highest priority)
        default_config.update(file_config)
        
        return default_config
    
    def get_test_generation_config(self) -> Dict[str, Any]:
        """Get test generation configuration."""
        return {
            'coverage_threshold': self.config.coverage_threshold,
            'max_test_cases_per_function': self.config.max_test_cases_per_function,
            'include_edge_cases': self.config.include_edge_cases,
            'include_integration_tests': self.config.include_integration_tests,
            'default_test_framework': self.config.default_test_framework
        }
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return {
            'output_format': self.config.output_format,
            'test_file_prefix': self.config.test_file_prefix,
            'test_directory': self.config.test_directory
        }
    
    def get_integration_config(self) -> Dict[str, Any]:
        """Get CI/CD integration configuration."""
        return {
            'github_integration': self.config.github_integration,
            'auto_pr_comments': self.config.auto_pr_comments,
            'coverage_check_enabled': self.config.coverage_check_enabled
        }
    
    def get_available_ai_providers(self) -> Dict[str, bool]:
        """Check which AI providers are available based on API keys."""
        return {
            'openai': bool(os.getenv('OPENAI_API_KEY')),
            'anthropic': bool(os.getenv('ANTHROPIC_API_KEY'))
        }
    
    def get_preferred_ai_provider(self) -> str:
        """Get the preferred AI provider based on configuration and availability."""
        available = self.get_available_ai_providers()
        provider = (self.config.ai_provider or "").strip().lower()
        
        if provider == "auto":
            # Auto-select based on availability (prefer OpenAI)
            if available['openai']:
                return 'openai'
            elif available['anthropic']:
                return 'anthropic'
            else:
                return 'mock'
        elif provider in available and available[provider]:
            return provider
        else:
            return 'mock'
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider."""
        if provider == 'openai':
            return os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            return os.getenv('ANTHROPIC_API_KEY')
        return None
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """Save current configuration to YAML file."""
        output_path = config_path or self.config_path
        config_dict = asdict(self.config)
        
        # Organize config into sections
        organized_config = {
            'ai': {
                'provider': config_dict['ai_provider'],
                'openai_model': config_dict['openai_model'],
                'anthropic_model': config_dict['anthropic_model'],
                'max_tokens': config_dict['ai_max_tokens'],
                'temperature': config_dict['ai_temperature'],
                'timeout': config_dict['ai_timeout']
            },
            'test_generation': {
                'coverage_threshold': config_dict['coverage_threshold'],
                'max_test_cases_per_function': config_dict['max_test_cases_per_function'],
                'include_edge_cases': config_dict['include_edge_cases'],
                'include_integration_tests': config_dict['include_integration_tests'],
                'default_test_framework': config_dict['default_test_framework']
            },
            'output': {
                'output_format': config_dict['output_format'],
                'test_file_prefix': config_dict['test_file_prefix'],
                'test_directory': config_dict['test_directory']
            },
            'integration': {
                'github_integration': config_dict['github_integration'],
                'auto_pr_comments': config_dict['auto_pr_comments'],
                'coverage_check_enabled': config_dict['coverage_check_enabled']
            }
        }
        
        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(organized_config, f, default_flow_style=False, indent=2)
    
    def _apply_config(self) -> None:
        """Apply configuration from loaded data."""
        if not self._config_data:
            return
        
        # Apply AI configuration
        ai_config = self._config_data.get('ai', {})
        if 'provider' in ai_config:
            self.config.ai_provider = ai_config['provider']
        if 'openai_model' in ai_config:
            self.config.openai_model = ai_config['openai_model']
        if 'anthropic_model' in ai_config:
            self.config.anthropic_model = ai_config['anthropic_model']
        if 'max_tokens' in ai_config:
            self.config.ai_max_tokens = ai_config['max_tokens']
        if 'temperature' in ai_config:
            self.config.ai_temperature = ai_config['temperature']
        if 'timeout' in ai_config:
            self.config.ai_timeout = ai_config['timeout']
        
        # Apply test generation configuration
        test_config = self._config_data.get('test_generation', {})
        if 'coverage_threshold' in test_config:
            self.config.coverage_threshold = test_config['coverage_threshold']
        if 'max_test_cases_per_function' in test_config:
            self.config.max_test_cases_per_function = test_config['max_test_cases_per_function']
        if 'include_edge_cases' in test_config:
            self.config.include_edge_cases = test_config['include_edge_cases']
        if 'include_integration_tests' in test_config:
            self.config.include_integration_tests = test_config['include_integration_tests']
        if 'default_test_framework' in test_config:
            self.config.default_test_framework.update(test_config['default_test_framework'])
        
        # Apply output configuration
        output_config = self._config_data.get('output', {})
        if 'output_format' in output_config:
            self.config.output_format = output_config['output_format']
        if 'test_file_prefix' in output_config:
            self.config.test_file_prefix = output_config['test_file_prefix']
        if 'test_directory' in output_config:
            self.config.test_directory = output_config['test_directory']
        
        # Apply integration configuration
        integration_config = self._config_data.get('integration', {})
        if 'github_integration' in integration_config:
            self.config.github_integration = integration_config['github_integration']
        if 'auto_pr_comments' in integration_config:
            self.config.auto_pr_comments = integration_config['auto_pr_comments']
        if 'coverage_check_enabled' in integration_config:
            self.config.coverage_check_enabled = integration_config['coverage_check_enabled']
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        def _get_env_str(name: str) -> Optional[str]:
            val = os.getenv(name)
            if val is None:
                return None
            val = val.strip()
            return val if val != "" else None
        # AI provider settings
        ai_provider_val = _get_env_str('AI_PROVIDER')
        if ai_provider_val is not None:
            self.config.ai_provider = ai_provider_val
        openai_model_val = _get_env_str('OPENAI_MODEL')
        if openai_model_val is not None:
            self.config.openai_model = openai_model_val
        anthropic_model_val = _get_env_str('ANTHROPIC_MODEL')
        if anthropic_model_val is not None:
            self.config.anthropic_model = anthropic_model_val
        
        # Numeric settings with validation
        try:
            ai_max_tokens_val = _get_env_str('AI_MAX_TOKENS')
            if ai_max_tokens_val is not None:
                self.config.ai_max_tokens = int(ai_max_tokens_val)
            ai_temp_val = _get_env_str('AI_TEMPERATURE')
            if ai_temp_val is not None:
                self.config.ai_temperature = float(ai_temp_val)
            ai_timeout_val = _get_env_str('AI_TIMEOUT')
            if ai_timeout_val is not None:
                self.config.ai_timeout = int(ai_timeout_val)
            coverage_threshold_val = _get_env_str('COVERAGE_THRESHOLD')
            if coverage_threshold_val is not None:
                self.config.coverage_threshold = float(coverage_threshold_val)
            max_tests_val = _get_env_str('MAX_TEST_CASES_PER_FUNCTION')
            if max_tests_val is not None:
                self.config.max_test_cases_per_function = int(max_tests_val)
        except ValueError:
            pass  # Keep defaults if invalid values
        
        # Boolean settings
        include_edge_cases_val = _get_env_str('INCLUDE_EDGE_CASES')
        if include_edge_cases_val is not None:
            self.config.include_edge_cases = include_edge_cases_val.lower() in ('true', '1', 'yes')
        include_integration_val = _get_env_str('INCLUDE_INTEGRATION_TESTS')
        if include_integration_val is not None:
            self.config.include_integration_tests = include_integration_val.lower() in ('true', '1', 'yes')
        github_integration_val = _get_env_str('GITHUB_INTEGRATION')
        if github_integration_val is not None:
            self.config.github_integration = github_integration_val.lower() in ('true', '1', 'yes')
        auto_pr_comments_val = _get_env_str('AUTO_PR_COMMENTS')
        if auto_pr_comments_val is not None:
            self.config.auto_pr_comments = auto_pr_comments_val.lower() in ('true', '1', 'yes')
        coverage_check_val = _get_env_str('COVERAGE_CHECK_ENABLED')
        if coverage_check_val is not None:
            self.config.coverage_check_enabled = coverage_check_val.lower() in ('true', '1', 'yes')
        
        # String settings
        output_format_val = _get_env_str('OUTPUT_FORMAT')
        if output_format_val is not None:
            self.config.output_format = output_format_val
        test_file_prefix_val = _get_env_str('TEST_FILE_PREFIX')
        if test_file_prefix_val is not None:
            self.config.test_file_prefix = test_file_prefix_val
        test_directory_val = _get_env_str('TEST_DIRECTORY')
        if test_directory_val is not None:
            self.config.test_directory = test_directory_val