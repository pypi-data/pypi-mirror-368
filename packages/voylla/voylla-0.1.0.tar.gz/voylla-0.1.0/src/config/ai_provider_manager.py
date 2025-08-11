"""
AI Provider Manager - Manages AI provider selection and fallback logic
"""
import os
from typing import Dict, Any, Optional, List
from src.interfaces.base_interfaces import IAIProvider
from src.factories.ai_provider_factory import AIProviderFactory
from src.config.configuration_manager import ConfigurationManager


class AIProviderManager:
    """Manages AI provider selection, fallback logic, and provider health."""
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.factory = AIProviderFactory()
        self._current_provider: Optional[IAIProvider] = None
        self._provider_health: Dict[str, bool] = {}
        self._fallback_order = ['openai', 'anthropic', 'mock']
    
    def get_provider(self) -> IAIProvider:
        """Get the current AI provider, creating one if necessary."""
        if self._current_provider is None:
            self._current_provider = self._create_best_provider()
        return self._current_provider
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider and available alternatives."""
        available_providers = self.config_manager.get_available_ai_providers()
        preferred_provider = self.config_manager.get_preferred_ai_provider()
        
        return {
            'current_provider': preferred_provider,
            'available_providers': available_providers,
            'fallback_order': self._fallback_order,
            'provider_health': self._provider_health.copy(),
            'has_ai_capability': preferred_provider != 'mock'
        }
    
    def test_provider_connection(self, provider_type: str) -> bool:
        """Test if a specific provider is working correctly."""
        try:
            if provider_type == 'mock':
                self._provider_health[provider_type] = True
                return True
            
            # Check if API key is available
            api_key = self.config_manager.get_api_key(provider_type)
            if not api_key:
                self._provider_health[provider_type] = False
                return False
            
            # Create provider directly without fallback to test the specific provider
            config = self.config_manager.get_ai_provider_config()
            
            # Create the specific provider class directly
            if provider_type == 'openai':
                from src.factories.ai_provider_factory import OpenAIProvider
                provider = OpenAIProvider(api_key, config)
            elif provider_type == 'anthropic':
                from src.factories.ai_provider_factory import AnthropicProvider
                provider = AnthropicProvider(api_key, config)
            else:
                # For other providers, use factory
                provider = self.factory.create_provider(provider_type, config)
            
            # Test with a simple code analysis request
            test_result = provider.analyze_code_patterns(
                "def test_function(): return True", 
                "python"
            )
            
            # Check if we got a valid response (not an error message)
            is_healthy = (
                test_result is not None and 
                isinstance(test_result, dict) and 
                'analysis' in test_result and
                'Unable to analyze code patterns' not in test_result['analysis'] and
                'Unable to get AI suggestions' not in test_result['analysis']
            )
            
            self._provider_health[provider_type] = is_healthy
            return is_healthy
            
        except Exception as e:
            print(f"Provider {provider_type} health check failed: {e}")
            self._provider_health[provider_type] = False
            return False
    
    def test_all_providers(self) -> Dict[str, bool]:
        """Test all available providers and return their health status."""
        available_providers = self.config_manager.get_available_ai_providers()
        
        # Test available providers
        for provider_type in available_providers:
            if available_providers[provider_type]:
                self.test_provider_connection(provider_type)
        
        # Mock provider is always available
        self._provider_health['mock'] = True
        
        return self._provider_health.copy()
    
    def force_provider(self, provider_type: str) -> bool:
        """Force the use of a specific provider, bypassing normal selection logic."""
        try:
            config = self.config_manager.get_ai_provider_config()
            self._current_provider = self.factory.create_provider(provider_type, config)
            return True
        except Exception as e:
            print(f"Failed to force provider {provider_type}: {e}")
            return False
    
    def reset_provider(self) -> None:
        """Reset the current provider, forcing re-selection on next use."""
        self._current_provider = None
        self._provider_health.clear()
    
    def get_fallback_recommendations(self) -> List[str]:
        """Get recommendations for improving AI provider setup."""
        recommendations = []
        available_providers = self.config_manager.get_available_ai_providers()
        
        if not any(available_providers.values()):
            recommendations.extend([
                "No AI providers configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable",
                "Example: export OPENAI_API_KEY='your-api-key-here'",
                "Currently using mock provider with limited functionality"
            ])
        elif available_providers.get('openai', False) and available_providers.get('anthropic', False):
            recommendations.append(
                "Both OpenAI and Anthropic API keys detected. Set AI_PROVIDER=openai or AI_PROVIDER=anthropic to choose explicitly"
            )
        elif not available_providers.get('openai', False) or not available_providers.get('anthropic', False):
            recommendations.append("Consider setting up both OpenAI and Anthropic API keys for better reliability")
        
        # Check provider health
        unhealthy_providers = [
            provider for provider, healthy in self._provider_health.items() 
            if not healthy and provider != 'mock'
        ]
        
        if unhealthy_providers:
            recommendations.append(
                f"Provider(s) {', '.join(unhealthy_providers)} are not responding correctly. "
                "Check your API keys and network connection."
            )
        
        return recommendations
    
    def _create_best_provider(self) -> IAIProvider:
        """Create the best available AI provider based on configuration and health."""
        config = self.config_manager.get_ai_provider_config()
        preferred_provider = self.config_manager.get_preferred_ai_provider()
        
        # If preferred provider is explicitly set and available, try it first
        if preferred_provider != 'auto' and preferred_provider != 'mock':
            try:
                provider = self.factory.create_provider(preferred_provider, config)
                # Test the provider quickly
                if self._quick_provider_test(provider, preferred_provider):
                    return provider
            except Exception as e:
                print(f"Failed to create preferred provider {preferred_provider}: {e}")
        
        # Try providers in fallback order
        for provider_type in self._fallback_order:
            try:
                # Skip if no API key available (except for mock)
                if provider_type != 'mock':
                    api_key = self.config_manager.get_api_key(provider_type)
                    if not api_key:
                        continue
                
                provider = self.factory.create_provider(provider_type, config)
                
                # Test the provider
                if self._quick_provider_test(provider, provider_type):
                    if provider_type != 'mock':
                        print(f"Using {provider_type} AI provider")
                    return provider
                    
            except Exception as e:
                print(f"Failed to create {provider_type} provider: {e}")
                continue
        
        # Fallback to mock if everything else fails
        print("Warning: All AI providers failed, using mock provider with limited functionality")
        return self.factory.create_provider('mock', config)
    
    def _quick_provider_test(self, provider: IAIProvider, provider_type: str) -> bool:
        """Perform a quick test of the provider to ensure it's working."""
        if provider_type == 'mock':
            return True
        
        try:
            # Quick test with minimal API call
            result = provider.analyze_code_patterns("def test(): pass", "python")
            is_working = (
                result is not None and 
                isinstance(result, dict) and 
                'analysis' in result and
                result['analysis'] is not None
            )
            
            self._provider_health[provider_type] = is_working
            return is_working
            
        except Exception as e:
            print(f"Quick test failed for {provider_type}: {e}")
            self._provider_health[provider_type] = False
            return False