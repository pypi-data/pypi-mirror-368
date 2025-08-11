"""
AI Configuration - Manages AI client settings and API keys
"""
import os
import yaml
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from src.interfaces.base_interfaces import IConfigurationManager, Language

@dataclass
class AIConfig:
    """Configuration for AI clients."""
    provider: str = "auto"  # "openai", "anthropic", "auto", "mock"
    openai_model: str = "gpt-4"
    anthropic_model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 1000
    temperature: float = 0.3
    timeout: int = 30

class AIConfigManager(IConfigurationManager):
    """Manages AI configuration and API key detection."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = AIConfig()
        self.config_data = self.load_config(config_path)
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Override defaults with environment variables if present
        self.config.provider = os.getenv('AI_PROVIDER', self.config.provider)
        self.config.openai_model = os.getenv('OPENAI_MODEL', self.config.openai_model)
        self.config.anthropic_model = os.getenv('ANTHROPIC_MODEL', self.config.anthropic_model)
        
        # Numeric settings
        try:
            self.config.max_tokens = int(os.getenv('AI_MAX_TOKENS', str(self.config.max_tokens)))
            self.config.temperature = float(os.getenv('AI_TEMPERATURE', str(self.config.temperature)))
            self.config.timeout = int(os.getenv('AI_TIMEOUT', str(self.config.timeout)))
        except ValueError:
            pass  # Keep defaults if invalid values
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Check which AI providers are available based on API keys."""
        return {
            'openai': bool(os.getenv('OPENAI_API_KEY')),
            'anthropic': bool(os.getenv('ANTHROPIC_API_KEY'))
        }
    
    def get_preferred_provider(self) -> str:
        """Get the preferred AI provider based on configuration and availability."""
        available = self.get_available_providers()
        
        if self.config.provider == "auto":
            # Auto-select based on availability (prefer OpenAI)
            if available['openai']:
                return 'openai'
            elif available['anthropic']:
                return 'anthropic'
            else:
                return 'mock'
        elif self.config.provider in available and available[self.config.provider]:
            return self.config.provider
        else:
            return 'mock'
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider."""
        if provider == 'openai':
            return os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            return os.getenv('ANTHROPIC_API_KEY')
        return None
    
    def validate_setup(self) -> Dict[str, Any]:
        """Validate AI setup and return status information."""
        available = self.get_available_providers()
        preferred = self.get_preferred_provider()
        
        return {
            'available_providers': available,
            'preferred_provider': preferred,
            'has_ai_capability': preferred != 'mock',
            'config': self.config,
            'recommendations': self._get_setup_recommendations(available)
        }
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file and environment."""
        config_data = {}
        
        # Load from YAML config file
        if config_path is None:
            config_path = "config/config.yaml"
        
        config_file = Path(config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
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
            if ai_config.get('provider') not in valid_providers:
                return False
            
            # Validate numeric settings
            if 'max_tokens' in ai_config:
                if not isinstance(ai_config['max_tokens'], int) or ai_config['max_tokens'] <= 0:
                    return False
            
            if 'temperature' in ai_config:
                temp = ai_config['temperature']
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                    return False
            
            return True
        except Exception:
            return False
    
    def get_ai_provider_config(self) -> Dict[str, Any]:
        """Get AI provider configuration."""
        ai_config = self.config_data.get('ai', {})
        
        return {
            'provider': ai_config.get('provider', self.config.provider),
            'openai_model': ai_config.get('openai_model', self.config.openai_model),
            'anthropic_model': ai_config.get('anthropic_model', self.config.anthropic_model),
            'max_tokens': ai_config.get('max_tokens', self.config.max_tokens),
            'temperature': ai_config.get('temperature', self.config.temperature),
            'timeout': ai_config.get('timeout', self.config.timeout)
        }
    
    def get_language_config(self, language: Language) -> Dict[str, Any]:
        """Get language-specific configuration."""
        languages_config = self.config_data.get('languages', {})
        lang_str = language.value if isinstance(language, Language) else str(language)
        
        default_configs = {
            'python': {
                'test_framework': 'pytest',
                'file_extension': '.py',
                'import_style': 'from module import function'
            },
            'javascript': {
                'test_framework': 'jest',
                'file_extension': '.js',
                'import_style': 'const { function } = require("module")'
            },
            'typescript': {
                'test_framework': 'jest',
                'file_extension': '.ts',
                'import_style': 'import { function } from "module"'
            },
            'java': {
                'test_framework': 'junit',
                'file_extension': '.java',
                'import_style': 'import package.Class'
            }
        }
        
        return languages_config.get(lang_str, default_configs.get(lang_str, {}))

    def _get_setup_recommendations(self, available: Dict[str, bool]) -> List[str]:
        """Get setup recommendations based on current configuration."""
        recommendations = []
        
        if not any(available.values()):
            recommendations.extend([
                "Set OPENAI_API_KEY environment variable to use OpenAI GPT-4 for test enhancement",
                "Or set ANTHROPIC_API_KEY environment variable to use Claude for test enhancement",
                "Example: export OPENAI_API_KEY='your-api-key-here'"
            ])
        
        if available['openai'] and available['anthropic']:
            recommendations.append(
                "Both OpenAI and Anthropic API keys detected. Set AI_PROVIDER=openai or AI_PROVIDER=anthropic to choose explicitly"
            )
        
        return recommendations