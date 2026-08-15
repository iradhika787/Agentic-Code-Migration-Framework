import re
from typing import List, Dict, Any


class AnalysisAgent:
    """Detects the common Python 2 constructs that need migration to Python 3."""

    def __init__(self) -> None:
        self.issue_types = {
            "dict_has_key": "Dictionary.has_key() is removed in Python 3.",
            "print_redirect_syntax": "Python 2 print redirection syntax is invalid in Python 3.",
            "old_raise_syntax": "Old raise syntax using a comma is no longer valid in Python 3.",
            "division_semantics_risk": "Python 2 division semantics differ from Python 3; review integer division behavior.",
            "iterator_semantics_risk": "This Python 2 iterator pattern may behave differently in Python 3.",
            "backtick_repr": "Backticks are removed in Python 3; use repr() instead.",
            "not_equal_operator": "<> was replaced by != in Python 3.",
        }

    def analyze(self, source_code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        for line_number, line in enumerate(source_code.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if re.search(r"\.has_key\s*\(", line):
                issues.append(
                    {
                        "line": line_number,
                        "type": "dict_has_key",
                        "detail": self.issue_types["dict_has_key"],
                    }
                )

            if re.search(r"print\s*>>|print\s+\S+\s*,", line):
                issues.append(
                    {
                        "line": line_number,
                        "type": "print_redirect_syntax",
                        "detail": self.issue_types["print_redirect_syntax"],
                    }
                )

            if re.search(r"raise\s+[^\n,]+\s*,\s*.*$", line):
                issues.append(
                    {
                        "line": line_number,
                        "type": "old_raise_syntax",
                        "detail": self.issue_types["old_raise_syntax"],
                    }
                )

            if re.search(r"(?<![A-Za-z0-9_])\d+\s*/\s*\d+", line) or re.search(r"\b(?:xrange|map|filter|zip)\s*\(", line):
                if re.search(r"(?<![A-Za-z0-9_])\d+\s*/\s*\d+", line):
                    issues.append(
                        {
                            "line": line_number,
                            "type": "division_semantics_risk",
                            "detail": self.issue_types["division_semantics_risk"],
                        }
                    )
                if re.search(r"\b(?:xrange|map|filter|zip)\s*\(", line):
                    issues.append(
                        {
                            "line": line_number,
                            "type": "iterator_semantics_risk",
                            "detail": self.issue_types["iterator_semantics_risk"],
                        }
                    )

            if "`" in line:
                issues.append(
                    {
                        "line": line_number,
                        "type": "backtick_repr",
                        "detail": self.issue_types["backtick_repr"],
                    }
                )

            if "<>" in line:
                issues.append(
                    {
                        "line": line_number,
                        "type": "not_equal_operator",
                        "detail": self.issue_types["not_equal_operator"],
                    }
                )

        return issues
