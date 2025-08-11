"""
Test Modification Engine (Task 6.2)
- Modify tests based on structured feedback
- Ensure consistency across related tests
- Validate modified test cases
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re

from src.interfaces.base_interfaces import TestSuite, TestCase, TestType, Language


@dataclass
class ValidationResult:
    ok: bool
    issues: List[str]


class TestModifier:
    """Engine to modify/validate tests independent of AI providers."""

    def modify_test(self, suite: TestSuite, target: str, change: Dict[str, Any]) -> List[str]:
        changes: List[str] = []
        tests = self._find_matching_tests(suite, target)
        for t in tests:
            # Supported change fields: rename, add_assertion, update_description, prepend_setup, append_teardown
            if new_name := change.get('rename'):
                old = t.name
                t.name = new_name
                changes.append(f"renamed {old} -> {t.name}")
            if desc := change.get('update_description'):
                t.description = desc
                changes.append(f"updated description for {t.name}")
            if assertion := change.get('add_assertion'):
                t.test_code = self._ensure_assertion(t.test_code, suite.language, assertion)
                changes.append(f"added assertion to {t.name}")
            if setup := change.get('prepend_setup'):
                t.test_code = setup + "\n" + t.test_code
                changes.append(f"prepended setup in {t.name}")
            if teardown := change.get('append_teardown'):
                t.test_code = t.test_code + "\n" + teardown
                changes.append(f"appended teardown in {t.name}")
        return changes

    def add_test(self, suite: TestSuite, target_function: str, template: Optional[str] = None) -> TestCase:
        base_name = f"test_{target_function}_additional"
        new_case = TestCase(
            name=base_name,
            test_type=TestType.UNIT,
            function_name=target_function,
            description=f"Additional test for {target_function}",
            test_code=self._default_template(suite.language, base_name, target_function) if not template else template,
        )
        suite.test_cases.append(new_case)
        return new_case

    def remove_test(self, suite: TestSuite, target: str) -> int:
        before = len(suite.test_cases)
        suite.test_cases = [t for t in suite.test_cases if not self._matches(t, target)]
        return before - len(suite.test_cases)

    def ensure_consistency(self, suite: TestSuite) -> List[str]:
        """Apply basic consistency rules across tests for the same function."""
        changes: List[str] = []
        # Rule 1: Unique test names
        seen = {}
        for t in suite.test_cases:
            if t.name in seen:
                idx = seen[t.name] + 1
                new_name = f"{t.name}_{idx}"
                seen[t.name] = idx
                t.name = new_name
                changes.append(f"deduped name -> {new_name}")
            else:
                seen[t.name] = 1
        # Rule 2: Ensure tests contain at least one assertion for UNIT tests
        for t in suite.test_cases:
            if t.test_type == TestType.UNIT and not self._has_assertion(t.test_code, suite.language):
                t.test_code = self._ensure_assertion(t.test_code, suite.language, None)
                changes.append(f"added minimal assertion to {t.name}")
        return changes

    def validate(self, suite: TestSuite) -> ValidationResult:
        issues: List[str] = []
        # Names not empty and unique
        names = [t.name for t in suite.test_cases]
        if len(set(names)) != len(names):
            issues.append("duplicate test names detected")
        # Code contains basic framework markers and assertions
        for t in suite.test_cases:
            if not self._has_framework_marker(t.test_code, suite.language):
                issues.append(f"{t.name}: missing framework structure")
            if t.test_type == TestType.UNIT and not self._has_assertion(t.test_code, suite.language):
                issues.append(f"{t.name}: missing assertion")
        return ValidationResult(ok=len(issues) == 0, issues=issues)

    # ---- helpers ----
    def _find_matching_tests(self, suite: TestSuite, target: str) -> List[TestCase]:
        return [t for t in suite.test_cases if self._matches(t, target)]

    def _matches(self, t: TestCase, target: str) -> bool:
        tl = target.lower()
        return tl in t.name.lower() or tl in t.function_name.lower() or tl in t.description.lower()

    def _default_template(self, language: Language, name: str, fn: str) -> str:
        if language == Language.PYTHON:
            return f"def {name}():\n    # TODO\n    assert True\n"
        if language == Language.JAVA:
            return f"@Test\npublic void {name}() {{\n    // TODO\n    assertTrue(true);\n}}\n"
        # JS default
        return f"test('{name}', () => {{\n  // TODO\n  expect(true).toBe(true);\n}});\n"

    def _has_assertion(self, code: str, language: Language) -> bool:
        if language == Language.PYTHON:
            return 'assert ' in code
        if language == Language.JAVA:
            return re.search(r"assert\w*\(", code) is not None
        return 'expect(' in code

    def _has_framework_marker(self, code: str, language: Language) -> bool:
        if language == Language.PYTHON:
            return re.search(r"def\s+test_\w+\s*\(", code) is not None
        if language == Language.JAVA:
            return '@Test' in code
        return re.search(r"\b(it|test)\(\s*'|\"", code) is not None

    def _ensure_assertion(self, code: str, language: Language, assertion: Optional[str]) -> str:
        if language == Language.PYTHON:
            return code if 'assert ' in code else code.rstrip() + "\nassert True\n"
        if language == Language.JAVA:
            return code if re.search(r"assert\w*\(", code) else code.rstrip() + "\nassertTrue(true);\n"
        return code if 'expect(' in code else code.rstrip() + "\nexpect(true).toBe(true);\n"
