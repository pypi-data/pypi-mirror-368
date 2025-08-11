"""
ExplanationFormatter - Formats analysis explanations, test generation reasoning,
and structured edge case details for display or reporting.
"""
from typing import Any, Dict, List
from dataclasses import asdict, is_dataclass

try:
    # Prefer real types if available
    from src.analyzers.code_analyzer import AnalysisResult, FunctionInfo  # type: ignore
except Exception:  # pragma: no cover - fallback in tests
    AnalysisResult = Any  # type: ignore
    FunctionInfo = Any  # type: ignore


class ExplanationFormatter:
    """Formats explanations and reasoning for analysis and generated tests."""

    @staticmethod
    def analysis_explanation(analysis: AnalysisResult) -> str:
        lines: List[str] = []
        lang = getattr(analysis, "language", "unknown")
        funcs = getattr(analysis, "functions", []) or []
        classes = getattr(analysis, "classes", []) or []
        imports = getattr(analysis, "imports", []) or []
        edge_cases = getattr(analysis, "edge_cases", []) or []
        complexity = getattr(analysis, "complexity_score", getattr(analysis, "complexity_metrics", None))

        lines.append(f"Language: {lang}")
        lines.append(f"Functions: {[getattr(f, 'name', str(f)) for f in funcs]}")
        if classes:
            names = [c.get('name', str(c)) if isinstance(c, dict) else getattr(c, 'name', str(c)) for c in classes]
            lines.append(f"Classes: {names}")
        if imports:
            lines.append(f"Imports: {imports[:5]}{'...' if len(imports) > 5 else ''}")
        if complexity is not None:
            lines.append(f"Complexity: {complexity}")
        if edge_cases:
            lines.append("Detected edge cases:")
            for ec in edge_cases[:10]:
                desc = getattr(ec, 'description', ec)
                lines.append(f"  - {desc}")
        return "\n".join(lines)

    @staticmethod
    def test_generation_reasoning(analysis: AnalysisResult, tests: List[Any]) -> str:
        lines: List[str] = []
        if not tests:
            return "No tests generated."
        lines.append("Test generation reasoning:")
        for t in tests[:20]:
            name = getattr(t, 'name', 'test')
            test_type = getattr(getattr(t, 'test_type', None), 'value', getattr(t, 'test_type', ''))
            func = getattr(t, 'function_name', '')
            desc = getattr(t, 'description', '') or ''
            hint = ExplanationFormatter._infer_reasoning_hint(analysis, t)
            lines.append(f"  • {name} [{test_type}] on {func}: {desc}{(' — ' + hint) if hint else ''}")
        return "\n".join(lines)

    @staticmethod
    def edge_case_explanations(analysis: AnalysisResult) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for ec in getattr(analysis, 'edge_cases', []) or []:
            if is_dataclass(ec):
                data = asdict(ec)
            elif isinstance(ec, dict):
                data = ec
            else:
                data = {"type": "edge_case", "description": str(ec), "severity": 1}
            # Normalize keys
            out = {
                "type": data.get("type", "edge_case"),
                "description": data.get("description", ""),
                "severity": data.get("severity", 1),
                "location": data.get("location", "")
            }
            result.append(out)
        return result

    @staticmethod
    def _infer_reasoning_hint(analysis: AnalysisResult, test: Any) -> str:
        """Lightweight heuristics to explain why a test was created."""
        name = getattr(test, 'name', '')
        desc = (getattr(test, 'description', '') or '').lower()
        edge_cases = [str(getattr(ec, 'description', ec)).lower() for ec in getattr(analysis, 'edge_cases', []) or []]
        if 'edge' in name or 'edge' in desc:
            return 'Targets detected edge conditions'
        if any(k in desc for k in ['null', 'empty', 'division', 'index']):
            return 'Covers common boundary conditions'
        if any(k in ' '.join(edge_cases) for k in ['division', 'index', 'file']):
            return 'Aligned with analysis edge case patterns'
        return ''
