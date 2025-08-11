"""
Edge case detector: lightweight heuristics across languages.
"""
from __future__ import annotations

import re
from typing import List

from ..interfaces.base_interfaces import EdgeCase


class EdgeCaseDetector:
    """Detect common edge cases in code using regex heuristics.

    Produces EdgeCase entries with a simple type, line location, description, and severity.
    """

    def detect(self, code: str, language: str) -> List[EdgeCase]:
        lines = code.splitlines()
        out: List[EdgeCase] = []

        def add(kind: str, line_idx: int, desc: str, severity: int = 1):
            loc = f"line {line_idx + 1}"
            out.append(EdgeCase(type=kind, location=loc, description=desc, severity=severity))

        # Normalized checks per line
        for i, ln in enumerate(lines):
            l = ln.strip()

            # Null/undefined checks
            if language == 'python':
                if re.search(r"\bis\s+None\b", l) or re.search(r"\bis\s+not\s+None\b", l):
                    add('null_check', i, 'Explicit None check')
            elif language in ('javascript', 'typescript'):
                if 'null' in l or 'undefined' in l:
                    add('null_check', i, 'null/undefined check')
            elif language == 'java':
                if 'null' in l:
                    add('null_check', i, 'null check')

            # Empty collection checks
            if language == 'python':
                if re.search(r"len\([^)]*\)\s*==\s*0", l) or re.search(r"^if\s+not\s+\w+\s*:|\bnot\s+\w+\b", l):
                    add('empty_collection', i, 'Potential empty collection handling')
            elif language in ('javascript', 'typescript'):
                if re.search(r"\.length\s*===?\s*0", l) or re.search(r"!\w+\.length", l):
                    add('empty_collection', i, 'Potential empty array handling')
            elif language == 'java':
                if '.isEmpty()' in l:
                    add('empty_collection', i, 'Collection emptiness handling')

            # Division by zero risk (heuristic): any division operator
            if '/' in l and not l.lstrip().startswith('//') and 'http' not in l:
                add('division_by_zero', i, 'Potential division by zero risk', severity=2)

            # Indexing risk (heuristic)
            if re.search(r"\w+\[[^\]]+\]", l):
                add('index_bounds', i, 'Potential index out-of-bounds risk')

        return out
