"""
AI Provider Factory - Creates AI provider instances
"""
from typing import Dict, Any, Type
from src.interfaces.base_interfaces import IAIProvider, IAIProviderFactory, TestType

# Import AI libraries at module level for easier mocking in tests
try:
    # OpenAI Python SDK v1.x
    from openai import OpenAI as _OpenAIClient
except ImportError:
    _OpenAIClient = None

try:
    # Anthropic Python SDK
    from anthropic import Anthropic as _AnthropicClient
except ImportError:
    _AnthropicClient = None


class OpenAIProvider(IAIProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.config = config
        self.model = config.get('openai_model', 'gpt-4')
        self.max_tokens = config.get('max_tokens', 1000)
        self.temperature = config.get('temperature', 0.3)
        self.timeout = config.get('timeout', 30)
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        if _OpenAIClient is None:
            raise ImportError("openai package not installed. Run: pip install openai")

        # OpenAI SDK v1.x client
        self._client = _OpenAIClient(
            api_key=self.api_key,
            timeout=self.timeout,
        )
    
    def enhance_test_case(self, test, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance test case using OpenAI API."""
        try:
            prompt = self._create_enhancement_prompt(test, context)
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software testing engineer. Enhance the provided test case to make it more comprehensive, realistic, and maintainable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            enhanced_content = response.choices[0].message.content
            return self._parse_enhancement_response(enhanced_content, test)
            
        except Exception as e:
            print(f"Warning: OpenAI API error: {e}")
            return None
    
    def suggest_test_improvements(self, test, context: Dict[str, Any]) -> str:
        """Get test improvement suggestions from OpenAI."""
        try:
            prompt = f"""
Analyze this test case and provide specific improvement suggestions:

Test Name: {test.name}
Test Type: {test.test_type}
Function: {test.function_name}
Language: {context['language']}

Current Test Code:
{test.test_code}

Context:
- Edge Cases: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Provide 3-5 specific, actionable improvement suggestions.
"""
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software testing engineer. Provide specific, actionable suggestions for improving test cases."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(500, self.max_tokens),
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Warning: OpenAI API error: {e}")
            return "Unable to get AI suggestions at this time."
    
    def analyze_code_patterns(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code patterns and suggest test strategies."""
        try:
            prompt = f"""
Analyze this {language} code and suggest testing strategies:

Code:
{code}

Provide analysis of:
1. Code patterns and complexity
2. Potential edge cases
3. Testing strategies
4. Risk areas that need special attention
"""
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code analyst. Analyze code patterns and suggest comprehensive testing strategies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return {
                'analysis': response.choices[0].message.content,
                'provider': 'openai'
            }
            
        except Exception as e:
            print(f"Warning: OpenAI API error: {e}")
            return {'analysis': 'Unable to analyze code patterns at this time.', 'provider': 'openai'}
    
    def _create_enhancement_prompt(self, test, context: Dict[str, Any]) -> str:
        """Create prompt for test enhancement."""
        return f"""
Enhance this {context['language']} test case to make it more comprehensive and realistic:

Test Name: {test.name}
Test Type: {test.test_type}
Function: {test.function_name}
Description: {test.description}

Current Test Code:
{test.test_code}

Context Information:
- Language: {context['language']}
- Detected Edge Cases: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Please enhance this test by:
1. Adding more specific and meaningful assertions
2. Using realistic test data
3. Adding proper error handling expectations
4. Including setup/teardown if needed
5. Adding clear comments explaining the test logic

Return the enhanced test code and a brief description of improvements made.
Format your response as:
ENHANCED_CODE:
[enhanced test code here]

DESCRIPTION:
[brief description of improvements]

ASSERTIONS:
[list of key assertions to verify]
"""
    
    def _parse_enhancement_response(self, response: str, original_test) -> Dict[str, Any]:
        """Parse OpenAI response into structured enhancement data."""
        try:
            parts = response.split('ENHANCED_CODE:')
            if len(parts) < 2:
                return None
            
            code_and_rest = parts[1].split('DESCRIPTION:')
            enhanced_code = code_and_rest[0].strip()
            
            description = original_test.description
            assertions = []
            
            if len(code_and_rest) > 1:
                desc_and_rest = code_and_rest[1].split('ASSERTIONS:')
                description = desc_and_rest[0].strip()
                
                if len(desc_and_rest) > 1:
                    assertions_text = desc_and_rest[1].strip()
                    assertions = [line.strip('- ').strip() for line in assertions_text.split('\n') if line.strip()]
            
            return {
                'code': enhanced_code,
                'description': description,
                'assertions': assertions
            }
            
        except Exception as e:
            print(f"Warning: Failed to parse OpenAI response: {e}")
            return None


class AnthropicProvider(IAIProvider):
    """Anthropic Claude API provider implementation."""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.config = config
        self.model = config.get('anthropic_model', 'claude-3-sonnet-20240229')
        self.max_tokens = config.get('max_tokens', 1000)
        self.temperature = config.get('temperature', 0.3)
        self.timeout = config.get('timeout', 30)
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client."""
        if _AnthropicClient is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self._client = _AnthropicClient(
            api_key=self.api_key,
            timeout=self.timeout,
        )
    
    def enhance_test_case(self, test, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance test case using Anthropic Claude API."""
        try:
            prompt = self._create_enhancement_prompt(test, context)
            
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced_content = response.content[0].text
            return self._parse_enhancement_response(enhanced_content, test)
            
        except Exception as e:
            print(f"Warning: Anthropic API error: {e}")
            return None
    
    def suggest_test_improvements(self, test, context: Dict[str, Any]) -> str:
        """Get test improvement suggestions from Anthropic Claude."""
        try:
            prompt = f"""
As an expert software testing engineer, analyze this test case and provide specific improvement suggestions:

Test Details:
- Name: {test.name}
- Type: {test.test_type}
- Function: {test.function_name}
- Language: {context['language']}

Current Test Code:
{test.test_code}

Context Information:
- Edge Cases Detected: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Please provide 3-5 specific, actionable suggestions to improve this test case.
"""
            
            response = self._client.messages.create(
                model=self.model,
                max_tokens=min(500, self.max_tokens),
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Warning: Anthropic API error: {e}")
            return "Unable to get AI suggestions at this time."
    
    def analyze_code_patterns(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code patterns and suggest test strategies."""
        try:
            prompt = f"""
As an expert code analyst, analyze this {language} code and suggest comprehensive testing strategies:

Code:
{code}

Please provide analysis of:
1. Code patterns and complexity
2. Potential edge cases
3. Testing strategies
4. Risk areas that need special attention

Format your response clearly with sections for each analysis area.
"""
            
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'analysis': response.content[0].text,
                'provider': 'anthropic'
            }
            
        except Exception as e:
            print(f"Warning: Anthropic API error: {e}")
            return {'analysis': 'Unable to analyze code patterns at this time.', 'provider': 'anthropic'}
    
    def _create_enhancement_prompt(self, test, context: Dict[str, Any]) -> str:
        """Create prompt for test enhancement."""
        return f"""
As an expert software testing engineer, please enhance this {context['language']} test case:

Current Test:
Name: {test.name}
Type: {test.test_type}
Function: {test.function_name}
Description: {test.description}

Code:
{test.test_code}

Context:
- Language: {context['language']}
- Detected Edge Cases: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Please enhance this test by:
1. Adding more specific and meaningful assertions
2. Using realistic, domain-appropriate test data
3. Adding proper error handling expectations
4. Including necessary setup/teardown
5. Adding clear, helpful comments

Please format your response as:

ENHANCED_CODE:
[Your enhanced test code here]

DESCRIPTION:
[Brief description of the improvements you made]

ASSERTIONS:
[List the key assertions that should be verified]
"""
    
    def _parse_enhancement_response(self, response: str, original_test) -> Dict[str, Any]:
        """Parse Anthropic response into structured enhancement data."""
        try:
            parts = response.split('ENHANCED_CODE:')
            if len(parts) < 2:
                return None
            
            code_and_rest = parts[1].split('DESCRIPTION:')
            enhanced_code = code_and_rest[0].strip()
            
            description = original_test.description
            assertions = []
            
            if len(code_and_rest) > 1:
                desc_and_rest = code_and_rest[1].split('ASSERTIONS:')
                description = desc_and_rest[0].strip()
                
                if len(desc_and_rest) > 1:
                    assertions_text = desc_and_rest[1].strip()
                    assertions = [line.strip('- ').strip() for line in assertions_text.split('\n') if line.strip()]
            
            return {
                'code': enhanced_code,
                'description': description,
                'assertions': assertions
            }
            
        except Exception as e:
            print(f"Warning: Failed to parse Anthropic response: {e}")
            return None


class MockAIProvider(IAIProvider):
    """Mock AI provider for demonstration when no API key is available."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def enhance_test_case(self, test, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock enhancement of test cases."""
        enhancements = {
            'code': test.test_code,
            'description': f"Enhanced: {test.description}",
            'assertions': [
                "assert result is not None",
                "assert isinstance(result, expected_type)",
                "assert result meets expected criteria"
            ]
        }
        
        # Add language-specific improvements
        if context['language'] == 'python':
            if 'pytest.raises' not in test.test_code and test.test_type == TestType.EDGE:
                enhancements['code'] = test.test_code.replace(
                    '# Assert',
                    '# Assert\n    # Consider using pytest.raises for exception testing'
                )
        
        return enhancements
    
    def suggest_test_improvements(self, test, context: Dict[str, Any]) -> str:
        """Mock test improvement suggestions."""
        suggestions = [
            "Consider adding more specific assertions",
            "Add setup and teardown if needed", 
            "Test boundary conditions",
            "Add documentation for test purpose",
            "Consider parameterized tests for multiple inputs",
            "Set OPENAI_API_KEY or ANTHROPIC_API_KEY for AI-powered suggestions"
        ]
        
        return "\n".join(f"• {suggestion}" for suggestion in suggestions)
    
    def analyze_code_patterns(self, code: str, language: str) -> Dict[str, Any]:
        """Mock code pattern analysis."""
        return {
            'analysis': f"""
Mock Analysis for {language} code:

1. Code Patterns: Basic function structure detected
2. Edge Cases: Consider null inputs, empty collections, boundary values
3. Testing Strategies: Unit tests, integration tests, edge case tests recommended
4. Risk Areas: Input validation, error handling, performance considerations

Note: Set OPENAI_API_KEY or ANTHROPIC_API_KEY for AI-powered analysis.
""",
            'provider': 'mock'
        }


class AIProviderFactory(IAIProviderFactory):
    """Factory for creating AI provider instances."""
    
    def __init__(self):
        self._providers: Dict[str, Type[IAIProvider]] = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'mock': MockAIProvider
        }
    
    def create_provider(self, provider_type: str, config: Dict[str, Any]) -> IAIProvider:
        """Create AI provider instance."""
        if provider_type not in self._providers:
            raise ValueError(f"Unsupported AI provider: {provider_type}")
        
        provider_class = self._providers[provider_type]
        
        if provider_type == 'mock':
            return provider_class(config)
        elif provider_type in ['openai', 'anthropic']:
            # Get API key from environment
            import os
            api_key = None
            if provider_type == 'openai':
                api_key = os.getenv('OPENAI_API_KEY')
            elif provider_type == 'anthropic':
                api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if not api_key:
                print(f"Warning: No API key found for {provider_type}, falling back to mock provider")
                return self._providers['mock'](config)
            
            try:
                return provider_class(api_key, config)
            except ImportError as e:
                print(f"Warning: {e}, falling back to mock provider")
                return self._providers['mock'](config)
        else:
            # For custom providers, try to instantiate with config only
            try:
                return provider_class(config)
            except TypeError:
                # If that fails, try with no arguments (for providers that don't need config)
                return provider_class()
    
    def get_supported_providers(self) -> list[str]:
        """Get list of supported providers."""
        return list(self._providers.keys())
    
    def register_provider(self, provider_type: str, provider_class: Type[IAIProvider]) -> None:
        """Register a new AI provider."""
        self._providers[provider_type] = provider_class