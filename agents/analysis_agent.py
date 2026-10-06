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

            # Check for dict.has_key()
            if re.search(r"\.has_key\s*\(", line):
                issues.append(
                    {
                        "line": line_number,
                        "type": "dict_has_key",
                        "detail": self.issue_types["dict_has_key"],
                    }
                )

            # Check for Python 2 print statement (more comprehensive)
            # Pattern: print followed by space but NOT '(' - catches both print >> and print expr
            if self._is_print_statement(line):
                issues.append(
                    {
                        "line": line_number,
                        "type": "print_redirect_syntax",
                        "detail": self.issue_types["print_redirect_syntax"],
                    }
                )

            # Check for old raise syntax (raise Exception, message)
            if re.search(r"raise\s+[^\n,]+\s*,\s*.*$", line):
                issues.append(
                    {
                        "line": line_number,
                        "type": "old_raise_syntax",
                        "detail": self.issue_types["old_raise_syntax"],
                    }
                )

            # Check for division semantics and iterator functions
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

            # Check for backtick repr
            if "`" in line:
                issues.append(
                    {
                        "line": line_number,
                        "type": "backtick_repr",
                        "detail": self.issue_types["backtick_repr"],
                    }
                )

            # Check for <> operator
            if "<>" in line:
                issues.append(
                    {
                        "line": line_number,
                        "type": "not_equal_operator",
                        "detail": self.issue_types["not_equal_operator"],
                    }
                )

        return issues

    def _is_print_statement(self, line: str) -> bool:
        """
        Detect Python 2 print statements.
        Returns True if the line contains a print statement (not a function call).
        
        Patterns to catch:
        - print "something"
        - print var
        - print expr >> file
        - print expr,  (with trailing comma)
        """
        # Check if line contains 'print' keyword
        if not re.search(r"\bprint\b", line):
            return False
        
        # If print is followed by '(', it's likely a function call (Python 3 style or function named print)
        # But we need to be careful - it could still be a print statement with parenthesized expression
        # Let's check for patterns that are definitively Python 2
        
        # Pattern 1: print >> (print redirect)
        if re.search(r"\bprint\s*>>", line):
            return True
        
        # Pattern 2: print "..." or print '...' without parentheses
        # Look for print followed by a space and a quote, without '(' before the quote
        if re.search(r"\bprint\s+['\"]", line):
            return True
        
        # Pattern 3: print var or print expr with comma at end (print expr,)
        # This is trickier - print(expr,) would be Python 3, but print expr, is Python 2
        if re.search(r"\bprint\s+(?!\()\S+\s*,\s*(?:$|#)", line):
            return True
        
        # Pattern 4: print with variable/identifier without parentheses and without string
        # e.g., "print x" or "print obj.attr"
        # But not "print(x)" or "print = ..."
        match = re.match(r"^(\s*)print\s+(?!\(|=)(\w+|\w+\.\w+|\w+\[\w+\])", line)
        if match:
            return True
        
        return False
