"""
Conversation Manager - Handles interactive test refinement through natural language.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
import json

from src.interfaces.base_interfaces import (
    IConversationManager, TestSuite, TestCase, TestType, IAIProvider
)


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    timestamp: datetime
    user_input: str
    system_response: str
    context: Dict[str, Any] = field(default_factory=dict)
    test_changes: List[str] = field(default_factory=list)


@dataclass
class ConversationContext:
    """Maintains context across conversation turns."""
    test_suite: TestSuite
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    current_focus: Optional[str] = None  # Current test or function being discussed
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationManager(IConversationManager):
    """Manages interactive conversation for test refinement."""
    
    def __init__(self, ai_provider: IAIProvider):
        self.ai_provider = ai_provider
        self.context: Optional[ConversationContext] = None
        self.feedback_patterns = self._initialize_feedback_patterns()
    
    def start_conversation(self, tests: TestSuite) -> None:
        """Start interactive conversation for test refinement."""
        self.context = ConversationContext(
            test_suite=tests,
            session_metadata={
                'start_time': datetime.now(),
                'language': tests.language.value,
                'framework': tests.framework,
                'total_tests': len(tests.test_cases)
            }
        )
        
        print(f"\n🤖 Test Refinement Assistant")
        print(f"Generated {len(tests.test_cases)} test cases for {tests.language.value}")
        print(f"Framework: {tests.framework}")
        print(f"\nYou can ask me to:")
        print("• Modify specific test cases")
        print("• Add more test scenarios")
        print("• Explain test logic")
        print("• Focus on specific functions")
        print("• Change testing approach")
        print("\nType 'help' for more options or 'done' to finish.\n")
    
    def process_feedback(self, feedback: str, context: Dict[str, Any]) -> TestSuite:
        """Process user feedback and update tests accordingly."""
        if not self.context:
            raise ValueError("Conversation not started. Call start_conversation() first.")
        
        # Clean and normalize feedback
        feedback = feedback.strip()
        if not feedback:
            return self.context.test_suite
        
        # Handle special commands
        if feedback.lower() in ['help', '?']:
            self._show_help()
            return self.context.test_suite
        elif feedback.lower() in ['done', 'exit', 'quit']:
            self._end_conversation()
            return self.context.test_suite
        elif feedback.lower().startswith('show'):
            self._handle_show_command(feedback)
            return self.context.test_suite
        
        # Process natural language feedback
        try:
            # Analyze feedback intent and extract requirements
            feedback_analysis = self._analyze_feedback(feedback, context)
            
            # Apply changes based on analysis
            updated_suite = self._apply_feedback_changes(feedback_analysis)
            
            # Generate response
            response = self._generate_response(feedback_analysis)
            
            # Record conversation turn
            turn = ConversationTurn(
                timestamp=datetime.now(),
                user_input=feedback,
                system_response=response,
                context=feedback_analysis,
                test_changes=feedback_analysis.get('changes_made', [])
            )
            self.context.conversation_history.append(turn)
            
            print(f"\n🤖 {response}")
            
            return updated_suite
            
        except Exception as e:
            error_response = f"I had trouble processing that request: {str(e)}. Could you rephrase it?"
            print(f"\n🤖 {error_response}")
            return self.context.test_suite
    
    def maintain_context(self, conversation_history: List[Dict[str, Any]]) -> None:
        """Preserve context across conversation turns."""
        if not self.context:
            return
        
        # Update user preferences based on conversation patterns
        self._update_user_preferences()
        
        # Update current focus based on recent interactions
        self._update_current_focus()
        
        # Clean up old context if conversation gets too long
        if len(self.context.conversation_history) > 20:
            # Keep only the last 15 turns plus any important context
            important_turns = [turn for turn in self.context.conversation_history 
                             if turn.test_changes or 'important' in turn.context]
            recent_turns = self.context.conversation_history[-10:]
            self.context.conversation_history = important_turns + recent_turns
    
    def _initialize_feedback_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for recognizing feedback types."""
        return {
            'modify_test': [
                r'change.*test.*(\w+)',
                r'modify.*(\w+)',
                r'update.*test.*(\w+)',
                r'fix.*(\w+)',
                r'improve.*(\w+)'
            ],
            'add_test': [
                r'add.*test.*for.*(\w+)',
                r'create.*test.*(\w+)',
                r'need.*test.*(\w+)',
                r'missing.*test.*(\w+)'
            ],
            'remove_test': [
                r'remove.*test.*(\w+)',
                r'delete.*(\w+)',
                r'don\'t need.*(\w+)'
            ],
            'explain': [
                r'explain.*(\w+)',
                r'why.*(\w+)',
                r'what.*does.*(\w+)',
                r'how.*(\w+)'
            ],
            'focus': [
                r'focus.*on.*(\w+)',
                r'work.*on.*(\w+)',
                r'concentrate.*on.*(\w+)'
            ]
        }
    
    def _analyze_feedback(self, feedback: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user feedback to understand intent and extract requirements."""
        analysis = {
            'intent': 'unknown',
            'target': None,
            'action': None,
            'details': feedback,
            'confidence': 0.0
        }
        
        feedback_lower = feedback.lower()
        
        # Pattern matching for common intents
        for intent, patterns in self.feedback_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, feedback_lower)
                if match:
                    analysis['intent'] = intent
                    analysis['target'] = match.group(1) if match.groups() else None
                    analysis['confidence'] = 0.8
                    break
            if analysis['confidence'] > 0:
                break
        
        # Use AI provider for more sophisticated analysis if pattern matching fails
        if analysis['confidence'] < 0.5:
            ai_analysis = self._get_ai_feedback_analysis(feedback, context)
            if ai_analysis:
                analysis.update(ai_analysis)
        
        # Add context from conversation history
        analysis['conversation_context'] = self._get_relevant_context()
        
        return analysis
    
    def _get_ai_feedback_analysis(self, feedback: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use AI provider to analyze complex feedback."""
        try:
            prompt = f"""
Analyze this user feedback about test cases and extract the intent:

User Feedback: "{feedback}"

Current Context:
- Language: {self.context.session_metadata.get('language', 'unknown')}
- Framework: {self.context.session_metadata.get('framework', 'unknown')}
- Total Tests: {self.context.session_metadata.get('total_tests', 0)}
- Current Focus: {self.context.current_focus or 'none'}

Available Test Cases:
{self._get_test_case_summary()}

Please analyze the feedback and respond with JSON:
{{
    "intent": "modify_test|add_test|remove_test|explain|focus|other",
    "target": "specific test name or function name if mentioned",
    "action": "specific action requested",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of analysis"
}}
"""
            
            # Use the AI provider's analyze_code_patterns method as a proxy
            ai_response = self.ai_provider.analyze_code_patterns(prompt, 'analysis')
            
            if ai_response and 'analysis' in ai_response:
                # Try to extract JSON from the response
                response_text = ai_response['analysis']
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
            
            return None
            
        except Exception as e:
            print(f"Warning: AI feedback analysis failed: {e}")
            return None
    
    def _apply_feedback_changes(self, feedback_analysis: Dict[str, Any]) -> TestSuite:
        """Apply changes to test suite based on feedback analysis."""
        intent = feedback_analysis.get('intent', 'unknown')
        target = feedback_analysis.get('target')
        changes_made = []
        
        if intent == 'modify_test' and target:
            changes_made.extend(self._modify_test(target, feedback_analysis))
        elif intent == 'add_test' and target:
            changes_made.extend(self._add_test(target, feedback_analysis))
        elif intent == 'remove_test' and target:
            changes_made.extend(self._remove_test(target))
        elif intent == 'focus':
            self.context.current_focus = target
            changes_made.append(f"Focused on {target}")
        
        feedback_analysis['changes_made'] = changes_made
        return self.context.test_suite
    
    def _modify_test(self, target: str, analysis: Dict[str, Any]) -> List[str]:
        """Modify existing test case."""
        changes = []
        
        # Find matching test cases
        matching_tests = self._find_matching_tests(target)
        
        for test in matching_tests:
            # Use AI to enhance the test based on feedback
            enhancement_context = {
                'language': self.context.session_metadata.get('language'),
                'feedback': analysis.get('details', ''),
                'edge_cases': [],
                'performance_risks': []
            }
            
            enhanced = self.ai_provider.enhance_test_case(test, enhancement_context)
            if enhanced:
                test.test_code = enhanced.get('code', test.test_code)
                test.description = enhanced.get('description', test.description)
                if enhanced.get('assertions'):
                    test.assertions = enhanced['assertions']
                changes.append(f"Modified test: {test.name}")
        
        return changes
    
    def _add_test(self, target: str, analysis: Dict[str, Any]) -> List[str]:
        """Add new test case."""
        changes = []
        
        # Create a new test case based on the target and feedback
        new_test = TestCase(
            name=f"test_{target}_additional",
            test_type=TestType.UNIT,
            function_name=target,
            description=f"Additional test for {target} based on user feedback",
            test_code=f"def test_{target}_additional():\n    # TODO: Implement based on feedback\n    pass"
        )
        
        # Use AI to generate proper test code
        enhancement_context = {
            'language': self.context.session_metadata.get('language'),
            'feedback': analysis.get('details', ''),
            'edge_cases': [],
            'performance_risks': []
        }
        
        enhanced = self.ai_provider.enhance_test_case(new_test, enhancement_context)
        if enhanced:
            new_test.test_code = enhanced.get('code', new_test.test_code)
            new_test.description = enhanced.get('description', new_test.description)
        
        self.context.test_suite.test_cases.append(new_test)
        changes.append(f"Added test: {new_test.name}")
        
        return changes
    
    def _remove_test(self, target: str) -> List[str]:
        """Remove test case."""
        changes = []
        original_count = len(self.context.test_suite.test_cases)
        
        # Remove matching tests
        self.context.test_suite.test_cases = [
            test for test in self.context.test_suite.test_cases
            if not self._test_matches_target(test, target)
        ]
        
        removed_count = original_count - len(self.context.test_suite.test_cases)
        if removed_count > 0:
            changes.append(f"Removed {removed_count} test(s) matching '{target}'")
        
        return changes
    
    def _find_matching_tests(self, target: str) -> List[TestCase]:
        """Find test cases that match the target."""
        matching = []
        target_lower = target.lower()
        
        for test in self.context.test_suite.test_cases:
            if (target_lower in test.name.lower() or 
                target_lower in test.function_name.lower() or
                target_lower in test.description.lower()):
                matching.append(test)
        
        return matching
    
    def _test_matches_target(self, test: TestCase, target: str) -> bool:
        """Check if a test matches the target for removal."""
        target_lower = target.lower()
        return (target_lower in test.name.lower() or 
                target_lower in test.function_name.lower())
    
    def _generate_response(self, feedback_analysis: Dict[str, Any]) -> str:
        """Generate appropriate response based on feedback analysis."""
        intent = feedback_analysis.get('intent', 'unknown')
        changes = feedback_analysis.get('changes_made', [])
        
        if changes:
            response = f"I've made the following changes:\n"
            for change in changes:
                response += f"• {change}\n"
            response += "\nAnything else you'd like me to adjust?"
        elif intent == 'explain':
            target = feedback_analysis.get('target')
            if target:
                explanation = self._explain_test(target)
                response = f"Here's what I can tell you about {target}:\n{explanation}"
            else:
                response = "I'd be happy to explain! Could you be more specific about what you'd like me to explain?"
        elif intent == 'focus':
            target = feedback_analysis.get('target')
            response = f"Now focusing on {target}. What would you like me to do with it?"
        else:
            response = "I understand you want to make changes, but I need more specific guidance. Could you tell me exactly what you'd like me to modify?"
        
        return response
    
    def _explain_test(self, target: str) -> str:
        """Provide explanation for a specific test or function."""
        matching_tests = self._find_matching_tests(target)
        
        if not matching_tests:
            return f"I couldn't find any tests matching '{target}'. Available tests: {', '.join([test.name for test in self.context.test_suite.test_cases[:5]])}"
        
        explanations = []
        for test in matching_tests[:3]:  # Limit to first 3 matches
            explanation = f"\n**{test.name}** ({test.test_type.value} test):\n"
            explanation += f"Purpose: {test.description}\n"
            explanation += f"Function: {test.function_name}\n"
            if test.assertions:
                explanation += f"Key assertions: {', '.join(test.assertions[:3])}\n"
            explanations.append(explanation)
        
        return ''.join(explanations)
    
    def _get_test_case_summary(self) -> str:
        """Get a summary of current test cases."""
        if not self.context or not self.context.test_suite.test_cases:
            return "No test cases available"
        
        summary = []
        for test in self.context.test_suite.test_cases[:10]:  # Limit to first 10
            summary.append(f"- {test.name} ({test.test_type.value}): {test.function_name}")
        
        if len(self.context.test_suite.test_cases) > 10:
            summary.append(f"... and {len(self.context.test_suite.test_cases) - 10} more")
        
        return '\n'.join(summary)
    
    def _get_relevant_context(self) -> Dict[str, Any]:
        """Get relevant context from conversation history."""
        if not self.context or not self.context.conversation_history:
            return {}
        
        # Get recent turns and any turns with changes
        recent_turns = self.context.conversation_history[-3:]
        important_turns = [turn for turn in self.context.conversation_history 
                          if turn.test_changes]
        
        return {
            'recent_topics': [turn.context.get('target') for turn in recent_turns 
                            if turn.context.get('target')],
            'recent_changes': [change for turn in important_turns 
                             for change in turn.test_changes],
            'current_focus': self.context.current_focus
        }
    
    def _update_user_preferences(self) -> None:
        """Update user preferences based on conversation patterns."""
        if not self.context or len(self.context.conversation_history) < 3:
            return
        
        # Analyze patterns in user feedback
        recent_intents = [turn.context.get('intent') for turn in self.context.conversation_history[-5:]]
        
        # Update preferences
        if recent_intents.count('modify_test') > 2:
            self.context.user_preferences['prefers_modifications'] = True
        if recent_intents.count('add_test') > 1:
            self.context.user_preferences['wants_comprehensive_coverage'] = True
    
    def _update_current_focus(self) -> None:
        """Update current focus based on recent interactions."""
        if not self.context or not self.context.conversation_history:
            return
        
        # Look for recent focus changes or repeated mentions
        recent_targets = []
        for turn in self.context.conversation_history[-3:]:
            target = turn.context.get('target')
            if target:
                recent_targets.append(target)
        
        if recent_targets:
            # Use the most recent target as current focus
            self.context.current_focus = recent_targets[-1]
    
    def _handle_show_command(self, command: str) -> None:
        """Handle show commands (show tests, show focus, etc.)."""
        command_lower = command.lower()
        
        if 'tests' in command_lower:
            print(f"\n📋 Current Test Cases ({len(self.context.test_suite.test_cases)}):")
            print(self._get_test_case_summary())
        elif 'focus' in command_lower:
            focus = self.context.current_focus or "No current focus"
            print(f"\n🎯 Current Focus: {focus}")
        elif 'history' in command_lower:
            print(f"\n📜 Conversation History ({len(self.context.conversation_history)} turns):")
            for i, turn in enumerate(self.context.conversation_history[-5:], 1):
                print(f"{i}. User: {turn.user_input[:50]}...")
                if turn.test_changes:
                    print(f"   Changes: {', '.join(turn.test_changes)}")
        else:
            print("\n❓ Available show commands:")
            print("• show tests - Display current test cases")
            print("• show focus - Display current focus")
            print("• show history - Display recent conversation")
    
    def _show_help(self) -> None:
        """Show help information."""
        print("""
🤖 Test Refinement Assistant Help

Available Commands:
• help - Show this help message
• show tests - List current test cases
• show focus - Show current focus area
• show history - Show recent conversation
• done/exit/quit - End conversation

Natural Language Examples:
• "Modify the test for calculate_average"
• "Add more tests for edge cases in divide function"
• "Remove the test_invalid_input test"
• "Explain why you created test_boundary_conditions"
• "Focus on the user authentication functions"
• "Make the tests more comprehensive"
• "Add error handling tests"

Tips:
• Be specific about which test or function you want to modify
• I can understand natural language requests
• I'll maintain context throughout our conversation
• Ask me to explain anything you don't understand
""")
    
    def _end_conversation(self) -> None:
        """End the conversation and provide summary."""
        if not self.context:
            return
        
        total_changes = sum(len(turn.test_changes) for turn in self.context.conversation_history)
        duration = datetime.now() - self.context.session_metadata['start_time']
        
        print(f"""
🎉 Conversation Summary:
• Duration: {duration.seconds // 60} minutes
• Conversation turns: {len(self.context.conversation_history)}
• Total changes made: {total_changes}
• Final test count: {len(self.context.test_suite.test_cases)}

Thanks for using the Test Refinement Assistant!
""")